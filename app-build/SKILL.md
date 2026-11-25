---
name: app-build
description: Load this when building, extending, or repairing an interactive app or web surface — a desk, form, dashboard, page, or sign-in path. Load msdmd and generate the docs from the metadata at the code. Do not load to author or revise a skill; use skill-build. Do not load for interdependentway.org file edits; use website-builder-journal. Do not load for a static document or a skill-only module declaration.
---

# app-build — load msdmd, then ship the surface

`msdmd` is the skill that turns metadata at the code into the document. This skill does not redefine that path.

## Trigger

Load when the user asks to build, extend, or repair an interactive app or web surface.

## Non-trigger

- Authoring or revising a skill. Use `skill-build`.
- Editing `The-Interdependency/The-Interdependency.github.io`. Use `website-builder-journal`.
- A static document, deck, or spreadsheet.
- A module declaration with no user-facing surface.

## Workflow

1. Freeze the purpose as a description. Do not turn it into an org chart, curriculum, or legal object.
2. Load `msdmd/SKILL.md`.
3. Declare otherwise-unexpressed facts as msdmd blocks at the owning source. Native docs and native metadata stay where they already are. Do not duplicate them.
4. Generate the doc with msdmd. Do not write a parallel document by hand.
   ```bash
   python -m msdmd.collect --root . --repo <repo> --out <repo>_msdmd.ts
   python -m msdmd.visualize <repo>_msdmd.ts --out <repo>_msdmd.mmd
   ```
   The `.ts` and `.mmd` are generated. If either is wrong, change the metadata and regenerate.
5. Decide persistence before styling. Device-local keeps auth off. Shared or account-following turns auth on and scopes every query to the signed-in user or a membership they hold.
6. A signed-out gate must contain a real sign-in control. An optional identity check gates a hold, not entry, unless the user requires entry to be gated.
7. Verify in a browser at desktop and mobile.

## Validation

- The published doc was produced by msdmd from metadata at the code.
- A stranger can name the purpose from the first screen.
- Signed-out has a working sign-in control, or auth is off and the surface is usable.

## Anti-patterns

- A handwritten README that restates the code.
- A local extractor that invents a second metadata schema.
- Blocks with no working control.

## hmmm

- Host-specific auth providers and database drivers stay in the host skill.
- If `msdmd` is not installed, propagate it from `The-Interdependency/skill-lib` into `.agents/skills/msdmd/` before generating. Do not substitute another collector.
