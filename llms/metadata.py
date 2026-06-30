# ratios: loc_comments=0:24 imports_exports=0:0 calls_definitions=0:0
"""Self-declared LLMS metadata for skill-lib."""

# === LLMS ===
# id: project_overview
#   content: skill-lib is the canonical organization-wide source for reusable agent skills in The Interdependency.
#     It provides msdmd-based metadata skills, procedural skills, pure-stdlib helper tools, and propagation guidance for consuming repositories.
#
# id: key_definitions
#   msdmd: Module Self-Declared Metadata in Markdown — the foundational convention where each source module declares its own structured metadata in a fenced comment block.
#   char-compress: Character-based context compression for agent handoff and skill writing, derived from the mathematics of the Unit Circle Number System.
#   llms-build: Self-declaring LLM instructions file generation from LLMS blocks into canonical root llms.txt.
#
# id: architecture_summary
#   content: - Skills live as root directories with SKILL.md files and optional helpers.
#     - Metadata-block skills apply msdmd to structured blocks such as DOCS, CAPABILITIES, DEPENDENCIES, OWNERS, CONTRACTS, MODULE_BUILD, BOUNDARIES, RATIOS, MANIFEST, and LLMS.
#     - Procedural skills define agent behavior without adding a metadata block.
#     - Pure-stdlib helpers live under tools; the llms package provides the python -m llms.build runner.
#
# id: usage_rules
#   content: - Read AGENTS.md, skills.json, and the relevant skill file before changing a skill.
#     - Ground responses in literal repository files including skill specs, parser source, helper source, README.md, ORG_DISTRIBUTION.md, CLAUDE.md, and generated llms.txt.
#     - Do not infer or expand declared key definitions.
#     - Write unresolved or missing values as hmmm.
#     - Edit source LLMS blocks before regenerating llms.txt.
# === END LLMS ===
# ratios: loc_comments=0:24 imports_exports=0:0 calls_definitions=0:0
