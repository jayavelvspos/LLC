# Session 5 — Build the Task Assistant (~45 min)

**Objective:** assemble memory + persistence + bounded context + approval gate
into `assistant.py` — a task assistant with a clean
`chat(thread_id, message) -> str` interface. Stage 3 deliverable.

**What you'll learn:**
- Assembling a full node order: summarize -> model -> review -> tools -> model
- A `chat()`/`resume()` interface that surfaces interrupts to the caller
- Wiring persistence (`SqliteSaver`) and a `user_id`-scoped long-term store
- Config constants that tie summarization, approval, and recursion limits together

**Prerequisites:** Sessions 1–4 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Assemble the graph: summarize → model → review → tools → model |
| 10–35 | Write `code/assistant.py` (graph + `chat()` + a tiny REPL) |
| 35–43 | Run a multi-session scenario (restart in the middle) |
| 43–45 | Notes + tick the Stage 3 checklist |

---

## Concepts

- **Node order:** `maybe_summarize` → `model` → `review_tools` (conditional) →
  `tools` → back to `model`. Conditional edge from `model` uses
  `tools_condition`.
- **Interface:** `chat(thread_id, message)` builds the config, invokes the
  graph, and returns the last message text — or an `INTERRUPT` marker plus the
  proposed calls if it paused. A second function `resume(thread_id, decision)`
  continues.
- **Tools:** Stage 1's read tools + at least one gated write tool
  (`create_ticket` or `send_email`, can be a stub that appends to a file).
- **Persistence:** `SqliteSaver` on `code/assistant.sqlite`; a `user_id` in
  config for the long-term store.
- **Config constants:** `MODEL`, `SUMMARIZE_AFTER`, `KEEP_RECENT`,
  `RECURSION_LIMIT`, `NEEDS_APPROVAL`.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 6** ("Assistant" /
  capstone): <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — the *multi-tool agent with memory* how-to end to end.

**Video (optional, ~15–30 min):**
- **LangChain** channel — search *"LangGraph full agent memory human in the
  loop"*.

---

## Track_B link (step 3)

**Light, non-blocking** (same as Session 3 — the summarize/keep threshold is an
expected-value call). Note and continue. If linear algebra in Track_B hasn't
started, schedule it now: **Stage 4 needs it.**

---

## Worked example — `chat()` over the assembled graph

```python
def chat(thread_id: str, message: str, user_id: str = "default") -> dict:
    cfg = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
    state = graph.invoke({"messages": [("user", message)]}, cfg,
                         {"recursion_limit": RECURSION_LIMIT})
    if state.get("__interrupt__"):
        return {"status": "needs_approval",
                "proposed": state["__interrupt__"][0].value["proposed"]}
    return {"status": "ok", "reply": state["messages"][-1].content}

def resume(thread_id: str, decision: dict, user_id: str = "default") -> dict:
    cfg = {"configurable": {"thread_id": thread_id, "user_id": user_id}}
    state = graph.invoke(Command(resume=decision), cfg)
    return {"status": "ok", "reply": state["messages"][-1].content}
```

**Expected output** (scripted scenario):

```
>>> chat("t1", "I'm planning a launch for next Tuesday.")
{'status': 'ok', 'reply': 'Noted - launch next Tuesday. ...'}
# ... restart the process ...
>>> chat("t1", "Create a ticket to prep the release notes.")
{'status': 'needs_approval', 'proposed': [{'name': 'create_ticket', 'args': {...}}]}
>>> resume("t1", {"action": "approve"})
{'status': 'ok', 'reply': 'Ticket created: "Prep release notes" (due Mon).'}
```

Memory survived the restart, context stays bounded by the summarizer, and the
write was gated.

---

## Build

Build `assistant.py`. Run this scenario, checking behavior at each step:
1. 3 turns establishing context (name, a project, a deadline).
2. Restart the process.
3. A follow-up that needs turn-1 context → answered correctly.
4. Ask it to do a write action → gets held → approve.
5. Push the thread past `SUMMARIZE_AFTER` → confirm the summary appears in state
   and per-turn input tokens flatten.
6. Reject a write action → model re-plans.

Tick every box in the Stage 3 `README.md` checklist.

---

## Quick test (step 7 — answer from memory, then check)

1. What's the node order in the assembled graph?
2. What does `chat()` return in the normal case vs when a write is proposed?
3. Which checkpointer, and why not `MemorySaver`?
4. What's scoped by `thread_id` vs by `user_id` here?
5. Name the five config constants and what each controls.

<details><summary>Answers</summary>

1. `maybe_summarize` → `model` → (`tools_condition`) → `review_tools` → `tools`
   → back to `model`.
2. Normal: `{"status": "ok", "reply": ...}`. Write proposed: `{"status":
   "needs_approval", "proposed": [...]}`, continued via `resume()`.
3. `SqliteSaver` — memory must survive restarts; `MemorySaver` is in-process.
4. `thread_id` = this conversation's history; `user_id` = long-term store of
   facts across conversations.
5. `MODEL` (which model), `SUMMARIZE_AFTER` (when to compress), `KEEP_RECENT`
   (verbatim tail), `RECURSION_LIMIT` (loop backstop), `NEEDS_APPROVAL` (which
   tools are gated).

</details>

---

## Done when

- [ ] The full scripted scenario passes, including the restart.
- [ ] Write actions are gated; approve/reject both work.
- [ ] Summarization keeps context bounded on a long thread.
- [ ] `chat()` / `resume()` are clean and importable.
- [ ] Stage 3 checklist in `README.md` fully ticked.

## Pitfalls

- **Interrupt state leaking between threads** — always pass the right
  `thread_id` to `resume()`.
- **Summarizer running inside the tool loop** — put it before `model`, once per
  user turn.
- **`assistant.sqlite` committed** — git-ignore it.

## Carries to next stage

You have a capable single agent with real memory. **Stage 4** grounds it in your
own documents (RAG) — and is the first stage where a Track_B detour into
`01_linear_algebra` is likely.
