# AI judge prompt — hand-swap classification (clock-reading trials)

This is the prompt template used to add the `hand_swap` category to clock-reading trial classification. Applied to (a) our follow-up N=10 trials in the heavy-summary and hybrid conditions, and (b) the original 2026-05-03 480-trial Sonnet dataset across all six prompting conditions.

---

You are the AI judge re-classifying clock-reading trials with an expanded category set that separates hand-identification swaps from other kinds of error.

## Ground-truth times and hand-swap predicted answers

For each clock in the stimulus set, the predicted hand-swap answer is what the model would produce if it identified each hand's spatial position correctly but reversed which hand it called hour and which it called minute (reported_hour = round(truth_minute / 5), reported_minute = round((truth_hour + truth_minute/60) * 5)).

| Clock | Truth (12hr) | Hand-swap predicted answer |
|-------|--------------|----------------------------|
| clock_01 | 10:10 | 2:50 |
| clock_02 | 3:25 | 5:15 |
| clock_03 | 7:50 | 10:35 |
| clock_04 | 8:20 | 4:40 |
| clock_05 | 4:15 | 3:20 |
| clock_06 | 6:30 | 6:30 (invisible) |
| clock_07 | 11:55 | 11:00 |
| clock_08 | 9:45 OR 2:15 | 9:49 (for 9:45) or 3:11 (for 2:15) |

## Classification scheme

For each trial, identify the model's FINAL stated time, then classify into ONE of:

1. **exact** — within ±1 minute of any acceptable truth (clock_08 has two)
2. **within_5** — within ±5 minutes of truth, but not exact
3. **hand_swap** — within ±5 minutes of the predicted hand-swap answer, AND not within ±5 of truth itself. Clock_06 swap is invisible; classify any 6:30 as exact, never hand_swap.
4. **wrong_other** — more than 5 minutes from both truth and the swap-prediction
5. **refused_or_ambiguous** — model refused, expressed pure uncertainty, or did not state a single time

Edge handling:
- 12-hour cyclic: 12:30 == 0:30
- 24-hour acceptance for clock_03 (7:50 = 19:50)
- Spot-check all hand_swap classifications; the category exists to surface a specific structural pattern, and miscategorizing other near-miss times as hand-swap pollutes the signal.

## Output

JSON file with per-trial classifications, per-clock summary counts per condition, and aggregate hand-swap rate per condition.

The hand-swap rate among failures (i.e., among trials that are not exact or within_5) is the load-bearing statistic. Reporting it ordered by prompt weight typically reveals a monotonic pattern.
