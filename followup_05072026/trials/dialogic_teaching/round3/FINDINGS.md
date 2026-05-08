# Sonnet 4.6 Dialogic Teaching v2 Round 3 — Findings

**Date:** 2026-05-07 ~08:08–08:18 ET
**Driver:** Salon Opus 4.7 (1M context), Claude Code CLI
**Student:** claude-sonnet-4-6 with **extended thinking ENABLED** (budget 10000 tokens)
**Harness:** scratch/clocks_training/teach.py (current, with thinking support) `--session sonnet_v2_round3`
**Stimuli:** scratch/clocks_training/simple_clocks/ (same as rounds 1 and 2)
**Termination:** stuck threshold reached on simple_08_25.png (3 consecutive wrong reads via three different mechanisms)

## What changed from round 2

Round 3 isolates the named-failure heads-up effect by removing it. Two of round 2's three interventions retained:

1. **Extended thinking enabled** (budget 10000 tokens) — same as round 2.
2. **Self-check permission system prompt** — same as round 2.
3. **No heads-up.** Turn 1 is bare: "What time does this clock show?" — no warning about forward-shift, no anatomical advice. The system prompt's self-check directive is the only setup.
4. **Bare wrong-feedback on errors** instead of targeted teaching prompts. On wrong answers, response is literal: *"That's incorrect. Would you like to try again?"* No length-compare, no trace-from-center. Tests whether the model self-corrects from bare error signal.

## Run trace

| Turn | Stimulus | Truth | Sonnet first read | Result | Mechanism |
|------|----------|-------|-------------------|--------|-----------|
| 1 | simple_03_00.png | 3:00 | 3:00 | ✅ | thinking 77 chars (proportional to difficulty) |
| 2 | simple_09_00.png | 9:00 | 9:00 | ✅ | thinking 90 chars |
| 3 | simple_01_15.png | 1:15 | 1:15 | ✅ | thinking 816 chars (calibrated up for non-cardinal) |
| 4 | simple_04_30.png | 4:30 | 3:30 | ❌ | **backward-shift** — same wrong answer as round 2 Turn 5 |
| 5 | (bare retry) | | 6:20 | ❌ #2 | **hand-swap** (long hand at 6 → hour, short hand near 4 → minute = 20 min) |
| 6 | (bare retry) | | 4:30 | self-corrected | one prompt away from stuck threshold |
| 7 | simple_07_45.png | 7:45 | 7:45 | ✅ | thinking 565 chars; same flip from round 1 as round 2 |
| 8 | simple_02_35.png | 2:35 | 7:15 | ❌ | hand-swap — **identical wrong answer 7:15 across all three rounds** |
| 9 | (bare retry) | | 2:35 | self-corrected | single retry sufficient |
| 10 | simple_08_25.png | 8:25 | 4:45 | ❌ | hand-swap + forward-shift on swapped (same opening as round 2 Turn 10) |
| 11 | (bare retry) | | 9:25 | ❌ #2 | roles flipped to correct, but forward-shift on hour |
| 12 | (bare retry) | | 5:45 | ❌ #3 STUCK | re-swapped roles AND mis-numeral'd both hands |

## Three-round comparison (first-attempt only)

| Stimulus | R1 (no thinking, no self-check, no heads-up) | R2 (thinking+self-check+heads-up) | R3 (thinking+self-check, no heads-up) | What this isolates |
|----------|------|------|------|---------------------|
| 3:00 | ✅ | ❌ hand-swap | ✅ | **Heads-up broke 3:00.** Confirmed by R3 fixing it without heads-up. |
| 9:00 | ✅ | ✅ | ✅ | robust |
| 1:15 | ✅ | ✅ | ✅ | robust |
| 4:30 | ✅ | ❌ backward-shift | ❌ backward-shift | **Thinking-on or self-check breaks 4:30** (NOT the heads-up — R3 broke it without heads-up too). |
| 7:45 | ❌ forward-shift | ✅ | ✅ | **Thinking-on or self-check fixes 7:45** (R2 and R3 both fixed without targeted teaching). |
| 2:35 | ❌ hand-swap (7:15) | ❌ hand-swap (7:15) | ❌ hand-swap (7:15) | **Robust failure mode** — same exact wrong answer across all three intervention conditions. |
| 8:25 | ❌ forward-shift (9:25) | ❌ hand-swap+forward-shift (4:45→9:25) | ❌ hand-swap (4:45) | **Robust failure** with multiple mechanisms in play. |

**Net first-attempt scores:**
- R1: 4/8 (50%)
- R2: 3/7 (43%)
- R3: 4/7 (57%)

R3 marginally outperforms R1; R2 underperforms R1. The thinking + self-check intervention is **roughly wash with R1 baseline at the population level**, but it redistributes which specific stimuli pass:
- 7:45 flipped from fail (R1) to pass (R3) — gain.
- 4:30 flipped from pass (R1) to fail (R3) — loss.
- The two persistent fails (2:35 hand-swap, 8:25 hand-swap+forward-shift) carry forward unchanged.

