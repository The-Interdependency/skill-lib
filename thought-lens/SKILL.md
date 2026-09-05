---
name: thought-lens
description: Translate raw, context-heavy, recursive, fragmentary, coined, or private-language thought into audience-legible language without changing the underlying claim. Load this when a user says people do not understand what they mean; asks to make a thought understandable to strangers, the public, a specific audience, or a platform; supplies dense notes rather than finished prose; needs jargon or coined terms introduced only after their ordinary-language meaning lands; or wants multiple audience/surface renderings from one thought. Do not load merely to polish finished prose or to simplify an already-stable canonical document; use ordinary editing for the former and plain-lens for the latter.
---

# thought-lens — translate thought without flattening it

`thought-lens` sits between a person's internal context and another person's
available context.

Its job is not to make the source thinker sound simpler. Its job is to recover
what the thinker is actually asserting, preserve that structure, and render the
minimum context another person needs to recover the same claim.

The governing rule is:

```text
raw thought -> recover structure -> freeze claim kernel -> render for audience
            -> back-read -> compare -> deliver or hmmm
```

Never simplify directly from raw thought. Recover the claim first.

## When to load

Load when the input is any combination of:

- notes, fragments, shorthand, recursive sentences, partial equations, coined
  terms, compressed references, or private vocabulary;
- understandable to a context-rich collaborator or model but not to a
  context-light human reader;
- a thought that needs to become a conversation answer, public post, thread,
  article paragraph, formal explanation, academic framing, technical note, or
  other audience-specific rendering;
- a request to preserve the thought while changing only how much prerequisite
  context the reader must already possess.

A useful trigger sentence is: **"I know what I mean, but other people do not
have the context."**

## Do not load

Do not use `thought-lens` for:

- spelling, grammar, tone polishing, or stylistic rewriting where the claim is
  already explicit;
- translating an established dense canon/spec/document into companion views;
  use `plain-lens` for that downstream task;
- deciding whether a new technical term should become canonical; use
  `domain-claims` for lexical governance;
- compressing working context for another agent; use `char-compress`;
- inventing a stronger, cleaner, more persuasive claim than the source
  supports.

## Source of truth and authority

The user's supplied thought is the source of truth for what they are trying to
say. Existing canon, evidence, or repo sources may constrain it when the user is
explicitly referring to them, but the translator must not silently substitute a
better-known theory for the user's thought.

Treat the source as evidence about intended meaning, not automatically as
truth about the world. Preserve the difference between:

```text
definition
observation
interpretation
hypothesis
causal claim
normative claim
metaphor
analogy
prediction
established/source-backed claim
```

Translation may change vocabulary. It may not silently change claim type,
certainty, polarity, quantifier, causal force, actor, scope, order, exception,
or status.

## Required inputs

Minimum input:

```yaml
source: <raw thought>
```

Optional controls:

```yaml
audience: stranger | peer | domain expert | named audience | hmmm
surface: conversation | x | thread | linkedin | article | formal | academic | technical | other
budget: 15_seconds | 1_minute | full | characters/words supplied by user
goal: understand | respond | remember | inspect | act | ask_more
voice: preserve | neutral | specified by user
```

If the user supplies no audience, use **context-light adult stranger**.
If the user supplies no surface, return a compact general explanation.
If the user supplies no budget, make the first layer understandable in roughly
15 seconds and put depth behind it.

Do not make the user pre-structure the thought before translation. That is the
work this skill exists to do.

## Stage 1 — recover the thought map

Privately recover the structure before writing audience prose.

Use this internal shape:

```yaml
thought_map:
  subject: ...
  core_claims: [...]
  distinctions: [...]
  definitions: [...]
  relationships: [...]
  causal_claims: [...]
  evidence_or_examples: [...]
  implications: [...]
  qualifications: [...]
  coined_terms: [...]
  prerequisites: [...]
  rhetorical_material: [...]
  unresolved: [...]
```

Rules:

1. **Recover; do not improve.** Infer only what is necessary to connect explicit
   fragments. If two plausible structures remain, keep both under `unresolved`.
2. **Separate idea from wording.** A striking phrase may be rhetorical material,
   a definition, or both. Do not assume rhetoric is literal mechanism.
