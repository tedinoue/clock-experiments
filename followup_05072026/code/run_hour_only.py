"""Hour-hand-only clock-reading experiment.

Each stimulus is a clock with ONLY an hour hand. Asks the model to
identify the time and estimate the minutes from the hour hand's
position between numerals.

Tests:
  (1) Hour-numeral identification across the full dial — does the B1
      lower-half wrong-end bias appear when there's no minute hand to
      role-confuse?
  (2) Minute-estimation capability — can the model use hour-hand
      fractional position as a minute cue (the consistency-check insight
      claimed verbally in dialogic teaching)?
  (3) Cross-numeral interpolation — does accuracy degrade between
      numerals vs on-the-hour?

Single-shot per stimulus, R1 generic system prompt, default thinking-on
for Sonnet (Stage 2 confirmed thinking-on alone is benign).
"""
import argparse, base64, json, os, re, sys
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
HOUR_ONLY = ROOT / "hour_only_clocks"
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
    "This clock has only one hand — the hour hand. What time does it show? "
    "Estimate the minute as best you can from where the hour hand sits "
    "between numerals (the hour hand moves continuously: at 30 minutes past "
    "the hour it sits halfway between two numerals; at 45 minutes it's "
    "three-quarters of the way to the next numeral)."
)

# 24 stimuli at every 30 min
TIMES = []
for h in range(12):
    H = 12 if h == 0 else h
    TIMES.append((H, 0))
    TIMES.append((H, 30))

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

def extract_time(text):
    bold = re.findall(r'\*\*\s*(\d{1,2}:\d{2})\s*\*\*', text)
    if bold:
        return bold[0]
    m = re.findall(r'\b(\d{1,2}:\d{2})\b', text)
    return m[0] if m else "(none)"

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default=SONNET, help="claude-sonnet-4-6 or claude-opus-4-7")
    ap.add_argument("--no-thinking", action="store_true")
    ap.add_argument("--out", default="hour_only_results.json")
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    label = f"{args.model} {'thinking-OFF' if args.no_thinking else 'thinking-ON'}"
    print(f"\n=== Hour-only experiment — {label} ===")
    results = []
    for h, m in TIMES:
        truth = f"{h}:{m:02d}"
        path = HOUR_ONLY / f"hour_only_{h:02d}_{m:02d}.png"
        try:
            text, thinking, in_tok, out_tok = run_one(client, path, args.model, not args.no_thinking)
            answer = extract_time(text)
            print(f"  truth={truth:<6} answer={answer:<7} (in={in_tok}, out={out_tok}, think={len(thinking)})")
            results.append({
                "truth": truth, "h": h, "m": m, "answer": answer,
                "response": text, "thinking_chars": len(thinking),
                "in_tok": in_tok, "out_tok": out_tok,
            })
        except Exception as e:
            print(f"  truth={truth} ERROR: {e}")
            results.append({"truth": truth, "h": h, "m": m, "error": str(e)})

    out_path = ROOT / args.out
    out_path.write_text(json.dumps({"label": label, "results": results}, indent=2))
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    main()