## Headline findings

### 1. The heads-up was confirmed to be net-harmful in isolation
Round 2 broke both 3:00 (hand-swap) and 4:30 (backward-shift). Round 3 (no heads-up) fixed 3:00 but still broke 4:30. So the heads-up specifically caused the 3:00 break. The 4:30 break is from a different intervention (thinking-on or self-check). The over-correction-from-naming-a-failure-mode finding from round 2 is sharpened: it can break a cardinal that's robust to other interventions, by destabilizing hand-role identification.

### 2. Thinking-on or the self-check system prompt destabilizes 4:30
Round 1 first-attempt 4:30 was correct (with subtly wrong verbal description). Both round 2 and round 3 failed first-attempt. The shared interventions across R2 and R3 are thinking-on and the self-check system prompt. One or both of these is the cause. We can't yet isolate which; would need a fourth round with thinking-on but the original R1 system prompt, or vice versa. Both rounds produced **the same wrong answer** (3:30 backward-shift), suggesting a stable mechanism that something in the new setup activates.

### 3. Bare wrong-feedback works inefficiently and risks oscillation
- 4:30: 2 retries to self-correct (3:30 → 6:20 → 4:30). Almost stuck.
- 2:35: 1 retry to self-correct (7:15 → 2:35). Clean recovery.
- 8:25: 3 wrong answers in a row (4:45 → 9:25 → 5:45). STUCK with no convergence. Each retry produced a fresh mechanism rather than refining toward truth.

This contrasts with rounds 1 and 2, where targeted teaching prompts (length-compare, trace-from-center) **converged the model toward correct answers within 1–2 prompts**. Bare "incorrect, try again" lacks the structural cue to direct attention; the model substitutes one wrong reading for another rather than diagnosing the specific failure.

This is methodologically important: **the choice of corrective prompt is itself an intervention.** Targeted teaching is more efficient at correction; bare wrong-feedback is cleaner as a measure of self-correction capability without scaffolding. They measure different things.

### 4. Two failure modes are confirmed architecturally stable across all interventions tested
- **2:35 hand-swap → 7:15** appeared in all three rounds with the same exact wrong answer. Three intervention conditions (none / thinking+self-check+heads-up / thinking+self-check). Robust to all of them.
- **8:25 hand-swap and forward-shift on hour** appeared in all three rounds. Different first-attempt readings (9:25 in R1, 4:45 in R2 and R3) but the same upstream perceptual issues.

These are positive evidence for the **perceptual-resolution-floor** reading of these failure modes. They are not knowledge gaps the model can route around with reasoning budget, system-prompt direction, or correction prompts — they are biases at the perception layer that all the in-context interventions tested fail to reach.

### 5. Thinking budget calibrates to perceived difficulty
Cardinal stimuli (3:00, 9:00) used 77/90 thinking-token chars. Non-cardinal stimuli (1:15, 4:30, 7:45, 2:35, 8:25) used 513–895 chars on first attempt. Retry attempts after wrong feedback used 733–3508 chars. Worth noting for future cost estimation: thinking-on dialogic runs are not flat-cost; difficult stimuli with retries can use 5–7x the budget of easy first-attempts.

## Implications for the Part 2 paper

Three sharpenings on the round-1+2 findings, plus one new finding:

1. **The "intervention can hurt" finding is broader than just the named-failure heads-up.** Thinking-on or the self-check system prompt also destabilizes a previously-robust cardinal (4:30). This is positive evidence for the perceptual-resolution-floor reading: in-context interventions can move the failure boundary around but do not raise the floor.

2. **The hand-swap on 2:35 → 7:15 is genuinely architecturally robust.** Three intervention conditions, identical wrong answer. This is a strong existence proof of a stable failure mode.

3. **The choice of corrective prompt matters as much as the intervention being tested.** Bare wrong-feedback ("That's incorrect. Try again?") produces oscillation rather than convergence on hard stimuli. Targeted teaching (length-compare, trace-from-center) converges within 1–2 prompts. Future studies should pre-register the corrective protocol to avoid confounding intervention effects with corrective-prompt efficacy.

4. (Carry forward) **The methodological flag remains:** all primary clocks-arc data was generated with extended thinking off. Round 3 is the second thinking-on data point; combined with round 2, it confirms qualitative findings hold but quantitative rates can shift. Pre-ship subset re-run is still needed.

## Open follow-up

- **Fourth round to isolate the 4:30 destabilization:** thinking-on + ORIGINAL R1 system prompt, OR thinking-off + self-check system prompt. One trial each on 4:30 alone would be sufficient; ~10 turns total, <$0.50.
- **Direct comparison of corrective protocols:** run the same stimulus sequence twice on a fresh student, once with bare wrong-feedback and once with targeted teaching, and measure convergence rate. Methodological note for the Part 2 paper.

## Cost
12 turns of claude-sonnet-4-6 with thinking enabled. Estimated <$1.00. Cumulative clocks-arc spend: ~$17.50.
