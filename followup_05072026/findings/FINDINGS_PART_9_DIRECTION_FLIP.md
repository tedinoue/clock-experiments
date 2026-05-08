# Part 9 — Direction-flip re-classification of all 640 Sonnet clock trials

**Date:** 2026-05-07 morning
**Method:** AI-judge subagent re-pass (8 parallel general-purpose subagents, one per condition) using extended 11-category set including direction-reversal failure modes.
**Spec:** `scratch/clocks_training/direction_flip_spec_v1.json`
**Outputs:** `scratch/clocks_training/judge_classified_v3_{S1,S2,S3a,S3b,S3c,S3d,hybrid,heavy_summary}.json`

## Categories

The 11-category set extended Part 6's 5-category scheme (`exact / within_5 / hand_swap / wrong_other / refused_or_ambiguous`) with six new direction-reversal categories:

- `hour_flip` (HF) — model reads hour hand at the opposite end (180° tip-flip)
- `minute_flip` (MF) — minute hand at opposite end
- `both_flip` (BF) — both hands at opposite ends
- `hand_swap_plus_hour_flip` (HS+HF) — swap composed with HF
- `hand_swap_plus_minute_flip` (HS+MF) — swap composed with MF
- `both_flip_plus_hand_swap` (BF+HS) — both flips composed with swap

Per-clock target tables (truth + 7 failure targets per clock) are in the spec file. Tolerance default ±5 min; clock_06 uses ±2 because flip targets cluster within 2 minutes of each other (6:00 / 6:02 / 6:30 / 6:32 and 12:00 / 12:02 / 12:30 / 12:32).

## Per-condition aggregates (n=80 trials each)

| Cond | exact | within_5 | HF | MF | HS | BF | HS+HF | HS+MF | BF+HS | wrong_other | refused |
|------|-------|----------|----|----|----|----|-------|-------|-------|-------------|---------|
| S1 (naive) | 13 | 7 | 0 | 0 | 2 | 7 | 0 | 0 | 0 | 41 | 10 |
| S2 (combined methodical) | 19 | 4 | 14 | 0 | 19 | 0 | 0 | 1 | 0 | 22 | 1 |
| S3a (methodology only) | 23 | 0 | 13 | 0 | 7 | 1 | 0 | 0 | 0 | 36 | 0 |
| S3b (feature-check) | 13 | 4 | 10 | 1 | 21 | 0 | 0 | 0 | 2 | 21 | 8 |
| S3c (anti-reasoning) | 18 | 12 | 0 | 0 | 0 | 1 | 0 | 0 | 10 | 39 | 0 |
| S3d (persona + stakes) | 19 | 0 | 4 | 0 | 18 | 1 | 0 | 0 | 0 | 38 | 0 |
| hybrid (trained variant) | 24 | 1 | 12 | 0 | 13 | 0 | 0 | 0 | 0 | 30 | 0 |
| heavy_summary (trained variant) | 34 | 0 | 7 | 0 | 11 | 0 | 0 | 0 | 0 | 28 | 0 |

## Headline finding 1 — Internal-consistency rule strongly confirmed

Direction-flip errors that occur are almost exclusively the geometrically-consistent variant (HF). The geometrically-inconsistent variants (MF, BF, HS+MF, BF+HS) are extremely rare or attributable to artifacts.

**Counts of direction-flip variants across all 640 trials:**
- Geometrically consistent: HF = 60, HS+HF = 0
- Geometrically inconsistent: MF = 1, BF = 10, HS+MF = 1, BF+HS = 12

Of the 12 BF+HS hits, 10 are concentrated in S3c on clock_04 — and clock_04's BF+HS target happens to be "10:10" (the canonical watchmaker advertising pose). The judge flagged these as likely prior-driven defaulting rather than actual flip-and-swap operation. Setting that artifact aside, geometrically-inconsistent direction-flips total roughly 14 across all 640 trials, while geometrically-consistent direction-flips total 60.

**Interpretation:** when Sonnet flips the tip-end identification of a hand, it overwhelmingly does so in a way that produces a self-consistent clock reading (a real time 6 hours away from the truth). The model is *not* committing the secondary error of reporting a minute reading that contradicts where the hour hand sits. This is structural evidence that the model retains hour-position-vs-minute-reading coherence even when the encoder fails. The failure is encoder-side (wrong tip identification on a single hand), not procedural-side (failed consistency check).

