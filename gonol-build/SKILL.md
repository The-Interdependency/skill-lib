---
name: gonol-build
description: Construction, review, replay, and continuation discipline for UCNS gonols. Load this when building character, word, morphology, definition, punctuation-function, or recursive gonols; when deciding whether a relationship belongs inside a gonol; when promoting a completed gonol to atomic participation at another scale; or when reviewing UCNS lexical-floor and recursive-gonol work. Do not load for unrelated geometric objects or ordinary prose editing. Treat current UCNS canon and receipts as authority; never restore historical gonal-morphology, omega/phi/psi, bone/flesh, or carrier-LCM language rules.
---

# gonol-build — construct, close, promote, recurse

Use this procedural skill to preserve gonol construction semantics while UCNS
changes. The authoritative definitions, source identities, executable APIs, and
evidence statuses live in the current `The-Interdependency/ucns` repository.
This skill governs how an agent works; it does not copy a frozen UCNS snapshot
into organization doctrine.

## Workflow: source gate

Before acting:

1. Resolve the current UCNS commit or PR under work.
2. Read its `AGENTS.md`, `CANON.md`, applicable option registry, relevant
   architecture document, behavior-bearing source declarations, tests, and
   evidence receipts.
3. Distinguish declared architecture, implemented construction, surviving or
   falsified evidence, proposed continuation, and `hmmm`.
4. If the governing sources disagree, stop at the conflict. Do not choose the
   most convenient or most recent-looking sentence.

Repo-local UCNS authority may evolve without a skill-lib release. This routing
rule is deliberate.

## Construction invariant

```text
eligible gonol participants
    -> explicit relation or function application
    -> relation enters the construction
    -> closure with source identity and receipt
    -> completed gonol
    -> atomic participant at another scale
```

`atomic` means indivisible for participation at the consuming scale. It does
not mean internally structureless, provenance-free, irreversible, or forbidden
from inspection.

When a relationship helps constitute the result, keep it intrinsic to the
gonol construction. Sidecars may carry indexes, caches, projections,
provenance, and receipts; an external edge table does not become the gonol's
authoritative relational content merely because it is easier to query.

## Active lexical order

Preserve this construction order unless current UCNS canon explicitly changes
it:

```text
characters -> morphology -> definitions -> recursive gonol relations
```

This is an order of construction dependencies, not permission to flatten every
word into characters at every later use. Close each completed scale and reuse
its atomic identity.

## Closure rules

- Preserve ordered occurrence identity, multiplicity, exact source evidence,
  source offsets, and provenance required by the governing UCNS profile.
- Apply no normalization, folding, trimming, deduplication, inferred sorting,
  or silent collapse unless the current profile explicitly authorizes it.
- Keep word closure intact inside a larger construction. A punctuation mark or
  function may participate without reopening the closed word into a free
  character stream.
- A repeated completed gonol reuses its atomic identity when the governing
  construction says it is the same gonol; repeated occurrences remain
  separately addressable.
- Larger and smaller scales may couple directly when current UCNS architecture
  permits it. Do not invent mandatory adjacent-scale traversal.
- Do not materialize an all-pairs relationship graph as semantic authority.

## Function application

Public Gonol punctuation and symbol participants are functions only to the
extent authorized by current UCNS source and receipts.

- Require caller-supplied, occurrence-addressed application context.
- Never infer adjacency, precedence, grammatical role, or application scope
  from glyph shape or neighboring text.
- Bind function identity, result identity, ordered participants, occurrence
  addresses, source table, and construction version in the receipt.
- Replay against the same authoritative table and explicit plans.
- Do not promote structural survival into parsing, grammar, semantic utility,
  or universal function law.

## Morphology boundary

Affixiation is a scale-general pattern: participants couple, the relationship
enters the result, closure occurs, and the result can participate atomically at
another scale. Linguistic prefixes and suffixes are one instance, not the
definition of affixiation.

The complete English root, stem, affix, irregular-transformation, and family
law remains unresolved unless current UCNS evidence establishes otherwise.
Never invent a decomposition to complete a pipeline. Do not assume every word
is `root + affix`, that a lemma is a final root, or that one stemmer supplies
semantic authority.

## Evidence and replay

For a construction that claims completion:

1. Bind the exact source artifact, profile, code identity, options, and plans.
2. Admit the complete declared source, not an inspected prefix presented as a
   finished run.
3. Preflight required compute and storage before starting. Once an admitted
   healthy run begins, let it reach its natural terminal condition unless a
   genuine safety boundary or preregistered load-bearing stop condition fires.
4. Emit a deterministic semantic receipt separately from resource observations.
5. Independently reconstruct or replay the complete declared scope.
6. Compare byte-for-byte where the protocol requires exact identity.
7. Propagate failures and unresolved prerequisites without changing criteria
   after outcome inspection.

Passing fixtures proves only the fixtures. A historical receipt remains
historical evidence after its constructor is superseded; it is not a receipt
for the replacement construction.

## Required output

Report:

```text
source identity:
construction identity:
participants and scales:
intrinsic relations/functions:
closure boundary:
atomic promotion boundary:
receipt and replay status:
claims supported:
claims not supported:
hmmm:
next dependency-complete action:
```

Use `SURVIVED`, `FALSIFIED`, `BLOCKED`, `UNRESOLVED`, and `DEPRECATED` only
under the governing protocol. Do not translate `SURVIVED` into proved or
canonical.

## Anti-patterns: refuse these

- Reopening closed word gonols merely because a larger construction contains
  punctuation or morphology.
- Inferring function context, syntax, or precedence from adjacency.
- Treating a source word list as a semantic dictionary.
- Inventing morphology, a lexical family map, geometry, or measurement
  authority to fill an absent constructor.
- Promoting a sidecar relationship graph into intrinsic gonol semantics.
- Treating a partial corpus run as complete evidence.
- Adding arbitrary wall-clock limits to a healthy admitted computation.
- Restoring the deprecated omega/phi/psi cores, bone/flesh categories, fixed
  morphology weights, or `multiplyFuel`/carrier-LCM as the universal language
  law.
- Transferring UCNS construction survival into EDCM measurement validity,
  PTCNA efficacy, cognition claims, or selected universal canon.

## Minimal examples

Closed-word preservation:

```text
don't      = close(don + apostrophe-function + t)
don't cut. = compose(closed don't, closed cut, period-function, explicit plan)
```

The second construction may cite the first one's internal receipt. It does not
reopen `don't` into an unbounded character/function stream.

Honest incomplete continuation:

```text
full source unavailable -> BLOCKED or UNRESOLVED under the governing protocol
                         -> no replacement completion receipt
                         -> hmmm names the absent source or constructor
```

## hmmm

- the source-supported complete English morphology law;
- executable geometry for direct coupling across distant recursive scales;
- quantitative compression and reconstruction behavior after recursive gonols
  exist;
- the first complete recursive-gonol relation constructor beyond definition
  closure;
- which current UCNS composition mechanisms survive inside later gonol
  construction without semantic overpromotion.
