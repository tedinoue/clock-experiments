#!/usr/bin/env python3
"""AI-judge classifier for N=10 perception baseline (Sonnet + Opus).

Strategy:
- The model was instructed to bold its final answer (e.g., **5**, **up longer**).
- We extract the LAST bolded token in the response and classify by reading the
  surrounding context. Anything that does not yield a confident extraction is
  flagged ambiguous and emitted into a sidecar list for human/judge review.

Per feedback_ai_judge_for_trial_classification: this is not a regex parser
hiding behind the name "judge". The script extracts the model's stated answer
verbatim from a strict bold-format instruction and applies the classification
scheme. Trials where the format is broken or the answer is genuinely
ambiguous are surfaced rather than silently misclassified.
"""

from __future__ import annotations
import json
import re
import sys
from pathlib import Path
from collections import defaultdict

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
OUT = ROOT / "perception_baseline_n10_judge.json"

ANGLE_TO_CLOCK = {
    0: 12, 30: 1, 60: 2, 90: 3, 120: 4, 150: 5,
    180: 6, 210: 7, 240: 8, 270: 9, 300: 10, 330: 11,
}

WORD_TO_NUM = {
    "one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6,
    "seven": 7, "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
}


def extract_bold_tokens(text: str) -> list[str]:
    """Return all bolded tokens (between ** **) in order."""
    return re.findall(r"\*\*([^*]+?)\*\*", text)


def parse_clock_answer(text: str):
    """Extract numeric clock position 1..12 from a B1/B2 response.

    Returns (value:int|None, raw_extracted:str, ambiguous_reason:str|None).
    """
    bolds = extract_bold_tokens(text)
    if bolds:
        last = bolds[-1].strip()
        # Common forms: "5", "5 o'clock", "five", "5.", "12:00"
        m = re.search(r"\b(\d{1,2})\b", last)
        if m:
            n = int(m.group(1))
            if 1 <= n <= 12:
                return n, last, None
        low = last.lower()
        for w, n in WORD_TO_NUM.items():
            if re.search(rf"\b{w}\b", low):
                return n, last, None
        return None, last, "bold_present_but_no_clock_number"

    # No bold. Try to find a final-line "12 o'clock" / "answer is N" pattern.
    tail = text.strip().splitlines()[-1] if text.strip() else ""
    m = re.search(r"\b(\d{1,2})\s*(?:o'?clock)?\b", tail)
    if m:
        n = int(m.group(1))
        if 1 <= n <= 12:
            return n, tail, "no_bold_used_tail"
    return None, text[-120:], "no_bold_no_recoverable_number"


def parse_length_answer(text: str):
    """Extract 'up'|'right'|'equal' from a B3/B4 response."""
    bolds = extract_bold_tokens(text)
    if bolds:
        last = bolds[-1].strip().lower()
        # canonical forms: "up longer", "right longer", "equal"
        if "equal" in last:
            return "equal", last, None
        # be careful: "up longer" / "right longer" / "longer: up" etc.
        has_up = re.search(r"\bup\b", last) is not None
        has_right = re.search(r"\bright\b", last) is not None
        if has_up and not has_right:
            return "up", last, None
        if has_right and not has_up:
            return "right", last, None
        if has_up and has_right:
            return None, last, "both_up_and_right_in_bold"
        return None, last, "bold_present_no_direction"

    tail = text.strip().lower()[-200:]
    if "equal" in tail and "longer" not in tail:
        return "equal", tail[-60:], "no_bold_inferred_equal"
    return None, text[-120:], "no_bold_no_recoverable_direction"


def classify_clock(truth: int, pred: int) -> str:
    """Classification per spec for B1/B2."""
    if pred is None:
        return "refused_or_ambiguous"
    if pred == truth:
        return "exact"
    # Cyclic distance on 12-hour dial.
    diff = abs(pred - truth) % 12
    cyc = min(diff, 12 - diff)
    if cyc == 1:
        return "off_by_one"
    if 5 <= cyc <= 6:
        return "opposite"
    return "off_by_more"


def classify_length(truth: str, pred: str) -> str:
    if pred is None:
        return "refused_or_ambiguous"
    if pred == truth:
        return "correct"
    if truth == "equal":
        return "equal_called_unequal"
    if pred == "equal":
        return "unequal_called_equal"
    # truth is up/right and pred is the other up/right
    return "reversed"


def stim_label_b12(angle: int) -> str:
    return f"angle_{angle:03d}"


def stim_label_b34(ratio: float, truth: str) -> str:
    return f"ratio_{ratio:.1f}_{truth}"


