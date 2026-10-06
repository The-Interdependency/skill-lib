# ratios: loc_comments=895:91 imports_exports=19:8 calls_definitions=295:26
# === DOCS ===
# id: msdmd_foundational_contract
#   source: msdmd/SKILL.md
#   catalogue: msdmd/references/metadata-conventions.md
#   summary: Native-first metadata collection with source-qualified facts, diagnostics, and coverage policy. Supplemental blocks express otherwise unexpressed information.
# === END DOCS ===
# === CAPABILITIES ===
# id: repo_collection_generator
#   exposes: collect, render_typescript, collection_errors
#   summary: Produces schema-2 collections from registered native readers and supplemental blocks without executing inspected sources.
#   runner_scope: native-and-supplemental-blocks
#   native_ingestion: implemented-tested-subsets
#   limitations: Supported features and versions are reader-qualified; declarations and parsed reports do not prove runtime behavior. Required-source policy detects incomplete extraction.
# === END CAPABILITIES ===
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
#   tests: tests/test_collect.py, tests/test_native_collection.py, tests/test_msdmd_consumer_review.py
#   rollout: schema 2 is the default CLI output; --legacy-blocks-only keeps explicit schema 1 compatibility
#   rollback: use --legacy-blocks-only while preserving schema incompatibility visibility
# === END MODULE_BUILD ===
"""Generate a versioned native-first MSDMD collection.

Usage guidance:
    python -m msdmd.collect --root . --repo owner/repo --out repo_msdmd.ts
    python -m msdmd.collect --root . --repo owner/repo --strict
    python -m msdmd.collect --root . --repo owner/repo --legacy-blocks-only
    python -m msdmd.collect --print-generator-identity

Exit status: 1 drift under --check, 2 strict diagnostics, 3 missing native
reader runtime (unless --allow-missing-reader-runtimes), 4 incompatible
schema helper for the configured output.

The default schema-2 path statically reads supported native conventions and
supplemental MSDMD blocks. It never imports inspected code, executes scripts,
loads plugins, follows network references, or treats declarations as verified
behavior. The explicit legacy flag emits the previous block-only shape for old
consumers; it cannot silently represent native facts.
"""
from __future__ import annotations

import argparse
import fnmatch
import tempfile
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import io
import tokenize
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import quote

from msdmd.parsers.universal import marker_for, parse_text
from msdmd.readers import READER_MANIFESTS, _redact_sensitive, read_native, readers_for

SCHEMA_ID = "the-interdependency.msdmd-collection"
SCHEMA_VERSION = "2.0.0"
LEGACY_SCHEMA_VERSION = "1.0.0"
DEFAULT_MAX_FILE_BYTES = 2 * 1024 * 1024
# Aggregate bound on source bytes retained for readers during one scan.
DEFAULT_MAX_TOTAL_BYTES = 256 * 1024 * 1024
# Native reader runtimes whose absence makes extraction incomplete.
RUNTIME_UNAVAILABLE_CODES = frozenset({
    "missing_docstring_parser",
    "typescript_reader_unavailable",
    "reader_dependency_unavailable",
})
# tempfile.mkstemp(prefix=".msdmd-") names written by this CLI.
_COLLECTOR_TEMP_RE = re.compile(r"\.msdmd-[a-z0-9_]{8}")
# Hidden sibling temporaries/candidates of any collection artifact, such as
# ".repo_msdmd.ts.<random>.candidate" written by fresh-making executors.
_ARTIFACT_SIBLING_RE = re.compile(r"\..+_msdmd\.ts\..+")

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
    text = text.replace("\r\n", "\n").replace("\r", "\n")
    comments = [""] * len(text.split("\n"))
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


def _is_own_output(relative: str, configured: frozenset[str] | set[str]) -> bool:
    """Return whether ``relative`` is this collection's output or a temporary of it.

    Configured outputs, their hidden ``.<name>.*`` siblings, any hidden
    ``.*_msdmd.ts.*`` sibling, and this CLI's ``.msdmd-*`` atomic-write
    temporaries are never inputs, so differently named temporaries cannot
    change collection bytes.
    """
    if relative in configured:
        return True
    parent, _, name = relative.rpartition("/")
    if _COLLECTOR_TEMP_RE.fullmatch(name) or _ARTIFACT_SIBLING_RE.fullmatch(name):
        return True
    for output in configured:
        output_parent, _, output_name = output.rpartition("/")
        if parent == output_parent and name.startswith("." + output_name + "."):
            return True
    return False


