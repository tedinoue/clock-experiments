# Half-Circle Scale Extrapolation Experiment — Ted's Hypothesis Confirmed

**Date:** 2026-05-07 ~14:50–15:25 ET
**Hypothesis (Ted):** *"With a shorter pointer, the tip will be further from the number. If you're scanning left-right, then the tip at 90 degrees will scan right to the '3' on the clock. No error. But what of a short hand pointing at 45 degrees? Might that read closer to 1? or 2?"*

The hypothesis: clock-reading errors come from short-pointer EXTRAPOLATION failures, not from anything specific to clocks. Test in an abstract setup: half-circle scale, letters A–S at 10° increments, three line lengths.

## Stimulus design

Stripped of all clock context. Half-circle on right side of canvas, pivot at left-center. Letters A through S at angles 0°, 10°, ..., 180° (clockwise from up). Light grey arc at the inner-tic ring. Black tic marks; black letters; black pointer line emanating from the pivot dot.

Three line-length conditions (lengths to the letter ring, not to the letter):
- **full:** tip reaches just inside the letter ring (215px from pivot)
- **three_quarter:** 3/4 of full (~161px)
- **half:** 1/2 of full (~108px)

37 angles (every 5° from 0° to 180°), 3 lengths, 5 trials per cell, 2 models = **1110 calls.**

Single-shot per call, R1 generic system prompt, models in thinking-ON mode (Sonnet `enabled` budget 6000; Opus `adaptive` effort high).

Prompt: *"This image shows a half-circle scale with letters A through S labeled at evenly-spaced positions around the curve. A black line emanates from the pivot dot. Which letter does the line point at? State your answer as a single letter (A through S) at the end of your response."*

## Headline results

| Condition | n | Correct | Within ±10° | Median \|err\|° | Mean \|err\|° | Max° |
|-----------|---|---------|-------------|----------------|---------------|------|
| **Sonnet full** | 185 | **173/185 (94%)** | 98% | 5.0 | 4.4 | 90 |
| Sonnet 3/4 | 185 | 87/185 (47%) | 65% | 10.0 | 13.1 | 90 |
| Sonnet 1/2 | 185 | 50/185 (27%) | 40% | 15.0 | 21.9 | 100 |
| **Opus full** | 185 | **185/185 (100%)** | **100%** | **0.0** | **2.4** | **5** |
| Opus 3/4 | 185 | 95/185 (51%) | 66% | 5.0 | 11.7 | 165 |
| Opus 1/2 | 185 | 98/185 (53%) | 70% | 5.0 | 12.0 | 180 |

(Correctness criterion: on-tic angles require exact letter; off-tic angles accept either of the two adjacent letters.)

## Eight load-bearing findings

### 1. Pointer length, not angle, is the dominant accuracy determinant
At full length both models read essentially perfectly. At 3/4 length, accuracy collapses to ~50%. At 1/2 length, Sonnet drops to 27% and even Opus stalls at 53%. **Same angles, same model, same prompt — only the pointer length changes — and accuracy drops by 40–67 percentage points.**

### 2. Opus full-length is essentially perfect
185/185 correct, 100% within ±10°, **maximum angular error 5°**. The architectural perception layer reads angles accurately when the pointer reaches the labels. Whatever bias drives shorter-pointer failures is NOT a fundamental angular-perception bias.

### 3. Sonnet shows monotonic degradation; Opus shows a floor at ~50% on short pointers
- Sonnet: 94% → 47% → 27% as length decreases.
- Opus: 100% → 51% → 53% (slight inversion at the bottom; effectively a floor).

Opus is more robust on the easy regime (full) and on the very short regime; Sonnet's degradation is sharper.

### 4. The opposite-end (180°) flip mechanism reappears at short lengths
Opus 1/2 max error = 180° (a full opposite-end flip). Opus 3/4 max = 165°. **The B1/B2 "wrong end of line" mechanism we documented this morning is now visible here in an abstract no-clock context — and it specifically triggers on short pointers.** The B1 lower-half failure zone may be a function of where short lines were drawn in B1 stimuli, not an intrinsic property of those angles.

### 5. Cardinal positions read robustly across lengths in some cases
90° (J, dead right) reads 5/5 in all three Sonnet length conditions. The horizontal-axis cardinal is the easiest. 0° (A, top) and 180° (S, bottom) degrade more. 90° benefits from being the cleanest axis.

### 6. Accuracy degrades NON-monotonically across angles within a length condition
At Sonnet 3/4, performance is patchy: 5/5 at 30°, 0/5 at 40°, 5/5 at 45°, 0/5 at 50°. The degradation isn't a smooth function of angle; it depends on where the truncated tip lands relative to which adjacent labels are visually salient. **This explains the apparent randomness of the clocks-task failures at the trial level.**

