# What "AI Can't Read Clocks" Actually Means

*A controlled six-condition experiment across five frontier models on eight analog clocks, prompted by Jing Hu's claim that even Claude Opus reads them at coin-toss accuracy.*

---

## Lessons learned (read this first)

1. **Cold-prompt accuracy dramatically understates capability.** Claude Opus 4.7 scored 28% on a naive prompt and 69% on a rich system prompt. The same model. The same images. The 41-point gap is what changes between "AI can't read clocks" and "AI reads clocks reasonably well when asked carefully."

2. **No single prompt is best for every model.** Opus benefits most from rich combined scaffolding. Sonnet 4.6 and Haiku 4.5 are *hurt* by every deliberation prompt and do best when told explicitly *not* to think. GPT-5 is robust at around 73 to 78% across all conditions. The right scaffold depends on the model.

3. **Methodical scaffolding can break correct native capability.** Sonnet 4.6 reads Roman numerals correctly 100% of the time on a cold prompt. Add a methodical "identify each hand and the numeral it points at" instruction and Sonnet drops to 0%, systematically misreading IX as III and committing to 9:25 instead of 3:25. The cleanest single result in the dataset.

4. **Specific failure modes survive every prompt.** A 24-hour double-ring clock defeats Sonnet and Haiku regardless of priming (always read as 10:15 or 10:10). The minute hand at 11 on a dark face gets read as the hour-pointer toward 12 across most models (giving 11:00 instead of 11:55). These are perception or rule-integration failures, not deliberation failures.

5. **Models can describe a rule without applying it.** On a mirror clock with counter-clockwise numerals, Gemini 2.5 Pro explicitly identifies the mirroring in its reasoning, then commits to a wrong time anyway. Knowing is not applying.

6. **The "AI can't read clocks" framing is wrong.** It conflates a default-behavior failure with a capability failure. The capability is there for the strongest models. What the original claim measures is how the models behave when nobody asks them to be careful.

---

## The original claim

Jing Hu posted a Substack note showing eight analog clocks alongside the line: *"even with the best and latest LLM, take Claude Opus for example, only got this right at a coin toss."* The image had complex chronographs, Roman numerals, a 24-hour double ring, naked-hands clocks, gradients, rainbows, dark faces, and a mirror clock with counter-clockwise numerals.

Coin-toss accuracy on her benchmark is a strong claim. We replicated her stimulus categories with programmatic rendering so we would know exactly what each clock shows. Then we ran a controlled experiment across five frontier models and six prompting conditions to figure out what is actually happening.

---

## The stimulus set

We built the eight clocks programmatically using Python's PIL library, with full control over every pixel and the time displayed. Each clock matched one of Jing Hu's style categories. Times were chosen to span easy and hard reads. Ground truth was set as the input parameter to the rendering function and verified manually before any trial ran.

| Clock | Style | Ground truth |
|---|---|---|
| 01 | Arabic numerals, three chronograph subdials, white face | 10:10 |
| 02 | Roman numerals, red MON date window at 3 | 3:25 |
| 03 | 24-hour double ring (inner 1-12, outer 24/1-23) | 7:50 |
| 04 | Two hands only. No face, no markers, no border | 8:20 |
| 05 | Vertical red-to-blue gradient, Arabic, day-date strip | 4:15 |
| 06 | Rainbow horizontal bands, no numerals, day-date strip | 6:30 |
| 07 | Plain dark face, slim white hands, day-date strip | 11:55 |
| 08 | **Mirrored** Arabic numerals (counter-clockwise sequence, glyphs flipped) | 9:45 OR 2:15 (dual rubric) |

For the mirror clock we accept two correct answers: 9:45 (mirror-aware reading of the numerals) and 2:15 (template-match without noticing the mirror). Both reflect correct hand-position reading. The interpretive difference is whether the model noticed the mirroring.

---

## The cohort

| Provider | Model |
|---|---|
| Anthropic | Claude Opus 4.7 |
| Anthropic | Claude Sonnet 4.6 |
| Anthropic | Claude Haiku 4.5 |
| OpenAI | GPT-5 |
| Google | Gemini 2.5 Pro |

Each model received the same eight images with the same user prompt: *"What time does this clock show?"* The only experimental variable was the system prompt.

N = 10 trials per (model × clock × condition). Total trial volume across all conditions: about 2,400 trials. Free-text responses, classified by AI-judge subagents into four buckets: exact match (within 1 minute), within 5 minutes, wrong by more, refused or uncertain.

---

## The six conditions

### S1. No system prompt (baseline)

```
[no system prompt]
User: What time does this clock show?
```

### S2. Combined prime (persona + scaffolding + feature-checking)

```
You are an experienced clockmaker who has spent decades reading and
repairing analog timepieces. You read clocks methodically, never guessing.

When you examine a clock, you proceed in this order:

1. First, examine the clock face as a whole. Note any unusual features
   before reading the time: mirrored numerals, absent face or markers,
   multiple subdials, 24-hour markings, decorative elements.

2. Identify the HOUR hand. It is shorter and thicker. State precisely
   which numeral or position it points at.

3. Identify the MINUTE hand. It is longer and thinner. State precisely
   which numeral position it points at. Each numeral represents 5 minutes.

4. Reason about the angles carefully.

5. Only after you have identified both hands, commit to a specific time.
```

