# Convention-Rule Fix Experiment — Conversion Error Partially Correctable, with Symmetric Over-correction

**Date:** 2026-05-07 ~18:50 ET
**Per Ted's design:** test whether the position-to-hour conversion error documented in the color-clock experiment (#13) is in-context-correctable. Use the same color clocks; add an explicit convention rule to the prompt.

**Hypothesis under test:** if the model knows the convention verbally but fails to apply it on perception, prompting the rule should fix the canonical conversion failures (7:45 → 8:45, 11:40 → 12:40, 5:50 → 6:50). If those failures persist with the rule, the conversion error is deeper than language-level instruction.

## Setup

Same 10 stimuli as #13 (color clocks). Same color-disambiguation prompt. Add a rule sentence:

> *Reminder on convention: the hour is determined by the numeral the hour hand has most recently passed, not the next one it's approaching. If the hour hand is between two numerals, the hour is the EARLIER numeral (the smaller one going clockwise), regardless of how close to the next numeral it sits. The minute hand tells you how many minutes past that hour.*

10 stimuli × 5 trials × 2 models = 100 calls. Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON.

**Note on execution:** the sandbox's cumulative-credential-risk classifier had ratcheted up by this point in the day, blocking all agent-emitted credential operations. Ted ran the experiment manually in his terminal after restarting Claude Code (which reset the classifier).

## Aggregate results

| Run | n | Correct | vs no-rule baseline (#13) | Net delta |
|-----|---|---------|---------------------------|-----------|
| Sonnet | 50 | 41/50 (82%) | 43/50 (86%) | **−2 correct** |
| Opus | 50 | 40/50 (80%) | 38/50 (76%) | **+2 correct** |

**Net effect across models: approximately zero.** The rule redistributes failures rather than removing them.

## Per-stimulus pattern

| Stimulus | Sonnet no-rule | Sonnet rule | Opus no-rule | Opus rule | Effect |
|----------|----------------|-------------|--------------|-----------|--------|
| 3:00 | 5/5 | 5/5 | 5/5 | 5/5 | unchanged |
| 9:00 | 5/5 | 5/5 | 5/5 | 5/5 | unchanged |
| **1:15** | **5/5 ✓** | **0/5** (all 12:15) | **5/5 ✓** | **0/5** (all 12:15) | **rule BREAKS in both models** |
| 4:30 | 5/5 | 5/5 | 5/5 | 5/5 | unchanged |
| **7:45** | 4/5 | 2/5 | 2/5 | **5/5 ✓** | mixed (Sonnet hurt, Opus fixed) |
| 10:30 | 5/5 | 5/5 | 5/5 | 5/5 | unchanged |
| 2:35 | 5/5 | 4/5 | 0/5 (all 2:32-ish) | 0/5 (all 2:32-ish) | minute-position slip persists |
| **5:50** | 2/5 | **5/5 ✓** | 5/5 | 5/5 | rule fixes (Sonnet), already perfect (Opus) |
| **11:40** | 2/5 | **5/5 ✓** | 1/5 | **5/5 ✓** | rule FIXES in both models |
| 8:25 | 5/5 | 5/5 | 5/5 | 5/5 | unchanged |

## Three findings

### 1. The rule fixes the canonical conversion failures
Stimuli where the hour hand is more than two-thirds of the way to the next numeral were the persistent residual in the color-clock test (#13). The convention rule fixes them:
- **5:50** (hour hand 83% past 5 toward 6): Sonnet 2/5 → 5/5
- **11:40** (hour hand 67% past 11 toward 12): Sonnet 2/5 → 5/5; Opus 1/5 → 5/5
- **7:45** for Opus (hour hand 75% past 7 toward 8): 2/5 → 5/5

These stimuli all share the same architectural pattern: the hour hand is past two-thirds of the way to the next numeral, the model previously read it as "the hour is N+1," and now reads it as "the hour is N." The conversion error is in-context-correctable for these cases.

### 2. The rule breaks 1:15 in both models with identical wrong answers
**The smoking-gun result:** 1:15 → 12:15 in ALL 5 trials, in BOTH models, across both Sonnet and Opus. Was 5/5 perfect in the no-rule color-clock test.

The rule says "the hour is the earlier numeral, the smaller one going clockwise." For 1:15, the hour hand is just past 1. The correct earlier numeral is 1 (the model should report "1:15"). But the model interprets "earlier" too aggressively, reaching back to 12 (the previous-previous numeral going clockwise from 1) and reporting "12:15."

This is the classic over-correction pattern: telling the model about a directional bias produces a bias in the opposite direction. The instruction "use the earlier numeral" pulls the model's reading backward beyond truth.

### 3. Same over-correction pattern as Round 2's heads-up
Round 2 of the morning's dialogic teaching (memory #564, sonnet_v2_round2/FINDINGS.md) tested adding a turn-1 heads-up about the forward-shift failure mode. The result: the model over-corrected in the opposite direction, breaking 4:30 (5/5 perfect → 0/5, all reading as 3:30 backward-shift).

This rule-fix experiment, twelve hours later, demonstrates the same pattern in a different configuration:
- **Round 2 (morning):** heads-up about forward-shift → backward-shift on 4:30
- **Rule-fix (evening):** rule about earlier-numeral → over-shoot to previous-previous numeral on 1:15

**Two independent demonstrations of "naming a bias triggers opposite-direction over-correction" in the same session.** The over-correction mechanism is robust across models, prompts, and experiment configurations.

## Implications for the three-mechanism story

The rule-fix experiment confirms that the position-to-hour conversion error (#13) is a separable architectural mechanism, distinct from perception. The model's verbal knowledge of the convention is real (the rule, when applied, fixes the canonical failures). But applying the verbal rule has its own architectural cost: the model can't reliably calibrate "how much earlier" without overshooting in cases where the hour hand is just slightly past a numeral.

**The conversion error is partially in-context-correctable but the fix isn't a clean fix.** It redistributes failures rather than removing them. Net effect across models: zero. Same number of trials wrong, different stimuli failing.

This rules out a simple "the model just needs the right prompt" objection to the conversion-error finding. Tested. Doesn't work cleanly.

## What the rule-fix tells us about the model's architecture

Three observations worth recording:

1. **The model's verbal knowledge of clock-reading convention is real** (5:50, 11:40 fix when prompted).

2. **Applying that verbal knowledge to perception is calibration-fragile.** The same instruction that fixes one direction of error introduces error in the other direction. The model can't reliably tune "how much earlier" without overshooting.

3. **Adding a rule does not provide isolation between rule-known cases and rule-not-applicable cases.** The rule was meant to apply to "hour hand near next numeral" cases (where the model defaults to "nearest numeral"). It also applies, incorrectly, to "hour hand just past current numeral" cases (1:15), pulling those backward when they shouldn't be.

In application terms: prompt-engineering this away requires more nuance than "tell the model the rule." A rule that applies conditionally ("only when the hour hand is past 2/3 of the way to the next numeral") might work better. Untested. Open follow-up.

## Cost
100 API calls (50 + 50). Run manually by Ted in his terminal after restart due to sandbox lockdown. ~$2-3.
Cumulative clocks-arc spend today: ~$60-70.

## Cross-references
- Color-clock baseline: `COLOR_CLOCK_FINDINGS_05072026.md`
- Round 2 heads-up over-correction: `sonnet_v2_round2/FINDINGS.md` (memory #564)
- Half-circle perceptual extrapolation: `HALFCIRCLE_FINDINGS_05072026.md`
- Long-handed validation: `LONG_HANDS_VALIDATION_FINDINGS_05072026.md`
- Master index: `INDEX_05072026.md`
