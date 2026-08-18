---
name: gonal-morphology
description: Current UCNS affixiation and morphology boundary. Load this when working on gonol composition across scale, lexical morphology, recursive closure, atomic gonols, or direct interscale coupling. Affixiation is scale-invariant: gonols couple, the relationship enters the resulting gonol, closure produces a new gonol, and the result becomes atomic at the next scale. Morphological prefixes/suffixes are one linguistic instance, not the definition of affixiation. The final English root/stem/affix/transformation law is unresolved; do not import the historical omega/phi/psi three-core model as current canon.
---

# gonal-morphology — affixiation across scale

This skill records the current operational doctrine needed by Codex when UCNS work crosses character, morphology, definition, and deeper recursive scales.

The earlier three-core `omega / phi / psi` morphology, fixed bone/flesh classification, and claim that one carrier-LCM product already supplies the full language decomposition are **historical candidate material, not current morphology canon**. Do not use those assumptions to fill unresolved gaps.

## Core invariant

Affixiation is the scale-invariant composition pattern:

```text
atomic gonol(s)
    ↓ couple / affixiate
relationship enters the resulting gonol
    ↓ closure
new gonol
    ↓
atomic at its scale
```

A completed gonol may retain arbitrarily rich internal construction, but the next scale consumes it as one atomic object unless the task explicitly reopens it.

`atomic` therefore means **indivisible for participation at the current higher scale**, not internally structureless and not provenance-free.

## Load this when

- constructing words from character gonols;
- investigating roots, stems, affixes, inflections, derivations, transformations, compounds, or irregular morphology;
- composing definition gonols from already-atomic word gonols;
- designing recursion where completed definition gonols participate as atomic objects;
- reasoning about compression created by recursive closure;
- implementing or reviewing direct coupling between gonols at different recursive scales;
- deciding whether an implementation has incorrectly externalized a relationship that should be intrinsic to a gonol.

## Scale is not one-way

A larger-scale gonol may couple a smaller-scale gonol and a smaller-scale gonol may couple a larger-scale gonol.

Direct coupling across non-adjacent recursive scales is allowed by the current UCNS architecture. Do not require a relation to reopen and traverse every intermediate closure merely because that is easier to implement.

```text
high-scale gonol
       ↘
         direct coupling
       ↗
low-scale gonol
```

Both participants remain atomic at their own scales.

The executable geometry for distant interscale coupling remains to be demonstrated once corresponding gonols exist. Permission to couple directly is architectural; proof of a particular implementation is separate evidence.

## Relationships enter gonols

Do not model the authoritative semantic or structural state as:

```text
gonol + external relationship graph
```

when the relation is part of the gonol's construction.

The intended pattern is:

```text
relation among gonols
    ↓
relation becomes intrinsic
    ↓
closure
    ↓
new atomic gonol
```

Sidecar records may preserve provenance, receipts, indexes, caches, or measurement projections. They do not substitute for the relationship entering the gonol.

## Lexical manifestation

For the current UCNS lexical program, read `The-Interdependency/ucns:docs/LEXICAL_RECURSION_ARCHITECTURE.md` before acting.

The active sequence is:

```text
characters
    ↓
morphology
    ↓
definitions
    ↓
recursive gonol relations
```

Character relations construct word gonols. Once word gonols exist they become atomic. Morphological relations then act on atomic gonols. Definition relationships enter definition gonols, which close and become atomic for the next recursion.

## Morphology is intentionally unresolved

The place of morphology is established; the complete English morphology law is not.

Known boundaries:

- affixes may themselves be gonols;
- affixiation and transformation must be representable;
- relationships discovered in morphology enter the resulting gonol;
- a completed morphological gonol becomes atomic at its scale;
- source evidence and provenance must be retained.

Do **not** assume:

- every word is `root + affix`;
- an OEWN lemma is necessarily a final linguistic root;
- one stemmer or lemmatizer is morphology canon;
- the historical omega/phi/psi three-core split is current authority;
- adjectives/adverbs/closed-class categories must be assigned to historical `bone` / `flesh` roles;
- `multiplyFuel`, carrier-LCM, or any other existing UCNS operation is automatically the complete morphology law merely because it can compose objects.

Inventory source morphology and current UCNS mechanisms first. Preserve unresolved decomposition as `hmmm`.

## Character-scale relation reminder

The current UCNS lexical architecture declares a shared Möbius glyph-axis traversal: glyph spaces are axes, glyphs are tics, accumulated traversal history is intrinsic, and the available future narrows with each realized step.

A completed word gonol closes that lower-scale traversal and then participates atomically. Do not repeatedly expand its character sequence at every higher-scale use.

## Materialization discipline

Do not pre-materialize every possible pairwise relation among all gonols.

Materialize unique completed gonols and their intrinsic construction identities. Reuse the same atomic identity when the same gonol recurs. Compute or expose cross-gonol relations from the gonol construction when needed rather than duplicating an authoritative all-pairs edge table.

This is an implementation discipline, not a claim that every cache or index is forbidden.

## Compression hypothesis

Recursive atomic closure is expected to provide structural compression:

```text
many lower-scale relations
    ↓
one reusable atomic gonol
    ↓
many higher-scale relations
    ↓
one reusable higher gonol
```

Direct interscale coupling is expected to preserve the utility of that compression by avoiding mandatory reopening of every intermediate scale.

Compression ratio, lossless reconstruction, and performance remain empirical questions. Do not claim them before measurement.

## Cognitive-origin boundary

The construction is informed by Erin Spencer's report of their own cognitive experience: many relations close into one mentally atomic object, atomic objects can couple across apparently distant scales, and internal structure may be reopened when needed.

Treat that as design provenance, not evidence that all human cognition works this way.

## Historical three-core material

The previous skill revision described:

- omega = bones;
- phi = roots;
- psi = words;
- fixed weights;
- a char -> circle -> seed ladder;
- carrier-LCM / `multiplyFuel` as the one language operator;
- bone/flesh category assignments.

Those claims are retained in Git history. They must not be read forward as current morphology canon unless independently re-authorized by current source evidence.

Existing UCNS multiplication/cancellativity work remains valid within its own declared scope. This correction does not falsify those mathematical experiments; it removes an unjustified semantic promotion from them into the current morphology architecture.

## Anti-patterns

- Treating affixiation as merely prefix/suffix concatenation.
- Re-expanding every lower-order constituent whenever an atomic gonol is reused.
- Building an external semantic graph and calling it the semantic content of the gonols.
- Requiring adjacent-scale traversal for every distant interscale relation.
- Reinstating omega/phi/psi, bone/flesh, or fixed morphology weights because an older skill contains them.
- Inventing a root/stem decomposition to make the pipeline look complete.
- Treating implementation convenience as architectural authority.

## hmmm

- the source-supported English root/stem/affix/transformation law;
- the exact executable geometry for direct coupling between gonols separated by several recursive scales;
- quantitative compression and reconstruction behavior after recursive gonols are materialized;
- which existing UCNS composition primitives survive as mechanisms inside the corrected architecture without semantic overpromotion.
