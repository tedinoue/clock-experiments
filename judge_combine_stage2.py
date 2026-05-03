#!/usr/bin/env python3
"""Combine Stage 2 subagent-classified batches into final classified set."""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
JUDGE_DIR = RESULTS_DIR / "judge_batches_stage2"
OUT = RESULTS_DIR / "stage2_classified.json"
COMBINED = RESULTS_DIR / "stage2_combined.json"

all_trials = json.load(open(COMBINED))
trials_by_index = {i: t for i, t in enumerate(all_trials)}

n_loaded = 0
for batch_file in sorted(JUDGE_DIR.glob("batch_*_classified.json")):
    payload = json.load(open(batch_file))
    for c in payload["classifications"]:
        idx = c["trial_index"]
        if idx in trials_by_index:
            trials_by_index[idx]["classification"] = c["classification"]
            trials_by_index[idx]["judge_notes"] = c.get("notes", "")
            n_loaded += 1
print(f"Loaded {n_loaded} classifications")

final = []
for i, t in enumerate(all_trials):
    if "classification" not in t:
        if not t.get("raw_response"):
            t["classification"] = "api_error"
            t["judge_notes"] = t.get("error", "no response")
        else:
            t["classification"] = "unclassified"
            t["judge_notes"] = "missing from judge batches"
    final.append(t)

# Apply dual rubric for clock_08 — re-judge clock_08 trials with the
# same logic as Stage 1's rejudge_clock08.py for consistency.
import re
times_re = re.compile(r'\b(\d{1,2}):(\d{2})\b')
def first_time(text):
    if not text: return None
    m = times_re.search(text)
    if not m: return None
    return int(m.group(1)) % 12, int(m.group(2))

def classify_dual_clock08(time_tuple):
    if time_tuple is None:
        return "refused_or_uncertain", "refused"
    h, m = time_tuple
    targets = [((9, 45), "mirror_aware"), ((2, 15), "template_match")]
    for (th, tm), interp in targets:
        delta = abs((h * 60 + m) - (th * 60 + tm))
        delta = min(delta, 12 * 60 - delta)
        if delta <= 1:
            return "exact_match", interp
        if delta <= 5:
            return "within_5_min", interp
    if h in (9, 8, 10):
        return "wrong_by_more", "mirror_aware_minute_miss"
    if h in (2, 3):
        return "wrong_by_more", "template_match_wrong"
    return "wrong_by_more", "other"

for t in final:
    if t["clock_id"] != "clock_08":
        continue
    if not t.get("raw_response"):
        t.setdefault("interpretation", "no_response")
        continue
    parsed = first_time(t["raw_response"])
    new_class, interp = classify_dual_clock08(parsed)
    t["classification"] = new_class
    t["interpretation"] = interp
    t["dual_rubric_parsed"] = f"{parsed[0]:02d}:{parsed[1]:02d}" if parsed else None

with open(OUT, "w") as f:
    json.dump(final, f, indent=2)
print(f"Wrote {OUT}")

from collections import Counter
cls = Counter(t["classification"] for t in final)
print("Distribution:", dict(cls))
