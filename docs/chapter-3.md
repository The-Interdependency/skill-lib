# Chapter 3: Modules That Speak for Themselves

*Chapter 3 of the distributed Interdependency textbook. Chapter 0 lives in
`metapat/CHAPTER_ZERO.md`; Chapter 1 in `ucns/docs/chapter-1.md`; Chapter 2 in
`edcm/docs/chapter-2.md`. Each chapter is bound by the license and status
vocabulary of the repository that carries it; no theorem, proof, or empirical
status crosses a chapter boundary by citation.*

Chapter 2 established what it costs to measure honestly. This chapter asks a
question that comes before measurement: how does a body of code state facts
about itself in a way that can be measured at all?

The conventional answer — documentation — fails in a specific, mechanical way.
A document that describes code from the outside is a second system claiming to
mirror a first, with no law binding the two. Every edit to the code widens the
gap; no gate detects the widening; and the reader cannot tell a current claim
from a fossil. The failure is not laziness. It is architecture: the fact and
its description live in different places, so they drift.

The repair is to move the declaration into the module, beside the code that
makes it true, and to make a machine responsible for reconciling the two. That
repair is a convention called **msdmd** — Module Self-Declared Metadata in
Markdown — and this repository, `skill-lib`, is its canonical home.

## 3.1 The Block

The unit of self-declaration is a fenced comment block:

```python
# === <BLOCK_NAME> ===
# id: <unique_snake_case_id>
#   <field>: <value>
#   <field>: <value>
# === END <BLOCK_NAME> ===
```

Five properties carry the design.

First, the block is a *comment*. It costs nothing at runtime, requires no
import, and survives in any language — only the comment marker changes; the
fence text and field structure are identical everywhere.

Second, the block lives *in the module it describes*. The declaration and the
implementation travel together through every edit, move, and review. Distance
is what made documentation drift; adjacency is what makes declaration
checkable.

Third, every entry begins with a stable `id:` — unique within its block,
constant across refactors. Claims need addresses. Without stable identity, a
runner cannot say *which* declaration went stale, and accountability dissolves
into diffs.

Fourth, unknown fields are written `hmmm`, never guessed. A declaration
convention that punishes admitted ignorance teaches its authors to fabricate.
`hmmm` is a first-class value: an explicit boundary object marking the edge of
what the module's author actually knows.

Fifth, the parser is dumb on purpose. A parser is a pure function over file
text: it returns entries, concatenates matching blocks, and returns an empty
list where no block exists. It interprets nothing — semantics belong to the
executor consuming the entries. This division keeps the parsers small enough
to be copied verbatim into any project, with zero non-stdlib dependencies,
which is the only distribution model that survives contact with real repos.

## 3.2 The Visible Gap

The convention would be decoration without its enforcement half: the
**runner**. A runner walks a source tree, recomputes what each block claims,
and fails on drift. But its most important output is not the failure — it is
the *gap list*.

Reference behavior: the tree walk returns two sets, the annotated and the
unannotated, so coverage gaps stay observable. A runner that reports only on
files that opted in creates the same illusion Chapter 2 forbade — absence
presenting as success. `NA != 0` has a documentation form: *undeclared* is not
*verified*, and the runner must say so in every report.

This is the chapter's central claim: **a self-description system is only as
honest as its gap reporting.** Perfect declarations over a tenth of a tree,
silently, are worth less than rough declarations over all of it, loudly.

## 3.3 A Family of Declarations

One convention, many blocks. Each metadata-block skill in this library applies
the same fence to a different class of fact a module can own: what a module is
and promises before it is built (`MODULE_BUILD`); what behavior it is
obligated to exhibit and which tests witness that behavior (`CONTRACTS` /
`CHECKS`, reconciled against each other); where its documentation lives
(`DOCS`); what capabilities it exposes (`CAPABILITIES`); what it depends on
(`DEPENDENCIES`); who stewards it (`OWNERS`); which runtime risk boundaries it
touches (`BOUNDARIES`); its own composition ratios, sealed on the first and
last line of the file (`ratios:`); and what instructions it contributes to the
repository's language-model surface (`LLMS`).

The pattern generalizes because the obligations rhyme: a stable id, fields
recomputable from the source, a runner that fails on drift, a visible gap
list, and `hmmm` where the truth runs out. Source modules own their
obligations; test modules own their witnesses; the audit reconciles the two
lists — and the reconciliation, not either list alone, is the evidence.

Beside the metadata-block skills stand **procedural** skills: doctrines with
no block, defining agent behavior — how to distinguish source-backed canon
from proposal, how to compress context without dropping load-bearing
structure, how to onboard a newcomer without inventing org-level facts. They
are chapters of method rather than schemas of fact, and they obey the same
epistemics: state the doctrine, name the output shape, mark the unresolved.

## 3.4 Canonical Source and the Vendored Copy

Declarations drift within a file; skills drift *between repositories*. The
library's answer is a strict provenance discipline:

- this repository is the single canonical source;
- consuming repos vendor copies at a recorded path, citing the source commit;
- edits land here first and propagate outward, never the reverse;
- a repo-local copy is never the source of truth, however recently edited;
- a scheduled detector diffs every consumer against canon and reports drift.

The shape should be familiar by now. It is Chapter 2's authority rule
recurring one level up: an installed copy does not silently override canon,
and provenance is recorded rather than assumed. A vendored skill is a mirror —
evidence of what canon said at a commit — and a mirror that disagrees with its
source is a *finding*, not a fork.

## 3.5 The Library as Method

Read as a whole, this repository is the textbook's methodological chapter in
executable form. Chapter 0 gave the root vocabulary; Chapter 1 subtracted
false structure from a geometry; Chapter 2 sealed measurement against
inheritance. This chapter supplies the mechanism those disciplines run on in
practice: facts declared beside their implementations, machines that reconcile
claim with source, gaps that stay visible, unknowns that stay marked, and one
canonical home from which every copy descends and against which every copy is
judged.

None of it is clever. All of it is load-bearing. The skills exist so that a
hundred modules across a dozen repositories can each answer, mechanically and
currently, the question every reader of code eventually asks: *what do you
claim about yourself, and who checked?*

**hmmm — the mechanism ends at the repository boundary: propagation still
requires human review, commit, and pull-request work in each target repo, so
canon can be current while a consumer lags behind it legitimately; the
compression checker is deterministic fixture support, not the full compression
engine its doctrine derives from; and the runners verify declared facts
against source, not the wisdom of declaring them — a module can be perfectly
self-described and still wrong about everything that matters, which is why
this chapter is method, and the other chapters exist.**
