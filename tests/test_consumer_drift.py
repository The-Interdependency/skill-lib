"""Consumer drift regressions, including declared skill dependency closure.

Usage: python -m unittest discover -s tests -p 'test_consumer_drift.py'
Fixtures and the propagation integration write only to temporary directories.
"""

from __future__ import annotations

import contextlib
import hashlib
import importlib.util
import io
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location(
    "check_consumer_drift", ROOT / "tools" / "check_consumer_drift.py"
)
ccd = importlib.util.module_from_spec(_spec)
sys.modules[_spec.name] = ccd  # dataclass introspection needs the module registered
_spec.loader.exec_module(ccd)


def _write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


class ConsumerDriftTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        base = Path(self._tmp.name)
        self.canon = base / "canon"
        self.consumer = base / "consumer"
        # canonical skill with a SKILL.md and a helper file
        _write(self.canon / "msdmd" / "SKILL.md", "canonical spec\n")
        _write(self.canon / "msdmd" / "parsers" / "universal.py", "print('x')\n")
        # a second canonical skill the consumer does NOT vendor
        _write(self.canon / "doc-build" / "SKILL.md", "docs\n")
        _write(
            self.canon / "skills.json",
            '{"superseded_skills":[{"name":"old-skill","replacements":["doc-build"]}]}\n',
        )
        # consumer vendors msdmd verbatim
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "canonical spec\n")
        _write(
            self.consumer / ".agents/skills" / "msdmd" / "parsers" / "universal.py",
            "print('x')\n",
        )

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def _report(self, **kw):
        return ccd.check_consumer(self.consumer, canon_root=self.canon, **kw)

    def test_verbatim_copy_is_clean(self) -> None:
        report = self._report()
        self.assertEqual([s.name for s in report.skills], ["msdmd"])
        self.assertTrue(all(s.ok for s in report.skills))

    def test_only_vendored_intersection_is_checked(self) -> None:
        # doc-build exists canonically but is not vendored -> not reported
        report = self._report()
        self.assertNotIn("doc-build", [s.name for s in report.skills])

    def test_differing_file_is_drift(self) -> None:
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "tampered\n")
        report = self._report()
        msdmd = next(s for s in report.skills if s.name == "msdmd")
        self.assertFalse(msdmd.ok)
        self.assertTrue(any("differs: SKILL.md" in r for r in msdmd.drift))

    def test_missing_canonical_file_is_drift(self) -> None:
        (self.consumer / ".agents/skills" / "msdmd" / "parsers" / "universal.py").unlink()
        report = self._report()
        msdmd = next(s for s in report.skills if s.name == "msdmd")
        self.assertTrue(any("missing:" in r for r in msdmd.drift))

    def test_local_addition_is_ignored(self) -> None:
        # a repo-local extra file must not count as drift
        _write(self.consumer / ".agents/skills" / "msdmd" / "runner.py", "local\n")
        report = self._report()
        self.assertTrue(all(s.ok for s in report.skills))

    def test_local_only_skill_is_ignored(self) -> None:
        _write(self.consumer / ".agents/skills" / "repo-local" / "SKILL.md", "local\n")
        report = self._report()
        self.assertNotIn("repo-local", [s.name for s in report.skills])

    def test_superseded_skill_fails_even_when_no_longer_canonical(self) -> None:
        _write(self.consumer / ".agents/skills" / "old-skill" / "SKILL.md", "stale\n")
        report = self._report()
        self.assertEqual(["old-skill is superseded; replace with doc-build"], report.superseded)
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertTrue(failed)
        self.assertIn("OLD   old-skill is superseded", text)

    def test_manifest_pin_stale_is_drift(self) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        wrong = hashlib.sha256(b"NOT-GEN\n").hexdigest()  # valid format, wrong digest
        _write(
            self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256",
            f"{wrong}  generate.py\n",
        )
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("stale pin" in r for r in manifest.drift))

    def _manifest_with_pin(self, pin_text: str) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256", pin_text)

    def test_manifest_pin_wrong_filename_is_drift(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest}  wrong.py\n")  # correct digest, wrong name
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_extra_line_is_drift(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest}  generate.py\n{digest}  other.py\n")
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_binary_marker_is_clean(self) -> None:
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest} *generate.py\n")  # sha256sum binary mode
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(manifest.ok)

    def test_manifest_pin_double_marker_is_drift(self) -> None:
        # '**generate.py' names the file '*generate.py' to sha256sum -c, not generate.py
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        self._manifest_with_pin(f"{digest} **generate.py\n")
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_extra_separator_is_drift(self) -> None:
        # sha256sum -c allows exactly one space + one mode char; surplus spacing
        # becomes part of the filename, so these must not read clean.
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        for bad in (f"{digest}   generate.py\n", f"{digest}  *generate.py\n"):
            with self.subTest(pin=bad):
                self._manifest_with_pin(bad)
                report = self._report()
                manifest = next(s for s in report.skills if s.name == "manifest")
                self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_uppercase_digest_is_drift(self) -> None:
        # GNU sha256sum emits lowercase hex; an uppercased digest is not its format.
        digest = hashlib.sha256(b"GEN\n").hexdigest().upper()
        self._manifest_with_pin(f"{digest}  generate.py\n")
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(any("malformed pin" in r for r in manifest.drift))

    def test_manifest_pin_current_is_clean(self) -> None:
        _write(self.canon / "manifest" / "SKILL.md", "m\n")
        _write(self.canon / "manifest" / "generate.py", "GEN\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "SKILL.md", "m\n")
        _write(self.consumer / ".agents/skills" / "manifest" / "generate.py", "GEN\n")
        digest = hashlib.sha256(b"GEN\n").hexdigest()
        _write(
            self.consumer / ".agents/skills" / "manifest" / "generate.py.sha256",
            f"{digest}  generate.py\n",
        )
        report = self._report()
        manifest = next(s for s in report.skills if s.name == "manifest")
        self.assertTrue(manifest.ok)

    def test_sha_citation_warning(self) -> None:
        report = self._report(sha="abc1234")
        self.assertIsNotNone(report.sha_warning)
        _write(
            self.consumer / ".agents/skills" / "README.md",
            "Source commit: `skill-lib` @ `abc1234`\n",
        )
        report = self._report(sha="abc1234")
        self.assertIsNone(report.sha_warning)

    def test_no_skills_dir_reports_nothing_vendored(self) -> None:
        empty = Path(self._tmp.name) / "empty"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        self.assertEqual(report.skills, [])
        self.assertIn("nothing vendored", report.sha_warning or "")

    def test_require_vendored_empty_fails(self) -> None:
        empty = Path(self._tmp.name) / "empty2"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=True)
        self.assertTrue(failed)

    def test_require_vendored_with_subset_is_clean(self) -> None:
        report = self._report()  # vendors msdmd
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=True)
        self.assertFalse(failed)

    def test_no_require_vendored_empty_is_clean(self) -> None:
        empty = Path(self._tmp.name) / "empty3"
        empty.mkdir()
        report = ccd.check_consumer(empty, canon_root=self.canon)
        _text, failed = ccd.format_report(report, strict_sha=False, require_vendored=False)
        self.assertFalse(failed)

    def _reference_doctrine(self, in_consumer: bool = True, consumer_body: str = "DOCTRINE\n") -> None:
        # canonical msdmd links to a shared doctrine doc; keep the vendored SKILL.md
        # identical so only doctrine state varies.
        body = "canonical spec\nSee [checks](../doctrine/msdmd-checks.md)\n"
        _write(self.canon / "msdmd" / "SKILL.md", body)
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", body)
        _write(self.canon / "doctrine" / "msdmd-checks.md", "DOCTRINE\n")
        if in_consumer:
            _write(self.consumer / ".agents/skills" / "doctrine" / "msdmd-checks.md", consumer_body)

    def test_referenced_doctrine_present_is_clean(self) -> None:
        self._reference_doctrine()
        report = self._report()
        self.assertEqual(report.doctrine, [])

    def test_missing_referenced_doctrine_is_drift(self) -> None:
        self._reference_doctrine(in_consumer=False)
        report = self._report()
        self.assertTrue(any("missing: doctrine/msdmd-checks.md" in r for r in report.doctrine))
        _text, failed = ccd.format_report(report, strict_sha=False)
        self.assertTrue(failed)

    def test_stale_referenced_doctrine_is_drift(self) -> None:
        self._reference_doctrine(consumer_body="STALE DOCTRINE\n")
        report = self._report()
        self.assertTrue(any("differs: doctrine/msdmd-checks.md" in r for r in report.doctrine))

    def test_unreferenced_doctrine_not_required(self) -> None:
        # a doctrine file no vendored skill links to is not required in the consumer
        _write(self.canon / "doctrine" / "unused.md", "x\n")
        report = self._report()
        self.assertEqual(report.doctrine, [])

    def test_format_and_exit_code(self) -> None:
        _write(self.consumer / ".agents/skills" / "msdmd" / "SKILL.md", "tampered\n")
        report = self._report()
        _text, failed = ccd.format_report(report, strict_sha=False)
        self.assertTrue(failed)


