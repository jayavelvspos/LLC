# Session 2 — The LLM Node & the Tool Node (~45 min)

**Objective:** make one node call the model (with tools bound) and another
execute the tools it asks for.

**What you'll learn:**
- `MessagesState` and the `add_messages` reducer
- `ChatAnthropic` and `bind_tools` for a model that can emit `tool_calls`
- Writing a model node vs. a tool node (and `ToolNode` from prebuilt)
- The `@tool` decorator: docstring + type hints become the schema

**Prerequisites:** Session 1 complete (`linear_graph.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | `MessagesState`; chat model wrappers; `bind_tools` |
| 10–25 | The model node: call the LLM, return `{"messages": [ai_msg]}` |
| 25–40 | The tool node: `ToolNode` from prebuilt, or hand-written |
| 40–45 | Notes |

---

## Concepts

- LangGraph ships `MessagesState` — a `State` with a single `messages` key that
  uses the `add_messages` reducer (Session 4). Nodes return
  `{"messages": [new_message]}` and the list grows automatically.
- A **chat model** wrapper (e.g. `ChatAnthropic(model="claude-opus-5")`) gives
  `.invoke(messages) -> AIMessage`. `model.bind_tools(tools)` attaches tool
  schemas so the model can emit `tool_calls`.
- **Model node:** `def call_model(state): return {"messages":
  [model_with_tools.invoke(state["messages"])]}`.
- **Tool node:** takes the last `AIMessage`, runs each `tool_call`, returns
  `{"messages": [ToolMessage(...), ...]}`. `langgraph.prebuilt.ToolNode(tools)`
  does this for you; writing it once by hand is worth it to see it's the same
  dispatch table from Stage 1 Session 3.
- Tools here are plain Python functions wrapped with LangChain's `@tool`
  decorator (name + docstring + type hints become the schema).

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 1–2** (agent with a
  tool): <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Use the prebuilt ToolNode* and *Chat models / tools*:
  <https://langchain-ai.github.io/langgraph/how-tos/tool-calling/>.
- `langchain-anthropic` docs — `ChatAnthropic`, `bind_tools`.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph ToolNode tool calling"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — model node + tool node (not yet looped)

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END, MessagesState
from langgraph.prebuilt import ToolNode

@tool
def get_weather(city: str) -> str:
    """Current temperature for a city, in Celsius."""
    return f"{ {'Paris': 14, 'Oslo': 3}.get(city, 20) } C"

model = ChatAnthropic(model="claude-opus-5", max_tokens=1024).bind_tools([get_weather])

def call_model(state: MessagesState):
    return {"messages": [model.invoke(state["messages"])]}

builder = StateGraph(MessagesState)
builder.add_node("model", call_model)
builder.add_node("tools", ToolNode([get_weather]))
builder.add_edge(START, "model")
builder.add_edge("model", "tools")     # naive: always go to tools
builder.add_edge("tools", END)
graph = builder.compile()

out = graph.invoke({"messages": [("user", "Weather in Oslo?")]})
for m in out["messages"]:
    print(type(m).__name__, "-", getattr(m, "content", ""))
```

**Expected output** (shape):

```
HumanMessage - Weather in Oslo?
AIMessage -                       <- empty content, has .tool_calls
ToolMessage - 3 C
```

Read it: the model node produced an `AIMessage` with `tool_calls` (not text);
the tool node ran `get_weather` and appended a `ToolMessage`. The graph ends
there — it never sends the result *back* to the model. That missing edge is
Session 3.

---

## Build

Build the two-node graph. Then:
- Ask something needing **no** tool (*"Say hi"*) → the `model→tools` edge still
  fires and `ToolNode` gets an `AIMessage` with no `tool_calls`. Observe what it
  does. This is why you need a *conditional* edge (Session 3).
- Add a second `@tool`; confirm both bind.
- Print `out["messages"][1].tool_calls` and compare its shape to Stage 1's raw
  `tool_use` block.

---

## Quick test (step 7 — answer from memory, then check)

1. What is `MessagesState` and what's special about its `messages` key?
2. What does `model.bind_tools(tools)` do?
3. What does the model node return?
4. What does `ToolNode` consume and produce?
5. What's still missing after this session's graph?

<details><summary>Answers</summary>

1. A prebuilt `State` with one `messages` key that uses the `add_messages`
   reducer, so returned messages append instead of overwrite.
2. Attaches the tool JSON schemas to the model so it can emit `tool_calls`.
3. `{"messages": [AIMessage]}` — the model's reply, which may carry
   `tool_calls`.
4. Consumes the last `AIMessage`'s `tool_calls`; produces
   `{"messages": [ToolMessage, ...]}`.
5. The edge back from `tools` to `model`, and a condition to skip `tools` when
   there are no `tool_calls` — i.e. the loop (Session 3).

</details>

---

## Done when

- [ ] The model node and tool node both run; you can print the message list.
- [ ] You've seen an `AIMessage` with `tool_calls` and a resulting `ToolMessage`.
- [ ] You've seen the naive `model→tools` edge misbehave on a no-tool prompt.
- [ ] You can compare `.tool_calls` to Stage 1's `tool_use` block.

## Pitfalls

- **Forgetting `.bind_tools`** → the model never emits `tool_calls`, the tool
  node gets nothing.
- **Returning the message, not `{"messages": [msg]}`** → reducer error.
- **Assuming `AIMessage.content` has the answer** when there are `tool_calls` —
  content is often empty in that case.

## Carries to next session

Two nodes exist but the graph is linear and dumb. Session 3 adds the conditional
edge that turns it into the Stage 1 loop.
