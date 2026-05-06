#!/usr/bin/env python3
"""AI-judge classifier for ORIGINAL 2026-05-03 single-shot Sonnet clock trials.

Adapted from judge_classify.py to handle the 6 stage1/2/3a/3b/3c/3d files
and produce judge_classified_original.json.

The judge (Claude Opus 4.7) uses this as a tool, then reviews flagged cases
manually before finalizing.
"""
import json
import re
from pathlib import Path

RESULTS = Path("/Users/tedinoue/work/claude-workspace/salon/files/clocks/results")
OUT_BASE = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")

CONDITIONS = [
    ("S1",  RESULTS / "clocks_stage1_claude-sonnet-4-6.json"),
    ("S2",  RESULTS / "clocks_stage2_claude-sonnet-4-6.json"),
    ("S3a", RESULTS / "clocks_stage3a_claude-sonnet-4-6.json"),
    ("S3b", RESULTS / "clocks_stage3b_claude-sonnet-4-6.json"),
    ("S3c", RESULTS / "clocks_stage3c_claude-sonnet-4-6.json"),
    ("S3d", RESULTS / "clocks_stage3d_claude-sonnet-4-6.json"),
]


def to_min(h, m):
    return ((h % 12) * 60 + m) % 720


TRUTH = {
    "clock_01": {"truths": [to_min(10, 10)], "swaps": [to_min(2, 50), to_min(2, 51)],
                 "truth_str": "10:10"},
    "clock_02": {"truths": [to_min(3, 25)], "swaps": [to_min(5, 15), to_min(5, 17)],
                 "truth_str": "3:25"},
    "clock_03": {"truths": [to_min(7, 50)], "swaps": [to_min(10, 35), to_min(10, 39)],
                 "truth_str": "7:50"},
    "clock_04": {"truths": [to_min(8, 20)], "swaps": [to_min(4, 40), to_min(4, 42)],
                 "truth_str": "8:20"},
    "clock_05": {"truths": [to_min(4, 15)], "swaps": [to_min(3, 20), to_min(3, 21)],
                 "truth_str": "4:15"},
    "clock_06": {"truths": [to_min(6, 30)], "swaps": [to_min(6, 30)],  # invisible
                 "truth_str": "6:30"},
    "clock_07": {"truths": [to_min(11, 55)], "swaps": [to_min(11, 0)],
                 "truth_str": "11:55"},
    "clock_08": {"truths": [to_min(9, 45), to_min(2, 15)],
                 "swaps": [to_min(9, 49), to_min(3, 11)],
                 "truth_str": "9:45 OR 2:15"},
}


def cyclic_dist(a, b, mod=720):
    d = abs(a - b) % mod
    return min(d, mod - d)


TIME_RE = re.compile(r"(\d{1,2})\s*:\s*(\d{2})")


def extract_final_time(text):
    """Return (hours, minutes) of the LAST HH:MM in the response, or None."""
    if not text:
        return None
    all_t = TIME_RE.findall(text)
    if all_t:
        h, m = all_t[-1]
        try:
            h = int(h); m = int(m)
        except ValueError:
            return None
        if 0 <= h < 24 and 0 <= m < 60:
            return h, m
        return None
    return None


def to_12hr_min(h, m):
    if 0 <= h < 24 and 0 <= m < 60:
        return ((h % 12) * 60 + m) % 720
    return None


def classify(label, extracted):
    spec = TRUTH[label]
    if extracted is None:
        return "refused_or_ambiguous", "no time extracted"
    h, m = extracted
    em = to_12hr_min(h, m)
    if em is None:
        return "refused_or_ambiguous", f"invalid time {h}:{m:02d}"
    truth_dists = [cyclic_dist(em, t) for t in spec["truths"]]
    swap_dists = [cyclic_dist(em, s) for s in spec["swaps"]]
    min_truth = min(truth_dists)
    min_swap = min(swap_dists)
    if min_truth <= 1:
        return "exact", f"matches truth (dist={min_truth} min)"
    if min_truth <= 5:
        return "within_5", f"within 5 of truth (dist={min_truth} min)"
    if label != "clock_06":
        if min_swap <= 5 and min_truth > 5:
            return "hand_swap", f"matches swap target within {min_swap} min"
    return "wrong_other", f"truth_dist={min_truth}, swap_dist={min_swap}"


def process(condition_name, path):
    with open(path) as f:
        trials = json.load(f)
    out = []
    for t in trials:
        # Original files use 'clock_id', not 'label'
        label = t.get("clock_id") or t.get("label")
        gt = t.get("ground_truth", TRUTH[label]["truth_str"])
        raw = t.get("raw_response", "")
        extracted = extract_final_time(raw)
        if extracted is None:
            cls = "refused_or_ambiguous"
            extracted_str = None
            notes = "no parseable time"
        else:
            h, m = extracted
            extracted_str = f"{h}:{m:02d}"
            cls, notes = classify(label, extracted)
        out.append({
            "condition": condition_name,
            "label": label,
            "trial": t["trial"],
            "ground_truth": gt,
            "extracted_answer": extracted_str,
            "classification": cls,
            "notes": notes,
            "_raw_tail": raw[-300:] if raw else "",
            "_raw_full": raw,
        })
    return out


def summarize(trials):
    per = {}
    for t in trials:
        lab = t["label"]
        per.setdefault(lab, {"exact": 0, "within_5": 0, "hand_swap": 0,
                             "wrong_other": 0, "refused": 0})
        c = t["classification"]
        key = "refused" if c == "refused_or_ambiguous" else c
        per[lab][key] += 1
    return per


def aggregate(trials):
    n = len(trials)
    if n == 0:
        return {}
    ex = sum(1 for t in trials if t["classification"] == "exact")
    w5 = sum(1 for t in trials if t["classification"] in ("exact", "within_5"))
    hs = sum(1 for t in trials if t["classification"] == "hand_swap")
    return {
        "n": n,
        "exact_pct": round(100 * ex / n, 1),
        "exact_or_within5_pct": round(100 * w5 / n, 1),
        "hand_swap_pct": round(100 * hs / n, 1),
    }


def main():
    by_cond = {}
    review_all = []
    for name, path in CONDITIONS:
        trials = process(name, path)
        by_cond[name] = trials
        review_all.extend(trials)

    # Write review file (with raw text) for judge to spot-check
    with open(OUT_BASE / "_judge_review_original_tails.json", "w") as f:
        json.dump(review_all, f, indent=2)

    clean = []
    for t in review_all:
        clean.append({k: v for k, v in t.items() if not k.startswith("_")})

    result = {
        "method": "ai-judge fresh-context, original 2026-05-03 single-shot Sonnet trials",
        "judge_model": "claude-opus-4-7[1m]",
        "trials": clean,
        "per_clock_summary": {n: summarize(by_cond[n]) for n, _ in CONDITIONS},
        "aggregate": {n: aggregate(by_cond[n]) for n, _ in CONDITIONS},
    }
    with open(OUT_BASE / "judge_classified_original.json", "w") as f:
        json.dump(result, f, indent=2)

    print("Wrote judge_classified_original.json")
    for name, _ in CONDITIONS:
        print(f"  {name}: {result['aggregate'][name]}")


if __name__ == "__main__":
    main()
