# Session 3 — Worker Sub-Agents & Hand-off (~45 min)

**Objective:** turn the stub workers into real sub-agents (each its own
graph/loop), and decide deliberately what state is shared vs isolated.

**What you'll learn:**
- A worker sub-agent as a compiled graph/function added as a node
- Designing shared vs. isolated state deliberately
- Reusing the Stage 4 RAG agent as a retriever worker
- A uniform worker interface contract: `run(subtask, shared_slice) -> update`

**Prerequisites:** Session 2 complete (`supervisor.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Sub-graphs as nodes; shared vs isolated state |
| 10–35 | `code/workers.py` — retriever (RAG), analyzer, writer as sub-agents |
| 35–43 | Wire into the supervisor graph; run end to end |
| 43–45 | Notes |

---

## Concepts

- A **worker sub-agent** is a compiled graph (or a plain function that runs its
  own tool loop). It's added as a node; it receives an input, does its job, and
  returns an update to the shared state.
- **State design is the core decision:**
  - *Shared* keys — `outline`, `notes`, `draft`, `log` — every worker and the
    supervisor read/write these (with reducers, Stage 2 Session 4).
  - *Isolated* — a worker's own scratch messages, tool-call chatter, retrieved
    raw chunks. Keep these inside the sub-graph; return only the distilled
    result to shared state.
- **Reuse:** the retriever is the Stage 4 RAG agent, wrapped. The analyzer and
  writer are Stage 1-style tool loops or single calls.
- **Input to a worker** should be a focused brief (the sub-task + relevant
  shared keys), not the whole state — mirrors the hand-off rule from Session 1.
- **Interface contract:** each worker `run(subtask, shared_slice) -> partial
  update`. Keep it uniform so the supervisor treats them alike.

---

## Learning resources

**Primary (official, stable):**
- LangGraph docs — *Subgraphs* (shared vs different state schemas; how state
  maps in/out): <https://langchain-ai.github.io/langgraph/how-tos/subgraph/>.
- LangChain Academy — *Introduction to LangGraph*, **Module 4** ("Research
  assistant" builds exactly this shape).
- Anthropic — *multi-agent research system* engineering post (worker prompts,
  what to isolate).

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph subgraphs research assistant"*.

---

## Track_B link (step 3)

**None** for wiring sub-agents. Note "no Track_B link" and continue. (If the
Session 2 routing revisit is still open, keep it on the backlog.)

---

## Worked example — uniform worker interface

`code/workers.py` (shape):

```python
def retriever(subtask: str, shared: dict) -> dict:
    hits = rag_search(subtask, k=6)                 # Stage 4
    note = summarize_hits(subtask, hits)            # distil: raw chunks stay here
    return {"notes": [{"point": subtask, "text": note,
                       "sources": [h.id for h in hits]}]}

def analyzer(subtask: str, shared: dict) -> dict:
    claims = model.invoke(analyze_prompt(shared["notes"])).content
    return {"claims": [claims]}

def writer(subtask: str, shared: dict) -> dict:
    draft = model.invoke(write_prompt(shared["outline"], shared["claims"])).content
    return {"draft": draft}

WORKERS = {"retriever": retriever, "analyzer": analyzer, "writer": writer}
```

In the graph, each worker node calls `WORKERS[name](state["current_subtask"],
state)` and returns its partial update; then edges back to `supervisor`.

**Expected output** (state after a full run, keys only):

```
outline: [5 points]
notes:   [5 entries, each with text + sources]   <- from retriever, raw chunks NOT here
claims:  [1 block of supported claims]           <- from analyzer
draft:   "<~250 word brief>"                     <- from writer
log:     [routing trail from session 2]
```

Read it: `notes` holds *distilled* findings with source ids, not the raw
retrieved text — that stayed isolated inside `retriever`. Shared state is small
and clean, so routing and the final assembly stay cheap.

---

## Build

- Build `workers.py` with the uniform `run(subtask, shared)` interface; the
  retriever must reuse your Stage 4 RAG code.
- Wire the three workers into the supervisor graph from Session 2; run 2 research
  questions end to end.
- Deliberately share too much: have `retriever` dump raw chunks into shared
  `notes`. Watch the supervisor prompt balloon and routing degrade. Revert.
- Print the size (chars/tokens) of shared state after each worker — keep it flat.

---

## Quick test (step 7 — answer from memory, then check)

1. What is a worker sub-agent, structurally?
2. Give two examples each of state that should be shared vs isolated.
3. What should a worker return to shared state?
4. Why give a worker a focused brief instead of the whole state?
5. Why keep a uniform worker interface?

<details><summary>Answers</summary>

1. A compiled sub-graph (or self-contained tool loop) added as a node; it takes
   an input and returns a partial update to shared state.
2. Shared: outline, notes, draft, log. Isolated: a worker's scratch messages,
   tool-call chatter, raw retrieved chunks.
3. Only the distilled result (e.g. notes with source ids) — not its working
   context.
4. Isolation and cost: passing full state inflates every worker call and lets
   one worker's mess pollute others.
5. So the supervisor can invoke any worker the same way, and workers stay
   swappable.

</details>

---

## Done when

- [ ] Three real workers run under the supervisor and produce a draft.
- [ ] The retriever reuses Stage 4 RAG.
- [ ] Shared state stays small; raw retrieved text is isolated.
- [ ] You can classify shared vs isolated state from memory.

## Pitfalls

- **Leaking raw context into shared state** — the most common cost blow-up.
- **Divergent worker interfaces** — makes the supervisor a special-case mess.
- **Workers writing the same shared key without a reducer** — Stage 2 Session 4
  problem; add `Annotated[..., add]`.

## Carries to next session

Workers run one at a time. Session 4 fans several out in parallel and reduces
their outputs.
