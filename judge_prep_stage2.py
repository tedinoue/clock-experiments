#!/usr/bin/env python3
"""Prepare Stage 2 batches for AI-judge classification.

Same rubric as Stage 1 plus the dual rubric for clock_08.
Writes batches to results/judge_batches_stage2/.
"""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
COMBINED = RESULTS_DIR / "stage2_combined.json"
JUDGE_DIR = RESULTS_DIR / "judge_batches_stage2"
JUDGE_DIR.mkdir(exist_ok=True)

BATCH_SIZE = 50

GROUND_TRUTH = {
    "clock_01": {"time": "10:10", "style": "Arabic chronograph + 3 subdials, white face. Subdials are decorative. Hour hand near 10, minute hand at 2."},
    "clock_02": {"time": "03:25", "style": "Roman numerals, red MON date window at 3 o'clock, white face. Hour just past III, minute at V."},
    "clock_03": {"time": "07:50", "style": "24-hour double ring (inner Arabic 1-12 standard, outer 24 numerals at 15° intervals with 24 at top, going CW: 1,2,3,...,12 at bottom,...,23). Hour between inner 7 and 8, minute at inner 10. Accept 12-hour 7:50 OR 24-hour 19:50."},
    "clock_04": {"time": "08:20", "style": "Two hands only, no face, no numerals, no markers. Hour toward lower-left (8 position), minute toward lower-right (4 position)."},
    "clock_05": {"time": "04:15", "style": "Vertical red→blue gradient, Arabic numerals, three-cell day-date strip MON|03|MAY at 4-5 o'clock area. Hour at 4, minute at 3."},
    "clock_06": {"time": "06:30", "style": "Rainbow horizontal bands (red top to purple bottom), NO numerals, three-cell day-date strip MON|03|MAY in middle. Both hands point straight down — minute at 6 (=30 min), hour just past 6 toward 7. NOTE: at 6:30 the hour hand sits to the LEFT of straight down because 7 is at the lower-left position (going CW from 6 toward 7 sweeps left)."},
    "clock_07": {"time": "11:55", "style": "Plain dark face, slim white hands, three-cell day-date strip MON|03|MAY just below center. Hour near 12 from 11 side, minute at 11."},
    "clock_08": {"time": "9:45 OR 2:15", "style": "Dark face, MIRRORED Arabic numerals (counter-clockwise sequence: 12 at top, 1 to LEFT of 12, 2 below 1, etc., each glyph also flipped horizontally). Hand positions: hour at 67.5° (just past 2 in normal terms; just past mirrored-9 in mirror terms). Minute at 90° (at normal-clock 3-position; at mirrored-9). DUAL RUBRIC: both 9:45 (mirror-aware) and 2:15 (template-match) are correct. A 3:15 or 3:00 answer is WRONG (>5 min from both)."},
}

RUBRIC = """
Classify each response into ONE of these buckets:

- "exact_match": time stated within ±1 minute of ground truth
- "within_5_min": time stated within ±5 minutes (excluding exact_match)
- "wrong_by_more": time stated more than 5 minutes off, OR confidently wrong
- "refused_or_uncertain": declined to answer, said "I can't tell," "approximately X but not sure," etc.

Edge cases:
- AM/PM is irrelevant; 7:50 PM = 7:50 = 19:50.
- "ten past ten" = 10:10. Strip seconds. Multiple times → use FIRST committed.
- Clock 03: accept 7:50 OR 19:50.
- Clock 06: ground truth 6:30. The hour hand at 6:30 leans LEFT of straight down (going CW from 6 toward 7 sweeps southwest). 6:30 is the only acceptable answer; 5:30 is WRONG.
- Clock 08: TWO acceptable answers — 9:45 (mirror-aware) AND 2:15 (template-match). Both reflect correct hand-position reading; the difference is whether the model noticed the mirroring. Either counts as correct. A 3:00 or 3:15 answer is wrong (>5 min from both).
"""

trials = json.load(open(COMBINED))
clean = [t for t in trials if t.get("raw_response")]
print(f"Total: {len(trials)}, clean: {len(clean)}")

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
    print(f"  {out.name}: {len(batch)} trials")

print(f"\n{(len(clean) + BATCH_SIZE - 1) // BATCH_SIZE} batches written to {JUDGE_DIR}")
