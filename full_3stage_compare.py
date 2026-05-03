#!/usr/bin/env python3
"""Full 4-model Stage 1 → 2 → 3a comparison (Opus, Sonnet, Haiku, GPT-5)."""
import json, re
from collections import defaultdict
from pathlib import Path

R = Path(__file__).parent / "results"
CLOCKS = ["clock_01","clock_02","clock_03","clock_04",
          "clock_05","clock_06","clock_07","clock_08"]
GT = {"clock_01":"10:10","clock_02":"03:25","clock_03":"07:50","clock_04":"08:20",
      "clock_05":"04:15","clock_06":"06:30","clock_07":"11:55","clock_08":"9:45/2:15"}
GOOD = {"exact_match","within_5_min"}

# === Build Stage 3a classified set ===
def load_classifications_for(stage_label, batches_dir):
    """Build (model_id, clock_id, trial) → classification map."""
    out = {}
    for bf in sorted((R / batches_dir).glob("batch_*_classified.json")):
        payload = json.load(open(bf))
        in_file = bf.name.replace("_classified", "")
        inp = json.load(open(R / batches_dir / in_file))
        for c, t in zip(payload["classifications"], inp["trials"]):
            # Match trial back to original combined data
            stage_combined_path = R / f"stage{stage_label}_combined.json"
            if not stage_combined_path.exists(): continue
            combined = json.load(open(stage_combined_path))
            for orig in combined:
                if (orig["model_id"] == t["model_id"]
                    and orig["clock_id"] == t["clock_id"]
                    and orig.get("raw_response") == t["raw_response"]):
                    key = (orig["model_id"], orig["clock_id"], orig["trial"])
                    out[key] = c["classification"]
                    break
    return out

# Stage 3a: re-aggregate (Anthropic + GPT-5 partial)
s3a_combined = []
for f in sorted(R.glob("clocks_stage3a_*.json")):
    s3a_combined.extend(json.load(open(f)))
with open(R / "stage3a_combined.json", "w") as fp:
    json.dump(s3a_combined, fp, indent=2)

s3a_classifications = load_classifications_for("3a", "judge_batches_stage3a")

# Apply
times_re = re.compile(r"\b(\d{1,2}):(\d{2})\b")
def first_time(text):
    if not text: return None
    m = times_re.search(text)
    return (int(m.group(1)) % 12, int(m.group(2))) if m else None

def reclass_clock08(t):
    if t["clock_id"] != "clock_08" or not t.get("raw_response"): return
    parsed = first_time(t["raw_response"])
    if parsed is None:
        t["classification"] = "refused_or_uncertain"; return
    h, m = parsed
    for (th, tm), interp in [((9,45),"mirror_aware"), ((2,15),"template_match")]:
        delta = abs((h*60+m) - (th*60+tm)); delta = min(delta, 720-delta)
        if delta <= 1:
            t["classification"] = "exact_match"; t["interpretation"] = interp; return
        if delta <= 5:
            t["classification"] = "within_5_min"; t["interpretation"] = interp; return
    t["classification"] = "wrong_by_more"

for t in s3a_combined:
    key = (t["model_id"], t["clock_id"], t["trial"])
    if key in s3a_classifications:
        t["classification"] = s3a_classifications[key]
    elif not t.get("raw_response"):
        t["classification"] = "api_error"
    else:
        t["classification"] = "unclassified"
    reclass_clock08(t)

with open(R / "stage3a_classified.json", "w") as fp:
    json.dump(s3a_combined, fp, indent=2)

s1 = json.load(open(R / "stage1_classified.json"))
s2 = json.load(open(R / "stage2_classified.json"))
s3a = s3a_combined

def by_mc(trials):
    m = defaultdict(lambda: defaultdict(int))
    for t in trials:
        m[(t["model_name"], t["clock_id"])][t.get("classification", "?")] += 1
    return m

def acc(counts):
    n = sum(counts.values())
    return None if n == 0 else sum(counts.get(b, 0) for b in GOOD) / n

s1_mc, s2_mc, s3a_mc = by_mc(s1), by_mc(s2), by_mc(s3a)

models = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5", "GPT-5", "Gemini 2.5 Pro"]
out = []
out.append("# Clocks Stage 1 → 2 → 3a comparison (with GPT-5 Stage 3a partial)")
out.append("")
out.append("- **Stage 1**: no system prompt")
out.append("- **Stage 2**: rich combined prime (persona + scaffolding + feature-checking)")
out.append("- **Stage 3a**: scaffolding only (no persona, no feature-checking)")
out.append("")
out.append("## Overall accuracy by model")
out.append("")
out.append("| model | S1 | S2 | S3a | Δ S1→S2 | Δ S1→S3a | Δ S2→S3a |")
out.append("|---|---|---|---|---|---|---|")
for m in models:
    s1t, s2t, s3at = defaultdict(int), defaultdict(int), defaultdict(int)
    n3a = 0
    for c in CLOCKS:
        for b, n in s1_mc[(m, c)].items(): s1t[b] += n
        for b, n in s2_mc[(m, c)].items(): s2t[b] += n
        for b, n in s3a_mc[(m, c)].items(): s3at[b] += n; n3a += n if b not in ("api_error","unclassified") else 0
    a1, a2, a3a = acc(s1t), acc(s2t), acc(s3at)
    s1s = f"{a1*100:.0f}%" if a1 is not None else "—"
    s2s = f"{a2*100:.0f}%" if a2 is not None else "—"
    s3as = f"{a3a*100:.0f}%" if a3a is not None else "—"
    if sum(s3at.values()) and sum(s3at.values()) < 80:
        s3as += f" ({sum(s3at.values())} trials)"
    d12 = f"{(a2-a1)*100:+.0f}pp" if (a1 and a2) else "—"
    d13 = f"{(a3a-a1)*100:+.0f}pp" if (a1 and a3a) else "—"
    d23 = f"{(a3a-a2)*100:+.0f}pp" if (a2 and a3a) else "—"
    out.append(f"| **{m}** | {s1s} | {s2s} | {s3as} | {d12} | {d13} | {d23} |")

out.append("")
out.append("## Per-clock comparison (S1 → S2 → S3a)")
out.append("")
header = ["model", "clock", "gt", "S1", "S2", "S3a"]
out.append("| " + " | ".join(header) + " |")
out.append("|" + "---|" * len(header))
for m in models:
    for c in CLOCKS:
        a1, a2, a3a = acc(s1_mc[(m,c)]), acc(s2_mc[(m,c)]), acc(s3a_mc[(m,c)])
        n1, n2, n3a = sum(s1_mc[(m,c)].values()), sum(s2_mc[(m,c)].values()), sum(s3a_mc[(m,c)].values())
        def cell(a, n):
            if a is None: return "—"
            s = f"{a*100:.0f}%"
            if n < 10: s += f"({n})"
            return s
        out.append(f"| {m} | {c} | {GT[c]} | {cell(a1,n1)} | {cell(a2,n2)} | {cell(a3a,n3a)} |")

p = R.parent / "STAGES_3WAY_COMPARED.md"
with open(p, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {p}")
print("\n".join(out[:25]))