3. **Expose prerequisite context.** Record every earlier concept the source
   assumes the reader already knows.
4. **Do not force completeness.** Fragmentary thought may contain a real claim
   without containing a full theory.
5. **Unknown becomes `hmmm`.** Never close a gap because a smoother sentence
   would sound better.

The thought map is usually internal. Show it only when the user requests the
analysis, when the source has material ambiguity, or when fidelity cannot be
established without exposing the fork.

## Stage 2 — freeze the claim kernel

Create the smallest structure that all valid renderings must preserve.

```yaml
kernel:
  claim_type: ...
  must_preserve:
    - actor / object / relation / condition / consequence
    - negation, quantifier, modal force, order, exception, scope
  must_not_imply:
    - claims not licensed by the source
  strength: observed | possible | proposed | likely | asserted | defined | source-backed | hmmm
  dependencies:
    - prerequisite concept needed for full version
  unresolved:
    - ...
```

The kernel is a translation contract, not a summary.

A shorter output is valid only if the omitted material is either:

- not part of the kernel; or
- explicitly deferred behind an `if they ask` / deeper layer.

If removing a detail changes what could make the claim true or false, that
detail belongs in the kernel.

## Stage 3 — calculate the context gap

For each kernel element, ask:

```text
What must this audience already know to parse this?
What ordinary distinction can carry the same relation?
What example makes the relation visible without becoming fake evidence?
Which coined term is useful only after the meaning is available?
```

Classify prerequisite context:

- **required now** — without it, the first claim is misunderstood;
- **defer safely** — needed for mechanism or precision, not first-pass meaning;
- **domain-only** — useful only to expert readers;
- **unresolved** — mapping itself is uncertain; emit `hmmm`.

Translation reduces **context required from the reader**. It must not reduce the
source's operative content merely to make the sentence shorter.

## Stage 4 — render from the kernel, never from the raw source

Render in this order:

```text
ordinary distinction
-> concrete consequence or example when useful
-> coined/technical name only if it buys precision
-> mechanism / architecture
-> source or deeper treatment
```

Do not lead with an acronym or coined term when its plain referent can land
first.

A coined term should normally enter as:

```text
<plain meaning>. I call this <term>.
```

not:

```text
<term> is <another unexplained term> involving <another unexplained term>.
```

### Surface adapters

**Conversation** — answer the point first, then one layer of why.

**Short public post / X** — one claim per post. Lead with the usable
distinction. Technical names follow only when needed. Do not turn one thought
into a manifesto merely because more source context exists.

**Thread** — concrete hook -> distinction -> claim -> implication -> mechanism
or term -> deeper source -> `hmmm` when material.

**LinkedIn / professional** — claim -> practical consequence -> mechanism or
example -> source. Remove platform-performance filler.

**Academic** — state claim type and scope first; distinguish proposal from
result; define terms before relying on them; identify evidence and unresolved
bridges.

**Technical** — preserve exact operators, entities, interfaces, values,
dependencies, conditions, and status. Lower context debt by adding definitions,
not by deleting structure.

## Stage 5 — produce progressive output

Default human-facing output:

```text
UNDERSTAND THIS FIRST
<minimum context-independent statement>

SAY IT LIKE THIS
<audience/surface-ready rendering>

IF THEY ASK WHY
<one deeper layer, only when useful>

IF THEY WANT THE MODEL
<technical/structural layer, only when useful>

HMMM
<only unresolved constraints whose omission would mislead>
```

Do not print empty sections. `SAY IT LIKE THIS` is the primary artifact.

For machine/UI use, the equivalent object is:

```yaml
translation:
  understand_first: ...
  say_it_like_this: ...
  if_they_ask_why: ... | null
  if_they_want_the_model: ... | null
  terms_introduced: [...]
  hmmm: [...]
```

## Stage 6 — fidelity audit

Before delivery compare **source -> kernel -> rendering**.

Required checks:

```text
[ ] no kernel claim disappeared
[ ] no new substantive claim appeared
[ ] negation/polarity survived
[ ] quantifiers and scope survived
[ ] causal strength did not increase
[ ] uncertainty/status did not increase
[ ] actor and object did not swap
[ ] conditions/exceptions/order survived where operative
[ ] analogy is not presented as evidence
[ ] coined terms are defined before they carry argumentative weight
[ ] unresolved constraints remain visible as hmmm
```