class ConsumerDependencyClosureTest(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        base = Path(self._tmp.name)
        self.canon = base / "canon"
        self.consumer = base / "consumer"
        self.skills_root = self.consumer / ".agents/skills"
        self.declarations = {
            "agent-instantiation": ["wdll"],
            "wdll": [],
            "msdmd": [],
            "unrelated": [],
        }
        for name in self.declarations:
            _write(self.canon / name / "SKILL.md", f"canonical {name}\n")
        self._write_index()
        self._vendor("agent-instantiation")

    def _write_index(self) -> None:
        _write(
            self.canon / "skills.json",
            json.dumps({
                "skills": [
                    {"name": name, "depends_on": dependencies}
                    for name, dependencies in self.declarations.items()
                ],
            }),
        )

    def _vendor(self, *names: str) -> None:
        for name in names:
            shutil.copytree(self.canon / name, self.skills_root / name, dirs_exist_ok=True)

    def _report(self):
        return ccd.check_consumer(self.consumer, canon_root=self.canon)

    def _assert_dependency_failure(self, *names: str):
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertTrue(failed, text)
        self.assertTrue(report.dependencies, text)
        diagnostics = "\n".join(report.dependencies)
        for name in names:
            self.assertIn(name, diagnostics)
        return report

    def _cli(self, *args: str) -> tuple[int, str]:
        stdout = io.StringIO()
        with contextlib.redirect_stdout(stdout):
            code = ccd.main([
                str(self.consumer), "--canon-root", str(self.canon), *args,
            ])
        return code, stdout.getvalue()

    def test_direct_missing_dependency_fails(self) -> None:
        self._assert_dependency_failure("agent-instantiation", "wdll")

    def test_transitive_missing_dependency_fails(self) -> None:
        self.declarations["wdll"] = ["msdmd"]
        self._write_index()
        self._vendor("wdll")
        self._assert_dependency_failure("agent-instantiation", "wdll", "msdmd")

    def test_missing_intermediate_still_checks_transitive_dependency(self) -> None:
        self.declarations["wdll"] = ["msdmd"]
        self._write_index()
        self._assert_dependency_failure("agent-instantiation", "wdll", "msdmd")

    def test_complete_transitive_closure_is_clean(self) -> None:
        self.declarations["wdll"] = ["msdmd"]
        self._write_index()
        self._vendor("wdll", "msdmd")
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False, require_vendored=True)
        self.assertFalse(failed, text)
        self.assertEqual(report.dependencies, [])
        self.assertEqual(
            {skill.name for skill in report.skills},
            {"agent-instantiation", "wdll", "msdmd"},
        )

    def test_shared_dependency_is_checked_once(self) -> None:
        self.declarations["agent-instantiation"] = ["wdll", "msdmd"]
        self.declarations["wdll"] = ["msdmd"]
        self._write_index()
        self._vendor("wdll", "msdmd")
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertFalse(failed, text)
        self.assertEqual([skill.name for skill in report.skills].count("msdmd"), 1)

    def test_unrelated_unvendored_dependency_errors_are_ignored(self) -> None:
        self.declarations["unrelated"] = ["not-in-index"]
        self._write_index()
        self._vendor("wdll")
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertFalse(failed, text)
        self.assertNotIn("unrelated", [skill.name for skill in report.skills])

    def test_local_only_skill_and_additions_remain_allowed(self) -> None:
        self._vendor("wdll")
        _write(self.skills_root / "repo-local" / "SKILL.md", "local skill\n")
        _write(self.skills_root / "wdll" / "runner.py", "local helper\n")
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertFalse(failed, text)
        self.assertNotIn("repo-local", [skill.name for skill in report.skills])

    def test_required_dependency_canonical_source_missing_fails(self) -> None:
        self._vendor("wdll")
        shutil.rmtree(self.canon / "wdll")
        report = self._assert_dependency_failure("agent-instantiation", "wdll")
        self.assertIn("canonical", "\n".join(report.dependencies).lower())

    def test_required_dependency_canonical_skill_file_missing_fails(self) -> None:
        self._vendor("wdll")
        (self.canon / "wdll" / "SKILL.md").unlink()
        self._assert_dependency_failure("agent-instantiation", "wdll")

    def test_unknown_dependency_fails_even_with_local_copy(self) -> None:
        self.declarations["agent-instantiation"] = ["not-in-index"]
        self._write_index()
        _write(self.skills_root / "not-in-index" / "SKILL.md", "local copy\n")
        self._assert_dependency_failure("agent-instantiation", "not-in-index")

    def test_unindexed_root_without_declared_dependents_remains_allowed(self) -> None:
        del self.declarations["agent-instantiation"]
        self._write_index()
        report = self._report()
        text, failed = ccd.format_report(report, strict_sha=False)
        self.assertFalse(failed, text)

    def test_unknown_dependency_cannot_hide_behind_an_already_checked_root(self) -> None:
        # The unindexed skill sorts first as a root, but a declared prerequisite
        # still needs an index entry even when its canonical files are present.
        del self.declarations["agent-instantiation"]
        self.declarations["unrelated"] = ["agent-instantiation"]
        self._write_index()
        self._vendor("unrelated")
        self._assert_dependency_failure("unrelated", "agent-instantiation")

    def test_dependency_cycle_fails(self) -> None:
        self.declarations["wdll"] = ["agent-instantiation"]
        self._write_index()
        self._vendor("wdll")
        report = self._assert_dependency_failure("agent-instantiation", "wdll")
        self.assertIn("cycle", "\n".join(report.dependencies).lower())

    def test_self_dependency_cycle_fails(self) -> None:
        self.declarations["agent-instantiation"] = ["agent-instantiation"]
        self._write_index()
        report = self._assert_dependency_failure("agent-instantiation")
        self.assertIn("cycle", "\n".join(report.dependencies).lower())

    def test_malformed_dependency_container_fails(self) -> None:
        for invalid in (None, "wdll", {"wdll": True}, 1, False):
            with self.subTest(depends_on=invalid):
                self.declarations["agent-instantiation"] = invalid
                self._write_index()
                self._assert_dependency_failure("agent-instantiation")

    def test_malformed_dependency_item_fails(self) -> None:
        self._vendor("wdll")
        for invalid in (None, 1, False, {"name": "wdll"}, ["wdll"], ""):
            with self.subTest(dependency=invalid):
                self.declarations["agent-instantiation"] = ["wdll", invalid]
                self._write_index()
                self._assert_dependency_failure("agent-instantiation")

    def test_malformed_transitive_declaration_fails(self) -> None:
        self.declarations["wdll"] = "msdmd"
        self._write_index()
        self._vendor("wdll")
        self._assert_dependency_failure("wdll")

    def test_dependency_helper_drift_is_checked(self) -> None:
        _write(self.canon / "wdll" / "helper.py", "canonical helper\n")
        self._vendor("wdll")
        _write(self.skills_root / "wdll" / "helper.py", "stale helper\n")
        report = self._report()
        wdll = next(skill for skill in report.skills if skill.name == "wdll")
        self.assertIn("differs: helper.py", wdll.drift)
        self.assertTrue(ccd.format_report(report, strict_sha=False)[1])

    def test_dependency_directory_without_skill_file_fails(self) -> None:
        (self.skills_root / "wdll").mkdir()
        report = self._report()
        self.assertTrue(ccd.format_report(report, strict_sha=False)[1])
        wdll = next(skill for skill in report.skills if skill.name == "wdll")
        self.assertIn("missing: SKILL.md", wdll.drift)

    def test_missing_dependency_still_requires_its_doctrine(self) -> None:
        _write(
            self.canon / "wdll" / "SKILL.md",
            "See [doctrine](../doctrine/dependency.md)\n",
        )
        _write(self.canon / "doctrine" / "dependency.md", "canonical doctrine\n")
        report = self._assert_dependency_failure("agent-instantiation", "wdll")
        self.assertIn("missing: doctrine/dependency.md", report.doctrine)

    def test_complete_dependency_closure_checks_doctrine_bytes(self) -> None:
        _write(
            self.canon / "wdll" / "SKILL.md",
            "See [doctrine](../doctrine/dependency.md)\n",
        )
        _write(self.canon / "doctrine" / "dependency.md", "canonical doctrine\n")
        self._vendor("wdll")
        _write(self.skills_root / "doctrine" / "dependency.md", "stale doctrine\n")
        report = self._report()
        self.assertIn("differs: doctrine/dependency.md", report.doctrine)
        self.assertTrue(ccd.format_report(report, strict_sha=False)[1])

    def test_missing_dependency_cli_text_is_nonzero_and_actionable(self) -> None:
        code, output = self._cli()
        self.assertEqual(code, 1, output)
        self.assertIn("DRIFT", output)
        self.assertIn("agent-instantiation", output)
        self.assertIn("wdll", output)
        self.assertIn("missing", output.lower())

    def test_missing_dependency_cli_json_is_nonzero_and_actionable(self) -> None:
        code, output = self._cli("--json")
        payload = json.loads(output)
        self.assertEqual(code, 1, output)
        self.assertTrue(payload["failed"])
        self.assertTrue(payload["dependencies"])
        self.assertIn("agent-instantiation", "\n".join(payload["dependencies"]))
        self.assertIn("wdll", "\n".join(payload["dependencies"]))

    def test_clean_dependency_cli_json_is_zero(self) -> None:
        self._vendor("wdll")
        code, output = self._cli("--json", "--require-vendored")
        payload = json.loads(output)
        self.assertEqual(code, 0, output)
        self.assertFalse(payload["failed"])
        self.assertEqual(payload["dependencies"], [])

    def test_malformed_dependency_cli_returns_structured_failure(self) -> None:
        self.declarations["agent-instantiation"] = None
        self._write_index()
        code, output = self._cli("--json")
        payload = json.loads(output)
        self.assertEqual(code, 1, output)
        self.assertTrue(payload["failed"])
        self.assertTrue(payload["dependencies"])

    def test_custom_install_root_checks_dependency_closure(self) -> None:
        custom = Path("custom/skills")
        destination = self.consumer / custom
        destination.parent.mkdir()
        shutil.move(str(self.skills_root), destination)
        report = ccd.check_consumer(
            self.consumer, canon_root=self.canon, skills_rel=custom,
        )
        self.assertTrue(ccd.format_report(report, strict_sha=False)[1])
        self.assertIn("wdll", "\n".join(report.dependencies))


class ConsumerPropagationIntegrationTest(unittest.TestCase):
    def test_agent_instantiation_propagation_then_wdll_deletion(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            consumer = Path(tmp)
            result = subprocess.run(
                [sys.executable, str(ROOT / "tools/propagate_skills.py"),
                 str(consumer), "--skills", "agent-instantiation", "--apply"],
                capture_output=True, text=True, check=False,
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            wdll = consumer / ".agents/skills/wdll"
            self.assertEqual(
                (wdll / "SKILL.md").read_bytes(),
                (ROOT / "wdll/SKILL.md").read_bytes(),
            )
            report = ccd.check_consumer(consumer, canon_root=ROOT)
            text, failed = ccd.format_report(report, strict_sha=False)
            self.assertFalse(failed, text)

            shutil.rmtree(wdll)
            report = ccd.check_consumer(consumer, canon_root=ROOT)
            text, failed = ccd.format_report(report, strict_sha=False)
            self.assertTrue(failed, text)
            self.assertIn("agent-instantiation", "\n".join(report.dependencies))
            self.assertIn("wdll", "\n".join(report.dependencies))
            self.assertFalse(wdll.exists(), "the checker must remain read-only")


if __name__ == "__main__":
    unittest.main()
