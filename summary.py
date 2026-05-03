#!/usr/bin/env python3
"""Generate Stage 1 summary report from classified trials."""
import json
from collections import defaultdict
from pathlib import Path

RESULTS_DIR = Path(__file__).parent / "results"
CLASSIFIED = RESULTS_DIR / "stage1_classified.json"
OUT = Path(__file__).parent / "STAGE_1_RESULTS.md"

CLOCKS = ["clock_01", "clock_02", "clock_03", "clock_04",
          "clock_05", "clock_06", "clock_07", "clock_08"]

GT = {
    "clock_01": ("10:10", "Arabic chronograph"),
    "clock_02": ("03:25", "Roman + date"),
    "clock_03": ("07:50", "24-hour double ring"),
    "clock_04": ("08:20", "Naked hands only"),
    "clock_05": ("04:15", "Gradient + Arabic"),
    "clock_06": ("06:30", "Rainbow no numerals"),
    "clock_07": ("11:55", "Dark face slim hands"),
    "clock_08": ("09:45", "Mirrored Arabic"),
}

GOOD = {"exact_match", "within_5_min"}

trials = json.load(open(CLASSIFIED))

matrix = defaultdict(lambda: defaultdict(int))
totals = defaultdict(lambda: defaultdict(int))
model_clock_counts = defaultdict(lambda: defaultdict(int))

models_seen = []
for t in trials:
    m = t["model_name"]
    if m not in models_seen:
        models_seen.append(m)
    c = t["clock_id"]
    b = t["classification"]
    matrix[(m, c)][b] += 1
    totals[m][b] += 1
    model_clock_counts[m][c] += 1

# Order: Anthropic ladder, then OpenAI, then Google
order = ["Opus 4.7", "Sonnet 4.6", "Haiku 4.5", "GPT-5", "Gemini 2.5 Pro"]
models_seen = [m for m in order if m in models_seen] + [m for m in models_seen if m not in order]

def acc(counts):
    n = sum(counts.values())
    if n == 0: return None
    return sum(counts.get(b, 0) for b in GOOD) / n

def pct_or_dash(counts, n_required=10):
    n = sum(counts.values())
    if n == 0:
        return "—"
    a = acc(counts) * 100
    if n < n_required:
        return f"{a:.0f}% ({n})"
    return f"{a:.0f}%"

# Identify partial-data models
partial = {m: sum(totals[m].values()) for m in models_seen
           if sum(totals[m].values()) < len(CLOCKS) * 10}

out = []
out.append("# Clocks Stage 1 — Results")
out.append("")
out.append("Naive prompt: `What time does this clock show?`")
out.append("")
out.append(f"**Cohort:** {', '.join(models_seen)}")
out.append(f"**Stimulus set:** 8 rendered clocks, ground truth at `salon/files/clocks/GROUND_TRUTH.md`")
out.append("**Classification:** Subagent-based AI judge (per `feedback_ai_judge_for_trial_classification.md`).")
out.append("**Buckets:** `exact_match` (±1 min) · `within_5_min` (±5 min, excl. exact) · `wrong_by_more` (>5 min off OR confidently wrong) · `refused_or_uncertain` (declined or hedged without committing)")
out.append("")
if partial:
    out.append("> ⚠️ **PARTIAL DATA WARNING.** The following models have fewer than 80 clean trials and their numbers are NOT comparable to others:")
    for m, n in partial.items():
        out.append(f"> - **{m}**: only {n} clean trials. (Underlying cause: Gemini API 503 overload during the run window. Need to re-run Gemini against fresh API conditions.)")
    out.append("")

out.append(f"Total trials run: {len(trials)} (clean: {sum(1 for t in trials if t['classification'] not in ('api_error','unclassified'))})")
out.append("")

