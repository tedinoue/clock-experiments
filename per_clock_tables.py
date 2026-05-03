#!/usr/bin/env python3
"""Per-clock data tables for the clocks experiment.

Produces 8 tables, one per clock, showing accuracy + most-common-wrong-answer
for each (model × condition) cell.

Conditions: S1 (no prime), S2 (combined), S3a (scaffolding-only),
S3b (feature-checking only), S3c (anti-reasoning), S3d (persona+stakes).

Output: salon/files/clocks/PER_CLOCK_TABLES.md
"""
import json, re
from collections import Counter, defaultdict
from pathlib import Path

R = Path(__file__).parent / "results"
OUT = Path(__file__).parent / "PER_CLOCK_TABLES.md"

CLOCKS = ["clock_01","clock_02","clock_03","clock_04",
          "clock_05","clock_06","clock_07","clock_08"]
GT = {
    "clock_01": ("10:10", "Arabic chronograph + 3 subdials"),
    "clock_02": ("03:25", "Roman + red MON window at 3"),
    "clock_03": ("07:50", "24-hour double ring (inner 1-12, outer 24/1-23)"),
    "clock_04": ("08:20", "Naked hands only — no face, no markers"),
    "clock_05": ("04:15", "Vertical red→blue gradient, Arabic, MON|03|MAY at 4-5"),
    "clock_06": ("06:30", "Rainbow horizontal bands, NO numerals, MON|03|MAY"),
    "clock_07": ("11:55", "Plain dark face, slim white hands, MON|03|MAY"),
    "clock_08": ("9:45 OR 2:15 (dual)", "Mirrored Arabic numerals (CCW, glyphs flipped)"),
}

GOOD = {"exact_match", "within_5_min"}
MODELS = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5", "GPT-5", "Gemini 2.5 Pro"]
times_re = re.compile(r"\b(\d{1,2}):(\d{2})\b")

def first_time_str(text):
    if not text: return None
    m = times_re.search(text)
    if not m: return None
    return f"{int(m.group(1)):d}:{m.group(2)}"

# ===== Build classified sets per stage =====

def load_classified_stage(stage_label):
    """Returns list of trials with classification field set."""
    # Stage 1, 2 have unified files
    if stage_label == "1":
        return json.load(open(R / "stage1_classified.json"))
    if stage_label == "2":
        return json.load(open(R / "stage2_classified.json"))
    # Stage 3a, 3b, etc.: build from per-model trial files + judge batches
    trials = []
    pattern = f"clocks_stage{stage_label}_*.json"
    for f in sorted(R.glob(pattern)):
        if "_classified" in f.name: continue
        trials.extend(json.load(open(f)))
    # Build classifications map (model_id, clock_id, trial) → classification
    judge_dir = R / f"judge_batches_stage{stage_label}"
    if not judge_dir.exists():
        return trials
    classifications = {}
    used_keys = set()
    for bf in sorted(judge_dir.glob("batch_*_classified.json")):
        payload = json.load(open(bf))
        in_file = bf.name.replace("_classified", "")
        if not (judge_dir / in_file).exists(): continue
        inp = json.load(open(judge_dir / in_file))
        for c, t in zip(payload["classifications"], inp["trials"]):
            # Match each batch trial to the next unused original trial with same model+clock+response
            for orig in trials:
                key = (orig["model_id"], orig["clock_id"], orig["trial"])
                if key in used_keys: continue
                if (orig["model_id"] == t["model_id"]
                    and orig["clock_id"] == t["clock_id"]
                    and orig.get("raw_response") == t["raw_response"]):
                    classifications[key] = c["classification"]
                    used_keys.add(key)
                    break
    for t in trials:
        key = (t["model_id"], t["clock_id"], t["trial"])
        if key in classifications:
            t["classification"] = classifications[key]
        elif not t.get("raw_response"):
            t["classification"] = "api_error"
        else:
            t["classification"] = "unclassified"
    # Apply dual rubric for clock_08
    for t in trials:
        if t["clock_id"] != "clock_08" or not t.get("raw_response"): continue
        m = times_re.search(t["raw_response"])
        if not m: continue
        h, mn = int(m.group(1)) % 12, int(m.group(2))
        for (th, tm) in [(9,45), (2,15)]:
            d = abs((h*60+mn) - (th*60+tm)); d = min(d, 720-d)
            if d <= 1:
                t["classification"] = "exact_match"; break
            if d <= 5:
                t["classification"] = "within_5_min"; break
        else:
            if t["classification"] not in ("api_error","unclassified","refused_or_uncertain"):
                t["classification"] = "wrong_by_more"
    return trials

