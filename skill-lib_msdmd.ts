import { defineMsdmdCollection } from "./msdmd/collection";

export default defineMsdmdCollection({
  "declarations": [
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "validate_report, canonical_bytes, digest",
        "module_kind": "instrument",
        "module_name": "portfolio_plan",
        "network_boundary": "none",
        "owner": "The-Interdependency/skill-lib maintainers",
        "public_surface": "load_report, build_portfolio, main",
        "rollback": "remove the aggregator, schemas, companion docs, and portfolio projection section without changing repo-owned source claims",
        "rollout": "explicit CLI or library invocation after repo reports are supplied",
        "storage_boundary": "none",
        "summary": "validates repo-owned plan reports and derives a deterministic cross-repository portfolio projection without transferring authority",
        "tests": "tests/test_interdependent_work_graph_portfolio_plan.py",
        "unresolved": "automatic portfolio membership discovery, persistent live service, cryptographic producer authentication",
        "user_data_boundary": "none"
      },
      "file": "interdependent-work-graph/portfolio_plan.py",
      "id": "interdependent_work_graph_portfolio_plan"
    },
    {
      "block": "LLMS",
      "fields": {
        "content": "- Skills live as root directories with SKILL.md files and optional helpers."
      },
      "file": "llms/metadata.py",
      "id": "architecture_summary"
    },
    {
      "block": "LLMS",
      "fields": {
        "msdmd": "Module Self-Declared Metadata in Markdown \u2014 native-first collection of existing code, documentation, manifest, schema, tooling and evidence metadata; MSDMD blocks supply otherwise unexpressed information. The collector remains block-only; a separate partial Python reader projects symbols, docstrings and structurally attached comments."
      },
      "file": "llms/metadata.py",
      "id": "key_definitions"
    },
    {
      "block": "LLMS",
      "fields": {
        "content": "skill-lib is the canonical organization-wide source for reusable agent skills in The Interdependency."
      },
      "file": "llms/metadata.py",
      "id": "project_overview"
    },
    {
      "block": "LLMS",
      "fields": {
        "content": "- Read AGENTS.md, skills.json, and the relevant skill file before changing a skill."
      },
      "file": "llms/metadata.py",
      "id": "usage_rules"
    },
    {
      "block": "CAPABILITIES",
      "fields": {
        "exposes": "collect, render_typescript",
        "limitations": "Native files outside COMMENT_MARKERS are uncollected; skip paths and read errors are not inventoried; matching blocks in strings and test fixtures can be collected. Empty gaps without expected_blocks is not complete coverage.",
        "native_ingestion": "contract",
        "runner_scope": "msdmd-blocks-only",
        "summary": "Generates block-only TypeScript collections from lexical source blocks using the canonical parser; not native discovery or identity validation.",
        "unresolved": "hmmm: native readers, qualified edge identities, duplicate-ID validation, native-capable schema migration, and executable native acceptance fixtures remain separate implementation work."
      },
      "file": "msdmd/collect.py",
      "id": "repo_collection_generator"
    },
    {
      "block": "DOCS",
      "fields": {
        "catalogue": "msdmd/references/metadata-conventions.md",
        "source": "msdmd/SKILL.md",
        "summary": "Native-first metadata and information-coverage contract; supplemental blocks express otherwise unexpressed information. This source link is not native extraction of the skill or catalogue."
      },
      "file": "msdmd/collect.py",
      "id": "msdmd_foundational_contract"
    },
    {
      "block": "CAPABILITIES",
      "fields": {
        "exposes": "deterministic JSONL projection, Python symbol identities, native docstrings, structurally attached comments, freshness key",
        "limitations": "Python source only; call graphs, runtime behavior, cross-revision rename identity, and non-Python readers remain hmmm",
        "summary": "creates one generated metadata sidecar per Python module while keeping source locations navigational rather than identity-bearing"
      },
      "file": "msdmd/module_projection.py",
      "id": "python_module_metadata_projection"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "provenance",
        "given": "source bytes, schema, reader implementation, or reader support manifest changes",
        "then": "the deterministic projection freshness key changes"
      },
      "file": "msdmd/module_projection.py",
      "id": "module_projection_freshness_binds_source_and_reader"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "identity",
        "given": "blank or comment lines are inserted without changing declaration structure",
        "then": "metadata remains attached to the same qualified symbol identity after regeneration"
      },
      "file": "msdmd/module_projection.py",
      "id": "module_projection_line_shift_stability"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "inspected Python source contains executable top-level code",
        "then": "projection parses bytes without importing or executing the inspected module"
      },
      "file": "msdmd/module_projection.py",
      "id": "module_projection_never_executes_source"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "Python symbol discovery, comment grouping, structural attachment, freshness computation",
        "module_kind": "instrument",
        "module_name": "module_projection",
        "network_boundary": "none",
        "owner": "The Interdependency skill-lib",
        "public_surface": "project_python_module, render_jsonl, project_tree, write_projections, check_projections",
        "rollback": "remove the runner and generated projection directories; native sources remain authoritative",
        "rollout": "explicit python -m msdmd.module_projection --write invocation",
        "storage_boundary": "write",
        "summary": "derives deterministic per-module JSONL metadata with structural symbol attachment from Python source without executing it",
        "tests": "tests/test_module_projection.py",
        "user_data_boundary": "read"
      },
      "file": "msdmd/module_projection.py",
      "id": "msdmd_python_module_projection"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a valid metadata entry uses lowercase snake-case field names containing digits",
        "then": "parsed entries retain those field names and string values without executing the inspected source"
      },
      "file": "msdmd/parsers/universal.py",
      "id": "msdmd_python_parser_preserves_field_names"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "marker and block matching helpers",
        "module_kind": "instrument",
        "module_name": "universal",
        "network_boundary": "none",
        "owner": "The Interdependency skill-lib",
        "public_surface": "COMMENT_MARKERS, RATIO_IDS, marker_for, parse_text, parse_file, walk_tree, parse_ratios, parse_ratios_file, ratios_placement",
        "rollback": "restore a previously accepted exact parser identity",
        "rollout": "exact-pinned reference parser propagation",
        "storage_boundary": "read",
        "summary": "parses canonical line-comment metadata without executing inspected source",
        "tests": "tests/test_universal_parser.py",
        "user_data_boundary": "read"
      },
      "file": "msdmd/parsers/universal.py",
      "id": "msdmd_python_reference_parser"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a valid metadata entry uses lowercase snake-case field names containing digits",
        "then": "parsed entries retain those field names and string values without executing the inspected source"
      },
      "file": "msdmd/parsers/universal.ts",
      "id": "msdmd_typescript_parser_preserves_field_names"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "marker and block matching helpers",
        "module_kind": "instrument",
        "module_name": "universal",
        "network_boundary": "none",
        "owner": "The Interdependency skill-lib",
        "public_surface": "Entry, WalkOptions, COMMENT_MARKERS, RATIO_IDS, markerFor, parseText, parseFile, walkTree, parseRatios, parseRatiosFile, ratiosPlacement",
        "rollback": "restore a previously accepted exact parser identity",
        "rollout": "exact-pinned reference parser propagation",
        "storage_boundary": "read",
        "summary": "parses canonical line-comment metadata without executing inspected source",
        "tests": "tests/test_universal_parser.py::test_typescript_parser_field_contract",
        "user_data_boundary": "read"
      },
      "file": "msdmd/parsers/universal.ts",
      "id": "msdmd_typescript_reference_parser"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "Jacobi eigensolver, eigenspace grouping, sinusoid least-squares fit",
        "module_kind": "experiment",
        "module_name": "harmonic_math",
        "network_boundary": "none",
        "owner": "The Interdependency",
        "public_surface": "graph_harmonics, harmonic_scan",
        "rollback": "remove this helper with ratios/harmonics.py; no stored state exists",
        "rollout": "imported only by the opt-in ratios harmonic explorer",
        "storage_boundary": "none",
        "summary": "supplies dependency-free graph and scalar harmonic estimators for ratio exploration",
        "tests": "tests/test_harmonics.py",
        "user_data_boundary": "none"
      },
      "file": "ratios/harmonic_math.py",
      "id": "ratios_harmonic_math"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "graph preparation, metric selection, distance projection, report rendering",
        "module_kind": "experiment",
        "module_name": "harmonics",
        "network_boundary": "none",
        "owner": "The Interdependency",
        "public_surface": "semantic_file_graph, source_balance_series, analyze, main",
        "requires": "ratios_harmonic_math",
        "rollback": "remove ratios/harmonics.py and harmonic_math.py; RATIOS seals remain unchanged",
        "rollout": "opt-in read-only CLI; never a compliance gate",
        "storage_boundary": "read",
        "summary": "explores harmonic structure of verified ratio primitives over non-time domains",
        "tests": "tests/test_harmonics.py",
        "user_data_boundary": "none"
      },
      "file": "ratios/harmonics.py",
      "id": "ratios_harmonic_explorer"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "doctrine",
        "given": "`loto clear` on a scar",
        "then": "refused on dirty tree; on clean tree produces a commit touching zero files, carrying scar trailers, and deletes the scar"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_clear_is_empty_commit"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "doctrine",
        "given": "one in-scope mutation commit and passing test evidence; `loto close`",
        "then": ".loto/ is empty and HEAD carries Loto-* trailers; git is the only archive"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_close_deletes_tag"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a failing run of a test command followed by a passing run of the identical command",
        "then": "close proceeds; a distinct command whose latest run failed still blocks close"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_latest_test_wins"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "doctrine",
        "given": "more than one commit between base and HEAD at close",
        "then": "close refuses (v0.1 invariant: one session, one mutation commit)"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_one_commit_per_session"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "doctrine",
        "given": "clean working tree; `loto open` succeeds",
        "then": "working tree is still clean; exclusion went to .git/info/exclude, never .gitignore"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_open_never_dirties"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "an unacknowledged SCAR-*.json in .loto/",
        "then": "`loto open` refuses and `loto guard` exits nonzero"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_scar_blocks_work"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "files touched outside the declared --files globs",
        "then": "close refuses with the violating paths named"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "loto_scope_enforced"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "_load, _save, _touched_files, _scope_violations, _trailers, _digest, _commit, _git, _ensure_gitignored",
        "module_kind": "instrument",
        "module_name": "repo_loto",
        "network_boundary": "none",
        "owner": "Way Seer Erin",
        "public_surface": "loto open, loto run, loto test, loto close, loto fail, loto clear, loto status, loto guard, loto install-hook",
        "rollback": "rm -rf .loto/ and remove hook line",
        "rollout": "manual invocation; pre-push hook calls `loto guard`",
        "storage_boundary": "write",
        "summary": "delete-on-completion session gate for repo mutation; presence of state means open work, absence means clean",
        "tests": "tests/test_repo_loto.py (CHECKS-declared, reconciled via --audit)",
        "unresolved": "credential-gate integration, ratios bookends",
        "user_data_boundary": "none"
      },
      "file": "skill_lib/safety/repo_loto.py",
      "id": "repo_mutation_gate"
    },
    {
      "block": "DOCS",
      "fields": {
        "source": "docs/module.md",
        "status": "current",
        "summary": "module docs"
      },
      "file": "tests/test_collect.py",
      "id": "module_docs"
    },
    {
      "block": "LLMS",
      "fields": {
        "content": "example only"
      },
      "file": "tests/test_llms_build.py",
      "id": "project_overview"
    },
    {
      "block": "LLMS",
      "fields": {
        "content": "real declaration"
      },
      "file": "tests/test_llms_build.py",
      "id": "project_overview"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_freshness_key_changes_with_source_or_reader",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "module_projection_freshness_binds_source_and_reader",
        "requires": "python3",
        "timeout": "10"
      },
      "file": "tests/test_module_projection.py",
      "id": "check_module_projection_freshness_binds_source_and_reader"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_line_insertions_preserve_symbol_identity_and_attachment",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "module_projection_line_shift_stability",
        "requires": "python3",
        "timeout": "10"
      },
      "file": "tests/test_module_projection.py",
      "id": "check_module_projection_line_shift_stability"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_projection_does_not_execute_inspected_source",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "module_projection_never_executes_source",
        "requires": "python3",
        "timeout": "10"
      },
      "file": "tests/test_module_projection.py",
      "id": "check_module_projection_never_executes_source"
    },
    {
      "block": "DOCS",
      "fields": {
        "summary": "module documentation"
      },
      "file": "tests/test_module_projection.py",
      "id": "module_docs"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_ratio_report_lists_low_coverage_oddity",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "org_ratio_oddities_visible",
        "requires": "python3, posix_shell",
        "timeout": "5"
      },
      "file": "tests/test_org_reports.py",
      "id": "check_org_ratio_oddities_visible"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_ratio_metrics_skip_vendored_agents",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "org_ratio_skips_vendored_skills",
        "requires": "python3, posix_shell",
        "timeout": "5"
      },
      "file": "tests/test_org_reports.py",
      "id": "check_org_ratio_skips_vendored_skills"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_aggregate_append_preserves_existing_content",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "org_rec_append_only",
        "requires": "python3, posix_shell",
        "timeout": "5"
      },
      "file": "tests/test_org_reports.py",
      "id": "check_org_rec_append_only"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_aggregate_lists_missing_rec_files",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "org_rec_missing_repo_visible",
        "requires": "python3, posix_shell",
        "timeout": "5"
      },
      "file": "tests/test_org_reports.py",
      "id": "check_org_rec_missing_repo_visible"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_aggregate_uses_remaining_when_latest_block_has_no_recommendations",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "org_rec_remaining_fallback",
        "requires": "python3, posix_shell",
        "timeout": "5"
      },
      "file": "tests/test_org_reports.py",
      "id": "check_org_rec_remaining_fallback"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_clear_is_empty_commit",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_clear_is_empty_commit",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_clear_is_empty_commit"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_close_deletes_tag",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_close_deletes_tag",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_close_deletes_tag"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_latest_test_wins",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_latest_test_wins",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_latest_test_wins"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_one_commit_per_session",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_one_commit_per_session",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_one_commit_per_session"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_open_never_dirties",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_open_never_dirties",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_open_never_dirties"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_scar_blocks_work",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_scar_blocks_work",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_scar_blocks_work"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_scope_enforced",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "loto_scope_enforced",
        "requires": "git, python3, posix_shell",
        "timeout": "20"
      },
      "file": "tests/test_repo_loto.py",
      "id": "check_scope_enforced"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "internal_surface": "_mk_repo, _run, _loto, _parse_block, _resolve_call, _requires_met",
        "module_kind": "checks",
        "module_name": "test_repo_loto",
        "owner": "Way Seer Erin",
        "public_surface": "test_* functions, main, --audit",
        "summary": "evidentiary procedures for repo_loto CONTRACTS; standalone or pytest; --audit reconciles the declared graph without execution",
        "tests": "self",
        "unresolved": "mutation-level verification that checks actually exercise their contracts"
      },
      "file": "tests/test_repo_loto.py",
      "id": "repo_loto_evidence"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_parser_field_contract",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "msdmd_python_parser_preserves_field_names",
        "requires": "python3",
        "timeout": "10"
      },
      "file": "tests/test_universal_parser.py",
      "id": "check_msdmd_python_numeric_field_contract"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_typescript_parser_field_contract",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "msdmd_typescript_parser_preserves_field_names",
        "requires": "python3, node24",
        "timeout": "10"
      },
      "file": "tests/test_universal_parser.py",
      "id": "check_msdmd_typescript_numeric_field_contract"
    },
    {
      "block": "DOCS",
      "fields": {
        "summary": "second"
      },
      "file": "tests/test_universal_parser.py",
      "id": "second_docs"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "filesystem",
        "given": "append_report is called for an existing aggregate file",
        "then": "existing bytes remain before the new report and the file is not truncated"
      },
      "file": "tools/aggregate_org_rec.py",
      "id": "org_rec_append_only"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a discovered git checkout has no rec.md",
        "then": "the aggregate includes the repository in a visible hmmm/missing list"
      },
      "file": "tools/aggregate_org_rec.py",
      "id": "org_rec_missing_repo_visible"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a repo's latest rec.md block has Remaining but no Recommendations",
        "then": "the aggregate reports the Remaining bullets as follow-up recommendations"
      },
      "file": "tools/aggregate_org_rec.py",
      "id": "org_rec_remaining_fallback"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "discover_repos, extract_section, git_value",
        "module_kind": "instrument",
        "module_name": "aggregate_org_rec",
        "network_boundary": "none",
        "owner": "Codex",
        "public_surface": "build_report, append_report, command line",
        "rollback": "remove tool and README entry",
        "rollout": "manual runner under tools",
        "storage_boundary": "write",
        "summary": "append repo-local rec.md recommendations into an org-level rec.md section.",
        "tests": "tests/test_org_reports.py",
        "user_data_boundary": "none"
      },
      "file": "tools/aggregate_org_rec.py",
      "id": "org_rec_aggregation_runner"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "SSH host alias and third-party CLIs own authentication; launcher never prints key values",
        "internal_surface": "remote bash quoting, tmux session/window lifecycle, key-to-tmux propagation",
        "module_kind": "cli",
        "module_name": "ai",
        "network_boundary": "SSH to configured VM host only",
        "owner": "skill-lib",
        "public_surface": "ai.sh start|attach|status|restart|logs|keys|grok|codex|deepcode|shell",
        "requires": "local bash + ssh; remote bash + tmux; optional remote grok/codex/deepcodei CLIs",
        "rollback": "remove installed ai.sh symlink; canonical source remains in skill-lib",
        "rollout": "explicit install via tools/install_ai.sh",
        "since": "2026-09-12",
        "storage_boundary": "remote pane logs under ~/.local/state/a0/logs; no secret persistence",
        "summary": "canonical Termux-side SSH/tmux launcher for coding-agent CLIs on the a0 development VM with health, restart, key propagation, and persistent remote pane logs",
        "tests": "tests/test_ai_launcher.py",
        "unresolved": "third-party CLI executable names and provider authentication methods may change",
        "user_data_boundary": "provider key values are only copied from the VM login environment into the VM tmux server environment"
      },
      "file": "tools/ai.sh",
      "id": "skill_lib_ai_launcher"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "doctrine_files",
        "module_kind": "checker",
        "module_name": "check_gonol_authority",
        "network_boundary": "none",
        "owner": "skill-lib",
        "public_surface": "bash tools/check_gonol_authority.sh",
        "requires": "gonol-build/SKILL.md, char-compress/SKILL.md, active skill-lib projections",
        "rollback": "revert only with an explicit authority change and matching doctrine update",
        "rollout": "skill-lib CI gate",
        "since": "2026-09-12",
        "storage_boundary": "read-only repository files",
        "summary": "fail-closed local regression gate for UCNS/Stack/EDCM gonol authority across active skill-lib doctrine and projections",
        "tests": "tests/test_gonol_build_skill.py, tests/test_char_compress_authority.py",
        "unresolved": "cross-repository authority truth is validated by each owning repository and Stack consistency gates",
        "user_data_boundary": "none"
      },
      "file": "tools/check_gonol_authority.sh",
      "id": "gonol_authority_gate"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "PATH target selection and symlink installation",
        "module_kind": "installer",
        "module_name": "install_ai",
        "network_boundary": "none",
        "owner": "skill-lib",
        "public_surface": "bash tools/install_ai.sh",
        "requires": "bash",
        "rollback": "remove the installed ai.sh symlink and marked PATH line if one was added",
        "rollout": "explicit user invocation",
        "since": "2026-09-12",
        "storage_boundary": "writes one ai.sh symlink and, outside an already-on-PATH bin directory, one idempotent ~/.profile PATH line",
        "summary": "installs the canonical skill-lib tools/ai.sh into the caller's PATH, preferring Termux $PREFIX/bin and otherwise ~/.local/bin",
        "tests": "tests/test_ai_launcher.py",
        "unresolved": "a current shell cannot inherit a newly appended PATH line from a child process",
        "user_data_boundary": "no credentials read or written"
      },
      "file": "tools/install_ai.sh",
      "id": "skill_lib_ai_installer"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a repo has low ratio coverage or dirty state",
        "then": "build_report lists a human-readable oddity for that repo"
      },
      "file": "tools/org_ratio_compare.py",
      "id": "org_ratio_oddities_visible"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "evidence",
        "given": "a repo contains product source and .agents/skills source",
        "then": "scalar/vector metrics exclude the vendored .agents tree"
      },
      "file": "tools/org_ratio_compare.py",
      "id": "org_ratio_skips_vendored_skills"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "false",
        "auth_boundary": "none",
        "internal_surface": "scan_repo, oddities, line_count",
        "module_kind": "instrument",
        "module_name": "org_ratio_compare",
        "network_boundary": "none",
        "owner": "Codex",
        "public_surface": "collect_metrics, build_report, append_report, command line",
        "rollback": "remove tool and README entry",
        "rollout": "manual runner under tools",
        "storage_boundary": "write",
        "summary": "collect org-wide scalar and vector repo metrics and append docs.report oddities.",
        "tests": "tests/test_org_reports.py",
        "user_data_boundary": "none"
      },
      "file": "tools/org_ratio_compare.py",
      "id": "org_ratio_comparison_runner"
    },
    {
      "block": "BOUNDARIES",
      "fields": {
        "admin_only": "true",
        "auth_boundary": "admin",
        "network_boundary": "local",
        "owner": "skill-lib vm-mcp maintainers",
        "side_effects": "process, filesystem, service, database, network",
        "storage_boundary": "write",
        "summary": "root-owned local broker receives only verified vmmcp Unix-socket requests and may execute arbitrary host commands in personal-console mode",
        "user_data_boundary": "read_write"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_admin_broker_root_boundary"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "a process connects to the root broker Unix socket",
        "then": "SO_PEERCRED must identify the configured vmmcp service user or the request is rejected"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_admin_broker_peer_verified"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "authority",
        "given": "personal-console admin_exec requests a command",
        "then": "the broker executes it as uid 0 and reports root mode explicitly in the result"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_admin_exec_explicit_root"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "a brokered command times out, emits excessive output, or leaves descendants running",
        "then": "the process group is killed, output is capped, and terminal evidence is returned"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_broker_execution_bounded"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "personal-console user_exec requests a local user",
        "then": "root is rejected and the child process drops uid/gid/groups to the requested non-root account before exec"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_user_exec_non_root"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "true",
        "auth_boundary": "admin",
        "internal_surface": "peer credential verification, privilege drop, bounded process execution",
        "module_kind": "service",
        "module_name": "vm_mcp_personal_console_broker",
        "network_boundary": "local",
        "owner": "skill-lib vm-mcp maintainers",
        "public_surface": "execute_request, serve",
        "rollback": "stop and disable vm-mcp-admin.service; return vm-mcp to read-only or workspace profile",
        "rollout": "vm-mcp-admin.service only when VM_MCP_PROFILE=personal-console",
        "storage_boundary": "write",
        "summary": "root-side Unix-socket broker for explicit non-root user_exec and root admin_exec in single-owner personal-console deployments",
        "tests": "vm-mcp/tests/test_admin_broker.py",
        "user_data_boundary": "read_write"
      },
      "file": "vm-mcp/admin_broker.py",
      "id": "vm_mcp_personal_console_broker"
    },
    {
      "block": "BOUNDARIES",
      "fields": {
        "admin_only": "true",
        "auth_boundary": "admin",
        "network_boundary": "local",
        "owner": "skill-lib vm-mcp maintainers",
        "side_effects": "process",
        "storage_boundary": "none",
        "summary": "connects only to the configured local Unix-domain broker socket and sends no SSH/cloud credentials",
        "user_data_boundary": "read_write"
      },
      "file": "vm-mcp/admin_client.py",
      "id": "vm_mcp_admin_client_socket_boundary"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "true",
        "auth_boundary": "admin",
        "internal_surface": "AF_UNIX JSON request/response transport",
        "module_kind": "adapter",
        "module_name": "vm_mcp_admin_client",
        "network_boundary": "local",
        "owner": "skill-lib vm-mcp maintainers",
        "public_surface": "request_exec",
        "rollback": "return deployment to workspace/read-only profile",
        "rollout": "imported by policy.py only in personal-console profile",
        "storage_boundary": "none",
        "summary": "sends bounded personal-console execution requests from the non-root MCP service to the local root broker",
        "tests": "vm-mcp/tests/test_assets.py",
        "user_data_boundary": "read_write"
      },
      "file": "vm-mcp/admin_client.py",
      "id": "vm_mcp_admin_client"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "the MCP service process has unrelated environment variables or host credentials",
        "then": "shell execution receives a sanitized environment rather than the service process environment"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_credentials_not_inherited"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "a directory listing encounters a symlink whose target is outside VM_MCP_ROOT",
        "then": "the listing reports the symlink itself and does not follow the target for file metadata"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_listing_symlinks_not_followed"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "a file, directory, or process result exceeds its configured response limit",
        "then": "the response is capped and reports truncation visibly"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_output_bounded"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "user_exec or admin_exec is requested",
        "then": "the deployment must explicitly select the personal-console profile"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_personal_console_explicit"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "the service starts without an explicit profile",
        "then": "writes, shell execution, user execution, and admin execution are refused"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_profile_default_read_only"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "a file or directory tool receives a relative path, absolute path, parent traversal, or symlink target",
        "then": "the resolved target must remain under VM_MCP_ROOT or the tool refuses access"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_read_paths_confined"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "shell execution receives a working directory outside VM_MCP_ROOT or through an escaping symlink",
        "then": "execution is refused before a process is spawned"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_shell_cwd_confined"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "safety",
        "given": "shell execution emits excessive output, exceeds its timeout, or tries to leave background descendants running",
        "then": "output is capped, timed-out process groups are killed, and surviving descendants are killed before return"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_shell_execution_bounded"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "a workspace write, move, directory creation, or removal is requested",
        "then": "the resolved path remains under VM_MCP_ROOT and the profile must permit workspace mutation"
      },
      "file": "vm-mcp/policy.py",
      "id": "vm_mcp_workspace_writes_confined"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "the non-root MCP service starts with its shipped systemd configuration",
        "then": "NoNewPrivileges remains enabled, Linux capabilities are empty, and direct service writes stay under VM_MCP_ROOT"
      },
      "file": "vm-mcp/server.py",
      "id": "vm_mcp_host_write_confined"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "the MCP server starts with its shipped runtime configuration",
        "then": "Streamable HTTP binds to 127.0.0.1 on /mcp rather than a public interface"
      },
      "file": "vm-mcp/server.py",
      "id": "vm_mcp_loopback_only"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "security",
        "given": "the non-root MCP service attempts to reach the standard cloud metadata-service address",
        "then": "the systemd network policy denies 169.254.169.254"
      },
      "file": "vm-mcp/server.py",
      "id": "vm_mcp_metadata_credentials_blocked"
    },
    {
      "block": "CONTRACTS",
      "fields": {
        "class": "authority",
        "given": "personal-console admin_exec is enabled",
        "then": "root execution occurs only in the separate Unix-socket broker and not by making the MCP service root"
      },
      "file": "vm-mcp/server.py",
      "id": "vm_mcp_personal_console_root_separate"
    },
    {
      "block": "MODULE_BUILD",
      "fields": {
        "admin_only": "true",
        "auth_boundary": "admin",
        "feature_flag": "VM_MCP_PROFILE",
        "internal_surface": "policy.py, admin_client.py, admin_broker.py",
        "module_kind": "service",
        "module_name": "vm_mcp_control_plane",
        "network_boundary": "external",
        "owner": "skill-lib vm-mcp maintainers",
        "public_surface": "vm_info, list_directory, read_text, stat_path, write_text, make_directory, move_path, remove_path, shell_exec, user_exec, admin_exec",
        "rollback": "disable vm-mcp services and remove private client registration",
        "rollout": "root_installer_plus_systemd_plus_private_mcp_tunnel",
        "storage_boundary": "write",
        "summary": "exposes loopback-only VM inspection, workspace mutation, confined shell, and explicit personal-console user/root execution surfaces",
        "tests": "vm-mcp/tests/test_policy.py, vm-mcp/tests/test_assets.py, vm-mcp/tests/test_admin_broker.py",
        "unresolved": "client_specific_private_tunnel_registration, application_layer_auth_when_not_using_a_private_tunnel",
        "user_data_boundary": "read_write"
      },
      "file": "vm-mcp/server.py",
      "id": "vm_mcp_control_plane"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_serve_source_uses_peer_credentials",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_admin_broker_peer_verified"
      },
      "file": "vm-mcp/tests/test_admin_broker.py",
      "id": "check_vm_mcp_admin_broker_peer_verified"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_admin_mode_selects_root",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_admin_exec_explicit_root"
      },
      "file": "vm-mcp/tests/test_admin_broker.py",
      "id": "check_vm_mcp_admin_exec_explicit_root"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_admin_execution_timeout_is_bounded_when_root",
        "cleanup": "process_group_killed",
        "mutates": "process",
        "proves": "vm_mcp_broker_execution_bounded"
      },
      "file": "vm-mcp/tests/test_admin_broker.py",
      "id": "check_vm_mcp_broker_execution_bounded"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_user_mode_rejects_root",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_user_exec_non_root"
      },
      "file": "vm-mcp/tests/test_admin_broker.py",
      "id": "check_vm_mcp_user_exec_non_root"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_server_binds_loopback_only",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_loopback_only"
      },
      "file": "vm-mcp/tests/test_assets.py",
      "id": "check_vm_mcp_loopback_config"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_systemd_blocks_cloud_metadata_address",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_metadata_credentials_blocked"
      },
      "file": "vm-mcp/tests/test_assets.py",
      "id": "check_vm_mcp_metadata_denial"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_personal_console_uses_separate_root_broker",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_personal_console_root_separate"
      },
      "file": "vm-mcp/tests/test_assets.py",
      "id": "check_vm_mcp_personal_console_root_separate"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_non_root_service_keeps_hardening",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_host_write_confined"
      },
      "file": "vm-mcp/tests/test_assets.py",
      "id": "check_vm_mcp_systemd_write_boundary"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_shell_does_not_inherit_unrelated_environment",
        "cleanup": "patch_dict_rollback",
        "mutates": "process_environment",
        "proves": "vm_mcp_credentials_not_inherited"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_environment_sanitized"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_listing_does_not_follow_symlink_metadata",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_listing_symlinks_not_followed"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_listing_symlink_not_followed"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_read_text_is_bounded",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_output_bounded"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_output_bounded"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_parent_escape_rejected",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_read_paths_confined"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_parent_escape_rejected"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_broker_exec_requires_personal_console",
        "cleanup": "none",
        "mutates": "none",
        "proves": "vm_mcp_personal_console_explicit"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_personal_console_gate"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_default_profile_is_read_only",
        "cleanup": "patch_dict_rollback",
        "mutates": "process_environment",
        "proves": "vm_mcp_profile_default_read_only"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_profile_default_read_only"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_shell_cwd_escape_rejected",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_shell_cwd_confined"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_shell_cwd_escape_rejected"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_shell_output_is_bounded_while_draining",
        "cleanup": "process_group_killed",
        "mutates": "process",
        "proves": "vm_mcp_shell_execution_bounded"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_shell_output_bounded"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_shell_timeout_is_enforced",
        "cleanup": "process_group_killed",
        "mutates": "process",
        "proves": "vm_mcp_shell_execution_bounded"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_shell_timeout"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_symlink_escape_rejected",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_read_paths_confined"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_symlink_escape_rejected"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_write_and_move_remain_under_root",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_workspace_writes_confined"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_workspace_write_confined"
    },
    {
      "block": "CHECKS",
      "fields": {
        "call": "self::test_write_requires_mutating_profile",
        "cleanup": "tempdir_teardown",
        "mutates": "filesystem",
        "proves": "vm_mcp_workspace_writes_confined"
      },
      "file": "vm-mcp/tests/test_policy.py",
      "id": "check_vm_mcp_workspace_write_gate"
    }
  ],
  "edges": [
    {
      "from": "vm_mcp_admin_broker_root_boundary",
      "kind": "owns",
      "source_block": "BOUNDARIES",
      "source_id": "vm_mcp_admin_broker_root_boundary",
      "to": "skill-lib vm-mcp maintainers"
    },
    {
      "from": "vm_mcp_admin_client_socket_boundary",
      "kind": "owns",
      "source_block": "BOUNDARIES",
      "source_id": "vm_mcp_admin_client_socket_boundary",
      "to": "skill-lib vm-mcp maintainers"
    },
    {
      "from": "python_module_metadata_projection",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "python_module_metadata_projection",
      "to": "Python symbol identities"
    },
    {
      "from": "python_module_metadata_projection",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "python_module_metadata_projection",
      "to": "deterministic JSONL projection"
    },
    {
      "from": "python_module_metadata_projection",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "python_module_metadata_projection",
      "to": "freshness key"
    },
    {
      "from": "python_module_metadata_projection",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "python_module_metadata_projection",
      "to": "native docstrings"
    },
    {
      "from": "python_module_metadata_projection",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "python_module_metadata_projection",
      "to": "structurally attached comments"
    },
    {
      "from": "repo_collection_generator",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "repo_collection_generator",
      "to": "collect"
    },
    {
      "from": "repo_collection_generator",
      "kind": "exposes",
      "source_block": "CAPABILITIES",
      "source_id": "repo_collection_generator",
      "to": "render_typescript"
    },
    {
      "from": "check_clear_is_empty_commit",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_clear_is_empty_commit",
      "to": "self::test_clear_is_empty_commit"
    },
    {
      "from": "check_clear_is_empty_commit",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_clear_is_empty_commit",
      "to": "loto_clear_is_empty_commit"
    },
    {
      "from": "check_clear_is_empty_commit",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_clear_is_empty_commit",
      "to": "git"
    },
    {
      "from": "check_clear_is_empty_commit",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_clear_is_empty_commit",
      "to": "posix_shell"
    },
    {
      "from": "check_clear_is_empty_commit",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_clear_is_empty_commit",
      "to": "python3"
    },
    {
      "from": "check_close_deletes_tag",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_close_deletes_tag",
      "to": "self::test_close_deletes_tag"
    },
    {
      "from": "check_close_deletes_tag",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_close_deletes_tag",
      "to": "loto_close_deletes_tag"
    },
    {
      "from": "check_close_deletes_tag",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_close_deletes_tag",
      "to": "git"
    },
    {
      "from": "check_close_deletes_tag",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_close_deletes_tag",
      "to": "posix_shell"
    },
    {
      "from": "check_close_deletes_tag",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_close_deletes_tag",
      "to": "python3"
    },
    {
      "from": "check_latest_test_wins",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_latest_test_wins",
      "to": "self::test_latest_test_wins"
    },
    {
      "from": "check_latest_test_wins",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_latest_test_wins",
      "to": "loto_latest_test_wins"
    },
    {
      "from": "check_latest_test_wins",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_latest_test_wins",
      "to": "git"
    },
    {
      "from": "check_latest_test_wins",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_latest_test_wins",
      "to": "posix_shell"
    },
    {
      "from": "check_latest_test_wins",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_latest_test_wins",
      "to": "python3"
    },
    {
      "from": "check_module_projection_freshness_binds_source_and_reader",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_freshness_binds_source_and_reader",
      "to": "self::test_freshness_key_changes_with_source_or_reader"
    },
    {
      "from": "check_module_projection_freshness_binds_source_and_reader",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_freshness_binds_source_and_reader",
      "to": "module_projection_freshness_binds_source_and_reader"
    },
    {
      "from": "check_module_projection_freshness_binds_source_and_reader",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_freshness_binds_source_and_reader",
      "to": "python3"
    },
    {
      "from": "check_module_projection_line_shift_stability",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_line_shift_stability",
      "to": "self::test_line_insertions_preserve_symbol_identity_and_attachment"
    },
    {
      "from": "check_module_projection_line_shift_stability",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_line_shift_stability",
      "to": "module_projection_line_shift_stability"
    },
    {
      "from": "check_module_projection_line_shift_stability",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_line_shift_stability",
      "to": "python3"
    },
    {
      "from": "check_module_projection_never_executes_source",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_never_executes_source",
      "to": "self::test_projection_does_not_execute_inspected_source"
    },
    {
      "from": "check_module_projection_never_executes_source",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_never_executes_source",
      "to": "module_projection_never_executes_source"
    },
    {
      "from": "check_module_projection_never_executes_source",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_module_projection_never_executes_source",
      "to": "python3"
    },
    {
      "from": "check_msdmd_python_numeric_field_contract",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_python_numeric_field_contract",
      "to": "self::test_parser_field_contract"
    },
    {
      "from": "check_msdmd_python_numeric_field_contract",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_python_numeric_field_contract",
      "to": "msdmd_python_parser_preserves_field_names"
    },
    {
      "from": "check_msdmd_python_numeric_field_contract",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_python_numeric_field_contract",
      "to": "python3"
    },
    {
      "from": "check_msdmd_typescript_numeric_field_contract",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_typescript_numeric_field_contract",
      "to": "self::test_typescript_parser_field_contract"
    },
    {
      "from": "check_msdmd_typescript_numeric_field_contract",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_typescript_numeric_field_contract",
      "to": "msdmd_typescript_parser_preserves_field_names"
    },
    {
      "from": "check_msdmd_typescript_numeric_field_contract",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_typescript_numeric_field_contract",
      "to": "node24"
    },
    {
      "from": "check_msdmd_typescript_numeric_field_contract",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_msdmd_typescript_numeric_field_contract",
      "to": "python3"
    },
    {
      "from": "check_one_commit_per_session",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_one_commit_per_session",
      "to": "self::test_one_commit_per_session"
    },
    {
      "from": "check_one_commit_per_session",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_one_commit_per_session",
      "to": "loto_one_commit_per_session"
    },
    {
      "from": "check_one_commit_per_session",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_one_commit_per_session",
      "to": "git"
    },
    {
      "from": "check_one_commit_per_session",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_one_commit_per_session",
      "to": "posix_shell"
    },
    {
      "from": "check_one_commit_per_session",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_one_commit_per_session",
      "to": "python3"
    },
    {
      "from": "check_open_never_dirties",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_open_never_dirties",
      "to": "self::test_open_never_dirties"
    },
    {
      "from": "check_open_never_dirties",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_open_never_dirties",
      "to": "loto_open_never_dirties"
    },
    {
      "from": "check_open_never_dirties",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_open_never_dirties",
      "to": "git"
    },
    {
      "from": "check_open_never_dirties",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_open_never_dirties",
      "to": "posix_shell"
    },
    {
      "from": "check_open_never_dirties",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_open_never_dirties",
      "to": "python3"
    },
    {
      "from": "check_org_ratio_oddities_visible",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_oddities_visible",
      "to": "self::test_ratio_report_lists_low_coverage_oddity"
    },
    {
      "from": "check_org_ratio_oddities_visible",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_oddities_visible",
      "to": "org_ratio_oddities_visible"
    },
    {
      "from": "check_org_ratio_oddities_visible",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_oddities_visible",
      "to": "posix_shell"
    },
    {
      "from": "check_org_ratio_oddities_visible",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_oddities_visible",
      "to": "python3"
    },
    {
      "from": "check_org_ratio_skips_vendored_skills",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_skips_vendored_skills",
      "to": "self::test_ratio_metrics_skip_vendored_agents"
    },
    {
      "from": "check_org_ratio_skips_vendored_skills",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_skips_vendored_skills",
      "to": "org_ratio_skips_vendored_skills"
    },
    {
      "from": "check_org_ratio_skips_vendored_skills",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_skips_vendored_skills",
      "to": "posix_shell"
    },
    {
      "from": "check_org_ratio_skips_vendored_skills",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_ratio_skips_vendored_skills",
      "to": "python3"
    },
    {
      "from": "check_org_rec_append_only",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_append_only",
      "to": "self::test_aggregate_append_preserves_existing_content"
    },
    {
      "from": "check_org_rec_append_only",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_append_only",
      "to": "org_rec_append_only"
    },
    {
      "from": "check_org_rec_append_only",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_append_only",
      "to": "posix_shell"
    },
    {
      "from": "check_org_rec_append_only",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_append_only",
      "to": "python3"
    },
    {
      "from": "check_org_rec_missing_repo_visible",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_missing_repo_visible",
      "to": "self::test_aggregate_lists_missing_rec_files"
    },
    {
      "from": "check_org_rec_missing_repo_visible",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_missing_repo_visible",
      "to": "org_rec_missing_repo_visible"
    },
    {
      "from": "check_org_rec_missing_repo_visible",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_missing_repo_visible",
      "to": "posix_shell"
    },
    {
      "from": "check_org_rec_missing_repo_visible",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_missing_repo_visible",
      "to": "python3"
    },
    {
      "from": "check_org_rec_remaining_fallback",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_remaining_fallback",
      "to": "self::test_aggregate_uses_remaining_when_latest_block_has_no_recommendations"
    },
    {
      "from": "check_org_rec_remaining_fallback",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_remaining_fallback",
      "to": "org_rec_remaining_fallback"
    },
    {
      "from": "check_org_rec_remaining_fallback",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_remaining_fallback",
      "to": "posix_shell"
    },
    {
      "from": "check_org_rec_remaining_fallback",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_org_rec_remaining_fallback",
      "to": "python3"
    },
    {
      "from": "check_scar_blocks_work",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_scar_blocks_work",
      "to": "self::test_scar_blocks_work"
    },
    {
      "from": "check_scar_blocks_work",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_scar_blocks_work",
      "to": "loto_scar_blocks_work"
    },
    {
      "from": "check_scar_blocks_work",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scar_blocks_work",
      "to": "git"
    },
    {
      "from": "check_scar_blocks_work",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scar_blocks_work",
      "to": "posix_shell"
    },
    {
      "from": "check_scar_blocks_work",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scar_blocks_work",
      "to": "python3"
    },
    {
      "from": "check_scope_enforced",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_scope_enforced",
      "to": "self::test_scope_enforced"
    },
    {
      "from": "check_scope_enforced",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_scope_enforced",
      "to": "loto_scope_enforced"
    },
    {
      "from": "check_scope_enforced",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scope_enforced",
      "to": "git"
    },
    {
      "from": "check_scope_enforced",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scope_enforced",
      "to": "posix_shell"
    },
    {
      "from": "check_scope_enforced",
      "kind": "requires",
      "source_block": "CHECKS",
      "source_id": "check_scope_enforced",
      "to": "python3"
    },
    {
      "from": "check_vm_mcp_admin_broker_peer_verified",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_admin_broker_peer_verified",
      "to": "self::test_serve_source_uses_peer_credentials"
    },
    {
      "from": "check_vm_mcp_admin_broker_peer_verified",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_admin_broker_peer_verified",
      "to": "vm_mcp_admin_broker_peer_verified"
    },
    {
      "from": "check_vm_mcp_admin_exec_explicit_root",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_admin_exec_explicit_root",
      "to": "self::test_admin_mode_selects_root"
    },
    {
      "from": "check_vm_mcp_admin_exec_explicit_root",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_admin_exec_explicit_root",
      "to": "vm_mcp_admin_exec_explicit_root"
    },
    {
      "from": "check_vm_mcp_broker_execution_bounded",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_broker_execution_bounded",
      "to": "self::test_admin_execution_timeout_is_bounded_when_root"
    },
    {
      "from": "check_vm_mcp_broker_execution_bounded",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_broker_execution_bounded",
      "to": "vm_mcp_broker_execution_bounded"
    },
    {
      "from": "check_vm_mcp_environment_sanitized",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_environment_sanitized",
      "to": "self::test_shell_does_not_inherit_unrelated_environment"
    },
    {
      "from": "check_vm_mcp_environment_sanitized",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_environment_sanitized",
      "to": "vm_mcp_credentials_not_inherited"
    },
    {
      "from": "check_vm_mcp_listing_symlink_not_followed",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_listing_symlink_not_followed",
      "to": "self::test_listing_does_not_follow_symlink_metadata"
    },
    {
      "from": "check_vm_mcp_listing_symlink_not_followed",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_listing_symlink_not_followed",
      "to": "vm_mcp_listing_symlinks_not_followed"
    },
    {
      "from": "check_vm_mcp_loopback_config",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_loopback_config",
      "to": "self::test_server_binds_loopback_only"
    },
    {
      "from": "check_vm_mcp_loopback_config",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_loopback_config",
      "to": "vm_mcp_loopback_only"
    },
    {
      "from": "check_vm_mcp_metadata_denial",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_metadata_denial",
      "to": "self::test_systemd_blocks_cloud_metadata_address"
    },
    {
      "from": "check_vm_mcp_metadata_denial",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_metadata_denial",
      "to": "vm_mcp_metadata_credentials_blocked"
    },
    {
      "from": "check_vm_mcp_output_bounded",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_output_bounded",
      "to": "self::test_read_text_is_bounded"
    },
    {
      "from": "check_vm_mcp_output_bounded",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_output_bounded",
      "to": "vm_mcp_output_bounded"
    },
    {
      "from": "check_vm_mcp_parent_escape_rejected",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_parent_escape_rejected",
      "to": "self::test_parent_escape_rejected"
    },
    {
      "from": "check_vm_mcp_parent_escape_rejected",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_parent_escape_rejected",
      "to": "vm_mcp_read_paths_confined"
    },
    {
      "from": "check_vm_mcp_personal_console_gate",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_personal_console_gate",
      "to": "self::test_broker_exec_requires_personal_console"
    },
    {
      "from": "check_vm_mcp_personal_console_gate",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_personal_console_gate",
      "to": "vm_mcp_personal_console_explicit"
    },
    {
      "from": "check_vm_mcp_personal_console_root_separate",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_personal_console_root_separate",
      "to": "self::test_personal_console_uses_separate_root_broker"
    },
    {
      "from": "check_vm_mcp_personal_console_root_separate",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_personal_console_root_separate",
      "to": "vm_mcp_personal_console_root_separate"
    },
    {
      "from": "check_vm_mcp_profile_default_read_only",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_profile_default_read_only",
      "to": "self::test_default_profile_is_read_only"
    },
    {
      "from": "check_vm_mcp_profile_default_read_only",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_profile_default_read_only",
      "to": "vm_mcp_profile_default_read_only"
    },
    {
      "from": "check_vm_mcp_shell_cwd_escape_rejected",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_cwd_escape_rejected",
      "to": "self::test_shell_cwd_escape_rejected"
    },
    {
      "from": "check_vm_mcp_shell_cwd_escape_rejected",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_cwd_escape_rejected",
      "to": "vm_mcp_shell_cwd_confined"
    },
    {
      "from": "check_vm_mcp_shell_output_bounded",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_output_bounded",
      "to": "self::test_shell_output_is_bounded_while_draining"
    },
    {
      "from": "check_vm_mcp_shell_output_bounded",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_output_bounded",
      "to": "vm_mcp_shell_execution_bounded"
    },
    {
      "from": "check_vm_mcp_shell_timeout",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_timeout",
      "to": "self::test_shell_timeout_is_enforced"
    },
    {
      "from": "check_vm_mcp_shell_timeout",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_shell_timeout",
      "to": "vm_mcp_shell_execution_bounded"
    },
    {
      "from": "check_vm_mcp_symlink_escape_rejected",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_symlink_escape_rejected",
      "to": "self::test_symlink_escape_rejected"
    },
    {
      "from": "check_vm_mcp_symlink_escape_rejected",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_symlink_escape_rejected",
      "to": "vm_mcp_read_paths_confined"
    },
    {
      "from": "check_vm_mcp_systemd_write_boundary",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_systemd_write_boundary",
      "to": "self::test_non_root_service_keeps_hardening"
    },
    {
      "from": "check_vm_mcp_systemd_write_boundary",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_systemd_write_boundary",
      "to": "vm_mcp_host_write_confined"
    },
    {
      "from": "check_vm_mcp_user_exec_non_root",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_user_exec_non_root",
      "to": "self::test_user_mode_rejects_root"
    },
    {
      "from": "check_vm_mcp_user_exec_non_root",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_user_exec_non_root",
      "to": "vm_mcp_user_exec_non_root"
    },
    {
      "from": "check_vm_mcp_workspace_write_confined",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_workspace_write_confined",
      "to": "self::test_write_and_move_remain_under_root"
    },
    {
      "from": "check_vm_mcp_workspace_write_confined",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_workspace_write_confined",
      "to": "vm_mcp_workspace_writes_confined"
    },
    {
      "from": "check_vm_mcp_workspace_write_gate",
      "kind": "calls",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_workspace_write_gate",
      "to": "self::test_write_requires_mutating_profile"
    },
    {
      "from": "check_vm_mcp_workspace_write_gate",
      "kind": "claims_proves",
      "source_block": "CHECKS",
      "source_id": "check_vm_mcp_workspace_write_gate",
      "to": "vm_mcp_workspace_writes_confined"
    },
    {
      "from": "gonol_authority_gate",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "gonol_authority_gate",
      "to": "skill-lib"
    },
    {
      "from": "gonol_authority_gate",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "gonol_authority_gate",
      "to": "active skill-lib projections"
    },
    {
      "from": "gonol_authority_gate",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "gonol_authority_gate",
      "to": "char-compress/SKILL.md"
    },
    {
      "from": "gonol_authority_gate",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "gonol_authority_gate",
      "to": "gonol-build/SKILL.md"
    },
    {
      "from": "interdependent_work_graph_portfolio_plan",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "interdependent_work_graph_portfolio_plan",
      "to": "The-Interdependency/skill-lib maintainers"
    },
    {
      "from": "msdmd_python_module_projection",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "msdmd_python_module_projection",
      "to": "The Interdependency skill-lib"
    },
    {
      "from": "msdmd_python_reference_parser",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "msdmd_python_reference_parser",
      "to": "The Interdependency skill-lib"
    },
    {
      "from": "msdmd_typescript_reference_parser",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "msdmd_typescript_reference_parser",
      "to": "The Interdependency skill-lib"
    },
    {
      "from": "org_ratio_comparison_runner",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "org_ratio_comparison_runner",
      "to": "Codex"
    },
    {
      "from": "org_rec_aggregation_runner",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "org_rec_aggregation_runner",
      "to": "Codex"
    },
    {
      "from": "ratios_harmonic_explorer",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "ratios_harmonic_explorer",
      "to": "The Interdependency"
    },
    {
      "from": "ratios_harmonic_explorer",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "ratios_harmonic_explorer",
      "to": "ratios_harmonic_math"
    },
    {
      "from": "ratios_harmonic_math",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "ratios_harmonic_math",
      "to": "The Interdependency"
    },
    {
      "from": "repo_loto_evidence",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "repo_loto_evidence",
      "to": "Way Seer Erin"
    },
    {
      "from": "repo_mutation_gate",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "repo_mutation_gate",
      "to": "Way Seer Erin"
    },
    {
      "from": "skill_lib_ai_installer",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "skill_lib_ai_installer",
      "to": "skill-lib"
    },
    {
      "from": "skill_lib_ai_installer",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "skill_lib_ai_installer",
      "to": "bash"
    },
    {
      "from": "skill_lib_ai_launcher",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "skill_lib_ai_launcher",
      "to": "skill-lib"
    },
    {
      "from": "skill_lib_ai_launcher",
      "kind": "requires",
      "source_block": "MODULE_BUILD",
      "source_id": "skill_lib_ai_launcher",
      "to": "local bash + ssh; remote bash + tmux; optional remote grok/codex/deepcodei CLIs"
    },
    {
      "from": "vm_mcp_admin_client",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "vm_mcp_admin_client",
      "to": "skill-lib vm-mcp maintainers"
    },
    {
      "from": "vm_mcp_control_plane",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "vm_mcp_control_plane",
      "to": "skill-lib vm-mcp maintainers"
    },
    {
      "from": "vm_mcp_personal_console_broker",
      "kind": "owns",
      "source_block": "MODULE_BUILD",
      "source_id": "vm_mcp_personal_console_broker",
      "to": "skill-lib vm-mcp maintainers"
    }
  ],
  "gaps": [],
  "repo": "The-Interdependency/skill-lib"
});
