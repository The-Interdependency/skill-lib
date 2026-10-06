"""Regressions for consumer-review findings on the native MSDMD collector.

Usage: python -m unittest tests.test_msdmd_consumer_review
Each test names the review finding it closes. Fixtures are parsed statically.
"""
from __future__ import annotations

import base64
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from msdmd.collect import collect, collection_errors, generator_identity, runtime_unavailable

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "ratios"))
import harmonics as H  # noqa: E402


def git(root: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=fixture", "-c", "user.email=fixture@example.invalid", *args],
        check=True, capture_output=True, text=True,
    ).stdout.strip()


def committed_repo(root: Path, files: dict[str, str]) -> str:
    for name, text in files.items():
        path = root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    git(root, "init", "-q")
    git(root, "add", "-A")
    git(root, "commit", "-q", "-m", "fixture")
    return git(root, "rev-parse", "HEAD")


def run_cli(*args: str, env: dict[str, str] | None = None, stdout=subprocess.PIPE) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, "-m", "msdmd.collect", *args], cwd=ROOT,
        stdout=stdout, stderr=subprocess.PIPE, text=True, env=env)


def schema_two_helper() -> str:
    return (ROOT / "msdmd" / "collection.ts").read_text(encoding="utf-8")


BASE_FILES = {
    "pkg/core.py": '"""Core."""\n\ndef double(x: int) -> int:\n    """Twice."""\n    return x * 2\n',
    "config.json": '{"name": "fixture"}\n',
    ".gitignore": "private.json\n",
}


class OwnOutputTests(unittest.TestCase):
    """stack#78 collect.py:790, a0#111 collect.py:790, zfae/aimmh/interdependent-lib collect.py:230."""

    def test_stack_candidate_then_verifier_flow_is_byte_identical(self) -> None:
        # Mirrors stack backend/msdmd.py: mkstemp candidate and verifier siblings
        # inside the target root, then an evaluate-time rerender beside the artifact.
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            files = dict(BASE_FILES, **{".agents/skills/msdmd/collection.ts": schema_two_helper()})
            sha = committed_repo(root, files)
            artifact = root / "fixture_msdmd.ts"

            def render(suffix: str) -> Path:
                fd, name = tempfile.mkstemp(prefix=f".{artifact.name}.", suffix=suffix, dir=root)
                os.close(fd)
                result = run_cli("--root", str(root), "--repo", "fixture", "--out", name, "--source-commit", sha)
                self.assertEqual(0, result.returncode, result.stderr)
                return Path(name)

            candidate = render(".candidate")
            verifier = render(".verify")  # the candidate is still present in the tree
            self.assertEqual(candidate.read_bytes(), verifier.read_bytes())
            text = candidate.read_text(encoding="utf-8")
            self.assertNotIn(candidate.name, text)
            self.assertNotIn(verifier.name, text)
            self.assertIn('"dirty_worktree": false', text)
            os.replace(candidate, artifact)
            verifier.unlink()
            status_verify = root / f".{artifact.name}.fresh-status-verify"
            result = run_cli("--root", str(root), "--repo", "fixture", "--out", str(status_verify), "--source-commit", sha)
            self.assertEqual(0, result.returncode, result.stderr)
            self.assertEqual(artifact.read_bytes(), status_verify.read_bytes())

    def test_configured_output_does_not_dirty_the_worktree_or_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, BASE_FILES)
            args = ["--root", str(root), "--repo", "fixture", "--json", "--out", str(root / "collection.json")]
            self.assertEqual(0, run_cli(*args).returncode)
            self.assertFalse(json.loads((root / "collection.json").read_text())["source"]["dirty_worktree"])
            check = run_cli(*args, "--check")
            self.assertEqual(0, check.returncode, check.stdout + check.stderr)

    def test_stdout_redirect_into_the_scanned_tree_is_not_an_input(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, BASE_FILES)
            destination = root / "collection.json"
            with destination.open("w", encoding="utf-8") as handle:
                result = run_cli("--root", str(root), "--repo", "fixture", "--json", "--strict", stdout=handle)
            self.assertEqual(0, result.returncode, result.stderr)
            collection = json.loads(destination.read_text(encoding="utf-8"))
            self.assertNotIn("collection.json", {item["file"] for item in collection["discovery"]})
            self.assertFalse(collection_errors(collection))


