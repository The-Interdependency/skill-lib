---
name: information-design
description: Evidence-grounded information-design and color-signaling workflow. Load when creating or reviewing infographics, study materials, explanatory diagrams, dashboards, interfaces, visual knowledge maps, or other information surfaces where color, salience, grouping, contrast, or multimodal signaling can influence attention, comprehension, memory, decision-making, or accessibility. Do not load for purely decorative art direction with no information-bearing visual structure.
---

# information-design — make color carry structure, not folklore

Use this skill to turn evidence about human perception, attention, learning, and accessibility into a reproducible visual grammar.

## Core contract

1. **Color encodes structure; it does not substitute for structure.** Hue may signal component family, modality, evidence state, or another declared dimension, but never several independent dimensions at once.
2. **No universal hue psychology.** Do not claim that red inherently impairs reasoning, blue creates creativity, green improves learning, or similar fixed effects. Treat hue associations as context-dependent priors.
3. **Salience is relational.** A color is attention-grabbing because it differs from its surround and competes with other signals, not because the hue is intrinsically dominant.
4. **Use redundant channels for meaning.** If color communicates state, repeat that meaning with at least one of: explicit label, shape, line style, pattern, icon, enclosure, or position.
5. **Luminance and contrast are load-bearing.** Critical text, boundaries, and graph elements must remain legible when hue discrimination is weak.
6. **Stable signaling supports learning.** Reuse the same visual mapping for the same meaning across a family of documents so color can function as an organizational and retrieval cue.
7. **Exact meaning stays textual.** Color can accelerate selection and grouping; labels, numbers, provenance, uncertainty, and status carry the exact claim.

## Evidence boundary

The strongest practical evidence supports signaling and cueing: selective, meaningful visual cues can improve retention and transfer by directing attention and clarifying relations. This does **not** imply that a particular hue independently improves intelligence, memory, or creativity.

Use `references/evidence.md` for the evidence summary and source provenance. The research basis is informative doctrine, not project-specific theorem status.

## Shared visual grammar

The machine-readable defaults live in `visual-grammar.json`.

### Encoding dimensions

| Channel | Preferred meaning |
|---|---|
| Hue | One categorical family or one semantic dimension |
| Lightness | Emphasis or ordered magnitude |
| Shape | State class / category redundancy |
| Position | Structural layer or reading order |
| Line direction | Processing, dependency, causal, or temporal flow |
| Line style | Current / provisional / historical / unavailable |
| Border style/count | Authority or selection boundary |
| Text label | Exact semantic meaning |
| Pattern | Color-independent redundancy |

Do not encode two independent variables with hue alone.

### Default categorical colors

Use these as defaults, not immutable branding:

- blue `#0072B2` — stable structural or informational family
- bluish green `#009E73` — supported/continuous family when paired with non-color state markers
- orange `#E69F00` — candidate, transformation, routing, or active transition
- vermillion `#D55E00` — diagnostic tension, contradiction, interruption, or error boundary
- sky blue `#56B4E9` — secondary information channel
- reddish purple `#CC79A7` — meta-level, recursive, semantic, or transformation family
- yellow `#F0E442` — localized highlight/unresolved marker with dark text and border
- charcoal `#111827` — primary ink / authoritative outline
- provenance gray `#6B7280` — historical or de-emphasized provenance, subject to contrast

Project branding may override hue choices, but not contrast, redundancy, or semantic-audit requirements.

## Workflow

### 1. Declare the message

Write one sentence describing what the reader should understand or decide after viewing the artifact. If the message is not clear, do not assign colors yet.

### 2. Declare semantic dimensions

List every variable the visual needs to encode, such as:

- component family
- evidence state
- modality
- recursion depth
- authority/provenance
- uncertainty
- temporal status
- magnitude

Assign each variable to a visual channel. Hue gets at most one independent semantic dimension within a local visual field.

### 3. Establish the neutral substrate

Use a high-contrast neutral background and ink before adding categorical colors. Most content should remain neutral or low-chroma so accents retain signaling power.

### 4. Allocate a salience budget

Reserve the strongest contrast/saturation for the information that deserves first attention.

- one primary accent path is preferable to many competing accents
- decorative accents must never outrank evidence/status distinctions
- use intense warning colors locally, not as broad ambient decoration

### 5. Add redundant state markers

Every information-bearing color state needs a non-color cue. Recommended defaults:

| State | Color | Redundancy |
|---|---|---|
| supported | `#009E73` | solid circle + `SUPPORTED` |
| falsified | `#D55E00` | octagon/cross + `FALSIFIED` |
| errored | `#CC79A7` | diamond/zigzag + `ERROR` |
| unavailable / NA | `#F0E442` | hollow square/dotted line + `NA` |
| historical provenance | `#6B7280` | dashed enclosure + `HISTORICAL` |
| current maintained authority | `#0072B2` | double border + `CURRENT` |

