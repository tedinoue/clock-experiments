#!/usr/bin/env python3
"""AI-judge classifier for clock-reading trials.

This is run as a tool by the judge (Claude Opus 4.7) to extract final times
and apply the classification rubric. The judge reviews edge cases manually.
"""
import json
import re
from pathlib import Path

BASE = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
HYBRID = BASE / "sonnet_hybrid" / "trials.json"
SYS = BASE / "sonnet_systemprompt" / "trials.json"
OUT = BASE / "judge_classified.json"

# Truth table: (truth_minutes_set, hand_swap_minutes_set) in 12-hour space.
# Each "minutes" is total minutes since 12:00 in [0,720).
def to_min(h, m):
    return ((h % 12) * 60 + m) % 720

# clock -> dict with 'truths' (list of 12-hr minute totals) and 'swaps' (list)
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
    "clock_06": {"truths": [to_min(6, 30)], "swaps": [to_min(6, 30)],  # invisible swap
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


# Extract the model's final stated HH:MM. Strategy: look for the LAST
# H:MM (or HH:MM) appearing in the response, preferring bold/markdown patterns.
TIME_RE = re.compile(r"(\d{1,2})\s*:\s*(\d{2})")


def extract_final_time(text):
    """Return (hours, minutes) in 24-hr-tolerant form, or None.

    Strategy: the LAST HH:MM occurring in the response is taken as the
    model's stated final answer. This is robust because every trial
    in this dataset places the final answer at the end (often with
    "**Time: HH:MM**" or just "**HH:MM**"). Earlier mid-text
    occurrences (e.g. "At 10:30, the hour hand...") are reasoning
    steps, not the final answer.
    """
    if not text:
        return None
    all_t = TIME_RE.findall(text)
    if all_t:
        h, m = all_t[-1]
        return int(h), int(m)
    return None


def to_12hr_min(h, m):
    """Map any (h, m) to 12-hr cyclic minutes. 24-hr accepted."""
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
    # exact: within 1 of any truth
    if min_truth <= 1:
        return "exact", f"matches truth (dist={min_truth} min)"
    # within_5
    if min_truth <= 5:
        return "within_5", f"within 5 of truth (dist={min_truth} min)"
    # hand_swap (only if not also near truth)
    if label == "clock_06":
        # invisible swap; never label hand_swap
        # already handled by exact/within_5 above for 6:30
        pass
    else:
        if min_swap <= 5 and min_truth > 5:
            return "hand_swap", f"matches swap target within {min_swap} min"
    return "wrong_other", f"truth_dist={min_truth}, swap_dist={min_swap}"


def looks_refused(text):
    """Heuristic: model refused or expressed pure uncertainty without a time."""
    if not text:
        return True
    low = text.lower()
    refused_phrases = [
        "i cannot determine", "unable to determine", "cannot read",
        "i can't read", "i'm unable", "i am unable", "no time can be",
    ]
    has_time = bool(TIME_RE.search(text))
    if not has_time:
        return True
    return False  # has a time → not refused


def process(condition_name, path):
    with open(path) as f:
        trials = json.load(f)
    out = []
    for t in trials:
        label = t["label"]
        gt = t.get("ground_truth", TRUTH[label]["truth_str"])
        raw = t.get("raw_response", "")
        if not raw or looks_refused(raw) and not TIME_RE.search(raw or ""):
            extracted = None
            cls = "refused_or_ambiguous"
            extracted_str = None
            notes = "no parseable time"
        else:
            extracted = extract_final_time(raw)
            if extracted is None:
                cls = "refused_or_ambiguous"
                extracted_str = None
                notes = "no time extracted"
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
            "_raw_tail": raw[-200:] if raw else "",
        })
    return out


def main():
    hybrid = process("hybrid", HYBRID)
    heavy = process("heavy_summary", SYS)
    all_trials = hybrid + heavy

    # Per-clock summary
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

    # Strip _raw_tail from output but keep for review
    review_dump = []
    clean = []
    for t in all_trials:
        review_dump.append(t)
        c = {k: v for k, v in t.items() if not k.startswith("_")}
        clean.append(c)

    result = {
        "method": "ai-judge fresh-context, dispatched from main session",
        "judge_model": "claude-opus-4-7[1m]",
        "trials": clean,
        "per_clock_summary": {
            "hybrid": summarize(hybrid),
            "heavy_summary": summarize(heavy),
        },
        "aggregate": {
            "hybrid": aggregate(hybrid),
            "heavy_summary": aggregate(heavy),
        },
    }
    with open(OUT, "w") as f:
        json.dump(result, f, indent=2)

    # Also dump review with tails for the judge to spot-check
    with open(BASE / "_judge_review_tails.json", "w") as f:
        json.dump(review_dump, f, indent=2)
    print(f"Wrote {OUT}")
    print("Hybrid aggregate:", result["aggregate"]["hybrid"])
    print("Heavy aggregate:", result["aggregate"]["heavy_summary"])


if __name__ == "__main__":
    main()