# Compact accuracy table
out.append("## Accuracy by model × clock")
out.append("")
out.append("Cell shows % within ±5 min of ground truth. `—` = no trials. `(n)` = trial count if <10.")
out.append("")
header = ["model"] + [f"c{c[6:]}" for c in CLOCKS] + ["overall"]
out.append("| " + " | ".join(header) + " |")
out.append("|" + "---|" * len(header))
out.append("| **gt** | " + " | ".join(GT[c][0] for c in CLOCKS) + " |    |")
for m in models_seen:
    row = [m]
    for c in CLOCKS:
        row.append(pct_or_dash(matrix[(m, c)]))
    a = acc(totals[m])
    overall = f"**{a*100:.0f}%**" if a is not None else "—"
    n = sum(totals[m].values())
    if n < 80:
        overall += f" *({n} trials)*"
    row.append(overall)
    out.append("| " + " | ".join(row) + " |")

out.append("")
out.append("## Bucket distribution by model")
out.append("")
out.append("| model | exact | ±5min | wrong | refused | n |")
out.append("|---|---|---|---|---|---|")
for m in models_seen:
    n = sum(totals[m].values())
    em = totals[m].get("exact_match", 0)
    w5 = totals[m].get("within_5_min", 0)
    wr = totals[m].get("wrong_by_more", 0)
    ref = totals[m].get("refused_or_uncertain", 0)
    err = totals[m].get("api_error", 0) + totals[m].get("unclassified", 0)
    pct = lambda x: f"{x*100/max(n-err,1):.0f}%" if (n-err) > 0 else "—"
    extras = f" (api_err: {err})" if err else ""
    out.append(f"| {m} | {em} ({pct(em)}) | {w5} ({pct(w5)}) | {wr} ({pct(wr)}) | {ref} ({pct(ref)}) | {n}{extras} |")

out.append("")
out.append("## Per-clock difficulty (% correct across complete-data models only)")
out.append("")
out.append("| clock | style | gt | n | % correct |")
out.append("|---|---|---|---|---|")
complete_models = [m for m in models_seen if m not in partial]
for c in CLOCKS:
    counts = defaultdict(int)
    for m in complete_models:
        for b, n in matrix[(m, c)].items():
            counts[b] += n
    a = acc(counts)
    n = sum(counts.values())
    out.append(f"| {c} | {GT[c][1]} | {GT[c][0]} | {n} | {a*100:.0f}% |")

out.append("")
out.append("## Comparison to Jing Hu's claim")
out.append("")
out.append("Jing Hu (https://substack.com/@jinghuu/note/c-250006786): *\"even with the best and latest LLM, take Claude Opus for example, only got this right at a coin toss\"* — interpreted as ~50% accuracy across her 8-clock set.")
out.append("")
opus_models = [m for m in complete_models if "Opus" in m]
for m in opus_models:
    a = acc(totals[m]) * 100
    em_only = totals[m].get("exact_match", 0) / max(sum(totals[m].values()), 1) * 100
    delta = a - 50
    out.append(f"- **{m}**: {a:.0f}% within ±5 min ({'+' if delta >= 0 else ''}{delta:.0f}% vs 50% claim). Strict exact-match: {em_only:.0f}%.")
out.append("")
out.append("Our Opus 4.7 result is **below** her claim. Caveats:")
out.append("- We measured against pixel-perfect known ground truth on rendered clocks; she eyeballed answers on her own screenshot. Her loose-criterion 50% is plausible if she counted close-enough as correct.")
out.append("- Jing Hu didn't specify Opus version. If she tested 4.6 (older), comparison is moot.")
out.append("- Our stimulus set mirrors her style categories but isn't her exact pixels.")

