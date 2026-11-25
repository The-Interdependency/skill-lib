---
name: char-compress
description: Character-based context compression for agent handoff and skill writing, owned as a skill-lib procedure rather than current UCNS mathematics. Use this when compressing a long thread, document, repo audit, canon handoff, or agent working-memory state; when a context window is filling and operative facts must survive; when writing a SKILL.md that should be flesh-dense and bone-sparse; or when checking whether a compression deleted negation, order, quantifier, operator, named object, value, decision, or unresolved hmmm. Historical bone/flesh and text-stack terminology is local compression notation, not a UCNS theorem/status transfer, active language-construction authority, or EDCM metric implementation.
---

# char-compress — bone/flesh compression for agent context

`char-compress` is a skill-lib-owned procedure: preserve irreducible content,
suppress only safely regenerable recurrence, and reconstruct through an
explicit shared grammar/domain. Its historical bone/flesh and text-stack
vocabulary is retained as local compression notation, not asserted as current
UCNS mathematics. It is not an implemented UCNS compression engine.

It separates text into:

- irreducible content that must be carried in full;
- meaning-critical small operators that must be frozen even though they look
  grammatical;
- regenerable connective scaffold that can be dropped and restored by grammar;
- unresolved boundary objects that must remain visible as `hmmm`.

The working asymmetry:

```text
Bones are often recoverable from inventory + grammar + slot expectation.
Flesh is not recoverable except by carrying the thing itself.
```

The compression rule:

```text
Drop only what is safely regenerable.
Carry every operative item exactly once.
When unsure, classify the unit as flesh.
```

## Repository placement

This skill belongs in `The-Interdependency/skill-lib` as a procedural skill.
It can be propagated into `.agents/skills/char-compress/` in other repos, but
this repo remains the canonical source.

### Relation to `ucns`

`ucns` owns current gonol objects, constructors, and geometry, not lexical
classes or this compression procedure. Active language-gonol construction is
owned by the applicable research workspace in `The-Interdependency/stack`;
EDCM owns measurement/evaluation only. None of those authorities is acquired
by calling a text inventory a carrier or a separator a twist.

The vocabulary below records this skill's historical model only. An exact
historical UCNS source establishing that model is unresolved (`hmmm`); no current
UCNS mathematical derivation is claimed. Resolve an exact producer contract
before using any actual UCNS operation or active Stack construction contract.

Allowed relation:

- character inventories and suppressed fingerprints are local compression artifacts;
- this skill defines agent behavior for applying those artifacts to context;
- future code needs a separately declared, tested codec contract;
- proof/status claims must remain scoped to the specific UCNS theorem or tested
  implementation that establishes them.

Forbidden phrasing:

```text
Theorem N validates the char-compress skill implementation.
The fixture runner is the full UCNS compression engine.
char-compress has DEFENDED UCNS theorem status.
SEQ-PRIME applies to compressed transcript objects.
```

### Relation to `edcm`

`edcm` owns EDCM measurement and evaluation. Its maintained
structural-measurement implementation is `edcm/measurement/`, consolidated from
`edcmbone` (archived 2026-07-28; superseded by `edcm`). `edcm` also carries the F1–F6
failure taxonomy (deletion, mutation, inversion, category collapse, persistence
failure, decorative preservation) and F-loss labels for text transforms in
`edcm/falsifiability_bridge.py`. This skill is not an EDCM metric runtime. It
is an agent procedure that should be measurable by EDCM.

Use EDCM doctrine as a guardrail:

- if dropping a unit would cause deletion, mutation, inversion, category
  collapse, persistence failure, or decorative preservation, the unit is not
  droppable;
- negations, quantifiers, modal force, operators, and ordering words are treated
  as frozen bones unless a domain-specific test proves they are safe to
  regenerate;
- reconstruction should be checked against F-loss and operator preservation
  when an EDCM runner is available.

## Optional local text-stack notation

The following is an optional notation for text grouping, not a UCNS construction
law or a mandatory Stack language-construction ladder. Here `tensor`, `twist`,
`gonol`, `carrier`, `spiral`, and `chirality` are historical local labels, not
constructed geometry.

See [references/text-stack-and-channels.md](references/text-stack-and-channels.md) for the scale mapping, `word_gonol` recurrence example, and multi-scale recurrence pattern.

The compressor preserves first-cycle carrier vertices, recurrence weights or
layers required for reconstruction, frozen operators, flesh anchors, chirality,
scope, and `hmmm`. It suppresses only recurrence or connective scaffold that is
safe to regenerate inside the declared grammar/domain.

## Channels

