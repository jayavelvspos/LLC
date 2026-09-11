# Session 2 — The Supervisor / Router (~45 min)

**Objective:** replace the fixed hand-off order with a supervisor that decides,
each step, which worker runs next (or whether the work is done).

**What you'll learn:**
- The supervisor pattern: a central node deciding the next worker or `DONE`
- Making the routing decision structured (enum/tool call), not free text
- Routing as an expected-value decision under uncertainty
- `Command(goto=..., update=...)` and why a hard step cap still matters

**Prerequisites:** Session 1 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The supervisor pattern; routing as a decision |
| 10–20 | **Track_B checkpoint** — does "pick the best next worker" feel principled? |
| 20–40 | `code/supervisor.py` — structured routing output → next node |
| 40–45 | Notes |

---

## Concepts

- **Supervisor pattern:** a central node reads the shared state and emits a
  decision: `next: "retriever" | "analyzer" | "writer" | "DONE"`. A conditional
  edge routes to that node; each worker returns to the supervisor.
- Make the decision **structured** — a tool call or `output_config.format` with
  an enum — so you never parse free text for control flow.
- **Routing is a decision under uncertainty:** given the state, which worker has
  the highest expected value (progress per unit cost)? A good supervisor prompt
  encodes that: "route to the cheapest worker that can make progress; only route
  to `writer` when every outline point has support."
- **Termination:** the supervisor must be able to say `DONE`, and there must be
  a hard step cap in case it won't (Session 5).
- LangGraph offers `Command(goto=..., update=...)` from inside a node, and a
  prebuilt `langgraph-supervisor` package — but hand-write it once.

---

## Learning resources

**Primary (official, stable):**
- LangGraph docs — *Multi-agent: supervisor* and `Command`:
  <https://langchain-ai.github.io/langgraph/concepts/multi_agent/#supervisor>.
- LangChain Academy — *Introduction to LangGraph*, **Module 4**
  ("Sub-graphs", "Map-reduce", "Research assistant"):
  <https://academy.langchain.com/courses/intro-to-langgraph>.
- Anthropic — *Building effective agents* (routing workflow):
  <https://www.anthropic.com/research/building-effective-agents>.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph supervisor multi-agent tutorial"*.

---

## Track_B link (step 3) — possible revisit point

Routing = choosing the action with the best expected outcome. That's
`Track_B/Math_stat/05_decision_and_orchestration_math` (expected value,
decisions under uncertainty). **If** your supervisor's choices feel like
guesswork — you can't articulate why routing to A beats B — spend 20–30 min
there on expected value, then return. Otherwise note
*"revisit in Track_B: expected-value routing"* and continue.

---

## Worked example — structured routing

`code/supervisor.py` (core):

```python
from typing import Literal
from pydantic import BaseModel

class Route(BaseModel):
    next: Literal["retriever", "analyzer", "writer", "DONE"]
    reason: str

SUP_SYS = ("You coordinate a research team. State has: outline, notes, draft. "
           "Route to the cheapest worker that advances the work. "
           "retriever: gather facts for uncovered outline points. "
           "analyzer: turn notes into supported claims. "
           "writer: only when every outline point has support. "
           "DONE: only when a complete draft exists.")

def supervisor(state) -> dict:
    r = model.with_structured_output(Route).invoke(
        [("system", SUP_SYS), ("user", summarize(state))])
    return {"route": r.next, "log": [f"-> {r.next}: {r.reason}"]}

# conditional edge:
def pick(state): return END if state["route"] == "DONE" else state["route"]
```

**Expected output** (`log` after a run):

```
-> retriever: outline points 2 and 4 have no notes
-> retriever: point 4 still thin
-> analyzer: enough notes to form claims
-> writer: all 5 points supported
-> DONE: full draft present
```

Read it: no fixed order — the supervisor kept calling `retriever` until coverage
was good, then moved on. The `reason` field makes the routing auditable.

---

## Build

- Build `supervisor.py` with 3 stub workers (they just append to state) and the
  structured `Route`.
- Give the supervisor a state where the draft is already done → it should route
  `DONE` immediately.
- Remove the "cheapest worker" instruction → observe routing get wasteful
  (jumps to `writer` early, has to backtrack). Restore it.
- Add a `step` counter; print the route each step.

---

## Quick test (step 7 — answer from memory, then check)

1. What does the supervisor read, and what does it emit?
2. Why must the routing decision be structured output, not free text?
3. Frame routing as a decision problem in one sentence.
4. Two things the supervisor prompt must guarantee about termination.
5. What makes routing auditable in the worked example?

<details><summary>Answers</summary>

1. It reads the shared state; it emits a structured decision naming the next
   worker (or `DONE`).
2. Control flow must not depend on parsing prose; an enum/tool call is
   unambiguous and validatable.
3. Given the current state, pick the worker with the highest expected progress
   per unit cost.
4. It must be able to output `DONE`, and there must be a hard step cap as a
   backstop.
5. The `reason` field logged with each route decision.

</details>

---

## Done when

- [ ] `supervisor.py` routes dynamically based on state, not a fixed order.
- [ ] Routing decisions are structured (enum) and logged with reasons.
- [ ] You've seen good vs wasteful routing by toggling the "cheapest worker"
      rule.
- [ ] Track_B checkpoint done (switched or logged).

## Pitfalls

- **Free-text routing** — one reword and the graph misroutes.
- **No `DONE` path** — the supervisor loops until the step cap every time.
- **Supervisor sees full raw state** — summarize it; a huge prompt makes routing
  worse and pricier.

## Carries to next session

The supervisor decides; the workers are stubs. Session 3 makes the workers real
sub-agents and defines what state they share.
