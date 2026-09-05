# Track A — Roadmap

Staged path from first LLM call to a production AI system that solves a complex
problem. Aligned with the learning path in `Track_A/CLAUDE.md`. Each stage ends
in something runnable.

This is a living document — alter stages, reorder, or split them as building
surfaces new needs. Track_B pull-ins are just-in-time, not prerequisites.

---

## Per-stage layout

Every stage is broken into ~45-minute sessions and run with the same 8-step
session loop. Templates live in [`_TEMPLATES/`](_TEMPLATES/):

- `_TEMPLATES/SESSION_METHOD.md` → copy into each stage as `_SESSION_METHOD.md`
  (the loop; fill the stage name + the stage's Track_B footing).
- `_TEMPLATES/session_file.md` → copy once per session.
- `_TEMPLATES/README.md` → checklist for spinning up a new stage.

**Stages 0–6 are built out** — each has a folder with `README.md`,
`_SESSION_METHOD.md`, `notes.md`, and its session files:

| Stage | Folder | Sessions |
|-------|--------|----------|
| 0 | `Stage_0_Setup_LLM_call/` | 5 |
| 1 | `Stage_1_First_Agent_No_Framework/` | 5 |
| 2 | `Stage_2_LangGraph_Basics/` | 5 |
| 3 | `Stage_3_Multi_Tool_And_Memory/` | 5 |
| 4 | `Stage_4_RAG/` | 6 |
| 5 | `Stage_5_Multi_Agent_Orchestration/` | 6 |
| 6 | `Stage_6_Production_Concerns/` | 6 |

Stage 7 (capstone) is not yet broken into sessions — build it from the templates
when you get there. `Stage_0_Setup_LLM_call/` is the reference implementation;
its session files are the most detailed.

---

## Stage 0 — Setup & first LLM call

**Goal:** environment ready, one raw API call working.

- API keys, Python env, SDK install, `.env` handling
- Messages API: system/user/assistant roles, temperature, max tokens, streaming
- Token counting, basic cost/latency awareness

**Build:** a script that sends a prompt and prints a streamed response.

---

## Stage 1 — Your first agent (no framework)

**Goal:** understand that an agent = LLM + loop + tools.

- Tool/function calling: schema definition, `tool_use` / `tool_result` cycle
- The agent loop: call -> model asks for tool -> run tool -> feed result back ->
  repeat until done
- Stop conditions, max-iteration guards, error handling in the loop
- Conversation state as a growing message list

**Build:** a CLI agent with 2-3 real tools (e.g. calculator, file reader, web
fetch) that chains tool calls to answer a multi-step question.

---

## Stage 2 — LangGraph basics

**Goal:** move the hand-rolled loop into a graph.

- Nodes, edges, conditional edges, the `State` object
- Reducers / how state updates merge
- Single-tool graph = re-implement your Stage 1 agent
- Tracing/inspecting graph execution

**Build:** the Stage 1 agent rebuilt as a LangGraph graph; compare control flow.

---

## Stage 3 — Multi-tool + memory

**Goal:** a more capable single agent.

- Multiple tools with routing logic (model decides which)
- Short-term memory (conversation buffer) vs. persisted memory
  (checkpointer / thread state)
- Summarization to control context growth
- Human-in-the-loop interrupt (approve before a tool runs)

**Build:** a task assistant that remembers prior turns across a session and asks
for confirmation on side-effecting actions.

---

## Stage 4 — RAG

**Goal:** ground answers in your own documents.

- Chunking strategies, embeddings (black-box API at first), vector store CRUD
- Retrieval -> context injection -> generation pipeline
- Retrieval quality: top-k, metadata filtering, re-ranking
- Evaluating retrieval (is the right chunk coming back?) and answer
  faithfulness / citations

**Track_B pull-in:** if retrieval is confusing or bad ->
`Track_B/Math_stat/01_linear_algebra` (cosine similarity, embedding geometry).

**Build:** a Q&A agent over a document set that cites sources; measure hit rate
on a small eval set.

---

## Stage 5 — Multi-agent orchestration

**Goal:** split work across specialized agents.

- Supervisor / router pattern, worker sub-agents, hand-off protocols
- Shared vs. isolated state between agents; message passing
- Parallel fan-out and result aggregation
- Loop/oscillation risks, cost blow-ups, termination guarantees

**Track_B pull-in:** routing math ->
`Track_B/Math_stat/05_decision_and_orchestration_math`
(Markov chains, expected-value routing).

**Build:** a research assistant where a supervisor delegates to retriever,
analyzer, and writer sub-agents.

---

## Stage 6 — Production concerns

**Goal:** make it reliable, observable, deployable.

- Structured logging + tracing (LangSmith or equivalent), run inspection
- Eval suites: golden datasets, regression checks, LLM-as-judge, CI gating
- Retries, timeouts, fallbacks, circuit breakers, idempotency
- Cost & latency budgets, caching (prompt caching, retrieval caching),
  token optimization
- Guardrails: input validation, output schema enforcement, prompt-injection
  defense, PII handling
- Deployment: API service, streaming endpoints, concurrency, rate limiting,
  secrets, versioning

**Build:** wrap the Stage 5 system as a deployed service with dashboards, an
eval pipeline, and alerting.

---

## Stage 7 — Capstone: complex problem end-to-end

**Goal:** one system that exercises everything.

- Pick a real, multi-step problem (e.g. "given a codebase + issue tracker,
  triage and draft fixes")
- Combines RAG + multi-agent + memory + tools + human checkpoints
- Full eval harness, cost/latency SLOs, monitoring, iteration loop

**Deliverable:** documented, deployed, measured system with a written
retrospective on which Track_B concepts it forced you to learn.
