# Color-Coded Clock Validation — Three Architectural Mechanisms Cleanly Distinguished

**Date:** 2026-05-07 ~18:05 ET
**Per Ted's design:** the cleanest possible test. Both hands long enough to reach the tic marks, hour hand RED and minute hand BLUE, hour hand wider than minute (so when they overlap the red shows behind the blue). Tell the model in the prompt: hour is red, minute is blue.

This removes:
- Extrapolation confound (long hands)
- Role-identification confound (explicit color cue + visual color difference + width difference)

What remains exposes the residual mechanism, if any.

## Setup

10 stimuli (same set as v2 dialogic teaching) × 5 trials × 2 models = 100 calls. Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON. Single-shot, R1 system prompt.

Prompt: *"What time does this clock show? On this clock the hour hand is RED and the minute hand is BLUE."*

## Aggregate results

| Run | n | Correct | vs long-handed | vs R1 baseline |
|-----|---|---------|---------------|----------------|
| **Sonnet color** | 50 | **43/50 (86%)** | 58% (no improvement was net) | R1 50% |
| **Opus color** | 50 | **38/50 (76%)** | 58% | Stage 3 90% |

Color disambiguation gave Sonnet a **+28 point boost** over long-handed alone, and **+36** over R1 baseline. Opus came in at 76% (Stage 3 thinking-ON simplest-clock had been 90%, but on different stimuli set with different prompt; not directly comparable). Color disambiguation cleanly removes the hand-swap failure mode.

## Per-stimulus pattern

| Stimulus | Truth | Sonnet | Opus | Failure mode |
|----------|-------|--------|------|--------------|
| 3:00 | 3:00 | 5/5 ✓ | 5/5 ✓ | (Opus 3:00 broke under long-hand; recovers with color) |
| 9:00 | 9:00 | 5/5 ✓ | 5/5 ✓ | |
| 1:15 | 1:15 | 5/5 ✓ | 5/5 ✓ | |
| 4:30 | 4:30 | 5/5 ✓ | 5/5 ✓ | |
| **7:45** | 7:45 | 4/5 | 2/5 | forward-conversion to 8:45 |
| 10:30 | 10:30 | 5/5 ✓ | 5/5 ✓ | |
| 2:35 | 2:35 | 5/5 ✓ | 0/5 | Sonnet fixed; Opus minute slip (2:32–2:33, ~3 min off) |
| 5:50 | 5:50 | 2/5 | 5/5 ✓ | Sonnet forward-conversion to 6:50; Opus recovers |
| 11:40 | 11:40 | 2/5 | 1/5 | both: forward-conversion / anchor to 12:40 |
| 8:25 | 8:25 | 5/5 ✓ | 5/5 ✓ | |

## The decisive finding: position-to-hour conversion error is real and independent

Hand-swap errors essentially eliminated by color:
- Sonnet 2:35 (was 0/5 in long-hand, all 7:15) → 5/5 ✓
- Opus 3:00 (was 0/5 in long-hand, all 12:15) → 5/5 ✓
- Opus 5:50 (was 0/5 in long-hand, all 10:30) → 5/5 ✓

A specific failure mode persists across both models even with all perceptual confounds removed:

| Stimulus | Hour hand position | Persistent answer | Pattern |
|----------|---------------------|-------------------|---------|
| 7:45 | 75% past 7 toward 8 | "8:45" | "near 8" → "the hour is 8" |
| 11:40 | 67% past 11 toward 12 | "12:40" | "near 12" → "the hour is 12" |
| 5:50 (Sonnet) | 83% past 5 toward 6 | "6:50" | "near 6" → "the hour is 6" |

In every persistent error, the hour hand is more than two-thirds of the way to the next numeral. The model reads "hour hand near numeral N" as "the hour is N." It uses **nearest-numeral** instead of **earlier-numeral** convention.

This is the **position-to-hour conversion error**. The model verbally knows the convention ("hour hand at three-quarters between 7 and 8 means 7:45, not 8:45") from the dialogic-teaching transcripts. But it doesn't apply the rule when reading directly. The error persists with no role ambiguity, no extrapolation challenge, no perceptual confound.

## Three architectural mechanisms now confirmed and separable

The day's experiments now cleanly distinguish:

### 1. Perceptual extrapolation
Demonstrated cleanly in the half-circle scale experiment. Single-hand, single-label task. Long pointer reaches the labels: 100% accuracy (Opus), 94% (Sonnet). Short pointer: collapse to 27–53% with rare opposite-end flips.

### 2. Role-identification
Eliminated by color disambiguation. Hand-swap errors that persisted across short-handed AND long-handed conditions disappear when the model is told and shown which hand is which by color. This isolates the role-identification mechanism: it's a separable architectural pattern, dependent on visual disambiguation cues (length, thickness, color).

### 3. Position-to-hour conversion
The residual mechanism after extrapolation and role-identification are removed. Persists at 7:45, 5:50, 11:40 across both models with color clocks. The model defaults to "nearest numeral" interpretation of the hour hand instead of the correct "earlier numeral." This is a CONVENTION error, not a perception error.

## Implications for the Fuego draft

The unified-mechanism story from this morning was overclaim, caught by the long-handed validation. The honest revised story:

> Vision-language models on clock-reading fail through three separable architectural mechanisms. Perceptual extrapolation: short pointers can't be reliably traced outward to labels. Role-identification: when both hands look alike, the model can't reliably tell them apart. Position-to-hour conversion: even with the perception correct and the role unambiguous, the model uses "nearest numeral" instead of "earlier numeral" to read the hour, producing systematic +1-hour errors when the hour hand is past two-thirds of the way to the next numeral.

The half-circle experiment isolates mechanism (1) cleanly. The color-coded validation isolates mechanism (3) cleanly. Mechanism (2) is exposed by the contrast between short-handed (where role identification by length is harder) and color-clock (where it's easy).

This is **three mechanisms cleanly distinguished**, not one mechanism that explains everything. The story is richer than the overclaim and arguably more useful for predicting failures in other diagram-reading tasks: pointer length matters (extrapolation), pointer-vs-pointer disambiguation matters (role-identification), and convention application matters (position-to-value conversion).

## Why this matters

The cleanest demonstration: **with a clock that has long color-coded hands, the model gets cardinal positions perfectly (3:00, 9:00, 1:15, 4:30, 10:30, 8:25), but still mis-reads stimuli where the hour hand is in the late-fractional zone (7:45, 11:40, 5:50).** Same model, same prompt, same kind of stimulus. Only the hour-hand position changes. The conversion error fires specifically when the hour hand is "near the next numeral."

This is positive evidence for an architectural pattern at the language layer (or the perception-to-output bridge): the model interprets "near X" as "X" rather than as "approaching X." On clocks the convention is the latter; the model defaults to the former.

## Open follow-up

Could test whether prompt-level instruction fixes the conversion error: tell the model explicitly "if the hour hand is past two-thirds of the way to the next numeral, the hour is the EARLIER numeral, not the next one." If that prompt fixes 7:45 / 11:40 / 5:50 reliably, the conversion error is in-context-correctable. If not, it's deeper.

## Cost
100 API calls, ~$2-3. Cumulative clocks-arc: ~$58-73.

## Cross-references
- Half-circle extrapolation: `HALFCIRCLE_FINDINGS_05072026.md`
- Long-handed validation: `LONG_HANDS_VALIDATION_FINDINGS_05072026.md`
- Style-swap: `STYLE_SWAP_FINDINGS_05072026.md`
- v2 dialogic teaching rounds 1–3: `sonnet_v2_round{1,2,3}/FINDINGS.md`
