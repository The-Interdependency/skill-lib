// ratios: loc_comments=196:0 imports_exports=1:0 calls_definitions=1:0
import { defineMsdmdCollection } from "./msdmd/collection";

// skill-lib is the canonical source of the msdmd family, not a normal consumer.
// This collection point is intentionally policy-heavy: it records the source
// surfaces other repos depend on, and it names the remaining completion gaps
// so visualizers have a root node to render.

export default defineMsdmdCollection({
  repo: "The-Interdependency/skill-lib",
  declarations: [
    {
      file: "msdmd/SKILL.md",
      block: "DOCS",
      id: "msdmd_foundational_contract",
      fields: {
        source: "msdmd/SKILL.md",
        status: "canonical",
        summary: "Module Self-Declared Metadata in Markdown block syntax, parser contract, visible gap doctrine, and collection-point shape",
      },
    },
    {
      file: "doctrine/msdmd-checks.md",
      block: "DOCS",
      id: "msdmd_checks_doctrine",
      fields: {
        source: "doctrine/msdmd-checks.md",
        status: "ratified",
        summary: "CONTRACTS are obligations, CHECKS are accountable witnesses, audit reconciles the witness list against the obligation list",
      },
    },
    {
      file: "msdmd/collect.py",
      block: "CAPABILITIES",
      id: "repo_collection_generator",
      fields: {
        exposes: "collect, render_typescript",
        summary: "Generates <reponame>_msdmd.ts collection points from module-local blocks including CHECKS",
      },
    },
    {
      file: "msdmd/collection.ts",
      block: "CAPABILITIES",
      id: "repo_collection_types",
      fields: {
        exposes: "defineMsdmdCollection, MsdmdCollection",
        summary: "Shared TypeScript shape for collection points and visualizers, including the CHECKS block name",
      },
    },
    {
      file: "msdmd/visualize.py",
      block: "CAPABILITIES",
      id: "collection_visualizer",
      fields: {
        exposes: "minimal Mermaid rendering for collection edges and gaps",
      },
    },
    {
      file: "skill_lib/safety/repo_loto.py",
      block: "MODULE_BUILD",
      id: "repo_mutation_gate",
      fields: {
        module_name: "repo_loto",
        module_kind: "instrument",
        summary: "Delete-on-completion session gate for repo mutation; presence of state means open work, absence means clean",
        tests: "tests/test_repo_loto.py (CHECKS-declared, reconciled via --audit)",
      },
    },
    {
      file: "skill_lib/safety/repo_loto.py",
      block: "CONTRACTS",
      id: "loto_scope_enforced",
      fields: {
        given: "files touched outside the declared --files globs",
        then: "close refuses with the violating paths named",
        class: "safety",
      },
    },
    {
      file: "tests/test_repo_loto.py",
      block: "CHECKS",
      id: "check_scope_enforced",
      fields: {
        proves: "loto_scope_enforced",
        call: "self::test_scope_enforced",
        requires: "git, python3, posix_shell",
        timeout: "20",
        mutates: "filesystem",
        cleanup: "tempdir_teardown",
      },
    },
    {
      file: "ratios/ratios_check.py",
      block: "CONTRACTS",
      id: "ratios_strict_gate",
      fields: {
        call: "python ratios/ratios_check.py --strict",
        summary: "Verifies first/last ratios seals for covered executable source files",
      },
    },
    {
      file: "llms/build.py",
      block: "CONTRACTS",
      id: "llms_build_drift_gate",
      fields: {
        call: "python -m llms.build --root . --out llms.txt --check",
        summary: "Checks generated llms.txt against source LLMS blocks",
      },
    },
    {
      file: "tools/check_skill_lib_drift.py",
      block: "CONTRACTS",
      id: "skill_index_drift_gate",
      fields: {
        call: "python tools/check_skill_lib_drift.py",
        summary: "Checks README, AGENTS, CLAUDE, ORG_DISTRIBUTION, skills.json, and generated llms.txt drift",
      },
    },
    {
      file: "tools/check_skill_compliance.py",
      block: "CONTRACTS",
      id: "skill_spec_compliance_gate",
      fields: {
        call: "python tools/check_skill_compliance.py",
        summary: "Checks SKILL.md frontmatter, triggers, hmmm boundaries, and index registration",
      },
    },
    {
      file: "ORG_DISTRIBUTION.md",
      block: "DEPENDENCIES",
      id: "org_target_repositories",
      fields: {
        exposes: ".agents/skills propagation contract",
        requires: "target repos listed in ORG_DISTRIBUTION.md",
      },
    },
  ],
  gaps: [
    {
      file: "skill-lib_msdmd.ts",
      missing: ["local generated refresh"],
      reason: "Still manually curated from known canonical surfaces; regenerate with python -m msdmd.collect after local checkout verification.",
    },
    {
      file: "ORG_DISTRIBUTION.md",
      missing: ["per-target source_commit audit"],
      reason: "Propagation targets are named, but each target repo still needs its copied skill-lib source commit recorded in its local .agents/skills/README.md.",
    },
    {
      file: "MSDMD_COMPLIANCE_AUDIT.md",
      missing: ["executor validity"],
      reason: "Audit measures block presence, not required-field validation or contract execution.",
    },
  ],
  edges: [
    {
      from: "repo_collection_generator",
      to: "repo_collection_types",
      kind: "emits",
      source_block: "CAPABILITIES",
      source_id: "repo_collection_generator",
    },
    {
      from: "repo_collection_types",
      to: "collection_visualizer",
      kind: "feeds",
      source_block: "CAPABILITIES",
      source_id: "repo_collection_types",
    },
    {
      from: "repo_mutation_gate",
      to: "tests/test_repo_loto.py",
      kind: "checked_by",
      source_block: "MODULE_BUILD",
      source_id: "repo_mutation_gate",
    },
    {
      from: "check_scope_enforced",
      to: "loto_scope_enforced",
      kind: "claims_proves",
      source_block: "CHECKS",
      source_id: "check_scope_enforced",
    },
    {
      from: "skill_index_drift_gate",
      to: "skills.json",
      kind: "checks",
      source_block: "CONTRACTS",
      source_id: "skill_index_drift_gate",
    },
    {
      from: "org_target_repositories",
      to: ".agents/skills/",
      kind: "propagates_to",
      source_block: "DEPENDENCIES",
      source_id: "org_target_repositories",
    },
  ],
});
// ratios: loc_comments=196:0 imports_exports=1:0 calls_definitions=1:0
