#!/usr/bin/env python3
"""Re-judge clock_08 trials under the dual-rubric for the mirror clock.

New rubric (per Ted 2026-05-03):
- Both 9:45 (mirror-aware reading) AND 2:15 (template-match reading) are acceptable.
- Tolerance: ±5 min around either acceptable answer.
- Track which interpretation each correct answer used.

Updates `stage1_classified.json` in place, marking clock_08 trials with:
- classification: exact_match / within_5_min / wrong_by_more / refused_or_uncertain
- interpretation: mirror_aware (9:xx) | template_match (2:xx) | template_match_wrong (3:xx, 10:xx, etc.) | other | refused

The interpretation field lets us preserve the original diagnostic value
(separating mirror-aware readers from template-matchers) even though the
correct/wrong axis now accepts both.
"""
import json
import re
from pathlib import Path

CLASSIFIED = Path(__file__).parent / "results/stage1_classified.json"

trials = json.load(open(CLASSIFIED))
times_re = re.compile(r'\b(\d{1,2}):(\d{2})\b')

def first_time(text):
    if not text: return None
    m = times_re.search(text)
    if not m: return None
    h = int(m.group(1)) % 12  # canonicalize 12 to 0
    minute = int(m.group(2))
    return h, minute

def classify_dual(time_tuple):
    """Return (classification, interpretation)."""
    if time_tuple is None:
        return "refused_or_uncertain", "refused"
    h, m = time_tuple
    # Acceptable: 9:45 (mirror-aware) or 2:15 (template-match), ±5 min
    targets = [
        ((9, 45), "mirror_aware"),
        ((2, 15), "template_match"),
    ]
    for (th, tm), interp in targets:
        # minute distance
        delta = abs((h * 60 + m) - (th * 60 + tm))
        # Handle 12-hour wrap (e.g., 11:55 vs 12:05 = 10 min apart not 11h50m)
        delta = min(delta, 12 * 60 - delta)
        if delta <= 1:
            return "exact_match", interp
        if delta <= 5:
            return "within_5_min", interp
    # Not within 5 of either acceptable answer.
    # Categorize the WRONG interpretation for analysis:
    if h == 9 or h == 8 or h == 10:
        # close to mirror-aware hour position but minute hand misread
        interp = "mirror_aware_minute_miss"
    elif h == 2 or h == 3:
        # template-match hour neighborhood but wrong reading
        interp = "template_match_wrong"
    else:
        interp = "other"
    return "wrong_by_more", interp

# Patch clock_08 trials
n_changed = 0
n_clock_08 = 0
for t in trials:
    if t["clock_id"] != "clock_08":
        continue
    n_clock_08 += 1
    if not t.get("raw_response"):
        # already api_error or refused; leave as-is
        t.setdefault("interpretation", "no_response")
        continue
    parsed = first_time(t["raw_response"])
    new_class, interp = classify_dual(parsed)
    old_class = t["classification"]
    t["classification"] = new_class
    t["interpretation"] = interp
    t["dual_rubric_parsed"] = f"{parsed[0]:02d}:{parsed[1]:02d}" if parsed else None
    if old_class != new_class:
        n_changed += 1

print(f"clock_08 trials: {n_clock_08}, classifications changed: {n_changed}")

# Save
with open(CLASSIFIED, "w") as f:
    json.dump(trials, f, indent=2)
print(f"Wrote {CLASSIFIED}")

# Print summary distribution
from collections import Counter
cls = Counter()
intr = Counter()
combo = Counter()
for t in trials:
    if t["clock_id"] != "clock_08":
        continue
    cls[t["classification"]] += 1
    intr[t.get("interpretation", "?")] += 1
    combo[(t["model_name"], t.get("interpretation", "?"))] += 1

print("\nClock_08 classification distribution:")
for c, n in cls.most_common():
    print(f"  {c}: {n}")

print("\nClock_08 interpretation distribution:")
for i, n in intr.most_common():
    print(f"  {i}: {n}")

print("\nClock_08 by model × interpretation:")
models = sorted({k[0] for k in combo})
interps = sorted({k[1] for k in combo})
for m in models:
    parts = [f"{i}={combo.get((m,i),0)}" for i in interps if combo.get((m,i),0) > 0]
    print(f"  {m}: {', '.join(parts)}")
