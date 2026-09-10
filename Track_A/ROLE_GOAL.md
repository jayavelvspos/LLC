# Target role — what Track_A is composed to produce

Set 2026-09-10. Every stage in [`ROADMAP.md`](ROADMAP.md) is chosen so that,
completed end-to-end, it satisfies this role profile. Revisit this file if the
target role changes — stages should follow it, not the other way round.

## Role: AI/ML Engineer (Mid-Career) — NLP / GenAI (RAG) / MLOps + Oracle + Python Middleware

- **NLP / GenAI delivery** — classification, extraction, summarization,
  semantic search, conversational experiences; RAG end-to-end (ingestion,
  chunking, embeddings, indexing, retrieval, reranking, grounding, citations,
  feedback loops); LLM orchestration (prompting, structured outputs, tool
  calling, memory, guardrails); PEFT fine-tuning and its trade-offs vs.
  RAG/prompting.
- **Deterministic / cost-optimized AI** — rules, validations, heuristics,
  templates, regex, scoring where they beat a model call; use LLMs only where
  they add measurable value.
- **Python middleware / API engineering** — FastAPI services layering
  deterministic + ML/LLM logic, external LLM calls, and DB/enterprise
  integration; auth/authz hooks, input validation, retries/timeouts, caching,
  logging, error handling.
- **Oracle DB integration** — SQL, joins, dataset extraction,
  performance-aware querying, secure handling of sensitive data.
- **ML / deep learning** — supervised/unsupervised models, metrics,
  experiments, error analysis; PyTorch/TensorFlow for text and multimodal.
- **MLOps / LLMOps** — reproducible training/deploy workflows, experiment
  tracking, model registry, versioning, CI/CD, deployment as APIs/batch,
  drift/quality/latency/cost monitoring.

## Mapping to Track_A (kept in sync — update when stages change)

| Role area | Stage(s) |
|---|---|
| RAG end-to-end | Stage 4 |
| LLM orchestration (prompting, tools, memory, guardrails) | Stages 1, 3, 5B, 6 |
| Multi-agent orchestration | Stages 5, 5B |
| Deterministic / cost-optimized AI, hybrid design | **Stage 1B** |
| Classical ML, deep learning, Hugging Face, PEFT fine-tuning | **Stage 4B** |
| Eval suites, CI gating, observability, cost/latency, deploy basics | Stage 6 |
| MLOps for trained models (tracking, registry, drift) | Stage 6 (extended) |
| Oracle DB + Python middleware (FastAPI, API engineering) | **Stage 6B** |
| Capstone exercising all of the above together | Stage 7 |

Stages in **bold** were added 2026-09-10 specifically to close gaps against
this role; they were not part of the original Track_A path. See
[[track-a-required-coverage]] (memory) for the 2026-09-07 rewrite that added
Stage 5B and expanded Stages 4-6 for tooling breadth — this role-goal pass is
the second layer on top of that.

## Not yet decided

- Whether TensorFlow gets any hands-on time (Stage 4B currently plans PyTorch
  only, since the JD says "PyTorch/TensorFlow" — either satisfies it).
- Whether Stage 4B's classical-ML session needs its own eval dataset or reuses
  a slice of the Stage 4 RAG corpus.
