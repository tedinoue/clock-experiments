#!/usr/bin/env python3
"""Aggregate per-model Stage 1 results into one master JSON for judging."""
import json
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
OUT = RESULTS_DIR / "stage1_combined.json"

combined = []
for f in sorted(RESULTS_DIR.glob("clocks_stage1_*.json")):
    if f.name == OUT.name:
        continue
    data = json.load(open(f))
    combined.extend(data)
    print(f"  {f.name}: {len(data)} trials")

print(f"Total: {len(combined)} trials")
clean = sum(1 for r in combined if r.get("raw_response"))
print(f"Clean: {clean}/{len(combined)}")
errors = [r for r in combined if not r.get("raw_response")]
if errors:
    print(f"Errors ({len(errors)}):")
    for r in errors[:5]:
        print(f"  {r['model_id']} {r['clock_id']} trial={r['trial']} err={r['error']}")

with open(OUT, "w") as f:
    json.dump(combined, f, indent=2)
print(f"Wrote {OUT}")