### S3a. Scaffolding only

```
You read clocks methodically.

For every clock, follow this two-step procedure before committing to a time:
1. Identify the HOUR hand. It is shorter and thicker. State which numeral
   it points at, or between which two numerals it sits.
2. Identify the MINUTE hand. It is longer and thinner. State which numeral
   position it points at. Each numeral represents 5 minutes.

Only after you have identified both hands, commit to a time.
```

### S3b. Feature-checking only

```
Some clocks have unusual features that change how the time should be read.
Before reading any clock, examine the face for these features:
- Mirrored numerals
- An absent face, missing markers, or hands floating with no reference
- 24-hour dual-ring markings
- Multiple subdials
- Decorative elements that aren't part of the time-reading

Notice and name any unusual features before committing to a time.
```

### S3c. Anti-reasoning

```
Don't overthink this. A glance is enough. State the time in HH:MM format
and stop. No reasoning, no commentary, no qualifications.
```

### S3d. Persona + stakes (no methodology)

```
You are an expert clockmaker. You have spent your entire career reading
and repairing analog timepieces, and your reputation depends on getting
times exactly right.

It is critically important that you read this clock accurately. Take
your time. Be careful. Make sure your answer is correct before you
commit to it.
```

---

## Headline results

Accuracy is percentage of trials within 5 minutes of ground truth. Bold = best condition for that model.

| Model | S1 (none) | S2 (combined) | S3a (method) | S3b (features) | S3c (anti-think) | S3d (persona+stakes) |
|---|---|---|---|---|---|---|
| **Opus 4.7** | 28% | **69%** | 66% | 50% | 37% | 57% |
| **Sonnet 4.6** | 25% | 36% | 29% | 21% | **37%** | 24% |
| **Haiku 4.5** | 6% | 11% | 2% | 16% | **36%** | 8% |
| **GPT-5** | 72% | 75% | **78%** | 73% | 73% | 79% |
| **Gemini 2.5 Pro** | (n=9) | 42% | 45% | not run | not run | not run |

Each model has a different best condition. Opus benefits from explicit deliberation. Sonnet and Haiku are *hurt* by deliberation prompts and recover only when told not to overthink. GPT-5 is essentially flat across conditions because it is already near its ceiling on the easier clocks.

---

## Per-clock difficulty (S1 baseline, complete-data models)

| Clock | Style | gt | S1 accuracy |
|---|---|---|---|
| 01 | Chronograph (watch-ad pose) | 10:10 | 82% |
| 02 | Roman numerals | 3:25 | 50% |
| 03 | 24-hour double ring | 7:50 | 18% |
| 04 | Naked hands, no face | 8:20 | 8% |
| 05 | Gradient + Arabic | 4:15 | 25% |
| 06 | Rainbow, no numerals | 6:30 | 42% |
| 07 | Dark face, slim hands | 11:55 | 20% |
| 08 | Mirrored Arabic | 9:45/2:15 | 18% |

The naked-hands clock is the hardest stimulus across the board. The 10:10 chronograph is the easiest. Mirror and 24-hour clocks defeat most models on cold prompts.

---

## Six findings worth keeping

### 1. The Sonnet Roman-numeral collapse

Sonnet 4.6 on clock_02 (Roman, ground truth 3:25):

| Condition | Accuracy | What Sonnet says |
|---|---|---|
| S1 (none) | **100%** | 3:25 |
| S2 (combined) | 10% | 9:25 (8 of 10 trials) |
| S3a (scaffolding) | **0%** | 9:25 (10 of 10 trials) |
| S3b (features) | 30% | 9:25 (6 of 10) |
| S3c (anti-think) | **100%** | 3:25 |
| S3d (persona+stakes) | 40% | 9:25 (5 of 10) |

The methodical "identify each hand at a numeral" instruction systematically inverts IX as III for Sonnet. *Any* prompt encouraging careful deliberation triggers it. Only the explicit anti-reasoning prompt preserves Sonnet's correct native read. The "take your time" framing in S3d partially triggers the collapse too, suggesting the failure is induced by the deliberation frame itself, not by the specific scaffolding wording.

Methodical thinking can be the wrong tool. Slowing down and parsing each glyph is exactly when Sonnet starts inverting Roman numerals.

### 2. The Opus methodology ladder

Opus 4.7 component-by-component:

```
S1  no prompt          28%
S3c anti-reasoning     37%   (+9pp)
S3b feature-check      50%   (+22pp)
S3d persona+stakes     57%   (+30pp)
S3a scaffolding        66%   (+38pp)
S2  combined           69%   (+41pp)
```

Each prompt component contributes additively for Opus. Methodology is the largest single contributor. Combining all three primes adds about 3 points over scaffolding alone. The bulk of the Stage 2 effect comes from the methodology component.

### 3. The 24-hour rule-integration failure

