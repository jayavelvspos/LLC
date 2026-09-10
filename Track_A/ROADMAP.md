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

**Stages 0–6 (incl. 5B) are built out** — each has a folder with `README.md`,
`_SESSION_METHOD.md`, `notes.md`, and its session files. **1B, 4B, 6B are
scaffolded** (README + `_SESSION_METHOD.md` + `notes.md` stub; session files
pending) — added so the roadmap satisfies the target-role goal in
[`ROLE_GOAL.md`](ROLE_GOAL.md):

| Stage | Folder | Sessions |
|-------|--------|----------|
| 0 | `Stage_0_Setup_LLM_call/` | 5 |
| 1 | `Stage_1_First_Agent_No_Framework/` | 5 |
| 1B | `Stage_1B_Deterministic_AI_Hybrid_Design/` | 2 |
| 2 | `Stage_2_LangGraph_Basics/` | 5 |
| 3 | `Stage_3_Multi_Tool_And_Memory/` | 5 |
| 4 | `Stage_4_RAG/` | 8 |
| 4B | `Stage_4B_Classical_ML_DL_FineTuning/` | 6 |
| 5 | `Stage_5_Multi_Agent_Orchestration/` | 8 |
| 5B | `Stage_5B_Orchestration_Frameworks_MCP/` | 7 |
| 6 | `Stage_6_Production_Concerns/` | 7 |
| 6B | `Stage_6B_Oracle_Middleware_Engineering/` | 5 |

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

## Stage 1B — Deterministic AI & hybrid design

**Goal:** build the instinct to reach for an LLM only when it adds measurable
value.

- Rules, regex, heuristics, lookup tables, scoring functions — where
  deterministic Python beats a model call outright (cost, latency,
  predictability, auditability)
- Deciding the boundary: classify inputs into "handle deterministically" vs
  "needs the model", using Stage 0's cost/latency numbers as the yardstick
- Hybrid pipeline design: deterministic pre/post-processing wrapped around an
  LLM call (validate → short-circuit → call model → validate output)

**Tools:** stdlib `re`, plain Python — no new dependency.

**Track_B pull-in:** none required; light connection to
`Track_B/Math_stat/05_decision_and_orchestration_math` if the routing logic
wants an expected-cost argument.

**Build:** take the Stage 1 CLI agent and add a deterministic fast path that
intercepts a class of questions (e.g. simple arithmetic, known-format lookups)
before they ever reach the model; measure the cost/latency saved.

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

- Loaders & splitters (LangChain), chunking strategies, embeddings
  (Voyage / Cohere / Jina, black-box at first), vector store CRUD
- Retrieval -> context injection -> generation pipeline
- Retrieval quality: top-k, metadata filtering, re-ranking (Cohere / Jina)
- Production vector DBs: pgvector, Qdrant (Docker, server-side filters, HNSW)
- Advanced RAG: multi-query, HyDE, RAG-fusion, hybrid dense+sparse, parent-doc
- Evaluating retrieval (is the right chunk coming back?) and answer
  faithfulness / citations

**Tools:** LangChain · pgvector · Qdrant · Cohere · Jina.

**Track_B pull-in:** if retrieval is confusing or bad ->
`Track_B/Math_stat/01_linear_algebra` (cosine similarity, embedding geometry).

**Build:** a Q&A agent over a document set that cites sources; measure hit rate
on a small eval set, then run a retrieval-strategy bake-off against it.

---

## Stage 4B — Classical ML, deep learning & fine-tuning

**Goal:** the non-LLM ML skillset — build, evaluate, and improve real models —
plus know when fine-tuning beats RAG/prompting. This is where the
`Track_B` Core ML / Deep Learning / NLP topic lists get scaffolded into real,
hands-on sessions instead of sitting as reference lists.

- Classical ML (scikit-learn): features & labels, train/test split, feature
  engineering, supervised learning (classification, regression) and
  unsupervised learning (clustering)
- Evaluation & error analysis: accuracy, precision, recall, F1, ROC-AUC,
  confusion matrix, cross-validation, overfitting/underfitting, class imbalance
- Deep learning fundamentals (PyTorch): perceptron -> neural net, forward /
  backward propagation, loss functions, optimizers, epochs/batches/learning
  rate, dropout, batch normalization
- Hugging Face `transformers`: tokenizers, pretrained pipelines for
  classification, NER, and summarization on real text
- PEFT fine-tuning (LoRA/QLoRA): fine-tune a small pretrained model on a
  narrow task; evaluate cost/quality/maintenance trade-offs vs. the Stage 4
  RAG system and vs. plain prompting on the same task

**Tools:** scikit-learn · PyTorch · Hugging Face `transformers` + `peft`.

**Track_B pull-in:** this stage *is* the pull-in point for
`Track_B/Core_ML`, `Track_B/Deep_Learning`, and `Track_B/NLP` (scaffold those
folders alongside `Math_stat/` when this stage starts, if not already done).

**Build:** a small classifier (scikit-learn) with a full eval report; a
from-scratch-feel PyTorch training loop on a toy dataset; a Hugging Face
pipeline solving a real NLP task; a LoRA-fine-tuned model compared head-to-head
against the Stage 4 RAG answer on the same questions (cost, latency, quality).

---

## Stage 5 — Multi-agent orchestration

**Goal:** split work across specialized agents.

