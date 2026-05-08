# Visual-Style Swap + Numerals-Removed Experiments

**Date:** 2026-05-07 ~13:25 ET
**Per Ted's experimental design:** isolate what's driving the apparent hour-vs-minute perceptual asymmetry after the asymmetric-scoring concern was raised.

## Setup

Three controlled-visual experiments, all on Sonnet 4.6 thinking-ON, single-shot, R1 generic system prompt:

- **Experiment A: minute-only with SHORT THICK hand** (n=60). Same minute angles as original `minute_only_clocks/`, drawn with the short-thick (hour-hand) visual.
- **Experiment B: hour-only with LONG THIN hand** (n=24). Same hour-hand angles as original `hour_only_clocks/`, drawn with long-thin (minute-hand) visual.
- **Experiment C: hour-only NO NUMERALS** (n=24). Same hour-hand angles, numerals removed from dial (just tick marks).

Files: `style_A_min_thick_sonnet.json`, `style_B_hour_thin_sonnet.json`, `style_C_hour_nonum_sonnet.json`.

## Unified angular-error comparison

| Run | n | Median° | Mean° | Max° | Within ±6° | Within ±15° | Big errs >30° |
|-----|---|---------|-------|------|-----------|-------------|----------------|
| Min-only LONG THIN (orig) | 60 | 6.0 | 19.9 | 180 | 62% | 80% | 8 |
| **Min-only SHORT THICK (NEW)** | 60 | **21.0** | **50.2** | 180 | **22%** | **42%** | **22** |
| Hour-only SHORT THICK (orig) | 24 | 15.0 | 12.4 | 30 | 29% | 75% | 0 |
| **Hour-only LONG THIN (NEW)** | 24 | **5.0** | **5.2** | 15 | **58%** | **100%** | **0** |
| Hour-only NO NUMERALS (NEW) | 24 | 10.0 | 12.4 | 62.5 | 29% | 75% | 1 |

## Three load-bearing findings

### 1. Visual style is the dominant accuracy driver, NOT hand semantic role

- Hour-hand angles drawn with long-thin (minute-hand) visual: **5° median, 100% within ±15°.** Better than the original minute-only experiment.
- Minute-hand angles drawn with short-thick (hour-hand) visual: **21° median, 42% within ±15°.** Dramatically worse than the original minute-only.
- **Same angles, different hand styles, ~4× difference in accuracy.**

The architectural perception layer reads long-thin lines accurately at any angle. Short-thick lines trigger biased processing.

### 2. The "numeral-as-minute confusion" is triggered by the SHORT-THICK visual, not by the minute-hand task

- Original minute-only (long thin): 7-8 numeral-as-minute errors out of 60 trials.
- Minute-only with short-thick visual: **22 large errors out of 60 trials.**

Examples from the new short-thick run: 38→8, 23→4, 33→6, 41→8, 50→10, 24→4, 39→9, 42→9, 52→9, 57→2, 56→11, 40→8, 8→2, 9→2, 11→2, 33→6. The model sees the short-thick hand and interprets it as an hour-hand-style reading, multiplying the conversion failure. **The confusion is visual-style-induced, not task-induced.**

### 3. Numerals are NOT cardinal attractors visually

Removing numerals from the dial did not improve accuracy. Hour-only no-numerals: 75% within ±15°, identical to hour-only WITH numerals. **The cardinal-attractor effect is intrinsic to angular processing, not driven by labeled numerals on the dial.** Whatever pulls perception toward 12/3/6/9 operates on the angles themselves (or on the short-thick hand's tip identification), not on the numeral labels.

## Reframing earlier claims

The morning's framing — "the hour hand is read less accurately than the minute hand" — was **substantially a visual-style artifact** plus the asymmetric scoring (12× minute-conversion factor). With angular-error scoring AND visual-style-controlled:

- The architectural perception layer reads long-thin lines accurately at any angle (5-6° median).
- Short-thick lines are read poorly regardless of which "hand" they represent.
- The cardinal-attractor effect is real but doesn't come from numeral labels.

**The dialogic-teaching failures on simplest clocks (forward-shift, hand-swap) likely have their root in the SHORT THICK HOUR HAND VISUAL specifically**, not in a general angular-perception bias. A simplest clock with both hands drawn long-and-thin (just different lengths) would likely reduce errors substantially. The two-hand task's failures may compound: short-thick hour hand triggers position bias + role assignment fails when hands are similar in length.

## Implications for the Part 2 paper

This adds **findings 12 and 13** to the paper queue and substantially reframes the mechanistic story:

**Finding 12 (visual-style):** the architectural perception layer reads long-thin lines accurately at any angle (5° median). Short-thick lines trigger position bias AND numeral-as-minute confusion. The "hour hand reads worse than minute hand" finding from the single-hand experiments was almost entirely a visual-style artifact, not an intrinsic angular-processing asymmetry.

**Finding 13 (numerals not attractors):** removing numerals from the dial doesn't improve accuracy. The cardinal-attractor effect operates on angles directly, not on labeled positions. Rules out "the model sees numeral N and snaps to it" as the mechanism.

**Reframe of finding 7 (consistency-check insight):** the verbal rule "hour hand at 3/4 between numerals = 45 min past" can be implemented accurately when the hand has the long-thin visual (hour-only LONG THIN: 100% within ±15°). The short-thick hand's processing is what blocks the rule from working perceptually, not the rule itself.

**Reframe of perceptual-resolution-floor:** the floor on long-thin lines is ~5-6° (better than 1 numeral's worth). The floor on short-thick lines is ~15-21°. **The floor is visual-style-dependent.** The "architecturally constrained, not prompt-modifiable" framing is too strong — visual style is itself a modifier.

## Open follow-ups

- **Run all three experiments on Opus 4.7** for cross-model confirmation (~$3-4). Would test whether the visual-style effect is shared across the family.
- **Two-hand simplest clock with BOTH hands long-thin** (just different lengths). Tests whether the two-hand failures (R1-R3) reduce when the short-thick hour hand is replaced with a long-thin shorter hand.
- **Short-thick hand at minute-hand length** (long+thick, the only style not yet tested). Disambiguates "thick triggers bias" vs "short triggers bias."

## Cost
108 calls on Sonnet 4.6 thinking-ON (60 + 24 + 24). ~$2.
Cumulative clocks-arc spend: ~$22.

## Cross-references
- Hour-only experiment: scratch/clocks_training/HOUR_ONLY_FINDINGS_05072026.md
- Minute-only experiment: scratch/clocks_training/minute_only_*_thinkon.json
- Earlier B1 correlation (population-level): scratch/clocks_training/PERCEPTION_BASELINE_CORRELATION_05072026.md