Clock_03 has 24 outer numerals at 15-degree intervals plus an inner 1-12 ring. It is functionally a 12-hour movement decorated with 24-hour reference numerals.

Sonnet says "10:15" across all six conditions. Haiku says "10:10" across all six conditions. They detect the structure, can describe the dual ring, but cannot apply the rule when reading time. Recognition without application.

Opus and GPT-5 both recover under scaffolding. Gemini partially recovers. The integration works for the stronger models when prompted to slow down. For the weaker models, no amount of priming moves the needle.

### 4. The mirror clock split-application failure

Clock_08 has Arabic numerals in counter-clockwise order with each glyph horizontally flipped. The hands point at the mirrored "9" position.

Two correct answers exist:
- 9:45 (mirror-aware: read the mirrored numerals to identify hour and minute positions in mirror space)
- 2:15 (template-match: ignore the numerals, read hand positions as if it were a normal clock)

The Anthropic family detects the mirror on the hour hand (correctly identifies the displayed "9" position) but fails to apply the same logic to the minute hand. Hour-only mirror application. They commit to "9:00" or "9:10" instead of "9:45."

GPT-5 either ignores the mirror entirely (template-match wins, gives 2:15) or partially applies it. Under the rich prime in Stage 2 GPT-5 went 100% template-match.

Gemini explicitly names the mirror in its reasoning then commits to wrong times like 10:15 anyway. The model knows what it is looking at and still cannot read it. Meta-cognitive failure.

### 5. The naked-hands clock and feature-checking unlock

Clock_04 has only two hands floating on white. No face, no markers, no border.

Without a feature-checking prompt the models confabulate. Sonnet's S1 response on this clock interpreted the image as a chemistry diagram and refused to give a time (in 10 of 10 trials). Opus and GPT-5 mostly guess "10:20."

With feature-checking (in S2 or S3b) the behavior shifts:
- Sonnet refuses appropriately (9 of 10 in S3b)
- Opus correctly reads the implied 12-at-top (90% in S2)
- GPT-5 splits between correct reads and wrong guesses

Telling the model to look for "absent face or markers" is what triggers the appropriate response. The methodology prompt alone does not produce this; it walks the model through hand-position reasoning that has no anchor and ends in confident wrong guesses.

### 6. The minute-hand-at-11 trap

Clock_07 (dark face, slim white hands, ground truth 11:55) fools most models into "11:00." The minute hand sits at the 11 position. Models read this as the hour cue pointing at 11 and report 11:00, dropping the inference that "minute hand at numeral N means N times 5 minutes."

Even with explicit scaffolding ("each numeral represents 5 minutes for the minute hand"), the failure persists for some models. GPT-5 dropped to 40% under feature-checking on this clock. Opus dropped to 20% under scaffolding alone. The 11:00 misread is a stubborn failure mode that prompt engineering only partially mitigates.

---

## What this means

Coin-toss accuracy on a cold prompt is a real measurement. It also is not a capability ceiling. The same Opus 4.7 model that scored 28% on the original prompt scored 69% with rich scaffolding. GPT-5 was already at 72% baseline and reached 78% with scaffolding alone.

Three categories of failure show up cleanly:

**Default-behavior failures** are recoverable by prompting. Most clocks improve substantially under scaffolded reasoning for Opus and GPT-5.

**Capability-breaking by methodology** appears for weaker models on stimuli they can already read. Sonnet's Roman collapse is the cleanest case. The methodical prompt walks the model through bad reasoning steps and locks them in. Telling the model not to overthink restores the native capability.

**Perception or rule-integration failures** survive all prompting. The 24-hour clock for Sonnet and Haiku, the mirror clock for everyone, and the minute-hand-at-11 trap on clock_07 across most models. These are the failures that look most like a real ceiling.

The right way to talk about multimodal model perception is not "the model can or cannot read clocks." It is: under what prompting conditions does which capability surface, and which failure modes are stable across all conditions. The cold-prompt single-number accuracy is one data point among many, and an unrepresentative one for the strongest models.

When the next viral "AI can't do X" post crosses your feed, the question worth asking is what the prompt was, what the cohort was, and whether anyone tried more than one framing.

---

## Methodology notes

- Stimuli rendered programmatically with Python PIL. Source code: `salon/files/clocks/scratch/clock_renderer.py`.
- Trials sent via direct API calls (Anthropic, OpenAI, Google) at temperature default with max_tokens 4096 (required for reasoning models that consume hidden reasoning tokens).
- Classification by parallel Claude subagents reading raw responses against per-clock ground truth and a published rubric. Zero metered cost for judging.
- Per `feedback_never_alter_experimental_prompts.md`: the user prompt was sent unchanged across all conditions. The system prompt was the only experimental variable.
- Per `feedback_api_trials_retry_until_n.md`: transient API errors retried with exponential backoff until N clean completions per condition.
- Cohort decision: skipped Gemini for Stage 3b, 3c, 3d due to persistent Google API 503 overload. Will run Gemini variants separately when API load drops.
- Total API spend across all stages: approximately $25 to $35.

Full data and per-clock failure-mode tables at `salon/files/clocks/PER_CLOCK_TABLES.md`.
