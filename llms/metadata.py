# ratios: loc_comments=0:24 imports_exports=0:0 calls_definitions=0:0
"""Self-declared LLMS metadata for skill-lib."""

# === LLMS ===
# id: project_overview
#   content: skill-lib is the canonical organization-wide source for reusable agent skills in The Interdependency.
#     It provides msdmd-based metadata skills, procedural skills, pure-stdlib helper tools, and propagation guidance for consuming repositories.
#
# id: key_definitions
#   msdmd: Module Self-Declared Metadata in Markdown — native-first collection of existing code, documentation, manifest, schema, tooling and evidence metadata; MSDMD blocks supply otherwise unexpressed information. The shipped collector remains block-only.
#   char-compress: Skill-lib-owned character-based context compression for agent handoff and skill writing; its historical bone/flesh and text-stack notation is not current UCNS mathematics.
#   llms-build: LLM instruction publication from owning metadata; the shipped runner generates root llms.txt from LLMS blocks, while native-reader integration remains a contract.
#
# id: architecture_summary
#   content: - Skills live as root directories with SKILL.md files and optional helpers.
#     - Metadata skills consume native owning conventions first; supplemental blocks include DOCS, CAPABILITIES, DEPENDENCIES, OWNERS, CONTRACTS, CHECKS, MODULE_BUILD, BOUNDARIES and LLMS. RATIOS keeps its separate non-block boundary syntax.
#     - Procedural skills define agent behavior without adding a metadata block.
#     - Pure-stdlib helpers live under tools; the llms package provides the python -m llms.build runner.
#
# id: usage_rules
#   content: - Read AGENTS.md, skills.json, and the relevant skill file before changing a skill.
#     - Ground responses in literal repository files including skill specs, parser source, helper source, README.md, ORG_DISTRIBUTION.md, CLAUDE.md, and generated llms.txt.
#     - Do not infer or expand declared key definitions.
#     - Write unresolved or missing values as hmmm; unsupported readers and unvalidated identities do not establish complete coverage.
#     - Edit source LLMS blocks before regenerating llms.txt.
# === END LLMS ===
# ratios: loc_comments=0:24 imports_exports=0:0 calls_definitions=0:0