# Session 6 — Evaluating RAG (~45 min)

**Objective:** build a small labelled eval set and measure two numbers —
retrieval hit-rate and answer faithfulness — so "is it better?" stops being a
guess. This is the Stage 4 deliverable.

**What you'll learn:**
- Evaluating retrieval and generation as two separate failure surfaces
- Retrieval metrics: hit-rate@k and MRR
- Generation metrics: faithfulness, answer correctness, refusal correctness
- Building an eval set (including unanswerable questions) and an LLM-as-judge

**Prerequisites:** Sessions 1–5 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Two things to measure separately: retrieval vs generation |
| 10–20 | Write `code/eval_set.jsonl` — 15–25 questions with gold answers/chunks |
| 20–40 | `code/eval_rag.py` — hit-rate + faithfulness (LLM judge) |
| 40–45 | Run it against 2 configs; notes; tick the Stage 4 checklist |

---

## Concepts

- **Evaluate retrieval and generation separately** — a wrong answer can come
  from bad retrieval *or* bad generation on good context, and the fixes differ.
- **Retrieval metrics:**
  - *Hit-rate@k* — fraction of questions where a gold chunk is in the top-k.
  - *MRR* — 1/rank of the first gold chunk, averaged. Rewards ranking it higher.
- **Generation metrics:**
  - *Faithfulness* — does the answer follow only from the retrieved context (no
    hallucination)? Graded by an LLM judge or by hand.
  - *Answer correctness* — does it match the gold answer? LLM judge with a
    rubric, or exact/keyword match for factoid questions.
  - *Refusal correctness* — for out-of-corpus questions, did it correctly say
    "not covered"?
- **Eval set:** 15–25 items is enough to catch regressions. Each:
  `{question, gold_answer, gold_chunk_ids, answerable}`. Include ~20%
  unanswerable.
- **LLM-as-judge:** a separate model call scoring the answer against the context
  + gold on a small scale (0–2). Cheap, noisy — keep the rubric tight.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — via the `claude-api` skill, the **`build-eval`** guide (grading
  methods, LLM-judge rubrics, runnable eval script). Ask Claude Code:
  `/claude-api build-eval`.
- Anthropic Cookbook — evaluation notebooks:
  <https://github.com/anthropics/anthropic-cookbook>.
- RAGAS docs (concepts: faithfulness, context precision/recall) — for
  vocabulary: <https://docs.ragas.io/>.

**Video (pick one, ~15–25 min):**
- Search *"evaluating RAG systems faithfulness hit rate"*.

---

## Track_B link (step 3)

**Light, non-blocking.** Hit-rate, precision, recall, MRR are basic statistics —
`Track_B/Math_stat` statistics. Also: with only ~20 questions, an eval delta of
±1 answer is noise, not signal — sample size / confidence is the same topic.
Note *"revisit in Track_B: how many eval items do I need to trust a delta"* and
continue.

---

## Worked example — hit-rate + faithfulness

`code/eval_set.jsonl` (excerpt):

```json
{"q": "How do I set up my dev environment?", "gold_chunks": ["onboarding.md#1"], "gold": "Run make dev-setup then docker compose up.", "answerable": true}
{"q": "What is the CEO's home address?", "gold_chunks": [], "gold": "", "answerable": false}
```

`code/eval_rag.py` (core):

```python
import json
from rag import answer
from store import search

def evaluate(path="code/eval_set.jsonl", k=5):
    rows = [json.loads(l) for l in open(path, encoding="utf-8")]
    hits = faithful = refusal_ok = 0
    answerable = [r for r in rows if r["answerable"]]
    for r in rows:
        retrieved = {f"{m['source']}#{m['chunk']}" for _, m, _ in search(r["q"], k=k)}
        out = answer(r["q"], k=k)
        if r["answerable"]:
            if set(r["gold_chunks"]) & retrieved: hits += 1
            faithful += judge(r["q"], out["text"], r["gold"])      # 1 if grounded & correct
        else:
            refusal_ok += "not covered" in out["text"].lower()
    n = len(answerable)
    print(f"hit-rate@{k}: {hits/n:.0%}   faithfulness: {faithful/n:.0%}   "
          f"refusal-correct: {refusal_ok/ (len(rows)-n):.0%}")
```

**Expected output** (two configs):

```
config A (k=5, no rerank):   hit-rate@5: 68%   faithfulness: 61%   refusal-correct: 75%
config B (k=20 -> rerank 5):  hit-rate@5: 88%   faithfulness: 79%   refusal-correct: 100%
```

Read it: reranking lifted hit-rate 20 points, and faithfulness followed —
better context in, better answers out. The refusal cases also improved because
fewer off-topic chunks were tempting the model.

---

## Build

- Write `eval_set.jsonl` (15–25 items, ~20% unanswerable). Derive gold chunks by
  actually looking in `corpus/`.
- Build `eval_rag.py` with hit-rate@k and an LLM `judge()` (0/1 grounded+correct).
- Run it against your **Session 4** config and your **Session 5** (rerank)
  config. Record both.
- Change one more thing (chunk size, k, filter) and re-run. Did the number move
  outside ±1 answer of noise?
- Tick the Stage 4 `README.md` checklist.

---

## Quick test (step 7 — answer from memory, then check)

1. Why evaluate retrieval and generation separately?
2. Define hit-rate@k and MRR.
3. What is faithfulness, and how is it graded here?
4. Why include unanswerable questions in the eval set?
5. With ~20 questions, is a 1-answer improvement meaningful?

<details><summary>Answers</summary>

1. A wrong answer can stem from bad retrieval or from bad generation on good
   context; the diagnosis and fix differ.
2. Hit-rate@k = fraction of questions where a gold chunk appears in the top-k.
   MRR = mean of 1/(rank of the first gold chunk).
3. Whether the answer follows only from the retrieved context (no
   hallucination); graded by an LLM judge against context + gold, or by hand.
4. To measure refusal behavior — a RAG system must decline when the corpus
   doesn't cover the question, not guess.
5. No — that's within noise for n≈20; you need a larger set or a repeated run to
   trust a small delta.

</details>

---

## Done when

- [ ] `eval_set.jsonl` exists with answerable and unanswerable items.
- [ ] `eval_rag.py` prints hit-rate@k, faithfulness, and refusal-correctness.
- [ ] You have numbers for ≥2 configs and know which is better and by how much.
- [ ] Stage 4 `README.md` checklist fully ticked.

## Pitfalls

- **Gold chunks guessed, not verified** — check `corpus/` for each.
- **Judge prompt too loose** — it'll rate hallucinations as fine. Tight rubric,
  require it to quote the supporting context.
- **Reading noise as signal** — small n, small deltas mean little.

## Carries to next stage

You can build, ground, and *measure* a retrieval agent. **Stage 5** splits work
across multiple specialized agents — and pulls in
`Track_B/Math_stat/05_decision_and_orchestration_math` for routing.
