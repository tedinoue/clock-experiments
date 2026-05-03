#!/usr/bin/env python3
"""
Clocks Stage 3 — three ablation/contrast prompts.

Same image suite, same user prompt as Stages 1 and 2. Variable: system prompt.

Variants:
- 3A "scaffolding only": hand-by-hand methodical reading, no persona, no
  feature-checking. Tests whether the methodical decomposition does the work.
- 3B "feature-check only": notice unusual features before reading, no
  scaffolding, no persona. Tests whether detection-priming alone recovers.
- 3C "anti-reasoning": tells the model NOT to overthink, just answer fast.
  Tests whether elaborate reasoning HURTS (motivated by Sonnet's clock_02
  collapse under Stage 2's combined prime).

Usage:
    python3 run_stage3.py --variant a    # scaffolding only
    python3 run_stage3.py --variant b    # feature-check only
    python3 run_stage3.py --variant c    # anti-reasoning
    python3 run_stage3.py --variant a --models claude-haiku-4-5 --clocks clock_01 --n-trials 1  # smoke test
"""
import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

USER_PROMPT = "What time does this clock show?"

PROMPTS = {
    "a": """You read clocks methodically.

For every clock, follow this two-step procedure before committing to a time:
1. Identify the HOUR hand. It is shorter and thicker. State which numeral it points at, or between which two numerals it sits and how far between them.
2. Identify the MINUTE hand. It is longer and thinner. State which numeral position it points at. Each numeral represents 5 minutes — a hand at "3" means 15 minutes, at "9" means 45 minutes.

Only after you have identified both hands and their positions, commit to a specific time.""",

    "b": """Some clocks have unusual features that change how the time should be read. Before reading any clock, examine the face for these features:
- Mirrored numerals (numbers running counter-clockwise or each glyph flipped)
- An absent face, missing markers, or hands floating with no reference
- 24-hour dual-ring markings
- Multiple subdials
- Decorative elements that aren't part of the time-reading

Notice and name any unusual features before committing to a time.""",

    "c": """Don't overthink this. A glance is enough. State the time in HH:MM format and stop. No reasoning, no commentary, no qualifications.""",

    "d": """You are an expert clockmaker. You have spent your entire career reading and repairing analog timepieces, and your reputation depends on getting times exactly right.

It is critically important that you read this clock accurately. Take your time. Be careful. Make sure your answer is correct before you commit to it.""",
}

COHORT = [
    ("anthropic", "claude-opus-4-7",                "Opus 4.7"),
    ("anthropic", "claude-sonnet-4-6",              "Sonnet 4.6"),
    ("anthropic", "claude-haiku-4-5-20251001",      "Haiku 4.5"),
    ("openai",    "gpt-5",                          "GPT-5"),
    ("google",    "gemini-2.5-pro",                 "Gemini 2.5 Pro"),
]

CLOCKS_DIR = Path(__file__).parent / "rendered"
RESULTS_DIR = Path(__file__).parent / "results"

CLOCKS = [
    ("clock_01", "10:10"),
    ("clock_02", "03:25"),
    ("clock_03", "07:50"),
    ("clock_04", "08:20"),
    ("clock_05", "04:15"),
    ("clock_06", "06:30"),
    ("clock_07", "11:55"),
    ("clock_08", "09:45"),
]

MAX_RETRIES_PER_TRIAL = 8
RETRY_BACKOFF_BASE = 4.0
TIMEOUT = 240


def load_image_b64(path):
    return base64.b64encode(open(path, "rb").read()).decode("ascii")


def http_post(url, headers, payload, timeout=TIMEOUT):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(model_id, key, image_b64, system_prompt):
    r = http_post(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
        {
            "model": model_id,
            "max_tokens": 4096,
            "system": system_prompt,
            "messages": [{"role": "user", "content": [
                {"type": "image", "source": {
                    "type": "base64", "media_type": "image/png", "data": image_b64,
                }},
                {"type": "text", "text": USER_PROMPT},
            ]}],
        },
    )
    return "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text").strip()


def call_openai(model_id, key, image_b64, system_prompt):
    r = http_post(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {
            "model": model_id,
            "max_completion_tokens": 4096,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                    }},
                    {"type": "text", "text": USER_PROMPT},
                ]},
            ],
        },
    )
    return r["choices"][0]["message"]["content"].strip()


