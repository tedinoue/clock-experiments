#!/usr/bin/env python3
"""Compare Anthropic models across Stage 1 (no prime), Stage 2 (combined prime),
Stage 3a (scaffolding only)."""
import json
import re
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"

CLOCKS = ["clock_01", "clock_02", "clock_03", "clock_04",
          "clock_05", "clock_06", "clock_07", "clock_08"]
GT = {
    "clock_01": "10:10", "clock_02": "03:25", "clock_03": "07:50",
    "clock_04": "08:20", "clock_05": "04:15", "clock_06": "06:30",
    "clock_07": "11:55", "clock_08": "9:45/2:15",
}
GOOD = {"exact_match", "within_5_min"}
ANTHROPIC = {"Opus 4.7", "Sonnet 4.6", "Haiku 4.5"}

# Combine stage 3a judge batches into a classified set
stage3a_combined = json.load(open(RESULTS_DIR / "stage3a_combined.json"))
stage3a_by_index = {i: t for i, t in enumerate(stage3a_combined)}
for batch_file in sorted((RESULTS_DIR / "judge_batches_stage3a").glob("batch_*_classified.json")):
    payload = json.load(open(batch_file))
    for c in payload["classifications"]:
        if c["trial_index"] in stage3a_by_index:
            stage3a_by_index[c["trial_index"]]["classification"] = c["classification"]
            stage3a_by_index[c["trial_index"]]["judge_notes"] = c.get("notes", "")

# Apply dual rubric for clock_08
times_re = re.compile(r'\b(\d{1,2}):(\d{2})\b')
def first_time(text):
    if not text: return None
    m = times_re.search(text)
    if not m: return None
    return int(m.group(1)) % 12, int(m.group(2))

def reclassify_clock08(t):
    if t["clock_id"] != "clock_08": return
    if not t.get("raw_response"):
        t.setdefault("interpretation", "no_response"); return
    parsed = first_time(t["raw_response"])
    if parsed is None:
        t["classification"] = "refused_or_uncertain"; return
    h, m = parsed
    targets = [((9, 45), "mirror_aware"), ((2, 15), "template_match")]
    for (th, tm), interp in targets:
        delta = abs((h * 60 + m) - (th * 60 + tm))
        delta = min(delta, 12 * 60 - delta)
        if delta <= 1:
            t["classification"] = "exact_match"; t["interpretation"] = interp; return
        if delta <= 5:
            t["classification"] = "within_5_min"; t["interpretation"] = interp; return
    t["classification"] = "wrong_by_more"

for t in stage3a_by_index.values():
    reclassify_clock08(t)

s1 = json.load(open(RESULTS_DIR / "stage1_classified.json"))
s2 = json.load(open(RESULTS_DIR / "stage2_classified.json"))
s3a = list(stage3a_by_index.values())

def by_mc(trials):
    m = defaultdict(lambda: defaultdict(int))
    for t in trials:
        if t["model_name"] not in ANTHROPIC: continue
        m[(t["model_name"], t["clock_id"])][t.get("classification", "?")] += 1
    return m

def acc(counts):
    n = sum(counts.values())
    return None if n == 0 else sum(counts.get(b, 0) for b in GOOD) / n

s1_mc, s2_mc, s3a_mc = by_mc(s1), by_mc(s2), by_mc(s3a)

models = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5"]

print("# Anthropic 3-stage comparison: Stage 1 (no prime) → Stage 2 (full prime) → Stage 3a (scaffolding only)")
print()
print("| model | clock | gt | S1 | S2 | S3a | Δ S1→S2 | Δ S1→S3a |")
print("|---|---|---|---|---|---|---|---|")
for m in models:
    for c in CLOCKS:
        a1 = acc(s1_mc[(m, c)])
        a2 = acc(s2_mc[(m, c)])
        a3a = acc(s3a_mc[(m, c)])
        a1s = f"{a1*100:.0f}%" if a1 is not None else "—"
        a2s = f"{a2*100:.0f}%" if a2 is not None else "—"
        a3as = f"{a3a*100:.0f}%" if a3a is not None else "—"
        d12 = f"{(a2-a1)*100:+.0f}pp" if (a1 is not None and a2 is not None) else ""
        d13 = f"{(a3a-a1)*100:+.0f}pp" if (a1 is not None and a3a is not None) else ""
        print(f"| {m} | {c} | {GT[c]} | {a1s} | {a2s} | {a3as} | {d12} | {d13} |")

print()
print("## Overall per-model")
print()
print("| model | S1 | S2 | S3a | Δ S1→S2 | Δ S1→S3a | Δ S2→S3a |")
print("|---|---|---|---|---|---|---|")
for m in models:
    s1t = defaultdict(int); s2t = defaultdict(int); s3at = defaultdict(int)
    for c in CLOCKS:
        for b, n in s1_mc[(m, c)].items(): s1t[b] += n
        for b, n in s2_mc[(m, c)].items(): s2t[b] += n
        for b, n in s3a_mc[(m, c)].items(): s3at[b] += n
    a1, a2, a3a = acc(s1t), acc(s2t), acc(s3at)
    d12 = (a2-a1)*100 if (a1 and a2) else 0
    d13 = (a3a-a1)*100 if (a1 and a3a) else 0
    d23 = (a3a-a2)*100 if (a2 and a3a) else 0
    print(f"| **{m}** | {a1*100:.0f}% | {a2*100:.0f}% | {a3a*100:.0f}% | {d12:+.0f}pp | {d13:+.0f}pp | {d23:+.0f}pp |")