class GitIgnoredInputTests(unittest.TestCase):
    """stack#78 collect.py:272."""

    def test_ignored_local_files_are_never_read(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            sha = committed_repo(root, BASE_FILES)
            (root / "private.json").write_text('{"value": "hunter2-local-only"}', encoding="utf-8")
            (root / "ignored-dir").mkdir()
            (root / ".gitignore").write_text("private.json\nignored-dir/\n", encoding="utf-8")
            git(root, "commit", "-q", "-am", "ignore dir")
            (root / "ignored-dir" / "x.json").write_text('{"y": 1}', encoding="utf-8")
            clean = collect(root, "fixture")
            discovered = {item["file"] for item in clean["discovery"]}
            self.assertNotIn("private.json", discovered)
            self.assertFalse(any(name.startswith("ignored-dir") for name in discovered))
            self.assertNotIn("hunter2-local-only", json.dumps(clean))
            self.assertFalse(clean["source"]["dirty_worktree"])
            self.assertNotEqual(sha, clean["source"]["revision"])  # second commit
            (root / "untracked.json").write_text('{"z": 1}', encoding="utf-8")
            dirty = collect(root, "fixture")
            self.assertIn("untracked.json", {item["file"] for item in dirty["discovery"]})
            self.assertTrue(dirty["source"]["dirty_worktree"])


class DiscoveryMemoryTests(unittest.TestCase):
    """a0#111 / aimmh#22 collect.py:314."""

    def test_aggregate_byte_budget_is_enforced_and_diagnosed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index in range(4):
                (root / f"doc{index}.json").write_text(json.dumps({"pad": "x" * 400}), encoding="utf-8")
            (root / "blob.bin").write_bytes(os.urandom(4096))
            result = collect(root, "fixture", max_total_bytes=1000)
            excluded = [item["file"] for item in result["discovery"] if item.get("reason") == "aggregate-size-limit"]
            self.assertEqual(["doc2.json", "doc3.json"], excluded)
            self.assertIn("aggregate_size_limit", {item["code"] for item in collection_errors(result)})
            self.assertFalse(result["source"]["snapshot_complete"])
            # Unconsumed bytes keep their identity but never count against the budget.
            blob = next(item for item in result["discovery"] if item["file"] == "blob.bin")
            self.assertEqual("unsupported", blob["status"])
            self.assertEqual(4096, blob["size"])


class GeneratorIdentityTests(unittest.TestCase):
    """stack#78 typescript-reader.cjs:8."""

    def test_identity_covers_typescript_worker_lock_and_assets_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp) / "msdmd"
            shutil.copytree(ROOT / "msdmd", base, ignore=shutil.ignore_patterns("node_modules", "__pycache__"))
            original = generator_identity(base)
            self.assertEqual(original, generator_identity(ROOT / "msdmd"))
            for name in ("typescript-reader.cjs", "package-lock.json", "package.json", "module-projection.schema.json", "requirements.txt", "collect.py"):
                path = base / name
                saved = path.read_bytes()
                path.write_bytes(saved + b"\n")
                self.assertNotEqual(original, generator_identity(base), name)
                path.write_bytes(saved)
            (base / "references" / "metadata-conventions.md").write_text("docs only", encoding="utf-8")
            (base / "node_modules").mkdir()
            (base / "node_modules" / "x.js").write_text("installed", encoding="utf-8")
            self.assertEqual(original, generator_identity(base))
        cli = run_cli("--print-generator-identity")
        self.assertEqual(0, cli.returncode, cli.stderr)
        self.assertEqual(generator_identity(), cli.stdout.strip())


class SchemaHelperTests(unittest.TestCase):
    """stack#78 collect.py:726."""

    SCHEMA_ONE = "export function defineMsdmdCollection<T>(value: T): T { return value; }\n"

    def test_schema_one_helper_target_is_refused_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            committed_repo(root, dict(BASE_FILES, **{".agents/skills/msdmd/collection.ts": self.SCHEMA_ONE}))
            out = root / "fixture_msdmd.ts"
            result = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(4, result.returncode)
            self.assertIn("defineMsdmdCollectionV2", result.stderr)
            self.assertFalse(out.exists())
            legacy = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out), "--legacy-blocks-only")
            self.assertEqual(0, legacy.returncode, legacy.stderr)
            self.assertIn("defineMsdmdCollection(", out.read_text(encoding="utf-8"))
            (root / ".agents/skills/msdmd/collection.ts").write_text(schema_two_helper(), encoding="utf-8")
            current = run_cli("--root", str(root), "--repo", "fixture", "--out", str(out))
            self.assertEqual(0, current.returncode, current.stderr)
            self.assertIn("defineMsdmdCollectionV2(", out.read_text(encoding="utf-8"))


