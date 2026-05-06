# AI judge prompt — N=10 perception baseline (Sonnet vs Opus)

This is the prompt template used to dispatch a fresh-context AI judge subagent for classifying the 840 perception-baseline trials. Reproducing the classification requires a fresh Claude instance (Opus 4.7 or similar capability) with file-read access.

---

You are the AI judge for the N=10 fundamental-perception baseline trials. Two models tested side by side: Sonnet 4.6 and Opus 4.7. Per the standing rule for this experimental track, no regex shortcuts — classify by reading the responses.

## Inputs

Eight JSON files of trial data, four per model. Each trial has a `model`, `condition` (b1-b4), `truth_clock_position` or `truth_longer`, `trial` index, and `raw_response` (the model's free-text answer).

Total 840 trials.

## What was tested

**B1 / B2 — single-line angle perception.** Single black hand-style line anchored at the center of a 512×512 white canvas, extending toward the rim at one of 12 angles (every 30 degrees, clock convention with 0° = 12 o'clock = up, 90° = 3 o'clock = right, 180° = 6 o'clock = down, 270° = 9 o'clock = left). B2 differs from B1 only in having three decorative chronograph-style subdial circles in the background.

The expected answer for each angle is the clock numeral exactly at that angle: 0° → 12, 30° → 1, 60° → 2, 90° → 3, 120° → 4, 150° → 5, 180° → 6, 210° → 7, 240° → 8, 270° → 9, 300° → 10, 330° → 11.

The model was asked: "Which clock-face position (1 through 12) does the line point toward?" with a request to bold the final number.

**B3 / B4 — two-line length comparison.** Two black hand-style lines from a common center: one straight up, one straight right. Same thickness and taper. Different lengths by ratio. Conditions:
- ratio 1.0 (both equal)
- ratio 1.1, 1.2, 1.3, 1.5, with either UP or RIGHT longer

B4 differs from B3 in having three subdial circles in the background.

The model was asked: "Which line is longer (or are they equal): up, right, or equal?"

## Classification scheme

For B1/B2:
- **exact** — answer matches truth clock-position exactly
- **off_by_one** — answer is one position off (cyclic)
- **off_by_more** — answer is two or more positions off, but not opposite
- **opposite** — answer is approximately 180° opposite (5–7 positions off cyclically)
- **refused_or_ambiguous**

For B3/B4:
- **correct** — answer matches truth direction
- **reversed** — answer is the opposite direction
- **equal_called_unequal** — truth=equal but answer says one is longer
- **unequal_called_equal** — truth has a longer one but answer says equal
- **refused_or_ambiguous**

## Output

JSON file with per-trial classifications, per-stimulus summary counts, and aggregate statistics per model and per condition.

Process all 840 trials.
