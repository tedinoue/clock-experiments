#!/usr/bin/env python3
"""Aggregate + batch Stage 3a Anthropic results for partial judging."""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
JUDGE_DIR = RESULTS_DIR / "judge_batches_stage3a"
JUDGE_DIR.mkdir(exist_ok=True)
COMBINED = RESULTS_DIR / "stage3a_combined.json"

BATCH_SIZE = 50

GROUND_TRUTH = {
    "clock_01": {"time": "10:10", "style": "Arabic chronograph + 3 subdials. Hour near 10, minute at 2."},
    "clock_02": {"time": "03:25", "style": "Roman + red MON window at 3. Hour just past III, minute at V."},
    "clock_03": {"time": "07:50", "style": "24-hour double ring (inner 1-12, outer 24/1-23). Hour between inner 7-8, minute at inner 10. Accept 7:50 OR 19:50."},
    "clock_04": {"time": "08:20", "style": "Two hands only, no face. Hour lower-left (8), minute lower-right (4)."},
    "clock_05": {"time": "04:15", "style": "Red→blue gradient + Arabic + MON|03|MAY at 4-5. Hour at 4, minute at 3."},
    "clock_06": {"time": "06:30", "style": "Rainbow horizontal bands, NO numerals, MON|03|MAY in middle. Both hands point straight down — minute at 6 (=30 min), hour just past 6 toward 7. NOTE: at 6:30 hour hand sits LEFT of straight down (going CW from 6 toward 7 sweeps left)."},
    "clock_07": {"time": "11:55", "style": "Dark face slim white hands, MON|03|MAY below center. Hour near 12 from 11 side, minute at 11."},
    "clock_08": {"time": "9:45 OR 2:15", "style": "Dark face MIRRORED Arabic numerals (CCW: 12 top, 1 to LEFT of 12, etc., glyphs flipped). DUAL RUBRIC: 9:45 (mirror-aware) AND 2:15 (template-match) both correct. 3:00 or 3:15 = wrong."},
}

RUBRIC = """
Classify into ONE bucket: exact_match (±1 min), within_5_min (±5 excl. exact), wrong_by_more (>5 OR confidently wrong), refused_or_uncertain.

Edges: Empty → refused. First committed time. Strip seconds. AM/PM irrelevant. Clock 03: 7:50 or 19:50. Clock 06: only 6:30 correct (5:30 is wrong by ~60 min). Clock 08: BOTH 9:45 and 2:15 acceptable.

Stage 3a responses include long methodical reasoning — score on FINAL committed time, not intermediate.
"""

# Read Anthropic Stage 3a results
combined = []
for mid in ["claude-haiku-4-5-20251001", "claude-opus-4-7", "claude-sonnet-4-6"]:
    f = RESULTS_DIR / f"clocks_stage3a_{mid}.json"
    if f.exists():
        d = json.load(open(f))
        combined.extend(d)
        print(f"  {f.name}: {len(d)} trials")

with open(COMBINED, "w") as f:
    json.dump(combined, f, indent=2)

clean = [t for t in combined if t.get("raw_response")]
print(f"Total: {len(combined)}, clean: {len(clean)}")

for i in range(0, len(clean), BATCH_SIZE):
    batch = clean[i:i+BATCH_SIZE]
    out = JUDGE_DIR / f"batch_{i//BATCH_SIZE:03d}.json"
    payload = {
        "rubric": RUBRIC.strip(),
        "ground_truth": GROUND_TRUTH,
        "trials": [
            {"trial_index": i + j, "model_id": t["model_id"], "model_name": t["model_name"],
             "clock_id": t["clock_id"], "ground_truth_time": t["ground_truth"],
             "raw_response": t["raw_response"]}
            for j, t in enumerate(batch)
        ],
    }
    with open(out, "w") as f:
        json.dump(payload, f, indent=2)
    print(f"  {out.name}: {len(batch)} trials")
