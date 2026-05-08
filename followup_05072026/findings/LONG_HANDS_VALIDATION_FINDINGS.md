# Long-Handed Clock Validation — Prediction PARTIALLY Refuted

**Date:** 2026-05-07 ~17:45 ET
**Per Ted's instruction:** validate the falsifiable prediction from the half-circle extrapolation experiment.

**Predicted (from half-circle finding):** A clock with both hands drawn LONG (tips reaching numeral ring) should read accurately even on stimuli that fail with the standard short-thick hour hand.

**Result:** **The prediction is partially confirmed, partially refuted.** Long-handed clocks fix some failures (Sonnet 4:30 recovered, Sonnet 8:25 improved partially) but persist or worsen others (5:50, 7:45, 2:35 still fail; Opus 3:00 → 12:15 BROKE on a previously-perfect cardinal). Net accuracy is about the same as the short-handed baseline. **Two-hand clock-reading involves additional architectural failures beyond the half-circle perceptual mechanism.**

## Setup

10 stimuli × 5 trials × 2 models = 100 calls. Same 10 stimuli as the v2 dialogic teaching set (R1 baseline). Both hands drawn long-thin (hour at 0.72 of inner radius, minute at 0.82). Both tips sit near or past the numeral ring at 0.74. Hour still shorter than minute for role distinction. Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON.

## Results

**Sonnet 4.6 thinking-ON, long-handed: 29/50 (58%)**

| Stimulus | Truth | Sonnet long-handed answers | Status vs R1 baseline |
|----------|-------|---------------------------|----------------------|
| 3:00 | 3:00 | 5/5 ✓ | maintains R1's perfect |
| 9:00 | 9:00 | 5/5 ✓ | maintains R1's perfect |
| 1:15 | 1:15 | 3/5 (two 12:15 hand-swap errors) | R1 was 1/1 ✓; degraded |
| **4:30** | 4:30 | **5/5 ✓** | R1 ✓; broken in R2/R3 with self-check; recovers |
| 7:45 | 7:45 | 2/5 (three 8:45 forward-conversion errors) | R1 was wrong (8:45); marginal improvement |
| 10:30 | 10:30 | 5/5 ✓ | R1 not tested |
| **2:35** | 2:35 | **0/5** (all 7:15 hand-swap) | R1 wrong (7:15); persists |
| **5:50** | 5:50 | **0/5** (all 10:30 hand-swap) | R1 wrong (10:30); persists |
| 11:40 | 11:40 | 2/5 (three 8:00 errors) | R1 not tested |
| 8:25 | 8:25 | 2/5 (mixed errors: 5:45, 9:25, 4:45) | R1 wrong (9:25); marginal improvement |

**Opus 4.7 thinking-ON, long-handed: 29/50 (58%)**

| Stimulus | Truth | Opus long-handed answers | Status vs Stage 3 Opus thinking-ON |
|----------|-------|--------------------------|-----------------------------------|
| **3:00** | 3:00 | **0/5** (all 12:15 hand-swap) | Stage 3 ✓; **BROKE** under long-hands |
| 9:00 | 9:00 | 5/5 ✓ | Stage 3 ✓ |
| 1:15 | 1:15 | 5/5 ✓ | Stage 3 ✓ |
| 4:30 | 4:30 | 5/5 ✓ | Stage 3 ✓ |
| **7:45** | 7:45 | **0/5** (all 8:45 forward-conversion) | Stage 3 ✓ at full thinking; **BROKE** under long-hands |
| 10:30 | 10:30 | 5/5 ✓ | Stage 3 ✓ |
| 2:35 | 2:35 | 4/5 (one 3:35 slip) | Stage 3 ✓; maintains |
| **5:50** | 5:50 | **0/5** (all 10:30 hand-swap) | Stage 3 ✓ at full thinking; **BROKE** under long-hands |
| 11:40 | 11:40 | 0/5 (mix of 12:40 and 8:00) | Stage 3 wrong (12:40); persists |
| 8:25 | 8:25 | 5/5 ✓ | Stage 3 ✓; maintains |

## What this means

The half-circle extrapolation mechanism is real. **But it's not the only architectural failure in two-hand clock-reading.** The long-handed clock validation reveals at least two additional mechanisms:

### 1. Hour-hand position-to-hour CONVERSION error (not just perceptual extrapolation)

7:45 persistently reads as 8:45 across both short-handed and long-handed conditions. With the long hand reaching the numeral ring, the model can clearly see the hour hand near numeral 8. **The persistent error isn't perceptual** (the hand IS near 8, and the model says so). **The error is in the conversion: the model interprets "hour hand near 8" as "the hour is 8" instead of "the hour is 7, going on 8."**

