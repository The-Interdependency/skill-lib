# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
# === MODULE_BUILD ===
# id: msdmd_native_reader_registry
#   module_name: readers
#   module_kind: instrument
#   summary: statically extracts supported native metadata conventions into provenance-bearing MSDMD facts
#   owner: The Interdependency skill-lib
#   public_surface: READER_MANIFESTS, readers_for, reader_for, read_native
#   internal_surface: convention-specific pure readers and source-qualified fact helpers
#   auth_boundary: none
#   storage_boundary: read
#   network_boundary: none
#   user_data_boundary: read
#   admin_only: false
#   tests: tests/test_native_collection.py
#   rollout: enable through msdmd.collect schema 2 collections
#   rollback: retain schema 1 block-only consumers while removing the schema 2 runner claim
# === END MODULE_BUILD ===
"""Static native metadata readers used by :mod:`msdmd.collect`.

Usage guidance:
    Call ``read_native(path, bytes, context)`` only with bytes already bounded
    by the collector. Readers never import inspected Python, execute scripts,
    expand templates, or resolve network references. ``READER_MANIFESTS`` is
    emitted in every collection so consumers can negotiate the exact supported
    subset instead of treating file recognition as full language support.

The registry intentionally implements conventions exercised by skill-lib and
the MSDMD worked example: Python syntax/docstrings/imports, RATIOS boundary
lines, JSON documents, TOML manifests, Markdown YAML frontmatter, safe YAML and
JavaScript/TypeScript subsets, GitHub CODEOWNERS, shell declarations, systemd
units, Git ignore rules, Python requirements files, bounded license detection,
SVG document metadata, and root ``llms.txt`` structure. Unmatched inputs stay
visible in the collection discovery ledger as unsupported ``hmmm`` scope.
"""
from __future__ import annotations

import ast
import datetime as dt
import hashlib
import io
import json
import math
import re
import shlex
import sys
import tokenize
import tomllib
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path
from typing import Any, Callable
from urllib.parse import quote

from msdmd.parsers.universal import marker_for, parse_ratios, ratios_placement

READER_MANIFESTS: tuple[dict[str, Any], ...] = (
    {
        "reader_id": "python-ast",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_python",
        "dependencies": ["python-stdlib:ast", "python-stdlib:tokenize"],
        "convention": "python.source-metadata",
        "specification": "https://docs.python.org/3/reference/",
        "supported_versions": ["Python 3 syntax accepted by the running ast parser"],
        "feature_subset": ["module and symbol docstrings", "signatures", "annotations", "decorators", "imports", "static __all__"],
        "detection": [".py", ".pyi", ".pyw"],
        "scope_attachment": "module and qualified symbol",
        "unknown_field_policy": "preserve source expression or emit dynamic-unresolved diagnostic",
        "execution_policy": "parse only; never import or evaluate",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "msdmd-ratios",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_ratios",
        "dependencies": ["msdmd.parsers.universal"],
        "convention": "msdmd.ratios-line",
        "specification": "The-Interdependency/skill-lib ratios/SKILL.md",
        "supported_versions": ["named ratios line v1"],
        "feature_subset": ["opening/closing placement", "named ratio/value preservation"],
        "detection": ["supported line-comment source containing ratios:"],
        "scope_attachment": "file boundary occurrence",
        "unknown_field_policy": "preserve hmmm as an explicit value",
        "execution_policy": "text parse only; never run ratio computers",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "json-stdlib",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_json",
        "dependencies": ["python-stdlib:json"],
        "convention": "json.document",
        "specification": "RFC 8259",
        "supported_versions": ["RFC 8259 JSON"],
        "feature_subset": ["complete typed document tree", "package.json dependency classes"],
        "detection": [".json"],
        "scope_attachment": "document and JSON Pointer",
        "unknown_field_policy": "preserve in typed document tree",
        "execution_policy": "parse only; no reference resolution",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "toml-stdlib",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_toml",
        "dependencies": ["python-stdlib:tomllib"],
        "convention": "toml.document",
        "specification": "TOML 1.0.0 and Python packaging metadata specifications",
        "supported_versions": ["TOML accepted by the running tomllib parser"],
        "feature_subset": ["complete typed document tree", "pyproject project/build dependency classes"],
        "detection": [".toml"],
        "scope_attachment": "document and TOML key path",
        "unknown_field_policy": "preserve in typed document tree",
        "execution_policy": "parse only; never invoke build backends",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "markdown-frontmatter",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_markdown",
        "dependencies": [],
        "convention": "markdown.yaml-frontmatter",
        "specification": "project-local flat YAML frontmatter convention",
        "supported_versions": ["flat scalar frontmatter with folded or literal scalar continuations"],
        "feature_subset": ["frontmatter", "generated-source notice"],
        "detection": [".md", ".mdx"],
        "scope_attachment": "document",
        "unknown_field_policy": "retain raw frontmatter and diagnose unsupported nested syntax",
        "execution_policy": "text parse only; never execute MDX",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "yaml-safe-subset",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_yaml",
        "dependencies": [],
        "convention": "yaml.safe-structural-subset",
        "specification": "YAML 1.2 structural subset documented by reader fixtures",
        "supported_versions": ["indent mappings/sequences, flow JSON, plain/quoted scalars, block scalars"],
        "feature_subset": ["CI and configuration structure without tags, anchors, aliases, or merge keys"],
        "known_limitations": ["not a general YAML implementation"],
        "detection": [".yml", ".yaml"],
        "scope_attachment": "document and structural path",
        "unknown_field_policy": "diagnose unsupported syntax; preserve raw source by digest",
        "execution_policy": "text parse only; no tags, templates, actions, or includes",
        "support": "partial",
    },
    {
        "reader_id": "typescript-static",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_typescript",
        "dependencies": [],
        "convention": "typescript.source-metadata",
        "specification": "ECMAScript module syntax and TypeScript declaration syntax",
        "supported_versions": ["line-anchored static import/export/declaration subset"],
        "feature_subset": ["static imports", "exported named declarations", "adjacent documentation comments"],
        "known_limitations": ["not a full JavaScript/TypeScript parser", "JSDoc versus TSDoc dialect remains ambiguous"],
        "detection": [".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"],
        "scope_attachment": "module and exported symbol",
        "unknown_field_policy": "preserve declaration/doc text and diagnose ambiguous documentation dialect",
        "execution_policy": "text parse only; never run modules or decorators",
        "support": "partial",
    },
    {
        "reader_id": "github-codeowners",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_codeowners",
        "dependencies": [],
        "convention": "github.codeowners",
        "specification": "https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-code-owners",
        "supported_versions": ["GitHub CODEOWNERS line grammar"],
        "feature_subset": ["ordered pattern and owner extraction"],
        "detection": ["CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"],
        "scope_attachment": "ordered path rule",
        "unknown_field_policy": "diagnose malformed rules; do not infer operational ownership",
        "execution_policy": "text parse only",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "shell-static",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_shell",
        "dependencies": [],
        "convention": "shell.source-metadata",
        "specification": "POSIX shebang convention and ShellCheck directives",
        "supported_versions": ["declaration extraction only"],
        "feature_subset": ["shebang", "ShellCheck directives"],
        "detection": [".sh", ".bash", ".zsh", ".fish", "extensionless shebang scripts"],
        "scope_attachment": "file",
        "unknown_field_policy": "preserve directive text",
        "execution_policy": "text parse only; never source or execute",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "systemd-unit",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_systemd",
        "dependencies": [],
        "convention": "systemd.unit",
        "specification": "https://www.freedesktop.org/software/systemd/man/latest/systemd.syntax.html",
        "supported_versions": ["section/key/value declaration extraction"],
        "feature_subset": ["ordered sections", "repeated directives", "continuation lines"],
        "detection": [".service", ".socket", ".timer", ".path", ".target"],
        "scope_attachment": "unit section and directive occurrence",
        "unknown_field_policy": "preserve key/value and order without interpreting runtime effect",
        "execution_policy": "text parse only; never invoke systemd",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "gitignore-lines",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_gitignore",
        "dependencies": [],
        "convention": "git.ignore",
        "specification": "https://git-scm.com/docs/gitignore",
        "supported_versions": ["ordered pattern declarations"],
        "feature_subset": ["pattern order", "negation", "anchoring", "directory-only flag"],
        "detection": [".gitignore"],
        "scope_attachment": "repository path rule",
        "unknown_field_policy": "preserve pattern text without evaluating matches",
        "execution_policy": "text parse only; never invoke Git matching",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "python-requirements",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_requirements",
        "dependencies": [],
        "convention": "python.requirements-file",
        "specification": "PyPA requirements file format",
        "supported_versions": ["one-line requirement and option subset"],
        "feature_subset": ["requirement text", "package name", "options", "ordered source lines"],
        "known_limitations": ["does not resolve includes, environment markers, URLs, or indexes"],
        "detection": ["requirements*.txt", "constraints*.txt"],
        "scope_attachment": "requirements document line",
        "unknown_field_policy": "preserve text and redact URL credentials",
        "execution_policy": "text parse only; never install or resolve packages",
        "support": "partial",
    },
    {
        "reader_id": "license-text",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_license",
        "dependencies": [],
        "convention": "license.text",
        "specification": "SPDX license identifiers plus exact known license headers",
        "supported_versions": ["MPL-2.0 exact header", "SPDX-License-Identifier line"],
        "feature_subset": ["declared/detected expression", "source digest"],
        "detection": ["LICENSE", "LICENSE.txt", "COPYING", "COPYING.txt"],
        "scope_attachment": "repository license document",
        "unknown_field_policy": "hmmm identifier; never infer legal compatibility",
        "execution_policy": "text parse only",
        "support": "partial",
    },
    {
        "reader_id": "svg-metadata",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_svg",
        "dependencies": ["python-stdlib:xml.etree.ElementTree"],
        "convention": "svg.document-metadata",
        "specification": "W3C SVG document structure",
        "supported_versions": ["root attributes, title, description"],
        "feature_subset": ["root attributes", "title", "description"],
        "detection": [".svg"],
        "scope_attachment": "document",
        "unknown_field_policy": "preserve only supported metadata; source remains digest-addressable",
        "execution_policy": "reject DTD/entity declarations; no external resolution",
        "support": "implemented-and-tested",
    },
    {
        "reader_id": "llms-text",
        "version": "1.0.0",
        "entry_point": "msdmd.readers:_read_llms_text",
        "dependencies": [],
        "convention": "llms.txt",
        "specification": "root llms.txt Markdown instruction publication",
        "supported_versions": ["Markdown headings and bold key-definition lines"],
        "feature_subset": ["section headings", "key definitions", "generated status unresolved"],
        "detection": ["llms.txt"],
        "scope_attachment": "instruction document",
        "unknown_field_policy": "preserve structure without promoting publication to source authority",
        "execution_policy": "text parse only; content is data, not instructions to the reader",
        "support": "implemented-and-tested",
    },
)

