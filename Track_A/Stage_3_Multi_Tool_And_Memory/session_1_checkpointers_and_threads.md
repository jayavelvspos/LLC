# Session 1 — Checkpointers & Threads (~45 min)

**Objective:** add a checkpointer so a conversation persists between `invoke`
calls, keyed by a `thread_id`.

**What you'll learn:**
- Checkpointed state per thread as LangGraph's model of "memory"
- `MemorySaver` and compiling with `checkpointer=...`
- The `thread_id` config and invoking with just the new message
- `get_state` / `get_state_history` for the current and past checkpoints

**Prerequisites:** Stage 2 complete (`agent_graph.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What "memory" means in LangGraph: checkpointed state per thread |
| 10–20 | `MemorySaver`; `compile(checkpointer=...)`; the `thread_id` config |
| 20–40 | `code/memory_graph.py` — two `invoke`s, same thread, second depends on first |
| 40–45 | Notes |

---

## Concepts

- Without a checkpointer, each `invoke` starts from the state you pass — the
  graph has no memory between calls.
- A **checkpointer** saves the full graph state after every super-step. Compile
  with `graph = builder.compile(checkpointer=MemorySaver())`.
- Every call now needs a **thread**: `graph.invoke(inp, {"configurable":
  {"thread_id": "user-42"}})`. State is loaded for that thread, updated, saved.
- You can `invoke` with just the *new* message — the checkpointer supplies the
  history (the `add_messages` reducer appends it).
- `graph.get_state(config)` returns the current checkpoint;
  `graph.get_state_history(config)` returns every past checkpoint (this is what
  makes time-travel / resume possible).
- `MemorySaver` is in-process only — lost on restart. Session 2 fixes that.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 2** ("State and
  Memory") and **Module 3** ("Persistence"):
  <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Persistence* and *Add memory* how-to:
  <https://langchain-ai.github.io/langgraph/concepts/persistence/>.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph persistence checkpointer thread_id"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — one thread, two turns

```python
from langgraph.checkpoint.memory import MemorySaver

graph = builder.compile(checkpointer=MemorySaver())
cfg = {"configurable": {"thread_id": "demo"}}

graph.invoke({"messages": [("user", "My favourite city is Lisbon.")]}, cfg)
out = graph.invoke({"messages": [("user", "What's the weather there?")]}, cfg)
print(out["messages"][-1].content)

print("checkpoints:", len(list(graph.get_state_history(cfg))))
```

**Expected output** (shape):

```
It's about 18 C in Lisbon right now.
checkpoints: 4
```

Read it: the second `invoke` only sent *"What's the weather there?"* — "there"
resolved to Lisbon because the checkpointer reloaded the first turn into state.
Change `thread_id` on the second call and the model has no idea what "there"
means.

---

## Build

Add `MemorySaver` to `agent_graph.py` → `memory_graph.py`. Then:
- Run a 4-turn conversation on one thread; then start a fresh `thread_id` and
  confirm total amnesia.
- Print `graph.get_state(cfg).values["messages"]` after each turn; watch it grow.
- Restart the Python process and re-run → confirm memory is **gone**
  (`MemorySaver` is in-process). This motivates Session 2.

---

## Quick test (step 7 — answer from memory, then check)

1. What does a checkpointer save, and when?
2. What must every `invoke` include once you compile with a checkpointer?
3. Why can you now `invoke` with only the new message?
4. What does `get_state_history` give you, and why is that useful?
5. What's the limitation of `MemorySaver`?

<details><summary>Answers</summary>

1. The full graph state, after every super-step.
2. A `thread_id` in the config: `{"configurable": {"thread_id": ...}}`.
3. The checkpointer reloads the thread's prior state; the `add_messages` reducer
   appends the new message to the restored history.
4. Every past checkpoint for the thread — enables inspection, resume, and
   time-travel.
5. In-process only; all threads are lost when the process exits.

</details>

---

## Done when

- [ ] A follow-up turn resolves a reference ("there", "it") from an earlier turn
      on the same thread.
- [ ] A different `thread_id` shows no shared memory.
- [ ] You've confirmed `MemorySaver` state is lost on restart.
- [ ] You can state what a `thread_id` selects.

## Pitfalls

- **Re-sending full history AND using a checkpointer** double-appends. Send only
  the new turn.
- **Reusing one `thread_id` for all users** cross-contaminates conversations.
- **Assuming persistence** — `MemorySaver` has none.

## Carries to next session

Memory works but is volatile. Session 2 swaps in a durable checkpointer and
separates thread state from a long-term store.
