"""Run the fundamental-perception baseline tests against Sonnet 4.6 in fresh
conversation states. Each trial is a single API call with no prior context, no
system prompt beyond the bare task instruction.

Sub-experiments:

B1 — single-line clean: 12 angles, ask which clock-position the line points to.
B2 — single-line cluttered: same 12 angles with chronograph-style subdial
     background, same question.
B3 — two-line clean: 9 length-ratio configurations (1.0 equal, 1.1/1.2/1.3/1.5
     up-longer, same right-longer), ask which is longer.
B4 — two-line cluttered: same 9 configurations with subdial background.

Output: scratch/clocks_training/perception_baseline/{b1,b2,b3,b4}/trials.json.
N defaults to 3 (overridable via --trials).

If we want N=10 for the final pass, run with --trials 10.
"""
import argparse
import base64
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path

from anthropic import Anthropic

DEFAULT_ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/perception_baseline")
STIMULI_ROOT = DEFAULT_ROOT  # stimuli always under perception_baseline/{b1..b4}/
DEFAULT_MODEL = "claude-sonnet-4-6"
MAX_TOKENS = 512

# Stimulus catalogs
B1_ANGLES = list(range(0, 360, 30))  # 0..330 every 30
B2_ANGLES = list(range(0, 360, 30))
B_RATIOS = [(1.0, "equal"),
            (1.1, "up"), (1.1, "right"),
            (1.2, "up"), (1.2, "right"),
            (1.3, "up"), (1.3, "right"),
            (1.5, "up"), (1.5, "right")]


def angle_to_clock_position(angle_deg):
    """Convert clock-convention angle (0=12, 90=3, etc.) to nearest 1-12 numeral."""
    pos = round((angle_deg % 360) / 30)
    if pos == 0:
        pos = 12
    return pos


SINGLE_PROMPT = """This image shows a single black line anchored at the center of the canvas, extending outward. Imagine a standard clock face overlaid on this image with 12 at the top, 3 on the right, 6 at the bottom, 9 on the left, and the other hour markers (1, 2, 4, 5, 7, 8, 10, 11) spaced evenly between.

Which clock-face position number (1 through 12) does the line point toward?

State your answer at the end as the bold number, e.g. **5**. Brief reasoning is fine but keep it short."""

TWO_LINE_PROMPT = """This image shows two black lines, both anchored at the center of the canvas. One points straight up. One points straight to the right. They are similar in style to the hands of a clock.

Compare the lengths of the two lines. Is the upward-pointing line longer than the rightward-pointing line, the rightward-pointing line longer than the upward, or are they the same length?

State your answer at the end in bold, exactly one of: **up longer**, **right longer**, or **equal**. Brief reasoning is fine but keep it short."""


def encode_image(path):
    return "image/png", base64.standard_b64encode(Path(path).read_bytes()).decode("utf-8")


def run_one(client, model, image_path, prompt):
    media_type, b64 = encode_image(image_path)
    resp = client.messages.create(
        model=model,
        max_tokens=MAX_TOKENS,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
    )
    text = "".join(b.text for b in resp.content if hasattr(b, "text"))
    return text, resp.usage.input_tokens, resp.usage.output_tokens


def run_b1_b2(client, model, condition, trials, out_root):
    angles = B1_ANGLES if condition == "b1" else B2_ANGLES
    results = []
    out_dir = out_root / condition
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / "transcript.md"
    transcript_path.write_text(f"# Perception baseline {condition.upper()} — {model}\n\nStarted: {datetime.now().isoformat()}\nTrials per stimulus: {trials}\n\n---\n\n")
    for a in angles:
        truth_pos = angle_to_clock_position(a)
        for i in range(trials):
            img = STIMULI_ROOT / condition / f"angle_{a:03d}.png"
            text, in_t, out_t = run_one(client, model, img, SINGLE_PROMPT)
            results.append({
                "condition": condition,
                "model": model,
                "angle_deg": a,
                "truth_clock_position": truth_pos,
                "trial": i + 1,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "raw_response": text,
            })
            with transcript_path.open("a") as f:
                f.write(f"## angle_{a:03d}° (truth pos: {truth_pos}) trial {i+1}\n\n")
                f.write(f"![angle_{a:03d}.png](../../perception_baseline/{condition}/angle_{a:03d}.png)\n\n")
                f.write(text + "\n\n---\n\n")
            print(f"  {condition} angle_{a:03d}° trial {i+1}: {out_t}t")
    return results


def run_b3_b4(client, model, condition, trials, out_root):
    results = []
    out_dir = out_root / condition
    out_dir.mkdir(parents=True, exist_ok=True)
    transcript_path = out_dir / "transcript.md"
    transcript_path.write_text(f"# Perception baseline {condition.upper()} — {model}\n\nStarted: {datetime.now().isoformat()}\nTrials per stimulus: {trials}\n\n---\n\n")
    for ratio, longer in B_RATIOS:
        label = f"ratio_{int(ratio*10):02d}_{longer}"
        for i in range(trials):
            img = STIMULI_ROOT / condition / f"{label}.png"
            text, in_t, out_t = run_one(client, model, img, TWO_LINE_PROMPT)
            results.append({
                "condition": condition,
                "model": model,
                "ratio": ratio,
                "truth_longer": longer,
                "trial": i + 1,
                "input_tokens": in_t,
                "output_tokens": out_t,
                "raw_response": text,
            })
            with transcript_path.open("a") as f:
                f.write(f"## {label} (truth longer: {longer}, ratio: {ratio}) trial {i+1}\n\n")
                f.write(f"![{label}.png](../../perception_baseline/{condition}/{label}.png)\n\n")
                f.write(text + "\n\n---\n\n")
            print(f"  {condition} {label} trial {i+1}: {out_t}t")
    return results


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--trials", type=int, default=3)
    ap.add_argument("--conditions", default="b1,b2,b3,b4")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--out-root", default=str(DEFAULT_ROOT),
                    help="Output root. Sonnet N=10 → perception_baseline_n10. Opus → perception_baseline_opus_n10.")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(2)

    out_root = Path(args.out_root)
    out_root.mkdir(parents=True, exist_ok=True)
    client = Anthropic(api_key=api_key)
    selected = [c.strip() for c in args.conditions.split(",")]

    if "b1" in selected:
        print(f"\n=== B1 (clean single-line) — {args.model} ===")
        r = run_b1_b2(client, args.model, "b1", args.trials, out_root)
        (out_root / "b1" / "trials.json").write_text(json.dumps(r, indent=2))

    if "b2" in selected:
        print(f"\n=== B2 (cluttered single-line) — {args.model} ===")
        r = run_b1_b2(client, args.model, "b2", args.trials, out_root)
        (out_root / "b2" / "trials.json").write_text(json.dumps(r, indent=2))

    if "b3" in selected:
        print(f"\n=== B3 (clean two-lines) — {args.model} ===")
        r = run_b3_b4(client, args.model, "b3", args.trials, out_root)
        (out_root / "b3" / "trials.json").write_text(json.dumps(r, indent=2))

    if "b4" in selected:
        print(f"\n=== B4 (cluttered two-lines) — {args.model} ===")
        r = run_b3_b4(client, args.model, "b4", args.trials, out_root)
        (out_root / "b4" / "trials.json").write_text(json.dumps(r, indent=2))

    print(f"\nDone. {args.model} → {out_root}")


if __name__ == "__main__":
    main()
