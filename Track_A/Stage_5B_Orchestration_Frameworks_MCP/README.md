# Stage 5B — Orchestration, Frameworks & MCP

**Stage goal:** learn the plumbing that sits *under* multi-agent systems —
composable chains (LCEL), routing and parallelism, the evaluator–optimizer loop,
trace-level observability with LangSmith — and connect agents to real systems
with **MCP** (Model Context Protocol). Ends with agents that call real tools
over MCP and a low-code automation pipeline.

Sits between Stage 5 (multi-agent orchestration) and Stage 6 (production).
Numbered **5B** so Stages 6–7 don't have to renumber.

Seven ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [LCEL & prompt templates](session_1_lcel_and_templates.md) | build chains with `|`; `ChatPromptTemplate`, output parsers, `.batch` / `.stream` |
| 2 | [Routing & parallelism](session_2_routing_and_parallelism.md) | `RunnableBranch` / `RunnableParallel` / `RunnableLambda`; fan-out then fan-in |
| 3 | [Evaluator–optimizer loop](session_3_evaluator_optimizer.md) | generator + critic in LangGraph; converges on checkable criteria or a budget |
| 4 | [LangSmith tracing & datasets](session_4_langsmith_tracing.md) | every run traced; a dataset + an eval that runs on change |
| 5 | [MCP I — hosts, servers, transports](session_5_mcp_hosts_and_servers.md) | connect Claude to an existing MCP server; call its tools |
| 6 | [MCP II — build a server](session_6_mcp_build_a_server.md) | your own MCP server; the MCP-Powered Desktop Assistant example |
| 7 | [Low-code orchestration: n8n & Langflow](session_7_low_code_n8n_langflow.md) | an n8n business-automation pipeline; when visual tools fit and when they don't |

## Conventions

Python 3.10+. Adds `langchain`, `langchain-anthropic`, `langgraph`, `langsmith`,
and the **MCP** Python SDK (`mcp`). `claude-opus-5` primary; `claude-haiku-4-5`
for cheap sub-steps. n8n and Langflow run locally via Docker. Run every session
with the 8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep
`notes.md`.

## Working files produced in this stage

```
Stage_5B_Orchestration_Frameworks_MCP/
  code/
    lcel_chain.py       # session 1 — a typed prompt→model→parser chain
    routing.py          # session 2 — branch + parallel + merge
    eval_optimizer.py   # session 3 — generator/critic graph
    traced_run.py       # session 4 — @traceable + a LangSmith dataset eval
    mcp_client.py        # session 5 — connect to an MCP server, list + call tools
    mcp_server.py        # session 6 — your MCP server (files + shell + notes tools)
    desktop_assistant.py # session 6 — Claude + mcp_server.py = the assistant
    n8n_flow.json        # session 7 — exported n8n workflow
  notes.md
```

## Done with Stage 5B when

- [ ] `lcel_chain.py` runs a `prompt | model | parser` chain and its `.batch`
      form; you can explain what `|` builds.
- [ ] `routing.py` routes an input to one of ≥3 branches **and** fans a task out
      to parallel sub-chains, then merges the results.
- [ ] `eval_optimizer.py` improves an output across rounds against explicit
      criteria and stops on pass or budget.
- [ ] Every run in this stage shows up as a structured trace in LangSmith, and
      an eval runs against a saved dataset.
- [ ] Claude calls tools from a **running MCP server** you did not write
      (session 5) and from one you **did** write (session 6).
- [ ] An n8n workflow does a real multi-step automation, and you can say where a
      visual tool beats code and where it doesn't.

## Where this connects

- **Back to Stage 5:** LCEL routing/parallelism are the primitives under the
  supervisor and fan-out you hand-built; MCP is how those workers reach real
  tools instead of mocked ones.
- **Forward to Stage 6:** LangSmith tracing and the evaluator–optimizer loop are
  the backbone of Stage 6's eval suite, CI gating, and cost/latency budgets.
