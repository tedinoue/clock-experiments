"""4:30 isolation experiment — three arms × 5 trials each.

Arm R1-replicate: thinking-OFF + R1 generic system prompt (matches R1 baseline)
Arm A:           thinking-OFF + self-check system prompt
Arm B:           thinking-ON + R1 generic system prompt

Each arm: 5 fresh single-call trials on simple_04_30.png. No multi-turn context.
Single-shot question: "What time does this clock show?"
"""
import argparse
import base64
import json
import os
import sys
from pathlib import Path
from anthropic import Anthropic

ROOT = Path("/Users/tedinoue/work/claude-workspace/scratch/clocks_training")
STIMULUS = ROOT / "simple_clocks" / "simple_04_30.png"
N_TRIALS = 5
MODEL = "claude-sonnet-4-6"
THINKING_BUDGET = 10000
MAX_TOKENS = 16384

R1_SYSTEM = (
    "You are an attentive student. The Salon (Terry) is teaching you to read "
    "analog clocks across multiple turns. Engage seriously, answer carefully, "
    "and when you make mistakes, treat the correction as a learning opportunity."
)

SELFCHECK_SYSTEM = (
    "You are reading analog clocks. You are an extended-thinking model — use "
    "your reasoning budget freely. Take your time on each clock; check your "
    "work before answering. If you spot a mistake on review, revise. Reply "
    "only when you're confident in the time."
)

USER_PROMPT = "What time does this clock show?"

def encode_image(p):
    return "image/png", base64.standard_b64encode(p.read_bytes()).decode()

def run_one(client, system, thinking_on):
    media_type, b64 = encode_image(STIMULUS)
    kwargs = dict(
        model=MODEL,
        max_tokens=MAX_TOKENS,
        system=system,
        messages=[{"role": "user", "content": [
            {"type": "image", "source": {"type": "base64", "media_type": media_type, "data": b64}},
            {"type": "text", "text": USER_PROMPT},
        ]}],
    )
    if thinking_on:
        kwargs["thinking"] = {"type": "enabled", "budget_tokens": THINKING_BUDGET}
    resp = client.messages.create(**kwargs)
    text = "".join(b.text for b in resp.content if b.type == "text")
    thinking = "".join(b.thinking for b in resp.content if b.type == "thinking")
    return text, thinking, resp.usage.input_tokens, resp.usage.output_tokens

def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr); sys.exit(2)
    client = Anthropic(api_key=api_key)

    arms = [
        ("R1-replicate", R1_SYSTEM, False),
        ("A: self-check + thinking-OFF", SELFCHECK_SYSTEM, False),
        ("B: R1-prompt + thinking-ON", R1_SYSTEM, True),
    ]

    results = {}
    for arm_name, system, thinking_on in arms:
        print(f"\n=== Arm: {arm_name} ===")
        print(f"system: {system[:80]}...")
        print(f"thinking_on: {thinking_on}")
        trials = []
        for i in range(N_TRIALS):
            try:
                text, thinking, in_tok, out_tok = run_one(client, system, thinking_on)
                trial = {"trial": i+1, "response": text, "thinking_chars": len(thinking), "in_tok": in_tok, "out_tok": out_tok}
                trials.append(trial)
                # Quick extraction: look for a time pattern in the response
                import re
                times = re.findall(r'\b\d{1,2}:\d{2}\b', text)
                first_time = times[0] if times else "(no time found)"
                print(f"  trial {i+1}: {first_time}  (in={in_tok}, out={out_tok}, think={len(thinking)})")
            except Exception as e:
                print(f"  trial {i+1}: ERROR {e}")
                trials.append({"trial": i+1, "error": str(e)})
        results[arm_name] = trials

    out_path = ROOT / "isolate_430_results.json"
    out_path.write_text(json.dumps(results, indent=2))
    print(f"\nSaved: {out_path}")

if __name__ == "__main__":
    main()
