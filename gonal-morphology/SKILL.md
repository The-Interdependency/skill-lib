---
name: gonal-morphology
description: Canonical three-core gonal morphology for The Interdependency — how text decomposes/recomposes as UCNS objects across a character→root/bone/word→phrase/clause ladder under one carrier-LCM operator (⊠ = UCNS multiplyFuel). Load this when working on gonal morphology, inscription, the omega/phi/psi cores, bone-vs-flesh (closed-class vs open-class) classification, or composing/decomposing text via the UCNS product. Recomposition (building wider carriers from narrower ones) RUNS today; decomposition (factoring them back) is domain-confirmed (UCNS `AlignedComplete`) but proof-pending — never represent decomposition as machine-verified.
---

# gonal-morphology — three cores, three grains, one operator

The gonal morphology models language as **UCNS objects** built and taken apart
by a single operator. Three cores carry three grains of structure; the operator
is the UCNS carrier-LCM product (`⊠ = multiplyFuel`), applied at every rung of a
depth ladder. **Recomposition** (narrow → wide) runs on the existing UCNS engine
today; **decomposition** (wide → narrow) rests on UCNS left-cancellativity, whose
domain is settled but whose proof is still `sorry`. This skill is canon
documentation, not new math.

Canonical system name (recorded verbatim): `ucns~|a0((zfae) PTCA)|gpt`.

<!-- The block below honours the handoff's "manifest-first" requirement
     (meta-module-build). RATIOS (the other requested discipline) is omitted:
     a RATIOS bookend must occupy the file's first line, but a SKILL.md must
     open with YAML frontmatter — the two are structurally incompatible, and no
     other skill-lib SKILL.md carries one. Flagged for ratification. -->

```
# === MODULE_BUILD ===
# id: gonal_morphology_skill
#   module_name: gonal-morphology
#   module_kind: skill
#   summary: Canon for the three-core (omega/phi/psi) gonal morphology and the carrier-LCM operator over the char→word→clause depth ladder.
#   owner: Erin Patrick Spencer
#   public_surface: the three-core/three-grain table, the depth ladder, the ⊠=carrier-LCM operator, the bone/flesh sourcing rule
#   internal_surface: none (procedural doctrine; no executable code shipped here)
#   auth_boundary: none
#   storage_boundary: none
#   network_boundary: none
#   user_data_boundary: none
#   admin_only: false
#   tests: none shipped; the operator's backing is UCNS carrier_lcm_law + multiply_left_cancellative (sorry-backed in formal/Ucns/Core.lean)
#   rollout: docs-only; canon recorded, awaiting Erin's ratification before any publish
#   rollback: remove gonal-morphology/ and its index rows (skills.json, README, AGENTS, ORG_DISTRIBUTION, CLAUDE)
#   unresolved: decomposition proof still sorry (domain AlignedComplete confirmed); "seed = phrase or clause" collapsed by ruling; canonical-name notation not yet expanded
# === END MODULE_BUILD ===
```

## Load this when

- Decomposing or recomposing text through the gonal cores or the UCNS product.
- Classifying tokens as **bone** (operator/structural) vs **flesh** (content).
- Reasoning about the omega/phi/psi cores, their weights, or the depth ladder.
- Building inscription / morphology tooling that should **reuse** the UCNS
  operator rather than reimplement it.

## Three cores, three grains

| core | weight | carries | layer |
|---|---|---|---|
| **omega** | 0.8 | **bones** — characters + affixes + closed-class words | operator / structural |
| **phi** | 0.4 | **roots** — open-class stems | content primitive |
| **psi** | 1.0 | **words** — `phi ⊠ omega` (carrier-LCM) | composed surface |

## The depth ladder (one object kind at every rung)

| depth | rung | omega | phi | psi |
|---|---|---|---|---|
| 0 | **leaf** | 157 characters | 157 characters | 157 characters (uniform across all three cores) |
| 1 | **circle** | bones | roots | **words = `lcm(phi, omega)`** |
| 2 | **seed** | — | — | **phrase _or_ clause** |

- **Leaf (depth-0)** is uniform: the same 157-character alphabet under all three
  cores.