| Channel | Contents | Compression rule |
|---|---|---|
| `FLESH` | Entities, values, paths, repos, URLs, decisions, claims, statuses, dates, quantities, secrets, canonical spellings, `hmmm` | Carry in full once; never drop as prose |
| `FROZEN_BONE` | `not`, `never`, `no`, `without`, `only`, `all`, `none`, `some`, `any`, `if`, `unless`, `except`, ordering, modals, comparators, status/privacy labels | Freeze explicitly; dropping alters polarity/scope/status |
| `REGENERABLE_BONE` | Articles, routine prepositions, ordinary conjunctions, filler scaffold | Drop in context compression or fingerprint in structure-preserving mode |
| `TRANSFORM` | Affixes and grammatical inflections (`root` + `transform`) | Store root + transform; promote to frozen if legal/safety/theorem status changes |
| `HMMM` | Unresolved constraints, unknown sources, incomplete tests, grammar mismatches | Carry explicitly; never delete |

See [references/text-stack-and-channels.md](references/text-stack-and-channels.md) for full channel examples.

## Suppression sort

Second-instance suppression on a string keeps the first occurrence of each
character and drops repeats:

```text
banana -> ban
committee -> comite
```

The result is an inventory fingerprint. In this local notation it preserves the
first-occurrence inventory, with recurrence retained as explicit ordered data
when required. For closed-class words in known slots, that fingerprint plus
grammar often recovers the word. For open-class content, the same operation can
destroy needed information unless recurrence and position data are carried.

Use suppression as a classifier, not as the complete codec:

```text
survives suppression + grammar can restore it -> candidate bone
breaks under suppression or carries operative fact -> flesh
looks grammatical but controls polarity/order/scope/status -> frozen bone
separator/boundary data that changes attachment or closure must be preserved
```

## Compression procedure

1. **Mark the domain.** State the repo, thread, language, and grammar assumed by
   the reconstruction. Compression is only lossless relative to that grammar.

2. **Declare the text grouping.** Use source-appropriate character, word,
   sentence, or other boundaries. The optional local text-stack notation above
   is not required and does not authorize UCNS geometry or active Stack
   construction.

3. **Run a suppression sort.** Identify first-occurrence inventory,
   recurrence data required for reconstruction, units that survive as
   recognizable scaffold, and units that become ambiguous or lose operative
   force. Historical `carrier`/`layer` labels apply only when that optional
   notation is explicitly selected.

4. **Extract flesh once.** Record every distinct operative item in resolved form.
   Do not repeat a flesh item unless the repetition itself is meaningful.

5. **Freeze dangerous bones.** Preserve negation, quantifiers, conditionals,
   modal force, operators, ordering, proof/status labels, privacy labels, and
   any small word that controls meaning.

6. **Record transforms.** Store root plus transform where the surface form is
   regenerable. Promote the transform to frozen bone when it changes status,
   safety, legality, or theorem scope.

7. **Preserve boundary data where it changes attachment.** Spaces, punctuation,
   paragraph breaks, and other separators must survive when they affect
   attachment or closure. Call them `twist` data only when using the optional
   historical notation.

8. **Drop regenerable scaffold.** Remove articles, routine connective prose,
   and repeated explanation that adds no new operative item.

9. **Carry hmmm.** Preserve unresolved constraints as explicit `hmmm` entries.
   Never convert unknowns into guesses to improve compression.

10. **Reconstruct and compare.** Regenerate readable prose around the skeleton.
    Check named objects, values, decisions, negations, operators, order,
    statuses, boundary/attachment closure, and hmmm. If any operative item is
    missing or inverted, move it to flesh, frozen bone, or preserved boundary
    data.

## Output shape for compressed handoffs

Use this notation-neutral shape when compressing a thread or repo audit. Include
`text_stack` only when the optional historical notation is actually selected.

```yaml
char_compress:
  domain: <repo/thread/document/language>
  mode: context-compression | structure-preserving
  ucns_relation: no current geometric derivation claimed
  local_notation: none | historical-text-stack
  flesh:
    - <distinct operative item>
  frozen_bones:
    - <meaning-critical operator/scope/status unit>
  boundary_data:
    - <space/punctuation/break/closure data that changes attachment>
  recurrence:
    - unit: <first-occurrence unit>
      positions_or_weights: <required recurrence data>
  transforms:
    - root: <root>
      transform: <prefix/suffix/class/aspect/polarity>
      status: regenerable | frozen
  dropped_bones:
    - <class of scaffold dropped, not every occurrence>
  reconstruction_checks:
    named_objects: pass | fail
    values: pass | fail
    decisions: pass | fail
    negation: pass | fail
    quantifiers: pass | fail
    order: pass | fail
    operators: pass | fail
    statuses: pass | fail
    boundary_closure: pass | fail
    hmmm: pass | fail
  hmmm:
    - <unresolved constraint>
```

Optional historical extension:

```yaml
text_stack:
  tensor: character
  twist: space_or_separator
  word: character_gonol
  sentence: word_gonol
  paragraph: sentence_gonol
  chapter: paragraph_gonol
  volume: chapter_gonol
```

## Skill-writing use

A `SKILL.md` should be flesh-dense and bone-sparse.