class ReaderRuntimeTests(unittest.TestCase):
    """stack#78 requirements.txt:5."""

    def test_missing_runtime_is_an_error_and_marks_the_reader(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "a.py").write_text('def f():\n    """Doc.\n\n    Args:\n        x: value\n    """\n', encoding="utf-8")
            with patch.dict(sys.modules, {"docstring_parser": None}):
                result = collect(root, "fixture")
            missing = runtime_unavailable(result)
            self.assertTrue(missing)
            self.assertTrue(all(item["severity"] == "error" for item in missing))
            run = next(item for item in result["reader_runs"] if item["reader_id"] == "python-ast")
            self.assertEqual("runtime-unavailable", run["status"])

    def test_cli_fails_closed_unless_explicitly_allowed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            root.mkdir()
            (root / "a.py").write_text('def f():\n    """Doc."""\n', encoding="utf-8")
            shim = Path(tmp) / "shim"
            shim.mkdir()
            (shim / "docstring_parser.py").write_text("raise ImportError('blocked for test')\n", encoding="utf-8")
            env = dict(os.environ, PYTHONPATH=os.pathsep.join([str(shim), str(ROOT)]))
            out = root / "fixture_msdmd.ts"
            args = ["--root", str(root), "--repo", "fixture", "--json", "--out", str(out)]
            failed = run_cli(*args, env=env)
            self.assertEqual(3, failed.returncode)
            self.assertIn("ERROR: native reader runtime unavailable", failed.stderr)
            self.assertFalse(out.exists())
            allowed = run_cli(*args, "--allow-missing-reader-runtimes", env=env)
            self.assertEqual(0, allowed.returncode, allowed.stderr)
            self.assertIn("WARNING", allowed.stderr)
            self.assertTrue(runtime_unavailable(json.loads(out.read_text(encoding="utf-8"))))


class RedactionTests(unittest.TestCase):
    """ai-tiw/aimmh/pcea readers.py:322, interdependent-lib readers.py:707, pcea readers.py:745,
    eml_ucns readers.py:869, interdependent-lib standards.py:202."""

    def collection(self, files: dict[str, str | bytes]) -> dict:
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        root = Path(tmp.name)
        for name, value in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(value if isinstance(value, bytes) else value.encode("utf-8"))
        return collect(root, "fixture")

    def test_camel_and_pascal_case_secret_keys_are_redacted(self) -> None:
        secrets = {"accessToken": "S1", "authToken": "S2", "secretKey": "S3", "databasePassword": "S4",
                   "refreshToken": "S5", "githubToken": "S6", "signingPrivateKey": "S7", "apiKey": "S8",
                   "ClientSecret": "S9"}
        keep = {"maxTokens": 7, "tokenizer": "bpe", "passwordPolicyUrl": "https://example.com/p"}
        json_doc = json.dumps(dict(secrets, **keep))
        yaml_doc = "".join(f"{k}: {v}-yaml\n" for k, v in secrets.items())
        toml_doc = "".join(f'{k} = "{v}-toml"\n' for k, v in secrets.items())
        text = json.dumps(self.collection({"a.json": json_doc, "b.yaml": yaml_doc, "c.toml": toml_doc}))
        for value in secrets.values():
            self.assertNotIn(f'"{value}"', text)
            self.assertNotIn(f"{value}-yaml", text)
            self.assertNotIn(f"{value}-toml", text)
        self.assertIn('"maxTokens": 7', text)
        self.assertIn('"tokenizer": "bpe"', text)

    def test_systemd_url_credentials_and_credential_data_are_withheld(self) -> None:
        unit = ("[Service]\n"
                "Environment=DATABASE_URL=postgres://admin:envpass@db.example/app MODE=prod\n"
                "Environment=\"CACHE_URL=redis://user:quotedpass@cache:6379\"\n"
                "SetCredential=database-password:hunter2\n"
                "SetCredentialEncrypted=api-key:ZW5jcnlwdGVk\n"
                "LoadCredential=tls-key:/etc/keys/tls.pem\n"
                "ExecStart=/usr/bin/app --upstream https://bot:execpass@upstream.example/\n")
        result = self.collection({"app.service": unit})
        text = json.dumps(result)
        for secret in ("envpass", "quotedpass", "hunter2", "ZW5jcnlwdGVk", "execpass"):
            self.assertNotIn(secret, text)
        values = {f["native"]["value"]["key"] + str(f["native"]["value"]["occurrence"]): f["native"]["value"]["value"]
                  for f in result["facts"] if f["kind"] == "unit-directive"}
        self.assertEqual("database-password:<redacted>", values["SetCredential1"])
        self.assertEqual("tls-key:/etc/keys/tls.pem", values["LoadCredential1"])
        self.assertIn("MODE=prod", values["Environment1"])
        self.assertIn("postgres://[redacted]@db.example/app", values["Environment1"])

    def test_svg_metadata_is_redacted_with_a_diagnostic(self) -> None:
        svg = ('<svg xmlns="http://www.w3.org/2000/svg" api_key="topsecret" data-authToken="svgtoken" width="10">'
               "<title>see https://u:svgpass@host.example/</title></svg>")
        result = self.collection({"icon.svg": svg})
        text = json.dumps(result)
        for secret in ("topsecret", "svgtoken", "svgpass"):
            self.assertNotIn(secret, text)
        self.assertIn('"width": "10"', text)
        self.assertIn("sensitive_fields_redacted", {d["code"] for d in result["diagnostics"]})

    def test_dsse_envelope_does_not_republish_the_raw_payload(self) -> None:
        statement = {"_type": "https://in-toto.io/Statement/v1", "subject": [{"name": "a", "digest": {"sha256": "0" * 64}}],
                     "predicateType": "https://example.com/p", "predicate": {"password": "dssesecret"}}
        payload = base64.b64encode(json.dumps(statement).encode()).decode()
        envelope = {"payloadType": "application/vnd.in-toto+json", "payload": payload, "signatures": []}
        result = self.collection({"att.json": json.dumps(envelope)})
        text = json.dumps(result)
        self.assertNotIn(payload, text)
        self.assertNotIn("dssesecret", text)
        kinds = {f["kind"] for f in result["facts"]}
        self.assertTrue({"signed-envelope", "attestation"} <= kinds)
        self.assertNotIn("structured-document", kinds)


