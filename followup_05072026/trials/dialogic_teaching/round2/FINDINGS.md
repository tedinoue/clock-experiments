# Sonnet 4.6 Dialogic Teaching v2 Round 2 — Findings

**Date:** 2026-05-07 ~07:50–08:05 ET
**Driver:** Salon Opus 4.7 (1M context), Claude Code CLI
**Student:** claude-sonnet-4-6 with **extended thinking ENABLED** (budget 10000 tokens)
**Harness:** scratch/clocks_training/teach.py with `--session sonnet_v2_round2` (patched for thinking support)
**Stimuli:** scratch/clocks_training/simple_clocks/ (same as round 1)
**Termination:** stuck threshold reached on simple_08_25.png (3 consecutive wrong reads after 3 distinct corrective prompts)

## What changed from round 1

Three stacked interventions:

1. **Extended thinking enabled.** All API calls used `thinking={"type": "enabled", "budget_tokens": 10000}`. Round 1 (and the entire 640-trial dataset, hybrid eval, perception baseline, and prior teach.py runs) was generated with thinking OFF.

2. **System prompt rewritten** to give explicit self-check permission:

> "You are reading analog clocks. You are an extended-thinking model — use your reasoning budget freely. Take your time on each clock; check your work before answering. If you spot a mistake on review, revise. Reply only when you're confident in the time."

3. **Named-failure heads-up in turn 1 only** (not stickied — one-shot setup, system prompt carries the self-check across the conversation):

> "What time does this clock show? Heads-up on a known issue: the hour hand can read as past the *upcoming* numeral instead of the *current* one. After your initial read, trace the hour hand from the center outward and verify which numeral it has just passed (going clockwise from 12). The hour hand's fractional position should also match the minute reading — at 45 minutes the hour hand should be three-quarters of the way to the next numeral. Revise if your check surfaces a mismatch."

Subsequent turns use bare prompts ("Try this", "Yes. And this") — same protocol shape as round 1.

## Run trace

| Turn | Stimulus | Truth | Sonnet first read | Result | Mechanism |
|------|----------|-------|-------------------|--------|-----------|
| 1 | simple_03_00.png | 3:00 | 12:15 | ❌ | hand-swap on a cardinal |
| 2 | (re-ask: length-compare) | 3:00 | 3:00 | self-corrected | |
| 3 | simple_09_00.png | 9:00 | 9:00 | ✅ | adopted length-compare-first structure |
| 4 | simple_01_15.png | 1:15 | 1:15 | ✅ | |
| 5 | simple_04_30.png | 4:30 | 3:30 | ❌ | **backward-shift** on hour hand (truth at 4-5 midpoint, read as 3-4 midpoint) |
| 6 | (re-ask: trace-from-center) | 4:30 | 4:30 | self-corrected | |
| 7 | simple_07_45.png | 7:45 | 7:45 | ✅ | applied trace pre-emptively — **flip from round 1** |
| 8 | simple_02_35.png | 2:35 | 7:15 | ❌ | hand-swap (same as round 1, but Sonnet reported it had "compared lengths") |
| 9 | (re-ask: length-by-position) | 2:35 | 2:35 | self-corrected | |
| 10 | simple_08_25.png | 8:25 | 4:45 | ❌ | hand-swap + forward-shift |
| 11 | (re-ask: length-by-position) | 8:25 | 9:25 | ❌ #2 | roles fixed; forward-shift remained |
| 12 | (re-ask: trace-from-center) | 8:25 | 9:25 | ❌ #3 | reaffirmed forward-shift after explicit count prompt |
| 13 | (re-ask: direct visual bracket) | 8:25 | 9:25 | ❌ stuck | metacognitive uncertainty ("Are you seeing it differently?") but no perceptual adjustment |

## Direct comparison with round 1 first-attempt reads

| Stimulus | Round 1 first-attempt | Round 2 first-attempt | Effect |
|----------|----------------------|------------------------|--------|
| 3:00 | ✅ 3:00 | ❌ 12:15 (hand-swap) | **HURT** — intervention broke a cardinal |
| 9:00 | ✅ 9:00 | ✅ 9:00 | same |
| 1:15 | ✅ 1:15 | ✅ 1:15 | same |
| 4:30 | ✅ 4:30 (verbal slightly off) | ❌ 3:30 (backward-shift) | **HURT** — intervention introduced backward-shift |
| 7:45 | ❌ 8:45 (forward-shift) | ✅ 7:45 | **HELPED** — first-attempt correct |
| 2:35 | ❌ 7:15 (hand-swap) | ❌ 7:15 (hand-swap) | same — same exact wrong answer |
| 8:25 | ❌ 9:25 (forward-shift) | ❌ 4:45 (hand-swap + forward-shift) | same or worse |

