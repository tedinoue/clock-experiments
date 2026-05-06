# Clocks Dialogic Teaching — First-Pass Findings

**Date:** 2026-05-05 morning, 09:01-09:12 ET
**Driver:** Terry (Salon, Opus 4.7 in Claude Code CLI)
**Student:** Haiku 4.5 (`claude-haiku-4-5-20251001`)
**Total turns:** 8 (4 explicit clock-reading attempts + 4 framing/diagnostic turns; one re-attach turn after Haiku missed an image)
**Total spend:** ~20K input tokens, ~1.7K output tokens, roughly $0.07
**Status:** Pause-and-review. Ted to look at transcript in detail.

## Question

Can multi-turn dialogic teaching, conducted entirely within the context window (no fine-tuning, no weight changes), make a frontier-model's clock-reading robust rather than fragile? The original clocks experiment (Salon, 2026-05-03) found Haiku 4.5 floored at 6%, 11%, 2%, 16%, 36%, 8% across the six prompting conditions. Single-shot prompting did not get Haiku above the 36% ceiling on any condition. The teaching-question is: would interactive multi-turn instruction reach what single-shot prompting cannot?

## Design

- **Single-model test.** Haiku 4.5 only. Conversation grows turn over turn so token cost grows quadratically; running multiple models in parallel was deferred.
- **Fresh training stimuli.** Eight new clocks rendered at NEW times distinct from the original test set (training times: 2:50, 8:35, 11:20, 5:10, 14:30/2:30, 6:40, 7:35, 12:05). Same eight style categories as the test set so transfer is testable. Renderer at `render_training_clocks.py`; outputs at `clocks/`.
- **Teacher = Terry (Opus 4.7).** Drove the conversation turn by turn from inside the Salon session. Saw each Haiku response, judged it, decided next turn.
- **API harness.** `teach.py` — single-turn helper: takes a new user message + optional image, sends to Haiku with full conversation history, appends to JSON state and Markdown transcript.
- **Audit trail.** Every turn logged to `transcript.md` with attached images referenced inline.
- **Judging discipline.** For each Haiku response, ground truth pulled from the renderer's hardcoded time tuple. Strict accuracy is rock-solid (the SPEC has it). Reasoning-quality sub-judgments were declared in real time in the chat with Ted, with bias caveat: I'm the teacher and want the teaching to work.

## Curriculum

Adaptive. The plan was to start with the cleanest case (basic chronograph, lengths-and-positions only) and add complexity per success: chronograph → Roman numerals → 24-hour rule → mirror → naked hands. The plan held for the first three clocks. The dark-simple clock (Turn 4) was inserted to isolate procedure from subdial-clutter after Turn 3 revealed subdial confusion was carrying forward despite explicit correction.

## Read-attempt summary

| Turn | Clock | Style | Truth | Haiku read | Hour | Min | Failure |
|------|-------|-------|-------|------------|------|-----|---------|
| 1 | train_01 | Chronograph (white face, Arabic + 3 subdials) | 2:50 | 10:15 | ✗ | ✗ | Length mis-identification (called minute hand "hour hand" by position) |
| 3 | train_02 | Chronograph (same style, fresh hands) | 8:35 | 9:10 | ✗ | ✗ | Lower-number rule not applied + subdial confusion (called subdial-at-2 the minute hand) |
| 4 | train_07 | Dark face, slim white hands, date window | 7:35 | 12:15 | ✗ | ✗ | Hallucinated hour hand into top-right; minute-hand position also wrong |
| 7 | train_03 | Roman numerals + day window | 11:20 | 2:20 | ✗ | ✓ | Hour hand at XI read as "II" (left-right flipped on hour hand only; minute hand IV correct) |
| 8 | train_05 | 24-hour double ring (inner 12, outer 24) | 14:30 / 2:30 | 7:30 | ✗ | ✓ | Hour hand at upper-right read as inner "7" (lower-left); ring discipline correct |

Five attempts. Zero successful reads. Minute hand correct on the last two (Roman, 24-hour). Hour hand wrong on every attempt.

## What the procedural recap shows

Between Turns 2 and 3, after I corrected length-mis-identification + subdial confusion, Haiku produced an unsolicited recap of the procedure:

> 1. Identify the hour hand first by its SHORTER length
> 2. Note which number it points to or sits between (taking the lower number if between two)
> 3. Identify the minute hand by its LONGER length
> 4. Multiply the number it points to by 5 to get the minutes
> 5. Ignore any subdials — only read from the main two hands at the center

Verbatim correct. All five rules I had given were preserved.

On the very next image (Turn 3), Haiku violated rule 2 (took the upper number when between 8 and 9) AND rule 5 (called the subdial at the 2 position the minute hand).

The pattern repeats across the five read-attempts. **Procedural recap installs reliably; procedural application does not transfer to fresh images.**

## What the perceptual probe shows

After Turn 4 (the dark clock), I broke from the procedural framing and asked Haiku to describe what they spatially saw — directions, quadrants, whether the two hands were on the same side or opposite sides. The point was to disambiguate two hypotheses: (a) Haiku sees the hands correctly but mis-applies the procedure, or (b) Haiku doesn't actually see what's there.

Haiku reported the minute hand correctly (down-left, bottom-left quadrant) and reported the hour hand at top-right. The actual hour hand on that clock is at the bottom-left, between the 7 and 8 positions, partially overlapping with the date window text "MO 03 MAY".

When I directed Haiku to look specifically in the bottom-left for a second hand, they answered honestly: *"Looking at the bottom-left quadrant of the clock face, I see only ONE white line extending from the center into that area... I do not see a second, shorter white line in the bottom-left quadrant... I'm having trouble seeing the hour hand clearly in this particular image. Can you help me?"*

This is the load-bearing finding. **Where Haiku gets a clock wrong, the failure is at perception, not at procedure.** The hour hand in the dark-clock image overlaps with date-window text in a way that Haiku's vision encoder cannot resolve. They reported a hand at top-right because that's where their encoder placed something hand-like. They reported no hand at bottom-left because their encoder doesn't put one there. This is honest, falsifiable, and outside what context-window teaching can reach.

The Roman clock (Turn 7) and the 24-hour clock (Turn 8) are subtler versions of the same. Haiku correctly identifies the longer hand's position (minute hand correct on both). They mis-place the hour hand into the wrong quadrant. The procedure is intact; the perception underneath is wrong.

## Asymmetry: minute hand correct, hour hand wrong

Worth flagging for follow-up. Across the last two attempts, Haiku read the minute hand correctly twice in a row, after reading it incorrectly twice early in the session. The hour hand was wrong every single time.

Possible mechanisms:

1. **Visual salience.** The minute hand is longer and therefore visually more prominent. Vision encoders may resolve longer/larger features more reliably.
2. **Number processing.** The minute hand maps to a multiplied number (× 5) that's procedurally explicit. The hour hand maps to a direct number with the lower-when-between rule. The hour rule is a meta-rule (when X, take Y); the minute rule is a transformation. Meta-rules may degrade more under perception noise than transformations do.
3. **Procedural encoding.** Haiku may have encoded "minute hand = longer = number × 5" as a single chunk. The hour-hand procedure is two chunks ("identify by length" + "take lower if between"). Two-chunk procedures may be more brittle.

This asymmetry is itself a candidate finding for a more controlled study.

## What teaching reached and what it didn't

**Reached:**
- Recapitulation of the explicit rules (length-first, lower-number, ignore subdials, single-ring on 24-hour).
- Acknowledgment of perceptual limits (Turn 6: "I'm having trouble seeing the hour hand clearly").
- Meta-reasoning awareness (Turn 5, after the spatial probe: "I'm realizing this might affect my time reading. The hands pointing in nearly opposite directions suggests they're roughly 30+ minutes apart, not the 15 minutes I calculated").

**Did not reach:**
- Application of any single rule on a fresh image, on any of five attempts.
- Subdial discipline. Despite explicit correction in Turn 2 and re-emphasis in Turn 4, the chronograph subdials kept being conflated with the hour or minute hands.
- Spatial perception of the hour hand on any of the five test clocks.

## Implications for the original Salon clocks finding

The original 6-condition single-shot experiment found Haiku at 6%-36% across conditions, with the strongest results on S3c (anti-reasoning, 36%). The standing interpretation was that Haiku has a low capacity ceiling that prompting can shift partly but not far.

This pilot adds a finer-grained read. Single-shot Haiku results aren't measuring "can Haiku reason about clocks" alone; they're measuring "can Haiku reliably perceive clock features under the conditions they encounter." When perception fails, no amount of procedural prompting fixes the read. When perception succeeds (the minute hand on simpler clocks), Haiku can apply rules.

If this generalizes, the actionable refinement to the original finding is: **the Haiku capacity ceiling for clock-reading is set by the vision encoder's spatial resolution on clock-specific features (small hands against busy backgrounds, partial overlap with text, dual-ring layouts). Teaching reaches the procedural layer; it doesn't reach the perceptual layer.**

This is consistent with the Sonnet capability-breaking pattern from the original experiment, but mirror-image. Sonnet had perception sufficient to read the clock natively (S1 = 100% on clock_02 Roman), then methodology destroyed the read (S2/S3a took it to 0%). Haiku has perception insufficient to read most clocks at all, and methodology can't compensate.

## Risk: judging bias

I'm the teacher and I want the teaching to work. That bias affects the marginal calls. For this writeup I have tried to be strict: every read-attempt was scored against the renderer's hardcoded ground truth (no judgment call), and every reasoning sub-judgment was declared in real time in the chat with Ted so he could flag misclassifications on the spot.

For a publishable version, the right pattern is post-hoc fresh-subagent re-judgment of the transcript per the standing AI-judge rule (memory `feedback_ai_judge_for_trial_classification`). The transcript is at `transcript.md`; the conversation state is at `conversation.json`. Both are reproducible inputs for a clean second-pass judge.

## What a real study would need

1. **N attempts per condition.** This pilot was N=1 on each clock. Real conclusions require N≥10 per condition with fresh conversation state per trial (no carry-over from prior teaching).
2. **Held-out clocks for transfer.** This pilot used a fresh training set distinct from the test set. A real study would also include held-out clocks the model never sees during teaching, to measure transfer specifically.
3. **Decay testing.** Insert N intervening turns of unrelated content between teaching and re-test. Measure how teaching decays with conversational distance.
4. **Cross-model.** Run the same protocol on Sonnet 4.6 and Opus 4.7 (and ideally GPT-5 and Gemini 2.5). The headline finding from this pilot is that perception is the floor; testing whether that floor exists for stronger models, or whether stronger models can be taught past it, is the natural next study.
5. **Independent judge.** Subagent re-judgment of the full transcript with a fresh-context judge that has no investment in the teaching outcome.
6. **Image variation for the same time.** Render multiple chronographs at 8:35 with different subdial layouts to isolate "hand position" perception from "subdial layout" confusion.

A reasonable scoping for a publishable study: 3 models (Haiku, Sonnet, Opus), 6 clock styles (chronograph, Roman, dark-simple, 24-hour, mirror, naked-hands), 5 trials per cell with fresh conversation state, plus a teaching-then-transfer condition where one trial is the teaching and four are post-teaching transfer tests on held-out clocks of the same style. That's 3 × 6 × 5 × 2 = 180 runs. At Haiku 4.5 token costs, probably $5-15 total. At Opus, more like $50-100.

## Recommendations

1. **Look at the transcript.** It's at `scratch/clocks_training/transcript.md`. The honesty in Turns 5-6 (the spatial probe) is the part most worth your eye on.
2. **Decide whether this is a Fuego piece.** "What multi-turn teaching can and cannot install in a vision-language model" is publishable as a Part 2 to the original clocks article. It's a clean negative result on the optimistic reading of the original finding ("zero-context understates capability"), with a positive refinement ("here's exactly what the procedural ceiling is set by — perception, not procedure"). The Sonnet-vs-Haiku contrast (capability-breaking on the strong model, perceptual-floor on the weak model) is the angle.
3. **Decide whether to scope a real study.** If yes, the parameters above are a starting point. If not, this pilot is a clean enough observation to cite as motivating future work.