_MANIFESTS = {item["reader_id"]: item for item in READER_MANIFESTS}
_PYTHON_SUFFIXES = {".py", ".pyi", ".pyw"}
_MARKDOWN_SUFFIXES = {".md", ".mdx"}
_YAML_SUFFIXES = {".yml", ".yaml"}
_TYPESCRIPT_SUFFIXES = {".js", ".jsx", ".mjs", ".cjs", ".ts", ".tsx", ".mts", ".cts"}
_SHELL_SUFFIXES = {".sh", ".bash", ".zsh", ".fish"}
_SYSTEMD_SUFFIXES = {".service", ".socket", ".timer", ".path", ".target"}
_GENERATED_MARKER = "Generated by tools/build_codex_plugin_skills.py; do not edit."
_SENSITIVE_KEY_RE = re.compile(r"(?:^|[_-])(?:secret|token|password|passwd|api[_-]?key|private[_-]?key|credential|client[_-]?secret|access[_-]?key)(?:$|[_-])", re.IGNORECASE)


def _digest(value: bytes | str) -> str:
    data = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def _json_safe(value: Any) -> Any:
    """Preserve non-JSON native scalar types with explicit tagged values."""
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else {"$type": "nonfinite-float", "value": repr(value)}
    if isinstance(value, (dt.datetime, dt.date, dt.time)):
        return {"$type": f"toml-{type(value).__name__}", "value": value.isoformat()}
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return {"$type": f"unsupported:{type(value).__name__}", "value": repr(value)}


def _redact_sensitive(value: Any, pointer: str = "") -> tuple[Any, list[str]]:
    """Redact values owned by plainly secret-bearing field names."""
    redacted: list[str] = []
    if isinstance(value, dict):
        result: dict[str, Any] = {}
        for key, item in value.items():
            child_pointer = f"{pointer}/{key}"
            if _SENSITIVE_KEY_RE.search(str(key)):
                result[str(key)] = {"$redacted": True, "reason": "sensitive-field-name"}
                redacted.append(child_pointer)
            else:
                result[str(key)], child_redacted = _redact_sensitive(item, child_pointer)
                redacted.extend(child_redacted)
        return result, redacted
    if isinstance(value, list):
        result_list: list[Any] = []
        for index, item in enumerate(value):
            child, child_redacted = _redact_sensitive(item, f"{pointer}/{index}")
            result_list.append(child)
            redacted.extend(child_redacted)
        return result_list, redacted
    return value, redacted


def _redaction_diagnostic(context: dict[str, Any], reader_id: str, pointers: list[str]) -> dict[str, Any] | None:
    if not pointers:
        return None
    return _diagnostic(
        context,
        reader_id=reader_id,
        code="sensitive_fields_redacted",
        message=f"withheld {len(pointers)} sensitive field value(s)",
        status="redacted",
        severity="warning",
    )


def _quoted(value: str, *, path: bool = False) -> str:
    return quote(value, safe="/" if path else "")