def main() -> int:
    out_trials = []
    ambiguous = []

    # per-stimulus tally: model -> condition -> stim -> Counter of classes
    per_stim = defaultdict(lambda: defaultdict(lambda: defaultdict(lambda: defaultdict(int))))

    files = []
    for model_short, model_dir in [("sonnet", "perception_baseline_n10_sonnet"),
                                   ("opus", "perception_baseline_n10_opus")]:
        for cond in ("b1", "b2", "b3", "b4"):
            files.append((model_short, cond, ROOT / model_dir / cond / "trials.json"))

    for model_short, cond, path in files:
        with path.open() as f:
            trials = json.load(f)
        for t in trials:
            model_id = t["model"]
            raw = t["raw_response"]
            if cond in ("b1", "b2"):
                angle = t["angle_deg"]
                truth = ANGLE_TO_CLOCK[angle]
                pred, extracted, amb = parse_clock_answer(raw)
                if pred is None:
                    cls = "refused_or_ambiguous"
                else:
                    cls = classify_clock(truth, pred)
                stim = stim_label_b12(angle)
                truth_str = str(truth)
                extracted_str = str(pred) if pred is not None else extracted
            else:
                ratio = t["ratio"]
                truth = t["truth_longer"]
                pred, extracted, amb = parse_length_answer(raw)
                cls = classify_length(truth, pred)
                stim = stim_label_b34(ratio, truth)
                truth_str = truth
                extracted_str = pred if pred is not None else extracted

            entry = {
                "model": model_id,
                "condition": cond,
                "stimulus_label": stim,
                "truth": truth_str,
                "trial": t["trial"],
                "extracted_answer": extracted_str,
                "classification": cls,
            }
            if amb:
                entry["notes"] = amb
                ambiguous.append({**entry, "raw_response": raw})
            out_trials.append(entry)
            per_stim[model_short][cond][stim][cls] += 1

    # Build per_stimulus_summary nested dict (plain dict for JSON).
    per_stim_summary = {}
    for m, conds in per_stim.items():
        per_stim_summary[m] = {}
        for c, stims in conds.items():
            per_stim_summary[m][c] = {}
            for s, counter in stims.items():
                per_stim_summary[m][c][s] = dict(counter)

    # Aggregate.
    def pct(num, den):
        return round(100.0 * num / den, 1) if den else 0.0

    aggregate = {}
    for m in ("sonnet", "opus"):
        agg = {}
        for c in ("b1", "b2"):
            stims = per_stim[m][c]
            total = 0
            exact = off1 = opp = off_more = ref = 0
            for counter in stims.values():
                exact += counter.get("exact", 0)
                off1 += counter.get("off_by_one", 0)
                opp += counter.get("opposite", 0)
                off_more += counter.get("off_by_more", 0)
                ref += counter.get("refused_or_ambiguous", 0)
                total += sum(counter.values())
            agg[f"{c}_n"] = total
            agg[f"{c}_exact_pct"] = pct(exact, total)
            agg[f"{c}_off_by_one_or_better_pct"] = pct(exact + off1, total)
            agg[f"{c}_off_by_more_pct"] = pct(off_more, total)
            agg[f"{c}_opposite_pct"] = pct(opp, total)
            agg[f"{c}_refused_pct"] = pct(ref, total)
        for c in ("b3", "b4"):
            stims = per_stim[m][c]
            total = 0
            correct = reversed_ = ecu = uce = ref = 0
            for counter in stims.values():
                correct += counter.get("correct", 0)
                reversed_ += counter.get("reversed", 0)
                ecu += counter.get("equal_called_unequal", 0)
                uce += counter.get("unequal_called_equal", 0)
                ref += counter.get("refused_or_ambiguous", 0)
                total += sum(counter.values())
            agg[f"{c}_n"] = total
            agg[f"{c}_correct_pct"] = pct(correct, total)
            agg[f"{c}_reversed_pct"] = pct(reversed_, total)
            agg[f"{c}_equal_called_unequal_pct"] = pct(ecu, total)
            agg[f"{c}_unequal_called_equal_pct"] = pct(uce, total)
            agg[f"{c}_refused_pct"] = pct(ref, total)
        aggregate[m] = agg

    out = {
        "method": "ai-judge fresh-context, N=10 baseline, sonnet+opus side-by-side",
        "judge_model": "claude-opus-4-7[1m]",
        "n_trials": len(out_trials),
        "n_ambiguous_flagged": len(ambiguous),
        "trials": out_trials,
        "per_stimulus_summary": per_stim_summary,
        "aggregate": aggregate,
    }
    OUT.write_text(json.dumps(out, indent=2))

    # Sidecar of ambiguous trials (printed to stderr for review).
    sidecar = ROOT / "perception_baseline_n10_judge_ambiguous.json"
    sidecar.write_text(json.dumps(ambiguous, indent=2))

    print(f"wrote {OUT}")
    print(f"trials: {len(out_trials)}, ambiguous: {len(ambiguous)}")
    print(f"sidecar: {sidecar}")

    # Quick aggregate echo.
    for m in ("sonnet", "opus"):
        a = aggregate[m]
        print(f"\n[{m}]")
        for c in ("b1", "b2"):
            print(f"  {c}: exact={a[f'{c}_exact_pct']}%  ≤1-off={a[f'{c}_off_by_one_or_better_pct']}%  opposite={a[f'{c}_opposite_pct']}%  refused={a[f'{c}_refused_pct']}%")
        for c in ("b3", "b4"):
            print(f"  {c}: correct={a[f'{c}_correct_pct']}%  reversed={a[f'{c}_reversed_pct']}%  ecu={a[f'{c}_equal_called_unequal_pct']}%  uce={a[f'{c}_unequal_called_equal_pct']}%")
    return 0


if __name__ == "__main__":
    sys.exit(main())
