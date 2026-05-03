#!/usr/bin/env python3
"""Stage 1 vs Stage 2 comparison summary.

Reads stage1_classified.json and stage2_classified.json. Produces
side-by-side accuracy by (model × clock), delta, and overall.

Writes salon/files/clocks/STAGES_COMPARED.md.
"""
import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
STAGE1 = RESULTS_DIR / "stage1_classified.json"
STAGE2 = RESULTS_DIR / "stage2_classified.json"
OUT = Path(__file__).parent / "STAGES_COMPARED.md"

CLOCKS = ["clock_01", "clock_02", "clock_03", "clock_04",
          "clock_05", "clock_06", "clock_07", "clock_08"]

GT = {
    "clock_01": "10:10",
    "clock_02": "03:25",
    "clock_03": "07:50",
    "clock_04": "08:20",
    "clock_05": "04:15",
    "clock_06": "06:30",
    "clock_07": "11:55",
    "clock_08": "9:45/2:15",
}

GOOD = {"exact_match", "within_5_min"}

def load(p):
    if not p.exists():
        return None
    return json.load(open(p))

s1 = load(STAGE1) or []
s2 = load(STAGE2) or []

def by_mc(trials):
    m = defaultdict(lambda: defaultdict(int))
    for t in trials:
        m[(t["model_name"], t["clock_id"])][t["classification"]] += 1
    return m

s1_mc = by_mc(s1)
s2_mc = by_mc(s2)

def acc(counts):
    n = sum(counts.values())
    if n == 0: return None
    return sum(counts.get(b, 0) for b in GOOD) / n

def cell(counts):
    if not counts:
        return "—"
    a = acc(counts)
    if a is None: return "—"
    return f"{a*100:.0f}%"

models = []
for t in s1 + s2:
    if t["model_name"] not in models:
        models.append(t["model_name"])
order = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5", "GPT-5", "Gemini 2.5 Pro"]
models = [m for m in order if m in models] + [m for m in models if m not in order]

out = []
out.append("# Clocks Stage 1 vs Stage 2 Comparison")
out.append("")
out.append("**Stage 1**: Naive prompt only, no system prompt.")
out.append("")
out.append("**Stage 2**: Same user prompt + rich system prompt (expert-clockmaker persona + hand-by-hand scaffolding + unusual-feature checking).")
out.append("")
out.append("## Accuracy by model × clock (Stage 1 → Stage 2)")
out.append("")
header = ["model"] + [f"c{c[6:]}" for c in CLOCKS] + ["overall"]
out.append("| " + " | ".join(header) + " |")
out.append("|" + "---|" * len(header))
out.append("| **gt** | " + " | ".join(GT[c] for c in CLOCKS) + " |    |")

for m in models:
    row = [m]
    for c in CLOCKS:
        s1c = s1_mc.get((m, c), {})
        s2c = s2_mc.get((m, c), {})
        s1cell = cell(s1c)
        s2cell = cell(s2c)
        if s1cell == "—" and s2cell == "—":
            row.append("—")
        elif s1cell == s2cell:
            row.append(s1cell)
        else:
            # show both with arrow
            row.append(f"{s1cell}→{s2cell}")
    # overall
    s1total = defaultdict(int)
    s2total = defaultdict(int)
    for c in CLOCKS:
        for b, n in s1_mc.get((m, c), {}).items():
            s1total[b] += n
        for b, n in s2_mc.get((m, c), {}).items():
            s2total[b] += n
    a1 = acc(s1total)
    a2 = acc(s2total)
    overall_str = "—"
    if a1 is not None and a2 is not None:
        overall_str = f"**{a1*100:.0f}% → {a2*100:.0f}%** ({'+' if (a2-a1) >= 0 else ''}{(a2-a1)*100:.0f}pp)"
    elif a1 is not None:
        overall_str = f"**{a1*100:.0f}%** (S1 only)"
    elif a2 is not None:
        overall_str = f"**{a2*100:.0f}%** (S2 only)"
    row.append(overall_str)
    out.append("| " + " | ".join(row) + " |")

out.append("")
out.append("## Per-clock difficulty change (across complete-data models)")
out.append("")
out.append("| clock | gt | Stage 1 | Stage 2 | Δ |")
out.append("|---|---|---|---|---|")
complete = [m for m in models
            if sum(sum(s1_mc.get((m, c), {}).values()) for c in CLOCKS) >= 80
            and sum(sum(s2_mc.get((m, c), {}).values()) for c in CLOCKS) >= 80]
for c in CLOCKS:
    s1c = defaultdict(int)
    s2c = defaultdict(int)
    for m in complete:
        for b, n in s1_mc.get((m, c), {}).items(): s1c[b] += n
        for b, n in s2_mc.get((m, c), {}).items(): s2c[b] += n
    a1 = acc(s1c)
    a2 = acc(s2c)
    if a1 is None or a2 is None:
        out.append(f"| {c} | {GT[c]} | {a1*100 if a1 is not None else '—':.0f}% | {a2*100 if a2 is not None else '—':.0f}% | partial |")
    else:
        out.append(f"| {c} | {GT[c]} | {a1*100:.0f}% | {a2*100:.0f}% | {'+' if a2-a1 >= 0 else ''}{(a2-a1)*100:.0f}pp |")

out.append("")
out.append("## System prompt used in Stage 2")
out.append("")
out.append("Combined three primes — persona induction (expert clockmaker), hand-by-hand scaffolding (identify each hand and its position before committing), and explicit unusual-feature checking (notice mirrors, missing faces, subdials, 24-hour rings before reading time). Full text in `salon/files/clocks/run_stage2.py` SYSTEM_PROMPT constant.")

with open(OUT, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {OUT}")
print()
print("\n".join(out[:40]))