def _source(context: dict[str, Any], location: dict[str, Any]) -> dict[str, Any]:
    return {
        "repository": context["repo"],
        "revision": context["revision"],
        "file": context["file"],
        "content_sha256": context["content_sha256"],
        "location": location,
    }


def _subject_address(context: dict[str, Any], scope: str, identity: str) -> str:
    return (
        f"msdmd://{_quoted(context['repo'])}@{_quoted(context['revision'])}/{_quoted(context['file'], path=True)}"
        f"#subject/{_quoted(scope)}/{_quoted(identity)}"
    )


def _fact(
    context: dict[str, Any],
    *,
    reader_id: str,
    kind: str,
    scope: str,
    identity: str,
    location: dict[str, Any],
    value: Any,
    native_id: str | None = None,
    convention: str | None = None,
    standing: str = "syntactically-observed",
    projection: dict[str, Any] | None = None,
) -> dict[str, Any]:
    subject = _subject_address(context, scope, identity)
    pointer = location.get("pointer") or f"lines:{location.get('start_line', '?')}-{location.get('end_line', '?')}"
    native_component = f"/{_quoted(native_id)}" if native_id is not None else ""
    address = f"{subject}/fact/{_quoted(kind)}/{_quoted(str(pointer))}{native_component}"
    result = {
        "address": address,
        "origin": "native",
        "kind": kind,
        "source": _source(context, location),
        "subject": {
            "address": subject,
            "scope": scope,
            "identity": identity,
        },
        "convention": {
            "namespace": convention or _MANIFESTS[reader_id]["convention"],
            "version": context.get("convention_version", "hmmm"),
            "dialect": context.get("dialect", "hmmm"),
        },
        "native": {"id": native_id, "value": _json_safe(value)},
        "standing": standing,
        "extraction": {
            "reader_id": reader_id,
            "reader_version": _MANIFESTS[reader_id]["version"],
            "support": _MANIFESTS[reader_id]["support"],
            "configuration_sha256": context["configuration_sha256"],
        },
    }
    if projection is not None:
        result["projection"] = projection
    return result


def _diagnostic(
    context: dict[str, Any],
    *,
    reader_id: str,
    code: str,
    message: str,
    status: str,
    severity: str = "warning",
    location: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "code": code,
        "severity": severity,
        "status": status,
        "message": message,
        "source": _source(context, location or {"pointer": "document"}),
        "reader_id": reader_id,
    }


def _edge(source: str, target: str, kind: str, *, standing: str = "syntactically-observed") -> dict[str, Any]:
    return {
        "from": source,
        "to": target,
        "kind": kind,
        "standing": standing,
        "target_resolution": "external-or-unresolved",
    }


def _unparse(node: ast.AST | None) -> str | None:
    return None if node is None else ast.unparse(node)


def _arguments(arguments: ast.arguments) -> list[dict[str, Any]]:
    positional = list(arguments.posonlyargs) + list(arguments.args)
    default_offset = len(positional) - len(arguments.defaults)
    result: list[dict[str, Any]] = []
    for index, argument in enumerate(positional):
        result.append({
            "name": argument.arg,
            "kind": "positional_only" if index < len(arguments.posonlyargs) else "positional_or_keyword",
            "annotation": _unparse(argument.annotation),
            "default": _unparse(arguments.defaults[index - default_offset]) if index >= default_offset else None,
        })
    if arguments.vararg:
        result.append({"name": arguments.vararg.arg, "kind": "var_positional", "annotation": _unparse(arguments.vararg.annotation), "default": None})
    for argument, default in zip(arguments.kwonlyargs, arguments.kw_defaults):
        result.append({"name": argument.arg, "kind": "keyword_only", "annotation": _unparse(argument.annotation), "default": _unparse(default)})
    if arguments.kwarg:
        result.append({"name": arguments.kwarg.arg, "kind": "var_keyword", "annotation": _unparse(arguments.kwarg.annotation), "default": None})
    return result


