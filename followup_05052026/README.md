# Clocks Follow-Up — May 5, 2026

This directory contains the follow-up to the original 2026-05-03 controlled experiment ("What 'AI Can't Read Clocks' Actually Means"). The original experiment surfaced a "scaffolding-can-break-correct" pattern in single-shot prompting. The follow-up asks: can dialogic teaching, system-prompt synthesis, or other prompting shapes REPAIR the failures? And what does it look like at the encoder layer?

Run over a single ~10-hour Salon session on 2026-05-05. ~$13 in total Anthropic API spend.

## What's here

- `PAPER_DRAFT.md` — the summary write-up. Three to four thousand words, discussion-focused, intended for Synth Sentience or a similar venue. Covers the types of error, what was tried, what worked and didn't, and the conclusion about why synths struggle with this stimulus class. Includes an anticipated-objections section. **Status: draft, pending Ted's adversarial-editor pass + cross-architecture red-team validation.**

- `FINDINGS.md` — the comprehensive internal record across 8 parts (~17,000 words). Structured chronologically by experimental phase. The paper draws from this; this is the source-of-truth for all numbers and per-cell results.

- `stimuli/` — all programmatically-rendered stimuli used in this round. Three subsets:
  - `training_clocks/` — 8 clocks at NEW times distinct from the original test set, used for the 24-turn dialogic teaching arc.
  - `held_out_clocks/` — 4 fresh-rendered stimuli used to test transfer of in-session-installed techniques (mirror at 9:50, Roman at 11:40 and 11:20, rainbow no-numerals at 12:55 in two thickness variants).
  - `perception_baseline/{b1,b2,b3,b4}/` — fundamental-perception primitive stimuli isolated from clock semantics. B1/B2 are single-line angle stimuli (12 angles, with and without subdial clutter). B3/B4 are two-line length-comparison stimuli (5 ratios × 2 directions, with and without subdial clutter).

- `trials/` — all recorded model responses and judge classifications.
  - `dialogic_teaching/transcript_sonnet_32_turns.md` — full Terry-driven 32-turn arc with Sonnet 4.6 (24 turns of training + 8 turns testing on the original test set).
  - `single_shot_revisited/` — N=10 follow-up evaluations on the original 8 clocks under three new prompt conditions (heavy-summary, hybrid, and the original 6 conditions re-classified with an expanded category set). Includes raw trials and AI-judge-classified output.
  - `perception_baseline_sonnet/` and `perception_baseline_opus/` — N=10 perception baseline trials for Sonnet 4.6 and Opus 4.7 side by side. 420 trials per model.
  - `perception_baseline_sonnet_and_opus_judge_classified.json` — the AI-judge classification covering all 840 perception baseline trials.

- `code/` — Python harnesses for renderer, runner, and judge tooling. Reusable for replication.

- `ai_judge_prompts/` — reproducibility for the AI-judge subagent dispatches. The classification scheme is reproducible from these prompts.

## What's new in this round vs. the original 2026-05-03 experiment

1. **Hand-identification swap as a separate failure-mode category.** The original AI judge classified each trial as correct, near-correct (within 5 minutes), or wrong. The follow-up adds `hand_swap` as a category for trials where the model's spatial perception is correct but the hour-vs-minute identification is reversed. Re-classifying the original 480 trials with this expanded category surfaces a structural pattern that wasn't visible in the original article: hand-swap rate scales monotonically with prompt weight, from 0% under anti-reasoning prompts to 36% under feature-check methodology.

2. **Dialogic teaching arc.** A 24-turn interactive teaching session with Terry (Opus 4.7) driving Sonnet 4.6 through fresh stimuli, introducing the standard procedure and patches for specific failure modes (length-measurement protocol, mirror-reading convention, base-width-as-backup-cue, Roman-numeral edge disambiguation, no-anchor angle-resolution acknowledgment). The trained student model talks unprompted about each technique in its reasoning text after the arc, but applying those techniques on cold-call test stimuli does not move accuracy above the naive baseline.

