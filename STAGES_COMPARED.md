# Clocks Stage 1 vs Stage 2 Comparison

**Stage 1**: Naive prompt only, no system prompt.

**Stage 2**: Same user prompt + rich system prompt (expert-clockmaker persona + hand-by-hand scaffolding + unusual-feature checking).

## Accuracy by model × clock (Stage 1 → Stage 2)

| model | c01 | c02 | c03 | c04 | c05 | c06 | c07 | c08 | overall |
|---|---|---|---|---|---|---|---|---|---|
| **gt** | 10:10 | 03:25 | 07:50 | 08:20 | 04:15 | 06:30 | 11:55 | 9:45/2:15 |    |
| Opus 4.7 | 100% | 0%→100% | 0% | 0%→90% | 0%→80% | 100%→70% | 0%→80% | 20%→30% | **28% → 69%** (+41pp) |
| Sonnet 4.6 | 100% | 100%→10% | 0% | 0%→50% | 0%→10% | 0% | 0%→40% | 0%→80% | **25% → 36%** (+11pp) |
| Haiku 4.5 | 30%→40% | 0% | 0% | 0% | 0%→10% | 0%→10% | 20% | 0%→10% | **6% → 11%** (+5pp) |
| GPT-5 | 100% | 100% | 70%→100% | 30%→40% | 100% | 70% | 60%→40% | 50% | **72% → 75%** (+3pp) |
| Gemini 2.5 Pro | 100% | —→30% | —→50% | —→0% | —→40% | —→10% | —→100% | —→10% | **100% → 42%** (-57pp) |

## Per-clock difficulty change (across complete-data models)

| clock | gt | Stage 1 | Stage 2 | Δ |
|---|---|---|---|---|
| clock_01 | 10:10 | 82% | 85% | +3pp |
| clock_02 | 03:25 | 50% | 52% | +3pp |
| clock_03 | 07:50 | 18% | 25% | +8pp |
| clock_04 | 08:20 | 8% | 45% | +38pp |
| clock_05 | 04:15 | 25% | 50% | +25pp |
| clock_06 | 06:30 | 42% | 38% | -5pp |
| clock_07 | 11:55 | 20% | 45% | +25pp |
| clock_08 | 9:45/2:15 | 18% | 42% | +25pp |

## System prompt used in Stage 2

Combined three primes — persona induction (expert clockmaker), hand-by-hand scaffolding (identify each hand and its position before committing), and explicit unusual-feature checking (notice mirrors, missing faces, subdials, 24-hour rings before reading time). Full text in `salon/files/clocks/run_stage2.py` SYSTEM_PROMPT constant.
