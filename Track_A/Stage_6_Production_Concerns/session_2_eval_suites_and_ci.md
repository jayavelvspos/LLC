# Session 2 — Eval Suites & CI (~45 min)

**Objective:** build an eval suite (golden set + regression checks + LLM judge)
and run it on every change so a quality regression fails the build.

**What you'll learn:**
- Building a golden set and the three check types it enables
- LLM-as-judge tooling: Ragas, TruLens
- Setting thresholds and gating CI on them
- Why determinism matters for a trustworthy eval suite

**Prerequisites:** Session 1 complete. Stage 4 Session 6 (RAG eval) as a
starting point.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What an eval suite is; golden set, assertions, judge, thresholds |
| 10–30 | `code/evals/` — dataset + runner; a `pytest` wrapper |
| 30–40 | Wire into CI (GitHub Actions or a make target); set a pass threshold |
| 40–45 | Notes |

---

## Concepts

- **Golden set** — 30–100 representative inputs with expected outputs or
  properties. Frozen; extended deliberately.
- **Three check types:**
  - *Deterministic assertions* — schema valid, cites ≥1 source, ≤ N tokens,
    latency < X, no PII pattern. Cheap, exact.
  - *LLM-as-judge* — score answer quality/faithfulness 0–2 against a rubric.
    Noisy; average over the set. Ready-made metric libraries save writing the
    rubric prompts:
    - **Ragas** — RAG-specific metrics: `faithfulness`, `answer_relevancy`,
      `context_precision`, `context_recall`. Takes `question / answer /
      contexts / ground_truth`, returns 0–1 scores; integrates with a LangSmith
      or `datasets` eval run.
    - **TruLens** — *feedback functions* (the "RAG triad": context relevance,
      groundedness, answer relevance) that attach to traced app runs and log
      scores over time; good for continuous eval on live-ish traffic, not just
      a fixed golden set.
  - *Regression* — compare this run's scores to the last committed baseline;
    fail if any metric drops more than a margin.
- **Thresholds** — the suite passes if aggregate score ≥ T and no hard
  assertion fails. Pick T from the current baseline, not aspiration.
- **CI** — run a fast subset on every PR, the full set nightly (LLM-judge costs
  money and time). Store baselines in the repo.
- **Determinism** — set `temperature=0` for eval runs; pin the model id; the
  judge too.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — the `claude-api` skill's **`build-eval`** and **`hillclimb`**
  guides. In Claude Code: `/claude-api build-eval`. This is the authoritative
  workflow (grading methods, rubrics, runnable script, measured cost).
- Anthropic docs — *Reduce hallucinations* / *Strengthen guardrails* eval
  guidance: <https://docs.anthropic.com/en/docs/test-and-evaluate>.
- `promptfoo` or `pytest` patterns for LLM eval (pick one and stick with it).
- Ragas docs — *Metrics* (faithfulness, answer relevancy, context
  precision/recall): <https://docs.ragas.io/>.
- TruLens docs — *Feedback functions* and the *RAG triad*:
  <https://www.trulens.org/>.

**Video (pick one, ~15–25 min):**
- Search *"LLM evaluation CI regression testing"*.

---

## Track_B link (step 3)

**Non-blocking but real.** With a 50-item set, an LLM-judge average moving from
1.42 → 1.48 may be noise. Sample size, variance, and "is this delta
significant" are `Track_B/Math_stat` statistics. Note *"revisit in Track_B: how
big must an eval delta be to trust it"* — and if you're about to gate a release
on a small delta, **switch** and learn confidence intervals first.

---

## Worked example — a runner with assertions + judge

`code/evals/run.py` (core):

```python
import json, statistics
from research import research

def run(dataset="code/evals/golden.jsonl", judge_model="claude-opus-5"):
    rows = [json.loads(l) for l in open(dataset, encoding="utf-8")]
    hard_fail, scores = [], []
    for r in rows:
        out = research(r["q"], budget_usd=0.30)
        # deterministic assertions
        if not out["sources"]:            hard_fail.append((r["id"], "no sources"))
        if out["cost_usd"] > 0.30:        hard_fail.append((r["id"], "over budget"))
        # llm judge 0..2
        scores.append(judge(judge_model, r["q"], out["brief"], r["rubric"]))
    return {"mean_score": round(statistics.mean(scores), 3),
            "p10_score": sorted(scores)[len(scores)//10],
            "hard_fail": hard_fail}
```

`code/evals/test_quality.py`:

```python
def test_no_hard_failures():
    assert run()["hard_fail"] == []

def test_score_not_regressed():
    baseline = json.load(open("code/evals/baseline.json"))["mean_score"]
    assert run()["mean_score"] >= baseline - 0.05
```

**Expected output** (`pytest -q`):

```
FAILED test_quality.py::test_score_not_regressed - assert 1.31 >= 1.44 - 0.05
PASSED test_quality.py::test_no_hard_failures
mean_score=1.31  p10_score=0  hard_fail=[]
```

Read it: no assertion broke, but the mean quality score dropped below the
baseline margin — the build fails, and you investigate the change that caused
it before merging.

---

## Build

- Assemble `code/evals/golden.jsonl` (≥30 items across your system's real
  question types; reuse Stage 4's `eval_set.jsonl`).
- Write the runner with ≥3 deterministic assertions + a rubric judge. For the
  judge, try **Ragas** `faithfulness` + `answer_relevancy` on the RAG answers
  instead of a hand-written rubric; compare its scores to your own rubric on
  10 items — where do they disagree, and which do you trust?
- Commit a `baseline.json`. Add a CI job (GitHub Actions or `make eval`) that
  runs a 10-item fast subset on push, full set on schedule.
- Make a deliberately bad prompt change → confirm the regression test fails.
  Revert → confirm it passes. Update the baseline only on a real improvement.

---

## Quick test (step 7 — answer from memory, then check)

1. What's in a golden set, and how does it change over time?
2. Name the three check types and what each is good for.
3. Why run `temperature=0` and pin model ids for evals?
4. Why a fast subset on PR and the full set nightly?
5. When should you update the baseline?

<details><summary>Answers</summary>

1. 30–100 representative inputs with expected outputs/properties; frozen, and
   extended deliberately (not edited to make failures pass).
2. Deterministic assertions (exact, cheap: schema, limits, PII); LLM-judge
   (quality/faithfulness, noisy, average it); regression (compare to committed
   baseline).
3. To remove sampling noise and model drift so a score change reflects *your*
   change, not variance.
4. LLM-judge runs cost money and minutes; PRs need fast feedback, the full
   signal can be nightly.
5. Only after a verified real improvement — never to paper over a regression.

</details>

---

## Done when

- [ ] `code/evals/` has a golden set, a runner with assertions + judge, and
      `pytest` tests.
- [ ] CI runs the suite; a regression fails the build (demonstrated).
- [ ] A committed `baseline.json` exists.
- [ ] You can name the three check types from memory.

## Pitfalls

- **Editing the golden set to make it pass** — that's deleting your safety net.
- **Judge with a vague rubric** — inconsistent scores, useless regression
  signal.
- **Gating on a delta smaller than the set's noise** — see the Track_B link.

## Carries to next session

You can tell if a change helped. Session 3 hardens the system against transient
and persistent failures.