stages = {}
for label in ["1", "2", "3a", "3b", "3c", "3d"]:
    try:
        stages[label] = load_classified_stage(label)
        n = len(stages[label])
        n_classed = sum(1 for t in stages[label] if t.get("classification") not in (None, "unclassified", "api_error"))
        print(f"Stage {label}: {n} trials, {n_classed} classified")
    except Exception as e:
        stages[label] = []
        print(f"Stage {label}: not available ({e})")

STAGE_LABELS = {
    "1": "S1 (no prime)",
    "2": "S2 (combined prime)",
    "3a": "S3a (scaffolding only)",
    "3b": "S3b (feature-check only)",
    "3c": "S3c (anti-reasoning)",
    "3d": "S3d (persona + stakes)",
}

def acc_and_top_wrong(trials_for_cell):
    """Returns (accuracy_pct, n_classified, top_wrong_string).
    top_wrong_string lists most common wrong answers like '5:15 (4×), 5:30 (2×)'."""
    if not trials_for_cell:
        return None, 0, "—"
    classified = [t for t in trials_for_cell
                  if t.get("classification") not in (None, "unclassified", "api_error")]
    if not classified:
        return None, 0, "—"
    n = len(classified)
    correct = sum(1 for t in classified if t["classification"] in GOOD)
    a = correct / n
    # Most common wrong-answer times
    wrong_times = [first_time_str(t["raw_response"])
                   for t in classified
                   if t["classification"] == "wrong_by_more" and t.get("raw_response")]
    wrong_times = [t for t in wrong_times if t]
    top = Counter(wrong_times).most_common(2)
    refused = sum(1 for t in classified if t["classification"] == "refused_or_uncertain")
    parts = []
    if top:
        parts.append(", ".join(f"{t} ({c}×)" for t, c in top))
    if refused:
        parts.append(f"{refused}× refused")
    if not parts:
        parts.append("—")
    return a, n, "; ".join(parts)

# Build per-clock tables
out = []
out.append("# Clocks — Per-Clock Data Tables")
out.append("")
out.append("Each table shows accuracy + dominant wrong-answer pattern for one clock across all model × prompting-condition cells. Empty cells = no data yet.")
out.append("")
out.append("**Conditions**:")
for k, v in STAGE_LABELS.items():
    out.append(f"- {v}")
out.append("")
out.append("**Buckets**: exact_match (±1 min) and within_5_min (±5 min) count as correct.")
out.append("")

for cid in CLOCKS:
    gt_time, gt_style = GT[cid]
    out.append(f"## {cid} — {gt_style} — ground truth: **{gt_time}**")
    out.append("")
    # Header
    cols = list(STAGE_LABELS.keys())
    header = ["model"] + [STAGE_LABELS[c] for c in cols]
    out.append("| " + " | ".join(header) + " |")
    out.append("|" + "---|" * len(header))
    for m in MODELS:
        row = [m]
        for label in cols:
            cell_trials = [t for t in stages.get(label, [])
                           if t.get("model_name") == m and t.get("clock_id") == cid]
            a, n, top = acc_and_top_wrong(cell_trials)
            if n == 0:
                row.append("—")
            else:
                pct = f"{a*100:.0f}%"
                if n < 10:
                    pct += f" (n={n})"
                cell = f"**{pct}**"
                if a < 1.0 and top != "—":
                    cell += f"<br>wrong: {top}"
                row.append(cell)
        out.append("| " + " | ".join(row) + " |")
    out.append("")
    out.append("---")
    out.append("")

with open(OUT, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {OUT}")
