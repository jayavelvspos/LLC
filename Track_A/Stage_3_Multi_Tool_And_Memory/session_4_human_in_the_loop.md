# Session 4 — Human-in-the-Loop (~45 min)

**Objective:** pause the graph before a side-effecting tool runs, surface the
proposed call to a human, and resume with approve / edit / reject.

**What you'll learn:**
- Classifying tools as safe-to-autorun vs. needs-approval
- `interrupt()` inside a node vs. `interrupt_before=["tools"]` at compile
- Resuming a paused run with `Command(resume=...)`
- Approve / edit / reject as the three resume outcomes

**Prerequisites:** Session 3 complete. A checkpointer is required for this.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why a gate; which tools need one (writes, sends, spends, deletes) |
| 10–25 | `interrupt()` inside a node, or `interrupt_before=["tools"]` at compile |
| 25–40 | Resume with `Command(resume=...)`; handle approve / edit / reject |
| 40–45 | Notes |

---

## Concepts

- **Read tools** (search, get_weather) are safe to autorun. **Write tools**
  (send_email, create_ticket, transfer_funds, delete_file) need a human OK.
- Two mechanisms:
  - `interrupt(payload)` inside a node — pauses the run, returns the payload to
    the caller, and waits. Resuming re-runs that node with the resume value.
  - `compile(..., interrupt_before=["tools"])` — pause before a whole node.
- Because state is checkpointed, an interrupt can last milliseconds or days —
  the run resumes from the exact checkpoint when you call
  `graph.invoke(Command(resume=value), cfg)`.
- **Approve / edit / reject:** on resume you can let the call through unchanged,
  modify the tool arguments, or replace the `AIMessage` with a `ToolMessage`
  saying "rejected by user" so the model re-plans.
- Classify tools once (`SAFE` vs `NEEDS_APPROVAL`) and gate only the latter.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 3**
  ("Human-in-the-loop", "Breakpoints", "Dynamic breakpoints"):
  <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Human-in-the-loop* concepts and the `interrupt` how-to:
  <https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/>.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph human in the loop interrupt"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — gate the write tools

```python
from langgraph.types import interrupt, Command

NEEDS_APPROVAL = {"send_email", "create_ticket"}

def review_tools(state):
    ai = state["messages"][-1]
    risky = [c for c in ai.tool_calls if c["name"] in NEEDS_APPROVAL]
    if not risky:
        return {}
    decision = interrupt({"proposed": risky})      # <-- pauses here
    if decision["action"] == "reject":
        from langchain_core.messages import ToolMessage
        return {"messages": [ToolMessage(tool_call_id=c["id"],
                    content="User rejected this action.") for c in risky]}
    if decision["action"] == "edit":
        ai.tool_calls = decision["tool_calls"]     # swap in edited args
    return {}                                       # approve -> fall through to ToolNode
```

Run, hit the interrupt, then:

```python
state = graph.invoke({"messages": [("user", "Email the team that deploy is delayed.")]}, cfg)
print(state["__interrupt__"])                       # shows proposed call
graph.invoke(Command(resume={"action": "approve"}), cfg)
```

**Expected output** (shape):

```
[Interrupt(value={'proposed': [{'name': 'send_email', 'args': {...}}]})]
# after resume:
{'tools': {'messages': [ToolMessage('email sent')]}}
{'model': {'messages': [AIMessage(content='Done - I emailed the team.')]}}
```

Read it: the graph stopped *before* `send_email` ran, handed you the proposed
arguments, and only executed after `Command(resume=...)`.

---

## Build

- Add `review_tools` before `ToolNode`; classify your Stage 1 tools (add a fake
  `send_email` / `create_ticket`).
- Exercise all three paths: approve, edit the args then approve, reject → model
  re-plans.
- Interrupt, kill the process, restart, resume with `Command(resume=...)` on the
  same thread → confirm it continues (this needs the SQLite checkpointer).

---

## Quick test (step 7 — answer from memory, then check)

1. Which tools get a gate and which don't?
2. Two ways to pause a graph for human input.
3. Why can an interrupt safely last for days?
4. How do you resume, and how do you implement "reject"?
5. How do you implement "edit the arguments"?

<details><summary>Answers</summary>

1. Side-effecting tools (send/write/spend/delete) get a gate; read-only tools
   (search, fetch) autorun.
2. `interrupt(payload)` inside a node; or `interrupt_before=[node]` at
   `compile`.
3. State is checkpointed, so the run resumes from the exact saved checkpoint
   whenever `Command(resume=...)` is called.
4. `graph.invoke(Command(resume=value), cfg)`. Reject = return a `ToolMessage`
   saying the user declined, so the model re-plans instead of the tool running.
5. Replace the `AIMessage.tool_calls` (or the specific call's `args`) with the
   edited version before flow reaches the tool node.

</details>

---

## Done when

- [ ] A write tool is held; approve/edit/reject all work.
- [ ] A resume works after a process restart on the same thread.
- [ ] Read-only tools still autorun (no gate).
- [ ] You can name the two pause mechanisms from memory.

## Pitfalls

- **Gating every tool** makes the agent unusable — gate only side effects.
- **Interrupt without a checkpointer** — nothing to resume from; it's required.
- **Resuming on the wrong `thread_id`** — the interrupt is thread-scoped.

## Carries to next session

All the pieces — memory, persistence, bounded context, approval gate — exist.
Session 5 assembles them into `assistant.py`.
