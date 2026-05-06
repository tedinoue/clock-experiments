# Can frontier AI models read analog clocks?

Raw data, code, and analysis for a controlled experiment across 5 frontier models on 8 analog clocks under 6 prompting conditions. About 2,400 trials.

**Substack writeup:** [What "AI Can't Read Clocks" Actually Means](https://synthsentience.substack.com/p/what-ai-cant-read-clocks-actually) (Synth Sentience, 2026-05-03). The article reads from this repo's data.

**Follow-up (2026-05-05):** see [`followup_05052026/`](followup_05052026/) for the next experimental round, which asks whether dialogic teaching, system-prompt synthesis, or other prompting shapes can REPAIR the failures surfaced in the original. Surfaces hand-identification swap as a separable failure mode, refines the "encoder floor" finding into model-specific perceptual mechanisms, and includes ~1,300 additional trials across Sonnet 4.6 and Opus 4.7. Draft summary paper at [`followup_05052026/PAPER_DRAFT.md`](followup_05052026/PAPER_DRAFT.md).

**Original claim being tested:** [Jing Hu, 2nd Order Thinkers, Substack note 2026-05-03](https://substack.com/@jinghuu/note/c-250006786): *"even with the best and latest LLM, take Claude Opus for example, only got this right at a coin toss."*

## TL;DR

| Model | Cold prompt (S1) | Best prompt | Best condition |
|---|---|---|---|
| Opus 4.7 | 28% | 69% | Combined prime |
| Sonnet 4.6 | 25% | 38% | Anti-reasoning |
| Haiku 4.5 | 6% | 36% | Anti-reasoning |
| GPT-5 | 72% | 79% | Persona+stakes |
| Gemini 2.5 Pro | (n=9) | 45% | Scaffolding |

The "AI can't read clocks" framing conflates default-behavior failure with capability failure. Cold-prompt accuracy dramatically understates capability for the strongest models. Methodical scaffolding can also *break* capability that's natively present in weaker models (Sonnet's Roman-numeral collapse is the cleanest case).

## Repo layout

### Read these first
- **`SUBSTACK_DRAFT.md`** — the article
- **`FINDINGS_SUMMARY.md`** — narrative writeup with implications
- **`PER_CLOCK_TABLES.md`** — 8 tables, one per clock, showing every model × condition cell with the dominant wrong-answer pattern (the actual scientific signal)
- **`GROUND_TRUTH.md`** — what each clock displays + the dual rubric for clock_08

### Stimuli
- `rendered/clock_NN.png` — the 8 clocks used in the experiment (programmatically rendered with PIL, 512×512)
- `native/clock_NN.jpg` — crops of the original Jing Hu screenshot for reference
- `sourceClocks.jpg` — Jing Hu's original screenshot
- `gemini_crops/` — failed Gemini-AI-upscaling attempts that motivated the switch to programmatic rendering (kept for methodology transparency)
- `CLOCKS_MONTAGE_4x2.png` — header image for the article

### Trial harnesses
- `run_stage1.py` — naive baseline (no system prompt)
- `run_stage2.py` — rich combined system prompt (persona + scaffolding + feature-checking)
- `run_stage3.py` — four ablation variants (`--variant a/b/c/d`)

Each script takes `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GOOGLE_API_KEY` from environment, calls the respective APIs with image + prompt, retries transient errors with exponential backoff, saves raw responses to `results/clocks_stage<N>_<model>.json`.

### Analysis pipeline
- `aggregate_results.py` / `aggregate_stage2.py` — combine per-model JSONs
- `judge_prep*.py` — package trials into batches for the AI judge
- `judge_combine*.py` — merge subagent classifications back into trial records
- `summary.py` / `summary_stage2.py` — generate per-stage summary reports
- `compare_stages.py` / `full_3stage_compare.py` / `anthropic_3stage_compare.py` — side-by-side comparisons
- `per_clock_tables.py` — generate per-clock failure-mode tables
- `rejudge_clock08.py` — apply the dual rubric (9:45 OR 2:15) for the mirror clock

### Results
- `results/clocks_stage<N>_<model>.json` — raw model responses (one file per model per stage)
- `results/stage<N>_combined.json` — aggregated across models
- `results/stage<N>_classified.json` — with AI-judge classifications applied
- `results/judge_batches_stage<N>/` — per-batch judge inputs and classified outputs

### Tables (PNG, for the Substack article)
- `tables/table_01_stimulus_set.png`
- `tables/table_02_cohort.png`
- `tables/table_03_headline_results.png`
- `tables/table_04_per_clock_difficulty.png`
- `tables/table_05_sonnet_roman_collapse.png`
- `tables/table_06_opus_ladder.png`
- `tables/table_07_best_per_cell.png`

### Per-stage reports
- `STAGE_1_RESULTS.md`
- `STAGE_2_RESULTS.md`
- `STAGES_COMPARED.md`
- `STAGES_3WAY_COMPARED.md`

## Reproducing the experiment

You'll need API keys for Anthropic, OpenAI, and Google AI Studio.

```bash
export ANTHROPIC_API_KEY=...
export OPENAI_API_KEY=...
export GOOGLE_API_KEY=...

# Stage 1 (no system prompt)
python3 run_stage1.py --n-trials 10

# Stage 2 (rich combined prime)
python3 run_stage2.py --n-trials 10

# Stage 3 ablations
python3 run_stage3.py --variant a --n-trials 10
python3 run_stage3.py --variant b --n-trials 10
python3 run_stage3.py --variant c --n-trials 10
python3 run_stage3.py --variant d --n-trials 10
```

Each stage takes 30 to 90 minutes depending on API load. The Google API was hitting persistent 503 overload during our run window; budget extra time for retries.

For classification, the original experiment used Claude subagents via Claude Code's subscription. To replicate that step without subagent infrastructure, port the `judge_prep*.py` batch payloads to direct Claude API calls or substitute another classifier of your choice. The rubric is published in each `judge_batches_*/batch_*.json` file's `rubric` field.

## Cohort

| Provider | Model | API ID |
|---|---|---|
| Anthropic | Claude Opus 4.7 | `claude-opus-4-7` |
| Anthropic | Claude Sonnet 4.6 | `claude-sonnet-4-6` |
| Anthropic | Claude Haiku 4.5 | `claude-haiku-4-5-20251001` |
| OpenAI | GPT-5 | `gpt-5` |
| Google | Gemini 2.5 Pro | `gemini-2.5-pro` |

## Six conditions tested

| Code | System prompt |
|---|---|
| **S1** | (none) |
| **S2** | Persona + scaffolding + feature-checking (combined) |
| **S3a** | Scaffolding only (hand-by-hand methodical reading) |
| **S3b** | Feature-checking only (notice unusual features) |
| **S3c** | Anti-reasoning ("don't overthink, state HH:MM and stop") |
| **S3d** | Persona + stakes only ("expert clockmaker, accuracy is critical") |

Full prompt text in `run_stage2.py` and `run_stage3.py` (look for `SYSTEM_PROMPT` and `PROMPTS` constants).

## Methodology notes

- **N = 10 trials** per (model × clock × condition).
- **User prompt unchanged** across all conditions: *"What time does this clock show?"* The only experimental variable was the system prompt.
- **Free-text responses**, no format constraint (except S3c which explicitly requested HH:MM).
- **AI-judge classification** into four buckets: exact_match (±1 min), within_5_min, wrong_by_more, refused_or_uncertain.
- **Clock_08 dual rubric:** both 9:45 (mirror-aware reading) and 2:15 (template-match without noticing the mirror) accepted as correct. Either reflects correct hand-position reading; the difference is whether the model noticed the numerals were flipped.
- **Token budget** 4096 per trial — required for reasoning models (GPT-5, Gemini 2.5 Pro) that consume ~1000 hidden reasoning tokens before producing visible output.
- **Retry policy:** transient errors (5xx, 429, timeouts) retried with exponential backoff up to 8 attempts per trial.

## Six findings worth keeping

1. **No universal best prompt.** Each model has a different optimal condition. Cleanest counter to "more reasoning is better."

2. **Capability-breaking by methodology.** Sonnet 4.6 reads Roman numerals correctly 100% on a cold prompt, drops to 0% under methodical scaffolding (systematic IX/III inversion), and recovers to 100% under explicit anti-reasoning. *Any* prompt encouraging deliberation triggers the collapse.

3. **Methodology > stakes > features > nothing (for Opus).** Component-by-component: S1 28% → S3c 37% → S3b 50% → S3d 57% → S3a 66% → S2 69%. Each component contributes additively.

4. **24-hour rule-integration failure.** Clock_03 (24-hour double ring): Sonnet and Haiku always say 10:15 / 10:10 across every condition tested. They detect and describe the dual ring but cannot apply the rule.

5. **Mirror-clock split-application failure.** Anthropic models DETECT the mirror on the hour hand (correctly identify mirrored "9") but fail to apply mirror logic to the minute hand. Gemini explicitly NAMES the mirror in its reasoning then commits to wrong times anyway.

6. **Naked-hands clock unlocks correct refusal under feature-checking.** Without a feature-prompt, models confabulate. With it, they refuse appropriately or read the implied 12-at-top.

## Cost

API spend across all stages: approximately $25 to $35 (rough estimate). Reasoning models GPT-5 + Gemini 2.5 Pro contribute most due to hidden reasoning tokens.

## License

Data, code, and analysis released to public domain (CC0). Use freely for replication, extension, critique, or whatever else.

Source images attribution: `sourceClocks.jpg` is from Jing Hu's Substack note (link above), included for replication transparency.

## Pending work

1. Re-run Gemini Stage 1 (only 9 trials due to API overload during the run window)
2. Re-run Gemini Stages 3b, 3c, 3d for full 5-model coverage
3. Cross-architecture validation of conclusions
4. Possibly extend to larger stimulus sets (e.g., systematic time × style factorial)

Pull requests welcome.
