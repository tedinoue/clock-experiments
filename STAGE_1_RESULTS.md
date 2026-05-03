# Clocks Stage 1 — Results

Naive prompt: `What time does this clock show?`

**Cohort:** Opus 4.7, Sonnet 4.6, Haiku 4.5, GPT-5, Gemini 2.5 Pro
**Stimulus set:** 8 rendered clocks, ground truth at `salon/files/clocks/GROUND_TRUTH.md`
**Classification:** Subagent-based AI judge (per `feedback_ai_judge_for_trial_classification.md`).
**Buckets:** `exact_match` (±1 min) · `within_5_min` (±5 min, excl. exact) · `wrong_by_more` (>5 min off OR confidently wrong) · `refused_or_uncertain` (declined or hedged without committing)

> ⚠️ **PARTIAL DATA WARNING.** The following models have fewer than 80 clean trials and their numbers are NOT comparable to others:
> - **Gemini 2.5 Pro**: only 9 clean trials. (Underlying cause: Gemini API 503 overload during the run window. Need to re-run Gemini against fresh API conditions.)

Total trials run: 329 (clean: 329)

## Accuracy by model × clock

Cell shows % within ±5 min of ground truth. `—` = no trials. `(n)` = trial count if <10.

| model | c01 | c02 | c03 | c04 | c05 | c06 | c07 | c08 | overall |
|---|---|---|---|---|---|---|---|---|---|
| **gt** | 10:10 | 03:25 | 07:50 | 08:20 | 04:15 | 06:30 | 11:55 | 09:45 |    |
| Opus 4.7 | 100% | 0% | 0% | 0% | 0% | 100% | 0% | 20% | **28%** |
| Sonnet 4.6 | 100% | 100% | 0% | 0% | 0% | 0% | 0% | 0% | **25%** |
| Haiku 4.5 | 30% | 0% | 0% | 0% | 0% | 0% | 20% | 0% | **6%** |
| GPT-5 | 100% | 100% | 70% | 30% | 100% | 70% | 60% | 50% | **72%** |
| Gemini 2.5 Pro | 100% (9) | — | — | — | — | — | — | — | **100%** *(9 trials)* |

## Bucket distribution by model

| model | exact | ±5min | wrong | refused | n |
|---|---|---|---|---|---|
| Opus 4.7 | 15 (19%) | 7 (9%) | 50 (62%) | 8 (10%) | 80 |
| Sonnet 4.6 | 10 (12%) | 10 (12%) | 50 (62%) | 10 (12%) | 80 |
| Haiku 4.5 | 5 (6%) | 0 (0%) | 65 (81%) | 10 (12%) | 80 |
| GPT-5 | 55 (69%) | 3 (4%) | 22 (28%) | 0 (0%) | 80 |
| Gemini 2.5 Pro | 9 (100%) | 0 (0%) | 0 (0%) | 0 (0%) | 9 |

## Per-clock difficulty (% correct across complete-data models only)

| clock | style | gt | n | % correct |
|---|---|---|---|---|
| clock_01 | Arabic chronograph | 10:10 | 40 | 82% |
| clock_02 | Roman + date | 03:25 | 40 | 50% |
| clock_03 | 24-hour double ring | 07:50 | 40 | 18% |
| clock_04 | Naked hands only | 08:20 | 40 | 8% |
| clock_05 | Gradient + Arabic | 04:15 | 40 | 25% |
| clock_06 | Rainbow no numerals | 06:30 | 40 | 42% |
| clock_07 | Dark face slim hands | 11:55 | 40 | 20% |
| clock_08 | Mirrored Arabic | 09:45 | 40 | 18% |

## Comparison to Jing Hu's claim

