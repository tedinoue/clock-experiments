# Clocks Stage 2 — Results

**User prompt** (unchanged from Stage 1): `What time does this clock show?`

**Stage 2 manipulation:** rich system prompt (expert clockmaker persona + hand-by-hand scaffolding + unusual-feature checking). Full text in `run_stage2.py`.

**Cohort:** Opus 4.7, Sonnet 4.6, Haiku 4.5, GPT-5, Gemini 2.5 Pro

> ⚠️ **PARTIAL DATA**: Gemini 2.5 Pro (14 trials)

Total trials: 334 (clean: 332)

## Accuracy by model × clock (Stage 2)

| model | c01 | c02 | c03 | c04 | c05 | c06 | c07 | c08 | overall |
|---|---|---|---|---|---|---|---|---|---|
| **gt** | 10:10 | 03:25 | 07:50 | 08:20 | 04:15 | 06:30 | 11:55 | 9:45/2:15 |    |
| Opus 4.7 | 100% | 100% | 0% | 90% | 80% | 70% | 80% | 30% | **69%** |
| Sonnet 4.6 | 100% | 10% | 0% | 50% | 10% | 0% | 40% | 80% | **36%** |
| Haiku 4.5 | 40% | 0% | 0% | 0% | 10% | 10% | 20% | 10% | **11%** |
| GPT-5 | 100% | 100% | 100% | 50% | 100% | 70% | 40% | 60% | **78%** |
| Gemini 2.5 Pro | 100% | 50% (4) | — | — | — | — | — | — | **86%** *(14)* |

## Bucket distribution by model

| model | exact | ±5min | wrong | refused | n |
|---|---|---|---|---|---|
| Opus 4.7 | 48 (60%) | 7 (9%) | 25 (31%) | 0 (0%) | 80 |
| Sonnet 4.6 | 19 (24%) | 10 (12%) | 50 (62%) | 1 (1%) | 80 |
| Haiku 4.5 | 6 (8%) | 3 (4%) | 67 (84%) | 4 (5%) | 80 |
| GPT-5 | 55 (71%) | 7 (9%) | 16 (21%) | 0 (0%) | 80 (api_err: 2) |
| Gemini 2.5 Pro | 12 (86%) | 0 (0%) | 2 (14%) | 0 (0%) | 14 |

## Per-clock difficulty (across complete-data models)

| clock | style | gt | n | % correct |
|---|---|---|---|---|
| clock_01 | Arabic chronograph | 10:10 | 40 | 85% |
| clock_02 | Roman + date | 03:25 | 40 | 52% |
| clock_03 | 24-hour double ring | 07:50 | 40 | 25% |
| clock_04 | Naked hands only | 08:20 | 40 | 48% |
| clock_05 | Gradient + Arabic | 04:15 | 40 | 50% |
| clock_06 | Rainbow no numerals | 06:30 | 40 | 38% |
| clock_07 | Dark face slim hands | 11:55 | 40 | 45% |
| clock_08 | Mirrored Arabic | 9:45/2:15 | 40 | 45% |

## Methodology notes
- Same image suite, same user prompt, same N as Stage 1.
- Only variable: system prompt added.
- AI-judge classification via parallel subagents.
- Clock_08 dual rubric: 9:45 OR 2:15 both acceptable (both reflect correct hand-position reading; difference is whether the model noticed the mirroring).