def _git_visible_files(root: Path) -> set[str] | None:
    """Return tracked plus untracked, not-ignored files under ``root``.

    Git-ignored files are machine-local and may hold credentials; they are not
    part of a commit-bound or portable snapshot identity.
    """
    try:
        output = subprocess.run(
            ["git", "-C", str(root), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
        ).stdout
    except (OSError, subprocess.CalledProcessError):
        return None
    return {os.fsdecode(item) for item in output.split(b"\0") if item}


def _git_identity(
    root: Path,
    explicit_revision: str | None,
    ignored_changes: Iterable[str] = (),
    configured_outputs: frozenset[str] | set[str] = frozenset(),
) -> tuple[str, bool | str, str | None]:
    revision = explicit_revision
    dirty: bool | str = "hmmm"
    git_head: str | None = None
    ignored_changes = set(ignored_changes)
    try:
        git_head = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if revision is None:
            revision = git_head
        prefix = subprocess.run(
            ["git", "-C", str(root), "rev-parse", "--show-prefix"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        status_output = subprocess.run(
            ["git", "-C", str(root), "status", "--porcelain=v1", "-z", "--untracked-files=all", "--", "."],
            check=True,
            capture_output=True,
        ).stdout
        records = [os.fsdecode(item) for item in status_output.split(b"\0")]
        input_changes = []
        index = 0
        while index < len(records):
            record = records[index]
            index += 1
            if len(record) < 4:
                continue
            if record[0] in "RC":
                index += 1  # the rename/copy source path follows
            changed_path = record[3:]
            if prefix and changed_path.startswith(prefix):
                changed_path = changed_path[len(prefix):]
            if (Path(changed_path).name.endswith("_msdmd.ts") or changed_path in ignored_changes
                    or _is_own_output(changed_path, configured_outputs)):
                continue
            input_changes.append(changed_path)
        dirty = bool(input_changes)
    except (OSError, subprocess.CalledProcessError):
        pass
    return revision or "hmmm", dirty, git_head


def _discover(
    root: Path,
    max_file_bytes: int,
    generated_outputs: Iterable[str] = (),
    *,
    stable_exclusions: bool = False,
    recorded_outputs: Iterable[str] | None = None,
    visible_files: set[str] | None = None,
    excluded_inodes: Iterable[tuple[int, int]] = (),
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    own_outputs: list[str] | None = None,
) -> tuple[list, list, list]:
    """Read bounded files through directory descriptors; never follow symlinks.

    Own outputs and temporaries are skipped without a ledger entry because
    their names vary per run. Git-ignored files are skipped the same way when
    ``visible_files`` is known. Only bytes that a reader or block marker can
    consume are retained, and the retained total is bounded.
    """
    if max_file_bytes < 1:
        raise ValueError("max_file_bytes must be positive")
    if max_total_bytes < 1:
        raise ValueError("max_total_bytes must be positive")
    readable: list = []
    ledger: list = []
    diagnostics: list = []
    configured = frozenset(generated_outputs)
    excluded_inodes = set(excluded_inodes)
    own_outputs = own_outputs if own_outputs is not None else []
    visible_dirs: set[str] | None = None
    if visible_files is not None:
        visible_dirs = set()
        for visible in visible_files:
            parent = visible.rpartition("/")[0]
            while parent and parent not in visible_dirs:
                visible_dirs.add(parent)
                parent = parent.rpartition("/")[0]
    retained_total = [0]
    over_budget: list[str] = []
    if not hasattr(os, "O_NOFOLLOW") or not hasattr(os, "O_DIRECTORY"):
        raise OSError("safe native discovery requires no-follow directory descriptor support")

    def excluded(relative: str, reason: str, *, entry_kind: str = "file", digest: str = "hmmm", size: int | None = None) -> None:
        item = {"file": relative, "entry_kind": entry_kind, "status": "excluded", "reason": reason,
                "reader_ids": [], "content_sha256": digest}
        if size is not None:
            item["size"] = size
        ledger.append(item)

    if stable_exclusions:
        for name in sorted(_DEFAULT_SKIP):
            excluded("**/" + name + "/**", "configured-subtree", entry_kind="subtree")
    for output in sorted(configured if recorded_outputs is None else set(recorded_outputs)):
        excluded(output, "generated-collection-output", entry_kind="output")

    def failed(relative: str, exc: Exception, entry_kind: str = "file") -> None:
        ledger.append({"file": relative, "entry_kind": entry_kind, "status": "unreadable", "reader_ids": [], "content_sha256": "hmmm"})
        diagnostics.append({"code": "unreadable_path", "severity": "error", "status": "unreadable",
            "message": type(exc).__name__, "source": {"file": relative}, "reader_id": None})

    def visit(directory_fd: int, parent: str = "") -> None:
        try:
            names = sorted(os.listdir(directory_fd))
        except OSError as exc:
            failed(parent or ".", exc, "subtree")
            return
        for name in names:
            relative = f"{parent}/{name}" if parent else name
            try:
                if _is_own_output(relative, configured):
                    own_outputs.append(relative)
                    continue
                mode = os.stat(name, dir_fd=directory_fd, follow_symlinks=False).st_mode
                if stat.S_ISLNK(mode):
                    if visible_files is not None and relative not in visible_files:
                        continue
                    excluded(relative, "symlink-not-followed", digest=_sha256(os.readlink(name, dir_fd=directory_fd)))
                    continue
                if stat.S_ISDIR(mode):
                    if name in _DEFAULT_SKIP:
                        if not stable_exclusions:
                            excluded(relative, "configured-subtree", entry_kind="subtree")
                    elif visible_dirs is not None and relative not in visible_dirs:
                        continue
                    else:
                        child = os.open(name, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW, dir_fd=directory_fd)
                        try:
                            visit(child, relative)
                        finally:
                            os.close(child)
                    continue
                if visible_files is not None and relative not in visible_files:
                    continue
                if not stat.S_ISREG(mode):
                    excluded(relative, "not-regular-file")
                    continue
                if name.endswith("_msdmd.ts"):
                    excluded(relative, "generated-collection-output")
                    continue
                if name.startswith(".env") or name.endswith((".pem", ".key")):
                    excluded(relative, "secret-file-disclosure-boundary")
                    continue
                fd = os.open(name, os.O_RDONLY | os.O_NOFOLLOW | os.O_NONBLOCK, dir_fd=directory_fd)
                with os.fdopen(fd, "rb") as handle:
                    info = os.fstat(handle.fileno())
                    if (info.st_dev, info.st_ino) in excluded_inodes:
                        own_outputs.append(relative)
                        continue
                    if not stat.S_ISREG(info.st_mode):
                        excluded(relative, "not-regular-file")
                        continue
                    if info.st_size > max_file_bytes:
                        excluded(relative, "size-limit", size=info.st_size)
                        continue
                    data = handle.read(max_file_bytes + 1)
                    if len(data) > max_file_bytes:
                        excluded(relative, "size-limit", size=len(data))
                        continue
                digest = _sha256(data)
                relative_path = Path(relative)
                if not readers_for(relative_path, data) and marker_for(relative_path) is None:
                    # No reader or block grammar consumes these bytes; keep identity only.
                    readable.append({"file": relative, "data": b"", "content_sha256": digest, "size": len(data)})
                    continue
                if retained_total[0] + len(data) > max_total_bytes:
                    excluded(relative, "aggregate-size-limit", digest=digest, size=len(data))
                    over_budget.append(relative)
                    continue
                retained_total[0] += len(data)
                readable.append({"file": relative, "data": data, "content_sha256": digest, "size": len(data)})
            except OSError as exc:
                failed(relative, exc)
    try:
        root_fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    except OSError as exc:
        failed(".", exc, "subtree")
    else:
        try:
            visit(root_fd)
        finally:
            os.close(root_fd)
    if over_budget:
        diagnostics.append({"code": "aggregate_size_limit", "severity": "error", "status": "unreadable",
            "message": f"{len(over_budget)} file(s) not read after the {max_total_bytes}-byte aggregate scan budget",
            "source": {"file": over_budget[0], "files": over_budget}, "reader_id": None})
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
    snapshot_identity: bool = False,
    generated_outputs: Iterable[str] = (),
    required_sources: Iterable[str] = (),
    required_facts: Iterable[dict[str, str]] = (),
    max_total_bytes: int = DEFAULT_MAX_TOTAL_BYTES,
    excluded_inodes: Iterable[tuple[int, int]] = (),
) -> dict[str, Any]:
    """Collect native facts and supplemental blocks under ``root`` as schema 2."""
    root = root.resolve()
    block_names = tuple(block_names)
    expected_blocks = tuple(expected_blocks)
    canonical_output = repo.rsplit("/", 1)[-1] + "_msdmd.ts"
    outputs = frozenset(generated_outputs) | {canonical_output}
    own_outputs: list[str] = []
    readable, discovery, diagnostics = _discover(
        root, max_file_bytes, outputs, stable_exclusions=snapshot_identity,
        # Only the stable artifact name is recorded; per-run output names are not.
        recorded_outputs={canonical_output}, visible_files=_git_visible_files(root),
        excluded_inodes=excluded_inodes, max_total_bytes=max_total_bytes, own_outputs=own_outputs,
    )
    revision, dirty, git_head = _git_identity(root, source_commit, own_outputs, outputs)
    required_sources = tuple(required_sources)
    required_facts = tuple(required_facts)
    for requirement in required_facts:
        if set(requirement) != {"file", "convention", "kind"} or not all(isinstance(v, str) and v for v in requirement.values()):
            raise ValueError("fact requirements must contain nonempty file, convention and kind strings")
    codeowners_source = next((name for name in (".github/CODEOWNERS", "CODEOWNERS", "docs/CODEOWNERS") if any(item["file"] == name for item in readable)), None)
    if snapshot_identity:
        if source_commit is not None:
            raise ValueError("snapshot identity and an explicit commit cannot both be selected")
        source_bytes = "\n".join(item["file"] + "\0" + item["content_sha256"] for item in sorted(readable, key=lambda x: x["file"]))
        revision = "snapshot:" + _sha256(source_bytes)
        dirty, git_head = "hmmm", None
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
            "codeowners_source": codeowners_source,
        }
        reader_ids, file_facts, file_edges, file_diagnostics = (
            read_native(relative_path, item["data"], context)
            if include_native
            else ([], [], [], [])
        )
        file_statuses = {diagnostic.get("status") for diagnostic in file_diagnostics}
        if "invalid" in file_statuses:
            status = "invalid"
        elif file_statuses & {"unsupported", "ambiguous", "dynamic-unresolved"} and file_facts:
            status = "partial"
        elif "dynamic-unresolved" in file_statuses:
            status = "partial"
        elif file_statuses & {"unsupported", "ambiguous"}:
            status = "unsupported"
        else:
            status = "supported" if reader_ids else "unsupported"
        discovery.append({
            "file": relative,
            "entry_kind": "file",
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
        if include_native and relative_path.suffix.lower() in {".js", ".jsx", ".ts", ".tsx", ".mjs", ".cjs", ".mts", ".cts", ".rs", ".java", ".c", ".cpp", ".cc", ".cxx", ".hpp", ".hxx", ".h"}:
            comments_available = any(f['kind'] == 'comment' and f['extraction']['reader_id'] in {'typescript-compiler', 'native-grammars'} for f in file_facts)
            if not comments_available and file_statuses & {'unsupported', 'ambiguous', 'invalid'}:
                candidates = []
                for candidate_block in block_names:
                    for entry in parse_text(text, candidate_block, marker):
                        candidate, _ = _redact_sensitive({'block': candidate_block, 'entry': entry})
                        candidates.append(candidate)
                if candidates:
                    diagnostics.append({'code': 'supplemental_comment_extraction_unavailable', 'severity': 'error', 'status': 'unsupported',
                        'message': 'block-shaped candidates retained without certifying comment origin; install or select the native parser',
                        'source': {'file': relative, 'content_sha256': item['content_sha256'], 'candidate_standing': 'unverified', 'candidate_blocks': candidates},
                        'reader_id': 'msdmd-block'})
            lines = [""] * len(text.split("\n"))
            for fact in file_facts:
                if fact["kind"] == "comment" and fact["extraction"]["reader_id"] in {"typescript-compiler", "native-grammars"}:
                    for offset, line in enumerate(fact["native"]["value"]["text"].split("\n")):
                        index = fact["source"]["location"]["start_line"] - 1 + offset
                        if index < len(lines):
                            lines[index] = line
            block_text = "\n".join(lines)
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
    statuses = Counter(item["status"] for item in discovery if item.get("entry_kind", "file") == "file")
    for pattern in required_sources:
        matches = [item for item in discovery if item.get("entry_kind", "file") == "file" and fnmatch.fnmatchcase(item["file"], pattern)]
        bad = [item for item in matches if item["status"] != "supported"]
        if not matches or bad:
            diagnostics.append({"code": "required_source_not_supported", "severity": "error", "status": "unsupported",
                "message": "required source pattern has no matches or incomplete extraction: " + pattern,
                "source": {"file": pattern, "matches": [{"file": i["file"], "status": i["status"]} for i in matches]}, "reader_id": None})
    requirements = []
    for requirement in required_facts:
        matches = [item for item in discovery if item.get("entry_kind", "file") == "file" and fnmatch.fnmatchcase(item["file"], requirement["file"])]
        results = []
        for item in matches:
            witnesses = [fact["address"] for fact in facts if fact["source"]["file"] == item["file"] and fact["convention"]["namespace"] == requirement["convention"] and fact["kind"] == requirement["kind"]]
            status = "provided" if witnesses and item["status"] == "supported" else "unresolved" if item["status"] != "supported" else "not-found-in-extracted-subset"
            results.append({"file": item["file"], "status": status, "witnesses": witnesses})
        status = "provided" if results and all(r["status"] == "provided" for r in results) else "unresolved"
        requirements.append({**requirement, "status": status, "sources": results})
        if status != "provided":
            diagnostics.append({"code": "required_fact_unresolved", "severity": "error", "status": "unsupported",
                "message": "required native fact is not supported by complete source extraction",
                "source": dict(requirement), "reader_id": None})
    runtime_unavailable_readers: set[str] = set()
    for diagnostic in diagnostics:
        if diagnostic.get("code") in RUNTIME_UNAVAILABLE_CODES:
            # Missing runtimes make output incomplete, never an accepted subset.
            diagnostic["severity"] = "error"
            runtime_unavailable_readers.add(str(diagnostic.get("reader_id")))
    reader_runs = []
    for manifest in READER_MANIFESTS:
        reader_id = manifest["reader_id"]
        matched = reader_counts[reader_id]
        reader_runs.append({
            "reader_id": reader_id,
            "reader_version": manifest["version"],
            "support": manifest["support"],
            "status": "runtime-unavailable" if reader_id in runtime_unavailable_readers else "applied" if matched else "not-applicable",
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
            "snapshot_complete": not any(item["status"] == "unreadable" or (item["status"] == "excluded" and item.get("reason") not in {"configured-subtree", "generated-collection-output"}) for item in discovery),
            "revision_kind": "content-snapshot" if snapshot_identity else "git-or-declared",
            "scope": "configured in-scope files; excluded subtrees are reported without traversing",
            "exclusion_accounting": "configured-patterns" if snapshot_identity else "observed-paths",
        },
        "requirements": requirements,
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
            "denominator": {"kind": "discovered-files", "count": sum(statuses.values())},
            "excluded_subtrees": sum(i.get("entry_kind") == "subtree" and i["status"] == "excluded" for i in discovery),
            "required_sources": list(required_sources),
            "supported_files": statuses["supported"],
            "partial_files": statuses["partial"],
            "unsupported_files": statuses["unsupported"],
            "invalid_files": statuses["invalid"],
            "excluded_files": statuses["excluded"],
            "unreadable_files": statuses["unreadable"],
            "native_facts": len(facts),
            "supplemental_declarations": len(declarations),
            "block_adoption": {block: len(block_files[block]) for block in block_names},
            "information_availability": "policy-evaluated" if required_facts else "not-evaluated-without-obligation-policy",
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


def runtime_unavailable(collection: dict[str, Any]) -> list[dict[str, Any]]:
    """Return diagnostics showing a native reader runtime was not installed."""
    return [item for item in collection.get("diagnostics", []) if item.get("code") in RUNTIME_UNAVAILABLE_CODES]


def generator_identity(base: Path | None = None) -> str:
    """Return ``sha256:<hex>`` over every collector input that can change output bytes.

    Covers the Python implementation, the trusted TypeScript worker, its npm
    manifest and lock file, reader schema assets and the pinned Python runtime
    requirements. Installed dependency trees and docs are excluded.
    """
    base = (base or Path(__file__).parent).resolve()
    files = sorted(
        path for path in base.rglob("*")
        if path.is_file()
        and not {"node_modules", "__pycache__", "references"} & set(path.relative_to(base).parts)
        and (path.suffix in {".py", ".cjs", ".json"} or path.name == "requirements.txt")
    )
    digest = hashlib.sha256()
    for path in files:
        digest.update(path.relative_to(base).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def helper_incompatibility(out: Path, import_path: str, rendered: str) -> tuple[str | None, bool]:
    """Check that the target's schema helper exports what ``rendered`` imports.

    Returns ``(problem, found)``. Bare module specifiers are not resolved.
    """
    if not import_path.startswith((".", "/")):
        return None, False
    first = rendered.split("\n", 1)[0]
    match = re.match(r"import \{ ([^}]+) \} from ", first)
    if not match:
        return None, False
    names = [name.strip() for name in match.group(1).split(",") if name.strip()]
    base = (out.parent / import_path) if not import_path.startswith("/") else Path(import_path)
    candidates = [base.with_name(base.name + ".ts"), base.with_name(base.name + ".d.ts"), base / "index.ts"]
    if base.suffix == ".ts":
        candidates.insert(0, base)
    for candidate in candidates:
        if candidate.is_file():
            text = candidate.read_text(encoding="utf-8", errors="replace")
            missing = [name for name in names if not re.search(r"\bexport\b[^;]*\b" + re.escape(name) + r"\b", text)]
            if missing:
                return (f"schema helper {candidate} does not export {', '.join(missing)}; propagate the "
                        "current msdmd skill to the target or regenerate with --legacy-blocks-only"), True
            return None, True
    return None, False


def render_typescript(collection: dict[str, Any], *, import_path: str) -> str:
    """Render a schema-1 or schema-2 collection as a TypeScript module."""
    helper = "defineMsdmdCollectionV2" if collection.get("schema_version") == SCHEMA_VERSION else "defineMsdmdCollection"
    imports = helper
    if helper == "defineMsdmdCollectionV2" and len(collection.get("facts", [])) > 64:
        # Bound TypeScript contextual inference without casts or losing type checks.
        imports += ", mergeMsdmdFactChunks"
        parts = []
        for key, value in sorted(collection.items()):
            if key == "facts":
                chunks = [json.dumps(value[i:i + 64], indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
                          for i in range(0, len(value), 64)]
                rendered = "mergeMsdmdFactChunks(\n" + ",\n".join(chunks) + "\n)"
            else:
                rendered = json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
            parts.append("  " + json.dumps(key) + ": " + rendered.replace("\n", "\n  "))
        payload = "{\n" + ",\n".join(parts) + "\n}"
    else:
        payload = json.dumps(collection, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False)
    return f'import {{ {imports} }} from "{import_path}";\n\nexport default {helper}({payload});\n'


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="repository root to scan")
    parser.add_argument("--repo", help="repository slug for the collection (required unless --print-generator-identity)")
    parser.add_argument("--out", type=Path, help="output .ts path; stdout when omitted")
    parser.add_argument("--block", action="append", dest="blocks", help="supplemental block name to collect; may be repeated")
    parser.add_argument("--expected-block", action="append", default=[], help="block expected on every supported line-comment file for adoption reporting")
    parser.add_argument("--import-path", default="./.agents/skills/msdmd/collection", help="TypeScript import path for the schema helper")
    parser.add_argument("--source-commit", help="source commit SHA to record; current git HEAD is detected when omitted")
    parser.add_argument("--max-file-bytes", type=int, default=DEFAULT_MAX_FILE_BYTES, help="per-file read boundary")
    parser.add_argument("--legacy-blocks-only", action="store_true", help="emit explicit schema-1 block-only compatibility output")
    parser.add_argument("--snapshot-identity", action="store_true", help="bind generated output to source bytes rather than a circular output commit")
    parser.add_argument("--require-source", action="append", default=[], help="glob that must have matched, fully extracted inputs; repeat as needed")
    parser.add_argument("--require-fact", action="append", default=[], help="required fileglob::convention::kind, repeated as needed")
    parser.add_argument("--json", action="store_true", help="emit raw collection JSON instead of TypeScript")
    parser.add_argument("--check", action="store_true", help="compare --out without writing; nonzero on drift")
    parser.add_argument("--strict", action="store_true", help="exit nonzero after rendering if invalid identity or syntax diagnostics exist")
    parser.add_argument("--max-total-bytes", type=int, default=DEFAULT_MAX_TOTAL_BYTES, help="aggregate bound on source bytes retained for readers")
    parser.add_argument("--allow-missing-reader-runtimes", action="store_true", help="write incomplete output when native reader runtimes are absent (still warns)")
    parser.add_argument("--print-generator-identity", action="store_true", help="print the collector implementation identity and exit")
    args = parser.parse_args()
    if args.print_generator_identity:
        print(generator_identity())
        return 0
    if not args.repo:
        parser.error("--repo is required")

    required_facts = []
    for value in args.require_fact:
        parts = value.split("::")
        if len(parts) != 3 or not all(parts):
            parser.error("--require-fact must be fileglob::convention::kind")
        required_facts.append(dict(zip(("file", "convention", "kind"), parts)))
    if args.legacy_blocks_only and (args.require_source or required_facts or args.snapshot_identity):
        parser.error("legacy output cannot represent native coverage policies or snapshot identity")
    if args.legacy_blocks_only:
        collection = collect_legacy(
            args.root,
            args.repo,
            block_names=args.blocks or DEFAULT_BLOCK_NAMES,
            expected_blocks=args.expected_block,
            source_commit=args.source_commit,
        )
    else:
        excluded_inodes = []
        if not args.out:
            # A shell redirect into the scanned tree is the output, not an input.
            try:
                info = os.fstat(sys.stdout.fileno())
            except (OSError, ValueError, AttributeError):
                info = None
            if info is not None and stat.S_ISREG(info.st_mode):
                excluded_inodes.append((info.st_dev, info.st_ino))
        collection = collect(
            args.root,
            args.repo,
            block_names=args.blocks or DEFAULT_BLOCK_NAMES,
            expected_blocks=args.expected_block,
            source_commit=args.source_commit,
            max_file_bytes=args.max_file_bytes,
            snapshot_identity=args.snapshot_identity,
            generated_outputs=[args.out.resolve().relative_to(args.root.resolve()).as_posix()] if args.out and args.out.resolve().is_relative_to(args.root.resolve()) else [],
            required_sources=args.require_source,
            required_facts=required_facts,
            max_total_bytes=args.max_total_bytes,
            excluded_inodes=excluded_inodes,
        )
        missing_runtimes = runtime_unavailable(collection)
        if missing_runtimes:
            readers = sorted({str(item.get("reader_id")) for item in missing_runtimes})
            files = {str(item.get("source", {}).get("file")) for item in missing_runtimes}
            print(f"msdmd: ERROR: native reader runtime unavailable ({', '.join(readers)}) for {len(files)} file(s); "
                  "the collection is incomplete. Install msdmd/requirements.txt and run npm ci --prefix msdmd.",
                  file=sys.stderr)
            if not args.allow_missing_reader_runtimes:
                return 3
            print("msdmd: WARNING: --allow-missing-reader-runtimes set; writing incomplete output.", file=sys.stderr)
    rendered = json.dumps(collection, indent=2, sort_keys=True, ensure_ascii=False, allow_nan=False) + "\n" if args.json else render_typescript(collection, import_path=args.import_path)
    if args.out and not args.json:
        problem, found = helper_incompatibility(args.out, args.import_path, rendered)
        if problem:
            print("msdmd: ERROR: " + problem, file=sys.stderr)
            return 4
        if not found and args.import_path.startswith("."):
            print(f"msdmd: WARNING: schema helper {args.import_path} not found relative to {args.out}", file=sys.stderr)
    if args.check:
        if not args.out:
            parser.error("--check requires --out")
        if not args.out.exists() or args.out.read_bytes() != rendered.encode("utf-8"):
            print("collection drift: " + str(args.out))
            return 1
    elif args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(prefix=".msdmd-", dir=args.out.parent)
        try:
            with os.fdopen(fd, "wb") as handle:
                handle.write(rendered.encode("utf-8"))
            os.replace(temporary, args.out)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    else:
        print(rendered, end="")
    if args.strict and not args.legacy_blocks_only and collection_errors(collection):
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
# ratios: loc_comments=895:91 imports_exports=19:8 calls_definitions=295:26
