# Clocks — Per-Clock Data Tables

Each table shows accuracy + dominant wrong-answer pattern for one clock across all model × prompting-condition cells. Empty cells = no data yet.

**Conditions**:
- S1 (no prime)
- S2 (combined prime)
- S3a (scaffolding only)
- S3b (feature-check only)
- S3c (anti-reasoning)
- S3d (persona + stakes)

**Buckets**: exact_match (±1 min) and within_5_min (±5 min) count as correct.

## clock_01 — Arabic chronograph + 3 subdials — ground truth: **10:10**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| Sonnet 4.6 | **100%** | **100%** | **100%** | **90%**<br>wrong: 2:50 (1×) | **100%** | **30%**<br>wrong: 2:50 (7×) |
| Haiku 4.5 | **30%**<br>wrong: 9:10 (4×), 4:10 (3×) | **40%**<br>wrong: 10:30 (1×), 12:15 (1×) | **10%**<br>wrong: 10:30 (6×), 4:30 (2×) | **40%**<br>wrong: 10:30 (6×) | **100%** | **10%**<br>wrong: 10:30 (9×) |
| GPT-5 | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| Gemini 2.5 Pro | **100% (n=9)** | **100%** | **100%** | — | — | — |

---

## clock_02 — Roman + red MON window at 3 — ground truth: **03:25**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **0%**<br>wrong: 5:15 (10×) | **100%** | **90%**<br>wrong: 5:15 (1×) | **80%**<br>wrong: 5:15 (2×) | **0%**<br>wrong: 2:25 (10×) | **50%**<br>wrong: 5:15 (4×), 4:15 (1×) |
| Sonnet 4.6 | **100%** | **10%**<br>wrong: 9:25 (8×), 9:00 (1×) | **0%**<br>wrong: 9:25 (10×) | **30%**<br>wrong: 9:25 (6×), 2:25 (1×) | **100%** | **40%**<br>wrong: 9:25 (2×), 3:26 (1×) |
| Haiku 4.5 | **0%**<br>wrong: 3:00 (7×), 3:15 (3×) | **0%**<br>wrong: 9:15 (6×), 9:45 (1×) | **0%**<br>wrong: 9:15 (8×), 8:15 (2×) | **10%**<br>wrong: 3:15 (5×), 9:15 (4×) | **0%**<br>wrong: 3:15 (9×), 15:00 (1×) | **0%**<br>wrong: 9:15 (7×), 8:15 (3×) |
| GPT-5 | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| Gemini 2.5 Pro | — | **30%**<br>wrong: 2:25 (7×) | **30%**<br>wrong: 2:25 (7×) | — | — | — |

---

## clock_03 — 24-hour double ring (inner 1-12, outer 24/1-23) — ground truth: **07:50**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **0%**<br>wrong: 9:40 (10×) | **0%**<br>wrong: 16:50 (4×), 20:40 (2×) | **90%**<br>wrong: 8:50 (1×) | **60%**<br>wrong: 8:50 (3×), 10:40 (1×) | **0%**<br>wrong: 9:40 (8×), 10:40 (2×) | **70%**<br>wrong: 8:50 (3×) |
| Sonnet 4.6 | **0%**<br>wrong: 10:15 (5×), 22:15 (2×) | **0%**<br>wrong: 10:15 (5×), 10:40 (2×) | **0%**<br>wrong: 10:15 (10×) | **0%**<br>wrong: 10:15 (7×), 22:00 (1×) | **0%**<br>wrong: 10:15 (10×) | **0%**<br>wrong: 10:40 (4×), 10:15 (4×) |
| Haiku 4.5 | **0%**<br>wrong: 10:10 (4×), 10:00 (3×) | **0%**<br>wrong: 10:10 (6×), 22:00 (2×) | **0%**<br>wrong: 10:10 (5×), 9:10 (4×) | **0%**<br>wrong: 10:10 (5×), 10:00 (2×) | **0%**<br>wrong: 10:50 (6×), 10:30 (2×) | **0%**<br>wrong: 10:45 (4×), 3:50 (2×) |
| GPT-5 | **70%**<br>wrong: 7:50 (3×) | **100%** | **100%** | **100% (n=7)** | **70%**<br>wrong: 8:50 (1×), 9:38 (1×) | **78% (n=9)**<br>wrong: 9:38 (1×), 10:39 (1×) |
| Gemini 2.5 Pro | — | **50%**<br>wrong: 15:50 (3×), 20:50 (1×) | **80%**<br>wrong: 3:50 (2×) | — | — | — |

---