If a rendering fails, regenerate from the kernel. Do not patch a bad rendering
by adding persuasive filler.

## Stage 7 — back-translation legibility test

Read the rendered text as though the raw source were unavailable and answer:

```yaml
back_translation:
  what_is_being_claimed: ...
  claim_type: ...
  strength: ...
  required_context_still_missing: [...]
```

Compare it to the kernel.

Pass when a context-naive reading recovers the kernel without acquiring a
material new claim.

If an actually separate model or human is available, use that as the better
legibility check. If the same model performs the check, label it a **self-check**
and do not call it evidence that humans will understand.

A readability score is not a substitute for this test. Short words can still
carry the wrong idea.

## Minimal example

Raw thought:

```text
A network gets called decentralized because there are many nodes, but if every
node must ask the same service who is allowed to speak, the authority is still
centralized. topology isn't authority.
```

Kernel:

```yaml
claim_type: distinction
must_preserve:
  - many execution nodes do not by themselves imply distributed authority
  - a shared permission authority can remain a central control point
  - topology and authority are distinct properties
must_not_imply:
  - that the network has only one physical node
  - that all centralized permission systems are necessarily bad
strength: asserted
```

Context-light rendering:

```text
A system can have thousands of independent machines and still have one gatekeeper.
Distribution of machines is not the same thing as distribution of authority.
```

Technical layer:

```text
Physical or computational topology and authorization topology are separate
properties. A network with many execution nodes remains authority-centralized
when a single service controls admission or permission.
```

The output uses different words while preserving the same falsifiable
distinction.

## Negative example

Source:

```text
The current implementation rejects unsigned requests.
```

Do **not** use thought recovery to turn this into a theory of trust, identity,
or security. The claim is already explicit. Ordinary editing or technical
explanation is sufficient.

## Failure modes / refusals

Reject or repair these transformations:

- **Jargon substitution** — replacing one private term with several unfamiliar
  public terms.
- **Flattening** — deleting conditions, exceptions, uncertainty, or interacting
  claims until only a slogan remains.
- **Persuasion drift** — changing `may` to `does`, `I suspect` to `is`, or
  proposal to fact because certainty reads more cleanly.
- **Mechanism invention** — supplying the missing causal bridge from general
  knowledge without marking it as an addition.
- **Analogy capture** — using a useful analogy and then accidentally reasoning
  as though the target literally has the analogy's properties.
- **Audience caricature** — assuming a general reader is stupid. Remove missing
  context, not intellectual content.
- **Voice erasure** — making every rendering sound like generic institutional
  prose when the source's cadence or directness can survive without increasing
  context debt.
- **Acronym-first output** — requiring the reader to join the private language
  before the public idea exists for them.
- **False legibility claim** — declaring that humans understand because the
  generating model understands its own output.

## Relation to neighboring skills

```text
raw thought
   |
   v
thought-lens        recover + freeze + translate
   |
   +--> public / conversational / academic / technical rendering
   |
   +--> stabilized document or canon candidate
            |
            v
        plain-lens   companion views of established dense source
```

Use `char-compress` when the target is agent-context size rather than human
legibility. Use `domain-claims` when a translated term is proposed for canonical
semantic authority.

## Validation

For each material translation, validation is the fidelity audit plus the
back-translation test.

For repository acceptance of this skill:

```bash
python tools/check_skill_compliance.py
python tools/check_skill_lib_drift.py
python tools/build_codex_plugin_skills.py --check
```

A repository check can prove packaging/registration consistency. It cannot
prove that a particular human audience understood a rendering. Field evidence
for that requires an external reader, restatement, question, click/action, or
other declared observation.

## hmmm

- Human understanding cannot be guaranteed from model self-evaluation. The
  back-translation pass is a guardrail; independent readers are stronger
  evidence.
- Audience models are approximations. A named audience may still vary widely in
  domain knowledge, literacy, language, culture, attention, and stakes.
- A future executable evaluator can compare kernels to independent
  back-translations across models/humans, but no such metric is claimed here.
- Sometimes the shortest route between two minds is a definition; sometimes it
  is a story; the compiler should know the difference before it buys a trumpet.
