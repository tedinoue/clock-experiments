"""Half-circle scale extrapolation experiment.

Per Ted's design (2026-05-07): test whether short-pointer extrapolation
is the failure mode behind clock-reading errors. Strip away clock context.

37 angles (0°-180° in 5° steps) × 3 lengths (full, 3/4, 1/2) × 5 trials
× 2 models (Sonnet 4.6 thinking-ON, Opus 4.7 thinking-ON) = 1110 calls.

For each stimulus the model is asked which letter the line points at.
Letters A-S are at angles 0°, 10°, ..., 180° respectively. The "correct"
answer for a 5° offset angle is the nearer letter (e.g., 5° → A or B,
both equidistant; conventionally we'll accept either at boundaries).
"""
import argparse
import base64
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training/halfcircle")
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"
THINKING_BUDGET = 6000   # smaller than clocks runs — task is simpler
MAX_TOKENS = 12000

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "diagrams across multiple turns. Engage seriously, answer carefully."
)

USER_PROMPT = (
    "This image shows a half-circle scale with letters A through S labeled "
    "at evenly-spaced positions around the curve. A black line emanates "
    "from the pivot dot. Which letter does the line point at? State your "
    "answer as a single letter (A through S) at the end of your response."
)

LETTERS = "ABCDEFGHIJKLMNOPQRS"
ANGLES = list(range(0, 181, 5))   # 0, 5, 10, ..., 180

def encode_image(p):
    return "image/png", base64.standard_b64encode(p.read_bytes()).decode()

def run_one(client, model, image_path):
    media_type, b64 = encode_image(image_path)
    kwargs = dict(
        model=model,
        max_tokens=MAX_TOKENS,
        system=R1_SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": USER_PROMPT},
        ]}],
    )
    if "opus" in model:
        kwargs["thinking"] = {"type": "adaptive"}
        kwargs["output_config"] = {"effort": "high"}
    else:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": THINKING_BUDGET}
    last_err = None
    for attempt in range(3):
        try:
            resp = client.messages.create(**kwargs)
            text = "".join(b.text for b in resp.content if b.type == "text")
            return text, resp.usage.input_tokens, resp.usage.output_tokens
        except Exception as e:
            last_err = e
            time.sleep(2 + attempt * 3)
    raise last_err

def extract_letter(text):
    # Look for the answer at the END of the response
    # First try a clear "answer is X" or just final letter pattern
    bold = re.findall(r'\*\*\s*([A-S])\s*\*\*', text)
    if bold:
        return bold[-1].upper()
    # Last single letter A-S in the response
    matches = re.findall(r'\b([A-S])\b', text)
    if matches:
        return matches[-1].upper()
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=[SONNET, OPUS])
    ap.add_argument("--length", required=True, choices=["full", "three_quarter", "half"])
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    stim_dir = ROOT / args.length

    # Build the trial list: every angle × n trials
    trials = []
    for a in ANGLES:
        for trial in range(args.n):
            trials.append({"angle": a, "trial": trial + 1})
    total = len(trials)
    print(f"\n=== Half-circle scale: {args.model} length={args.length} n={args.n} (total {total} calls, workers={args.workers}) ===")

    results = [None] * total

    def do_trial(idx, t):
        path = stim_dir / f"scale_{t['angle']:03d}.png"
        try:
            text, in_tok, out_tok = run_one(client, args.model, path)
            ans = extract_letter(text)
            return idx, {"angle": t["angle"], "trial": t["trial"], "answer": ans, "response": text, "in_tok": in_tok, "out_tok": out_tok}
        except Exception as e:
            return idx, {"angle": t["angle"], "trial": t["trial"], "error": str(e)}

    completed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(do_trial, i, t) for i, t in enumerate(trials)]
        for fut in as_completed(futures):
            idx, r = fut.result()
            results[idx] = r
            completed += 1
            if completed % 20 == 0 or completed == total:
                print(f"  ...{completed}/{total} done")

    out_path = ROOT.parent / args.out
    out_path.write_text(json.dumps({
        "model": args.model, "length": args.length, "n_per_angle": args.n,
        "results": results,
    }, indent=2))
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    main()
