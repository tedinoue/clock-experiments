# Sonnet 4.6 Dialogic Teaching v2 — Findings

**Date:** 2026-05-07 ~07:18-07:30 ET
**Driver:** Salon Opus 4.7 (1M context), Claude Code CLI
**Student:** claude-sonnet-4-6
**Harness:** scratch/clocks_training/teach.py with --session sonnet_v2
**Stimuli:** scratch/clocks_training/simple_clocks/ (12 Arabic numerals, hour + minute tick marks, two hands, no subdials/Roman/24-hour)
**Termination:** stuck threshold reached on simple_05_50.png (3 consecutive failures with three distinct mechanisms)

## Run trace

| Turn | Stimulus | Truth | Sonnet first read | Result | Mechanism |
|------|----------|-------|-------------------|--------|-----------|
| 1 | simple_03_00.png | 3:00 | 3:00 | ✅ | — |
| 2 | simple_09_00.png | 9:00 | 9:00 | ✅ | — |
| 3 | simple_01_15.png | 1:15 | 1:15 | ✅ | — (used consistency check spontaneously) |
| 4 | simple_04_30.png | 4:30 | 4:30 | ✅ (subtle) | hour-hand verbal description "closer to 4" when truth is exactly halfway |
| 5 | simple_07_45.png | 7:45 | 8:45 | ❌ | forward-shift: hour hand read as "between 8 and 9, closer to 9" (truth: between 7 and 8, closer to 8) |
| 6 | (re-ask) | 7:45 | 7:45 | self-corrected | "walk me through the hour hand" prompt; Sonnet stated consistency-check rule unprompted |
| 7 | simple_02_35.png | 2:35 | 7:15 | ❌ | hand-swap: long hand read as hour, short hand read as minute |
| 8 | (re-ask) | 2:35 | 3:35 | partial | length-compare prompt fixed roles; hour position still forward-shifted ("right at 3", truth ~58% between 2 and 3) |
| 9 | (re-ask) | 2:35 | 2:35 | self-corrected | trace-from-center directional prompt |
| 10 | simple_08_25.png | 8:25 | 9:25 | ❌ | forward-shift recurred — teaching from Turn 9 did NOT transfer |
| 11 | (re-ask) | 8:25 | 8:25 | self-corrected | same trace-from-center prompt; Sonnet explicitly named the recurring pattern |
| 12 | simple_05_50.png | 5:50 | 10:30 | ❌ | hand-swap recurred — teaching from Turn 8 did NOT transfer |
| 13 | (re-ask) | 5:50 | 6:40 | ❌ #2 | length-compare fixed roles; introduced two new errors (minute miscount 10→40 instead of 50; hour read as "at 6" instead of between 5 and 6) |
| 14 | (re-ask) | 5:50 | 6:50 | ❌ #3 | minute math corrected to 50; hour position still forward-shifted ("between 6 and 7, close to 7") — STUCK |

## Headline findings

### 1. Cardinal positions and quarter-past with current-numeral hour: robust
3:00, 9:00, 1:15, 4:30 all read first-attempt correct. Mastery streak reached 4 before breaking on 7:45.

### 2. Two distinct failure modes recur: forward-shift and hand-swap
- **Forward-shift hour reading:** hour hand perceived as past the *upcoming* numeral instead of the current one. 7:45→8:45, 8:25→9:25, 5:50→6:50. Three out of three non-cardinal late-minute stimuli.
- **Hand-swap:** long and short hand role assignments inverted at perception. 2:35→7:15, 5:50→10:30. Two out of three non-cardinal stimuli where the relevant hand positions could trip it.

These mechanisms align with the failure modes documented in FINDINGS_PART_9_DIRECTION_FLIP.md from the 640-trial re-judge: hand-swap (HS) and direction-related hour misreads (HF/MF/BF) are the dominant failure categories there too.

### 3. The consistency-check insight is in Sonnet's repertoire but does not protect against the underlying perceptual biases
Sonnet spontaneously stated the rule on Turn 1 of the first non-cardinal: "the hour hand should be three-quarters of the way through the current hour." It then ran a consistency check on every subsequent reading.

