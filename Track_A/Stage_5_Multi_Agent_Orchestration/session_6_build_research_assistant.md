# Session 6 — Build the Research Assistant (~45 min)

**Objective:** assemble the guarded supervisor, the three worker sub-agents, and
parallel retrieval into `research.py` — a tool that turns a question into a
sourced written brief. Stage 5 deliverable.

**Prerequisites:** Sessions 1–5 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Final graph: supervisor ⇄ {plan, fan-out retrieve, analyze, write}, guarded |
| 10–35 | Write `code/research.py` (`research(question) -> {brief, sources, cost}`) |
| 35–43 | Run 3 questions; compare to a single-agent RAG baseline |
| 43–45 | Notes + tick the Stage 5 checklist |

---

## Concepts

- **Graph:** `plan` (outline) → `supervisor` loop → `retrieve` (fan-out over
  uncovered points) → `analyze` → `write` → `supervisor` says `DONE` →
  `finalize` (attach sources, compute cost).
- **Interface:** `research(question, budget_usd=0.50) -> {"brief": str,
  "sources": [...], "cost_usd": float, "steps": int, "halted": str | None}`.
- **Sources:** carried on each `note` from the retriever; `finalize` collects
  the unique set actually reflected in the draft.
- **Baseline:** keep a `simple_answer(question)` that just does Stage 4 RAG with
  a big `k`, for comparison. The point of the stage is to know *when the
  orchestration earns its cost*.
- Reuse everything: Stage 4 RAG (retriever), Stage 0 cost helper, Stage 2 graph,
  Session 5 `Budget`.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 4** ("Research
  Assistant") end to end: <https://academy.langchain.com/courses/intro-to-langgraph>.
- Anthropic — *multi-agent research system* post (re-read; their architecture
  maps onto yours).

**Video (optional, ~15–30 min):**
- **LangChain** channel — search *"LangGraph research assistant full build"*.

---

## Track_B link (step 3)

**Light, non-blocking** (routing = expected value; termination = absorbing-state
reasoning — Sessions 2 and 5). Note and continue. If
`Track_B/Math_stat/05_decision_and_orchestration_math` still isn't started,
schedule it — **Stage 6's** eval and budgeting work leans on statistics and
expected value too.

---

## Worked example — `research()` shape

```python
def research(question: str, budget_usd: float = 0.50) -> dict:
    budget = Budget(max_steps=20, max_usd=budget_usd)
    state = graph.invoke(
        {"question": question, "notes": [], "claims": [], "draft": "", "log": []},
        {"configurable": {"budget": budget}, "recursion_limit": 40})
    return {"brief": state["draft"],
            "sources": sorted({s for n in state["notes"] for s in n["sources"]}),
            "cost_usd": round(budget.usd, 4),
            "steps": budget.steps,
            "halted": next((l for l in state["log"] if l.startswith("[guard]")), None)}
```

**Expected output** (shape):

```
{'brief': '<~300 word sourced brief>',
 'sources': ['rfc-793.md#2', 'perf-guide.md#7', 'blog-2025.md#1'],
 'cost_usd': 0.14, 'steps': 7, 'halted': None}
```

Baseline comparison (same question):

```
orchestrated : cost $0.14, 7 steps, brief covers 5/5 outline points, 3 sources
single RAG   : cost $0.03, 1 call,  brief covers 3/5 points,          2 sources
```

Read it: orchestration cost ~5x more and covered the question more completely —
worth it for a research brief, *not* worth it for a quick factoid. That judgment
is the deliverable's real lesson.

---

## Build

Build `research.py`. Run:
1. A broad question (should fan out, use all workers) — inspect the `log`.
2. A narrow factoid — note it over-engineers; compare cost to `simple_answer`.
3. An unanswerable question — confirm a guard halts it under budget.

For each, record in `notes.md`: cost, steps, coverage vs the single-agent
baseline, and your verdict on whether orchestration was justified.

Tick every box in the Stage 5 `README.md` checklist.

---

## Quick test (step 7 — answer from memory, then check)

1. Name the nodes in the final graph, in order.
2. What does `research()` return, and why include `cost_usd` and `halted`?
3. Where do the `sources` come from?
4. Why keep a single-agent baseline around?
5. From your runs: name one question type where orchestration won and one where
   it just cost more.

<details><summary>Answers</summary>

1. `plan` → `supervisor` (loop) → `retrieve` (fan-out) → `analyze` → `write` →
   `supervisor`→`DONE` → `finalize`.
2. `{brief, sources, cost_usd, steps, halted}` — cost and halt reason make every
   run's economics and safety visible, which is the stage's whole point.
3. Attached to each retriever `note` (the chunk ids it used); `finalize`
   collects the unique set.
4. To measure when the extra orchestration cost actually buys better answers vs
   when a single RAG call suffices.
5. (Your own data.) Typically: broad/multi-part research questions win;
   single-fact lookups just cost more.

</details>

---

## Done when

- [ ] `research.py` produces a sourced brief with a cost and step count.
- [ ] Fan-out retrieval is used for multi-point questions.
- [ ] A guard halts a bad run within budget.
- [ ] You have a written verdict (orchestration vs single-agent) for ≥3
      questions.
- [ ] Stage 5 `README.md` checklist fully ticked.

## Pitfalls

- **No baseline** — you can't tell if the complexity paid off.
- **Sources listed that the draft doesn't actually use** — collect from the
  draft's cited notes, not everything retrieved.
- **Budget passed but never checked in every model-calling node** — thread it
  through consistently.

## Carries to next stage

You can orchestrate multiple agents safely and know when it's worth it.
**Stage 6** makes the whole thing production-grade: logging, evals, retries,
cost/latency budgets, guardrails, deployment.