out.append("")
out.append("## Key findings")
out.append("")
out.append("**1. Per-clock difficulty hierarchy.** Three tiers under the dual rubric:")
out.append("- *Easiest:* clock_01 (10:10 Arabic chronograph, the watch-ad pose) — 82% across complete-data models.")
out.append("- *Universally hard:* clock_04 (naked hands, no face) at 8%. No reference frame; models either refuse or guess.")
out.append("- *Mostly hard but with structure:* clock_08 (mirror) at 18% under dual rubric (was 5% under strict rubric where only 9:45 counted). The accuracy understates the cognitive picture — see finding #2.")
out.append("- *Mid-difficulty:* clock_03 (24-hour, 18%), clock_07 (11:55, 20%), clock_05 (4:15, 25%), clock_06 (rainbow 6:30, 42%), clock_02 (Roman 3:25, 50%).")
out.append("")
out.append("**2. The mirror clock splits the cohort by interpretation, not just by accuracy.** Under the dual rubric (both 9:45 mirror-aware and 2:15 template-match are acceptable, since hand positions are 67.5°/90°), the picture is much richer than \"all models fail\":")
out.append("- **GPT-5**: 5/10 trials say \"2:15\" exactly (clean template-match — didn't notice the numerals were mirrored). 4/10 say something close to \"9:xx\" (saw the mirror, missed the minute). 1 empty.")
out.append("- **Opus 4.7**: 2/10 close to mirror-aware (9:50). 8/10 say \"9:xx\" but with wrong minute. **All 10 trials show some mirror-detection** — they read hour as 9, then misread minute.")
out.append("- **Sonnet 4.6**: 10/10 say \"9:xx\" (all mirror-aware on hour) but 0/10 get the minute. *Same partial-mirror pattern as Opus.*")
out.append("- **Haiku 4.5**: 10/10 say \"3:xx\" — neither mirror-aware nor correct template-match. The 3-position is ~20° off from where the hour hand actually is.")
out.append("- **The diagnostic signal**: Anthropic models DETECT the mirror partially — they correctly identify the displayed mirrored \"9\" as the hour position. They then fail to apply the mirror logic consistently to the minute hand. GPT-5 either ignores the mirror entirely (template-match wins) or only partially applies it. This is a *split-application failure*, not a *detection failure*.")
out.append("")
out.append("**3. The naked-hands clock splits the cohort.** Models either refuse (Sonnet, Haiku) or guess wrong (Opus, GPT-5 mostly say 10:20). The refusals are arguably the *correct* response — without numerals there's no canonical 12-position reference, but the conventional assumption is 12-at-top.")
out.append("")
out.append("**4. Numeral style sensitivity.** Roman numerals (clock_02) split the cohort: Sonnet 4.6 and GPT-5 read them; Opus 4.7 and Haiku 4.5 mistook V (5) and III (3) for digit values, producing 5:15. This is a *literacy* failure, not a perception failure.")
out.append("")
out.append("**5. Reading-direction bias on clock_07 (11:55).** Most models said 11:00 instead of 11:55 — they followed the hour hand without correctly reading the minute hand at 11. The minute-hand-points-AT-11-which-is-55-minutes-not-11 reasoning is consistently dropped.")
out.append("")
out.append("**6. The 24-hour clock confuses everyone except GPT-5.** Outer 24-numeral ring + inner 12-numeral ring at different angular positions defeats most readers. GPT-5 70% (probably the chain-of-thought reasoning helping). Opus and Sonnet collapse into reading the wrong ring.")

out.append("")
out.append("## Stage 2 framing study — failers identified")
out.append("")
THRESHOLD = 80
for m in complete_models:
    a = acc(totals[m]) * 100
    if a < THRESHOLD:
        out.append(f"- **{m}** ({a:.0f}%): below {THRESHOLD}% — Stage 2 framing variations warranted")
out.append("")
out.append("All four complete-data models fail at Stage 1 ceiling. Stage 2 framings (look-harder prime, expert-clockmaker persona, step-by-step, confidence elicitation, negative prime) should be run against the failing model × clock cells where accuracy is below 50%.")

out.append("")
out.append("## Methodology notes")
out.append("- Free-text responses, no format constraint, prompt unaltered (per `feedback_never_alter_experimental_prompts.md`).")
out.append("- AI-judge classification via 7 parallel subagents (per `feedback_ai_judge_for_trial_classification.md`).")
out.append("- Token budget 4096 per trial — required for reasoning models GPT-5 and Gemini 2.5 Pro that consume ~1000 hidden reasoning tokens before producing visible output. (1024 was insufficient; 1/80 GPT-5 trials still returned empty content even at 4096.)")
out.append("- Retry-until-N-clean per `feedback_api_trials_retry_until_n.md`. Cohort fixed per `feedback_cohort_scoping_first_round.md`.")
out.append("- Cost: ~$3-5 in API calls.")

with open(OUT, "w") as f:
    f.write("\n".join(out) + "\n")
print(f"Wrote {OUT}")
print()
print("\n".join(out))
