# Perception-Baseline ↔ Dialogic-Teaching Correlation

**Date:** 2026-05-07 ~08:25 ET
**Scope:** Cross-reference the B1/B2 single-line angle-perception failures (perception baseline, run_perception_baseline.py) against the first-attempt clock-reading failures observed in v2 dialogic teaching rounds 1-3.
**Hypothesis under test (Ted, 2026-05-07):** *"Errors we're seeing in clocks-reading correlate with the geometric failure modes already documented in the perception baseline."*

## Perception baseline failure map

**B1 (single black line, clean canvas, 12 angles, 3 trials each = 36 trials):**

| Angle | Truth numeral | B1 classifications |
|-------|---------------|---------------------|
| 0° | 12 | exact ×3 |
| 30° | 1 | exact ×3 |
| 60° | 2 | exact ×2, off_by_one ×1 |
| 90° | 3 | exact ×3 |
| 120° | 4 | exact ×3 |
| 150° | 5 | exact ×2, off_by_one ×1 |
| 180° | 6 | off_by_one ×2, exact ×1 (borderline; minor slips) |
| **210°** | **7** | **opposite ×2, off_by_more ×1 (all "wrong end of line")** |
| **240°** | **8** | **opposite ×3 (all wrong-end)** |
| 270° | 9 | exact ×3 |
| **300°** | **10** | **opposite ×2, off_by_more ×1 (all wrong-end)** |
| **330°** | **11** | **off_by_more ×2, opposite ×1 (all wrong-end)** |

**B2 (single line, cluttered with subdial-style background, same angles):** same pattern as B1 PLUS 270°/9 also fails (all 3 trials → "3" via opposite-flip). Clutter pushes 270° from safe to failure-zone.

**The B1 failure zone:** angles in the lower half of the dial — specifically 210°, 240°, 300°, 330° — read as their OPPOSITE numeral (truth N → reported N±6 mod 12). The model "tracks the wrong end of the line" per the judge's notes. Robust pattern: 11 of 12 failure-classified B1 trials are explicit "wrong-end" misreads.

The B1 safe zone: top half of the dial (12, 1, 2, 3, 4, 5) plus 9 (270°). The bottom-half angles 6 (180°) is borderline but mostly safe.

## Clock-reading angle decomposition

For an analog clock with hour H and minute M:
- minute hand angle = M × 6°
- hour hand angle = H × 30° + M × 0.5°

| Stimulus | Hour angle | Minute angle | Hour B1 zone | Minute B1 zone |
|----------|-----------|--------------|--------------|----------------|
| 3:00 | 90° | 0° | safe (=3) | safe (=12) |
| 9:00 | 270° | 0° | safe (=9, B1 clean; B2 fails) | safe (=12) |
| 1:15 | 37.5° | 90° | safe (between 1 and 2) | safe (=3) |
| 4:30 | 135° | 180° | safe (between 4 and 5) | borderline (180°) |
| **7:45** | **232.5°** | 270° | **FAILURE-ZONE (between 210=fail and 240=fail)** | safe (B1 clean) |
| **2:35** | 77.5° | **210°** | safe (between 2 and 3) | **FAILURE-ZONE (=7)** |
| **8:25** | **252.5°** | 150° | **FAILURE-ADJACENT (between 240=fail and 270=safe)** | safe (=5) |
| **5:50** | 175° | **300°** | safe (just before 6) | **FAILURE-ZONE (=10)** |

## Three-round first-attempt comparison vs B1 zone