def call_google(model_id, key, image_b64, system_prompt):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model_id}:generateContent?key={key}")
    r = http_post(url, {}, {
        "systemInstruction": {"parts": [{"text": system_prompt}]},
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": image_b64}},
            {"text": USER_PROMPT},
        ]}],
        "generationConfig": {"maxOutputTokens": 4096},
    })
    cand = r.get("candidates", [{}])[0]
    return "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])).strip()


DISPATCH = {"anthropic": call_anthropic, "openai": call_openai, "google": call_google}


def run_one_with_retry(provider, model_id, key, image_b64, system_prompt,
                       max_retries=MAX_RETRIES_PER_TRIAL):
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            raw = DISPATCH[provider](model_id, key, image_b64, system_prompt)
            return raw, time.time() - t0, attempt, None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {e.code}: {body}"
            if 400 <= e.code < 500 and e.code != 429:
                return None, 0.0, attempt, last_err
        except urllib.error.URLError as e:
            last_err = f"URLError: {e.reason}"
        except Exception as e:
            last_err = f"{type(e).__name__}: {e}"
        if attempt < max_retries:
            wait = RETRY_BACKOFF_BASE * (2 ** (attempt - 1))
            print(f"      retry {attempt}/{max_retries-1} in {wait:.0f}s ({last_err[:80]})", flush=True)
            time.sleep(wait)
    return None, 0.0, max_retries, last_err


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--variant", required=True, choices=["a", "b", "c", "d"])
    ap.add_argument("--n-trials", type=int, default=10)
    ap.add_argument("--models", nargs="*", default=None)
    ap.add_argument("--clocks", nargs="*", default=None)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    system_prompt = PROMPTS[args.variant]
    stage_label = f"3{args.variant}"

    keys = {
        "anthropic": os.environ.get("ANTHROPIC_API_KEY", ""),
        "openai": os.environ.get("OPENAI_API_KEY", ""),
        "google": os.environ.get("GOOGLE_API_KEY", ""),
    }

    cohort = COHORT
    if args.models:
        cohort = [m for m in COHORT if any(f in m[1] for f in args.models)]
    clocks = CLOCKS
    if args.clocks:
        clocks = [c for c in CLOCKS if any(f in c[0] for f in args.clocks)]

    total_trials = len(cohort) * len(clocks) * args.n_trials
    print(f"Stage {stage_label} plan: {len(cohort)} models × {len(clocks)} clocks × {args.n_trials} trials = {total_trials} clean")
    print(f"User prompt: {USER_PROMPT!r}")
    print(f"System prompt ({len(system_prompt)} chars):")
    print("  " + "\n  ".join(system_prompt.split("\n")))

    if args.dry_run:
        return 0

    missing = sorted({p for p, _, _ in cohort if not keys[p]})
    if missing:
        print(f"FATAL: missing API keys: {missing}", file=sys.stderr)
        return 2

    images = {}
    for cid, _ in clocks:
        path = CLOCKS_DIR / f"{cid}.png"
        if not path.exists():
            print(f"FATAL: missing {path}", file=sys.stderr)
            return 2
        images[cid] = load_image_b64(path)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    grand_t0 = time.time()
    for provider, model_id, name in cohort:
        out_path = RESULTS_DIR / f"clocks_stage{stage_label}_{model_id}.json"
        results = []
        print(f"\n=== {name} ({provider}/{model_id}) ===", flush=True)
        for cid, gt in clocks:
            print(f"  {cid} (gt={gt}): ", end="", flush=True)
            for trial in range(1, args.n_trials + 1):
                raw, elapsed, attempts, err = run_one_with_retry(
                    provider, model_id, keys[provider], images[cid], system_prompt)
                rec = {
                    "model_id": model_id,
                    "model_name": name,
                    "clock_id": cid,
                    "ground_truth": gt,
                    "trial": trial,
                    "raw_response": raw,
                    "elapsed_s": round(elapsed, 2),
                    "attempts": attempts,
                    "error": err,
                    "stage": stage_label,
                }
                results.append(rec)
                print("." if raw else "X", end="", flush=True)
                with open(out_path, "w") as f:
                    json.dump(results, f, indent=2)
            print(f" ({sum(1 for r in results[-args.n_trials:] if r['raw_response'])}/{args.n_trials})")
        clean = sum(1 for r in results if r["raw_response"])
        print(f"  {name}: {clean}/{len(results)} clean. Saved {out_path}")

    elapsed_min = (time.time() - grand_t0) / 60
    print(f"\nDONE Stage {stage_label}. Total elapsed {elapsed_min:.1f} minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
