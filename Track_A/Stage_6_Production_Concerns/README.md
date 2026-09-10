# Stage 6 — Production Concerns

**Stage goal:** take the Stage 5 system from "works on my machine" to a
deployed service you can trust — with structured tracing, an eval suite wired
into CI, reliability (retries, timeouts, fallbacks, circuit breakers,
idempotency), cost and latency budgets, guardrails, and a real deployment.

Seven ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Structured logging & tracing](session_1_logging_and_tracing.md) | every run is a structured, queryable trace with a request id (LangSmith / Arize Phoenix) |
| 2 | [Eval suites & CI](session_2_eval_suites_and_ci.md) | golden set + regression + LLM-judge (Ragas / TruLens), run on every change |
| 3 | [Reliability](session_3_reliability.md) | retries, timeouts, fallbacks, circuit breakers, idempotency keys |
| 4 | [Cost & latency budgets](session_4_cost_latency_budgets.md) | per-route budgets, caching, batching, p50/p95 measured |
| 5 | [Guardrails & safety](session_5_guardrails_and_safety.md) | input validation, output schema, injection defense, PII, refusals (+ NeMo Guardrails); the Guardrailed, Evaluated Chatbot |
| 6 | [Deployment](session_6_deployment.md) | the Stage 5 system deployed as a streaming API (FastAPI / LangServe, Docker, AWS/GCP/Azure); the End-to-End AI Copilot |
| 7 | [Self-hosting inference](session_7_self_hosting_inference.md) | Ollama & vLLM behind OpenAI-compatible APIs; route one step to a local model, eval-gated |

## Conventions

Python 3.10+. Adds `fastapi`/`uvicorn` (+ optional `langserve`), `structlog` (or
stdlib logging + JSON), `tenacity`, `pytest`, `docker`. Tracing via LangSmith,
Arize Phoenix, or OpenTelemetry. Eval metrics via Ragas / TruLens. Guardrails
via NeMo Guardrails. Self-hosted inference via Ollama / vLLM (session 7).
`claude-opus-5` primary; cheaper or local models where a session calls for it.
Run every session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

## Working files produced in this stage

```
Stage_6_Production_Concerns/
  code/
    obs.py            # session 1 — logging/tracing setup
    evals/            # session 2 — dataset + runner + CI config
    reliability.py    # session 3 — retry/timeout/breaker wrappers
    budgets.py        # session 4 — per-route cost/latency budgets + caching
    guards.py         # session 5 — input/output guardrails
    service.py        # session 6 — FastAPI app wrapping research.py
    dashboards/       # session 6 — what to chart + alert on
    Dockerfile        # session 6 — container image
    docker-compose.yml # session 6 — service + Qdrant + Phoenix
    local_infer.py    # session 7 — Ollama/vLLM client + a routed step
  notes.md
```

## Done with Stage 6 when

- [ ] Every request has an id and a full structured trace you can look up after
      the fact.
- [ ] An eval suite runs on every change and fails the build on a regression.
- [ ] A transient API failure is retried and succeeds; a persistent one trips a
      breaker and returns a graceful error, not a hang.
- [ ] Each route has a cost and latency budget; you can show p50/p95 latency and
      $/request from real traffic.
- [ ] Malformed input is rejected, outputs are schema-checked, and an injection
      attempt in a document doesn't hijack the agent.
- [ ] `service.py` serves the Stage 5 research assistant over a streaming
      endpoint, with dashboards and at least one alert defined.
- [ ] The service runs as a Docker image (compose brings up service + vector DB
      + tracing) — the End-to-End AI Copilot.
- [ ] One step is routed to a self-hosted model (Ollama/vLLM) and the eval suite
      still passes — or it was reverted because the number dropped.
