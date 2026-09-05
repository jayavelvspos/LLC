# Stage 3 — Multi-Tool + Memory

**Stage goal:** make a single agent genuinely capable — it remembers earlier
turns (within a session and across restarts), keeps its context from growing
without bound, and pauses for human approval before doing anything with side
effects.

Five ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Checkpointers & threads](session_1_checkpointers_and_threads.md) | `MemorySaver` + `thread_id`; a conversation resumes across calls |
| 2 | [Persisted memory](session_2_persisted_memory.md) | Sqlite checkpointer; memory survives a process restart; thread state vs long-term store |
| 3 | [Context growth & summarization](session_3_context_growth_summarization.md) | `trim_messages` + a summary node; bounded context, cost under control |
| 4 | [Human-in-the-loop](session_4_human_in_the_loop.md) | `interrupt` before side-effecting tools; approve / edit / reject then resume |
| 5 | [Build the task assistant](session_5_build_task_assistant.md) | `assistant.py` — the Stage 3 deliverable |

## Conventions

Python 3.10+. Builds on Stage 2's `agent_graph.py`. Add `langgraph-checkpoint-
sqlite` for Session 2. `claude-opus-5` by default. Run every session with the
8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

> LangGraph API drift caveat from Stage 2 still applies — verify imports against
> current docs; the concepts are stable.

## Working files produced in this stage

```
Stage_3_Multi_Tool_And_Memory/
  code/
    memory_graph.py      # sessions 1–2
    summarizing_graph.py # session 3
    hitl_graph.py        # session 4
    assistant.py         # session 5 — the deliverable
    assistant.sqlite     # persisted checkpoints (git-ignored)
  notes.md
```

## Done with Stage 3 when

- [ ] The assistant answers a follow-up that depends on something said many
      turns earlier — after the process was restarted.
- [ ] Context length (and per-turn token cost) stays bounded on a long
      conversation.
- [ ] A side-effecting tool call is held for approval; you can approve, edit the
      arguments, or reject, and the run continues correctly.
- [ ] You can explain the difference between thread (checkpoint) state and a
      long-term memory store.
- [ ] `assistant.py` exposes a clean `chat(thread_id, message) -> str`.