## clock_04 — Naked hands only — no face, no markers — ground truth: **08:20**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **0%**<br>wrong: 7:25 (1×), 10:25 (1×); 8× refused | **90%**<br>wrong: 7:22 (1×) | **40%**<br>wrong: 10:25 (5×), 10:20 (1×) | **0%**<br>wrong: 7:20 (1×), 4:40 (1×); 6× refused | **0%**<br>wrong: 10:05 (8×), 10:04 (1×) | **0%**<br>wrong: 8:25 (4×), 9:25 (2×) |
| Sonnet 4.6 | **0%**<br>wrong: 10× refused | **50%**<br>wrong: 10:20 (3×), 8:35 (1×); 1× refused | **10%**<br>wrong: 10:20 (4×), 9:20 (3×) | **0%**<br>wrong: 10:10 (1×); 9× refused | **0%**<br>wrong: 10:10 (10×) | **0%**<br>wrong: 10:20 (4×), 10:22 (3×) |
| Haiku 4.5 | **0%**<br>wrong: 10× refused | **0%**<br>wrong: 10:20 (5×), 10:10 (1×); 4× refused | **0%**<br>wrong: 10:15 (6×), 10:10 (4×) | **0%**<br>wrong: 10× refused | **0%**<br>wrong: 10:10 (6×), 10:00 (2×) | **0%**<br>wrong: 10:10 (10×) |
| GPT-5 | **30%**<br>wrong: 10:20 (3×), 8:20 (2×) | **44% (n=9)**<br>wrong: 7:20 (3×), 7:25 (1×) | **20%**<br>wrong: 7:25 (4×), 7:20 (2×) | **40%**<br>wrong: 7:20 (2×), 8:25 (1×) | **38% (n=8)**<br>wrong: 10:20 (5×) | **38% (n=8)**<br>wrong: 7:22 (2×), 6:24 (1×) |
| Gemini 2.5 Pro | — | **0%**<br>wrong: 10:10 (6×), 10:20 (4×) | **0%**<br>wrong: 10:10 (7×), 10:20 (3×) | — | — | — |

---

## clock_05 — Vertical red→blue gradient, Arabic, MON|03|MAY at 4-5 — ground truth: **04:15**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **0%**<br>wrong: 3:20 (10×) | **80%**<br>wrong: 3:00 (1×), 3:15 (1×) | **60%**<br>wrong: 3:15 (4×) | **10%**<br>wrong: 3:20 (4×), 3:15 (4×) | **0%**<br>wrong: 3:18 (6×), 3:19 (4×) | **0%**<br>wrong: 3:15 (9×), 3:48 (1×) |
| Sonnet 4.6 | **0%**<br>wrong: 3:00 (8×), 3:15 (2×) | **10%**<br>wrong: 3:15 (7×), 3:00 (2×) | **70%**<br>wrong: 3:15 (2×), 3:00 (1×) | **0%**<br>wrong: 3:15 (10×) | **0%**<br>wrong: 3:27 (5×), 3:30 (5×) | **70%**<br>wrong: 3:15 (2×), 3:00 (1×) |
| Haiku 4.5 | **0%**<br>wrong: 3:15 (5×), 3:00 (5×) | **10%**<br>wrong: 3:15 (7×), 4:45 (1×) | **10%**<br>wrong: 3:45 (5×), 3:15 (3×) | **10%**<br>wrong: 3:27 (6×), 3:00 (1×) | **0%**<br>wrong: 3:15 (10×) | **50%**<br>wrong: 3:15 (4×), 3:35 (1×) |
| GPT-5 | **100%** | **100%** | **100%** | **100%** | **100%** | **100%** |
| Gemini 2.5 Pro | — | **40%**<br>wrong: 9:15 (6×) | **50%**<br>wrong: 9:15 (5×) | — | — | — |

---

## clock_06 — Rainbow horizontal bands, NO numerals, MON|03|MAY — ground truth: **06:30**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **100%** | **70%**<br>wrong: 6:40 (1×), 7:00 (1×) | **70%**<br>wrong: 7:30 (3×) | **80%**<br>wrong: 7:30 (2×) | **100%** | **100%** |
| Sonnet 4.6 | **0%**<br>wrong: 12:00 (7×), 12:49 (2×) | **0%**<br>wrong: 12:30 (5×), 11:30 (4×) | **0%**<br>wrong: 11:55 (5×), 11:30 (3×) | **0%**<br>wrong: 12:30 (4×), 10:30 (3×) | **0%**<br>wrong: 12:49 (9×), 12:01 (1×) | **0%**<br>wrong: 11:30 (9×), 10:30 (1×) |
| Haiku 4.5 | **0%**<br>wrong: 3:00 (7×), 12:00 (2×) | **10%**<br>wrong: 6:00 (8×), 12:30 (1×) | **0%**<br>wrong: 6:00 (7×), 12:30 (3×) | **50%**<br>wrong: 6:00 (4×), 3:00 (1×) | **50%**<br>wrong: 6:00 (5×) | **0%**<br>wrong: 12:15 (2×), 10:30 (2×) |
| GPT-5 | **70%**<br>wrong: 6:30 (2×), 5:28 (1×) | **70%**<br>wrong: 5:30 (2×), 7:30 (1×) | **80%**<br>wrong: 5:30 (2×) | **40%**<br>wrong: 5:30 (5×), 4:30 (1×) | **40%**<br>wrong: 5:30 (4×), 5:32 (1×) | **78% (n=9)**<br>wrong: 1:30 (1×), 5:30 (1×) |
| Gemini 2.5 Pro | — | **10%**<br>wrong: 7:30 (9×) | **0%**<br>wrong: 7:30 (9×), 5:30 (1×) | — | — | — |