| Stimulus | R1 | R2 | R3 | Hand in B1 failure zone | Correlation |
|----------|----|----|----|-------------------------|-------------|
| 3:00 | ✅ | ❌ swap (R2 only) | ✅ | none | clean: safe-zone stimulus → success (R2 break is heads-up artifact, not perceptual) |
| 9:00 | ✅ | ✅ | ✅ | none | clean: safe → success |
| 1:15 | ✅ | ✅ | ✅ | none | clean: safe → success |
| 4:30 | ✅ | ❌ back-shift | ❌ back-shift | none | **EXCEPTION**: safe-zone stimulus, but R2/R3 break it via intervention-induced backward-shift. Different mechanism. |
| 7:45 | ❌ fwd-shift | ✅ | ✅ | hour | matches: hour in failure zone → R1 fails. R2/R3 thinking+self-check compensates. |
| 2:35 | ❌ swap (7:15) | ❌ swap (7:15) | ❌ swap (7:15) | minute | **strong match**: minute in failure zone → ALL THREE rounds fail with identical wrong answer. |
| 8:25 | ❌ fwd-shift (9:25) | ❌ swap+shift | ❌ swap+shift | hour (failure-adjacent) | matches: hour at boundary → all three rounds fail. |
| 5:50 | ❌ swap | (not reached in R2/R3) | (not reached) | minute | matches: minute in failure zone → R1 fails via swap. |

