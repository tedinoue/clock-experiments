"""Long-handed simplest clock validation experiment.

Tests the falsifiable prediction from the half-circle extrapolation
finding: clocks where both hands' tips reach the numeral ring should
read accurately even on stimuli that fail with the standard short-thick
hour hand (5:50, 7:45, 2:35, 8:25, 11:40 etc.).

10 stimuli × 5 trials × 2 models = 100 calls.
"""
import argparse, base64, json, os, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
STIM_DIR = ROOT / "long_hands_clocks"
SONNET = "claude-sonnet-4-6"
OPUS = "claude-opus-4-7"
THINKING_BUDGET = 6000
MAX_TOKENS = 12000

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully."
)

USER_PROMPT = "What time does this clock show?"

STIMULI = [(3,0), (9,0), (1,15), (4,30), (7,45), (10,30), (2,35), (5,50), (11,40), (8,25)]

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
    import time
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

def extract_time(text):
    bold = re.findall(r'\*\*\s*(\d{1,2}:\d{2})\s*\*\*', text)
    if bold: return bold[-1]
    m = re.findall(r'\b(\d{1,2}:\d{2})\b', text)
    return m[-1] if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True, choices=[SONNET, OPUS])
    ap.add_argument("--n", type=int, default=5)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    trials = []
    for h, m in STIMULI:
        for trial in range(args.n):
            trials.append({"h": h, "m": m, "truth": f"{h}:{m:02d}", "trial": trial+1})
    total = len(trials)
    print(f"\n=== Long-handed clock validation: {args.model} n={args.n} (total {total} calls, workers={args.workers}) ===")

    results = [None] * total
    def do_trial(idx, t):
        path = STIM_DIR / f"long_hands_{t['h']:02d}_{t['m']:02d}.png"
        try:
            text, in_tok, out_tok = run_one(client, args.model, path)
            ans = extract_time(text)
            return idx, {"truth": t["truth"], "trial": t["trial"], "answer": ans, "response": text, "in_tok": in_tok, "out_tok": out_tok}
        except Exception as e:
            return idx, {"truth": t["truth"], "trial": t["trial"], "error": str(e)}

    completed = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futures = [ex.submit(do_trial, i, t) for i, t in enumerate(trials)]
        for fut in as_completed(futures):
            idx, r = fut.result()
            results[idx] = r
            completed += 1
            if completed % 10 == 0 or completed == total:
                print(f"  ...{completed}/{total} done")

    out_path = ROOT / args.out
    out_path.write_text(json.dumps({
        "model": args.model, "n_per_stim": args.n,
        "stimuli": STIMULI, "results": results,
    }, indent=2))
    print(f"\nSaved: {out_path}")

    # Quick summary
    correct = sum(1 for r in results if r.get("answer") == r["truth"])
    print(f"Exact: {correct}/{total} = {correct/total*100:.0f}%")
    # Per-stimulus
    print("\nPer-stimulus:")
    for h, m in STIMULI:
        truth = f"{h}:{m:02d}"
        cell = [r for r in results if r["truth"] == truth]
        ok = sum(1 for r in cell if r.get("answer") == truth)
        answers = [r.get("answer", "?") for r in cell]
        print(f"  {truth:<6}  {ok}/{len(cell)}  answers: {answers}")

if __name__ == "__main__":
    main()
