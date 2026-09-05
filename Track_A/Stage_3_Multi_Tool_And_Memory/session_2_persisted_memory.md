# Session 2 — Persisted Memory (~45 min)

**Objective:** make memory survive a process restart with a SQLite checkpointer,
and understand the difference between per-thread checkpoint state and a
cross-thread long-term store.

**Prerequisites:** Session 1 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Durable checkpointers; two kinds of "memory" |
| 10–30 | Swap `MemorySaver` → `SqliteSaver`; restart-proof the demo |
| 30–40 | Add a tiny long-term store (facts about the user across threads) |
| 40–45 | Notes |

---

## Concepts

- **Checkpointer = thread memory.** `SqliteSaver.from_conn_string(
  "assistant.sqlite")` (or the Postgres saver) persists every checkpoint to
  disk. Restart the process, pass the same `thread_id`, and the conversation is
  right there.
- **Store = long-term memory.** A separate key-value store (LangGraph's
  `BaseStore` / `InMemoryStore` / a DB) holds facts you want available across
  *all* threads for a user — preferences, profile, learned facts. Nodes read/
  write it via the `store` argument.
- Rule of thumb: **thread state** = "what was said in this conversation";
  **store** = "what we know about this user regardless of conversation".
- Writing to the store is a deliberate act (a node, or a `save_memory` tool),
  not automatic — you decide what's worth persisting.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 3** ("Persistence")
  and **Module 5** ("Long-Term Memory"):
  <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Persistence* (SQLite/Postgres savers) and *Memory Store*:
  <https://langchain-ai.github.io/langgraph/concepts/persistence/>.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph long term memory store"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — restart-proof memory

```python
from langgraph.checkpoint.sqlite import SqliteSaver

with SqliteSaver.from_conn_string("code/assistant.sqlite") as cp:
    graph = builder.compile(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "jay-main"}}
    graph.invoke({"messages": [("user", "Remember: I deploy on Fridays.")]}, cfg)

# --- process exits here; run the script again with only this: ---
with SqliteSaver.from_conn_string("code/assistant.sqlite") as cp:
    graph = builder.compile(checkpointer=cp)
    cfg = {"configurable": {"thread_id": "jay-main"}}
    out = graph.invoke({"messages": [("user", "When do I deploy?")]}, cfg)
    print(out["messages"][-1].content)
```

**Expected output** (second run, fresh process):

```
You deploy on Fridays.
```

Read it: nothing was passed but the new question — the SQLite file carried the
whole thread across the restart. With `MemorySaver` (Session 1) this second run
would answer "I don't know".

---

## Build

- Swap your Session 1 graph to `SqliteSaver`; prove restart persistence.
- Add an `InMemoryStore` (or SQLite-backed store) and a `remember(fact)` tool
  that writes `(user_id, fact)`; add a node that loads that user's facts into
  the system prompt at the start of each turn.
- Start a **new** `thread_id` for the same `user_id` → confirm the stored facts
  are available even though the conversation history isn't.
- Delete `assistant.sqlite` → confirm clean slate. Add it to `.gitignore`.

---

## Quick test (step 7 — answer from memory, then check)

1. What does a durable checkpointer change vs `MemorySaver`?
2. Define thread state vs a long-term store in one line each.
3. Which one is scoped per conversation, which per user?
4. Is writing to the store automatic? How does it happen?
5. Same user, new `thread_id`: what's available and what isn't?

<details><summary>Answers</summary>

1. Checkpoints are written to disk (SQLite/Postgres), so threads survive process
   restarts.
2. Thread state = what was said in this conversation. Store = what we know about
   this user across all conversations.
3. Thread state = per conversation (`thread_id`); store = per user (`user_id`).
4. No — a node or a tool explicitly writes chosen facts to the store.
5. The stored user facts are available; the previous conversation's message
   history is not.

</details>

---

## Done when

- [ ] A conversation resumes correctly after a full process restart.
- [ ] A stored user fact is visible from a brand-new thread.
- [ ] `assistant.sqlite` is git-ignored.
- [ ] You can articulate thread-state vs store from memory.

## Pitfalls

- **Putting everything in the store** — it becomes an unbounded dumping ground.
  Persist deliberately.
- **Leaking one user's store to another** — always scope by `user_id`.
- **Not closing the saver** — use the context manager or an explicit connection
  lifecycle.

## Carries to next session

Memory is durable — and therefore *grows*. Session 3 keeps context (and cost)
bounded with trimming and summarization.