def _read_python(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "python-ast"
    context = dict(context, convention_version=f"Python {sys.version_info.major}.{sys.version_info.minor}", dialect="python")
    facts: list[dict] = []
    edges: list[dict] = []
    diagnostics: list[dict] = []
    try:
        encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
        text = data.decode(encoding)
    except (SyntaxError, UnicodeDecodeError) as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    try:
        tree = ast.parse(text, filename=context["file"], type_comments=True)
    except SyntaxError as exc:
        location = {"start_line": exc.lineno or 1, "end_line": exc.end_lineno or exc.lineno or 1}
        return [], [], [_diagnostic(context, reader_id=reader_id, code="python_syntax_error", message=exc.msg, status="invalid", severity="error", location=location)]

    module_identity = context["file"]
    module_subject = _subject_address(context, "module", module_identity)
    doc = ast.get_docstring(tree, clean=False)
    if doc is not None and tree.body:
        owner = tree.body[0]
        facts.append(_fact(context, reader_id=reader_id, kind="documentation", scope="module", identity=module_identity, location={"start_line": owner.lineno, "end_line": getattr(owner, "end_lineno", owner.lineno)}, value={"text": doc, "format": "pep257"}, convention="python.pep257"))

    static_all: list[str] | None = None
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if any(isinstance(target, ast.Name) and target.id == "__all__" for target in targets):
                value_node = node.value
                try:
                    value = ast.literal_eval(value_node) if value_node is not None else None
                except (ValueError, TypeError, SyntaxError):
                    value = None
                if isinstance(value, (list, tuple)) and all(isinstance(item, str) for item in value):
                    static_all = list(value)
                    facts.append(_fact(context, reader_id=reader_id, kind="exports", scope="module", identity=module_identity, location={"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}, value={"names": static_all, "resolution": "static"}, native_id="__all__"))
                    for name in static_all:
                        edges.append(_edge(module_subject, f"python-symbol:{context['file']}#{name}", "exports"))
                else:
                    diagnostics.append(_diagnostic(context, reader_id=reader_id, code="dynamic_python_exports", message="__all__ is not a static list or tuple of strings", status="dynamic-unresolved", location={"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}))

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                location = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
                facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="module", identity=module_identity, location=location, value={"kind": "import", "module": alias.name, "alias": alias.asname}, native_id=alias.name, projection={"mapping_version": "python-imports@1", "relation": "imports", "loss": "none"}))
                edges.append(_edge(module_subject, f"python-module:{alias.name}", "imports"))
        elif isinstance(node, ast.ImportFrom):
            module = "." * node.level + (node.module or "")
            for alias in node.names:
                location = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
                target = f"{module}:{alias.name}"
                facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="module", identity=module_identity, location=location, value={"kind": "from_import", "module": module, "name": alias.name, "alias": alias.asname, "level": node.level}, native_id=target, projection={"mapping_version": "python-imports@1", "relation": "imports", "loss": "none"}))
                edges.append(_edge(module_subject, f"python-symbol:{target}", "imports"))

    def visit(body: list[ast.stmt], prefix: str = "") -> None:
        for node in body:
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            qualified = f"{prefix}.{node.name}" if prefix else node.name
            location = {"start_line": node.lineno, "end_line": getattr(node, "end_lineno", node.lineno)}
            if isinstance(node, ast.ClassDef):
                value = {
                    "name": node.name,
                    "qualified_name": qualified,
                    "kind": "class",
                    "bases": [_unparse(base) for base in node.bases],
                    "keywords": [{"name": item.arg, "value": _unparse(item.value)} for item in node.keywords],
                    "decorators": [_unparse(item) for item in node.decorator_list],
                }
                kind = "class-declaration"
            else:
                value = {
                    "name": node.name,
                    "qualified_name": qualified,
                    "kind": "async_function" if isinstance(node, ast.AsyncFunctionDef) else "function",
                    "parameters": _arguments(node.args),
                    "returns": _unparse(node.returns),
                    "decorators": [_unparse(item) for item in node.decorator_list],
                    "type_comment": node.type_comment,
                }
                kind = "callable-declaration"
            facts.append(_fact(context, reader_id=reader_id, kind=kind, scope="symbol", identity=qualified, location=location, value=value, native_id=qualified, projection={"mapping_version": "python-surfaces@1", "canonical_field": "declared_surface", "loss": "behavior not inferred"}))
            symbol_doc = ast.get_docstring(node, clean=False)
            if symbol_doc is not None and node.body:
                doc_node = node.body[0]
                facts.append(_fact(context, reader_id=reader_id, kind="documentation", scope="symbol", identity=qualified, location={"start_line": doc_node.lineno, "end_line": getattr(doc_node, "end_lineno", doc_node.lineno)}, value={"text": symbol_doc, "format": "pep257"}, convention="python.pep257"))
            visit(node.body, qualified)

    visit(tree.body)
    if static_all is None:
        facts.append(_fact(context, reader_id=reader_id, kind="exports", scope="module", identity=module_identity, location={"pointer": "implicit-public-names"}, value={"names": [item["native"]["value"]["name"] for item in facts if item["kind"] in {"class-declaration", "callable-declaration"} and "." not in item["subject"]["identity"] and not item["native"]["value"]["name"].startswith("_")], "resolution": "python-leading-underscore-convention"}, native_id=None, standing="derived", projection={"mapping_version": "python-public-names@1", "canonical_field": "declared_exports", "loss": "dynamic exports unresolved"}))
    return facts, edges, diagnostics


def _read_ratios(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "msdmd-ratios"
    marker = marker_for(path)
    if marker is None:
        return [], [], []
    context = dict(context, convention_version="named ratios line v1", dialect=f"line-comment:{marker}")
    try:
        if path.suffix.lower() in _PYTHON_SUFFIXES:
            encoding, _ = tokenize.detect_encoding(io.BytesIO(data).readline)
            source = data.decode(encoding)
            comments = [""] * len(source.splitlines())
            for token in tokenize.generate_tokens(io.StringIO(source).readline):
                if token.type == tokenize.COMMENT:
                    comments[token.start[0] - 1] = token.string
            text = "\n".join(comments)
        else:
            text = data.decode("utf-8")
    except (SyntaxError, UnicodeDecodeError, tokenize.TokenError, IndentationError) as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_ratios_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    diagnostics: list[dict] = []
    occurrence: Counter[str] = Counter()
    for line_number, line in enumerate(text.splitlines(), start=1):
        for entry in parse_ratios(line, marker):
            ratio_id = str(entry["id"])
            occurrence[ratio_id] += 1
            identity = f"{ratio_id}[{occurrence[ratio_id]}]"
            facts.append(_fact(context, reader_id=reader_id, kind="composition-ratio", scope="file", identity=identity, location={"start_line": line_number, "end_line": line_number}, value={"ratio": ratio_id, "value": str(entry["value"]), "occurrence": occurrence[ratio_id]}, native_id=ratio_id, convention="msdmd.ratios-line", standing="declared"))
    if facts:
        opening, closing = ratios_placement(text, marker)
        if not opening or not closing:
            diagnostics.append(_diagnostic(context, reader_id=reader_id, code="misplaced_ratios_boundary", message=f"opening={opening} closing={closing}", status="invalid", severity="error"))
    return facts, [], diagnostics


def _read_json(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "json-stdlib"
    context = dict(context, convention_version="RFC 8259", dialect="json")
    try:
        value = json.loads(data)
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="invalid_json", message=str(exc), status="invalid", severity="error")]
    value, redacted = _redact_sensitive(value)
    if path.name == "package.json":
        convention = "npm.package-json"
    elif path.name.endswith(".schema.json") or (isinstance(value, dict) and "$schema" in value):
        convention = "json.schema"
        context["convention_version"] = str(value.get("$schema", "hmmm")) if isinstance(value, dict) else "hmmm"
    elif isinstance(value, dict) and "openapi" in value:
        convention = "openapi.document"
        context["convention_version"] = str(value["openapi"])
    elif context["file"] == "skills.json":
        convention = "skill-lib.skills-index"
    elif context["file"] == ".codex-plugin/plugin.json":
        convention = "codex.plugin-manifest"
    elif context["file"] == ".claude-plugin/marketplace.json":
        convention = "claude.plugin-marketplace"
    else:
        convention = "json.document"
    facts = [_fact(context, reader_id=reader_id, kind="structured-document", scope="document", identity=context["file"], location={"pointer": ""}, value=value, convention=convention)]
    edges: list[dict] = []
    if path.name == "package.json" and isinstance(value, dict):
        subject = _subject_address(context, "document", context["file"])
        for field, kind in (("dependencies", "runtime"), ("devDependencies", "development"), ("peerDependencies", "peer"), ("optionalDependencies", "optional")):
            dependencies = value.get(field, {})
            if isinstance(dependencies, dict):
                for name, constraint in dependencies.items():
                    facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="package", identity=str(value.get("name", context["file"])), location={"pointer": f"/{field}/{name}"}, value={"name": name, "constraint": constraint, "class": kind}, native_id=name, convention=convention, projection={"mapping_version": "npm-dependencies@1", "relation": "depends_on", "loss": "none"}))
                    edges.append(_edge(subject, f"npm-package:{name}", f"depends_on:{kind}"))
    diagnostic = _redaction_diagnostic(context, reader_id, redacted)
    return facts, edges, [diagnostic] if diagnostic else []


def _read_toml(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "toml-stdlib"
    context = dict(context, convention_version="TOML 1.0.0", dialect="toml")
    try:
        value = tomllib.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, tomllib.TOMLDecodeError) as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="invalid_toml", message=str(exc), status="invalid", severity="error")]
    value, redacted = _redact_sensitive(value)
    convention = "python.pyproject" if path.name == "pyproject.toml" else "toml.document"
    facts = [_fact(context, reader_id=reader_id, kind="structured-document", scope="document", identity=context["file"], location={"pointer": ""}, value=value, convention=convention)]
    edges: list[dict] = []
    if path.name == "pyproject.toml":
        project = value.get("project", {}) if isinstance(value, dict) else {}
        package = str(project.get("name", context["file"])) if isinstance(project, dict) else context["file"]
        subject = _subject_address(context, "package", package)
        groups: list[tuple[str, Any, str]] = [
            ("/project/dependencies", project.get("dependencies", []) if isinstance(project, dict) else [], "runtime"),
            ("/build-system/requires", value.get("build-system", {}).get("requires", []) if isinstance(value.get("build-system", {}), dict) else [], "build"),
        ]
        optional = project.get("optional-dependencies", {}) if isinstance(project, dict) else {}
        if isinstance(optional, dict):
            groups.extend((f"/project/optional-dependencies/{group}", deps, f"optional:{group}") for group, deps in optional.items())
        for pointer, dependencies, kind in groups:
            if not isinstance(dependencies, list):
                continue
            for index, dependency in enumerate(dependencies):
                if not isinstance(dependency, str):
                    continue
                name = re.split(r"[<>=!~;\[\s]", dependency, maxsplit=1)[0]
                facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="package", identity=package, location={"pointer": f"{pointer}/{index}"}, value={"requirement": dependency, "name": name, "class": kind}, native_id=name, convention=convention, projection={"mapping_version": "pyproject-dependencies@1", "relation": "depends_on", "loss": "marker retained in requirement"}))
                edges.append(_edge(subject, f"python-package:{name}", f"depends_on:{kind}"))
    diagnostic = _redaction_diagnostic(context, reader_id, redacted)
    return facts, edges, [diagnostic] if diagnostic else []


