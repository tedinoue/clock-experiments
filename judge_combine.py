#!/usr/bin/env python3
"""Combine subagent-classified batches into a final classified trial set.

Reads results/judge_batches/batch_NNN_classified.json (written by the
classifier subagent) and combines them, attaching the classification
to each original trial.

Output: results/stage1_classified.json
"""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
JUDGE_DIR = RESULTS_DIR / "judge_batches"
OUT = RESULTS_DIR / "stage1_classified.json"
COMBINED = RESULTS_DIR / "stage1_combined.json"

trials_by_index = {}
all_trials = json.load(open(COMBINED))
for i, t in enumerate(all_trials):
    trials_by_index[i] = t

# Walk classified batches
classified_results = []
unclassified = []
for trial_idx, trial in trials_by_index.items():
    if not trial.get("raw_response"):
        # API errored — leave classification empty
        trial["classification"] = "api_error"
        trial["judge_notes"] = trial.get("error", "no response")
        classified_results.append(trial)
        continue

# Now load judge outputs
n_loaded = 0
for batch_file in sorted(JUDGE_DIR.glob("batch_*_classified.json")):
    payload = json.load(open(batch_file))
    classifications = payload["classifications"]
    for c in classifications:
        idx = c["trial_index"]
        if idx in trials_by_index:
            trials_by_index[idx]["classification"] = c["classification"]
            trials_by_index[idx]["judge_notes"] = c.get("notes", "")
            n_loaded += 1
print(f"Loaded {n_loaded} classifications from judge batches")

# Final assembly: every trial with classification (api_error if no response)
final = []
for i, t in enumerate(all_trials):
    if "classification" not in t:
        if not t.get("raw_response"):
            t["classification"] = "api_error"
            t["judge_notes"] = t.get("error", "no response")
        else:
            t["classification"] = "unclassified"
            t["judge_notes"] = "missing from judge batches"
            unclassified.append(i)
    final.append(t)

print(f"Total trials: {len(final)}")
print(f"Unclassified: {len(unclassified)}")
if unclassified:
    print(f"  indices: {unclassified[:20]}{'...' if len(unclassified)>20 else ''}")

with open(OUT, "w") as f:
    json.dump(final, f, indent=2)
print(f"Wrote {OUT}")