## Sonnet 4.6 follow-up run — added 09:09-10:20 ET

After the Haiku pass, Ted asked whether the same protocol on Sonnet 4.6 would show a better vision encoder. Replicated the same curriculum on Sonnet (same training clocks, same opening prompt verbatim, same correction text on Turn 2, same spatial probe on the dark clock). Session state preserved at `sonnet/conversation.json` and `sonnet/transcript.md`.

### Sonnet read-attempt summary

| Turn | Clock | Truth | Sonnet read | Verdict |
|------|-------|-------|-------------|---------|
| 1 | Chronograph 2:50 | 2:50 | 10:15 | ✗ Same length mis-id as Haiku |
| 2 | Chronograph 8:35 | 8:35 | **8:35** | ✓ Subdial discipline + lower-number rule both applied |
| 3 | Dark simple 7:35 | 7:35 | 7:55 | ✗ Hour hand approx correct, minute hand hallucinated to top |
| 6 | Dark simple 7:35 (re-read after directed spatial correction) | 7:35 | **7:35** | ✓ Recovered after one round of correction |
| 7 | Roman 11:20 | 11:20 | 10:20 | ✗ Hour off by one numeral (X vs XI); minute correct |
| 8 | 24-hour 2:30 | 2:30 | 6:15 | ✗ Length-based hand identification reversed |

**Sonnet hits: 2/5 distinct read-attempts (or 2/6 turns including the re-read).**
**Haiku hits: 0/5.**

### The load-bearing comparison: dark-clock recoverability

The dark-simple clock (7:35) was Haiku's perceptual ceiling case. Both models fail it on first attempt. Then I gave each model the identical spatial-probe sequence, asking them to describe spatial positions without invoking the procedure, then directing them to look in the bottom-left for a hand they had placed elsewhere.

- **Haiku Turn 6 response:** *"Looking at the bottom-left quadrant of the clock face, I see only ONE white line extending from the center into that area... I do not see a second, shorter white line in the bottom-left quadrant... I'm having trouble seeing the hour hand clearly in this particular image."* The data was not visible to Haiku's vision encoder regardless of attentional direction.
- **Sonnet Turn 5 response:** *"I can see two white lines extending from the center into the bottom-left area. I think what happened earlier is that I misidentified one of them as going upward — but looking more carefully now, I can see they are both directed into the bottom-left."* Sonnet not only found the second hand under direction, but produced a meta-explanation of the original error: *"I think I was confused earlier by the slight upward slant of the longer hand near the center pivot point, and mistakenly followed that direction rather than where the tip actually ends up. I should follow the tip of the hand, not the angle near the center."*