def _parse_flat_frontmatter(raw: str) -> tuple[dict[str, Any], list[str]]:
    lines = raw.splitlines()
    result: dict[str, Any] = {}
    unsupported: list[str] = []
    index = 0
    while index < len(lines):
        line = lines[index]
        index += 1
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line.startswith((" ", "\t")) or ":" not in line:
            unsupported.append(line)
            continue
        key, raw_value = line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if value in {">", ">-", "|", "|-"}:
            parts: list[str] = []
            while index < len(lines) and (not lines[index] or lines[index].startswith((" ", "\t"))):
                parts.append(lines[index].strip())
                index += 1
            result[key] = "\n".join(parts).strip() if value.startswith("|") else " ".join(part for part in parts if part).strip()
        elif value.startswith(("[", "{")):
            try:
                result[key] = json.loads(value)
            except json.JSONDecodeError:
                unsupported.append(line)
                result[key] = value
        else:
            lowered = value.lower()
            if lowered in {"true", "false"}:
                result[key] = lowered == "true"
            elif lowered in {"null", "~"}:
                result[key] = None
            else:
                result[key] = value.strip('"\'')
    return result, unsupported


def _read_markdown(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "markdown-frontmatter"
    context = dict(context, convention_version="project-flat-v1", dialect="yaml-frontmatter")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    if not text.startswith("---\n"):
        return [], [], []
    end = text.find("\n---\n", 4)
    if end < 0:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="unterminated_frontmatter", message="opening YAML frontmatter has no closing fence", status="invalid", severity="error")]
    raw = text[4:end]
    value, unsupported = _parse_flat_frontmatter(raw)
    value, redacted = _redact_sensitive(value)
    standing = "derived" if _GENERATED_MARKER in text else "syntactically-observed"
    facts = [_fact(context, reader_id=reader_id, kind="frontmatter", scope="document", identity=context["file"], location={"start_line": 1, "end_line": raw.count("\n") + 3}, value={"fields": value, "raw_source": "source-reference", "generated": standing == "derived"}, convention="markdown.yaml-frontmatter", standing=standing)]
    diagnostics = []
    if unsupported:
        diagnostics.append(_diagnostic(context, reader_id=reader_id, code="unsupported_frontmatter_structure", message=f"{len(unsupported)} frontmatter line(s) exceed the supported flat subset", status="unsupported"))
    redaction = _redaction_diagnostic(context, reader_id, redacted)
    if redaction:
        diagnostics.append(redaction)
    return facts, [], diagnostics


def _yaml_scalar(value: str) -> Any:
    stripped = value.strip()
    if not stripped:
        return {}
    if stripped.startswith(("[", "{")):
        try:
            return json.loads(stripped)
        except json.JSONDecodeError:
            if stripped.startswith("[") and stripped.endswith("]"):
                return [part.strip().strip('"\'') for part in stripped[1:-1].split(",") if part.strip()]
            return stripped
    if stripped[0:1] in {"\"", "'"} and stripped[-1:] == stripped[0:1]:
        return stripped[1:-1]
    lowered = stripped.lower()
    if lowered in {"true", "false"}:
        return lowered == "true"
    if lowered in {"null", "~"}:
        return None
    if re.fullmatch(r"-?(?:0|[1-9][0-9]*)(?:\.[0-9]+)?", stripped):
        return float(stripped) if "." in stripped else int(stripped)
    return stripped


def _parse_yaml_subset(text: str) -> tuple[Any, list[str]]:
    """Parse the explicitly supported safe YAML subset without tag execution."""
    if re.search(r"(^|\s)(?:!\S*|&\S+|\*\S+|<<:)($|\s)", text, re.MULTILINE):
        raise ValueError("tags, anchors, aliases, and merge keys are unsupported")
    lines = text.splitlines()
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    unsupported: list[str] = []
    index = 0
    while index < len(lines):
        raw = lines[index]
        index += 1
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        indent = len(raw) - len(raw.lstrip(" "))
        if "\t" in raw[:indent]:
            unsupported.append(raw)
            continue
        content = raw[indent:]
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                unsupported.append(raw)
                continue
            item = content[2:].strip()
            if ":" in item and not item.startswith(("\"", "'")):
                key, rest = item.split(":", 1)
                child: dict[str, Any] = {key.strip(): _yaml_scalar(rest)}
                parent.append(child)
                stack.append((indent, child))
            else:
                parent.append(_yaml_scalar(item))
            continue
        if ":" not in content or not isinstance(parent, dict):
            unsupported.append(raw)
            continue
        key, rest = content.split(":", 1)
        key = key.strip().strip('"\'')
        rest = rest.strip()
        if rest in {"|", ">", "|-", ">-"}:
            block: list[str] = []
            while index < len(lines):
                next_raw = lines[index]
                next_indent = len(next_raw) - len(next_raw.lstrip(" "))
                if next_raw.strip() and next_indent <= indent:
                    break
                block.append(next_raw[indent + 2 :] if len(next_raw) >= indent + 2 else "")
                index += 1
            parent[key] = "\n".join(block).rstrip() if rest.startswith("|") else " ".join(part.strip() for part in block).strip()
            continue
        if rest:
            parent[key] = _yaml_scalar(rest)
            continue
        next_content = ""
        next_indent = -1
        look = index
        while look < len(lines):
            if lines[look].strip() and not lines[look].lstrip().startswith("#"):
                next_indent = len(lines[look]) - len(lines[look].lstrip(" "))
                next_content = lines[look][next_indent:]
                break
            look += 1
        child_value: Any = [] if next_indent > indent and next_content.startswith("- ") else {}
        parent[key] = child_value
        stack.append((indent, child_value))
    return root, unsupported


