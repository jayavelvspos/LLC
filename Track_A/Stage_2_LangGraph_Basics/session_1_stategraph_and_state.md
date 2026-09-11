# Session 1 — Why a Graph? StateGraph & State (~45 min)

**Objective:** build the smallest possible LangGraph — two nodes in a line —
and understand what `State` is and how a node updates it.

**What you'll learn:**
- Nodes as `state -> partial state update` functions, connected by edges
- `State` as a typed dict every node reads from and writes to
- `START`/`END` sentinel nodes and `builder.compile()`
- Why moving control flow into a graph (vs. a hand-rolled loop) helps

**Prerequisites:** Stage 1 complete (you have a working hand-rolled agent).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why a graph at all — the Stage 1 pain points it addresses |
| 10–20 | Install; `StateGraph`, `State` TypedDict, `START`/`END` |
| 20–40 | Write `code/linear_graph.py` — two nodes, one edge, `invoke` |
| 40–45 | Notes |

---

## Concepts

- A LangGraph app is a **graph of nodes**. A **node** is a function
  `state -> partial state update`. Edges say which node runs next.
- **State** is a typed dict (a `TypedDict` or Pydantic model) that every node
  reads from and writes to. LangGraph merges each node's returned dict into the
  running state.
- `START` and `END` are sentinel nodes. `graph.add_edge(START, "a")`,
  `graph.add_edge("a", "b")`, `graph.add_edge("b", END)`.
- `graph = builder.compile()` gives you something with `.invoke(initial_state)`
  and `.stream(...)`.
- **Why bother** (vs the Stage 1 `while` loop): the branch logic, the
  "what runs next", and the state bookkeeping become *data* (a graph you can
  inspect, draw, checkpoint, and resume) instead of control flow tangled into
  one function.

---

## Learning resources

**Primary (official, stable):**
- **LangChain Academy — *Introduction to LangGraph*** (free course, video +
  notebooks): <https://academy.langchain.com/courses/intro-to-langgraph>.
  Module 1 covers exactly this session.
- LangGraph docs — *Low Level Concepts* (State, Nodes, Edges):
  <https://langchain-ai.github.io/langgraph/concepts/low_level/>.

**Video (pick one, ~15–30 min):**
- **LangChain** channel — search *"LangGraph introduction StateGraph"*.

---

## Track_B link (step 3)

**None.** Graph plumbing. Note "no Track_B link" and continue.

---

## Worked example — two nodes, one line

`code/linear_graph.py`:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    text: str
    steps: list[str]

def upper(state: State) -> dict:
    return {"text": state["text"].upper(), "steps": state["steps"] + ["upper"]}

def exclaim(state: State) -> dict:
    return {"text": state["text"] + "!!!", "steps": state["steps"] + ["exclaim"]}

builder = StateGraph(State)
builder.add_node("upper", upper)
builder.add_node("exclaim", exclaim)
builder.add_edge(START, "upper")
builder.add_edge("upper", "exclaim")
builder.add_edge("exclaim", END)
graph = builder.compile()

print(graph.invoke({"text": "hello graph", "steps": []}))
```

**Expected output:**

```
{'text': 'HELLO GRAPH!!!', 'steps': ['upper', 'exclaim']}
```

Read it: each node returned a **partial** dict; LangGraph merged it into state
and passed the merged state to the next node. `steps` accumulated because each
node explicitly rebuilt it — Session 4 shows how a *reducer* does that
automatically.

---

## Build

Build `linear_graph.py`. Then:
- Add a third node between the two; re-wire the edges.
- Have `upper` return `{}` (no update) → observe state passes through unchanged.
- Have both nodes write `text` and add an edge making them "parallel" (both from
  START) → observe the error / last-write behavior. Note what happened; Session
  4 explains why you need a reducer for concurrent writes.
- Call `graph.get_graph().draw_ascii()` (or `.draw_mermaid()`) and paste the
  diagram into `notes.md`.

---

## Quick test (step 7 — answer from memory, then check)

1. What is a node, as a function signature?
2. What does a node return, and what does LangGraph do with it?
3. What is `State` and who reads/writes it?
4. What do `START` and `END` do?
5. One concrete reason to use a graph instead of a `while` loop.

<details><summary>Answers</summary>

1. `state -> partial-state-update` (a dict of the keys it changed).
2. A partial dict; LangGraph merges it into the running state before the next
   node runs.
3. A typed dict every node reads from and writes to; it's the app's shared,
   inspectable memory.
4. Sentinel nodes marking the entry and exit of the graph.
5. The routing and state bookkeeping become inspectable data (drawable,
   checkpointable, resumable) instead of tangled control flow.

</details>

---

## Done when

- [ ] `linear_graph.py` runs and prints the merged final state.
- [ ] You've seen a node return `{}` and pass state through.
- [ ] You've drawn the graph and saved the diagram in `notes.md`.
- [ ] You can give the node signature from memory.

## Pitfalls

- **Returning the whole state** instead of just changed keys works but hides
  what a node actually does — return the minimal partial dict.
- **Concurrent writes to the same key** without a reducer is an error or a
  silent last-write — deferred to Session 4.

## Carries to next session

You can build a linear graph. Session 2 makes one node an LLM call and another a
tool executor.