## Headline finding 2 — Clock_06 reframe partially holds

Clock_06 (rainbow no-numerals, 6:30) was previously classified as "encoder floor — no prompting condition recovers." Under the direction-flip taxonomy:

| Condition | exact | within_5 | HF (12:30) | BF (12:00) | wrong_other |
|-----------|-------|----------|-----------|------------|-------------|
| S1 | 0 | 0 | 0 | 7 | 3 |
| S2 | 0 | 0 | 5 | 0 | 5 (mostly 11:30) |
| S3a | 0 | 0 | 3 | 0 | 7 (mostly 11:30) |
| S3b | 0 | 0 | 4 | 0 | 6 (mostly 10:30/11:30) |
| S3c | 0 | 0 | 0 | 1 | 9 (mostly 12:49) |
| S3d | 0 | 0 | 0 | 1 | 9 (mostly 11:30) |
| hybrid | 0 | 0 | 8 | 0 | 2 (11:30) |
| heavy_summary | 0 | 0 | 4 | 0 | 6 (10:30/11:30) |

What the data say:
- The "encoder floor" claim was based on 0/80 across all six original conditions reading clock_06 correctly. That part still stands — no prompt produces a correct read.
- But the failure mode is NOT pure perception failure. Across all conditions, **24 of 80 trials produced HF (12:30) reads** — clean direction-reversal. **8 of 80 produced BF (12:00) reads** — both-hands flipped. The model IS detecting the hands; it's mis-identifying which end is the tip.
- The remaining wrong_other reads cluster at "11:30" (most conditions) and "12:49" (S3c). "11:30" is hour-hand-read-as-11 + minute correct — adjacent to HF (12:30) but off by one numeral on the hour. "12:49" is closer to BF (12:00) but with a fractional-minute reading.
- Clock_06's failure is best described as "lower-half angle bias driving hour-hand tip-flip, with a tendency to round the flipped position to nearby numerals." Not "encoder cannot resolve."

**Implication for the paper:** the "encoder floor" framing for clock_06 should soften. Clock_03 (24-hour 7:50) remains the cleanest encoder-floor case — its failures are 10:15 / 22:15 / 10:35 reads that don't fit any flip target and reflect a systematic mis-anchoring on the inner ring.

## Headline finding 3 — Clock_02 hour_flip is condition-dependent

Clock_02 (Roman 3:25) modal "9:25" reads were flagged as the smoking-gun "scaffolding-broke-correct" pattern. Under direction-flip classification:

| Condition | exact | within_5 | HF (9:25) | HS (5:15) | wrong_other |
|-----------|-------|----------|-----------|-----------|-------------|
| S1 | 3 | 7 | 0 | 0 | 0 |
| S2 | 0 | 0 | 9 | 1 | 0 |
| S3a | 0 | 0 | 10 | 0 | 0 |
| S3b | 1 | 0 | 6 | 0 | 3 |
| S3c | 10 | 0 | 0 | 0 | 0 |
| S3d | 4 | 0 | 4 | 0 | 2 |
| hybrid | 1 | 0 | 0 | 7 | 2 |
| heavy_summary | 3 | 0 | 2 | 0 | 5 (all "2:25") |

What the data say:
- Under methodical conditions (S2, S3a), clock_02 is essentially 10/10 hour_flip — every failure is "9:25", a clean direction-reversal of the Roman numeral hour hand.
- Under hybrid, clock_02 fails as hand_swap (5:15) instead — the hybrid prompt eliminates the HF mode but introduces HS.
- **Heavy_summary's clock_02 was previously reported as "9:25 in 7/10 trials" (FINDINGS line 705).** The new judge says heavy_summary's clock_02 is 3 exact + 2 HF + 5 wrong_other (all "2:25"). The dominant failure under heavy_summary is "2:25" — an off-by-one hour misread (model reads hour hand at 2 instead of 3, possibly because hand hasn't crossed numeral 3 yet by 25 minutes' worth of advance), not direction-flip. **Prior FINDINGS overstated the HF rate for heavy_summary on clock_02.**

## Headline finding 4 — Hand-swap rates mostly hold from prior re-pass

Hand-swap counts under the new 11-category re-pass vs the prior 5-category pass:

