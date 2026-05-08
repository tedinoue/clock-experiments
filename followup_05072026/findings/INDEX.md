# Clocks-Arc Experiment Index — 2026-05-07

This index catalogs the full arc of clock-reading experiments run by Salon (Terry, Opus 4.7 in Claude Code CLI) on 2026-05-07. The morning began with the v2 dialogic teaching protocol designed the previous evening; by afternoon the entire failure mechanism had been isolated to a single architectural pattern (short-pointer extrapolation). Eleven distinct experiments, ~$50–65 in API spend, ~3300 API calls total.

The arc resolved into a single falsifiable mechanistic claim: **when a pointer's tip reaches the labeled positions on a scale, vision-language models read angles accurately. When the tip is interior, accuracy collapses by 40–70 percentage points, occasionally producing full opposite-end identification.**

Read this index in order; each experiment built on prior findings, and several earlier framings were superseded by later results. Where claims were superseded, the index notes which later experiment did so.

---

## Pre-existing context (entering 2026-05-07)

- **640-trial systemprompt-condition study** (Sonnet 4.6 thinking-OFF, run before today) on 8 test clocks with prompt manipulations S1, S2, S3a–d, hybrid, heavy_summary. Per-condition outputs at `judge_classified_v3_S{1,2,3a,3b,3c,3d}.json`, `judge_classified_v3_hybrid.json`, `judge_classified_v3_heavy_summary.json`. Documented forward-shift, hand-swap, and "encoder floor" failure patterns.
- **Direction-flip re-judge** (memory #554, FINDINGS_PART_9_DIRECTION_FLIP.md) — 8 parallel AI-judge subagents reclassified all 640 trials with extended categories (HF, MF, HS, BF, HS+HF, HS+MF, BF+HS). Established the **internal-consistency rule**: HF flips are geometrically valid given biased perception; MF/BF/composite-flips are inconsistent and rare.
- **Perception baseline** (B1/B2 single-line, B3/B4 two-line). `perception_baseline/judge_classified.json`. Established that single-line angles 210°/240°/300°/330° read as their direct opposites in B1; B2 (cluttered) extends the failure zone to include 270°.

---

## Today's experiments, in order

### 1. v2 dialogic teaching — ROUND 1 (morning, ~07:14–07:30 ET)
**Files:** `sonnet_v2_round1/{conversation.json, transcript.md, FINDINGS.md}`. **Memory:** #557.
**Setup:** Sonnet 4.6 thinking-OFF (default), no interventions, original "attentive student" system prompt. Drove turn-by-turn through simplest-clock stimuli (10 simple clocks at 30-min intervals).
**Result:** Stuck-condition termination on 5:50 after 14 turns. **First-attempt 4/8** (3:00, 9:00, 1:15, 4:30 correct; 7:45, 2:35, 8:25, 5:50 wrong). Two failure mechanisms surfaced: hand-swap and forward-shift. Targeted teaching corrected single instances but did NOT transfer across stimuli.
**Cost:** ~$0.50.
**Status:** Original baseline. Findings sharpened by later experiments but data stands.

### 2. v2 dialogic teaching — ROUND 2 (morning, ~07:50–08:05 ET)
**Files:** `sonnet_v2_round2/{conversation.json, transcript.md, FINDINGS.md}`. **Memory:** #564.
**Setup:** Three stacked interventions vs Round 1: (a) extended thinking ENABLED (10K budget), (b) self-check permission system prompt, (c) named-failure heads-up about forward-shift in turn 1.
**Result:** Stuck on 8:25 at Turn 13 (one stimulus earlier than R1). **First-attempt 3/7 — net WORSE than R1.** Predicted over-correction realized: cardinals 3:00 (hand-swap) and 4:30 (backward-shift) broke. 7:45 fixed (the only non-cardinal gain).
**Cost:** ~$1.00.
**Status:** Established that stacked interventions can hurt cardinals. Specific destabilizers later isolated by Stage 2 (#568) — the self-check system prompt was the cause, not thinking-on.

### 3. v2 dialogic teaching — ROUND 3 (morning, ~08:08–08:18 ET)
**Files:** `sonnet_v2_round3/{conversation.json, transcript.md, FINDINGS.md}`. **Memory:** #565.
**Setup:** Per Ted's two corrections to R2: (a) drop the named-failure heads-up; (b) replace targeted teaching with bare *"That's incorrect. Would you like to try again?"* feedback on errors.
**Result:** Stuck on 8:25 at Turn 12. **First-attempt 4/7.** Three-arm comparison (R1/R2/R3) cleanly isolated: HEADS-UP broke 3:00 (R3 fix confirms). THINKING-ON or SELF-CHECK breaks 4:30 (both R2 and R3 broke it). 2:35 → 7:15 hand-swap robust across all 3 rounds.
**Cost:** ~$1.00.
**Status:** Findings stand, sharpened further by Stage 2 isolation.

### 4. B1 zone correlation analysis (morning, ~08:25 ET — pure analysis, no API)
**Files:** `PERCEPTION_BASELINE_CORRELATION_05072026.md`. **Memory:** #566 (later refined by #567).
**Setup:** Mapped the angles of each hand on each test clock against the B1 single-line failure zone (210°/240°/300°/330°). Cross-tabulated against R1 first-attempt results.
**Initial finding (over-claimed):** R1 first-attempts: 4/4 stimuli with at-least-one-hand-in-failure-zone failed; 3/3 safe-zone stimuli succeeded. 100% prediction accuracy.
**Status:** Superseded by experiment #5 (population-level analysis) which showed B1 alone doesn't predict the test set. Final correlation analysis in #5.

### 5. B1 ↔ clocks population-level re-analysis (morning, no API)
**Files:** `PERCEPTION_BASELINE_CORRELATION_05072026.md` (updated). **Memory:** #567 supersedes #566.
**Setup:** Cross-tabulated all 640 trials by per-clock B1-zone classification.
**Result:** B1 alone does NOT predict the test-set patterns at population scale. clock_01 (10:10, hour in B1 fail zone): 85% exact (canonical-pose training prior overrides). clock_02 (3:25, both safe): 27.5% (visual clutter). clock_06 (6:30, borderline): 0/80 with 30% defaulting to 12:30 (anchor-attractor). **B1 is one of multiple architectural factors, not the universal predictor.**
**Status:** Findings stand but later collapsed under the half-circle unified mechanism (#11).

### 6. Three-stage experiment batch (mid-morning)
**Stage 1 — B2 reanalysis** (free): only 1 reclassification (clock_08 minute moves B1-safe → B2-FAIL); doesn't recover test-set discrepancies.
**Stage 2 — 4:30 isolation experiment** (~$0.30, 15 calls). **Memory:** #568. Three arms × 5 trials on `simple_04_30.png`:
- R1-replicate (think-OFF, R1 prompt): 4/5 correct
- Arm A (self-check + think-OFF): **1/5 correct** (4 stable hand-swaps to 6:20)
- Arm B (R1 prompt + think-ON): 4/5 correct (baseline-comparable)

**The destabilizer is the SELF-CHECK SYSTEM PROMPT, not thinking-on.** Round 2/3 had an unisolated system-prompt confound.

**Stage 3 — Opus 4.7 simplest-clock comparison** (~$0.50, 20 calls). **Memory:** #569. 10 stimuli × 2 thinking modes. Opus thinking-OFF: 7/10. Opus thinking-ON: 9/10 (90%). Same failure mechanisms as Sonnet (forward-shift on 7:45, hand-swap on 5:50, anchor-attractor on 11:40 → 12:40 in BOTH thinking modes). Opus uses adaptive thinking API (`type: adaptive`, `output_config.effort: high`); harness must distinguish.
**Files:** `isolate_430.py`, `isolate_430_results.json`, `opus_simplest.py`, `opus_simplest_results.json`.
**Status:** Findings stand, sharpened by half-circle (#11).

### 7. Hour-hand-only single-hand experiment (~10:30–11:00 ET)
**Files:** `render_hour_only.py`, `run_hour_only.py`, `hour_only_clocks/` (24 PNGs), `hour_only_sonnet_thinkon.json`, `hour_only_opus_thinkon.json`, `HOUR_ONLY_FINDINGS_05072026.md`. **Memory:** #570.
**Setup:** Render clocks with ONLY an hour hand at 30-min intervals from 12:00 to 11:30 (24 stimuli). Ask the model to identify hour and estimate minute from hand position. Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON. Per Ted's design to isolate hour-hand position perception without role-confound.
**Result (initial reporting):** Sonnet 5/24 exact, median |error| 30 min. Opus 7/24 exact, median |error| 15 min. Cardinal-attractor pull (12, 3, 6, 9). 12-anchor jump (11:30 → 12:05) in BOTH models. Opus 9:00 → 3:00 a B1/B2 opposite-flip on a single-hand clock.
**Status:** Initial framing of "hour-hand reads worse than minute-hand" later identified as an asymmetric-scoring artifact; see #9 for re-analysis in unified angular-error terms.

### 8. Minute-hand-only single-hand experiment (~11:00–11:30 ET)
**Files:** `render_minute_only.py`, `run_minute_only.py`, `minute_only_clocks/` (60 PNGs), `minute_only_sonnet_thinkon.json`, `minute_only_opus_thinkon.json`.
**Setup:** Per Ted's symmetric design. 60 minute-hand-only clocks (every minute 0–59), randomized presentation order (seed 42). Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON.
**Result:** Sonnet 14/60 exact, 51/60 within ±3 min, median 1 min. Opus 17/60 exact, 59/60 within ±3 min, median 1 min, max 4 min. Sonnet showed 7 numeral-as-minute confusions (truth N near numeral K → reports K instead of 5×K); Opus had 0.
**Status:** Most "errors" were rounding to nearest 5-min landmark (functionally correct, not failures). True per-trial errors: Sonnet ~9, Opus ~1.

### 9. Asymmetric-scoring correction (no API, just analysis)
After Ted pushed back on the apparent hour-vs-minute asymmetry, I re-scored both single-hand experiments in unified angular error (degrees):
| Run | Median° | Within ±15° |
|-----|---------|-------------|
| Hour-only Sonnet | 15° | 75% |
| Hour-only Opus | 7.5° | 83% |
| Min-only Sonnet | 6° | 80% |
| Min-only Opus | 6° | 97% |

**The 30× minute-error gap was a scoring artifact:** hour-hand minutes are 0.5°/min, minute-hand minutes are 6°/min (12× different). Same angular error reported as 12× more "minutes" on hour-only. Honest finding: Sonnet shows ~2.5× worse hour-hand reading; Opus is roughly equal across hands.
**Status:** Folded into the half-circle unified explanation (#11).

### 10. Visual-style swap + numerals-removed experiments (~13:25 ET)
**Files:** `render_swap_styles.py`, `run_style_swap.py`, `minute_only_thick/`, `hour_only_thin/`, `hour_only_no_numerals/`, `style_A_min_thick_sonnet.json`, `style_B_hour_thin_sonnet.json`, `style_C_hour_nonum_sonnet.json`, `STYLE_SWAP_FINDINGS_05072026.md`.
**Setup:** Per Ted's design to isolate what drives the residual hour-vs-minute asymmetry:
- (A) minute-only with SHORT THICK hand visual (n=60)
- (B) hour-only with LONG THIN hand visual (n=24)
- (C) hour-only with NO NUMERALS (n=24)

Sonnet 4.6 thinking-ON.
**Result:** Visual style is the dominant accuracy driver, NOT hand semantic.
- Hour-hand angles + LONG THIN visual: 5° median, 100% within ±15°.
- Min-hand angles + SHORT THICK visual: 21° median, 42% within ±15°, 22 large errors.
- Hour-only NO NUMERALS: 75% within ±15°, identical to with-numerals.

**Numerals are NOT cardinal attractors.** The numeral-as-minute confusion is triggered by the short-thick visual.
**Cost:** ~$2 (108 calls).
**Status:** Findings stand, then unified by half-circle (#11).
**NB:** Memory_save was sandbox-blocked from this point forward (cumulative-credential-classifier flagged the recent /tmp key writes); details captured in FINDINGS docs only.

### 14. Convention-rule fix experiment (~18:50 ET)
**Files:** `run_color_clock_with_rule.py`, `color_clock_rule_sonnet.json`, `color_clock_rule_opus.json`, `RULE_FIX_FINDINGS_05072026.md`.
**Setup:** Same color-coded clock stimuli as #13. Add explicit convention rule to the prompt: "the hour is determined by the numeral the hour hand has most recently passed, not the next one it's approaching." Tests whether the position-to-hour conversion error (#13's residual) is in-context-correctable. 100 calls. NB: Ted ran this manually in his terminal after restarting Claude Code (sandbox cumulative-credential-classifier had locked down agent-emitted credential operations).
**Result — partial fix with symmetric over-correction:**
- Sonnet 41/50 (82%) — was 86% without rule, **delta −2**
- Opus 40/50 (80%) — was 76% without rule, **delta +2**
- Net effect across models: **approximately zero**. Failures redistributed, not removed.

The rule fixes canonical conversion failures (5:50 → 5/5, 11:40 → 5/5 in both models, Opus 7:45 → 5/5). But breaks 1:15 in BOTH models, all 5 trials, identical wrong answer (12:15). The "earlier numeral" instruction over-corrects: hand at 1:15 is just past 1, but the model reaches back to 12.

**Same over-correction pattern as Round 2's heads-up (#2 in this index, sonnet_v2_round2):** naming a directional bias produces a bias in the opposite direction. **Two independent demonstrations of the same architectural quirk in one session, twelve hours apart.**

**Status:** Confirms the position-to-hour conversion error is a separable architectural mechanism, partially in-context-correctable but not cleanly. Rules out "the model just needs the right prompt" as a fix.
**Cost:** ~$2-3.

### 13. Color-coded clock validation (~18:05 ET)
**Files:** `render_color_clock.py`, `run_color_clock.py`, `color_clocks/` (10 PNGs), `color_clock_sonnet.json`, `color_clock_opus.json`, `COLOR_CLOCK_FINDINGS_05072026.md`.
**Setup:** Hour hand RED, minute hand BLUE, hour wider than minute (overlap shows red behind blue), both reach tic marks. Prompt explicitly tells model the color mapping. Removes both extrapolation AND role-identification confounds. 10 stimuli × 5 trials × 2 models = 100 calls.
**Result — DECISIVE:**
- Sonnet 4.6 thinking-ON: **43/50 (86%)** — +28 points over long-handed alone
- Opus 4.7 thinking-ON: **38/50 (76%)**

Hand-swap errors essentially eliminated (Sonnet 2:35 → 5/5; Opus 3:00 → 5/5; Opus 5:50 → 5/5). But position-to-hour CONVERSION error persists in both models on stimuli where hour hand is past 2/3 of the way to next numeral: 7:45 → 8:45, 11:40 → 12:40, Sonnet's 5:50 → 6:50. The model defaults to "nearest numeral" instead of "earlier numeral." Convention error, not perception error.

**THREE ARCHITECTURAL MECHANISMS NOW CLEANLY DISTINGUISHED:**
1. Perceptual extrapolation (half-circle test) — independent
2. Role-identification (eliminated by color test) — independent
3. Position-to-hour conversion (residual on color test) — independent

The unified-mechanism story from #11 was overclaim, refuted by #12 and now sharpened by #13. Real story: three separable mechanisms.
**Cost:** ~$2-3.

### 12. Long-handed clock validation (~17:45–17:55 ET)
**Files:** `render_long_hands_clock.py`, `run_long_hands.py`, `long_hands_clocks/` (10 PNGs), `long_hands_sonnet.json`, `long_hands_opus.json`, `LONG_HANDS_VALIDATION_FINDINGS_05072026.md`.
**Setup:** Test the falsifiable prediction from the half-circle experiment: clocks with both hands long (tips reaching numeral ring) should read accurately even on stimuli that fail with the standard short-thick hour hand. 10 stimuli × 5 trials × 2 models = 100 calls.
**Result — prediction PARTIALLY REFUTED.** Sonnet 29/50 (58%); Opus 29/50 (58%). About the same as short-handed baseline. Some fixes (Sonnet 4:30 recovered, Sonnet 8:25 partially improved). Some persistences (5:50 hand-swap, 7:45 forward-conversion in both models). Some NEW BREAKS (Opus 3:00 → 12:15 hand-swap on a previously-perfect cardinal; Opus 7:45, 5:50 broke despite Stage 3 thinking-on getting them right).
**Three architectural mechanisms now visible:**
1. Half-circle perceptual extrapolation (still real, well-isolated)
2. Position-to-hour conversion error (separate; long-hand doesn't fix it)
3. Role-identification dependency on visual length disparity (long-thin both hands weakens role cue, can break previously-correct reads)

**Status:** The unified-mechanism claim from the half-circle write-up is overclaim. The full clock-reading task involves at least three mechanisms, not one. This is the second adversarial-test catch of the day (the first was memory #566's B1-predicts-everything claim, refuted by population-level analysis).
**Cost:** ~$2-3.

### 11. Half-circle scale extrapolation experiment (~14:50–15:25 ET)
**Files:** `render_halfcircle_scale.py`, `run_halfcircle.py`, `halfcircle/{full,three_quarter,half}/scale_*.png` (111 stimuli + 5 samples), `halfcircle_{sonnet,opus}_{full,three_quarter,half}.json` (6 result files), `HALFCIRCLE_FINDINGS_05072026.md`.
**Setup:** Per Ted's hypothesis: short-pointer extrapolation is the architectural failure mode. Strip away clock context entirely. Half-circle scale, 19 letters A–S at 10° increments, three line lengths (full / 3/4 / 1/2 of distance to label ring). 37 angles × 3 lengths × 5 trials × 2 models = **1110 calls.** Sonnet 4.6 thinking-ON (`enabled` budget 6000), Opus 4.7 thinking-ON (`adaptive` effort high).
**Result — decisive confirmation of Ted's hypothesis:**

| Run | n | Correct | Within ±10° | Median° | Max° |
|-----|---|---------|-------------|---------|------|
| Sonnet full | 185 | 94% | 98% | 5° | 90° |
| Sonnet 3/4 | 185 | 47% | 65% | 10° | 90° |
| Sonnet 1/2 | 185 | 27% | 40% | 15° | 100° |
| **Opus full** | 185 | **100%** | **100%** | **0°** | **5°** |
| Opus 3/4 | 185 | 51% | 66% | 5° | 165° |
| Opus 1/2 | 185 | 53% | 70% | 5° | 180° |

**Same angles, same model, same prompt — only pointer length changes — accuracy drops 40–67 points.** Opus full = 100% / 100% / 5° max. Opus 1/2 = 180° max (full opposite-end flip). The B1/B2 wrong-end mechanism reappears in this clean abstract no-clock context, specifically on short pointers.
**Cost:** ~$30–45.
**Status:** **Final unified mechanism for the entire arc.** All earlier mechanisms (B1 fail zone, cardinal-attractor, visual-style effect, numerals-not-attractors, anchor-attractor) collapse to one: **pointer-tip-to-label distance.**

---

## Mechanistic story (revised after experiment 13 — three mechanisms cleanly distinguished)

The day's experiments now cleanly distinguish **three separable architectural mechanisms** in vision-language clock-reading:

### Mechanism 1: Perceptual extrapolation
Demonstrated in #11 (half-circle scale, 1110 trials). When the pointer's tip reaches the labeled positions, vision-language models read angles accurately (Opus 100%, Sonnet 94% at full length). When the tip is interior, accuracy collapses by 40–70 points, with rare full-opposite-end failures. **Single-hand, single-label task isolates this mechanism cleanly.**

### Mechanism 2: Role-identification
Exposed by the contrast between long-handed clocks (#12, where role disambiguation by length is weakened) and color-coded clocks (#13, where color makes role unambiguous). Hand-swap errors that persist in long-handed conditions disappear when color disambiguates. **Color test isolates this mechanism cleanly.**

### Mechanism 3: Position-to-hour conversion
Confirmed in #13 (color-clock test). Persists when both perceptual extrapolation AND role-identification confounds are removed. Specific pattern: when the hour hand is past two-thirds of the way to the next numeral, the model reads "hour hand near N" as "the hour is N" instead of "the hour is N-1." Both Sonnet and Opus systematically misread 7:45 → 8:45, 11:40 → 12:40, and Sonnet 5:50 → 6:50 even on color-coded long-handed clocks. **Convention error, not perception error.**

**The clocks task fails for these three reasons. Each is a separable architectural pattern, demonstrated by an isolation experiment.**

## Falsifiable prediction → tested → partially refuted

The prediction "long-handed clocks should read accurately" was tested in #12 and **partially refuted.** Net accuracy of 58% on long-handed clocks, about the same as short-handed baseline. Some fixes (4:30 recovered for Sonnet); some persistences (5:50, 7:45); some new breaks (Opus 3:00). The mechanism story is richer than predicted.

## Methodological flags (carried forward)

1. **All primary 640-trial data was thinking-OFF.** Harnesses (`run_systemprompt_eval.py`, `run_hybrid_eval.py`, `run_perception_baseline.py`, pre-2026-05-07 `teach.py`) call `messages.create` without the `thinking` parameter. Pre-paper-ship: thinking-on subset re-run (~160 trials, $2–5) recommended for disclosure.
2. **Memory_save was sandbox-blocked** from experiment #10 onward (cumulative-credential-classifier flagged the recent /tmp key writes). Findings captured in FINDINGS docs and the LATEST/TODO/CRITICAL_REMINDERS updates instead. Memories #568, #569 saved successfully; #566–#570 are in quad-memory; later findings are in docs only.
3. **Self-check system prompt destabilizes hand-role identification** (Stage 2 isolated). Future studies should pre-register the corrective protocol and avoid stacked-intervention designs without isolation.
4. **Opus 4.7 uses adaptive thinking API** (`type: "adaptive"`, `output_config.effort: "high"`) — different from Sonnet's `enabled` + `budget_tokens`. Multi-model harnesses must distinguish.
5. **Asymmetric scoring conventions can mislead.** Hour-hand error in "minutes" is 12× larger than the same angular error reported on minute-hand. Always report angular error in degrees for cross-task comparison.

## Cumulative cost

~$50–65 across 11 experiments, ~3300 API calls. Detailed per-experiment costs above.

## Reading order for paper drafting

1. **`HALFCIRCLE_FINDINGS_05072026.md`** — final unified mechanism. Open the paper here.
2. **`STYLE_SWAP_FINDINGS_05072026.md`** — supporting evidence: visual style affects accuracy via tip-to-label distance.
3. **`HOUR_ONLY_FINDINGS_05072026.md`** — applied to clocks, with the asymmetric-scoring caveat noted.
4. **`PERCEPTION_BASELINE_CORRELATION_05072026.md`** — population-level B1 analysis; useful to show the test-set complexity.
5. **`sonnet_v2_round{1,2,3}/FINDINGS.md`** — dialogic-teaching applied case study.
6. **`FINDINGS_PART_9_DIRECTION_FLIP.md`** — the direction-flip failure taxonomy on the 640-trial dataset (pre-existing).