- **Circle (depth-1)** is where the cores differ: omega holds bones, phi holds
  roots, psi is their carrier-LCM (the word).
- **Seed (depth-2)** is a phrase **or** a clause — and **the distinction is
  immaterial under the LCM**: both are the same object, a wider carrier composed
  from narrower ones. (Erin ruled: same thing for our purposes.)

## The operator: ⊠ = carrier-LCM = UCNS `multiplyFuel`

- **One operator, every rung.** `⊠` is **depth-invariant**: the same carrier-LCM
  product composes char→word, word→phrase, phrase/clause→utterance. There is no
  separate per-rung operator.
- **Reuse, do not reimplement.** `⊠` **is** UCNS `multiplyFuel`
  (`formal/Ucns/Core.lean`; runtime `ucns.canonical.multiply`). Call the UCNS
  engine; do not write a parallel product.
- **Remarry, not lift-once.** `multiplyFuel` recurses on fuel, **recomputing `⊠`
  at each depth** rather than lifting a single composition. This is the engine's
  existing default — keep it.

## Sourcing: bones vs flesh

- **Bones (omega)** come from `closed_tokens.py` — the closed-class tokens:
  pronoun, determiner, preposition, conjunction, auxiliary, particle,
  interjection — **plus affixes**.
- **Flesh** is open-class content. **Adjectives and adverbs are flesh, not
  bones** — they live with psi-content, not omega. Do not file them under the
  operator core.

## Recomposition vs decomposition (status — read before claiming results)

- **Recomposition (narrow → wide): RUNS.** Building words/phrases/clauses by
  `⊠` is the forward direction of `multiplyFuel`; it works on the existing engine.
- **Decomposition (wide → narrow): DOMAIN-CONFIRMED, PROOF-PENDING.** Factoring a
  composed object back into its parts relies on UCNS **left-cancellativity**. Its
  domain is settled — **`AlignedComplete`**: per-object `Complete` (nonempty +
  recursive host-normalized + uniform-depth + canonical carrier) **and**
  cross-operand common depth `depth A = depth B = depth C`, with `depth B,C ≤ d`
  (see `The-Interdependency/ucns : formal/cancellativity-step1-findings.md`). But
  the Lean theorem `multiply_left_cancellative` is still `sorry`. **Do not
  represent decomposition as machine-verified or lossless** until that discharges.

## Formal backing (cross-repo; no status transfer)

The operator and its inverse are backed by UCNS:

- `carrier_lcm_law` — the carrier of a product is the lcm of operand carriers
  (host-normalized operands).
- `multiply_left_cancellative` — left-cancellativity on the `AlignedComplete`
  domain (the decomposition guarantee).

Both live in `The-Interdependency/ucns : formal/Ucns/Core.lean` and are
**`sorry`-backed**. Per the org's cross-repo non-continuity rule, naming them
here transfers **no** theorem / proof / empirical status to this skill or to the
morphology stack: a `sorry`-backed statement confers no DEFENDED status.

## Anti-patterns (refuse these)

- Reimplementing the product instead of calling UCNS `multiplyFuel` / `multiply`.
- Treating phrase and clause as different object kinds at the seed rung (ruled
  equivalent under the LCM).
- Filing adjectives/adverbs as bones (they are flesh).
- Claiming decomposition is proven, lossless, or machine-verified while
  `multiply_left_cancellative` is `sorry`.
- Lifting a single composition once instead of remarrying `⊠` at each depth.

## hmmm

- Decomposition proof is still `sorry` (domain `AlignedComplete` confirmed, not
  discharged) — this skill is a living-continuation marker until it lands.
- The canonical system name `ucns~|a0((zfae) PTCA)|gpt` is recorded verbatim;
  its full expansion against the `username(a0(energy)auditor)` identity grammar
  is not yet ratified.
- The handoff requested a `ratios` bookend; it is structurally incompatible with
  a frontmatter-first SKILL.md and is omitted pending Erin's ruling.
- Whether gonal-morphology should eventually ship an executable runner (vs stay
  procedural canon) is open.