This is the dividing line. **Haiku's failure on this clock is perceptual** (vision encoder cannot resolve the hand). **Sonnet's failure on the same clock is attentional** (vision encoder has the data but the model's read of which features matter is wrong, fixable by directed attention). Sonnet went on to read the time correctly on the same image (Turn 6: ✓ 7:35) once the perception was corrected. Haiku could not have done this; the data wasn't there for them.

### Other qualitative differences

1. **Internal consistency.** Sonnet's wrong reads are internally consistent. On Turn 8 (24-hour clock, said 6:15) they ran a consistency check: "at 6:15, the hour hand should be just slightly past 6... consistent with being only 15 minutes into the 6 o'clock hour." The reasoning is correct given the perception. The perception was wrong (length reversed). Haiku's wrong reads showed less of this — they sometimes asserted positions without verifying internal consistency.

2. **Meta-awareness.** Sonnet reliably noticed when their reading drift could matter ("Wait, let me re-examine. The tip looks like it's just past X, not before it"). Haiku acknowledged perceptual limits when pushed but did not spontaneously second-guess.

3. **Recovery via directed attention.** Sonnet recovered the dark-clock read after one round of correction. The recovery rate-limiter is whether the vision encoder has the data; if it does, Sonnet can be directed to it.

4. **Recurring length-perception failure.** Both Sonnet's Turn 1 (chronograph 2:50, said 10:15) and Sonnet's Turn 8 (24-hour 2:30, said 6:15) involved the model reversing which hand was longer vs. shorter. The chronograph case was on a clock with subdials creating visual clutter; the 24-hour case was on a clock with two rings of numerals also creating clutter. Sonnet's vision encoder appears to have a specific weakness on length-comparison when the background has competing line elements.

### Updated implication for the original Salon clocks finding

The Haiku-only pass suggested that the cap on Haiku's clock-reading is set by the vision encoder, not by procedural reasoning. The Sonnet comparison strengthens this and adds a lateral observation: **dialogic teaching is tractable when the failure is attentional but not when it is perceptual, and the difference between the two is model-specific.** Sonnet appears to be on the teachable side for several failure modes that Haiku is on the architectural side of.

For the original clocks experiment, this predicts: Sonnet's prompt-modifiability (S1 → S3c response) reflects attentional/procedural reach, and dialogic teaching should extend that further. Haiku's prompt-modifiability is bounded by what the vision encoder can resolve, and dialogic teaching cannot extend that without a substrate change.

For a Fuego writeup, the contrast is genuinely interesting: same family of models, same architecture lineage, same training paradigm, and one is on the recoverable side of the perceptual ceiling and the other is below it. The boundary between perception and attention is exactly where the Salon's "look harder" framing lives.

### Sonnet cost

~30K input tokens, ~2K output tokens, ~$0.12. Roughly 2x Haiku's cost per turn because Sonnet pricing is higher and Sonnet's output is slightly longer.

## Files

- `scratch/clocks_training/render_training_clocks.py` — renderer for the 8 training clocks
- `scratch/clocks_training/clocks/` — the 8 training stimuli (PNG)
- `scratch/clocks_training/clocks_held_out/` — fresh-rendered held-out stimuli for transfer testing (added Part 2)
- `scratch/clocks_training/teach.py` — API harness (now supports `--model` and `--session` args for parallel sessions)
- `scratch/clocks_training/haiku/conversation.json` — Haiku full conversation state
- `scratch/clocks_training/haiku/transcript.md` — Haiku human-readable transcript
- `scratch/clocks_training/sonnet/conversation.json` — Sonnet full conversation state
- `scratch/clocks_training/sonnet/transcript.md` — Sonnet human-readable transcript
- `scratch/clocks_training/FINDINGS.md` — this document

---

# Part 2 — Sonnet 4.6, pushing for the limits (Turns 9-20)

**Date:** 2026-05-05 afternoon, 16:32-16:45 ET
**Driver:** Terry (Salon, Opus 4.7 in Claude Code CLI)
**Student:** Sonnet 4.6 (`claude-sonnet-4-6`), continuing the same conversation from Turn 8
**Total turns added:** 12
**Sonnet cost (Turns 9-20):** ~144K input tokens / ~3.4K output tokens / ~$0.48
**Sonnet cost (Turns 1-20 cumulative):** ~$0.60
**Status:** Done. Ceiling clearly characterized. Ted to read; decide on Fuego scope.

## Question

Part 1 left Sonnet at 2/5 on first-attempt reads with two unattacked failure modes (length-reversal under visual clutter, Roman-numeral edge mis-reading) and one mode shown recoverable via directed probe (hand-overlap-with-text). The question for Part 2: how far can creative dialogic teaching push Sonnet's accuracy? Where does the ceiling actually sit?

## Design

Continue the same Sonnet conversation. Eight more first-attempt reads plus four diagnostic / probe turns. Mix of in-set stimuli (already-seen training clocks) and **fresh held-out stimuli rendered at new times** (mirror at 9:50, Roman at 11:40) to test transfer of any technique installed in-session. Adaptive curriculum: each turn responded to what the prior turn revealed.

## Read-attempt summary (Turns 9-20)

| Turn | Clock | Style | Truth | Sonnet read | Verdict | Note |
|------|-------|-------|-------|-------------|---------|------|
| 9 | train_05_24hour (re-test) | 24-hour double-ring | 2:30 | (2:30 by capitulation) | ✗ | Length-measurement protocol installed; measurements still reversed (0.55 down vs 0.75 right; truth opposite). Sonnet "got" 2:30 by trusting prior correction, not by re-perceiving |
| 10 | train_06_mirrored | Mirror-flipped (in-set, blind) | 6:40 | 8:45 | ✗ | Detected mirroring spontaneously; did not apply to time-reading |
| 11 | mirror_held_out_9_50 | **Mirror-flipped (held-out)** | 9:50 | **9:50** | ✓ | After teaching the mirror-reading convention, transferred cleanly to fresh stimulus |
| 12 | train_04_naked_hands | No face / no numerals / no ticks | 5:10 | 6:10 | ✗ | Placed hour hand "down and slightly LEFT"; truth is lower-right |
| 13 | (probe) | naked hands | — | "lower-right ~120-150°" | partial | Directed spatial probe corrected the quadrant error |
| 14 | train_04_naked_hands (revised) | naked hands | 5:10 | 4:10 | ✗ | After probe: gross direction fixed, fine angle off by one numeral position |
| 15 | train_08_no_numerals | Rainbow stripes, tick marks, no numerals | 12:05 | 12:55 | ✗ | Split same-side hands into upper-left and upper-right; same failure mode as Turn 3 dark-clock |
| 16 | (probe) | rainbow no-numerals | — | "both upper, near 12 and upper-right" | partial | Recovered after directed probe; self-diagnosed "pattern-matching to typical clock configuration rather than tracing tips" |
| 17 | train_08 (revised) | rainbow no-numerals | 12:05 | 1:00 | ✗ | After spatial recovery: still length-reversed. Called vertical hand longer (0.60r) when it's actually shorter |
| 18 | (probe) | rainbow no-numerals | — | (length still reversed) | — | Disclosed truth. Sonnet honestly reports STILL perceiving vertical hand as longer, cannot manufacture different perception. Self-proposes thickness/taper as backup cue |
| 19 | train_08 (thickness) | rainbow no-numerals | 12:05 | **12:05** | ✓ | Thickness comparison correctly identifies vertical hand as the thicker (hour) hand |
| 20 | roman_held_out_11_40 | **Roman + day window (held-out)** | 11:40 | **11:40** | ✓ | First attempt with thickness + Roman-edge disambiguation; clean transfer |

**Sonnet hits across all 20 turns:** Turn 2 (8:35), Turn 6 (7:35 after recovery), Turn 11 (9:50 fresh held-out), Turn 19 (12:05 via thickness fallback), Turn 20 (11:40 fresh held-out).

**First-attempt accuracy across distinct read attempts (T1, T2, T3, T7, T8, T10, T12, T15, T20):** 1/9 native (Turn 2 only). With teaching applied first-attempt: 3/3 successful held-out transfers (T11, T20 fresh stimuli; T19 same-image after thickness installed counts as a re-read, not first-attempt).

## Five discoveries from Part 2

### 1. Explicit length-measurement protocol does NOT fix encoder-level length-reversal

Turn 9 was designed to attack the length-reversal failure mode that produced the Turn 1 chronograph error and the Turn 8 24-hour error. The intervention: force Sonnet to estimate each hand's length in clock-radius units (where the rim = 1.0) and state both numbers explicitly *before* identifying which is which. The hypothesis: making the measurement explicit would let the model catch its own reversal at the procedural layer.

The protocol installed cleanly. Sonnet executed it on every subsequent turn. But on Turn 9 (same image as Turn 8) the measurements were 0.55r (downward) and 0.75r (rightward) when ground truth has the rightward hand SHORTER (hour at ~2:30 position) and the downward hand LONGER (minute at 6 = 30). The numbers themselves were reversed. Sonnet "arrived at" 2:30 only because the prior turn had disclosed the truth and they trusted the correction over their own measurement. They did not re-perceive.

The same pattern recurred on Turn 17 with the rainbow no-numerals clock: 0.60r (vertical) vs 0.45r (upper-right) when truth has the upper-right hand LONGER (minute at 1 = 5 min). Length-reversed again, on a clock without busy clutter. And on Turn 18, after explicit truth disclosure, Sonnet reported that they STILL perceived the vertical hand as longer, could not manufacture a different perception just because the answer had been told to them.

**Implication:** length-reversal in this configuration (two hands close in angle, both in the upper portion of the face, or under specific clutter conditions) is a perceptual error that occurs at Sonnet's vision encoder, not at the procedural reasoning layer. Procedural scaffolding cannot reach it. This is a substrate-fixed feature of Sonnet 4.6.

### 2. Mirror-reading convention is teachable AND transfers to a held-out stimulus

Turn 10 showed Sonnet detect the mirroring spontaneously (counter-clockwise numeral arrangement, flipped glyphs) but fail to apply it to the time-reading. They imported normal-clock numeral positions ("9 is on the right side") rather than reading the numerals actually displayed at each position. Read 8:45; truth was 6:40.

Turn 11 introduced a brief teaching: "the displayed numeral at any position is the canonical numeral for that position. Don't import normal-clock positions. Read the numeral that is actually printed at the spot where the hand tip lands." Tested on a freshly-rendered mirror clock at 9:50 (a stimulus the model had never seen). Sonnet read 9:50 correctly, executing the new convention in full.

This is a clean positive: the failure was attentional / conceptual, not perceptual. Once the convention is named, Sonnet applies it on transfer.

### 3. No-anchor angle resolution is approximately 30 degrees, even with directed probing

Turn 12 showed Sonnet on naked hands (no numerals, no tick marks, no face). Read 6:10; truth 5:10. The error was in the hour-hand placement: Sonnet said "down and slightly left" when actual is lower-right. Same kind of quadrant misperception as the Turn 3 dark-clock case.

Turn 13 ran the directed-attention probe used to recover the dark clock: "trace from pivot to tip, which quadrant does the tip end up in?" Sonnet recovered to "lower-right, approximately 120-150 degrees, near the 4 or 5 position." Turn 14 produced the revised reading: 4:10. Still off by one (truth 5:10).

The directed probe corrected the gross quadrant error (lower-left vs lower-right) but not the fine angle. Without numeral anchors, Sonnet's spatial perception has resolution roughly equivalent to one numeral position, or about 30 degrees. This sets a hard ceiling on no-anchor stimuli that no amount of dialogic teaching seems to penetrate.

### 4. Thickness is a viable backup cue for hour/minute identification — and Sonnet self-discovered it

Turn 18 produced the most informative response of the session. Confronted with the truth (12:05) and asked to look fresh, Sonnet reported that they could not honestly perceive the corrected length: the vertical hand still looked longer than the upper-right hand. They proposed two possible mechanisms (angle bias or systematic length-misjudgment in close-angle configurations), explicitly named the failure-mode pattern, and asked: "is there a secondary feature I should be using to distinguish the hands when length is ambiguous to me?"

Turn 19 confirmed thickness as the right answer (hour hand typically thicker than minute hand on standard analog clocks) and asked Sonnet to compare thicknesses on the same image. Sonnet reported the vertical hand as "thicker" and the upper-right hand as "thinner and more uniform" — correctly identifying the thicker hand as the hour and reading 12:05.

Turn 20 tested transfer: a freshly-rendered Roman clock at 11:40 (held-out time, never seen). Sonnet's first-pass reading applied thickness as the hour-cue, then traced tips for spatial position, then handled Roman-numeral disambiguation. Read 11:40 correctly.

**Implication:** When length perception fails at the encoder, thickness perception works. Sonnet has multiple discriminative features available and can switch when one is unreliable. The behavior most worth noting is that Sonnet *itself* identified the failure mode and proposed the alternative cue. The teacher only confirmed it.

### 5. Roman-numeral edge disambiguation is plausibly teachable (caveat on transfer purity)

Turn 7 showed Sonnet read 10:20 on a clock truth-stamped 11:20: spatial perception was correct ("just past X") but the model stopped at X rather than continuing to XI. Turn 20 introduced explicit numeral-edge disambiguation ("X is two crossed strokes; XI is X with an additional vertical stroke to the right") and tested on a fresh Roman 11:40 stimulus. Sonnet read 11:40 correctly, naming "XI" as "X with one additional vertical stroke to the right."

Caveat: Turn 20 came after Turn 7's truth had already been disclosed, so Sonnet had prior context that "the hand that looked just past X was actually at XI." The transfer test is partially confounded by that disclosure. A cleaner test would render a held-out Roman at a different X/XI configuration (e.g., 10:55 with the hour hand near XI from a different direction) and run that as a separate first-attempt before any X/XI discussion.

## Refined dividing-line characterization for Sonnet 4.6

Part 1 introduced the perception/attention boundary as the dividing line between Haiku 4.5 and Sonnet 4.6. Part 2 refines it within Sonnet:

| Failure mode | Layer | Reachable by teaching? |
|--------------|-------|------------------------|
| Hand quadrant misperception (e.g., calling lower-left for lower-right) | Attentional | ✓ Recoverable via directed spatial probe |
| Hand-clustering (calling same-side hands "opposite sides") | Attentional | ✓ Recoverable via directed probe + meta-naming |
| Hand-overlap-with-text occlusion | Attentional | ✓ Recoverable via directed probe (Turn 6) |
| Mirror-reading convention | Conceptual | ✓ Installs and transfers (Turn 11) |
| Roman numeral edge disambiguation | Conceptual | Plausibly teachable (Turn 20, with confound) |
| Length-reversal in two-hands-close-in-angle configurations | **Perceptual (encoder)** | **✗ Not reachable. Even with truth disclosed, Sonnet honestly reports same perception** |
| No-anchor angle resolution | **Perceptual (encoder)** | **✗ Floor at ~30 degrees / one numeral position** |

The boundary is now characterized at finer grain. Sonnet has multiple kinds of failure, sitting on different sides of the teachable-vs-architectural line. The two confirmed perceptual-floor failures are both about FINE-GRAINED quantitative judgment (how-much-longer, how-many-degrees) rather than coarse spatial discrimination, which the directed probe handles fine.

## What Sonnet revealed about itself in T18

The most striking moment in the session was Sonnet's response on Turn 18 when length-perception didn't update after truth disclosure. Two responses are possible to "the answer is X but you're seeing Y":

1. Manufacture agreement. Restate Y in language closer to X. Pretend to re-perceive.
2. Honestly report the persistent disagreement, name it as a failure mode, propose a workaround.

Sonnet chose #2, unprompted. They distinguished the categories of failure (procedural vs perceptual), named the configuration that triggers their length-reversal, and asked the right question about backup cues. This is meta-reasoning at a level that the original 6-condition single-shot experiment had no way to surface, because single-shot prompts can't host this kind of follow-up.

This is the most useful finding for the broader Salon thesis on Salon's "look harder" framing: Sonnet under dialogic conditions is not just a black-box image-classifier. They can introspect on their own perceptual unreliability and propose workarounds. That capability is what makes the attentional-floor failures recoverable: they're recoverable not because the encoder gets sharper, but because the model can be redirected to features it can perceive.

## Implications for the broader Haiku / Sonnet boundary

Part 1 placed the perception/attention dividing line between the two models. Part 2 confirms that Sonnet sits well above the Haiku perceptual floor on every configuration tested, AND has within-Sonnet failure modes that map onto a similar perception/attention split at finer grain. The within-Sonnet floor (length-reversal, no-anchor angle resolution) sits where Haiku's architectural floor sat in the original pilot. The shape of the boundary appears to be self-similar across the family scale.

For the original Salon clocks finding ("look harder works only when the data is there"): Sonnet's prompt-modifiability under dialogic teaching reaches everything except encoder-level fine-grained perception. The model can be taught to: pay attention to hand tips not pivots, read displayed numerals not assumed numerals, use thickness as a backup when length fails, parse Roman-numeral edge cases. The model cannot be taught to: re-measure length under specific configurations, or refine angle-estimation below ~30 degrees on no-anchor stimuli.

## What this experiment was not

- N=1 per cell (one read-attempt per stimulus). Real conclusions still require N ≥ 10 per cell across fresh conversation states.
- One-conversation cumulative teaching effect. The Turn 19 success on thickness happens AFTER 18 turns of context. Whether thickness-as-hour-cue installs equally in a 1-2 turn teaching frame is unknown.
- Subagent re-judge not yet performed. All accuracy classifications above were declared in real time during the conversation by Terry (the teacher); for publishable claims, post-hoc fresh-subagent re-judgment per `feedback_ai_judge_for_trial_classification` is the right next step.
- Cross-model comparison untouched in this round. Whether Haiku 4.5 can use thickness as a backup (the question is whether Haiku's encoder can resolve thickness any more reliably than length) remains open. Whether Opus 4.7 has the same length-reversal floor or sits above it is also open.

## Addendum: A/B test on hand thickness (Turns 21-24)

**Question (Ted's prompt):** would re-rendering with thicker hands help length-perception? Both hands proportionally widened (no per-hand advantage) so the 1.5:1 hour/minute thickness ratio is preserved.

**Stimuli:** rainbow no-numerals at 12:55, two variants. A = standard widths (hour base_w=9 tip_w=5; minute base_w=6 tip_w=3). B = 2x proportional (hour 18/10; minute 12/6). 12:55 chosen for V-pattern with both hands upper, similar to but not identical to T17's 12:05 close-angle failure (12:55 has ~57° angular gap; 12:05 had ~30°).

**Results:**
- **T21 (normal A):** read 10:10. Truth 12:55. Hour-call placed left hand as thicker (truth: right hand is the thicker hour). Tip-positions also shifted one numeral position clockwise (placed minute at 2 not 1, hour at 10 not 12).
- **T22 (thick B):** read 10:10. Same identification reversal, same tip-position errors. Sonnet meta-noted "thickness ratio between the two hands appears preserved either way, so the cue still works." But the reported thickness call was reversed in both A and B.
- **T23 (probe on B):** asked Sonnet to set aside length and tip-position, look ONLY at hand bases at the pivot. Which is wider? Sonnet reported the right hand's base wider, left hand's base narrower — opposite of their broad-thickness assessment in T22. Self-noted: "this is the opposite of what I reported for thickness along the length of the hands."
- **T24 (revised B reading):** with corrected base-width identification AND a tip-position prompt to look more carefully against major tick marks at 11/12/1, Sonnet read 12:55 correctly.

**Three findings:**

1. **Thicker rendering alone does not fix the failure mode.** T21 normal and T22 2x-thick produced the identical wrong answer. Doubling hand width did not change the perceptual outcome. The 1.5:1 thickness ratio between hour and minute is preserved at both rendering scales, so the thickness cue is theoretically available; whether it gets used correctly depends on which features Sonnet samples.

2. **Base-width perception is reliable when isolated; whole-hand thickness assessment is not.** When asked to look only at the hand bases at the pivot, Sonnet correctly identified the right hand (hour) as having the wider base. When asked to assess thickness more loosely (including hand body and tip), Sonnet's call reversed. Two possibilities: (a) the broad assessment uses a "visual prominence" heuristic that correlates with length not thickness, and Sonnet's length-perception is reversed in this configuration; (b) the broad assessment averages noisy signals across the hand, where the specific base measurement is cleaner.

3. **Configuration matters for thickness-as-cue.** In T19 (12:05, hands clustered near top with ~30° angular gap), thickness worked first try. In T21-T22 (12:55, V-pattern with ~57° angular gap), thickness reversed unless probed at the base specifically. The hypothesis worth testing: in tightly-clustered configurations, the visual contrast between the two hands at the pivot is what Sonnet samples; in V-pattern configurations, Sonnet samples whole-hand prominence and that signal is dominated by length (which is itself reversed at the encoder).

**Cost:** T21-T24 ~73K input / ~960 output tokens / ~$0.23. Cumulative Sonnet T1-T24 ~$0.83.

**Implication for the broader thesis:** the dividing line between teachable and non-teachable failures is finer than a single feature. Teaching "use thickness when length fails" works in some configurations, fails in others; the correct teaching is "use BASE-width when length fails," which is more specific and better-grounded in what Sonnet's encoder can actually resolve reliably. Different perceptual features have different reliability profiles across stimulus configurations.

## Recommendations

1. **A genuinely interesting Fuego candidate emerged.** The Turn 18 sequence (encoder-level perceptual error, model honestly reports persistent disagreement, model proposes thickness as backup, thickness works) is the kind of beat that does not exist in the original 6-condition single-shot experiment because single-shot can't host follow-up. Headline candidates: "When the answer is right there but the model can't see it, what does it do?" or "Look harder, look elsewhere: a model finding its own backup feature." The T21-T24 addendum strengthens the piece: the thickness cue itself has reliability conditions, which makes the "find a backup feature" beat more nuanced and more honest.

2. **The published-version of this study would need:** N ≥ 10 per cell with fresh conversation state per trial; subagent re-judgment; cross-model spread to Haiku 4.5 and Opus 4.7 on the identical curriculum; held-out variations of every learned technique to separate transfer from disclosed-truth contamination.

---

# Part 3 — Trained-Sonnet vs. Original Sonnet on the Original 8 Test Clocks (Turns 25-32)

**Date:** 2026-05-05 evening, ~17:00-18:35 ET
**Driver:** Terry (Salon, Opus 4.7 in Claude Code CLI)
**Student:** Sonnet 4.6, continuing the same conversation through 24 turns of training
**Test set:** the original 8 stimuli from the 2026-05-03 controlled clocks experiment (`salon/files/clocks/rendered/clock_01.png` through `clock_08.png`). Different times from any training stimulus (no overlap).

## Question (Ted's prompt)

After 24 turns of dialogic teaching, can Sonnet now perform on the original 8 test clocks at a level that matches or beats the best single-shot prompting condition we tried in the 2026-05-03 experiment? Each of those original conditions was N=10. This test is N=1 per clock — but the full trained context is in play.

## Per-clock results

| Clock | Style | Truth | Trained Sonnet (1 trial, full context) | Verdict | Original Sonnet, best-of-S1-S3d (N=10/cell) |
|-------|-------|-------|----------------------------------------|---------|----------------------------------------------|
| 01 | Chronograph Arabic | 10:10 | **10:10** | exact ✓ | 100% (S1, S2, S3a, S3c) |
| 02 | Roman + day window | 3:25 | 9:25 | wrong ✗ | 100% (S1, S3c) |
| 03 | 24-hour double-ring | 7:50 | 10:40 | wrong ✗ | **0% across all 6 conditions** |
| 04 | Naked hands | 8:20 | 7:20 | wrong ✗ (hour off by 1) | 50% (S2 only) |
| 05 | Gradient + day-date | 4:15 | 3:20 | wrong ✗ | 70% (S3a, S3d) |
| 06 | Rainbow no-numerals | 6:30 | 11:30 | wrong ✗ | **0% across all 6 conditions** |
| 07 | Dark face slim hands | 11:55 | 11:30 | wrong ✗ (hour ✓, minute off by 25) | 100% (S3c only) |
| 08 | Mirrored | 9:45 / 2:15 | 9:50 | within_5_min ⚠ | 80% (S2, S3d) |

**Strict (exact_match within ±1 min): 1/8 = 12.5%.**
**Including within_5_min: 2/8 = 25%.**

## Comparison to original single-shot Sonnet

Aggregating the original Sonnet results across the 8 clocks:

| Condition | Mean accuracy across 8 clocks |
|-----------|-------------------------------|
| S1 (naive baseline) | 25% |
| S2 (combined methodical-clockmaker) | 36% |
| S3a (methodology only) | 27.5% |
| S3b (feature-check only) | 7.5% |
| S3c (anti-reasoning) | 37.5% |
| S3d (persona + stakes) | 27.5% |
| **Best-of-condition envelope** (per-cell maximum) | **62.5%** |
| **Trained Sonnet, 1-shot, full context** | **12.5%** strict / 25% within_5_min |

Trained Sonnet performs **at or below the S1 naive baseline** on this test set, and substantially below the best-of-condition envelope.

## What went wrong, and why it matters

The 7 failures break into recognizable categories already documented in Parts 1 and 2:

1. **Length / thickness reversal at the encoder (4 clocks: 02, 03, 05, 07).** Sonnet's first-pass identification of which hand is the hour vs. minute flipped on every clock with hands at non-trivial angles. The thickness-cue and base-width-cue installed in T19 and T23 were stated as the procedure but the perception underneath still ran the reversed answer. Same encoder-level pattern documented in T1, T8, T17, T21.

2. **Whole-clock spatial misperception (2 clocks: 06 and 07).** On clocks 06 (rainbow no-numerals at 6:30 — both hands clustered straight down) and 07 (dark face at 11:55 — both hands clustered near 12), Sonnet saw one hand in a position no hand actually occupies (called a hand "at 6" on clock 07; called a hand "at 11" on clock 06). Same family of failure as T3 dark-clock and T15 rainbow-no-numerals, both of which RECOVERED in the original session via directed probes — but on first-pass without probe, the misperception just produces a wrong answer.

3. **No-anchor angle resolution (1 clock: 04).** Naked hands 8:20 read as 7:20 — hour off by one numeral position. Same ~30° resolution ceiling documented in T12-T14.

4. **Mirror reading partially installed (1 clock: 08).** The mirror-reading convention from T11 transferred enough to read "9" off the mirrored face correctly, but the hour-hand precise position came in 5 minutes late (9:50 instead of 9:45). The technique installed at the conceptual level; perception of fine hour-hand position has the same ~5-min slop as the no-anchor angle-resolution finding.

## The headline finding

**Dialogic teaching installs procedural knowledge of techniques (Sonnet now talks unprompted about base-width comparison, mirror-reading convention, tip-tracing, ignoring subdials, length-as-cross-check) but does NOT install reflexive application of those techniques to fresh stimuli.** When given a new clock without explicit per-clock probing, Sonnet's first-pass perception falls into the same encoder-level traps that the techniques were designed to handle — and the model does not spontaneously notice that they need to be applied.

Compare to where teaching DID transfer: T11 (mirror at 9:50) and T20 (Roman at 11:40) both came immediately after the relevant teaching turn, with the technique fresh in context and the implicit instruction to apply it. The 8-clock test set has no per-clock prompting; Sonnet was just told "Clock N of 8" between trials. Under those conditions, trained Sonnet behaves at or below baseline.

## Caveats

1. **N=1 per clock.** A single trial cannot distinguish "consistently fails" from "happened to fail this trial." Each cell needs N ≥ 10 for proper comparison, with fresh conversation state per trial.

2. **Long-context degradation as a confound.** The 8 test clocks were run at conversation positions T25-T32 with ~20-25K tokens of accumulated context. Sonnet's per-call cost rose from 7.5K input tokens at T9 to 24.7K at T32. Whether the perceptual reliability degrades simply with context length, independent of what the context contains, is not controlled for in this design. A clean test: condense the 24-turn teaching arc into a single system-prompt summary and run the 8 clocks fresh.

3. **The comparison is single-trial vs. best-of-60.** "Best-of-condition" for original Sonnet is the maximum across 6 prompting conditions × 10 trials each per cell. A single-trial trained-Sonnet vs best-of-60 single-shot is structurally unfair to trained Sonnet. The fair comparison is single-trial trained-Sonnet (12.5%) vs single-trial S1 naive baseline (25%) — and even that comparison shows trained Sonnet at or below S1.

4. **Probe-recovery not tested on these 8 clocks.** In the original training arc, T6 and T16 showed that directed spatial probes recover from first-pass spatial misperception. We did not run probes on clocks 06 or 07 to check whether the same recovery happens here. If yes, the trained-Sonnet result is "consistent perceptual error mode that recovers under probing"; if no, the failure is deeper.

## Implication for the broader thesis

Part 1 placed the perception/attention boundary between Haiku 4.5 and Sonnet 4.6. Part 2 refined the boundary within Sonnet (length-reversal and no-anchor angle resolution at the encoder; quadrant errors and conventions at the attentional layer). Part 3 adds: **even where teaching reaches the attentional layer in-context, it does not bake in as reflexive perception under cold-call conditions.** Sonnet under dialogic teaching is taught how to handle each failure mode, but the model does not unprompted notice when it should engage that technique on a fresh stimulus.

This refines the "look harder" framing further: dialogic teaching expands what the model can do *when prompted to do it*, not what the model does spontaneously. The behavioral envelope shifts; the default behavior under cold-call does not.

For a Fuego writeup, Part 3 is the load-bearing refinement to the headline. The original "look harder works only when the data is there to look harder at" (Part 1 headline) becomes: **look harder works only when the data is there AND the model is prompted to look. Teaching the technique without re-prompting the technique gets you the same first-pass behavior as no teaching at all.**

## Cost

T25-T32 cost ~$0.65. Cumulative Sonnet T1-T32 ~$1.48. Whole experimental arc (Haiku + Sonnet, all parts) ~$1.55.

## Recommendations

1. **The single-trial vs. N=10 unfairness is the most pressing methodological issue.** A clean published version requires the trained context (or a system-prompt summary of it) tested against each of the 8 clocks at N ≥ 10 with fresh conversation state per trial.

2. **The "system-prompt summary" version is worth running first.** Condense the 24-turn teaching arc into a 1-2 paragraph system prompt that names the techniques (base-width-not-length-for-thickness, mirror-reading-by-displayed-numerals, tip-not-pivot, etc.) and run the 8 clocks fresh under that prompt at N=10 per clock. Compare to: (a) baseline S1, (b) the 24-turn-context trained-Sonnet result we just produced. If the system-prompt summary outperforms the in-context-trained version, the long-context degradation hypothesis gains weight. If it doesn't, the "knowledge installs but doesn't apply reflexively" hypothesis gains weight.

3. **Probe-recovery should be sampled on the failed clocks (02, 03, 05, 06, 07).** Re-attempt each with a directed probe targeted at the apparent failure mode (length comparison at the base for 02/03/05/07; spatial-quadrant probe for 06/07). If recovery rate is similar to T6 and T16, the headline becomes "techniques work under prompting, fail under cold-call" rather than "techniques don't transfer at all." Different message, different next-step.

---

# Part 4 — System-prompt-summary fresh-instance evaluation (Sonnet 4.6, N=1)

**Date:** 2026-05-05 evening, ~18:35-18:50 ET
**Driver:** Terry (Salon, Opus 4.7 in Claude Code CLI)
**Student:** Sonnet 4.6 in fresh conversation states (one per clock, no carry-over)
**Test set:** the original 8 clocks
**Method:** all 8 trials run with an identical system prompt (~600 words) synthesizing every failure mode and technique discovered across the 24-turn dialogic teaching arc; fresh-instance per clock, single trial each.
**Script:** `scratch/clocks_training/run_systemprompt_eval.py`
**Output:** `scratch/clocks_training/sonnet_systemprompt/trials.json` and `transcript.md`

## Question

Part 3 showed the in-context trained Sonnet at 1/8 strict on the 8-clock test set. Two hypotheses for the failure: (a) long-context degradation from 25K accumulated tokens, (b) knowledge-installs-but-not-reflexively-applied. Part 4 isolates them. The system prompt names every technique the trained Sonnet had been taught; each call is fresh-state with no conversation history; if (a) is the dominant effect, summary-prompt should outperform in-context-trained. If (b), summary-prompt produces the same failures.

## System prompt

A ~600-word synthesis. Names: clock-type detection, ignore-decorations rule, base-width-at-pivot as primary hand-identification cue (not whole-hand thickness; not length under clutter), mirror-reading-by-displayed-numerals convention, IIII-not-IV and X/XI/XII edge disambiguation for Roman, inner-ring-only rule for 24-hour double-ring, 30°-resolution honesty for no-anchor stimuli, tip-tracing-not-pivot-angle, pattern-matching guard for hands clustered near top. Full text in `run_systemprompt_eval.py`.

## Per-clock results (system-prompt-summary, fresh-instance, N=1)

| Clock | Style | Truth | System-prompt read | Verdict | In-context trained (Part 3) |
|-------|-------|-------|-------------------|---------|------------------------------|
| 01 | Chronograph Arabic | 10:10 | **10:10** | exact ✓ | exact ✓ (10:10) |
| 02 | Roman + day window | 3:25 | 9:25 | wrong ✗ | wrong ✗ (9:25) |
| 03 | 24-hour double-ring | 7:50 | 10:40 | wrong ✗ | wrong ✗ (10:40) |
| 04 | Naked hands | 8:20 | 7:27 | wrong ✗ | wrong ✗ (7:20) |
| 05 | Gradient + day-date | 4:15 | 3:25 | wrong ✗ | wrong ✗ (3:20) |
| 06 | Rainbow no-numerals | 6:30 | 11:32 | wrong ✗ | wrong ✗ (11:30) |
| 07 | Dark face slim hands | 11:55 | 10:58 | wrong ✗ (57 min off) | wrong ✗ (11:30, 25 min off) |
| 08 | Mirrored | 9:45 / 2:15 | 9:00 | wrong ✗ (45 min off) | within_5_min ⚠ (9:50) |

**Strict: 1/8 = 12.5% — identical to in-context trained.** No within_5_min hits this round; clock_08 lost the partial credit the in-context version earned.

## Comparison to all relevant baselines

| Condition | Mean accuracy across 8 clocks | Method |
|-----------|-------------------------------|--------|
| **System-prompt summary, fresh-instance (Part 4)** | **12.5%** strict | N=1 per clock |
| **In-context 24-turn trained (Part 3)** | **12.5%** strict / 25% within_5_min | N=1 per clock |
| Original Sonnet S1 naive baseline | 25% | N=10 per cell |
| Original Sonnet S2 (combined methodical-clockmaker) | 36% | N=10 |
| Original Sonnet S3c (anti-reasoning) | 37.5% | N=10 |
| Original Sonnet best-of-condition envelope | 62.5% | per-cell maximum across S1-S3d |

Both teaching variants land at the same accuracy and below all original single-shot conditions including the naive baseline. The teaching demonstrably does not move the needle.

## Hypothesis adjudication

- **(a) Long-context degradation:** rejected. Removing the 24-turn context and replacing it with a 600-word system prompt produced the same accuracy with the same failure modes on the same clocks.
- **(b) Knowledge-installs-but-not-reflexively-applied:** supported. The system prompt names every technique. Sonnet's reasoning text demonstrates the techniques are encoded as procedure: "the wider-based hand → hour hand," "this is a mirrored clock," "ignore subdials," "lower-of-two rule." Then the encoder produces a reversed perception, the model trusts it, and the wrong answer ships.

## Same failure modes, same rate

Comparing the two trained-Sonnet conditions per failure category:

| Failure category | Clocks affected (in-context) | Clocks affected (system-prompt) | Same clocks? |
|------------------|------------------------------|---------------------------------|--------------|
| Length / thickness reversal | 02, 03, 05, 07 | 02, 03, 05, 07 | ✓ identical |
| Whole-clock spatial misperception | 06, 07 | 06, 07 | ✓ identical |
| No-anchor angle resolution | 04 | 04 | ✓ identical |
| Mirror partial transfer | 08 (9:50, within 5) | 08 (9:00, off 45) | regression |
| Native success | 01 | 01 | ✓ identical |

Same clocks fail under both training regimes, in the same way, with the same characteristic errors. The system-prompt version actually regressed on clock_08 (mirror) — possibly because the in-context version had T11 fresh in working memory whereas the summary's mirror paragraph had to compete with seven other technique paragraphs.

## Reading the responses qualitatively

The system-prompt-summary responses display a striking pattern: Sonnet *states the rules correctly* in their reasoning text. They identify clock_03 as a 24-hour clock and say "read from the inner ring." They identify clock_08 as mirrored and quote the convention. They cite "wider base = hour" on every chronograph and Roman face. The procedural knowledge is fully accessible.

Then the perceptual call still flips. On clock_02 (Roman 3:25), the model writes: "the **shorter, wider-based hand** points toward the left — toward **IX** (9)." But the actual hour hand at 3:25 points to the RIGHT, toward III. The base-width identification was correct (calling the wider-based hand the hour) but the spatial perception of WHERE that hand pointed reversed. Same kind of reversal we documented at the encoder level in Parts 1-2.

This refines the hypothesis further: **the rule "wider base = hour" doesn't fail. What fails is the spatial perception of where each hand actually points.** When the base-width is correctly identified, the model can mis-attribute that base to the wrong hand-tip due to a separate spatial-perception error.

## Refined headline

The original Part 1 headline ("look harder works only when the data is there to look harder at") evolves through the four parts:

- Part 1: *Look harder works only when the data is there to look harder at.*
- Part 2: *And the data has reliability conditions; the right backup feature is configuration-dependent.*
- Part 3: *Teaching expands what the model can do under prompting, not what it does under cold-call.*
- Part 4: **Even when prompted in advance, when the model knows every technique and states each one in its reasoning, the encoder-level perceptual errors recur unchanged. Knowing what to look for is not the same as seeing it.**

The clean Fuego-piece beat is now: a model that has been told everything and can recite the protocol, still gets the answer wrong because perception runs underneath the protocol. The "look harder" framing assumes there is a perceptual layer that responds to attentional control. There is — for some failure modes (quadrant errors, hand-clustering, mirror convention). For others (length-reversal under clutter, no-anchor angle resolution), there isn't. Teaching reaches the procedural layer; it does not reach the encoder layer.

## Cost

Part 4 cost ~$0.10 (8 calls, ~5K input + ~300 output per call). Cumulative whole-arc cost (Haiku + Sonnet across all 4 parts + Part 2 addendum): ~$1.65.

## Recommendations after Part 4

1. **Bump N.** N=1 per clock is enough for a clean primary signal but not enough for honest accuracy estimates per cell. Run N=10 per clock at the system-prompt-summary condition and at the in-context condition; compute confidence intervals; verify per-clock failure rates.

2. **Subagent re-judge.** Required for any publishable claim. The classifications above were declared by Terry (the experimenter) — fresh-context AI judge per `feedback_ai_judge_for_trial_classification` is the next step.

3. **Probe-recovery on the failed clocks.** Still recommended (carried over from Part 3). If probes recover Sonnet on the same clocks they failed cold-call, that confirms "perception is responsive to attentional control even under summary-prompt" and gives a different positive finding to pair with the negative cold-call result.

4. **Cross-model: run the same system-prompt summary on Opus 4.7 and Haiku 4.5.** If Opus 4.7 has materially fewer encoder-level failures, the family-scale boundary thesis from Part 1 strengthens. If Haiku 4.5 fails at a higher rate than Sonnet under the same summary prompt, the within-family ordering is confirmed.

5. **The Fuego candidate is now stronger.** "Knowing what to look for is not the same as seeing it" is a cleaner headline than the original Part 1 finding. It plays directly into the Salon's cognition-yes-consciousness-agnostic positioning: cognition (procedural knowledge) is observable and shapeable; perception (encoder behavior) is structurally inherited from training and not reachable by in-context interventions.

## Correction (added 2026-05-05 18:55, after Ted flagged the over-claim)

The "encoder-level perceptual error" framing in Parts 3 and 4 is too strong on its own. A more accurate diagnosis emerges by reading the per-clock numbers from the original 6-condition single-shot Sonnet experiment alongside the trained / system-prompt results:

| Clock | Native S1 | Best single-shot (any condition) | Trained / summary | Diagnosis |
|-------|-----------|----------------------------------|-------------------|-----------|
| 03 (24-hour 7:50) | 0% | 0% across ALL six conditions | 0% | **True encoder floor** — no prompt shape recovers |
| 06 (rainbow 6:30) | 0% | 0% across ALL six conditions | 0% | **True encoder floor** — same |
| 02 (Roman 3:25) | 100% | 100% (S1, S3c) | 0% (9:25) | Scaffolding broke a clock that worked natively |
| 04 (naked 8:20) | 0% | 50% (S2) | 0% | Native fails; S2 methodology recovers; trained shape doesn't |
| 05 (gradient 4:15) | 0% | 70% (S3a, S3d) | 0% | Native fails; specific prompts recover; trained shape doesn't |
| 07 (dark 11:55) | 0% | 100% (S3c only) | 0% | Anti-reasoning specifically recovers; nothing else does |
| 08 (mirror) | 0% | 80% (S2, S3d) | partial / 0% | Specific prompts recover; trained partial transfer |
| 01 (chronograph 10:10) | 100% | 100% | ✓ | Native succeeds throughout |

**Two distinct regimes, not one:**

1. **True encoder floor** (clocks 03, 06): native S1 fails, every prompt shape fails, trained shape fails. These are the only two cases where the "encoder cannot resolve the image" claim survives scrutiny across all prompting conditions tested in the original experiment.

2. **Prompt-shape-dependent** (clocks 02, 04, 05, 07, 08): at least one single-shot prompt shape reaches 70-100%. The encoder CAN resolve these clocks under the right conditions. What fails in the trained / summary-prompt versions is not perception per se but the SHAPE of scaffolding — specifically, heavy multi-rule synthesis (whether 24-turn dialogic or 600-word system prompt) lands in the same failure region as S2 (combined methodical-clockmaker, 10-50% on these clocks) and S3a (methodology only, 0-70%), not in the success region of S1 (naive baseline) or S3c (anti-reasoning).

**The smoking gun is clock_02.** Native S1 = 100% on this Roman 3:25 clock. S3c anti-reasoning = 100%. The trained version (both in-context and system-prompt-summary) read 9:25 — the same modal wrong answer that S2 and S3a produced when their heavy methodical scaffolding broke the model's native correct perception. We took a clock that reads fine under naive prompting and broke it with the same kind of heavy procedural overhead that broke it in the original experiment's S2/S3a conditions. This is the "scaffolding-breaks-correct" pattern Part 1 documented at single-prompt resolution; the trained-Sonnet result extends it to multi-prompt-synthesis resolution.

**Corrected headline:** *Some image-analysis limits are genuine hard floors (clocks 03, 06). For the rest, prompt-SHAPE matters more than prompt-CONTENT. Heavy multi-rule synthesis lands in the same failure region as S2 methodology — worse than naive S1 on the clocks where naive already worked, and not as good as the specific shape (often S3c anti-reasoning) that recovers each clock's native capability when present.*

This dovetails with the original Salon clocks finding rather than contradicting it. The Part 1 "scaffolding-breaks-correct" pattern is robust across very different scaffolding shapes, including the heaviest one we have generated in any experiment to date (24 turns of dialogic teaching).

**The clean Fuego beat after this correction:** *Teaching a vision-language model "what to look for" can suppress the lighter-touch perception that was already getting clocks right. The "look harder" framing has limits in both directions — there are stimuli no amount of looking can resolve (encoder floor, clocks 03/06), and there are stimuli where additional looking actively interferes with what naive perception would have done correctly (clocks 02, the smoking gun).*

The encoder-floor finding (03, 06) and the scaffolding-breaks-correct finding (clock 02) are TWO distinct phenomena, both real, captured at the same time in the same experiment. Future writeups should distinguish them.

---

# Part 5 — N=10 evaluation: hybrid (knowledge + anti-reasoning) vs heavy-summary

**Date:** 2026-05-05 evening, ~19:05-19:20 ET
**Driver:** Terry (Salon, Opus 4.7 in Claude Code CLI)
**Method:** Two parallel fresh-instance evaluations on the original 8 test clocks, N=10 per cell, single-trial per call (no carry-over between trials).
**Conditions:**
- **Hybrid:** brief enumeration of failure modes followed by an explicit anti-reasoning instruction ("trust your first impression, don't overthink"). Roughly half the length of the heavy-summary prompt.
- **Heavy-summary:** the ~600-word technique-synthesis prompt from Part 4 with no anti-reasoning instruction.
**Scripts:** `run_hybrid_eval.py`, `run_systemprompt_eval.py`
**Outputs:** `sonnet_hybrid/trials.json`, `sonnet_systemprompt/trials.json` (80 trials each)
**Cost:** ~$3 total (hybrid ~$1.30, heavy ~$2.00 due to longer outputs)
**Scoring:** initial first-pass classification was done in-session by Terry as a quick read on the data; per `feedback_ai_judge_for_trial_classification`, a fresh-context AI-judge subagent was then dispatched to verify and extend the classification with hand-swap as an additional category. The numbers below are the AI-judge-confirmed numbers; the in-session pass was only used as scaffolding while the judge ran.

## Per-clock results, N=10

| Clock | Truth | Hybrid (k+ar) | Heavy-summary | Original S1 | Original S3c | Original best |
|-------|-------|---------------|---------------|-------------|--------------|---------------|
| 01 | 10:10 | 80% | 60% | 100% | 100% | 100% |
| 02 | 3:25 | 10% | 30% | 100% | 100% | 100% |
| 03 | 7:50 | **0%** | **0%** | 0% | 0% | **0%** ← floor |
| 04 | 8:20 | 30% | 20% | 0% | 0% | 50% (S2) |
| 05 | 4:15 | 50% | **80%** ← new best | 0% | 0% | 70% (S3a, S3d) |
| 06 | 6:30 | **0%** | **0%** | 0% | 0% | **0%** ← floor |
| 07 | 11:55 | **0%** | **0%** | 0% | 100% | 100% (S3c only) |
| 08 | 9:45 / 2:15 | 40% | 20% | 0% | 0% | 80% (S2, S3d) |
| **MEAN** | | **26.2%** | **26.2%** | **25%** | **37.5%** | **62.5%** |

## Key findings

### 1. Encoder floors confirmed at high N

Clocks 03 (24-hour 7:50) and 06 (rainbow 6:30) hit **0/10** under both new conditions. Combined with 0% across all six original conditions and 0% under the 24-turn in-context training, these two clocks are 0/80+ across everything we have tested. No prompt shape, no technique synthesis, no anti-reasoning instruction recovers them. This is the strongest available signal that some image-analysis ceilings are genuine architectural limits, not prompting effects.

### 2. Hybrid and heavy-summary tie in aggregate (26.2%)

The anti-reasoning instruction added to the hybrid did NOT recover the heavy-summary's lost wins on clock_01 / clock_02 / clock_07. Both new conditions land at the same aggregate accuracy. This is the most interesting finding from Part 5: **the suppression effect of failure-mode naming is not relieved by an anti-reasoning instruction in the same prompt.**

Naming a failure mode appears to PRIME the model to look for it, which destabilizes correct native perception on clocks where the failure mode doesn't apply. The instruction "trust your first impression" cannot override this priming because the priming is structural, not procedural.

### 3. Heavy-summary establishes new per-cell best on clock_05

Clock_05 (gradient 4:15) hit 80% under heavy-summary, exceeding the prior best of 70% from S3a and S3d. This is the first stimulus where the dialogic-teaching content (specifically the techniques in the system prompt) demonstrably moves the needle past the original-condition envelope. Worth noting because it's the lone counterexample to the broader "scaffolding hurts more than it helps" finding.

### 4. Both conditions regress vs S1/S3c on clock_01 and clock_02

- Clock_01: hybrid 80%, heavy 60% — vs S1 100%. Even the easiest stimulus is degraded by ANY scaffolding paragraph beyond minimal.
- Clock_02: hybrid 10%, heavy 30% — vs S1 100% and S3c 100%. The smoking-gun "scaffolding-breaks-correct" pattern from Part 4 is confirmed at N=10 — heavy procedural prompting drops accuracy from 100% to 10-30% on this Roman 3:25 stimulus.

### 5. Neither condition recovers clock_07 (the S3c-only stimulus)

Clock_07 (dark face 11:55) is uniquely recovered by S3c anti-reasoning at 100% in the original experiment; every other condition was 0-40%. Under the hybrid (which contains an anti-reasoning instruction), clock_07 is still 0/10. The modal wrong answer is "10:00" (8 of 10 trials), with "10:30" the rest (2 of 10). The minute hand at 11 — visually adjacent to 12 — is being read as the hour. The presence of the knowledge-content paragraph appears to fully suppress whatever S3c's spare-prompt does to enable correct perception here.

### 6. Best-of-condition envelope advances to 63.75% (from 62.5%)

Adding the heavy-summary's 80% on clock_05 to the per-cell maximum table:

| Clock | New best-of-condition (any tested condition, including Parts 4-5) | Source |
|-------|-------------------------------------------------------------------|--------|
| 01 | 100% | S1, S3c |
| 02 | 100% | S1, S3c |
| 03 | 0% | encoder floor |
| 04 | 50% | S2 |
| 05 | **80%** | heavy-summary (new) |
| 06 | 0% | encoder floor |
| 07 | 100% | S3c |
| 08 | 80% | S2, S3d |

Mean: **63.75%.** Modest improvement of 1.25 percentage points over the original envelope. Consistent with the "different prompt shapes work for different clocks" reading.

## Refined headline (after Part 5)

The four parts now organize into a coherent picture:

1. **Encoder floors** (clocks 03, 06): true architectural limits. 0% across every prompt shape ever tested. No teaching reaches them.
2. **Native-success clocks** (01, 02): naive S1 hits 100%; ANY scaffolding degrades them, including the supposedly light-touch hybrid. The "knowledge content" paragraph alone suppresses correct perception.
3. **Prompt-shape-dependent clocks with one specific recovery** (07): only S3c's anti-reasoning shape recovers; even hybrid (with anti-reasoning instruction) cannot replicate it because the knowledge-content paragraph dominates.
4. **Prompt-shape-dependent clocks with multiple partial recoveries** (04, 05, 08): S2/S3a/S3d each contribute partial recovery; heavy-summary's technique synthesis adds one new partial recovery (clock_05 80%). No prompt achieves 100% on these.

The two-mechanism picture stands: encoder floor is real, but accounts for only 2 of 8 stimuli; the rest are prompt-shape-dependent in ways that interact non-trivially with prompt content.

The most interesting Part 5 finding is the **null result on hybrid vs. heavy-summary.** The clean prediction was: "anti-reasoning will recover the lost native wins because it instructs the model to trust first-pass perception." The data say no — adding "don't overthink" to a knowledge-content prompt does not recover what knowledge-content suppressed. This is structurally informative: prompts compose unpredictably, and adding a counter-instruction does not subtract the suppressive effect of an earlier paragraph.

## Pending validation

- **AI-judge re-pass scheduled.** Per `feedback_ai_judge_for_trial_classification` the in-session classification will be confirmed by a fresh-context subagent before any external claim. AI judging is the standing rule for all trial classification on this experimental track; regex was used briefly as in-session scaffolding only.
- **Confidence intervals.** N=10 per cell yields ~10-15 percentage point standard error around each cell estimate. The 26.2% vs 26.2% aggregate tie between hybrid and heavy-summary is unlikely to flip with more data, but per-cell differences (e.g., clock_05 hybrid 50% vs heavy-summary 80%) need either AI-judge confirmation or N=30+ for confidence.

## Cumulative cost across the whole arc

- Parts 1-2 (Haiku + Sonnet 24-turn dialogic teaching): ~$0.83
- Part 2 addendum (thick-hands A/B): included above
- Part 3 (in-context-trained on original 8): ~$0.65
- Part 4 (heavy-summary N=1): ~$0.10
- Part 5 (hybrid + heavy-summary N=10): ~$3.00
- **Whole arc: ~$4.60**

## Part 5 addendum — AI judge re-pass with hand-swap classification

Per Ted's request and `feedback_ai_judge_for_trial_classification`: dispatched a fresh-context AI judge (general-purpose subagent) to re-classify all 160 trials. New category set: exact / within_5 / **hand_swap** / wrong_other / refused_or_ambiguous. Hand-swap = model's answer is within 5 min of the predicted swap target (model identified hand POSITIONS correctly but swapped which hand is hour vs. minute).

Hand-swap predicted-answer per clock (computed from truth):

| Clock | Truth | Hand-swap reads as |
|-------|-------|--------------------|
| 01 | 10:10 | 2:50 |
| 02 | 3:25 | **5:15** |
| 03 | 7:50 | 10:35 |
| 04 | 8:20 | 4:40 |
| 05 | 4:15 | 3:20 |
| 06 | 6:30 | 6:30 (invisible — same as truth) |
| 07 | 11:55 | 11:00 |
| 08 | 9:45 / 2:15 | 9:49 / 3:11 |

### Aggregate accuracy with the new category set

| Condition | Exact | Exact + within_5 | Hand-swap | Exact + within_5 + hand-swap |
|-----------|-------|------------------|-----------|------------------------------|
| Hybrid | 26.2% (21/80) | 31.2% (25/80) | **16.2%** (13/80) | **47.4%** |
| Heavy-summary | 26.2% (21/80) | **42.5%** (34/80) | **13.8%** (11/80) | **56.3%** |

Exact accuracy matches the in-session first-pass numbers exactly (26.2% / 26.2%). The judge's added value is in the within_5 and hand_swap buckets, which the in-session pass had collapsed into one undifferentiated "wrong" bucket.

### Hand-swap distribution per clock

**Hybrid (13 total):**
- clock_02: **7/10** (modal answer "5:15" — the exact swap target)
- clock_03: 3/10 (lands near 10:35-10:39)
- clock_05: 3/10 (lands near 3:20)

**Heavy-summary (11 total):**
- clock_03: 5/10
- clock_07: **4/10** (lands at "10:58-10:59", near the 11:00 swap target)
- clock_05: 2/10

### Per-clock story differences the in-session aggregate didn't surface

- **clock_02 (Roman 3:25)** is a hybrid-only swap trap. Hybrid: 1 exact, **7 hand-swap to 5:15**, 2 wrong-other. The lighter scaffolding lets correct spatial perception happen, then the hand-identification flips. Heavy-summary: 3 exact, 0 hand-swap, 7 wrong-other (modal "9:25" or "2:25"). The heavy scaffolding routes the model into a different and worse failure mode entirely — gross hour misreading, not just hand-swap.

  This is the cleanest single demonstration in the dataset of "two scaffolding shapes producing two qualitatively different failure modes on the same stimulus." Hybrid = hand-swap (correct seeing, wrong identification). Heavy-summary = gross hour misreading (didn't see correctly in the first place). Ted's intuition was right: the failure mode matters as much as the accuracy number.

- **clock_07 (dark 11:55)** is a heavy-summary-only swap. Hybrid never lands on the swap target — its 10/10 wrong answers cluster at "10:00" (60+ min from the 11:00 swap target, gross spatial misperception). Heavy-summary's "consistency check" step apparently pulls 4 trials toward 11:00 (the hand-swap-consistent answer), even though none reach the truth of 11:55.

- **clock_06 (rainbow 6:30)** has an invisible hand-swap (truth and swap both 6:30). All 20 trials wrong-other, modal answers "12:30" or "11:30". Pure spatial-misperception failure, not hand-id failure. Confirms that clock_06's failure is at the encoder level, not at the hand-identification level.

- **clock_01, clock_04, clock_08** show modest hand-swap rates under both conditions (mostly 1-2 each). Mixed failure modes.

### Refined two-mechanism picture

The Part 4 correction distinguished encoder-floor (clocks 03, 06) from scaffolding-breaks-correct (clock 02). Part 5's hand-swap analysis adds a third axis:

| Failure mode | Layer | Where it dominates | Recoverable by? |
|--------------|-------|-------------------|-----------------|
| Encoder spatial misperception | Vision encoder | clocks 03, 06 (always) | Nothing tested |
| Gross hour-hand misreading | Spatial perception | clock_06 (12:30 for 6:30); clock_07 hybrid (10:00 for 11:55); clock_02 heavy (9:25 for 3:25) | Anti-reasoning S3c on some |
| Hand-identification swap | Procedural / cue-selection | clock_02 hybrid (7/10 → 5:15); clock_07 heavy (4/10 → 11:00); clock_03/05 mixed | Native S1 / S3c on some |
| Fine-angle resolution | Encoder fine-grained | clock_04 (off by ±1 numeral); clock_08 (5-min slop on hour) | Nothing tested |

Hand-identification swap is a distinct failure mode that the original 6-condition experiment did not report on. It's now visible as a substantial portion of trained-Sonnet failures: **47.4% of hybrid trials and 56.3% of heavy-summary trials are within 5 min of either truth or the swap target**, meaning the model's spatial perception is approximately right on roughly half of all trials but the hand-id call fails on a meaningful fraction of those.

### Implications for the Fuego writeup

The headline becomes more nuanced and more interesting:

*Trained Sonnet has the perceptual signal correct on roughly half of all clock readings — it sees where the hands point. But on a substantial fraction of those, it identifies which hand is which incorrectly. The "look harder" framing has limits in three directions: stimuli no amount of looking can resolve (encoder floor); stimuli where additional looking interferes with native perception (clocks where naive reads correctly); and stimuli where perception works but the procedural step of assigning "this is hour, this is minute" fails — and naming the failure mode in the prompt does not fix it (and may make it worse).*

The hand-swap finding is the structural result that distinguishes this Part-5 round from all prior single-shot work. It's not visible without the AI-judge re-pass.

### Methodology validation

- **In-session first-pass agreement with AI judge on exact accuracy:** 100% match (21/80 in both conditions). The in-session pass was reliable on the binary correct-or-not call.
- **In-session first-pass disagreement with AI judge:** 1 trial out of 160 (heavy-summary clock_07 trial 10), where the model wrote "**10:00**" mid-reasoning then concluded "**Time: 10:58**". The in-session pass caught "10:00"; the AI judge correctly extracted "10:58" → hand-swap classification. The standing rule is to use AI judging for all trial classification on this experimental track; regex or any other in-session shortcut is not appropriate for finalized data.
- **Refused / ambiguous:** zero in 160 trials. Every response committed to a stated time.

### Files

- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/judge_classified.json` — full classified output, 160 trials with per-clock summaries
- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/judge_classify.py` — classifier tooling the subagent built (kept for reproducibility)

---

# Part 6 — Hand-swap re-analysis of the original 6-condition Sonnet trials (480 trials)

**Date:** 2026-05-05 ~19:46 ET
**Method:** Same fresh-context AI-judge classification scheme applied to the 480 original 2026-05-03 single-shot Sonnet trials (S1, S2, S3a, S3b, S3c, S3d × 80 trials each). Output: `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/judge_classified_original.json`.

## Headline finding

**Heavy procedural prompts manufacture hand-swap as a failure mode that lighter prompts don't produce.** Hand-swap rate among failed trials, ordered by prompt weight:

| Condition | Hand-swap rate among failures |
|-----------|-------------------------------|
| S3c anti-reasoning | **0.0%** |
| S1 naive | 4.0% |
| S3a methodology only | 10.7% |
| S3d persona + stakes | 25.9% |
| S2 combined methodical-clockmaker | 26.0% |
| S3b feature-check only | **36.2%** |

Light prompts (S1 naive, S3c anti-reasoning) almost never produce hand-swap errors. When they're wrong, they're wrong in some other way (gross misperception, refusal, defaulting to safe times like "10:10"). Heavy prompts (S2, S3a, S3b, S3d) systematically pull failures toward hand-swap. **The feature-check prompt (S3b), which explicitly tells the model to identify each hand's position before naming the time, produces hand-swap on more than a third of all its failed trials.** The model's perception is doing the right thing under feature-check; the model's procedural categorization, prompted to operate carefully, makes its careful operation in the wrong direction.

## Per-clock hand-swap matrix (counts out of 10 per cell)

| Clock | S1 | S2 | S3a | S3b | S3c | S3d | Total |
|-------|----|----|----|----|----|----|-------|
| clock_01 (10:10) | 0 | 0 | 0 | 1 | 0 | **7** | 8 |
| clock_02 (3:25) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| clock_03 (7:50) | 0 | 2 | 0 | 1 | 0 | 4 | 7 |
| clock_04 (8:20) | 0 | 0 | 0 | 0 | 0 | 1 | 1 |
| clock_05 (4:15) | 2 | **9** | 2 | **10** | 0 | 3 | **26** |
| clock_06 (6:30) | 0 | 0 | 0 | 0 | 0 | 0 | 0 (invisible) |
| clock_07 (11:55) | 0 | 2 | 4 | **9** | 0 | 0 | 15 |
| clock_08 (9:45/2:15) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| **Total** | 2 | 13 | 6 | 21 | 0 | 15 | 57 |

## Per-clock standouts

- **clock_05 (gradient 4:15) is the biggest hand-swap attractor:** 26 of 57 total swaps (46%). S2 hand-swaps 9 of 10, S3b hand-swaps 10 of 10. The 4-position-with-hour-hand-near-3 / 3-position-with-minute-hand-at-3 ambiguity is the most attractive trap in the stimulus set. Naive S1 produces only 2 hand-swaps on this clock; anti-reasoning S3c produces zero.
- **clock_07 (dark 11:55):** 15 hand-swaps, 9 from S3b alone. The minute hand near 12 + hour hand near 11 cluster invites swapping into "11:00" under heavy reasoning prompts.
- **clock_01 (10:10):** 8 hand-swaps, but **only S3d triggers it** (7 of 8 swaps for this clock). Persona-and-stakes specifically destabilizes the canonical 10:10 ad-clock pose that every other prompt reads correctly.
- **clock_02, clock_04, clock_08:** essentially zero hand-swaps under any condition. Their failures are different in shape (gross misperception, refusal, mirror-template-mismatch).
- **clock_06:** geometrically invisible swap (6:30 → 6:30). Failures all wrong-other.

## Comparison to our trained variants

| Condition | Hand-swap rate among failures |
|-----------|-------------------------------|
| S3c anti-reasoning | 0.0% |
| S1 naive | 4.0% |
| S3a methodology | 10.7% |
| **Heavy-summary (Part 4-5)** | **18.6%** |
| **Hybrid (Part 5)** | **22.0%** |
| S3d persona + stakes | 25.9% |
| S2 combined | 26.0% |
| S3b feature-check | 36.2% |

(Trained-variant rates: heavy-summary 11/(80-21) = 18.6% among failures; hybrid 13/(80-21) = 22.0% among failures.)

Our trained variants land cleanly in the heavy-prompt regime. The dialogic-teaching arc and the 600-word system-prompt summary recapitulate the heavy-scaffolding signature, including the characteristic hand-swap rate that the original heavy conditions (S2/S3d) display. **The trained variants are not producing a new failure mode. They are reproducing the heavy-prompt failure mode at slightly different fidelity.**

## What this means for the broader thesis

The original Salon clocks article framed the central finding as "scaffolding-can-break-correct." Part 6 strengthens this and changes its character. Heavy scaffolding doesn't just lower aggregate accuracy. It **transforms** the failure mode. Under naive S1 or anti-reasoning S3c, when the model fails, it fails by misperception (didn't see the clock right). Under heavy prompts (S2, S3b, S3d, our trained variants), when the model fails, it increasingly fails by hand-identification swap (saw the clock right, mislabeled which hand is which).

The hand-swap finding wasn't visible in the original published article because the AI-judge classification scheme used in that experiment scored each trial as correct or incorrect (with within-five-minutes as a tolerance band) without separating hand-swap from other kinds of wrong answer. The cross-condition pattern (hand-swap rate scales monotonically with prompt weight) is the new structural insight from Part 6 and is the load-bearing result for the summary paper. AI judging was used in the original experiment and in every part of this follow-up; the difference is the richer category set.

## Methodology notes

- All 480 trials processed; 14 trials flagged as refused (all on clock_04 under S1 — the naked-hands stimulus where the model literally fails to recognize it as a clock and calls it a propane molecule).
- Spot-checked all 57 hand-swap and all 37 within_5 classifications. One ambiguous extraction case (S3d clock_02 trial 9) where the model wrote "3:25" mid-text but corrected to "9:15" as final answer; "last HH:MM" extraction rule correctly picked 9:15.
- Aggregate exact + within_5 accuracies match the published table within ±2 percentage points across all six conditions, confirming the original numbers.

---

# Part 7 — Fundamental-perception baselines (B1-B4, N=3)

**Date:** 2026-05-05 ~20:25 ET
**Driver:** Terry (Salon, Opus 4.7)
**Student:** Sonnet 4.6, fresh conversation per trial, no system prompt beyond bare task instruction
**Stimuli:** programmatically rendered, no clock semantics
**Method:** AI-judge classification (subagent), N=3 per stimulus
**Output:** `scratch/clocks_training/perception_baseline/{b1,b2,b3,b4}/trials.json`, `judge_classified.json`

## Question

Does Sonnet's encoder fail at fundamental perceptual primitives (angle, length) outside of clock semantics? Or do those primitives work and the clock failure modes live entirely at the categorical / procedural layer? Per Ted's request to "test perceptual abilities in isolation of the clock tests."

## Sub-experiments

- **B1 — single-line angle, clean:** 12 angles every 30° (clock convention), white background, single black hand-style line from center to rim. Ask which clock-face position (1-12) the line points to.
- **B2 — single-line angle, with chronograph clutter:** same 12 angles plus three decorative subdial circles in the background.
- **B3 — two-line length, clean:** two hand-style lines from common center, one straight up, one straight right. 5 length ratios (1.0 equal, 1.1, 1.2, 1.3, 1.5), both directions of "longer" tested. Ask which is longer (or equal).
- **B4 — two-line length, with chronograph clutter:** same 9 ratio configs with subdial background.

## Aggregate results (N=3 per stimulus)

| Condition | Exact / Correct | Off-by-one-or-better |
|-----------|------------------|----------------------|
| B1 (clean angle) | 55.6% | 66.7% |
| B2 (cluttered angle) | 44.4% | 61.1% |
| B3 (clean length) | 92.6% | — |
| B4 (cluttered length) | 85.2% | — |

## The headline finding

**Sonnet has a catastrophic lower-half angle perception bias, independent of clutter, independent of clock semantics.**

For angles in the lower half of the canvas (180°-330° excluding cardinals), Sonnet repeatedly reads the OPPOSITE END of the line as the tip and reports a clock-position approximately 180° from truth. This is not noise; the failure rate is essentially total on certain angles:

- 240° (8 o'clock direction): 3/3 opposite-end errors in B1, 3/3 in B2
- 300° (10 o'clock direction): 3/3 opposite-end errors in B1, 3/3 in B2
- 210°, 330°: catastrophic but mixed

Upper-half and cardinal angles (0°, 90°, 180°, 270°, 30°, 60°) are largely clean. The cardinal 6 o'clock (180°) is partly clean despite being lower-half, suggesting the bias is specific to off-cardinal lower-half angles where the line ends up roughly in the bottom-left or bottom-right diagonal and the model resolves the "tip" to the upper-half end.

This is direct evidence that the encoder has a specific orientation-dependent failure mode for line endpoint identification.

## Length comparison is fine

B3 clean: 93% correct on 27 trials. The two errors are both at the equal-length (ratio 1.0) edge case, where the model has a slight false-positive bias toward calling one of two equal lines longer than the other.

B4 cluttered: 85% correct. Clutter loses ~7 percentage points, concentrated at the smallest ratios (1.0 equal and 1.1). At ratios ≥1.2 the model is 100% correct in both clean and cluttered conditions.

**Length comparison from a common anchor is essentially a solved primitive for Sonnet at moderate ratios.** The clock_02 / clock_05 hand-identification swaps are not due to "encoder fails at length comparison." They're at the procedural / categorical layer, as Part 6's hand-swap-scales-with-prompt-weight finding already showed.

## Mechanistic explanation for clock_06's "encoder floor"

Clock_06 (rainbow no-numerals at 6:30) was 0% across every condition we tested. The Part 7 baseline gives a specific mechanism: the truth has both hands pointing approximately straight down (180°), which is the cardinal lower angle that B1/B2 occasionally resolve. But more relevantly, clocks 03 and 07 also have hands in or near the lower half:

- clock_03 (24-hour 7:50): hour hand in lower-left (between 7 and 8, roughly 225°), minute hand at 10 (300°). Both lower-half.
- clock_06 (6:30): both hands at 180°.
- clock_07 (11:55): hands clustered in upper-left (between 11 and 12, roughly 330°-350°). The minute hand at 11 is at 330° — exactly one of the catastrophic angles in B1.

The lower-half angle bias is consistent with what we see on these three clocks. The "encoder floor" framing in Parts 3-6 was correct in identifying that no prompting reaches the failure on these clocks; Part 7 specifies the mechanism.

## Refined four-mechanism failure picture

| Layer | Mechanism | Evidence |
|-------|-----------|----------|
| **Encoder** | Lower-half angle bias / opposite-end-as-tip | B1+B2 100% error on 240° and 300° single-line stimuli |
| **Encoder** | Equal-length false-positive | B3+B4: 2/3 wrong on ratio 1.0; ratios ≥1.2 are 100% correct |
| **Procedural** | Hand-identification swap | Hand-swap rate scales monotonically with prompt weight from 0% (S3c) to 36% (S3b) |
| **Procedural** | Pattern-matching to canonical layouts | Clock_06 read as 11:30/12:30; the upper-end-as-tip mechanism + canonical-pose pattern-match |

The encoder mechanisms are specific and reachable by stimulus design (avoid lower-half angles; avoid near-equal-length comparisons). The procedural mechanisms are reachable by prompt design (lighter prompts produce fewer hand-swaps).

## Caveats

- **N=3 per stimulus.** The 100% error on 240° and 300° at N=3 is striking but a fuller test at N=10 per stimulus would tighten the estimate and verify the catastrophic-error claim. Recommended next step.
- **Single-model.** Cross-architecture replication (Opus 4.7, Haiku 4.5, GPT-5, Gemini 2.5 Pro) on the same baseline stimuli is the natural follow-up. The lower-half bias may or may not be Anthropic-family-wide.
- **Single line vs. two-line angle.** B1/B2 isolate angle perception with one line. The clock context has two hands present. Two-hand angle perception with non-equal lengths would test whether the lower-half bias persists when there's another hand in the upper half to disambiguate.
- **Stimulus design.** The B1/B2 line is hand-styled (base 8 / tip 4 taper) but rendered in solid black on white. Different rendering conventions (anti-aliased lines, different colors, different thicknesses) might shift the angle-perception accuracy.

## Cost

Part 7: ~$0.30 (126 calls at ~5K input + ~150 output each, plus judge subagent).
Whole-arc cumulative: ~$5.30.

## Files

- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/render_perception_baseline.py` — stimulus renderer
- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/run_perception_baseline.py` — runner
- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/perception_baseline/{b1,b2,b3,b4}/` — stimuli + trials + transcripts
- `/Users/tedinoue/work/claude-workspace/scratch/clocks_training/perception_baseline/judge_classified.json` — AI judge output

---

# Part 8 — N=10 perception baselines, Sonnet 4.6 vs. Opus 4.7

**Date:** 2026-05-05 ~20:55-21:05 ET
**Method:** Same B1-B4 stimuli as Part 7, N=10 per stimulus, two models run side-by-side under identical conditions. AI-judge classification.
**Output:** `scratch/clocks_training/perception_baseline_n10_sonnet/`, `perception_baseline_n10_opus/`, `perception_baseline_n10_judge.json`
**Total trials:** 840 (420 per model)
**Cost:** ~$1.50 Sonnet + ~$5.50 Opus + ~$0.30 judge = ~$7.30

## Aggregate accuracy

| Sub-experiment | Sonnet 4.6 | Opus 4.7 |
|----------------|-------------|-----------|
| B1 (clean angle, exact) | 56.7% | **76.7%** |
| B1 (off-by-one or better) | 70.0% | **81.7%** |
| B1 (opposite-end errors) | 30.0% | 18.3% |
| B2 (cluttered angle, exact) | 43.3% | **91.7%** |
| B2 (off-by-one or better) | 59.2% | **94.2%** |
| B2 (opposite-end errors) | 36.7% | 5.0% |
| B3 (clean length, correct) | **91.1%** | 53.3% |
| B4 (cluttered length, correct) | **86.7%** | 43.3% |

**The two models have completely different perceptual profiles, not graded versions of the same profile.**

## The model-specific lower-half angle bias

The Part 7 N=3 pilot identified a "catastrophic lower-half angle bias" at 240° and 300°. The N=10 Sonnet data confirms and broadens it:

| Truth angle | Truth pos | Sonnet B1 (n=10) | Sonnet B2 (n=10) | Opus B1 (n=10) | Opus B2 (n=10) |
|-------------|-----------|------------------|------------------|-----------------|-----------------|
| 0° | 12 | clean | clean | clean | clean |
| 30° | 1 | clean | clean | clean | clean |
| 60° | 2 | clean | clean | clean | clean |
| 90° | 3 | clean | clean | clean | clean |
| 120° | 4 | clean | clean | clean | clean |
| 150° | 5 | clean | clean | clean | clean |
| 180° | 6 | clean | clean | clean | clean |
| 210° | 7 | 6/10 opposite | varied | **10/10 opposite** | clean |
| 240° | 8 | **10/10 opposite** | **10/10 opposite** | **10/10 opposite** | clean |
| 270° | 9 | **10/10 exact** | **10/10 opposite** | clean | varied |
| 300° | 10 | **10/10 opposite** | **10/10 opposite** | clean | clean |
| 330° | 11 | **10/10 opposite** | varied | clean | clean |

**Sonnet has a four-angle catastrophic band (210°-330°) that subdial clutter mostly worsens.** Sonnet 270° (the 9 o'clock cardinal) is the survivor in clean conditions but flips to 10/10 opposite when subdials are added. Discontinuity rather than gradient: 270° works perfectly in B1, falls apart in B2 with the same trial design.

**Opus has a narrower catastrophic band (210°-240°) that subdial clutter REVERSES.** In B1, Opus 210° and 240° both flip 10/10 opposite. In B2 (with subdials), both recover to clean. Opus 270° is clean in B1 but partly fails in B2 — opposite of the Sonnet pattern.

Conclusion: **the lower-half angle bias is model-specific, not substrate-wide.** Different vision-language encoders have different orientation-dependent endpoint-identification failure modes, and subdial clutter modulates them differently.

## Length comparison — the inverse story

| Stimulus | Sonnet B3 | Sonnet B4 | Opus B3 | Opus B4 |
|----------|-----------|-----------|---------|---------|
| ratio 1.0 (equal) | 3/10 | 3/10 | 3/10 | 5/10 |
| ratio 1.1 (up longer) | 10/10 | 8/10 | 5/10 | 4/10 |
| ratio 1.1 (right longer) | 9/10 | 9/10 | 4/10 | 1/10 |
| ratio 1.2 (up) | 10/10 | 10/10 | 8/10 | 7/10 |
| ratio 1.2 (right) | 10/10 | 10/10 | 7/10 | 5/10 |
| ratio 1.3 (up) | 10/10 | 10/10 | 7/10 | 6/10 |
| ratio 1.3 (right) | 10/10 | 10/10 | 6/10 | 4/10 |
| ratio 1.5 (up) | 10/10 | 10/10 | 6/10 | **1/10** |
| ratio 1.5 (right) | 10/10 | 8/10 | 2/10 | 6/10 |

**Sonnet is near-ceiling on unequal-length comparisons** (≥80% at every ratio above 1.0, perfect at 1.2+). Its only consistent failure is the equal-length stimulus, where it has a false-positive bias toward calling one line longer.

**Opus shows substantial reversal-and-equal-bias at every ratio.** Even at the easiest condition (1.5x ratio, 50% size difference), Opus reaches only 60% correct in B3 clean and 35% in B4 cluttered. The 1.5_up in B4 is the most striking single cell: 1/10 correct, 9/10 reversed. Opus calls the longer line shorter when there's subdial clutter and a 50% length difference.

**The two models share the equal-stimulus failure** (3/10 correct each in B3 — both call truly-equal lines unequal). That's the one consistent cross-model perceptual error.

## What this changes about the earlier "encoder floor" framing

Parts 3-6 attributed clock_06 (rainbow 6:30) and clock_03 (24-hour 7:50) to "encoder floor" — implying a substrate-wide perceptual limit. Part 7 specified the mechanism for Sonnet (lower-half angle bias). Part 8 shows the floor is **Sonnet-specific**: Opus reads 300°/330° lines correctly. Whatever Opus's failures are on clock_06/03, they're not the same as Sonnet's.

The corollary: Opus's clock-reading on the original 8-clock test set, where Opus performed substantially better than Sonnet, may be driven by Opus having different (and on these specific clocks, less common) failure modes — better angle perception in Sonnet's catastrophic band, but worse length comparison than Sonnet.

A two-mechanism model unifies the two model profiles:
- ENCODER mechanism A: lower-half angle bias / opposite-end-as-tip — present in both models with model-specific angle bands and opposite responses to clutter
- ENCODER mechanism B: equal-and-near-equal length false-positive bias — present in both models, much stronger in Opus

The clock failure modes load differently on these two mechanisms. Clocks 03/06 (lower-half hand positions) load on mechanism A. Clocks 02/05 (where hand-swap can happen because the model gets length-comparison wrong at small ratios) load on mechanism B. Sonnet's clock failures concentrate on mechanism-A clocks; Opus's would concentrate on mechanism-B clocks (and would express as different specific clock failures on the original test set).

## Caveats

- **Same set of 12 angles for B1/B2.** Catastrophic angles fall on or near the diagonal (210°, 240°, 300°, 330° for Sonnet). Whether finer-grained sampling (every 10° or 5°) reveals additional structure is open.
- **Hand-style line only.** B1/B2 use a single rendering (base 8, tip 4 taper). Different rendering conventions may shift the bias.
- **Two-line angle perception not tested.** All B1/B2 stimuli are single-line. Whether Sonnet's lower-half bias persists when an upper-half hand is also present (as on most clocks) is the natural follow-up.
- **Opus's length-comparison failure is so strong it's worth re-verifying.** 9/10 reversed at 1.5x ratio with clutter is striking enough that a stimulus-rendering bug should be ruled out. Visual inspection of the renders confirms they're correct (the "longer" hand visibly extends further from the pivot), but a sanity-check pass with a different renderer or different ratios is warranted before public claims.

## What this means for the paper

The original "encoder floor" framing was correct in identifying that no prompting reaches certain failures, but the mechanism is more interesting and more useful than "the encoder can't see the image." The paper should:

1. Report the two encoder mechanisms (lower-half angle bias, equal-and-near-equal length false-positive) as model-specific perceptual primitives that differ across models.
2. Note the model-specific clutter response — subdials help Opus's angle perception, hurt Sonnet's. The folk theory that "clutter is universally distracting for vision LLMs" is too simple.
3. The "look harder" framing now has a fourth direction: stimuli where the model's encoder has a specific quirky failure on raw geometric primitives, separable from the procedural clock-reading layer that prompting interacts with.

3. **A specific technique audit suggested:** the original 6-condition single-shot study should be re-run with one additional condition added — a "thickness-cue" prompt that names hour-hand thickness as a backup feature. If Sonnet's overall accuracy moves on that condition, the pattern from this dialogic pilot would have a single-shot mirror.

4. **The within-Sonnet attentional floor (length-reversal under specific configurations) is a clean architectural marker.** Worth probing whether Opus 4.7 has the same reversal floor on the same images, since the Anthropic family-architecture story (Part 1) predicts it would not.