**Net correlation:**
- 4 of 4 stimuli with at-least-one-hand-in-failure-zone failed in round 1: **100% predicted-fail rate.**
- 3 of 3 safe-zone stimuli succeeded in round 1: **100% predicted-success rate.**
- 4:30 broke under interventions in R2 and R3 — but via a mechanism that does NOT fit the B1 pattern (it's backward-shift on a safe-zone hand, not the B1 wrong-end mechanism).

**Ted's hypothesis is strongly supported for round 1 (no interventions): the clock-reading failures cluster precisely on stimuli where at least one hand falls in the B1 perceptual failure zone.** The architectural perceptual bias documented in B1 — "wrong end" misreads on lower-half angles 210°/240°/300°/330° — predicts which clock stimuli will fail.

## How the B1 mechanism manifests differently in clocks

The B1 task is single-line angle judgment. The clock task is two-hand angle PLUS hand-role identification PLUS time arithmetic. The B1 "wrong end" failure can manifest in clocks via three pathways:

### Pathway A: Forward-shift on the failure-zone hand
When the model's perception of a failure-zone angle is unstable, it tends to drift toward the nearest perceptually-stable angle. At 232.5° (truth 7:45 hour) the model reads "between 8 and 9 closer to 9" (drift toward 270°/9, which is B1-safe). At 252.5° (truth 8:25 hour) the model reads "just past 9, between 9 and 10" (drift toward 270°/9 same way).

This is the **forward-shift hour reading** documented in FINDINGS_PART_9. The B1 baseline already shows the upstream cause: the model can't reliably track the actual angular position when the hand is in the lower-left quadrant.

### Pathway B: Hand-swap when minute hand is in the failure zone
When the LONG (minute) hand falls in the failure zone (e.g., minute at 7 = 210° on a 2:35 clock), the model's perception of the long hand becomes unreliable. The angle CAN still be reported correctly ("longer hand toward 7"), but the LENGTH judgment ("which hand is longer?") becomes unstable. The model often misassigns roles, reading the long hand as short and vice versa. This produces the hand-swap pattern: 2:35 → 7:15 (minute "at 3 = 15 min" + hour "at 7 = 7 o'clock" via inverted role assignment).

This is the **hand-swap** documented in FINDINGS_PART_9. The B1 baseline shows the upstream cause: lower-half angles destabilize perception generally, including the geometric features (length, tip identification) that role assignment depends on.

### Pathway C: Compounded swap-plus-shift on stimuli where both pathways apply
Round 2/3 8:25: minute at 150° (safe) but hour at 252.5° (failure-adjacent). The model swaps roles AND forward-shifts the perceived hour position, producing 4:45 → after correction 9:25. Two upstream perceptual instabilities compounding in one stimulus.

## What 4:30's failure under intervention reveals (the exception)

4:30 has both hands in the B1 safe zone. Round 1 read it correctly. Rounds 2 and 3 (with thinking-on + self-check system prompt) both produced the same wrong answer (3:30, hour hand "halfway between 3 and 4").

**This is positive evidence that the round 2/3 4:30 break is a separate mechanism, not the B1 perceptual bias.** Likely candidates:
- Thinking-on may bias the model toward more elaborate hour-position reasoning, which can over-shift in either direction on perfectly-symmetric half-hour positions.
- The self-check system prompt may push the model to revise an initially-correct percept toward an "alternative interpretation" that turns out to be backward.
- The half-hour position itself (hour hand exactly at midpoint between two numerals) may be intrinsically ambiguous in a way that interventions exacerbate.

This break is **not** the same architectural failure documented in B1. It's an intervention-induced failure that B1 wouldn't predict.

## Implications for the Part 2 paper

This correlation analysis adds a load-bearing finding:

**The B1 single-line perception baseline predicts which clock-reading stimuli will fail.** Hands in the 210°-330° lower-half angular zone are perceptually unreliable in B1; clock stimuli where one or both hands fall in this zone fail dialogic teaching at 100% rate (round 1, 4 of 4) while safe-zone stimuli succeed at 100% rate (3 of 3). The B1 "wrong-end" mechanism manifests in clock-reading via three pathways (forward-shift on failure-zone hour hand, hand-swap when minute hand is in failure zone, or compounded swap-plus-shift).

This connects the perception baseline (a methodological setup paper might position as a separate study) directly to the FINDINGS_PART_9 failure taxonomy (forward-shift, hand-swap, internal-consistency rule). They are the same architectural perceptual bias surfacing in different task structures.

**Recommended additions to CLOCKS_PART_2_DRAFT_v2_05062026.md:**

- New section connecting the perception baseline to the clock-reading failures via the B1 zone analysis above. Include the per-stimulus angle/zone table and the three pathways.
- This is now finding 9 in the paper's revision queue: *"The clock-reading failures are predictable from the single-line perception baseline. Hands in the lower-half angular zone (210°-330°) where B1 produces 'wrong-end' misreads are the same hands that drive forward-shift, hand-swap, and compounded failures in clock reading. The architectural perceptual bias is one bias, not multiple."*
- The 4:30 intervention-induced break stays as finding 8 (intervention can hurt) — distinct mechanism, important contrast case showing that not all clocks failures reduce to B1.

This sharpens the paper's mechanistic story considerably. The perception baseline is no longer a separate setup that establishes "the model has trouble with low-angles" — it's the upstream measure that PREDICTS the clock-reading failures.

## Caveats

- B1 was generated with thinking OFF (per the methodological flag from earlier today). Thinking-on B1 trials might tighten or loosen the failure zone. A pre-ship subset re-run would address this.
- B1 has 3 trials per angle. Sample size is small; the failure-zone designation is pattern-strong but quantitatively imprecise.
- B2 (cluttered) extends the failure zone to include 270°. The 640-trial test set uses cluttered/subdialed clocks, so B2 may be the more relevant baseline for the test set than B1 alone.

## Population-level verification (640-trial test set) — the prediction is partial, not total

Per Ted's request after the simplest-clock analysis: cross-tabulated the 640 trials by per-clock B1-zone classification.

**Per-clock test-set decomposition** (hour and minute angles by truth time, B1-zone of nearest numeral, n=80 per clock):

| Clock | Truth | Hour zone | Minute zone | Style | Exact rate |
|-------|-------|-----------|-------------|-------|-----------|
| clock_01 | 10:10 | FAIL (10, 305°) | safe (2, 60°) | chronograph arabic | **68/80 (85.0%)** |
| clock_02 | 3:25 | safe (3, 102°) | safe (5, 150°) | Roman + day window | 22/80 (27.5%) |
| clock_03 | 7:50 | FAIL (8, 235°) | FAIL (10, 300°) | 24-hour double-ring | **0/80 (0.0%)** |
| clock_04 | 8:20 | FAIL (8, 250°) | safe (4, 120°) | naked hands (no numerals) | 17/80 (21.2%) |
| clock_05 | 4:15 | safe (4, 127°) | safe (3, 90°) | thin minimal | 28/80 (35.0%) |
| clock_06 | 6:30 | borderline (6, 195°) | borderline (6, 180°) | rainbow | **0/80 (0.0%)** |
| clock_07 | 11:55 | safe (12, 357°) | FAIL (11, 330°) | dark simple | 1/80 (1.2%) |
| clock_08 | 9:45 | FAIL (10, 292°) | safe (9, 270°) | mirrored | 26/80 (32.5%) |

**Aggregate by B1-zone status:**

| Zone status | Clocks | n | Exact | HF | HS |
|-------------|--------|---|-------|----|----|
| both_safe | 02, 05 | 160 | 50 (31.2%) | 31 (19.4%) | 38 (23.8%) |
| both_borderline | 06 | 80 | 0 (0.0%) | 24 (30.0%) | 0 (0.0%) |
| hour-only_FAIL | 01, 04, 08 | 240 | 111 (46.2%) | 5 (2.1%) | 19 (7.9%) |
| minute-only_FAIL | 07 | 80 | 1 (1.2%) | 0 (0.0%) | 19 (23.8%) |
| BOTH_FAIL | 03 | 80 | 0 (0.0%) | 0 (0.0%) | 15 (18.8%) |

**The clean R1 simplest-clock prediction does NOT translate cleanly to the test set.** The test-set picture has at least three additional factors that interact with B1:

### 1. Canonical-pose training prior dominates B1 on clock_01 (10:10)

clock_01 has its hour hand at 305° — squarely in the B1 failure zone (10 numeral). B1 alone predicts low exact rate. **Actual: 85.0% exact across 80 trials.** The "watchmaker pose" 10:10 is overwhelmingly common in advertising, training images, and stock photos. The model has memorized this specific pose strongly enough to override the angular-failure-zone bias.

When clock_01 *does* fail, the wrong answer is the canonical hand-swap target: 8 of 10 wrong reads are "2:50" (hour↔minute swap of 10:10). And condition S3d specifically breaks the prior — 7/10 of S3d clock_01 trials produce 2:50 hand-swaps. The pose effect is condition-modifiable.

**Implication:** training-data priors are an *additional* architectural factor that can override or compound with B1.

### 2. Visual clutter reduces accuracy independently of angular zone

clock_02 (3:25, both safe in B1) has Roman numerals plus a day window. **Exact rate: 27.5%** — moderate failure despite both hands in the safe zone. clock_05 (4:15, both safe, thin minimal) also gets 35%. The simplest-clock R1 saw 100% on safe-zone stimuli; the test-set safe-zone clocks are 27%–35%. Visual clutter (Roman characters, subdials, date windows) reduces accuracy across the board, including on B1-safe stimuli.

### 3. Anchor-attractor pose effect dominates clock_06 (6:30, both borderline)

clock_06 has both hands near vertical (hour at 195°, minute at 180°). B1 calls 180° borderline-safe. **Actual: 0/80 exact, 24/80 hour-flip to "12:30," 8/80 both-flip to "12:00."** The model defaults to canonical clock poses (12:30, 12:00) when both hands are close to vertical. This is a separate mechanism from B1's wrong-end failure.

### 4. clock_07 (11:55) confirms B1 prediction strongly

clock_07 minute hand at 330° (B1 failure zone). **Actual: 1/80 exact.** Strong support for B1 prediction on this clock.

### 5. clock_03 (7:50, BOTH_FAIL) confirms B1 prediction strongly

Both hands in B1 failure zone. **Actual: 0/80 exact.** Strong support.

## Honest revised framing

**The B1 single-line perception baseline is ONE of multiple architectural factors driving clock-reading failures. It is not a complete predictor at the population level.**

B1 captures one real architectural perceptual bias — the model's inability to reliably track hand-position direction in the lower-half angular zone (210°-330°). This bias is the upstream mechanism for forward-shift and hand-swap failures on stimuli where it dominates. **The simplest-clock R1 result (4/4 failure-zone fail, 3/3 safe-zone succeed) is the cleanest case where B1 dominates because confounds are stripped away.**

But the 640-trial test set has additional architectural factors:
1. **Training-data priors** (canonical 10:10, 12:00, 12:30 poses) can override B1 when stimulus geometry matches a memorized pattern.
2. **Visual clutter** (Roman numerals, subdials, date windows) reduces accuracy across the board.
3. **Anchor-attractor poses** pull readings toward 12:00 / 12:30 when hands are near vertical.

These are *additional* mechanisms, not refutations of B1. They MODIFY the prediction.

## Implications for the Part 2 paper (revised)

The original "B1 predicts everything" framing was overclaim based on simplest-clock R1 alone. The honest framing for the paper:

- **B1 establishes that the perceptual bias exists architecturally** (single-line baseline, clean stimuli, isolated angular-position task).
- **Simplest-clock R1 confirms B1's predictive validity in isolation** (when other confounds are absent, B1 perfectly predicts which clock stimuli fail).
- **The 640-trial test set shows B1 INTERACTS with other architectural factors:** training-data priors (10:10 canonical-pose advantage), visual clutter (Roman numerals reduce accuracy on safe-zone clocks), anchor-attractors (12:30 / 12:00 default for vertical hands).
- **Each of these is a separable architectural pattern.** The model has multiple failure mechanisms, B1 is one well-isolated mechanism, and the test-set complexity shows them interacting.

This is a *better* story than "B1 explains everything" because it shows the failure modes have multiple architectural origins, and the simplest-clock baseline is the clean isolation case.

**Updated Part 2 paper queue (revised finding 9):** The B1 perception baseline is one of multiple architectural factors driving clock-reading failures. Simplest-clock R1 confirms B1's predictive validity in isolation (4/4 fail, 3/3 succeed). The 640-trial test set demonstrates B1 interacting with: (a) training-data priors (clock_01 10:10 canonical pose: 85% exact despite B1-failure-zone hour); (b) visual clutter (clock_02 Roman+date 27.5% exact despite both-safe); (c) anchor-attractors (clock_06 6:30 both borderline → 0/80 exact, 24/80 default to 12:30). **Restructure to present B1 as the upstream isolated measure and the 640-trial test set as the interactive picture.** Don't overclaim B1 as universal predictor.

## Cross-references
- Round 1 findings: scratch/clocks_training/sonnet_v2_round1/FINDINGS.md, memory #557
- Round 2 findings: scratch/clocks_training/sonnet_v2_round2/FINDINGS.md, memory #564
- Round 3 findings: scratch/clocks_training/sonnet_v2_round3/FINDINGS.md, memory #565
- 640-trial direction-flip re-judge: scratch/clocks_training/FINDINGS_PART_9_DIRECTION_FLIP.md, memory #554
- Perception baseline classifications: scratch/clocks_training/perception_baseline/judge_classified.json
- Per-condition × per-clock decomposition (this analysis): generated 2026-05-07 ~08:50 ET via inline Python; raw data in judge_classified_v3_*.json files

## Cross-references
- Round 1 findings: scratch/clocks_training/sonnet_v2_round1/FINDINGS.md, memory #557
- Round 2 findings: scratch/clocks_training/sonnet_v2_round2/FINDINGS.md, memory #564
- Round 3 findings: scratch/clocks_training/sonnet_v2_round3/FINDINGS.md, memory #565
- 640-trial direction-flip re-judge: scratch/clocks_training/FINDINGS_PART_9_DIRECTION_FLIP.md, memory #554
- Perception baseline classifications: scratch/clocks_training/perception_baseline/judge_classified.json