**Net:** 2 cardinals broken (3:00, 4:30), 1 non-cardinal fixed (7:45). Round 2 is **net negative** on first-attempt accuracy compared to round 1.

Round 1: 4 of 8 first-attempts correct.
Round 2: 3 of 7 first-attempts correct (stopped one stimulus earlier due to stuck-condition on 8:25 instead of round 1's 5:50).

Stuck condition reached **earlier** in round 2 (Turn 13, stimulus 7) than round 1 (Turn 14, stimulus 8).

## Headline findings

### 1. The named-failure heads-up caused over-correction
This was the predicted risk. Round 2's two cardinal failures (3:00 → hand-swap; 4:30 → backward-shift) and the backward-shift on 4:30 are most simply explained as the model fixating on hour-hand position at the expense of length-compare, and erring in the OPPOSITE direction from the named failure mode. Round 1's 4:30 was first-attempt correct with subtly wrong verbal description. Round 2 broke 4:30 entirely.

### 2. Cross-stimulus transfer DID happen — but only for length-compare-first, not for trace-from-center
After Turn 2's length-compare correction, Sonnet adopted "Comparing lengths directly:" as the first step of every subsequent response. This is real cross-stimulus transfer that round 1 did not show.

But the trace-from-center procedure did NOT transfer cleanly. On 8:25 (Turn 10) Sonnet did invoke the trace, but counted up through "1, 2, 3, 4, 5, 6, 7, 8, 9" and concluded the hand had passed 9. The procedure ran on biased perception of where the hand actually is. After explicit teaching prompts on Turns 11–13, Sonnet doubled down on "just past 9" three times.

So: the structural procedure transfers, but the underlying perceptual bias (which numeral the hour hand is actually past) is **not** correctable by structural prompting.

### 3. Thinking mode did not fix the perceptual biases
Each turn used 500–1900 tokens of internal thinking budget. The model applied the budget to careful step-by-step reasoning — visible in the response structure. But every wrong answer in the run was self-validated by an internal consistency check that ran on biased perception, exactly as in round 1. More reasoning budget produced more elaborate self-validation, not corrected perception.

### 4. Sonnet showed metacognitive uncertainty at the stuck threshold but couldn't act on it
Turn 13 final response: "Are you seeing it differently — is the tip actually between 8 and 9?" The model has the meta-level awareness that it might be wrong, and even names the correct alternative bracketing — but visually maintains "between 9 and 10." This is a clean demonstration that the failure is upstream of metacognition: knowing you might be biased doesn't fix the bias.

## Implications for the Part 2 paper

The two findings already queued from round 1 strengthen substantially:

- **In-context teaching does not transfer across stimuli within a session** — round 2 shows that a STRUCTURAL procedure can transfer (length-compare-first), but the underlying PERCEPTUAL biases (which numeral the hour hand is past, which physical hand is longer) do not yield to in-context intervention. Targeted teaching corrects single instances; the upstream perception remains biased.
- **The consistency-check insight operates on perceptual outputs, not perceptual processes** — confirmed across both rounds, now with a thinking-on data point. Extended reasoning budget produces longer self-validation, not corrected perception.

New finding from round 2 specifically:

- **Naming a failure mode in the prompt can cause over-correction in the opposite direction.** This is positive evidence for the "perceptual resolution floor" reading: the failures are not knowledge gaps the model can route around, they are biases at the perception layer. Telling the model "you read X as Y" causes it to read X as not-Y, but it doesn't bring perception closer to truth. It just shifts which side of truth perception lands on.

## Methodological flag (carried forward, urgent)

**All prior clocks-arc results were generated with extended thinking OFF.** This includes:
- The 640-trial systemprompt-condition Sonnet dataset (S1, S2, S3a-d, heavy_summary)
- The hybrid-condition Sonnet trials
- The perception baseline (B1–B4, Sonnet)
- Round 1 of this dialogic teaching run

Round 2 is the first thinking-on data point. Comparison shows that thinking-on does not change the qualitative findings (forward-shift, hand-swap, internal-consistency rule all still present), but quantitative rates may differ. Before the Part 2 paper ships, a representative thinking-on subset of the 640-trial dataset should be run for direct comparison, and the paper should disclose that all primary results are in the non-thinking mode.

## Cost
13 turns of claude-sonnet-4-6 with thinking enabled (10K budget) and multimodal input. Estimated <$1.00. Higher than round 1's <$0.50 due to thinking tokens.
