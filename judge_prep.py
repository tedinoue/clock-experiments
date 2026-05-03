#!/usr/bin/env python3
"""Prepare batches for AI-judge classification.

Splits the combined Stage 1 trials into batches of N, writes each batch
to a JSON file ready for a subagent to classify. Each batch carries its
own ground truth + rubric inline so the subagent has everything it needs
in one prompt.

The subagent is invoked separately per batch and returns a JSON array of
classifications, one per trial in the batch (in input order).
"""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
COMBINED = RESULTS_DIR / "stage1_combined.json"
JUDGE_DIR = RESULTS_DIR / "judge_batches"
JUDGE_DIR.mkdir(exist_ok=True)

BATCH_SIZE = 50  # trials per subagent invocation

GROUND_TRUTH = {
    "clock_01": {"time": "10:10", "style": "Arabic chronograph + 3 subdials, white face. Subdials are decorative. Hour hand near 10, minute hand at 2."},
    "clock_02": {"time": "03:25", "style": "Roman numerals, red MON date window at 3 o'clock, white face. Hour just past III, minute at V."},
    "clock_03": {"time": "07:50", "style": "24-hour double ring (inner Arabic 1-12 standard, outer 24 numerals at 15° intervals with 24 at top, going CW: 1,2,3,...,12 at bottom,...,23). Hour between inner 7 and 8, minute at inner 10. Accept 12-hour 7:50 OR 24-hour 19:50."},
    "clock_04": {"time": "08:20", "style": "Two hands only, no face, no numerals, no markers. Hour toward lower-left (8 position), minute toward lower-right (4 position)."},
    "clock_05": {"time": "04:15", "style": "Vertical red→blue gradient, Arabic numerals, three-cell day-date strip MON|03|MAY at 4-5 o'clock area. Hour at 4, minute at 3."},
    "clock_06": {"time": "06:30", "style": "Rainbow horizontal bands (red top to purple bottom), NO numerals, three-cell day-date strip MON|03|MAY in middle. Both hands point straight down."},
    "clock_07": {"time": "11:55", "style": "Plain dark face, slim white hands, three-cell day-date strip MON|03|MAY just below center. Hour near 12 from 11 side, minute at 11."},
    "clock_08": {"time": "09:45", "style": "Dark face, MIRRORED Arabic numerals (counter-clockwise sequence: 12 at top, 1 to LEFT of 12, 2 below 1, etc., each glyph also flipped horizontally). Mirrored 'NOM' date window left of center. Hands point at the displayed mirrored '9' on the right side. Correct answer is 9:45. A '3:15' answer is wrong — it means the model failed to detect the mirroring."},
}

RUBRIC = """
Classify each response into ONE of these buckets:

- "exact_match": time stated within ±1 minute of ground truth
- "within_5_min": time stated within ±5 minutes (excluding exact_match)
- "wrong_by_more": time stated more than 5 minutes off, OR confidently wrong (e.g., 3:15 when ground truth is 9:45 due to missing the mirror)
- "refused_or_uncertain": declined to answer, said "I can't tell," "approximately X but not sure," etc., without committing to a specific time within ±5 min

Edge cases:
- AM/PM is irrelevant; 7:50 PM = 7:50 = 19:50.
- "ten past ten" = 10:10.
- "10:10:30" = strip seconds, classify on HH:MM.
- For the mirrored clock (clock_08): correct answer is the time as displayed reading the mirrored numerals (so 9:45 when hands point at the mirrored "9"). A "3:15" answer means the model treated it as a normal clock and missed the mirror — that's wrong_by_more.
- For clock_03 (24-hour): accept either 7:50 OR 19:50.
- If the model gives multiple times (e.g., "looks like either 10:10 or 10:08"), use the FIRST committed time stated.
- "About 10:10" or "approximately 10:10" with a specific number → classify on the number, not the hedge.
"""

if not COMBINED.exists():
    print(f"FATAL: {COMBINED} not found. Run aggregate_results.py first.")
    raise SystemExit(2)

trials = json.load(open(COMBINED))
print(f"Loaded {len(trials)} trials")

# Filter to clean trials only — errored trials are reported separately
clean = [t for t in trials if t.get("raw_response")]
errored = [t for t in trials if not t.get("raw_response")]
print(f"Clean: {len(clean)}, errored: {len(errored)}")

# Write batches
for i in range(0, len(clean), BATCH_SIZE):
    batch = clean[i:i+BATCH_SIZE]
    out = JUDGE_DIR / f"batch_{i//BATCH_SIZE:03d}.json"
    payload = {
        "rubric": RUBRIC.strip(),
        "ground_truth": GROUND_TRUTH,
        "trials": [
            {
                "trial_index": i + j,
                "model_id": t["model_id"],
                "model_name": t["model_name"],
                "clock_id": t["clock_id"],
                "ground_truth_time": t["ground_truth"],
                "raw_response": t["raw_response"],
            }
            for j, t in enumerate(batch)
        ],
    }
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  Wrote {out.name} ({len(batch)} trials)")

print(f"\n{(len(clean) + BATCH_SIZE - 1) // BATCH_SIZE} batches written to {JUDGE_DIR}")
