# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
# === MODULE_BUILD ===
# id: msdmd_collection_generator
#   module_name: collect
#   module_kind: instrument
#   summary: produces versioned native-first MSDMD collections without executing inspected sources
#   owner: The Interdependency skill-lib
#   public_surface: collect, collect_legacy, collection_errors, render_typescript
#   internal_surface: bounded discovery, block identity validation, edge reconciliation, coverage accounting
#   auth_boundary: none
#   storage_boundary: read
#   network_boundary: none
#   user_data_boundary: read
#   admin_only: false
#   tests: tests/test_collect.py, tests/test_native_collection.py
#   rollout: schema 2 is the default CLI output; --legacy-blocks-only keeps explicit schema 1 compatibility
#   rollback: use --legacy-blocks-only while preserving schema incompatibility visibility
# === END MODULE_BUILD ===
"""Generate a versioned native-first MSDMD collection.

Usage guidance:
    python -m msdmd.collect --root . --repo owner/repo --out repo_msdmd.ts
    python -m msdmd.collect --root . --repo owner/repo --strict
    python -m msdmd.collect --root . --repo owner/repo --legacy-blocks-only

The default schema-2 path statically reads supported native conventions and
supplemental MSDMD blocks. It never imports inspected code, executes scripts,
loads plugins, follows network references, or treats declarations as verified
behavior. The explicit legacy flag emits the previous block-only shape for old
consumers; it cannot silently represent native facts.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import stat
import subprocess
import io
import tokenize
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

from msdmd.parsers.universal import marker_for, parse_text
from msdmd.readers import READER_MANIFESTS, read_native

SCHEMA_ID = "the-interdependency.msdmd-collection"
SCHEMA_VERSION = "2.0.0"
LEGACY_SCHEMA_VERSION = "1.0.0"
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024

DEFAULT_BLOCK_NAMES = (
    "DOCS",
    "CAPABILITIES",
    "DEPENDENCIES",
    "OWNERS",
    "CONTRACTS",
    "CHECKS",
    "MODULE_BUILD",
    "BOUNDARIES",
    "LLMS",
    "FRONTEND_META",
)

EDGE_FIELDS = {
    "requires": "requires",
    "exposes": "exposes",
    "owner": "owns",
    "covers": "covers",
    "call": "calls",
    "proves": "claims_proves",
    "boundaries": "risk",
}

_DEFAULT_SKIP = {
    ".git",
    ".agents",
    ".skill-lib",
    ".venv",
    ".mypy_cache",
    ".pytest_cache",
    ".tox",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}


def _sha256(data: bytes | str) -> str:
    payload = data if isinstance(data, bytes) else data.encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _quote(value: str, *, path: bool = False) -> str:
    return quote(value, safe="/" if path else "")


def _split_targets(value: str) -> list[str]:
    return [part.strip() for part in value.split(",") if part.strip()]


def _block_source_text(path: Path, text: str) -> str:
    """Return only real Python comments, or unchanged non-Python source.

    The universal block grammar remains language-neutral. Python collection
    adds syntax awareness here so block-shaped examples inside strings are not
    collected as declarations.
    """
    if path.suffix.lower() not in {".py", ".pyi", ".pyw"}:
        return text
    comments = [""] * len(text.splitlines())
    try:
        for token in tokenize.generate_tokens(io.StringIO(text).readline):
            if token.type == tokenize.COMMENT:
                comments[token.start[0] - 1] = token.string
    except (tokenize.TokenError, IndentationError):
        return ""
    return "\n".join(comments)


def _decode_block_source(path: Path, data: bytes) -> str:
    """Decode Python by its declared source encoding; other sources as UTF-8."""
    if path.suffix.lower() in {".py", ".pyi", ".pyw"}:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        return data.decode(encoding)
    return data.decode("utf-8")


def _block_address(repo: str, revision: str, file: str, block: str, entry_id: str) -> str:
    return (
        f"msdmd://{_quote(repo)}@{_quote(revision)}/{_quote(file, path=True)}"
        f"#block/{_quote(block)}/{_quote(entry_id)}"
    )


def _block_declaration(
    *,
    file: str,
    repo: str,
    revision: str,
    content_sha256: str,
    block: str,
    entry: dict[str, str],
) -> dict[str, Any]:
    entry_id = str(entry["id"])
    return {
        "address": _block_address(repo, revision, file, block, entry_id),
        "origin": "msdmd-block",
        "standing": "declared",
        "source": {
            "repository": repo,
            "revision": revision,
            "file": file,
            "content_sha256": content_sha256,
            "location": {"pointer": f"block:{block}/id:{entry_id}"},
        },
        "file": file,
        "block": block,
        "id": entry_id,
        "fields": {str(key): str(value) for key, value in entry.items() if key != "id"},
    }


def _raw_block_edges(declaration: dict[str, Any]) -> list[dict[str, Any]]:
    edges: list[dict[str, Any]] = []
    for field, kind in EDGE_FIELDS.items():
        value = declaration["fields"].get(field)
        if not value or value == "hmmm":
            continue
        for target in _split_targets(value):
            edges.append({
                "from": declaration["address"],
                "to": target,
                "kind": kind,
                "standing": "declared",
                "source_block": declaration["block"],
                "source_id": declaration["address"],
                "source_entry_id": declaration["id"],
                "target_resolution": "pending",
            })
    return edges


def _git_identity(root: Path, explicit_revision: str | None) -> tuple[str, bool | str, str | None]:
    revision = explicit_revision
    dirty: bool | str = "hmmm"
    git_head: str | None = None
    try:
        git_head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if revision is None:
            revision = git_head
        status_output = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain", "--untracked-files=all"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout
        input_changes = []
        for line in status_output.splitlines():
            changed_path = line[3:].split(" -> ")[-1].strip('"') if len(line) > 3 else ""
            if not Path(changed_path).name.endswith("_msdmd.ts"):
                input_changes.append(line)
        dirty = bool(input_changes)
    except (OSError, subprocess.CalledProcessError):
        pass
    return revision or "hmmm", dirty, git_head


def _discover(root: Path, max_file_bytes: int) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Return ``(readable, ledger, diagnostics)`` without following symlinks."""
    readable: list[dict[str, Any]] = []
    ledger: list[dict[str, Any]] = []
    diagnostics: list[dict[str, Any]] = []

    def visit(directory: Path) -> None:
        try:
            children = sorted(directory.iterdir(), key=lambda item: item.name)
        except OSError as exc:
            relative = directory.relative_to(root).as_posix() if directory != root else "."
            diagnostics.append({
                "code": "unreadable_directory",
                "severity": "error",
                "status": "unreadable",
                "message": str(exc),
                "source": {"file": relative},
                "reader_ids": [],
            })
            return
        for path in children:
            relative = path.relative_to(root).as_posix()
            try:
                mode = path.lstat().st_mode
            except OSError as exc:
                diagnostics.append({"code": "unreadable_path", "severity": "error", "status": "unreadable", "message": str(exc), "source": {"file": relative}, "reader_id": None})
                ledger.append({"file": relative, "status": "unreadable", "reader_ids": [], "content_sha256": "hmmm"})
                continue
            if stat.S_ISLNK(mode):
                target = os.readlink(path)
                ledger.append({"file": relative, "status": "excluded", "reason": "symlink-not-followed", "reader_ids": [], "content_sha256": _sha256(target)})
                continue
            if stat.S_ISDIR(mode):
                if path.name not in _DEFAULT_SKIP:
                    visit(path)
                continue
            if not stat.S_ISREG(mode):
                ledger.append({"file": relative, "status": "excluded", "reason": "not-regular-file", "reader_ids": [], "content_sha256": "hmmm"})
                continue
            if path.name.endswith("_msdmd.ts"):
                continue
            size = path.stat().st_size
            if size > max_file_bytes:
                ledger.append({"file": relative, "status": "excluded", "reason": "size-limit", "size": size, "reader_ids": [], "content_sha256": "hmmm"})
                diagnostics.append({"code": "file_size_limit", "severity": "warning", "status": "excluded", "message": f"{size} bytes exceeds {max_file_bytes}", "source": {"file": relative}, "reader_id": None})
                continue
            try:
                data = path.read_bytes()
            except OSError as exc:
                ledger.append({"file": relative, "status": "unreadable", "reader_ids": [], "content_sha256": "hmmm"})
                diagnostics.append({"code": "unreadable_file", "severity": "error", "status": "unreadable", "message": str(exc), "source": {"file": relative}, "reader_id": None})
                continue
            readable.append({"path": path, "file": relative, "data": data, "content_sha256": _sha256(data), "size": size})

    visit(root)
    return readable, ledger, diagnostics


