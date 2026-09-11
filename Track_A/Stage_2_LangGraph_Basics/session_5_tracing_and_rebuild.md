# Session 5 — Tracing & the Rebuild (~45 min)

**Objective:** rebuild the Stage 1 CLI agent as a LangGraph graph
(`agent_graph.py`), get a trace of a run, and write down exactly what the
framework replaced.

**What you'll learn:**
- Setting up run tracing (LangSmith, or `stream_mode="debug"`)
- Rebuilding an agent as `MessagesState` + `call_model` + `ToolNode` + `tools_condition`
- Reusing Stage 1's tool functions unchanged behind the `@tool` decorator
- What the framework replaces vs. what you still own (tools, system prompt, routing intent)

**Prerequisites:** Sessions 1–4 complete; Stage 1's `agent.py` on hand.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Set up tracing (LangSmith env vars, or `stream_mode` printing) |
| 10–35 | Write `code/agent_graph.py` — same 3 tools, same tasks as Stage 1 |
| 35–43 | Run the four Stage 1 test tasks; open the trace |
| 43–45 | Write the "what the framework replaced" note |

---

## Concepts

- **Tracing:** set `LANGSMITH_TRACING=true` + `LANGSMITH_API_KEY` and every
  graph run shows up as a tree of node/model/tool spans with inputs, outputs,
  tokens, and timing. No LangSmith account? `graph.stream(..., stream_mode=
  "updates" | "debug")` prints the same information to stdout.
- **The rebuild** is small: `MessagesState` + `call_model` + `ToolNode` +
  `tools_condition` + the loop-back edge + `recursion_limit`. Reuse the *tool
  functions* from Stage 1 unchanged (wrap them with `@tool`).
- **Keep the same interface:** `run_agent(question: str) -> str` so it's a
  drop-in for the CLI and for later stages.
- **What you no longer write:** the `while` loop, `stop_reason` branching,
  `messages.append` bookkeeping, the parallel-tool-result assembly,
  the iteration counter. What you *do* still own: the tools, the system prompt,
  and the routing intent.

---

## Learning resources

**Primary (official, stable):**
- LangSmith docs — *Trace with LangGraph* (setup, reading a trace):
  <https://docs.smith.langchain.com/>.
- LangGraph docs — *Streaming* (`stream_mode` values):
  <https://langchain-ai.github.io/langgraph/concepts/streaming/>.
- LangChain Academy — *Introduction to LangGraph*, **Module 1** recap.

**Video (optional, ~10–20 min):**
- **LangChain** channel — search *"LangSmith tracing LangGraph walkthrough"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue. From **Stage 4** the Track_B link
becomes real (linear algebra for retrieval) — if you have slack, start it now.

---

## Worked example — `agent_graph.py` core

```python
from langchain_core.tools import tool
from langchain_anthropic import ChatAnthropic
from langgraph.graph import StateGraph, START, MessagesState
from langgraph.prebuilt import ToolNode, tools_condition
import stage1_tools   # reuse the plain functions from Stage 1

TOOLS = [tool(fn) for fn in (stage1_tools.get_weather,
                             stage1_tools.calculator,
                             stage1_tools.word_count)]
model = ChatAnthropic(model="claude-opus-5", max_tokens=1500).bind_tools(TOOLS)
SYSTEM = "You are a CLI assistant with weather, math, and text tools. ..."

def call_model(state: MessagesState):
    return {"messages": [model.invoke([("system", SYSTEM)] + state["messages"])]}

b = StateGraph(MessagesState)
b.add_node("model", call_model)
b.add_node("tools", ToolNode(TOOLS))
b.add_edge(START, "model")
b.add_conditional_edges("model", tools_condition)
b.add_edge("tools", "model")
graph = b.compile()

def run_agent(question: str) -> str:
    out = graph.invoke({"messages": [("user", question)]},
                       {"recursion_limit": 20})
    return out["messages"][-1].content
```

**Expected output** (task 3 from Stage 1, via `stream_mode="updates"`):

```
{'model': {'messages': [AIMessage(tool_calls=[get_weather x3])]}}
{'tools': {'messages': [ToolMessage, ToolMessage, ToolMessage]}}
{'model': {'messages': [AIMessage(content='Range is 28 C: Lagos 31, Reykjavik 3.')]}}
```

Same answer as Stage 1, ~15 lines of graph instead of a ~40-line loop.

---

## Build

Build `agent_graph.py`. Run the **exact four** Stage 1 test tasks
(single tool / two sequential / parallel+reduce / no tool fits) and confirm
matching behavior. Then:
- Open one run's trace (LangSmith or `stream_mode="debug"`); find token counts
  per model call.
- Trigger `GraphRecursionError` with a low `recursion_limit`.
- In `notes.md`, write the "what the framework replaced" list from memory, then
  diff it against Stage 1's `agent.py`.

---

## Quick test (step 7 — answer from memory, then check)

1. Two ways to get a trace of a graph run.
2. Which Stage 1 tool code do you reuse unchanged in the rebuild?
3. List three things you no longer hand-write after moving to LangGraph.
4. What do you still own after the move?
5. What's the framework's equivalent of Stage 1's `MAX_ITERATIONS`?

<details><summary>Answers</summary>

1. LangSmith tracing (env vars) or `graph.stream(..., stream_mode="updates"/
   "debug")` printed to stdout.
2. The plain tool *functions* (wrapped with `@tool`); the schemas are derived
   from their signatures/docstrings.
3. Any three: the `while` loop, `stop_reason` branching, `messages.append`
   bookkeeping, parallel tool-result assembly, the iteration counter.
4. The tools, the system prompt, the routing intent, and the state shape.
5. `recursion_limit` (raises `GraphRecursionError`).

</details>

---

## Done when

- [ ] `agent_graph.py` matches Stage 1 behavior on all four test tasks.
- [ ] You've inspected at least one full trace.
- [ ] `GraphRecursionError` demonstrated.
- [ ] The "what the framework replaced" note is written and verified against
      Stage 1 code.
- [ ] Stage 2 checklist in `README.md` is ticked.

## Pitfalls

- **Re-implementing tools** instead of importing them — the point is that tools
  are portable.
- **Losing the `str -> str` interface** — keep `run_agent` clean for Stage 3.
- **Trusting `recursion_limit`'s default silently** — set it explicitly.

## Carries to next stage

You can build and trace a graph agent. **Stage 3** adds memory (checkpointers,
threads), context-growth control (summarization), and human-in-the-loop
interrupts on top of this graph.