class RequirementTests(unittest.TestCase):
    """a0-betatest/aimmh/eml_ucns/interdependent-lib/pcea/zfae readers.py:819-822, a0 readers.py:804."""

    def test_direct_url_vcs_and_path_requirements_stay_unresolved(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "requirements.txt").write_text(
                "https://example.com/pkg.whl\n"
                "git+https://github.com/acme/widget.git#egg=widget\n"
                "./local/pkg\n"
                "demo-1.0.tar.gz\n"
                "named @ https://example.com/named-1.0.whl\n"
                "requests==2.32.0\n", encoding="utf-8")
            result = collect(root, "fixture")
        names = [f["native"]["value"]["name"] for f in result["facts"] if f["kind"] == "dependency"]
        self.assertEqual(["hmmm", "hmmm", "hmmm", "hmmm", "named", "requests"], names)
        targets = {e["to"] for e in result["edges"]}
        self.assertEqual({"python-package:named", "python-package:requests"}, {t for t in targets if t.startswith("python-package:")})
        unresolved = [d for d in result["diagnostics"] if d["code"] == "unresolved_direct_requirement_name"]
        self.assertEqual(4, len(unresolved))

    def test_backslash_continuations_form_one_requirement(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "requirements.txt").write_text(
                "foo==1.0 \\\n"
                "    ; python_version < '3.9'\n"
                "bar==2.0 \\\n"
                "    --hash=sha256:" + "a" * 64 + "\n", encoding="utf-8")
            result = collect(root, "fixture")
        deps = [f for f in result["facts"] if f["kind"] == "dependency"]
        self.assertEqual(["foo", "bar"], [f["native"]["value"]["name"] for f in deps])
        self.assertEqual({"start_line": 1, "end_line": 2}, {k: deps[0]["source"]["location"][k] for k in ("start_line", "end_line")})
        self.assertIn("--hash=sha256:", deps[1]["native"]["value"]["requirement"])
        self.assertNotIn("python_version", {f["native"]["value"]["name"] for f in deps})


class RatiosSemanticGraphTests(unittest.TestCase):
    """stack#78, zfae#23 and a0-betatest#33 ratios/harmonics.py:111."""

    def test_schema_two_block_edges_resolve_to_owning_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            block = "# === MODULE_BUILD ===\n# id: {id}\n#   requires: {req}\n# === END MODULE_BUILD ===\nx = 1\n"
            (root / "a.py").write_text(block.format(id="alpha", req="beta"), encoding="utf-8")
            (root / "b.py").write_text(block.format(id="beta", req="gamma"), encoding="utf-8")
            (root / "c.py").write_text(block.format(id="gamma", req="external_thing"), encoding="utf-8")
            collection = collect(root, "fixture")
            self.assertTrue(all(e["to"].startswith("msdmd://") for e in collection["edges"]
                                if e.get("target_resolution") == "resolved-unique-entry-id"))
            files = [str((root / name).resolve()) for name in ("a.py", "b.py", "c.py")]
            report = H.semantic_file_graph(collection, root, files)
        a, b, c = files
        self.assertEqual([b], report["adjacency"][a])
        self.assertEqual([c], report["adjacency"][b])
        self.assertEqual(2, report["resolved_edges"])
        self.assertEqual(1, len(report["unresolved_edges"]))
        self.assertTrue(report["unresolved_edges"][0].endswith("->external_thing"))


if __name__ == "__main__":
    unittest.main()