def _reconcile_block_edges(
    raw_edges: list[dict[str, Any]],
    declarations: list[dict[str, Any]],
    diagnostics: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    by_id: dict[str, list[str]] = defaultdict(list)
    for declaration in declarations:
        by_id[declaration["id"]].append(declaration["address"])
    edges: list[dict[str, Any]] = []
    for edge in raw_edges:
        candidates = by_id.get(edge["to"], [])
        if len(candidates) == 1:
            edge["to"] = candidates[0]
            edge["target_resolution"] = "resolved-unique-entry-id"
        elif len(candidates) > 1:
            diagnostics.append({
                "code": "ambiguous_edge_target",
                "severity": "warning",
                "status": "ambiguous",
                "message": f"target {edge['to']!r} matches {len(candidates)} qualified declarations",
                "source": {"address": edge["source_id"]},
                "reader_id": "msdmd-block",
                "candidates": sorted(candidates),
            })
            edge["target_resolution"] = "ambiguous"
        else:
            edge["target_resolution"] = "external-or-unresolved"
        edges.append(edge)
    return edges


def _duplicate_diagnostics(declarations: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[tuple[str, str, str], list[dict[str, Any]]] = defaultdict(list)
    for declaration in declarations:
        groups[(declaration["file"], declaration["block"], declaration["id"])].append(declaration)
    diagnostics: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for (file, block, entry_id), group in sorted(groups.items()):
        if len(group) < 2:
            continue
        address = group[0]["address"]
        diagnostics.append({
            "code": "duplicate_block_id",
            "severity": "error",
            "status": "invalid",
            "message": f"{file} contains {len(group)} {block} entries with id {entry_id!r}",
            "source": {"address": address, "file": file},
            "reader_id": "msdmd-block",
        })
        conflicts.append({
            "kind": "identity-conflict",
            "status": "unresolved",
            "identity": address,
            "witnesses": [item["source"] for item in group],
            "reason": "duplicate entry id within one block type and owning file",
        })
    return diagnostics, conflicts


def _native_identity_diagnostics(facts: list[dict[str, Any]]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for fact in facts:
        groups[fact["address"]].append(fact)
    diagnostics: list[dict[str, Any]] = []
    conflicts: list[dict[str, Any]] = []
    for address, group in sorted(groups.items()):
        if len(group) < 2:
            continue
        diagnostics.append({
            "code": "duplicate_native_fact_address",
            "severity": "error",
            "status": "invalid",
            "message": f"collector generated {len(group)} native facts at one address",
            "source": {"address": address, "file": group[0]["source"]["file"]},
            "reader_id": group[0]["extraction"]["reader_id"],
        })
        conflicts.append({
            "kind": "collector-address-conflict",
            "status": "unresolved",
            "identity": address,
            "witnesses": [item["source"] for item in group],
            "reason": "multiple native facts received one generated collector address",
        })
    return diagnostics, conflicts


def collect(
    root: Path,
    repo: str,
    *,
    block_names: Iterable[str] = DEFAULT_BLOCK_NAMES,
    expected_blocks: Iterable[str] = (),
    source_commit: str | None = None,
    max_file_bytes: int = DEFAULT_MAX_FILE_BYTES,
    include_native: bool = True,
) -> dict[str, Any]:
    """Collect native facts and supplemental blocks under ``root`` as schema 2."""
    root = root.resolve()
    block_names = tuple(block_names)
    expected_blocks = tuple(expected_blocks)
    revision, dirty, git_head = _git_identity(root, source_commit)
    readable, discovery, diagnostics = _discover(root, max_file_bytes)
    if source_commit is not None and git_head is not None and source_commit != git_head:
        diagnostics.append({
            "code": "source_revision_mismatch",
            "severity": "error",
            "status": "invalid",
            "message": f"declared source revision {source_commit} does not match git HEAD {git_head}",
            "source": {"file": ".", "declared_revision": source_commit, "git_head": git_head},
            "reader_id": None,
        })

    declarations: list[dict[str, Any]] = []
    facts: list[dict[str, Any]] = []
    native_edges: list[dict[str, Any]] = []
    raw_block_edges: list[dict[str, Any]] = []
    missing_by_file: dict[str, set[str]] = defaultdict(set)
    reader_counts: Counter[str] = Counter()
    reader_fact_counts: Counter[str] = Counter()
    block_files: dict[str, set[str]] = defaultdict(set)

    for item in readable:
        relative = item["file"]
        relative_path = Path(relative)
        context = {
            "repo": repo,
            "revision": revision,
            "file": relative,
            "content_sha256": item["content_sha256"],
        }
        reader_ids, file_facts, file_edges, file_diagnostics = (
            read_native(relative_path, item["data"], context)
            if include_native
            else ([], [], [], [])
        )
        file_statuses = {diagnostic.get("status") for diagnostic in file_diagnostics}
        if "invalid" in file_statuses:
            status = "invalid"
        elif "unsupported" in file_statuses and file_facts:
            status = "partial"
        elif "unsupported" in file_statuses:
            status = "unsupported"
        else:
            status = "supported" if reader_ids else "unsupported"
        discovery.append({
            "file": relative,
            "status": status,
            "reader_ids": reader_ids,
            "content_sha256": item["content_sha256"],
            "size": item["size"],
        })
        for reader_id in reader_ids:
            reader_counts[reader_id] += 1
        for fact in file_facts:
            reader_fact_counts[fact["extraction"]["reader_id"]] += 1
        facts.extend(file_facts)
        native_edges.extend(file_edges)
        diagnostics.extend(file_diagnostics)

        marker = marker_for(relative_path)
        if marker is None:
            continue
        try:
            text = _decode_block_source(relative_path, item["data"])
        except (SyntaxError, UnicodeDecodeError) as exc:
            diagnostics.append({
                "code": "undecodable_block_source",
                "severity": "error",
                "status": "invalid",
                "message": str(exc),
                "source": {"file": relative, "content_sha256": item["content_sha256"]},
                "reader_id": "msdmd-block",
            })
            continue
        block_text = _block_source_text(relative_path, text)
        for block in block_names:
            entries = parse_text(block_text, block, marker)
            if entries:
                block_files[block].add(relative)
            elif block in expected_blocks:
                missing_by_file[relative].add(block)
            for entry in entries:
                if "id" not in entry:
                    continue
                declaration = _block_declaration(
                    file=relative,
                    repo=repo,
                    revision=revision,
                    content_sha256=item["content_sha256"],
                    block=block,
                    entry=entry,
                )
                declarations.append(declaration)
                raw_block_edges.extend(_raw_block_edges(declaration))

    declarations.sort(key=lambda item: (item["file"], item["block"], item["id"], json.dumps(item["fields"], sort_keys=True)))
    facts.sort(key=lambda item: item["address"])
    duplicate_diagnostics, conflicts = _duplicate_diagnostics(declarations)
    diagnostics.extend(duplicate_diagnostics)
    native_diagnostics, native_conflicts = _native_identity_diagnostics(facts)
    diagnostics.extend(native_diagnostics)
    conflicts.extend(native_conflicts)
    block_edges = _reconcile_block_edges(raw_block_edges, declarations, diagnostics)
    edges = native_edges + block_edges
    edges.sort(key=lambda item: (item["from"], item["kind"], item["to"]))
    gaps = [
        {"file": file, "missing": sorted(missing), "kind": "block-adoption"}
        for file, missing in sorted(missing_by_file.items())
    ]
    discovery.sort(key=lambda item: item["file"])
    diagnostics.sort(key=lambda item: (str(item.get("source", {}).get("file", item.get("source", {}).get("address", ""))), item["code"], item["message"]))

    snapshot_entries = [
        f"{item['file']}\0{item.get('content_sha256', 'hmmm')}\0{item['status']}"
        for item in discovery
    ]
    snapshot_sha256 = _sha256("\n".join(snapshot_entries))
    statuses = Counter(item["status"] for item in discovery)
    reader_runs = []
    for manifest in READER_MANIFESTS:
        reader_id = manifest["reader_id"]
        matched = reader_counts[reader_id]
        reader_runs.append({
            "reader_id": reader_id,
            "reader_version": manifest["version"],
            "support": manifest["support"],
            "status": "applied" if matched else "not-applicable",
            "files_matched": matched,
            "facts_emitted": reader_fact_counts[reader_id],
        })

    return {
        "schema": SCHEMA_ID,
        "schema_version": SCHEMA_VERSION,
        "capabilities": [
            "native-facts",
            "supplemental-msdmd-blocks",
            "source-qualified-identities",
            "duplicate-id-diagnostics",
            "discovery-accounting",
        ],
        "repo": repo,
        "source": {
            "repository": repo,
            "revision": revision,
            "git_head": git_head or "hmmm",
            "dirty_worktree": dirty,
            "snapshot_sha256": snapshot_sha256,
            "snapshot_complete": not any(item["status"] in {"unreadable", "excluded"} and item.get("content_sha256") == "hmmm" for item in discovery),
        },
        "reader_manifests": list(READER_MANIFESTS),
        "reader_runs": reader_runs,
        "discovery": discovery,
        "declarations": declarations,
        "facts": facts,
        "gaps": gaps,
        "edges": edges,
        "conflicts": conflicts,
        "diagnostics": diagnostics,
        "coverage": {
            "denominator": {"kind": "discovered-files", "count": len(discovery)},
            "supported_files": statuses["supported"],
            "partial_files": statuses["partial"],
            "unsupported_files": statuses["unsupported"],
            "invalid_files": statuses["invalid"],
            "excluded_files": statuses["excluded"],
            "unreadable_files": statuses["unreadable"],
            "native_facts": len(facts),
            "supplemental_declarations": len(declarations),
            "block_adoption": {block: len(block_files[block]) for block in block_names},
            "information_availability": "not-evaluated-without-obligation-policy",
            "verified_behavior": "not-evaluated",
        },
    }


def collect_legacy(
    root: Path,
    repo: str,
    *,
    block_names: Iterable[str] = DEFAULT_BLOCK_NAMES,
    expected_blocks: Iterable[str] = (),
    source_commit: str | None = None,
) -> dict[str, Any]:
    """Emit explicit schema-1 block-only compatibility output."""
    current = collect(
        root,
        repo,
        block_names=block_names,
        expected_blocks=expected_blocks,
        source_commit=source_commit,
        include_native=False,
    )
    declarations = [
        {"file": item["file"], "block": item["block"], "id": item["id"], "fields": item["fields"]}
        for item in current["declarations"]
    ]
    legacy_by_address = {item["address"]: item["id"] for item in current["declarations"]}
    edges = []
    for edge in current["edges"]:
        if "source_block" not in edge:
            continue
        edges.append({
            "from": legacy_by_address.get(edge["from"], edge["from"]),
            "to": legacy_by_address.get(edge["to"], edge["to"]),
            "kind": edge["kind"],
            "source_block": edge["source_block"],
            "source_id": edge["source_entry_id"],
        })
    result: dict[str, Any] = {
        "schema_version": LEGACY_SCHEMA_VERSION,
        "repo": repo,
        "declarations": declarations,
        "gaps": [{"file": item["file"], "missing": item["missing"]} for item in current["gaps"]],
        "edges": edges,
    }
    if source_commit:
        result["source_commit"] = source_commit
    return result


def collection_errors(collection: dict[str, Any]) -> list[dict[str, Any]]:
    """Return diagnostics that invalidate collection identity or syntax."""
    return [item for item in collection.get("diagnostics", []) if item.get("severity") == "error"]


def render_typescript(collection: dict[str, Any], *, import_path: str) -> str:
    """Render a schema-1 or schema-2 collection as a TypeScript module."""
    payload = json.dumps(collection, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
    helper = "defineMsdmdCollectionV2" if collection.get("schema_version") == SCHEMA_VERSION else "defineMsdmdCollection"
    return (
        f'import {{ {helper} }} from "{import_path}";\n\n'
        f"export default {helper}({payload});\n"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root to scan")
    parser.add_argument("--repo", required=True, help="repository slug for the collection")
    parser.add_argument("--out", type=Path, help="output .ts path; stdout when omitted")
    parser.add_argument("--block", action="append", dest="blocks", help="supplemental block name to collect; may be repeated")
    parser.add_argument("--expected-block", action="append", default=[], help="block expected on every supported line-comment file for adoption reporting")
    parser.add_argument("--import-path", default="./.agents/skills/msdmd/collection", help="TypeScript import path for the schema helper")
    parser.add_argument("--source-commit", help="source commit SHA to record; current git HEAD is detected when omitted")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES, help="per-file read boundary")
    parser.add_argument("--legacy-blocks-only", action="store_true", help="emit explicit schema-1 block-only compatibility output")
    parser.add_argument("--strict", action="store_true", help="exit nonzero after rendering if invalid identity or syntax diagnostics exist")
    args = parser.parse_args()

    if args.legacy_blocks_only:
        collection = collect_legacy(
            args.root,
            args.repo,
            block_names=args.blocks or DEFAULT_BLOCK_NAMES,
            expected_blocks=args.expected_block,
            source_commit=args.source_commit,
        )
    else:
        collection = collect(
            args.root,
            args.repo,
            block_names=args.blocks or DEFAULT_BLOCK_NAMES,
            expected_blocks=args.expected_block,
            source_commit=args.source_commit,
            max_file_bytes=args.max_file_bytes,
        )
    rendered = render_typescript(collection, import_path=args.import_path)
    if args.out:
        args.out.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    if args.strict and not args.legacy_blocks_only and collection_errors(collection):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
