# Follow-up: Three-mechanism resolution (2026-05-07)

A second follow-up arc to the original clocks experiment. Where `followup_05052026/` asked whether prompting could repair the failures, this round asks **what the failures actually are at the architectural level**.

About 1,700 API calls across 13 experiments, ~$60–70 in compute. Sonnet 4.6 and Opus 4.7.

**Substack writeup:** [How AIs Fail at Reading Clocks and Why That's Important](https://synthsentience.substack.com/) (Synth Sentience, 2026-05-08).

## TL;DR — Three architectural mechanisms

Vision-language clock-reading failures resolve into three separable mechanisms, each independently testable:

1. **Perceptual extrapolation.** When a pointer's tip reaches the labels, models read accurately (Opus 100% on the half-circle test, max 5° error). When the tip is interior to the label ring, accuracy collapses by 40–67 percentage points, with rare full opposite-end flips. *Cleanest demonstration:* `findings/HALFCIRCLE_FINDINGS.md`.

2. **Hand-role identification.** Two-hand clocks force the model to decide which hand is which. Length disparity disambiguates; reduced disparity produces hand-swap errors. Adding explicit color disambiguation (red hour, blue minute) eliminates hand-swap errors. *Demonstrated in:* `findings/COLOR_CLOCK_FINDINGS.md` + `findings/LONG_HANDS_VALIDATION_FINDINGS.md`.

3. **Position-to-hour conversion.** When the hour hand is more than two-thirds of the way to the next numeral, models default to "nearest numeral" instead of "earlier numeral." 7:45 reads as 8:45. The model verbally knows the convention but doesn't apply it. *Residual on color test* (with both perceptual mechanisms removed): `findings/COLOR_CLOCK_FINDINGS.md`. *Partial in-context fix with symmetric over-correction:* `findings/RULE_FIX_FINDINGS.md`.

## Reading order

1. `findings/INDEX.md` — master index of all 14 experiments in chronological order, with supersession notes for hypotheses that were refuted in-arc.
2. `findings/HALFCIRCLE_FINDINGS.md` — mechanism 1, cleanest isolation (1,110 trials).
3. `findings/LONG_HANDS_VALIDATION_FINDINGS.md` — refutes the early "all five mechanisms collapse to one" overclaim.
4. `findings/COLOR_CLOCK_FINDINGS.md` — mechanisms 2 and 3 separated.
5. `findings/RULE_FIX_FINDINGS.md` — convention error is partially in-context-correctable but with symmetric over-correction (rule fixes 5:50, breaks 1:15).

Supporting:
- `findings/STYLE_SWAP_FINDINGS.md` — visual style (long-thin vs short-thick) as the dominant accuracy driver, not hand semantic role.
- `findings/HOUR_ONLY_FINDINGS.md` — single-hand clock isolation; rules out role confusion as the cause of off-cardinal drift.
- `findings/PERCEPTION_BASELINE_CORRELATION.md` — population-level analysis of B1 single-line angle baseline against the 640-trial test set from `followup_05052026/`. Refines an earlier overclaim that B1 was the universal predictor.
- `findings/FINDINGS_PART_9_DIRECTION_FLIP.md` — direction-reversal added to the failure-mode taxonomy of `followup_05052026/`.

## Two adversarial-test catches in one day

- An early "B1 zone predicts everything" claim (cleanly true on the simplest-clock isolation case) was refuted at population scale by the 640-trial re-judge — B1 is one of multiple architectural factors, not the universal predictor.
- A "five mechanisms collapse to one" unification claim from the half-circle finding was refuted by the long-handed clock validation — two-hand clock-reading involves more than line-pointer perception. The three-mechanism story replaced it.

Both catches are documented in the relevant FINDINGS docs.

## Layout

- `findings/` — markdown writeups for each experiment, plus the master index.
- `stimuli/` — programmatically-rendered PNG stimuli for each experiment.
  - `halfcircle/` — 19-letter half-circle scale, three pointer lengths.
  - `color_clocks/` — red hour, blue minute, both reach tick marks.
  - `long_hands_clocks/` — both hands long-thin.
  - `hour_only_clocks/` — single-hand clock at 30-min intervals.
  - `hour_only_thin/` — long-thin hour-hand visual.
  - `hour_only_no_numerals/` — numerals removed, tick marks only.
  - `minute_only_clocks/` — long-thin minute-hand only.
  - `minute_only_thick/` — short-thick visual on minute-hand angles.
- `trials/` — raw JSON results from each run.
  - `dialogic_teaching/round1|round2|round3/` — three-arm dialogic teaching comparison transcripts and conversation logs (Sonnet 4.6 student).
  - `halfcircle_*.json` — 1,110 trials.
  - `color_clock_*.json` — 100 trials, 100 with rule.
  - `long_hands_*.json` — 100 trials.
  - `hour_only_*.json` — 48 trials.
  - `minute_only_*.json` — supporting style-swap experiments.
  - `isolate_430_results.json` — three-arm × 5-trial isolation of the 4:30 destabilizer (self-check system prompt vs thinking-on).
  - `opus_simplest_results.json` — Opus 4.7 vs Sonnet 4.6 simplest-clock comparison.
- `code/` — render scripts (`render_*.py`), trial harnesses (`run_*.py`, `isolate_430.py`, `opus_simplest.py`, `teach.py`), and a Haiku-judge classification harness (`judge_n10.py`).

## Reproduction

Each `run_*.py` script reads `ANTHROPIC_API_KEY` from the environment, calls `claude-sonnet-4-6` and/or `claude-opus-4-7` on the corresponding stimulus set, and writes results to a JSON file at the repo root. Stimuli were rendered deterministically with PIL by the matching `render_*.py` script.

Models tested:
- `claude-sonnet-4-6` with `thinking={"type": "enabled", "budget_tokens": ...}` (most experiments) or thinking-OFF where noted.
- `claude-opus-4-7` with `thinking={"type": "adaptive"}` and `output_config={"effort": "high"}` (Opus uses adaptive thinking, not Sonnet's `enabled` + `budget_tokens` — harness handles this distinction).

## Methodological note

All primary results from the original `followup_05052026/` round were generated with extended thinking OFF. This was surfaced during this arc; the disclosure is mandatory for any paper draft that ships from this data. A representative thinking-on subset re-run is queued before any formal paper publication.

The convention-rule fix is partially in-context-correctable but with symmetric over-correction: telling the model the convention fixes one direction of error (5:50 → 5/5) and breaks another (1:15 → 12:15 in 5/5 trials, both models). This is the same over-correction pattern observed when naming a directional bias to the model produces a bias in the opposite direction. Two independent demonstrations within twelve hours.