def _read_yaml(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "yaml-safe-subset"
    context = dict(context, convention_version="YAML 1.2 subset v1", dialect="safe-structural-subset")
    try:
        text = data.decode("utf-8")
        value, unsupported = _parse_yaml_subset(text)
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    except ValueError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="unsupported_yaml_feature", message=str(exc), status="unsupported", severity="warning")]
    value, redacted = _redact_sensitive(value)
    convention = "github.actions.workflow" if context["file"].startswith(".github/workflows/") else "yaml.document"
    facts = [_fact(context, reader_id=reader_id, kind="structured-document", scope="document", identity=context["file"], location={"pointer": ""}, value=value, convention=convention)]
    diagnostics = []
    if unsupported:
        diagnostics.append(_diagnostic(context, reader_id=reader_id, code="unsupported_yaml_lines", message=f"{len(unsupported)} line(s) exceed the supported YAML subset", status="unsupported"))
    redaction = _redaction_diagnostic(context, reader_id, redacted)
    if redaction:
        diagnostics.append(redaction)
    return facts, [], diagnostics


def _read_codeowners(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "github-codeowners"
    context = dict(context, convention_version="GitHub current documented grammar", dialect="github")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    diagnostics: list[dict] = []
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        try:
            parts = shlex.split(raw, comments=True, posix=True)
        except ValueError as exc:
            diagnostics.append(_diagnostic(context, reader_id=reader_id, code="invalid_codeowners_rule", message=str(exc), status="invalid", severity="error", location={"start_line": line_number, "end_line": line_number}))
            continue
        if len(parts) < 2:
            diagnostics.append(_diagnostic(context, reader_id=reader_id, code="ownerless_codeowners_rule", message="CODEOWNERS rule has no owner", status="invalid", severity="error", location={"start_line": line_number, "end_line": line_number}))
            continue
        facts.append(_fact(context, reader_id=reader_id, kind="review-ownership", scope="path-rule", identity=f"rule:{line_number}", location={"start_line": line_number, "end_line": line_number}, value={"pattern": parts[0], "owners": parts[1:], "precedence": line_number, "authority": "review-assignment-only"}, native_id=parts[0], convention="github.codeowners", projection={"mapping_version": "github-codeowners@1", "canonical_field": "review_owners", "loss": "does not imply operational ownership or permissions"}))
    return facts, [], diagnostics


_ECMA_IMPORT_RE = re.compile(
    r"^\s*import\s+(?:(?P<bindings>.+?)\s+from\s+)?[\"'](?P<module>[^\"']+)[\"']\s*;?\s*$"
)
_ECMA_REEXPORT_RE = re.compile(
    r"^\s*export\s+(?P<bindings>\*|\{.*?\})\s+from\s+[\"'](?P<module>[^\"']+)[\"']\s*;?\s*$"
)
_ECMA_DECLARATION_RE = re.compile(
    r"^\s*export\s+(?P<default>default\s+)?(?:(?:declare|abstract|async)\s+)*(?P<kind>interface|type|class|function|const|let|var|enum|namespace)\s+(?P<name>[A-Za-z_$][A-Za-z0-9_$]*)"
)


def _documentation_comment(lines: list[str]) -> dict[str, Any]:
    cleaned: list[str] = []
    tags: list[dict[str, str]] = []
    for raw in lines:
        text = raw.strip()
        text = re.sub(r"^/\*\*?", "", text)
        text = re.sub(r"\*/$", "", text)
        text = re.sub(r"^\*\s?", "", text).strip()
        if not text:
            continue
        if text.startswith("@"):
            tag, _, value = text[1:].partition(" ")
            tags.append({"tag": tag, "value": value})
        else:
            cleaned.append(text)
    return {"description": "\n".join(cleaned), "tags": tags, "dialect": "jsdoc-or-tsdoc-unresolved"}


def _read_typescript(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "typescript-static"
    dialect = "typescript" if path.suffix.lower() in {".ts", ".tsx", ".mts", ".cts"} else "ecmascript"
    context = dict(context, convention_version="static subset v1", dialect=dialect)
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    edges: list[dict] = []
    diagnostics: list[dict] = []
    module_identity = context["file"]
    module_subject = _subject_address(context, "module", module_identity)
    lines = text.splitlines()
    pending_doc: tuple[int, list[str]] | None = None
    in_doc = False
    doc_lines: list[str] = []
    doc_start = 0
    for number, line in enumerate(lines, start=1):
        stripped = line.strip()
        if not in_doc and stripped.startswith("/**"):
            in_doc = True
            doc_start = number
            doc_lines = [line]
            if "*/" in stripped[3:]:
                in_doc = False
                pending_doc = (doc_start, doc_lines)
            continue
        if in_doc:
            doc_lines.append(line)
            if "*/" in line:
                in_doc = False
                pending_doc = (doc_start, doc_lines)
            continue
        import_match = _ECMA_IMPORT_RE.match(line) or _ECMA_REEXPORT_RE.match(line)
        if import_match:
            module = import_match.group("module")
            value = {"module": module, "bindings": (import_match.groupdict().get("bindings") or "side-effect"), "kind": "reexport" if stripped.startswith("export") else "import"}
            facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="module", identity=module_identity, location={"start_line": number, "end_line": number}, value=value, native_id=f"{number}:{module}", projection={"mapping_version": "ecma-static-imports@1", "relation": "imports", "loss": "conditions and dynamic imports not resolved"}))
            edges.append(_edge(module_subject, f"ecma-module:{module}", value["kind"]))
            pending_doc = None
            continue
        declaration = _ECMA_DECLARATION_RE.match(line)
        if declaration:
            name = declaration.group("name")
            facts.append(_fact(context, reader_id=reader_id, kind="exported-declaration", scope="symbol", identity=name, location={"start_line": number, "end_line": number}, value={"name": name, "kind": declaration.group("kind"), "default": bool(declaration.group("default")), "declaration": stripped}, native_id=name, projection={"mapping_version": "ecma-exports@1", "canonical_field": "declared_surface", "loss": "multiline signature body not parsed"}))
            edges.append(_edge(module_subject, _subject_address(context, "symbol", name), "exports"))
            if pending_doc:
                start, attached_lines = pending_doc
                facts.append(_fact(context, reader_id=reader_id, kind="documentation", scope="symbol", identity=name, location={"start_line": start, "end_line": number - 1}, value=_documentation_comment(attached_lines), convention="typescript.documentation-comment"))
                diagnostics.append(_diagnostic(context, reader_id=reader_id, code="ambiguous_documentation_dialect", message="documentation comment was preserved without choosing JSDoc or TSDoc semantics", status="ambiguous", severity="warning", location={"start_line": start, "end_line": number - 1}))
            pending_doc = None
            continue
        if stripped and not stripped.startswith("//"):
            pending_doc = None
    if in_doc:
        diagnostics.append(_diagnostic(context, reader_id=reader_id, code="truncated_documentation_comment", message="file ends inside documentation comment", status="invalid", severity="error", location={"start_line": doc_start, "end_line": len(lines)}))
    return facts, edges, diagnostics


