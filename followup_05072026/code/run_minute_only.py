"""Minute-hand-only clock-reading experiment.

60 stimuli, minute hand at minutes 0-59. Single-shot, randomized
presentation order. Asks the model to report only the minute setting
(0 to 59) since there is no hour hand to indicate the hour.

Tests minute-hand position perception in isolation. Complement to
the hour-only experiment.
"""
import argparse, base64, json, os, random, re, sys
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
MIN_ONLY = ROOT / "minute_only_clocks"
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"
THINKING_BUDGET = 10000
MAX_TOKENS = 16384

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully, "
    "and when you make mistakes, treat the correction as a learning opportunity."
)

USER_PROMPT = (
    "This clock has only one hand — the minute hand. There is no hour hand. "
    "What minute setting (a number from 0 to 59) does the minute hand indicate? "
    "State your answer as a single number."
)

RANDOM_SEED = 42  # reproducible randomization

def encode_image(p):
    return "image/png", base64.standard_b64encode(p.read_bytes()).decode()

def run_one(client, image_path, model, thinking_on):
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
    if thinking_on:
        if "opus" in model:
            kwargs["thinking"] = {"type": "adaptive"}
            kwargs["output_config"] = {"effort": "high"}
        else:
            kwargs["thinking"] = {"type": "enabled", "budget_tokens": THINKING_BUDGET}
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if b.type == "text")
    thinking = "".join(b.thinking for b in resp.content if b.type == "thinking")
    return text, thinking, resp.usage.input_tokens, resp.usage.output_tokens

def extract_minute(text):
    """Pull out the first integer 0-59 from the response."""
    # Prefer bolded numbers
    bold = re.findall(r'\*\*\s*(\d{1,2})\s*\*\*', text)
    for b in bold:
        n = int(b)
        if 0 <= n <= 59:
            return n
    # Otherwise first standalone integer in the right range
    nums = re.findall(r'\b(\d{1,2})\b', text)
    for n in nums:
        v = int(n)
        if 0 <= v <= 59:
            return v
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=SONNET)
    ap.add_argument("--no-thinking", action="store_true")
    ap.add_argument("--out", default="minute_only_results.json")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    # Randomize presentation order with fixed seed
    minutes = list(range(60))
    rng = random.Random(RANDOM_SEED)
    presentation_order = minutes[:]
    rng.shuffle(presentation_order)

    label = f"{args.model} {'thinking-OFF' if args.no_thinking else 'thinking-ON'}"
    print(f"\n=== Minute-only experiment — {label} ===")
    print(f"Random seed: {RANDOM_SEED}, presentation order shuffled.")
    results = []
    for idx, m in enumerate(presentation_order):
        path = MIN_ONLY / f"minute_only_{m:02d}.png"
        try:
            text, thinking, in_tok, out_tok = run_one(client, path, args.model, not args.no_thinking)
            answer = extract_minute(text)
            err = (answer - m) if answer is not None else None
            # Wrap to signed
            if err is not None:
                err = ((err + 30) % 60) - 30
            mark = "✓" if answer == m else "✗"
            print(f"  [{idx+1:2d}/60] {mark} truth={m:2d}  answer={answer if answer is not None else '?':<3}  err={err if err is not None else '?':<5}  (in={in_tok} out={out_tok} think={len(thinking)})")
            results.append({
                "presentation_idx": idx + 1, "truth": m, "answer": answer,
                "signed_err_min": err, "response": text,
                "thinking_chars": len(thinking),
                "in_tok": in_tok, "out_tok": out_tok,
            })
        except Exception as e:
            print(f"  [{idx+1:2d}/60] truth={m} ERROR: {e}")
            results.append({"presentation_idx": idx + 1, "truth": m, "error": str(e)})

    out_path = ROOT / args.out
    out_path.write_text(json.dumps({"label": label, "seed": RANDOM_SEED, "results": results}, indent=2))
    print(f"\nSaved: {out_path}")

    # Quick summary
    correct = sum(1 for r in results if r.get("answer") == r["truth"])
    within3 = sum(1 for r in results if r.get("signed_err_min") is not None and abs(r["signed_err_min"]) <= 3)
    errs = [abs(r["signed_err_min"]) for r in results if r.get("signed_err_min") is not None]
    import statistics
    print(f"\nExact: {correct}/60 = {correct/60*100:.1f}%")
    print(f"Within ±3 min: {within3}/60 = {within3/60*100:.1f}%")
    print(f"|error| median: {statistics.median(errs):.1f} min, mean: {statistics.mean(errs):.1f} min, max: {max(errs)} min")

if __name__ == "__main__":
    main()
