# Session 4 — LangSmith Tracing & Datasets (~45 min)

**Objective:** make every run in this stage a structured, inspectable trace in
LangSmith, then save a dataset and run an eval against it so a change's effect is
a number, not a vibe.

**Prerequisites:** Sessions 1–3 complete. A LangSmith account + API key
(free tier is enough). `pip install langsmith`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What a trace is; runs, spans, tags, metadata |
| 10–25 | Turn on tracing; re-run Session 2/3 chains; read the trace tree |
| 25–40 | `code/traced_run.py` — a dataset + an evaluator + `evaluate()` |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Enable tracing** with env vars — no code change for LCEL/LangGraph:
  `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY=...`, `LANGSMITH_PROJECT=track-a`.
  Every `.invoke` then logs a **run tree**.
- **Trace vocabulary:** a **run** is one traced call; a **trace** is the whole
  tree for a top-level invoke; **spans** are child runs (each chain step, each
  model call, each tool). Each run has inputs, outputs, latency, token counts,
  cost, and any error.
- **`@traceable`** decorates a plain Python function so it shows up as a span
  too — use it on your own tools / glue code.
- **Tags & metadata:** attach `tags=["v2","routing"]` and
  `metadata={"prompt_rev": 7}` via `config={"tags": ..., "metadata": ...}` so you
  can filter runs later.
- **Datasets & `evaluate()`:** a dataset is a list of `{inputs, outputs}`
  examples in LangSmith. `evaluate(target_fn, data=<name>, evaluators=[...])`
  runs your function on every example and scores each with evaluator functions
  (`(run, example) -> {"key": ..., "score": ...}`), including LLM-as-judge.
- This is the substrate for **Stage 6** — the eval suite, CI gating, and
  cost/latency dashboards all read from these traces.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- LangSmith docs — *Tracing* quickstart and *Evaluation* quickstart:
  <https://docs.smith.langchain.com/>.
- LangSmith docs — *`@traceable`* and *`evaluate`* reference.

**Video (pick one, ~10–20 min):**
- Search *"LangSmith tracing tutorial"* — focus on reading the run tree and
  creating a dataset from traced runs.

---

## Track_B link (step 3)

**Light, non-blocking.** Reading a trace summary means reading distributions —
p50/p95 latency, token/cost spread across runs. Note *"revisit in Track_B:
statistics — percentiles, summarising a distribution"* and continue.

---

## Worked example — trace a chain, then evaluate it  <!-- step 4 -->

`code/traced_run.py`:

```python
import os
os.environ["LANGSMITH_TRACING"] = "true"      # + LANGSMITH_API_KEY, LANGSMITH_PROJECT in env

from langsmith import Client, traceable
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser

model = ChatAnthropic(model="claude-opus-5", max_tokens=1024)
chain = ChatPromptTemplate.from_messages(
    [("system", "Answer in one sentence."), ("human", "{q}")]) | model | StrOutputParser()

@traceable(name="answer")
def answer(q: str) -> str:
    return chain.invoke({"q": q}, config={"tags": ["v1"]})

print(answer("what is a vector clock?"))       # -> a trace appears in LangSmith

# ---- dataset + eval ----
client = Client()
ds = client.create_dataset("qa-smoke")
client.create_examples(
    inputs=[{"q": "capital of France?"}, {"q": "2+2?"}],
    outputs=[{"a": "Paris"}, {"a": "4"}],
    dataset_id=ds.id,
)

def contains_expected(run, example):
    got = (run.outputs or {}).get("output", "")
    want = example.outputs["a"].lower()
    return {"key": "contains_expected", "score": int(want in got.lower())}

from langsmith import evaluate
res = evaluate(lambda x: answer(x["q"]), data="qa-smoke", evaluators=[contains_expected])
print(res)
```

**Expected output** (shape):

```
A vector clock is a per-process array of counters used to derive a partial order of events in a distributed system.
<evaluate() summary: 2 examples, contains_expected mean 1.0>
```

Read it: the `answer` call produced a **trace tree** (answer → chain → prompt →
model) you can open in LangSmith, and `evaluate()` ran the function over the
dataset and scored each example — the same numbers Stage 6 will gate CI on.

---

## Build: `code/traced_run.py`  <!-- step 5 -->

Build it. Experiments:
1. **Re-run with tracing on.** Set the env vars, re-run Session 2's `routing.py`
   and Session 3's `eval_optimizer.py` unchanged. Open the traces: find the
   branch that ran, and the round-by-round drafts in the loop.
2. **Tag a change.** Edit the system prompt, tag the run `["v2"]`, and filter
   `v1` vs `v2` in LangSmith. Compare latency and token counts.
3. **LLM-as-judge evaluator.** Add a second evaluator that asks
   `claude-haiku-4-5` "is the answer correct given the reference? yes/no" and
   returns a 0/1 score. Compare it to the string-match evaluator on the same
   dataset — where do they disagree?

---

## Quick test (step 7 — answer from memory, then check)

1. What env vars turn on tracing for LCEL/LangGraph, with no code change?
2. Run vs trace vs span.
3. What does `@traceable` do?
4. What does an evaluator function take and return?
5. Why does Stage 6 depend on this session?

<details><summary>Answers</summary>

1. `LANGSMITH_TRACING=true`, `LANGSMITH_API_KEY`, and (optionally)
   `LANGSMITH_PROJECT`.
2. A run is one traced call; a trace is the full tree for a top-level invoke;
   spans are the child runs inside it.
3. Wraps a plain Python function so its call shows up as a span (inputs,
   outputs, latency, errors) in the trace.
4. `(run, example) -> {"key": name, "score": number}` — it grades one run
   against its dataset example (can be a string check or an LLM judge).
5. Stage 6's eval suite, CI gating, and cost/latency dashboards all read from
   these traces and datasets.

</details>

---

## Done when  <!-- step 8 -->

- [ ] Every chain/graph you've built this stage shows up as a trace tree in
      LangSmith.
- [ ] `traced_run.py` creates a dataset and runs `evaluate()` with ≥1 evaluator.
- [ ] You've compared two prompt versions by tag on latency/tokens.
- [ ] You can explain run/trace/span from memory.

## Pitfalls

- **Key set, `LANGSMITH_TRACING` not `true`** — no traces, no error.
- **Secrets in inputs** — traced runs store inputs verbatim; scrub API keys /
  PII before they enter a chain.
- **One-example datasets** — you can't see variance; use enough examples to
  trust the mean.
- **Judge with no reference** — give the LLM evaluator the expected output.

## Carries to next session

Full observability over chains and graphs. Session 5 connects Claude to **real
external tools** over **MCP** — and those tool calls will show up in your traces
too.
