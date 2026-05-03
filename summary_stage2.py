#!/usr/bin/env python3
"""Generate Stage 2 summary report (parallel structure to summary.py)."""
import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
CLASSIFIED = RESULTS_DIR / "stage2_classified.json"
OUT = Path(__file__).parent / "STAGE_2_RESULTS.md"

CLOCKS = ["clock_01", "clock_02", "clock_03", "clock_04",
          "clock_05", "clock_06", "clock_07", "clock_08"]

GT = {
    "clock_01": ("10:10", "Arabic chronograph"),
    "clock_02": ("03:25", "Roman + date"),
    "clock_03": ("07:50", "24-hour double ring"),
    "clock_04": ("08:20", "Naked hands only"),
    "clock_05": ("04:15", "Gradient + Arabic"),
    "clock_06": ("06:30", "Rainbow no numerals"),
    "clock_07": ("11:55", "Dark face slim hands"),
    "clock_08": ("9:45/2:15", "Mirrored Arabic"),
}

GOOD = {"exact_match", "within_5_min"}
trials = json.load(open(CLASSIFIED))

matrix = defaultdict(lambda: defaultdict(int))
totals = defaultdict(lambda: defaultdict(int))
models_seen = []
for t in trials:
    m = t["model_name"]
    if m not in models_seen: models_seen.append(m)
    matrix[(m, t["clock_id"])][t["classification"]] += 1
    totals[m][t["classification"]] += 1

order = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5", "GPT-5", "Gemini 2.5 Pro"]
models_seen = [m for m in order if m in models_seen] + [m for m in models_seen if m not in order]

def acc(counts):
    n = sum(counts.values())
    return None if n == 0 else sum(counts.get(b, 0) for b in GOOD) / n

def cell(counts, n_required=10):
    n = sum(counts.values())
    if n == 0: return "—"
    a = acc(counts) * 100
    return f"{a:.0f}% ({n})" if n < n_required else f"{a:.0f}%"

partial = {m: sum(totals[m].values()) for m in models_seen
           if sum(totals[m].values()) < len(CLOCKS) * 10}

out = []
out.append("# Clocks Stage 2 — Results")
out.append("")
out.append("**User prompt** (unchanged from Stage 1): `What time does this clock show?`")
out.append("")
out.append("**Stage 2 manipulation:** rich system prompt (expert clockmaker persona + hand-by-hand scaffolding + unusual-feature checking). Full text in `run_stage2.py`.")
out.append("")
out.append(f"**Cohort:** {', '.join(models_seen)}")
out.append("")
if partial:
    out.append("> ⚠️ **PARTIAL DATA**: " + ", ".join(f"{m} ({n} trials)" for m, n in partial.items()))
    out.append("")
out.append(f"Total trials: {len(trials)} (clean: {sum(1 for t in trials if t['classification'] not in ('api_error','unclassified'))})")
out.append("")

out.append("## Accuracy by model × clock (Stage 2)")
out.append("")
header = ["model"] + [f"c{c[6:]}" for c in CLOCKS] + ["overall"]
out.append("| " + " | ".join(header) + " |")
out.append("|" + "---|" * len(header))
out.append("| **gt** | " + " | ".join(GT[c][0] for c in CLOCKS) + " |    |")
for m in models_seen:
    row = [m]
    for c in CLOCKS:
        row.append(cell(matrix[(m, c)]))
    a = acc(totals[m])
    n = sum(totals[m].values())
    overall = f"**{a*100:.0f}%**" if a is not None else "—"
    if n < 80: overall += f" *({n})*"
    row.append(overall)
    out.append("| " + " | ".join(row) + " |")

out.append("")
out.append("## Bucket distribution by model")
out.append("")
out.append("| model | exact | ±5min | wrong | refused | n |")
out.append("|---|---|---|---|---|---|")
for m in models_seen:
    n = sum(totals[m].values())
    em = totals[m].get("exact_match", 0)
    w5 = totals[m].get("within_5_min", 0)
    wr = totals[m].get("wrong_by_more", 0)
    ref = totals[m].get("refused_or_uncertain", 0)
    err = totals[m].get("api_error", 0) + totals[m].get("unclassified", 0)
    pct = lambda x: f"{x*100/max(n-err,1):.0f}%" if (n-err) > 0 else "—"
    extras = f" (api_err: {err})" if err else ""
    out.append(f"| {m} | {em} ({pct(em)}) | {w5} ({pct(w5)}) | {wr} ({pct(wr)}) | {ref} ({pct(ref)}) | {n}{extras} |")

out.append("")
out.append("## Per-clock difficulty (across complete-data models)")
out.append("")
out.append("| clock | style | gt | n | % correct |")
out.append("|---|---|---|---|---|")
complete = [m for m in models_seen if m not in partial]
for c in CLOCKS:
    counts = defaultdict(int)
    for m in complete:
        for b, n in matrix[(m, c)].items(): counts[b] += n
    a = acc(counts)
    out.append(f"| {c} | {GT[c][1]} | {GT[c][0]} | {sum(counts.values())} | {a*100:.0f}% |")

out.append("")
out.append("## Methodology notes")
out.append("- Same image suite, same user prompt, same N as Stage 1.")
out.append("- Only variable: system prompt added.")
out.append("- AI-judge classification via parallel subagents.")
out.append("- Clock_08 dual rubric: 9:45 OR 2:15 both acceptable (both reflect correct hand-position reading; difference is whether the model noticed the mirroring).")

with open(OUT, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {OUT}")
