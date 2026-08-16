---
name: meta
description: METAPAT consultation router for The Interdependency. Load this when deciding which distinctions, relations, boundaries, transformations, scales, or cross-domain correspondences should organize downstream work; when the-interdependency skill's METAPAT consultation gate triggers; when an unresolved conceptual choice would constrain architecture, semantics, measurement, ontology, or later claims; or when explicitly asked to consult, apply, or interpret current METAPAT. Do not load merely for routine implementation under already-fixed conceptual contracts.
---

# meta — consult current METAPAT

This skill does not contain METAPAT doctrine.

Its purpose is to recognize when METAPAT is required, retrieve the current source, and return the relevant conceptual boundary without creating a competing frozen copy inside `skill-lib`.

## Source of truth

Current `The-Interdependency/metapat` outranks this skill on every METAPAT claim.

When this skill loads, inspect the current repository state before reasoning from METAPAT. Start with the files relevant to the question, normally including:

- `AXIOMS.md` for root commitments;
- `POSTULATES.md` for revisable working commitments;
- `DOMAIN_RESTRAINT.md` for cross-domain transfer boundaries;
- `THEORIES.md`, `THEOREMS.md`, `CHAPTER_ZERO.md`, or implementation documents when directly relevant.

Do not substitute historical wording from this repository, memory, another repo, or an older METAPAT commit when current METAPAT is available.

## Consultation gate

Consult METAPAT when the work must decide **what relation, distinction, boundary, transformation, scale, or cross-domain correspondence should exist or matter** before downstream implementation can proceed.

Strong triggers:

- choosing or revising an architecture-level distinction;
- deciding whether a boundary deserves independent status;
- relating similarly shaped transformations across different domains;
- importing a domain term, formula, metaphor, ontology, or explanatory structure into another layer;
- deciding what remains invariant across scale or representation change;
- separating design choice, aesthetic choice, discovery heuristic, empirical claim, mathematical claim, and implementation dependency when that classification changes architecture;
- an unexplained but productive discovery path is being removed only because its mechanism is not yet known;
- two repositories disagree because they encode different conceptions of the same relation rather than because of an implementation defect;
- deciding whether a simpler independent recovery invalidates, merely verifies, or should replace a richer discovery path.

Do not consult METAPAT merely for:

- routine refactors under fixed contracts;
- dependency or runtime-version updates;
- deterministic ingestion or serialization;
- tests whose expected relation is already declared;
- formatting, packaging, CI, deployment, or syntax repair;
- independent recovery after the discovery result and comparison criterion are already frozen, unless the recovery exposes a new conceptual boundary.

## Workflow

1. State the conceptual question that triggered consultation in one sentence.
2. Read current METAPAT source relevant to that question.
3. Distinguish root axiom, postulate, theory, theorem, implementation, example, and `hmmm`; do not transfer status between them.
4. If crossing domains, state what relation or question-form transfers and what does not.
5. Apply only enough METAPAT to resolve the downstream choice. Do not turn consultation into compulsory theory expansion.
6. Return the decision boundary to the calling task, including any unresolved constraint that still matters.
7. Continue implementation locally once the conceptual relation is fixed.

## Discovery boundary

METAPAT consultation must not become a requirement that every exploratory architecture justify itself before discovery.

Interest may select exploration. Discovery may precede explanation. Freeze discoveries before independent recovery. A simpler recovery path tests a result; it does not automatically invalidate the richer path that discovered it.

Consultation is required when a conceptual commitment would constrain downstream work, not merely because an unusual or complex choice exists.

## Output

Keep consultation compact:

```text
question: <conceptual boundary>
METAPAT standing: <axiom | postulate | theory | theorem | implementation | hmmm>
relevant relation: <what current METAPAT contributes>
transfers: <what may guide this task>
does not transfer: <what remains domain/local>
downstream consequence: <what can now proceed>
hmmm: <remaining unresolved constraint>
```

## Validation

A valid consultation:

- cites or identifies current METAPAT source rather than remembered doctrine;
- does not promote domain-specific language into METAPAT root authority;
- does not transfer theorem/proof/empirical status across repositories or domains;
- resolves or isolates the conceptual choice that blocked downstream work;
- leaves routine implementation outside METAPAT once the boundary is fixed;
- preserves `hmmm` rather than inventing closure.

## Anti-patterns

- Duplicating METAPAT doctrine inside skill-lib.
- Consulting METAPAT for every implementation detail.
- Treating elegance, interest, similarity, or explanatory reach as evidence.
- Treating lack of explanation as evidence that an exploratory choice is invalid.
- Treating independent recovery as proof that the discovery architecture was unnecessary.
- Using a domain's vocabulary to redefine METAPAT because the analogy is convenient.
- Resolving a live conceptual disagreement by silently choosing the more familiar interpretation.

hmmm

The calling harness may not support automatic cross-repository retrieval. When current METAPAT cannot be read, report that consultation is required and preserve the unresolved boundary rather than falling back to this skill as theory authority.