Jing Hu (https://substack.com/@jinghuu/note/c-250006786): *"even with the best and latest LLM, take Claude Opus for example, only got this right at a coin toss"* — interpreted as ~50% accuracy across her 8-clock set.

- **Opus 4.7**: 28% within ±5 min (-22% vs 50% claim). Strict exact-match: 19%.

Our Opus 4.7 result is **below** her claim. Caveats:
- We measured against pixel-perfect known ground truth on rendered clocks; she eyeballed answers on her own screenshot. Her loose-criterion 50% is plausible if she counted close-enough as correct.
- Jing Hu didn't specify Opus version. If she tested 4.6 (older), comparison is moot.
- Our stimulus set mirrors her style categories but isn't her exact pixels.

## Key findings

**1. Per-clock difficulty hierarchy.** Three tiers under the dual rubric:
- *Easiest:* clock_01 (10:10 Arabic chronograph, the watch-ad pose) — 82% across complete-data models.
- *Universally hard:* clock_04 (naked hands, no face) at 8%. No reference frame; models either refuse or guess.
- *Mostly hard but with structure:* clock_08 (mirror) at 18% under dual rubric (was 5% under strict rubric where only 9:45 counted). The accuracy understates the cognitive picture — see finding #2.
- *Mid-difficulty:* clock_03 (24-hour, 18%), clock_07 (11:55, 20%), clock_05 (4:15, 25%), clock_06 (rainbow 6:30, 42%), clock_02 (Roman 3:25, 50%).

**2. The mirror clock splits the cohort by interpretation, not just by accuracy.** Under the dual rubric (both 9:45 mirror-aware and 2:15 template-match are acceptable, since hand positions are 67.5°/90°), the picture is much richer than "all models fail":
- **GPT-5**: 5/10 trials say "2:15" exactly (clean template-match — didn't notice the numerals were mirrored). 4/10 say something close to "9:xx" (saw the mirror, missed the minute). 1 empty.
- **Opus 4.7**: 2/10 close to mirror-aware (9:50). 8/10 say "9:xx" but with wrong minute. **All 10 trials show some mirror-detection** — they read hour as 9, then misread minute.
- **Sonnet 4.6**: 10/10 say "9:xx" (all mirror-aware on hour) but 0/10 get the minute. *Same partial-mirror pattern as Opus.*
- **Haiku 4.5**: 10/10 say "3:xx" — neither mirror-aware nor correct template-match. The 3-position is ~20° off from where the hour hand actually is.
- **The diagnostic signal**: Anthropic models DETECT the mirror partially — they correctly identify the displayed mirrored "9" as the hour position. They then fail to apply the mirror logic consistently to the minute hand. GPT-5 either ignores the mirror entirely (template-match wins) or only partially applies it. This is a *split-application failure*, not a *detection failure*.

**3. The naked-hands clock splits the cohort.** Models either refuse (Sonnet, Haiku) or guess wrong (Opus, GPT-5 mostly say 10:20). The refusals are arguably the *correct* response — without numerals there's no canonical 12-position reference, but the conventional assumption is 12-at-top.

**4. Numeral style sensitivity.** Roman numerals (clock_02) split the cohort: Sonnet 4.6 and GPT-5 read them; Opus 4.7 and Haiku 4.5 mistook V (5) and III (3) for digit values, producing 5:15. This is a *literacy* failure, not a perception failure.

**5. Reading-direction bias on clock_07 (11:55).** Most models said 11:00 instead of 11:55 — they followed the hour hand without correctly reading the minute hand at 11. The minute-hand-points-AT-11-which-is-55-minutes-not-11 reasoning is consistently dropped.

**6. The 24-hour clock confuses everyone except GPT-5.** Outer 24-numeral ring + inner 12-numeral ring at different angular positions defeats most readers. GPT-5 70% (probably the chain-of-thought reasoning helping). Opus and Sonnet collapse into reading the wrong ring.

## Stage 2 framing study — failers identified

- **Opus 4.7** (28%): below 80% — Stage 2 framing variations warranted
- **Sonnet 4.6** (25%): below 80% — Stage 2 framing variations warranted
- **Haiku 4.5** (6%): below 80% — Stage 2 framing variations warranted
- **GPT-5** (72%): below 80% — Stage 2 framing variations warranted

All four complete-data models fail at Stage 1 ceiling. Stage 2 framings (look-harder prime, expert-clockmaker persona, step-by-step, confidence elicitation, negative prime) should be run against the failing model × clock cells where accuracy is below 50%.

## Methodology notes
- Free-text responses, no format constraint, prompt unaltered (per `feedback_never_alter_experimental_prompts.md`).
- AI-judge classification via 7 parallel subagents (per `feedback_ai_judge_for_trial_classification.md`).
- Token budget 4096 per trial — required for reasoning models GPT-5 and Gemini 2.5 Pro that consume ~1000 hidden reasoning tokens before producing visible output. (1024 was insufficient; 1/80 GPT-5 trials still returned empty content even at 4096.)
- Retry-until-N-clean per `feedback_api_trials_retry_until_n.md`. Cohort fixed per `feedback_cohort_scoping_first_round.md`.
- Cost: ~$3-5 in API calls.