But the consistency check **always self-validates whatever role/position assignments the perception layer produced**:
- On hand-swap (Turn 7), the check confirmed "minute at 15 → hour 1/4 between 7 and 8" — internally consistent given the swapped roles.
- On forward-shift (Turn 10), the check confirmed "25 min → hour 42% between 9 and 10" — internally consistent given the wrong base numeral.
- On Turn 14 (5:50→6:50), the check confirmed "50 min → hour 83% between 6 and 7, close to 7" — internally consistent given the forward-shifted base numeral.

The check operates on perceptual outputs, not on the perceptual process itself. It cannot detect either failure mode. This is consistent with the **internal-consistency rule** finding from FINDINGS_PART_9: Sonnet's flips are geometrically valid given biased base perception.

### 4. Targeted teaching corrects single stimuli but does not transfer to next stimuli
Each failure was correctable with one or two targeted prompts (trace-from-center for forward-shift; length-compare for hand-swap). But the same failure mode recurred on the next fresh stimulus every time:
- Forward-shift correction on 7:45 (Turn 6) → 8:25 still forward-shifted (Turn 10).
- Forward-shift correction on 8:25 (Turn 11) → 5:50 still forward-shifted (Turn 14).
- Hand-swap correction on 2:35 (Turn 8) → 5:50 still hand-swapped (Turn 12).

In Turn 11 Sonnet even *named the recurring pattern* ("I keep misjudging which numeral the hour hand has just passed. Tracing carefully from the center is the key move"). On the very next non-cardinal stimulus (Turn 12, 5:50), it did not first-attempt apply the trace; it produced a hand-swap instead.

This is the **irreconcilable failure pattern** the protocol was designed to surface. The teaching is *episodic-corrective*: it can fix the immediate stimulus when the right targeted question is asked, but it does not produce stable carryover across stimuli within a single session.

### 5. Methodological caveats

- **n=8 stimuli on one model in one session.** This is a single-trial existence proof of the failure-transfer pattern, not a quantified rate. The 640-trial Sonnet study (FINDINGS_PART_9) provides the population-level evidence.
- **Driver-effect risk.** All corrective prompts came from Salon Opus 4.7. A different teacher persona (or a non-AI teacher) might phrase corrections differently. Open question: would non-prompted in-context examples (e.g., "here's a clock at 8:25, and the hour hand sits between 8 and 9, ~42% past 8") produce more stable transfer than question-based correctives?
- **Single session, no fine-tuning.** This run tests in-context teaching only. The mechanism producing the biases is upstream of in-context reasoning and likely persists into the next context window without intervention at the weights level.
- **Positive-framing discipline held throughout.** No "don't do X" corrections. All corrections were "compare directly," "trace from center," "stay with the tension you noticed," or affirming acks of correct reasoning. Per Ted's Turn-5-of-prior-session feedback that negative phrasing primed the model to look for the named failure modes.

## What this means for the Part 2 paper

Two specific incorporations recommended:

1. **In-context teaching does not transfer across stimuli within a session.** This is positive evidence for the "perceptual resolution floor" reading of these failure modes (architecturally constrained, not prompt-modifiable). Add to the discussion of the architecturally-constrained vs. prompt-modifiable distinction.
2. **The consistency-check insight is in the model's repertoire but operates on perceptual outputs, not perceptual processes.** This sharpens the claim from FINDINGS_PART_9 about internal-consistency: the check is genuine reasoning (geometrically valid given inputs), but it cannot detect either of the two dominant upstream perception failures.

## Open questions for follow-up

- **Does fine-tuning on simplest-clock stimuli produce stable hour-hand-position perception?** The current run shows in-context teaching fails to transfer. Weights-level training is the natural next test if Salon wants to push further. Out of scope for the Part 2 paper.
- **Does the failure pattern hold for Opus 4.7 on the same simplest-clock stimuli?** The 640-trial study used clocks with subdials, Roman numerals, and other complications. A clean simplest-clock comparison Opus-vs-Sonnet would isolate model-capability effects from stimulus-complexity effects. One-off existence-proof scope, low cost.
- **Would showing Sonnet a worked example (clock + correct read + position breakdown) before each new stimulus produce transfer that the question-based correctives did not?** Would distinguish "the model can't see the position correctly" from "the model can but doesn't deploy the right reading procedure unprompted."

## Cost
Single session, ~14 turns, claude-sonnet-4-6 with multimodal input. Estimated <$0.50 in API cost.
