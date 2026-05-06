"""Score the hybrid and heavy-summary N=10 evals against ground truth.

Per `feedback_ai_judge_for_trial_classification`: regex parsing alone misclassifies
~25% of free-text trials. This script does a first-pass regex extraction with an
explicit final-answer pattern (responses end in **HH:MM** by prompt design), then
flags any response where the extraction is ambiguous or absent for manual review.

Output: per-clock + aggregate accuracy table for each condition; comparison
against the original S1/S2/S3a/S3b/S3c/S3d Sonnet results.
"""
import json
import re
from pathlib import Path

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")

# Truth times (HH, MM). For clock_08 (mirror), both 9:45 and 2:15 are acceptable.
TRUTH = {
    "clock_01": [(10, 10)],
    "clock_02": [(3, 25)],
    "clock_03": [(7, 50)],
    "clock_04": [(8, 20)],
    "clock_05": [(4, 15)],
    "clock_06": [(6, 30)],
    "clock_07": [(11, 55)],
    "clock_08": [(9, 45), (2, 15)],
}

# Original Sonnet single-shot numbers for comparison (% exact, N=10 per cell)
ORIGINAL = {
    "clock_01": {"S1": 100, "S2": 100, "S3a": 100, "S3b": 90, "S3c": 100, "S3d": 30},
    "clock_02": {"S1": 100, "S2": 10, "S3a": 0, "S3b": 30, "S3c": 100, "S3d": 40},
    "clock_03": {"S1": 0, "S2": 0, "S3a": 0, "S3b": 0, "S3c": 0, "S3d": 0},
    "clock_04": {"S1": 0, "S2": 50, "S3a": 10, "S3b": 0, "S3c": 0, "S3d": 0},
    "clock_05": {"S1": 0, "S2": 10, "S3a": 70, "S3b": 0, "S3c": 0, "S3d": 70},
    "clock_06": {"S1": 0, "S2": 0, "S3a": 0, "S3b": 0, "S3c": 0, "S3d": 0},
    "clock_07": {"S1": 0, "S2": 40, "S3a": 0, "S3b": 10, "S3c": 100, "S3d": 0},
    "clock_08": {"S1": 0, "S2": 80, "S3a": 50, "S3b": 40, "S3c": 0, "S3d": 80},
}


def extract_time(text):
    """Extract a HH:MM from the response. Look for the LAST bold-formatted time
    or the last 'Time:' line. Returns (hh, mm) or None if ambiguous."""
    # Bold-formatted time at end (e.g., **10:10** or **The time is 10:10**)
    bold_times = re.findall(r"\*\*[^*]*?(\d{1,2}):(\d{2})[^*]*?\*\*", text)
    if bold_times:
        h, m = bold_times[-1]
        return (int(h) % 12 if int(h) != 12 else 12, int(m))
    # Look for "Time:" pattern
    time_line = re.findall(r"[Tt]ime[^\d]*?(\d{1,2}):(\d{2})", text)
    if time_line:
        h, m = time_line[-1]
        return (int(h) % 12 if int(h) != 12 else 12, int(m))
    # Fall back to last HH:MM in text
    all_times = re.findall(r"\b(\d{1,2}):(\d{2})\b", text)
    if all_times:
        h, m = all_times[-1]
        return (int(h) % 12 if int(h) != 12 else 12, int(m))
    return None


def classify(read, truths):
    """Return 'exact', 'within_5', or 'wrong'. Accept any of the truth tuples."""
    if read is None:
        return "ambiguous"
    rh, rm = read
    for th, tm in truths:
        # Convert to minutes-of-day-12hr; allow wrap-around comparison
        rmin = (rh % 12) * 60 + rm
        tmin = (th % 12) * 60 + tm
        diff = min(abs(rmin - tmin), 12 * 60 - abs(rmin - tmin))
        if diff <= 1:
            return "exact"
        if diff <= 5:
            return "within_5"
    return "wrong"


