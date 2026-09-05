# Stage 2 — LangGraph Basics

**Stage goal:** move the hand-rolled loop from Stage 1 into a graph. Learn
nodes, edges, conditional edges, the `State` object, and reducers by rebuilding
the Stage 1 agent in LangGraph — then compare, so you can see exactly which
plumbing the framework takes over.

Five ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Why a graph? StateGraph & State](session_1_stategraph_and_state.md) | a 2-node linear graph runs; you can read/update `State` |
| 2 | [The LLM node & the tool node](session_2_llm_node_tool_node.md) | a model node + a `ToolNode`, tools bound to the model |
| 3 | [Conditional edges & the loop](session_3_conditional_edges_loop.md) | `should_continue` routes model→tools→model→END |
| 4 | [State & reducers](session_4_state_and_reducers.md) | `add_messages` reducer; you can explain how updates merge |
| 5 | [Tracing & the rebuild](session_5_tracing_and_rebuild.md) | Stage 1 agent, rebuilt as a graph, traced — the deliverable |

## Conventions

Python 3.10+. Install `langgraph` and `langchain-anthropic` (or `langchain-core`
+ the Anthropic integration). `claude-opus-5` by default. Run every session with
the 8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

> **LangGraph's API moves faster than the Anthropic SDK.** Treat this stage's
> code as illustrative and check the current LangGraph docs
> (<https://langchain-ai.github.io/langgraph/>) for exact imports and signatures.
> The *concepts* — nodes, edges, conditional routing, state reducers — are
> stable.

## Working files produced in this stage

```
Stage_2_LangGraph_Basics/
  code/
    linear_graph.py       # session 1
    graph_with_tools.py   # sessions 2–3
    agent_graph.py        # session 5 — the deliverable
  notes.md
```

## Done with Stage 2 when

- [ ] `agent_graph.py` reproduces the Stage 1 agent's behavior on the same test
      tasks.
- [ ] You can draw the graph (nodes + conditional edge) from memory.
- [ ] You can point at the exact code from Stage 1 that the framework now
      replaces (the `while` loop, the message-append bookkeeping, the branch).
- [ ] You can explain what a reducer does and why `add_messages` exists.
- [ ] A run is visible as a trace (LangSmith or a printed event stream).
