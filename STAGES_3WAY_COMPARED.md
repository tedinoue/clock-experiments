# Clocks Stage 1 → 2 → 3a comparison (with GPT-5 Stage 3a partial)

- **Stage 1**: no system prompt
- **Stage 2**: rich combined prime (persona + scaffolding + feature-checking)
- **Stage 3a**: scaffolding only (no persona, no feature-checking)

## Overall accuracy by model

| model | S1 | S2 | S3a | Δ S1→S2 | Δ S1→S3a | Δ S2→S3a |
|---|---|---|---|---|---|---|
| **Opus 4.7** | 28% | 69% | 66% | +41pp | +39pp | -3pp |
| **Sonnet 4.6** | 25% | 36% | 29% | +11pp | +4pp | -8pp |
| **Haiku 4.5** | 6% | 11% | 2% | +5pp | -4pp | -9pp |
| **GPT-5** | 72% | 75% | 78% | +3pp | +5pp | +3pp |
| **Gemini 2.5 Pro** | 100% | 42% | 65% (20 trials) | -57pp | -35pp | +23pp |

## Per-clock comparison (S1 → S2 → S3a)

| model | clock | gt | S1 | S2 | S3a |
|---|---|---|---|---|---|
| Opus 4.7 | clock_01 | 10:10 | 100% | 100% | 100% |
| Opus 4.7 | clock_02 | 03:25 | 0% | 100% | 90% |
| Opus 4.7 | clock_03 | 07:50 | 0% | 0% | 70% |
| Opus 4.7 | clock_04 | 08:20 | 0% | 90% | 40% |
| Opus 4.7 | clock_05 | 04:15 | 0% | 80% | 60% |
| Opus 4.7 | clock_06 | 06:30 | 100% | 70% | 70% |
| Opus 4.7 | clock_07 | 11:55 | 0% | 80% | 20% |
| Opus 4.7 | clock_08 | 9:45/2:15 | 20% | 30% | 80% |
| Sonnet 4.6 | clock_01 | 10:10 | 100% | 100% | 100% |
| Sonnet 4.6 | clock_02 | 03:25 | 100% | 10% | 0% |
| Sonnet 4.6 | clock_03 | 07:50 | 0% | 0% | 0% |
| Sonnet 4.6 | clock_04 | 08:20 | 0% | 50% | 10% |
| Sonnet 4.6 | clock_05 | 04:15 | 0% | 10% | 70% |
| Sonnet 4.6 | clock_06 | 06:30 | 0% | 0% | 0% |
| Sonnet 4.6 | clock_07 | 11:55 | 0% | 40% | 0% |
| Sonnet 4.6 | clock_08 | 9:45/2:15 | 0% | 80% | 50% |
| Haiku 4.5 | clock_01 | 10:10 | 30% | 40% | 10% |
| Haiku 4.5 | clock_02 | 03:25 | 0% | 0% | 0% |
| Haiku 4.5 | clock_03 | 07:50 | 0% | 0% | 0% |
| Haiku 4.5 | clock_04 | 08:20 | 0% | 0% | 0% |
| Haiku 4.5 | clock_05 | 04:15 | 0% | 10% | 10% |
| Haiku 4.5 | clock_06 | 06:30 | 0% | 10% | 0% |
| Haiku 4.5 | clock_07 | 11:55 | 20% | 20% | 0% |
| Haiku 4.5 | clock_08 | 9:45/2:15 | 0% | 10% | 0% |
| GPT-5 | clock_01 | 10:10 | 100% | 100% | 100% |
| GPT-5 | clock_02 | 03:25 | 100% | 100% | 100% |
| GPT-5 | clock_03 | 07:50 | 70% | 100% | 100% |
| GPT-5 | clock_04 | 08:20 | 30% | 40% | 20% |
| GPT-5 | clock_05 | 04:15 | 100% | 100% | 100% |
| GPT-5 | clock_06 | 06:30 | 70% | 70% | 80% |
| GPT-5 | clock_07 | 11:55 | 60% | 40% | 40% |
| GPT-5 | clock_08 | 9:45/2:15 | 50% | 50% | 80% |
| Gemini 2.5 Pro | clock_01 | 10:10 | 100%(9) | 100% | 100% |
| Gemini 2.5 Pro | clock_02 | 03:25 | — | 30% | 30% |
| Gemini 2.5 Pro | clock_03 | 07:50 | — | 50% | — |
| Gemini 2.5 Pro | clock_04 | 08:20 | — | 0% | — |
| Gemini 2.5 Pro | clock_05 | 04:15 | — | 40% | — |
| Gemini 2.5 Pro | clock_06 | 06:30 | — | 10% | — |
| Gemini 2.5 Pro | clock_07 | 11:55 | — | 100% | — |
| Gemini 2.5 Pro | clock_08 | 9:45/2:15 | — | 10% | — |
