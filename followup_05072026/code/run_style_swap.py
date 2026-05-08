"""Style-swap and numerals-removed experiment harness.

Three runs:
  (A) minute_only_thick — minute-hand angles drawn with hour-hand visual
  (B) hour_only_thin    — hour-hand angles drawn with minute-hand visual
  (C) hour_only_no_numerals — hour-hand angles, no numerals on dial

Each run on Sonnet 4.6 thinking-ON, single-shot per stimulus, R1 system prompt.
"""
import argparse, base64, json, os, random, re, sys
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
SONNET = "claude-sonnet-4-6"
THINKING_BUDGET = 10000
MAX_TOKENS = 16384

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully, "
    "and when you make mistakes, treat the correction as a learning opportunity."
)

PROMPT_MINUTE = (
    "This clock has only one hand — the minute hand. There is no hour hand. "
    "What minute setting (a number from 0 to 59) does the minute hand indicate? "
    "State your answer as a single number."
)
PROMPT_HOUR = (
    "This clock has only one hand — the hour hand. What time does it show? "
    "Estimate the minute as best you can from where the hour hand sits "
    "between numerals (the hour hand moves continuously: at 30 minutes past "
    "the hour it sits halfway between two numerals; at 45 minutes it's "
    "three-quarters of the way to the next numeral)."
)
PROMPT_HOUR_NO_NUMERALS = (
    "This clock has only one hand — the hour hand. The dial has no numerals "
    "drawn, but the standard clock layout applies (the 12 position is at the "
    "top, 3 on the right, 6 at the bottom, 9 on the left, and the other "
    "hours spaced evenly between, indicated by the larger tick marks). "
    "What time does it show? Estimate the minute as best you can from where "
    "the hour hand sits relative to the implied numeral positions (the hour "
    "hand moves continuously: at 30 minutes past the hour it sits halfway "
    "between two implied numerals; at 45 minutes it's three-quarters of the "
    "way to the next)."
)

RANDOM_SEED = 42

def encode_image(p):
    return "image/png", base64.standard_b64encode(p.read_bytes()).decode()

def run_one(client, image_path, prompt):
    media_type, b64 = encode_image(image_path)
    resp = client.messages.create(
        model=SONNET,
        max_tokens=MAX_TOKENS,
        system=R1_SYSTEM,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": prompt},
        ]}],
        thinking={"type": "enabled", "budget_tokens": THINKING_BUDGET},
    )
    text = "".join(b.text for b in resp.content if b.type == "text")
    thinking = "".join(b.thinking for b in resp.content if b.type == "thinking")
    return text, thinking, resp.usage.input_tokens, resp.usage.output_tokens

def extract_minute(text):
    bold = re.findall(r'\*\*\s*(\d{1,2})\s*\*\*', text)
    for b in bold:
        n = int(b)
        if 0 <= n <= 59:
            return n
    nums = re.findall(r'\b(\d{1,2})\b', text)
    for n in nums:
        v = int(n)
        if 0 <= v <= 59:
            return v
    return None

def extract_time(text):
    bold = re.findall(r'\*\*\s*(\d{1,2}:\d{2})\s*\*\*', text)
    if bold: return bold[0]
    m = re.findall(r'\b(\d{1,2}:\d{2})\b', text)
    return m[0] if m else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--exp", required=True, choices=["A_min_thick", "B_hour_thin", "C_hour_no_num"])
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    if args.exp == "A_min_thick":
        stim_dir = ROOT / "minute_only_thick"
        prompt = PROMPT_MINUTE
        stims = [(m, stim_dir / f"minute_only_thick_{m:02d}.png", str(m)) for m in range(60)]
        rng = random.Random(RANDOM_SEED); rng.shuffle(stims)
        extractor = extract_minute
        is_minute = True
    else:
        if args.exp == "B_hour_thin":
            stim_dir = ROOT / "hour_only_thin"
            prompt = PROMPT_HOUR
        else:  # C_hour_no_num
            stim_dir = ROOT / "hour_only_no_numerals"
            prompt = PROMPT_HOUR_NO_NUMERALS
        times = []
        for h in range(12):
            H = 12 if h == 0 else h
            times.append((H, 0))
            times.append((H, 30))
        if args.exp == "B_hour_thin":
            stims = [((h, m), stim_dir / f"hour_only_thin_{h:02d}_{m:02d}.png", f"{h}:{m:02d}") for h, m in times]
        else:
            stims = [((h, m), stim_dir / f"hour_only_nonum_{h:02d}_{m:02d}.png", f"{h}:{m:02d}") for h, m in times]
        extractor = extract_time
        is_minute = False

    print(f"\n=== {args.exp} — Sonnet 4.6 thinking-ON, n={len(stims)} ===")
    results = []
    for idx, (truth_key, path, truth_label) in enumerate(stims):
        try:
            text, thinking, in_tok, out_tok = run_one(client, path, prompt)
            ans = extractor(text)
            mark = "✓" if str(ans) == truth_label else "✗"
            print(f"  [{idx+1:2d}/{len(stims)}] {mark} truth={truth_label:<6} answer={str(ans):<7} (in={in_tok} out={out_tok} think={len(thinking)})")
            results.append({
                "presentation_idx": idx + 1,
                "truth": truth_label,
                "answer": ans,
                "response": text,
                "thinking_chars": len(thinking),
                "in_tok": in_tok, "out_tok": out_tok,
            })
        except Exception as e:
            print(f"  [{idx+1:2d}/{len(stims)}] truth={truth_label} ERROR: {e}")
            results.append({"presentation_idx": idx + 1, "truth": truth_label, "error": str(e)})

    out_path = ROOT / args.out
    out_path.write_text(json.dumps({"experiment": args.exp, "results": results}, indent=2))
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    main()