def score_condition(name, trials_path):
    if not trials_path.exists():
        print(f"  {name}: no data at {trials_path}")
        return None
    trials = json.loads(trials_path.read_text())
    by_clock = {}
    for t in trials:
        clk = t["label"]
        read = extract_time(t["raw_response"])
        verdict = classify(read, TRUTH[clk])
        by_clock.setdefault(clk, []).append((verdict, read, t["raw_response"][-200:]))
    return by_clock


def report(name, by_clock):
    if by_clock is None:
        return
    print(f"\n=== {name} ===")
    print(f"{'clock':<10} {'truth':<10} {'exact':<7} {'wkin5':<7} {'wrong':<7} {'amb':<5} {'rate':<6} {'orig best':<12}")
    total_exact = total_w5 = total_wrong = total_amb = total = 0
    for clk in sorted(by_clock):
        rs = by_clock[clk]
        n = len(rs)
        e = sum(1 for v, _, _ in rs if v == "exact")
        w5 = sum(1 for v, _, _ in rs if v == "within_5")
        wr = sum(1 for v, _, _ in rs if v == "wrong")
        amb = sum(1 for v, _, _ in rs if v == "ambiguous")
        truth_str = "/".join(f"{h}:{m:02d}" for h, m in TRUTH[clk])
        rate = f"{100*e/n:.0f}%"
        orig = ORIGINAL[clk]
        orig_best = f"{max(orig.values())}% ({max(orig, key=orig.get)})"
        print(f"{clk:<10} {truth_str:<10} {e:<7} {w5:<7} {wr:<7} {amb:<5} {rate:<6} {orig_best:<12}")
        total_exact += e; total_w5 += w5; total_wrong += wr; total_amb += amb; total += n
    print("-" * 72)
    print(f"{'TOTAL':<10} {'':<10} {total_exact:<7} {total_w5:<7} {total_wrong:<7} {total_amb:<5} {100*total_exact/total:.1f}%")


if __name__ == "__main__":
    hybrid = score_condition("hybrid", ROOT / "sonnet_hybrid" / "trials.json")
    heavy = score_condition("heavy-summary", ROOT / "sonnet_systemprompt" / "trials.json")
    report("HYBRID (knowledge + anti-reasoning)", hybrid)
    report("HEAVY-SUMMARY (synthesis only)", heavy)

    # Reference table for original Sonnet
    print(f"\n=== ORIGINAL SONNET (N=10 per cell) reference ===")
    print(f"{'clock':<10} {'S1':<5} {'S2':<5} {'S3a':<5} {'S3b':<5} {'S3c':<5} {'S3d':<5}")
    for clk in sorted(ORIGINAL):
        o = ORIGINAL[clk]
        print(f"{clk:<10} {o['S1']:<5} {o['S2']:<5} {o['S3a']:<5} {o['S3b']:<5} {o['S3c']:<5} {o['S3d']:<5}")
    s1_mean = sum(o["S1"] for o in ORIGINAL.values()) / 8
    s2_mean = sum(o["S2"] for o in ORIGINAL.values()) / 8
    s3a_mean = sum(o["S3a"] for o in ORIGINAL.values()) / 8
    s3b_mean = sum(o["S3b"] for o in ORIGINAL.values()) / 8
    s3c_mean = sum(o["S3c"] for o in ORIGINAL.values()) / 8
    s3d_mean = sum(o["S3d"] for o in ORIGINAL.values()) / 8
    envelope = sum(max(o.values()) for o in ORIGINAL.values()) / 8
    print(f"{'MEAN':<10} {s1_mean:<5.1f} {s2_mean:<5.1f} {s3a_mean:<5.1f} {s3b_mean:<5.1f} {s3c_mean:<5.1f} {s3d_mean:<5.1f}")
    print(f"  Best-of-condition envelope (per-cell maximum): {envelope:.1f}%")