- Supervisor / router pattern, worker sub-agents, hand-off protocols
- Shared vs. isolated state between agents; message passing
- Parallel fan-out and result aggregation
- Loop/oscillation risks, cost blow-ups, termination guarantees
- Agentic patterns catalog: prompt chaining, routing, parallelization,
  orchestrator-workers, evaluator-optimizer; ReAct / reflection / planning
- Multi-agent frameworks: CrewAI (primary), AutoGen, Agno — vs the LangGraph spine

**Tools:** LangChain · LangGraph · CrewAI · Agno · AutoGen.

**Track_B pull-in:** routing math ->
`Track_B/Math_stat/05_decision_and_orchestration_math`
(Markov chains, expected-value routing).

**Build:** a research assistant where a supervisor delegates to retriever,
analyzer, and writer sub-agents (the Tool-Calling Research Agent); plus a
Multi-Agent Content Crew in CrewAI for comparison.

---

## Stage 5B — Orchestration, frameworks & MCP

**Goal:** learn the plumbing under multi-agent systems, and connect agents to
real systems.

- LCEL & prompt templates; the `Runnable` interface
- Routing & parallelism (`RunnableBranch` / `RunnableParallel`)
- The evaluator-optimizer loop in LangGraph
- LangSmith tracing & datasets (the substrate for Stage 6 evals)
- MCP: hosts, clients, servers, transports; consuming an MCP server
- Building an MCP server (`FastMCP`) — the MCP-Powered Desktop Assistant
- Low-code orchestration: n8n & Langflow, and where visual tools fit

**Tools:** LCEL · LangGraph · LangSmith · MCP · n8n · Langflow.

**Track_B pull-in:** light / none — mostly protocol and framework engineering.

**Build:** an agent that calls tools over MCP (one server you wrote, one you
didn't) and an n8n business-automation pipeline that calls your code.

---

## Stage 6 — Production concerns

**Goal:** make it reliable, observable, deployable.

- Structured logging + tracing (LangSmith / Arize Phoenix / OTel), run inspection
- Eval suites: golden datasets, regression checks, LLM-as-judge (Ragas /
  TruLens), CI gating
- Retries, timeouts, fallbacks, circuit breakers, idempotency
- Cost & latency budgets, caching (prompt caching, retrieval caching),
  token optimization
- Guardrails: input validation, output schema enforcement, prompt-injection
  defense, PII handling — hand-rolled and via NeMo Guardrails
- Deployment: API service (FastAPI / LangServe), streaming endpoints,
  concurrency, rate limiting, secrets, versioning, Docker, AWS/GCP/Azure
- Self-hosting inference: Ollama, vLLM; hybrid routing (local vs API per step)
- MLOps for trained models (from Stage 4B): experiment tracking (MLflow),
  model registry & versioning, drift monitoring — the classical-ML counterpart
  to the LLM-side eval/observability above

**Tools:** NeMo Guardrails · Ragas · TruLens · Ollama · vLLM · Docker · MLflow.

**Build:** wrap the Stage 5 system as a deployed, containerised service with
dashboards, an eval pipeline, and alerting — the End-to-End AI Copilot.

---

## Stage 6B — Oracle DB & Python middleware engineering

**Goal:** the "intermediate server layer" role itself — a FastAPI service that
combines deterministic logic, ML/LLM calls, and Oracle-backed data, engineered
to production API standards.

- Oracle SQL for AI pipelines: writing queries, joins, extracting datasets via
  `python-oracledb`
- Performance-aware querying: indexes, execution plans, pagination, and secure
  handling of sensitive data pulled into a pipeline
- FastAPI middleware architecture: a service layer that routes a request
  through Stage 1B's deterministic path, a Stage 4B model, or a Stage 5/6
  agent, backed by Oracle data
- API engineering practices: auth/authz hooks, input validation, retries &
  timeouts, caching, structured logging, error handling — as first-class
  requirements, not afterthoughts
- Wiring this service into the Stage 6 MLOps/CI pipeline (build, test, deploy)

**Tools:** FastAPI · `python-oracledb` · Docker (continued from Stage 6).

**Track_B pull-in:** none — pure applied engineering.

**Build:** a FastAPI service with 2-3 endpoints that (a) hit Oracle for real
data, (b) short-circuit to deterministic logic where possible, (c) fall
through to an LLM/ML call otherwise — with auth, validation, retries, caching,
and logging all present and tested.

---

## Stage 7 — Capstone: complex problem end-to-end

**Goal:** one system that exercises everything — shaped to double as a
portfolio piece for the target role in [`ROLE_GOAL.md`](ROLE_GOAL.md).

- Pick a real, multi-step problem (e.g. "given a codebase + issue tracker,
  triage and draft fixes")
- Combines RAG + multi-agent + memory + tools + human checkpoints
- Uses deterministic short-circuits (Stage 1B) where they beat a model call
- Includes a classical/fine-tuned model (Stage 4B) somewhere it's a better fit
  than prompting a general model
- Exposed through the Stage 6B FastAPI middleware, backed by Oracle data
- Full eval harness, cost/latency SLOs, MLOps (experiment tracking, registry,
  drift monitoring), CI/CD, monitoring, iteration loop

**Deliverable:** documented, deployed, measured system with a written
retrospective on which Track_B concepts it forced you to learn.
