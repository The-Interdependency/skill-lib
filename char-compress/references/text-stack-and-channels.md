# char-compress — Optional Text-Stack Notation & Channel Details

Companion reference for [`../SKILL.md`](../SKILL.md).

## Optional local text-stack ladders and `word_gonol` example

```text
tensors = characters
spaces = twists
words = character-gonols between twists
sentences = word-gonols
paragraphs = sentence-gonols
chapters = paragraph-gonols
volumes = chapter-gonols
```

Under this notation a meaningful space is recorded as a separator (`twist`),
and punctuation/breaks retain their source-specific attachment role. No geometric
strength, operation, or closure follows from a punctuation class alone.

Each higher object is a gonol whose vertices are lower objects:

```text
word vertex      = character tensor
sentence vertex  = word gonol
paragraph vertex = sentence gonol
chapter vertex   = paragraph gonol
volume vertex    = chapter gonol
```

A word such as `banana` is not merely reduced to `ban`. The first-cycle carrier
is `b, a, n`; repeated characters become recurrence data attached to the carrier
as weights and/or ordered spiral layers:

```yaml
word_gonol:
  surface: banana
  carrier_vertices:
    - char: b
      first_position: 1
      recurrence_positions: [1]
      weight: 1
    - char: a
      first_position: 2
      recurrence_positions: [2, 4, 6]
      weight: 3
    - char: n
      first_position: 3
      recurrence_positions: [3, 5]
      weight: 2
  twist_left: word_start
  twist_right: space
```

Compression across the text stack uses the same move at every scale:

```text
character recurrence inside word
word recurrence inside sentence
sentence recurrence inside paragraph
paragraph recurrence inside chapter
chapter recurrence inside volume
```


## Channels

### FLESH channel

Open-class or content-bearing units carried in full.

Examples:

```text
entities, values, named objects, filenames, repo names, URLs, decisions,
claims, constraints, promises, statuses, dates, quantities, secrets,
private-key material, carrier choices, canonical spellings, unresolved hmmm
```

Flesh is expensive and irreducible. It is not inventory-determined. A value or
named object dropped as connective prose is unrecoverable.

### FROZEN_BONE channel

Closed-class, operator-like, or short structural units that look cheap but are
not safely regenerable because they control meaning.

Examples:

```text
not, never, no, without, only, all, none, some, any, if, unless, except,
before, after, during, until, must, may, should, cannot, first, second, last,
minus, plus, equals, not-equals, greater-than, less-than, public, private,
secret, experimental, defended, implemented, test-backed
```

Frozen bones are carried explicitly. They are bone-shaped but flesh-critical.
Dropping them creates the exact failures this skill exists to prevent.

### REGENERABLE_BONE channel

Closed-class connective scaffold that grammar can usually restore.

Examples:

```text
articles, routine prepositions, ordinary conjunctions, filler connective
phrases, repeated explanatory scaffolding, prose padding around already-carried
facts
```

Regenerable bones are the compression target. They may be dropped in
context-compression mode or carried as fingerprints in structure-preserving
mode.

### TRANSFORM channel

Affixes and grammatical surface changes stored as root plus transform.

Examples:

```text
root=compress, transform=-ion
root=measure, transform=-ment
root=run, transform=-ning
root=build, transform=re-
root=valid, transform=in-
```

The root is flesh. The transform is cheap if the domain grammar is shared.
When a transform changes legal, safety, or theorem status, treat it as frozen.

### HMMM channel

Visible unresolved constraints.

Examples:

```text
unknown source, missing bridge, unverified claim, incomplete test, ambiguous
bone/flesh boundary, security uncertainty, domain grammar mismatch
```

`hmmm` is not deleted. It is carried as an operative object.