This is the consistency-check insight from earlier dialogic-teaching findings: at 7:45 the hour hand should be 75% of the way from 7 to 8 (clearly closer to 8). The visual perception is right; the time-conversion is wrong. The long-handed test makes the perception even cleaner, but the conversion error persists. **This is independent of the half-circle extrapolation mechanism.**

### 2. Role-identification depends on visual length disparity

5:50 → 10:30 hand-swap and 2:35 → 7:15 hand-swap persist across long-handed conditions. Worse, **Opus's previously-perfect 3:00 broke under long-hands** (5/5 → 12:15 hand-swap), and Opus's previously-correct 7:45, 5:50 also broke (5/5 ✓ in Stage 3 → 5/5 ✗ here).

Why? With both hands drawn long-thin and only modest length difference (0.72 vs 0.82 of inner radius), **the visual disambiguation cue between hour and minute is weakened.** The original short-thick hour hand provided a strong disambiguating signal: "this hand is short and stubby; that hand is long and thin." Removing that cue makes role assignment harder.

So **the long-handed visual has two competing effects:**
- (+) Hour hand tip near numerals → easier hour-position read
- (-) Length disparity reduced → harder role identification

For some stimuli the (+) wins (4:30 recovered, Sonnet 8:25 partially improved). For others the (-) wins (Opus 3:00 broke, 5:50 persisted).

### 3. Anchor-attractor at 12 partially persists

11:40 → 12:40 anchor pull was documented in Opus simplest-clock test. Long-handed Opus 11:40: mix of 12:40 and 8:00 (8:00 is new, suggesting the long-thin minute hand at angle 240° is being read as the hour hand at 8). Anchor-attractor effect partially persists.

## Reframe

The half-circle finding still stands as the cleanest demonstration of **single-hand extrapolation** accuracy. The clean prediction "vision-language models read angles accurately when the pointer tip reaches labels" is robust on the half-circle scale.

But the **claim that this single mechanism explains all clock-reading failures** is overclaim. Two-hand clock-reading has additional layers:
1. **Position-to-hour conversion** (the model must interpret "hour hand near N" as "hour is N-1 with significant minute past")
2. **Role-identification depends on visual length disparity** (making hands more similar weakens role assignment)
3. **Anchor-attractor poses** at near-vertical positions remain present

The long-handed test partially DECOUPLES extrapolation from these other mechanisms. It shows the half-circle mechanism is one factor, not the whole story.

## Implications for the paper and the Fuego draft

The Fuego draft I wrote earlier ("the morning's five 'mechanisms' collapse into one") is **partially refuted by this validation experiment.** The single-mechanism framing was overclaim. The actual structure:

- **Half-circle test:** demonstrates the perceptual extrapolation mechanism cleanly. Single hand. Single label. Clean.
- **Two-hand clock-reading:** involves perceptual extrapolation PLUS hour-conversion PLUS role-identification PLUS anchor-attractor. Multiple architectural layers.

The Fuego draft should be revised:
- Soften "all five mechanisms collapse into one" to "the half-circle experiment demonstrates ONE mechanism (perceptual extrapolation); the long-handed clock validation shows two-hand clock-reading involves at least two more (conversion and role-identification)."
- The "real clock validation" experiment didn't validate the full prediction. It validated the perception layer, but two-hand clock-reading has additional failures.
- This is actually **more interesting and more honest** than the single-mechanism story. It frames the half-circle as one well-isolated mechanism while preserving the multi-mechanism reality of clock-reading.

The paper structure should reflect this:
1. Open with the half-circle experiment as the cleanest mechanism demonstration.
2. Apply to clocks: explain forward-shift errors (sometimes perceptual, sometimes conversion).
3. **Acknowledge the long-handed test result:** the prediction is partially confirmed; perceptual extrapolation is one factor, conversion and role-identification add more.
4. The unified-mechanism story was an overclaim that this experiment caught. Document the iteration honestly.

## Methodological lesson

This is the second time today a clean overclaim was caught by a falsifying test:
- Memory #566 (B1 predicts everything) was overclaim caught by the population-level analysis (#567).
- The unified-mechanism Fuego draft is overclaim caught by this long-handed validation.

Two adversarial-test catches in one day. Both rescued the analysis from a too-clean story. The lesson: every "single mechanism explains everything" story should be subjected to a falsifying test before it gets published. This is exactly what the long-handed validation just did.

## Cost
100 API calls (50 + 50). ~$2-3.
Cumulative clocks-arc: ~$55-70.
