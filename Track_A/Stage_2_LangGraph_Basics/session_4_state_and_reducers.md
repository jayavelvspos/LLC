# Session 4 — State & Reducers (~45 min)

**Objective:** understand how LangGraph merges node updates into state, why
`messages` needs the `add_messages` reducer, and how to define your own.

**What you'll learn:**
- Default state merge (overwrite) vs. a reducer (combine)
- `Annotated[list, reducer]` and how LangGraph calls a reducer to merge
- What `add_messages` does: append, plus update-by-id
- How reducers resolve concurrent writes to the same state key

**Prerequisites:** Session 3 complete (a working graph loop).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Default merge (overwrite) vs a reducer (combine) |
| 10–25 | `Annotated[list, add_messages]`; what `add_messages` does |
| 25–40 | Define a custom reducer; add a second state key |
| 40–45 | Notes |

---

## Concepts

- By default, a node's returned value for a key **overwrites** that key in
  state. Fine for scalars (`current_city`), wrong for accumulators (`messages`,
  `steps`, `errors`).
- A **reducer** is a function `(old, update) -> new` attached to a state key via
  `Annotated[T, reducer]`. LangGraph calls it to merge instead of overwrite.
- `add_messages` is the reducer for chat history: it appends new messages, and
  it can **update by id** (a message with an existing id replaces it) — needed
  for streaming and edits.
- Reducers also resolve **concurrent writes**: if two branches both update
  `messages` in the same super-step, the reducer combines them
  deterministically. Without one, concurrent writes to a key error out.
- `MessagesState` is just `class MessagesState(TypedDict): messages:
  Annotated[list, add_messages]`.

---

## Learning resources

**Primary (official, stable):**
- LangGraph docs — *State reducers* and *`add_messages`*:
  <https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers>.
- LangChain Academy — *Introduction to LangGraph*, **Module 2** ("State and
  Memory"): <https://academy.langchain.com/courses/intro-to-langgraph>.

**Video (pick one, ~10–20 min):**
- **LangChain** channel — search *"LangGraph state reducers add_messages"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — overwrite vs reduce

```python
from typing import Annotated, TypedDict
from operator import add
from langgraph.graph import StateGraph, START, END

class State(TypedDict):
    last: str                      # no reducer -> overwrite
    log: Annotated[list, add]      # reducer -> concatenate

def a(s): return {"last": "a", "log": ["a"]}
def b(s): return {"last": "b", "log": ["b"]}

g = StateGraph(State)
g.add_node("a", a); g.add_node("b", b)
g.add_edge(START, "a"); g.add_edge("a", "b"); g.add_edge("b", END)
print(g.compile().invoke({"last": "", "log": []}))
```

**Expected output:**

```
{'last': 'b', 'log': ['a', 'b']}
```

Read it: `last` was overwritten (only `b`'s value survives); `log` was **reduced**
with `add`, so both entries are kept. Swap `add` out and `log` becomes `['b']`
too — that's the bug `add_messages` exists to prevent for chat history.

---

## Build

- Add an `errors: Annotated[list, add]` key to your agent graph; have the tool
  node append to it on `is_error`.
- Write a custom reducer `keep_last_n(n)` (returns `(old + update)[-n:]`) and use
  it on a `recent_tools` key.
- Make two nodes both write `messages` from a single parent (fan-out), join them,
  and confirm `add_messages` merges both without error. Remove the annotation →
  see the concurrent-write error.

---

## Quick test (step 7 — answer from memory, then check)

1. What happens by default when two nodes write the same state key in sequence?
2. What is a reducer, as a signature?
3. Give two things `add_messages` does beyond plain append.
4. Why do concurrent (fan-out) writes need a reducer?
5. Write the definition of `MessagesState`.

<details><summary>Answers</summary>

1. The later write overwrites the earlier one.
2. `(old_value, update) -> new_value`, attached via `Annotated[T, reducer]`.
3. Appends new messages; replaces an existing message when the update has a
   matching id (supports streaming/edits).
4. Without one, two updates to the same key in the same super-step conflict and
   error; the reducer defines a deterministic merge.
5. `class MessagesState(TypedDict): messages: Annotated[list, add_messages]`.

</details>

---

## Done when

- [ ] You've seen overwrite vs reduced behavior side by side.
- [ ] Your agent graph has an extra reduced key (`errors` or similar) that
      accumulates.
- [ ] You wrote and used a custom reducer.
- [ ] You can define `MessagesState` from memory.

## Pitfalls

- **No reducer on an accumulator key** → silent data loss (only the last node's
  contribution survives).
- **A reducer with side effects** — keep it pure; it may be called more than
  once.
- **Mutating `old` in place** instead of returning a new value.

## Carries to next session

You understand the state model. Session 5 adds tracing and rebuilds the full
Stage 1 agent as `agent_graph.py` — the deliverable.