---

## clock_07 — Plain dark face, slim white hands, MON|03|MAY — ground truth: **11:55**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **0%**<br>wrong: 11:00 (10×) | **80%**<br>wrong: 11:00 (1×), 10:59 (1×) | **20%**<br>wrong: 10:55 (5×), 11:00 (3×) | **10%**<br>wrong: 11:00 (9×) | **0%**<br>wrong: 11:00 (10×) | **80%**<br>wrong: 10:55 (1×), 11:00 (1×) |
| Sonnet 4.6 | **0%**<br>wrong: 12:50 (9×), 12:58 (1×) | **40%**<br>wrong: 11:00 (2×), 10:00 (2×) | **0%**<br>wrong: 10:00 (6×), 10:58 (4×) | **10%**<br>wrong: 11:00 (9×) | **100%** | **0%**<br>wrong: 10:00 (10×) |
| Haiku 4.5 | **20%**<br>wrong: 11:00 (8×) | **20%**<br>wrong: 12:05 (3×), 11:00 (2×) | **0%**<br>wrong: 1:10 (10×) | **10%**<br>wrong: 11:00 (7×), 11:05 (1×) | **100%** | **0%**<br>wrong: 11:05 (5×), 11:10 (3×) |
| GPT-5 | **60%**<br>wrong: 11:55 (3×), 11:00 (1×) | **40%**<br>wrong: 11:00 (5×), 12:55 (1×) | **40%**<br>wrong: 11:00 (6×) | **40%**<br>wrong: 11:00 (6×) | **40%**<br>wrong: 11:00 (6×) | **40%**<br>wrong: 11:00 (6×) |
| Gemini 2.5 Pro | — | **100%** | **100%** | — | — | — |

---

## clock_08 — Mirrored Arabic numerals (CCW, glyphs flipped) — ground truth: **9:45 OR 2:15 (dual)**

| model | S1 (no prime) | S2 (combined prime) | S3a (scaffolding only) | S3b (feature-check only) | S3c (anti-reasoning) | S3d (persona + stakes) |
|---|---|---|---|---|---|---|
| Opus 4.7 | **20%**<br>wrong: 9:10 (4×), 8:50 (2×) | **30%**<br>wrong: 9:10 (4×), 10:00 (2×) | **80%**<br>wrong: 3:10 (1×), 8:50 (1×) | **60%**<br>wrong: 3:10 (2×), 10:45 (1×) | **100%** | **60%**<br>wrong: 10:45 (3×), 3:10 (1×) |
| Sonnet 4.6 | **0%**<br>wrong: 9:00 (10×) | **80%**<br>wrong: 3:00 (2×) | **50%**<br>wrong: 9:00 (5×) | **40%**<br>wrong: 9:00 (5×), 2:45 (1×) | **0%**<br>wrong: 9:00 (6×), 9:02 (4×) | **80%**<br>wrong: 9:00 (2×) |
| Haiku 4.5 | **0%**<br>wrong: 3:00 (10×) | **10%**<br>wrong: 9:00 (3×), 3:00 (2×) | **0%**<br>wrong: 3:00 (7×), 3:30 (1×) | **10%**<br>wrong: 3:45 (5×), 3:00 (2×) | **50%**<br>wrong: 3:00 (3×), 10:10 (2×) | **0%**<br>wrong: 3:15 (7×), 10:15 (1×) |
| GPT-5 | **50%**<br>wrong: 10:10 (2×), 10:15 (2×) | **83% (n=6)**<br>wrong: 10:15 (1×) | **89% (n=9)**<br>wrong: 1:10 (1×) | **71% (n=7)**<br>wrong: 10:45 (1×), 10:15 (1×) | **90%**<br>wrong: 10:10 (1×) | **89% (n=9)**<br>wrong: 1:15 (1×) |
| Gemini 2.5 Pro | — | **10%**<br>wrong: 10:15 (5×), 10:45 (2×) | **0%**<br>wrong: 10:15 (6×), 10:45 (2×); 1× refused | — | — | — |

---