| Condition | Prior HS | New HS | Change |
|-----------|----------|--------|--------|
| S1 | 2 | 2 | 0 |
| S2 | 13 | 19 | +6 |
| S3a | 6 | 7 | +1 |
| S3b | 21 | 21 | 0 |
| S3c | 0 | 0 | 0 |
| S3d | 15 | 18 | +3 |
| hybrid | 13 | 13 | 0 |
| heavy_summary | 11 | 11 | 0 |

Some prior wrong_other trials now resolve as HS (especially under S2 and S3d where the heavy methodical scaffolding was producing both HS and HF errors). The "hand_swap rate scales with prompt weight" finding still holds qualitatively, with the modal-prompt-weight conditions producing the most hand-swaps.

## Headline finding 5 — Direction-flip is a substantial new failure category

Total counts across all 640 trials:
- exact: 163
- within_5: 24
- hour_flip (HF): 60 — new
- hand_swap (HS): 91
- both_flip (BF): 10 — new
- minute_flip (MF): 1 — new (negligible)
- hand_swap_plus_hour_flip (HS+HF): 0 — new (negligible)
- hand_swap_plus_minute_flip (HS+MF): 1 — new (negligible)
- both_flip_plus_hand_swap (BF+HS): 12 — new (mostly likely-artifact)
- wrong_other: 255
- refused_or_ambiguous: 19

**Direction-flip variants together account for 84 trials** out of 640 (versus 91 hand_swap). HF alone is 60 trials, comparable in magnitude to hand-swap. **Direction-reversal is roughly as common as hand-identification swap as a failure mechanism on this dataset.** It was previously buried inside the "wrong_other" bucket.

## Methodological caveats

1. **Prior overlap.** Some failure-mode targets coincide with high-prior times (10:10, 12:00, 11:30). The judge flagged S3c clock_04's 10/10 BF+HS hits as suspicious — the model may be defaulting to "10:10" as a canonical pose rather than actually performing flip-and-swap. Targets that overlap common defaults should be marked "geometric-or-prior" rather than committing to one mechanism.

2. **Tolerance choice.** Clock_06 used ±2 min tolerance to keep its eight close-clustered targets distinguishable. Other clocks used ±5. This is intentional and matches the geometric structure (clock_06 has hand_swap target at 6:32 just 2 minutes from truth).

3. **Inter-judge consistency.** Eight different subagent instances did the classification, one per condition. Same model (Opus 4.7), same spec, same instructions, but minor inter-instance variation possible. For publication-grade tabulation a re-pass with one consistent judge instance over all 640 trials would be more rigorous.

4. **Clock_08 mirror.** Both truth interpretations (9:45 displayed-numerals and 2:15 mirror-convention) were tracked. In practice models almost always anchored on truth_a (9:45) — truth_b reads were rare across all conditions. If we want to make a stronger claim about mirror-convention, the data is sparse.

## Implications for the Part 2 paper

The current Part 2 draft (`salon/files/CLOCKS_PART_2_DRAFT_v2_05062026.md`) needs updates:

1. **Add direction-reversal as a fifth failure mode** (or restructure the four existing modes). The "gross hour-hand misreading" mode (currently #2 in the paper) is mostly hour_flip in the new taxonomy, with a smaller component of off-by-one rounding on flipped positions.

2. **Soften the "encoder floor on two clocks" claim.** Clock_03 remains a clean encoder-floor case. Clock_06 is partly direction-reversal and partly off-by-one-on-flipped-position. Reword to acknowledge clock_06's hands ARE detected — it's the tip-end identification that fails.

3. **Correct the heavy_summary clock_02 claim.** The prior "9:25 in seven trials out of ten" claim is wrong; heavy_summary's clock_02 is 3 exact + 2 HF + 5 "2:25" off-by-one. The dominant failure under heavy is the off-by-one hour misread, not direction-flip.

4. **Add internal-consistency framing as a structural insight.** Sonnet's flip errors are overwhelmingly geometrically valid (HF, not MF/BF), suggesting the model retains hour-position-vs-minute coherence even when the encoder mis-identifies tip ends. This is a separate cognitive layer from "encoder vs procedural" and worth surfacing.

5. **Rewrite the "two encoders" section to connect direction-flip-on-clocks with the perception-baseline `opposite` classifications on single-line stimuli.** They're the same mechanism upstream; the paper should make this explicit.
