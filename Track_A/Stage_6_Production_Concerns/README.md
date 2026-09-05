# Stage 6 — Production Concerns

**Stage goal:** take the Stage 5 system from "works on my machine" to a
deployed service you can trust — with structured tracing, an eval suite wired
into CI, reliability (retries, timeouts, fallbacks, circuit breakers,
idempotency), cost and latency budgets, guardrails, and a real deployment.

Six ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Structured logging & tracing](session_1_logging_and_tracing.md) | every run is a structured, queryable trace with a request id |
| 2 | [Eval suites & CI](session_2_eval_suites_and_ci.md) | golden set + regression + LLM-judge, run on every change |
| 3 | [Reliability](session_3_reliability.md) | retries, timeouts, fallbacks, circuit breakers, idempotency keys |
| 4 | [Cost & latency budgets](session_4_cost_latency_budgets.md) | per-route budgets, caching, batching, p50/p95 measured |
| 5 | [Guardrails & safety](session_5_guardrails_and_safety.md) | input validation, output schema, prompt-injection defense, PII, refusals |
| 6 | [Deployment](session_6_deployment.md) | the Stage 5 system deployed as a streaming API with dashboards + alerts |

## Conventions

Python 3.10+. Adds `fastapi`/`uvicorn`, `structlog` (or stdlib logging + JSON),
`tenacity`, `pytest`. Tracing via LangSmith or OpenTelemetry. `claude-opus-5`
primary; cheaper models where a session calls for it. Run every session with the
8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

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