3. **Heavy-summary system-prompt evaluation.** The 24-turn teaching arc condensed into a single ~600-word system prompt named every failure mode and its corresponding technique. Run fresh-instance on the original 8 clocks at N=10. Lands at the same accuracy as the in-context version. Long context is not the relevant variable.

4. **Hybrid system-prompt evaluation.** Brief failure-mode enumeration plus an explicit anti-reasoning instruction ("trust your first impression, don't overthink"). Tests whether the suppression effect of failure-mode-naming can be relieved by a counter-instruction. It cannot. Hybrid lands at the same accuracy as heavy-summary.

5. **Fundamental-perception baselines.** Single black hand-style line at 12 angles, with and without chronograph subdial clutter. Two black hand-style lines at 5 length ratios, with and without subdial clutter. Tested on Sonnet 4.6 and Opus 4.7 at N=10 each. Surfaces two encoder-level mechanisms: orientation-dependent endpoint-identification failure, and equal-and-near-equal length false-positive bias.

6. **Cross-model encoder comparison (Sonnet 4.6 vs. Opus 4.7).** The two models have completely different perceptual profiles. Sonnet has a four-angle catastrophic band on lower-half line orientations that subdial clutter mostly worsens. Opus has a narrower band that subdial clutter recovers. Subdials help Opus's angle reading; they hurt Sonnet's. Length comparison inverts: Sonnet near-ceiling at moderate ratios, Opus reverses 9 of 10 trials at 50% length difference with subdials present. The "encoder floor" attributed to specific clocks in the earlier analysis is therefore model-specific, not substrate-wide.

## Headline findings

- Hand-identification swap is a real, separable failure mode that scales monotonically with prompt weight (0% under anti-reasoning, 36% under feature-check methodology).
- Dialogic teaching expands what the model can do under prompting; it does not move what the model does under cold-call.
- Naming a failure mode in a prompt primes the model to look for that mode, which destabilizes correct native perception on stimuli where the mode does not apply. An anti-reasoning instruction in the same prompt cannot subtract this priming effect.
- Sonnet and Opus have distinct, model-specific encoder failure profiles on geometric primitives. The "encoder floor" framing for vision-language models needs to be replaced by a finer-grained model-specific picture.

## Caveats

- N=10 per cell across most evaluations. Confidence intervals are wide. The qualitative findings (hand-swap monotonic, lower-half angle bias for Sonnet, length-comparison failure for Opus) are robust at N=10; per-cell quantitative claims should be interpreted with appropriate uncertainty.
- Sonnet 4.6 was the focus of the dialogic teaching and follow-up evaluations; Opus 4.7 was tested only on the perception baselines. Cross-architecture replication (GPT-5, Gemini 2.5 Pro) on the perception baselines is the natural next step.
- The Opus length-comparison result is striking enough that a render-bug sanity check is warranted before public claims. Visual inspection of the renders confirms correctness, but a fresh-renderer cross-check is prudent before the paper goes external.
- AI-judge classifications were performed by fresh-context subagents with the classification schema given as an explicit prompt. The standing rule for this experimental track (memory `feedback_ai_judge_for_trial_classification`) bans regex-based classification. Replicators should preserve this discipline.

## Reproducing this round

1. Use the renderers in `code/render_*.py` to regenerate the stimuli.
2. Use `code/run_systemprompt_eval.py` and `code/run_hybrid_eval.py` to run the heavy-summary and hybrid conditions. Use `code/run_perception_baseline.py` with `--model claude-sonnet-4-6` or `--model claude-opus-4-7` to run the perception baselines.
3. The dialogic teaching arc is interactive and was driven turn-by-turn from inside a Salon Claude Code session; the transcript is preserved at `trials/dialogic_teaching/`. The harness is `code/teach.py`. Replicating the full dialogic teaching arc would require re-running with judgment-bearing prompts at each turn; this is not a fully-scripted run.
4. The AI judge classifications can be reproduced by reading `ai_judge_prompts/` and dispatching a fresh-context subagent with the included classification schema.