Keep:

```text
schemas, constants, invariants, load triggers, procedures, forbidden phrases,
status labels, tests, boundary rules, output shapes, hmmm
```

Minimize:

```text
long connective explanation, repeated motivation, prose restatement of tables,
examples that add no new boundary, decorative summaries
```

Do not remove:

```text
negation, ordering, scope, proof boundary, security warning, privacy status,
operator semantics, failure criteria, attachment/closure boundaries
```

Test a skill by stripping the connective prose. If the operative content still
stands, the skill is dense. If the rule changes when prose is removed, the
removed prose was misclassified.

## Executable support

Minimum preservation fixtures live in:

```text
char-compress/fixtures.json
```

Run them with:

```bash
python tools/char_compress_check.py
python tools/char_compress_check.py --json
```

The runner is a local preservation guardrail, not a UCNS compression
engine. It verifies that the fixture skeleton preserves negation, quantifier,
order, values, statuses, secrets, `hmmm`, and the theorem/status boundary.

## Falsifiability tests

A char-compression fails if reconstruction produces any of these:

- missing named object;
- missing number, date, path, carrier, repo, or URL;
- dropped negation;
- widened `only`, `must`, `cannot`, `unless`, or `except`;
- swapped order of operations;
- changed proof/status label;
- transformed `private` into `public` or `secret` into `publishable`;
- replaced a specific class with a vague category;
- preserved decorative wording while deleting operative force;
- omitted an unresolved `hmmm`;
- treated a space, punctuation mark, or paragraph break as absence when it
  changes closure or attachment;
- lost recurrence order where ordered recurrence is required for reconstruction.

Minimum fixture set for an implementation:

```text
1. negation_preserved: "not a supervisor" does not reconstruct as supervisor
2. quantifier_preserved: "only X" does not reconstruct as "X among others"
3. order_preserved: first/then/last stays ordered
4. value_preserved: numbers, dates, paths, repos, URLs survive exactly
5. status_preserved: EXPERIMENTAL does not reconstruct as DEFENDED
6. secret_preserved: private carrier material stays private
7. hmmm_preserved: unresolved constraints remain visible
8. no_theorem_transfer: output does not claim unearned theorem/status support
9. boundary_preserved: spaces/punctuation/breaks that change attachment survive
10. recurrence_preserved: repeated units keep required position/order/weight data
```

## Security note

Compression is not opacity. Bone fingerprints leak structure: clause count,
hinge placement, relation shape, boundary placement, and sometimes operator
class. If opacity is required, the inventory-to-position mapping is key material
and must not be published.

Do not place private carrier arrangements, slot maps, secret alphabets, or
cryptographic mappings in public skills, public README files, demos, tests, or
handoffs.

## Completion criteria

A compression is complete when:

```text
all flesh appears once in resolved form;
all frozen bones are explicit;
transforms are root + transform;
source grouping and grammar required for reconstruction are declared;
boundary/separator details that affect closure or attachment are preserved;
recurrence position/order/weight data required for reconstruction are preserved;
regenerable scaffold is absent or fingerprinted according to mode;
hmmm is visible;
reconstruction preserves named objects, values, decisions, negation,
quantifiers, order, operators, statuses, boundary closure, recurrence, and unresolved constraints;
no theorem/proof/status support is inferred from this procedure or its optional historical notation.
```

When `local_notation: historical-text-stack` is selected, additionally record
the chosen text-stack scale and any `twist`/`carrier`/`layer` details required
for reconstruction. Those historical fields are not required in notation-free
compression.

## Anti-patterns

- Carrying full connective prose and calling it compression.
- Dropping a named object, value, status, path, repo, URL, or decision.
- Dropping `not`, `only`, `unless`, `must`, `cannot`, `before`, or `after`.
- Treating a short token as safe because it is common.
- Treating a meaningful separator as absence when it changes attachment.
- Treating recurrence weight as enough when ordered recurrence is required.
- Treating the bone channel as opaque.
- Compressing an unresolved constraint into silence.
- Treating the fixture runner as the full Unit Circle Number System compression engine.
- Claiming theorem/status support without an implementation and tests.
- Claiming EDCM metric status without an implementation and tests.

## hmmm

- the bone/flesh boundary is grammar-relative and domain-relative
- numerals are inventory-poor like bones but content-bearing like flesh
- transform vocabulary may be closed in one repo and open in another
- reconstruction assumes a shared grammar; a different agent grammar may
  regenerate different bones
- `tools/char_compress_check.py` is deterministic fixture support, not a full codec
- exact historical source for the text-stack model remains unresolved; this helper is not a UCNS codec
- whether repeated characters become weights only, ordered recurrence layers only,
  or both
- whether future structure-preserving mode should carry bone fingerprints,
  dependency slots, twist seams, recurrence layers, or all of them
- whether opacity should layer on top of this compression or replace the
  inventory boundary with a secret mapping