### 7. Errors of small magnitude dominate; large-magnitude errors are tail events
Median |error| at Sonnet 1/2 is 15° (1.5 letters off). Mean is 21.9° (skewed by tail). Most failures are off-by-1-or-2-letters; rare failures are full opposite-flips. The model isn't randomly guessing; it's making a biased extrapolation that lands close-but-wrong most of the time.

### 8. The three-level clocks evidence stack now reduces to a single mechanism
- B1 single-line failures (lower-half angles)
- Hour-only cardinal-attractor pull
- Two-hand simplest clock failures (forward-shift, hand-swap)
- Style-swap result (short-thick hand reads worse than long-thin)

All are consistent with a single architectural failure: **short-pointer extrapolation.** When the line tip is near the labels, the model reads accurately. When the tip is interior, the model has to mentally extend the line outward and frequently picks a slightly-wrong (or fully-opposite) target. Visual style, hand semantic, numeral labels, and clock context all matter only insofar as they affect the tip-to-label distance.

## Reframing the morning's findings

The morning's mechanistic story had multiple layers:
- B1 fail zone (210°–330°)
- Cardinal attractor (12/3/6/9)
- Visual-style effect (short-thick vs long-thin)
- Numerals not being attractors
- Anchor-attractor at 12

The half-circle experiment **collapses these into one mechanism.** The line tip's distance to the labels is the load-bearing variable:
- B1 lower-half failure zone: B1's lines may have been drawn shorter relative to the label ring than B1's safe-zone test angles. Or the lower-half ANGLES may have happened to land between labels in ways the upper-half didn't. The half-circle data suggests the bias isn't about the angles intrinsically.
- Cardinal attractor: the model's biased extrapolation tends to land at strong visual axes (horizontal, vertical) when forced to guess from a short pointer.
- Visual-style effect: long-thin hand's tip reaches the numeral ring; short-thick hand's tip is interior. Same mechanism.
- Numerals not attractors: confirmed. The mechanism operates on visual extrapolation, not on label salience.
- Anchor-attractor at 12: the 12 attracts because near-vertical short pointers are biased toward the nearest visual axis (the vertical axis = 12 or 6 depending on direction).

## Implications for the Part 2 paper

This is a substantial reframe. The paper's mechanistic story collapses to a single sentence:

> **"When the pointer's tip is at the label ring, vision-language models read angles accurately (Opus 100%, Sonnet 94% on a 19-letter scale). When the tip is interior, accuracy collapses by 40–70 percentage points, with rare full-opposite-end failures."**

The clocks task fails because:
1. Real clocks have a short-thick hour hand whose tip is well inside the numeral ring.
2. The model cannot reliably extrapolate the hour-hand direction outward to identify the hour.
3. This drives forward-shift (extrapolation lands at the wrong numeral), hand-swap (extrapolation ambiguity makes role assignment unreliable), and anchor-attractor (extrapolation defaults to nearest strong visual axis).

The paper should be substantially restructured around this finding. The half-circle experiment becomes the load-bearing mechanism demonstration; the clocks data becomes the applied-task case where the mechanism explains specific failure patterns.

**Falsifiable prediction:** a real-clock test with both hands DRAWN LONG (tips reaching the numeral ring) should dramatically reduce errors. A real-clock test with both hands DRAWN SHORT (tips interior) should produce the dialogic-teaching failures even on the easy stimuli (3:00, 9:00, etc.). This is the natural validation experiment.

## Open follow-ups
- Real-clock validation: render simplest clocks with both hands LONG, rerun R1-style first-attempt reads. If accuracy is 100% on cardinals + non-cardinals, the mechanism is confirmed.
- Same with both hands SHORT — should produce the failure pattern even on cardinals.
- Could also test the half-circle scale with even SHORTER pointers (1/4, 1/8) to chart the full degradation curve.
- Could test pointers with ARROWHEADS at the tip vs without — does an arrowhead help the model identify "this is the tip" and reduce extrapolation errors?

## Cost
1110 API calls (185 × 6 conditions). Sonnet ~$5–10, Opus ~$25–35. Total ~$30–45.
Cumulative clocks-arc spend: ~$50–65.

## Cross-references
- Style-swap experiments: scratch/clocks_training/STYLE_SWAP_FINDINGS_05072026.md
- Hour-only / minute-only experiments: scratch/clocks_training/HOUR_ONLY_FINDINGS_05072026.md
- B1 perception baseline correlation: scratch/clocks_training/PERCEPTION_BASELINE_CORRELATION_05072026.md
- Dialogic teaching rounds 1-3: scratch/clocks_training/sonnet_v2_round{1,2,3}/FINDINGS.md
- 640-trial direction-flip re-judge: scratch/clocks_training/FINDINGS_PART_9_DIRECTION_FLIP.md
