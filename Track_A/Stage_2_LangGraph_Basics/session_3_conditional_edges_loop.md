# Session 3 — Conditional Edges & the Loop (~45 min)

**Objective:** add the conditional edge that routes model → tools → model → …
→ END. This *is* the Stage 1 `while` loop, expressed as a graph.

**Prerequisites:** Session 2 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | `add_conditional_edges`; a router function returning a node name |
| 10–30 | Wire `model → (tools | END)` and `tools → model`; run a 2-step task |
| 30–40 | Recursion limit; compare to Stage 1's `MAX_ITERATIONS` |
| 40–45 | Notes |

---

## Concepts

- **Conditional edge:** `builder.add_conditional_edges("model", route, {...})`.
  `route(state)` returns a key; the mapping sends flow to that node.
- The router is one line: *if the last `AIMessage` has `tool_calls` → `"tools"`,
  else → `END`*. LangGraph ships this as `tools_condition`.
- `builder.add_edge("tools", "model")` closes the loop — after tools run, go
  back to the model.
- **Termination:** the model stops emitting `tool_calls` → route to `END`. The
  backstop is `graph.invoke(state, {"recursion_limit": N})` — the framework's
  version of your Stage 1 iteration cap. Hitting it raises
  `GraphRecursionError`.
- You have now rebuilt Stage 1. The `while`, the `if stop_reason`, the
  append-bookkeeping — all replaced by two edges and a router.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 1** ("Agent") and
  the `tools_condition` how-to:
  <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Conditional edges* and *Recursion limit*:
  <https://langchain-ai.github.io/langgraph/concepts/low_level/#edges>.

**Video (pick one, ~10–20 min):**
- **LangChain** channel — search *"LangGraph conditional edges agent loop"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — the loop as two edges

```python
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition

builder = StateGraph(MessagesState)
builder.add_node("model", call_model)          # from session 2
builder.add_node("tools", ToolNode(TOOLS))
builder.add_edge(START, "model")
builder.add_conditional_edges("model", tools_condition)   # -> "tools" or END
builder.add_edge("tools", "model")             # loop back
graph = builder.compile()

for chunk in graph.stream({"messages": [("user",
        "Compare the weather in Paris and Oslo.")]}, stream_mode="updates"):
    print(chunk)
```

**Expected output** (shape):

```
{'model': {'messages': [AIMessage(tool_calls=[get_weather x2])]}}
{'tools': {'messages': [ToolMessage('14 C'), ToolMessage('3 C')]}}
{'model': {'messages': [AIMessage(content='Paris is 14 C, Oslo 3 C - an 11 degree gap.')]}}
```

Read it: `model` asked for tools → router sent flow to `tools` → edge looped
back to `model` → this time no `tool_calls`, so the router sent it to `END`.
Identical behavior to Stage 1's loop, zero `while`.

---

## Build

Rebuild the graph with `tools_condition`. Then:
- Write your **own** `route(state)` instead of `tools_condition` (return
  `"tools"` / `END`) — prove it's one `if`.
- Set `{"recursion_limit": 4}` and give a task needing more steps → catch
  `GraphRecursionError`. Map this to Stage 1's `MAX_ITERATIONS`.
- `graph.get_graph().draw_mermaid()` → paste into `notes.md`; annotate which
  edge is the loop.

---

## Quick test (step 7 — answer from memory, then check)

1. What does a router function return, and how is it wired?
2. In words, what is the routing condition for a tool-using agent?
3. Which edge makes it a loop rather than a line?
4. How does a LangGraph agent terminate normally? What's the backstop?
5. Which specific pieces of Stage 1 code does this session replace?

<details><summary>Answers</summary>

1. A key (usually a node name or `END`); wired via
   `add_conditional_edges(source, router, mapping)`.
2. If the last `AIMessage` has `tool_calls` → go to `tools`; otherwise → `END`.
3. `add_edge("tools", "model")` — the back-edge from the tool node to the model
   node.
4. The model stops emitting `tool_calls`, so the router routes to `END`. The
   backstop is `recursion_limit`, which raises `GraphRecursionError`.
5. The `while` loop, the `if resp.stop_reason != "tool_use"` branch, and the
   manual message-append bookkeeping.

</details>

---

## Done when

- [ ] The graph loops model↔tools and ends on a no-tool turn.
- [ ] You wrote your own router and it behaves like `tools_condition`.
- [ ] You triggered and caught `GraphRecursionError`.
- [ ] You can name the loop-forming edge from memory.

## Pitfalls

- **Edge from `tools` to `END`** instead of back to `model` — the model never
  sees the tool results (the Session 2 bug).
- **No `recursion_limit`** — default is 25, but rely on it consciously, not
  accidentally.
- **Router reads the wrong message** — it must inspect the *last* message.

## Carries to next session

The loop works. Session 4 opens up the `messages` key: what `add_messages`
actually does, and how state updates merge in general.
