# Clocks Stage 1 — Ground Truth

Stimuli at `salon/files/clocks/rendered/clock_NN.png` (512×512 PNG, programmatically rendered).

Style categories mirror the 8 clocks in Jing Hu's Substack note (https://substack.com/@jinghuu/note/c-250006786) — but with our chosen ground-truth times so we know exactly what each clock displays. This trades replication-fidelity-of-her-pixels for replication-fidelity-of-her-stimulus-categories with known answers.

## Per-clock reference

| Clock | Style | Time (HH:MM, 12-hour) | Date displayed | Notes |
|---|---|---|---|---|
| 01 | Arabic numerals + 3 chronograph subdials, white face | **10:10** | none | Subdials at the 10/2/7 positions are decorative, not functional. Hour hand near 10, minute hand at 2 position. |
| 02 | Roman numerals + red day-window at 3 o'clock, white face | **3:25** | MON | Hour hand just past III, minute hand at V. |
| 03 | 24-hour double ring (inner Arabic 1-12, outer 24/1-2-...-12-...-23 at 15° intervals), white face | **7:50** | none | Hour hand between inner 7 and 8 (lower-left). Minute hand at inner 10 (upper-left). |
| 04 | Two hands only, no face, no border, no markers, white background | **8:20** | none | Hour hand toward lower-left (8 position), minute hand toward lower-right (4 position). No reference points — must be read from hand positions alone. |
| 05 | Vertical red→blue gradient, Arabic numerals, three-cell day-date strip at 4-5 o'clock | **4:15** | MON 03 MAY | Day, date number, month abbreviation horizontally. |
| 06 | Rainbow horizontal bands (red→purple), **no numerals**, three-cell day-date strip in middle | **6:30** | MON 03 MAY | Hands point straight down (both at 6/30 position). Must read from hand position relative to face — no numeral reference. |
| 07 | Plain dark face, slim white hands, three-cell day-date strip just below center | **11:55** | MON 03 MAY | Hour hand near 12 from the 11 side, minute hand at 11. |
| 08 | Dark face, **mirrored Arabic numerals** (counter-clockwise sequence: 12 at top, 1 to LEFT of 12, 2 below 1, etc., each glyph also flipped horizontally), date window left of center with mirrored "MON" | **9:45 OR 2:15** | NOM (mirrored MON) | Two acceptable readings — see rubric below. Hand positions: hour at 67.5° (just past the 2-position in normal-clock terms; or just past mirrored-9 in mirror terms). Minute at 90° (at the 3-position normally; at mirrored-9 in mirror terms). |

## Acceptable-answer rubric (for AI judge)

For each free-text response, the judge classifies into one of:

- **exact_match** — model states a time within 1 minute of ground truth (e.g., 10:10 ground truth → "10:10", "ten ten"). Allow 0–1 min slop.
- **within_5_min** — model states a time within 5 minutes either side (e.g., 10:05 to 10:15 for ground truth 10:10).
- **wrong_by_more** — model states a time more than 5 minutes off, or states a confidently wrong time (e.g., "5:30" for a ground truth of 10:10).
- **refused_or_uncertain** — model declines to answer, says "I can't tell," "the image is unclear," "approximately X but I'm not sure," etc., without committing to a specific time within ±5 minutes.

Edge cases:
- AM/PM is irrelevant (analog clocks don't disambiguate).
- 12:00 vs 0:00 are the same.
- "ten past ten" = 10:10.
- "10:10:30" with seconds — strip seconds, classify by HH:MM.
- For clock 08 (mirrored) — TWO answers are acceptable:
  - **9:45** (mirror-aware): correctly reads the mirrored numerals, identifying the hour hand as pointing at mirrored-9 and minute hand at mirrored-9 (= 45 min in mirror).
  - **2:15** (template-match): treats the clock as if it were a normal clock without examining the numerals. The hour hand is at 67.5° (just past normal-clock "2"); the minute hand at 90° (at normal-clock "3" = 15 min). A reader who didn't notice the numerals were mirrored would correctly read template-match time as 2:15.
  - Either is a valid answer. A "3:15" or "3:00" answer is **wrong_by_more** — these reflect both failure to detect mirror AND misreading the template (since hour hand is at 2-position, not 3-position).
  - Track separately: which interpretation each correct response chose. This distinguishes mirror-aware readers from template-matchers — the original diagnostic value of clock 08.
- For clock 03 (24-hour) — accept either 12-hour or 24-hour answer. 7:50 = 19:50.

## Stimulus generation

- Renderer: `scratch/clock_renderer.py` (deterministic PIL). Each `render_clock_NN_*()` function returns `(path, (hour, minute))`.
- Resolution: 512×512 PNG.
- Source motivation: Jing Hu's screenshot at `salon/files/clocks/sourceClocks.jpg` and her note text claiming "Claude Opus only got this right at a coin toss" on her 8 clocks.
- Replication-fidelity-of-pixels was abandoned after Gemini-based upscaling produced hallucinated content (added subdials, half-mirrored numerals). Programmatic rendering gives pixel-perfect ground truth at the cost of "her exact 8 clocks."