These are communication defaults. They do not transfer epistemic authority between repositories or convert evidence into canon.

### 6. Check contrast

Minimum targets:

- ordinary text: `4.5:1`
- large text: `3:1`
- essential graphical objects and state boundaries: `3:1`

Prefer stronger contrast when labels are small, thin, compressed, displayed outdoors, or expected to be viewed on low-quality screens.

Use `python information-design/audit.py <manifest.json>` for deterministic checks of declared text/non-text contrast and color-independent state redundancy.

### 7. Run the four publication gates

1. **Grayscale gate** — remove hue mentally or with a renderer; all important relations and states remain identifiable.
2. **Color-vision gate** — inspect under protan, deutan, and tritan simulation when tooling is available; no critical distinction depends on hue alone.
3. **Contrast gate** — automated manifest audit passes applicable thresholds.
4. **Semantic gate** — every hue has one declared role in context, and every claim is visibly marked as observed, measured, inferred, supported, falsified, provisional, historical, unavailable, or otherwise appropriate.

A deterministic checker may support gates 1–3 indirectly, but it must not claim to reproduce a human perceptual review.

### 8. Preserve a nonvisual representation

For publication-capable outputs, provide alt text or structured metadata that states:

- the main message
- important entities
- important relations
- reading/flow direction
- status and uncertainty
- any quantitative values needed to understand the conclusion

## Output shape

When this skill is active, produce or request a compact design manifest with:

```json
{
  "message": "one-sentence reader takeaway",
  "semantic_dimensions": {"component_family": "hue", "evidence_state": "shape+label"},
  "text_pairs": [{"foreground": "#FFFFFF", "background": "#0B1020", "size": "normal"}],
  "nontext_pairs": [{"foreground": "#0072B2", "background": "#F7F9FC"}],
  "states": [{"name": "supported", "color": "#009E73", "redundancy": ["label", "shape"]}],
  "manual_gates": {"grayscale": "pass", "cvd": "pass", "semantic": "pass"},
  "hmmm": []
}
```

The artifact and manifest should agree. A manifest is not evidence that an image passed a human review unless the review was actually performed.

## Validation

Run, where applicable:

```bash
python information-design/audit.py information-design/examples/design-manifest.json
python -m unittest tests.test_information_design
python tools/check_skill_compliance.py
python tools/check_skill_lib_drift.py
python tools/build_codex_plugin_skills.py --check
```

Success means:

- no required information state is color-only
- declared contrast pairs meet their threshold
- semantic dimensions have explicit visual channels
- manual publication gates are visible rather than silently assumed
- project-specific canon/provenance boundaries remain intact

## Anti-patterns

- Rainbow decoration where every node competes for attention.
- Reusing one hue to mean both component identity and evidence status.
- White or light text on yellow/orange fills without checking contrast.
- Thin isoluminant colored lines as the only boundary between important regions.
- Treating `NA` as zero or using a neutral color to imply neutrality when the datum is unavailable.
- Coloring recursion depth progressively redder unless greater diagnostic severity is actually being encoded.
- Letting risk-matrix color bands replace the underlying number or threshold definition.
- Calling a palette "colorblind-safe" and assuming that means its text contrast also passes WCAG.
- Claiming automated contrast checks prove comprehension, memory, or emotional effect.

## Non-triggers

Do not load this skill for:

- purely decorative image generation with no information-bearing color semantics
- ordinary prose formatting with no visual information architecture
- scientific colorimetry calculations where the task is measurement rather than communication design

For statistical charts, load `data-visualization` as well. For cross-repository authority/status diagrams, also load `interdependent-work-graph` and preserve repo-local authority.

## Maintenance

- `visual-grammar.json` is the machine-readable default grammar.
- `audit.py` must remain pure stdlib unless a dependency is explicitly justified.
- Update `references/evidence.md` when the evidence base materially changes; distinguish replication/meta-analysis from single-study findings.
- Do not silently modify imported `data-visualization` doctrine; delegate organization-specific information-design semantics here.

hmmm
- Automated simulation of protan/deutan/tritan perception is intentionally not claimed by the stdlib audit; image-level perceptual simulation remains a separate renderer/tool concern.
- Exact project brand palettes may override the defaults while preserving the grammar and gates.
- Whether image-generation prompts should emit a sidecar design manifest automatically is unresolved.
- A warning color that screams louder than the warning itself has become performance art.
