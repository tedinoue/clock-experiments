#!/usr/bin/env python3
"""
Clocks Stage 1 — naive baseline.

Single naive prompt, no system prompt, no formatting instructions, no retry
budget for non-transient errors.

  PROMPT: "What time does this clock show?"

5 models × 8 clocks × N=10 trials = 400 clean completions required.

Per `feedback_never_alter_experimental_prompts.md` — the prompt is sent
exactly as above, never wrapped, never reformatted.

Per `feedback_api_trials_retry_until_n.md` — transient errors (5xx, 429,
timeouts) retry with exponential backoff until N clean completions per
condition. Hard 4xx errors (auth, bad request) surface immediately.

Per `feedback_cohort_scoping_first_round.md` — first round cohort is fixed:
Opus 4.7, Sonnet 4.6, Haiku 4.5, GPT-5, Gemini 2.5 Pro.

Per `feedback_ai_judge_for_trial_classification.md` — this script ONLY
collects raw responses. Classification happens later via subagent judge.

Usage:
    ANTHROPIC_API_KEY=... OPENAI_API_KEY=... GOOGLE_API_KEY=... \
        python3 run_stage1.py
    python3 run_stage1.py --dry-run
    python3 run_stage1.py --models claude-opus-4-7 --n-trials 1  # smoke test
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

PROMPT = "What time does this clock show?"

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
    ("clock_01", "10:10", "Arabic chronograph + 3 subdials"),
    ("clock_02", "03:25", "Roman + red MON date"),
    ("clock_03", "07:50", "24-hour double ring"),
    ("clock_04", "08:20", "Naked hands only"),
    ("clock_05", "04:15", "Red→blue gradient + Arabic + day/date"),
    ("clock_06", "06:30", "Rainbow + no numerals + day/date"),
    ("clock_07", "11:55", "Dark face + slim hands + day/date"),
    ("clock_08", "09:45", "Mirrored Arabic"),
]

MAX_RETRIES_PER_TRIAL = 8
RETRY_BACKOFF_BASE = 4.0
TIMEOUT = 180


def load_image_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def http_post(url, headers, payload, timeout=TIMEOUT):
    req = urllib.request.Request(
        url,
        data=json.dumps(payload).encode("utf-8"),
        headers={**headers, "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))


def call_anthropic(model_id, key, image_b64):
    r = http_post(
        "https://api.anthropic.com/v1/messages",
        {"x-api-key": key, "anthropic-version": "2023-06-01"},
        {
            "model": model_id,
            "max_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image", "source": {
                        "type": "base64", "media_type": "image/png", "data": image_b64,
                    }},
                    {"type": "text", "text": PROMPT},
                ],
            }],
        },
    )
    text = "".join(b.get("text", "") for b in r.get("content", []) if b.get("type") == "text")
    return text.strip()


def call_openai(model_id, key, image_b64):
    r = http_post(
        "https://api.openai.com/v1/chat/completions",
        {"Authorization": f"Bearer {key}"},
        {
            "model": model_id,
            "max_completion_tokens": 4096,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {
                        "url": f"data:image/png;base64,{image_b64}",
                    }},
                    {"type": "text", "text": PROMPT},
                ],
            }],
        },
    )
    return r["choices"][0]["message"]["content"].strip()


def call_google(model_id, key, image_b64):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{model_id}:generateContent?key={key}")
    r = http_post(url, {}, {
        "contents": [{"parts": [
            {"inline_data": {"mime_type": "image/png", "data": image_b64}},
            {"text": PROMPT},
        ]}],
        "generationConfig": {"maxOutputTokens": 4096},
    })
    cand = r.get("candidates", [{}])[0]
    return "".join(p.get("text", "") for p in cand.get("content", {}).get("parts", [])).strip()


DISPATCH = {"anthropic": call_anthropic, "openai": call_openai, "google": call_google}


def run_one_with_retry(provider, model_id, key, image_b64,
                       max_retries=MAX_RETRIES_PER_TRIAL):
    """Returns (raw_text, elapsed_s, attempts, last_err)."""
    last_err = None
    for attempt in range(1, max_retries + 1):
        try:
            t0 = time.time()
            raw = DISPATCH[provider](model_id, key, image_b64)
            return raw, time.time() - t0, attempt, None
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:300]
            last_err = f"HTTP {e.code}: {body}"
            # 4xx (except 429) usually unrecoverable
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
    ap.add_argument("--n-trials", type=int, default=10)
    ap.add_argument("--models", nargs="*", default=None,
                    help="Filter cohort by model_id substring.")
    ap.add_argument("--clocks", nargs="*", default=None,
                    help="Filter clocks by clock_id substring (e.g. clock_01).")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

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
    print(f"Plan: {len(cohort)} models × {len(clocks)} clocks × {args.n_trials} trials = "
          f"{total_trials} clean completions required")
    for provider, mid, name in cohort:
        print(f"  {provider:9s} {mid:36s} {name}")
    print(f"Prompt: {PROMPT!r}")

    if args.dry_run:
        return 0

    missing = sorted({p for p, _, _ in cohort if not keys[p]})
    if missing:
        print(f"FATAL: missing API keys for providers: {missing}", file=sys.stderr)
        return 2

    # Pre-load all clock images
    images = {}
    for cid, _, _ in clocks:
        path = CLOCKS_DIR / f"{cid}.png"
        if not path.exists():
            print(f"FATAL: missing clock image {path}", file=sys.stderr)
            return 2
        images[cid] = load_image_b64(path)
    print(f"Loaded {len(images)} clock images")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    grand_t0 = time.time()
    for provider, model_id, name in cohort:
        out_path = RESULTS_DIR / f"clocks_stage1_{model_id}.json"
        results = []
        print(f"\n=== {name} ({provider}/{model_id}) ===", flush=True)
        for cid, gt, desc in clocks:
            print(f"  {cid} (gt={gt}): ", end="", flush=True)
            for trial in range(1, args.n_trials + 1):
                raw, elapsed, attempts, err = run_one_with_retry(
                    provider, model_id, keys[provider], images[cid])
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
                }
                results.append(rec)
                if raw is not None:
                    print(".", end="", flush=True)
                else:
                    print("X", end="", flush=True)
                # incremental save in case of crash
                with open(out_path, "w") as f:
                    json.dump(results, f, indent=2)
            print(f" ({sum(1 for r in results[-args.n_trials:] if r['raw_response'])}/{args.n_trials})")
        clean = sum(1 for r in results if r["raw_response"])
        print(f"  {name}: {clean}/{len(results)} clean. Saved {out_path}")

    elapsed_min = (time.time() - grand_t0) / 60
    print(f"\nDONE. Total elapsed {elapsed_min:.1f} minutes.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