def _read_shell(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "shell-static"
    context = dict(context, convention_version="source declaration v1", dialect=path.suffix.lstrip(".") or "shebang")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    lines = text.splitlines()
    if lines and lines[0].startswith("#!"):
        facts.append(_fact(context, reader_id=reader_id, kind="interpreter", scope="file", identity=context["file"], location={"start_line": 1, "end_line": 1}, value={"shebang": lines[0][2:].strip()}, native_id="shebang", convention="posix.shebang"))
    for number, line in enumerate(lines, start=1):
        match = re.match(r"^\s*#\s*shellcheck\s+(?P<body>.+?)\s*$", line, re.IGNORECASE)
        if match:
            facts.append(_fact(context, reader_id=reader_id, kind="tool-directive", scope="file", identity=context["file"], location={"start_line": number, "end_line": number}, value={"tool": "shellcheck", "directive": match.group("body")}, native_id=f"shellcheck:{number}", convention="shellcheck.directive"))
    return facts, [], []


def _read_systemd(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "systemd-unit"
    context = dict(context, convention_version="systemd.syntax current documented grammar", dialect=path.suffix.lstrip("."))
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    diagnostics: list[dict] = []
    section = "hmmm"
    logical = ""
    logical_start = 1
    occurrence: dict[tuple[str, str], int] = {}
    for number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not logical and (not stripped or stripped.startswith(("#", ";"))):
            continue
        if not logical:
            logical_start = number
        logical += raw.rstrip("\\").strip()
        if raw.rstrip().endswith("\\"):
            continue
        line = logical
        logical = ""
        if line.startswith("[") and line.endswith("]"):
            section = line[1:-1]
            continue
        if "=" not in line:
            diagnostics.append(_diagnostic(context, reader_id=reader_id, code="invalid_systemd_directive", message="expected key=value", status="invalid", severity="error", location={"start_line": logical_start, "end_line": number}))
            continue
        key, value = line.split("=", 1)
        published_value = value
        if key.lower() == "environment" and "=" in value:
            environment_name = value.split("=", 1)[0].strip('"\'')
            if _SENSITIVE_KEY_RE.search(environment_name):
                published_value = f"{environment_name}=<redacted>"
                diagnostics.append(_diagnostic(context, reader_id=reader_id, code="sensitive_fields_redacted", message="withheld sensitive systemd Environment value", status="redacted", severity="warning", location={"start_line": logical_start, "end_line": number}))
        identity_key = (section, key)
        occurrence[identity_key] = occurrence.get(identity_key, 0) + 1
        identity = f"{section}.{key}[{occurrence[identity_key]}]"
        facts.append(_fact(context, reader_id=reader_id, kind="unit-directive", scope="configuration", identity=identity, location={"start_line": logical_start, "end_line": number}, value={"section": section, "key": key, "value": published_value, "occurrence": occurrence[identity_key]}, native_id=key, convention="systemd.unit"))
    if logical:
        diagnostics.append(_diagnostic(context, reader_id=reader_id, code="truncated_systemd_continuation", message="file ends during a continuation", status="invalid", severity="error"))
    return facts, [], diagnostics


def _read_gitignore(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "gitignore-lines"
    context = dict(context, convention_version="gitignore current documented grammar", dialect="gitignore")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    order = 0
    for line_number, raw in enumerate(text.splitlines(), start=1):
        if not raw or raw.startswith("#"):
            continue
        order += 1
        negated = raw.startswith("!") and not raw.startswith("\\!")
        pattern = raw[1:] if negated else raw
        facts.append(_fact(context, reader_id=reader_id, kind="ignore-rule", scope="path-rule", identity=f"rule:{order}", location={"start_line": line_number, "end_line": line_number}, value={"pattern": pattern, "negated": negated, "anchored": pattern.startswith("/"), "directory_only": pattern.endswith("/"), "order": order}, native_id=pattern, convention="git.ignore", standing="declared"))
    return facts, [], []


_REQUIREMENT_NAME_RE = re.compile(r"^(?P<name>[A-Za-z0-9][A-Za-z0-9._-]*)")


def _read_requirements(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "python-requirements"
    context = dict(context, convention_version="PyPA requirements file subset v1", dialect="requirements")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    edges: list[dict] = []
    diagnostics: list[dict] = []
    subject = _subject_address(context, "requirements-document", context["file"])
    order = 0
    for line_number, raw in enumerate(text.splitlines(), start=1):
        stripped = raw.strip()
        if not stripped or stripped.startswith("#"):
            continue
        order += 1
        published = re.sub(r"(?<=://)[^/@\s]+@", "<redacted>@", stripped)
        if published != stripped:
            diagnostics.append(_diagnostic(context, reader_id=reader_id, code="sensitive_fields_redacted", message="withheld requirement URL credentials", status="redacted", severity="warning", location={"start_line": line_number, "end_line": line_number}))
        if published.startswith("-"):
            facts.append(_fact(context, reader_id=reader_id, kind="requirements-option", scope="requirements-document", identity=f"option:{order}", location={"start_line": line_number, "end_line": line_number}, value={"text": published, "order": order}, native_id=f"option:{order}", convention="python.requirements-file", standing="declared"))
            continue
        match = _REQUIREMENT_NAME_RE.match(published)
        name = match.group("name") if match else "hmmm"
        facts.append(_fact(context, reader_id=reader_id, kind="dependency", scope="requirements-document", identity=f"requirement:{order}", location={"start_line": line_number, "end_line": line_number}, value={"requirement": published, "name": name, "class": "runtime-or-unresolved", "order": order}, native_id=name if name != "hmmm" else None, convention="python.requirements-file", standing="declared", projection={"mapping_version": "requirements-lines@1", "relation": "depends_on", "loss": "resolution and environment markers not evaluated"}))
        if name != "hmmm":
            edges.append(_edge(subject, f"python-package:{name}", "depends_on:runtime-or-unresolved"))
    return facts, edges, diagnostics


def _read_license(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "license-text"
    context = dict(context, convention_version="detector v1", dialect="license-text")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    spdx_match = re.search(r"SPDX-License-Identifier:\s*(?P<value>[^\r\n]+)", text)
    if spdx_match:
        expression = spdx_match.group("value").strip()
        method = "declared-spdx-line"
    elif text.startswith("Mozilla Public License Version 2.0"):
        expression = "MPL-2.0"
        method = "exact-known-header"
    else:
        expression = "hmmm"
        method = "unrecognized-text"
    fact = _fact(context, reader_id=reader_id, kind="license-declaration", scope="document", identity=context["file"], location={"pointer": "document"}, value={"expression": expression, "detection_method": method, "legal_interpretation": "not-performed", "text": "source-reference"}, native_id=expression if expression != "hmmm" else None, convention="license.text", standing="declared" if method == "declared-spdx-line" else "derived")
    diagnostics = [] if expression != "hmmm" else [_diagnostic(context, reader_id=reader_id, code="unrecognized_license_text", message="license identifier remains hmmm", status="ambiguous", severity="warning")]
    return [fact], [], diagnostics


def _read_svg(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "svg-metadata"
    context = dict(context, convention_version="SVG document subset v1", dialect="xml")
    if b"<!DOCTYPE" in data.upper() or b"<!ENTITY" in data.upper():
        return [], [], [_diagnostic(context, reader_id=reader_id, code="unsafe_xml_declaration", message="DTD/entity declarations are unsupported", status="unsupported", severity="warning")]
    try:
        root = ET.fromstring(data)
    except ET.ParseError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="invalid_svg_xml", message=str(exc), status="invalid", severity="error")]
    local_name = root.tag.rsplit("}", 1)[-1]
    if local_name != "svg":
        return [], [], [_diagnostic(context, reader_id=reader_id, code="unexpected_svg_root", message=f"root element is {local_name!r}", status="invalid", severity="error")]
    title = None
    description = None
    for child in root:
        child_name = child.tag.rsplit("}", 1)[-1]
        if child_name == "title" and title is None:
            title = "".join(child.itertext()).strip()
        elif child_name == "desc" and description is None:
            description = "".join(child.itertext()).strip()
    value = {"attributes": dict(root.attrib), "title": title, "description": description}
    return [_fact(context, reader_id=reader_id, kind="document-metadata", scope="document", identity=context["file"], location={"pointer": "/svg"}, value=value, convention="svg.document-metadata")], [], []


_LLMS_HEADING_RE = re.compile(r"^(?P<marks>#{1,6})\s+(?P<title>.+?)\s*$")
_LLMS_DEFINITION_RE = re.compile(r"^-\s+\*\*(?P<term>.+?)\*\*\s*=\s*(?P<definition>.+?)\s*$")


def _read_llms_text(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[dict], list[dict], list[dict]]:
    reader_id = "llms-text"
    context = dict(context, convention_version="Markdown structural subset v1", dialect="llms.txt")
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError as exc:
        return [], [], [_diagnostic(context, reader_id=reader_id, code="undecodable_source", message=str(exc), status="invalid", severity="error")]
    facts: list[dict] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        heading = _LLMS_HEADING_RE.match(line)
        if heading:
            title = heading.group("title")
            facts.append(_fact(context, reader_id=reader_id, kind="instruction-section", scope="document-section", identity=f"heading:{line_number}", location={"start_line": line_number, "end_line": line_number}, value={"level": len(heading.group("marks")), "title": title, "generated": "hmmm"}, native_id=title, convention="llms.txt", standing="declared"))
            continue
        definition = _LLMS_DEFINITION_RE.match(line)
        if definition:
            term = definition.group("term")
            facts.append(_fact(context, reader_id=reader_id, kind="key-definition", scope="instruction-definition", identity=term, location={"start_line": line_number, "end_line": line_number}, value={"term": term, "definition": definition.group("definition"), "generated": "hmmm"}, native_id=term, convention="llms.txt", standing="declared"))
    return facts, [], []


Reader = Callable[[Path, bytes, dict[str, Any]], tuple[list[dict], list[dict], list[dict]]]


def readers_for(path: Path, data: bytes | None = None) -> list[tuple[str, Reader]]:
    """Return every compatible reader selected for ``path``."""
    suffix = path.suffix.lower()
    relative = path.as_posix()
    selected: list[tuple[str, Reader]] = []
    if path.name == "CODEOWNERS" and relative in {"CODEOWNERS", ".github/CODEOWNERS", "docs/CODEOWNERS"}:
        selected.append(("github-codeowners", _read_codeowners))
    elif suffix in _PYTHON_SUFFIXES:
        selected.append(("python-ast", _read_python))
    elif suffix == ".json":
        selected.append(("json-stdlib", _read_json))
    elif suffix == ".toml":
        selected.append(("toml-stdlib", _read_toml))
    elif suffix in _MARKDOWN_SUFFIXES:
        selected.append(("markdown-frontmatter", _read_markdown))
    elif suffix in _YAML_SUFFIXES:
        selected.append(("yaml-safe-subset", _read_yaml))
    elif suffix in _TYPESCRIPT_SUFFIXES:
        selected.append(("typescript-static", _read_typescript))
    elif suffix in _SHELL_SUFFIXES:
        selected.append(("shell-static", _read_shell))
    elif suffix in _SYSTEMD_SUFFIXES:
        selected.append(("systemd-unit", _read_systemd))
    elif path.name == ".gitignore":
        selected.append(("gitignore-lines", _read_gitignore))
    elif (path.name.startswith("requirements") or path.name.startswith("constraints")) and suffix == ".txt":
        selected.append(("python-requirements", _read_requirements))
    elif path.name in {"LICENSE", "LICENSE.txt", "COPYING", "COPYING.txt"}:
        selected.append(("license-text", _read_license))
    elif suffix == ".svg":
        selected.append(("svg-metadata", _read_svg))
    elif path.name == "llms.txt":
        selected.append(("llms-text", _read_llms_text))
    elif not suffix and data is not None and data.startswith(b"#!"):
        selected.append(("shell-static", _read_shell))
    if data is not None and b"ratios:" in data and marker_for(path) is not None:
        selected.append(("msdmd-ratios", _read_ratios))
    return selected


def reader_for(path: Path, data: bytes | None = None) -> tuple[str, Reader] | None:
    """Return the primary reader for compatibility; prefer :func:`readers_for`."""
    selected = readers_for(path, data)
    return selected[0] if selected else None


def read_native(path: Path, data: bytes, context: dict[str, Any]) -> tuple[list[str], list[dict], list[dict], list[dict]]:
    """Read one immutable source buffer with every applicable native reader."""
    reader_ids: list[str] = []
    facts: list[dict] = []
    edges: list[dict] = []
    diagnostics: list[dict] = []
    for reader_id, reader in readers_for(path, data):
        reader_ids.append(reader_id)
        local_context = dict(context)
        local_context["configuration_sha256"] = _digest(json.dumps({"reader_id": reader_id, "reader_version": _MANIFESTS[reader_id]["version"]}, sort_keys=True))
        reader_facts, reader_edges, reader_diagnostics = reader(path, data, local_context)
        facts.extend(reader_facts)
        edges.extend(reader_edges)
        diagnostics.extend(reader_diagnostics)
    return reader_ids, facts, edges, diagnostics
# ratios: loc_comments=hmmm imports_exports=hmmm calls_definitions=hmmm
