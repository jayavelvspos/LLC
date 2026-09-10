# Stage 6B — Oracle DB & Python Middleware Engineering

**Stage goal:** the "intermediate server layer" role itself — a FastAPI
service that combines deterministic logic, ML/LLM calls, and Oracle-backed
data, engineered to production API standards (auth, validation, retries,
caching, logging).

Sits between Stage 6 (production concerns) and Stage 7 (capstone). Numbered
**6B** so Stage 7 doesn't have to renumber.

*Session files not yet written — this is the ROADMAP-level skeleton. See
[`../ROADMAP.md`](../ROADMAP.md) for the full stage description and
[`../ROLE_GOAL.md`](../ROLE_GOAL.md) for why this stage exists.*

| # | Session | Outcome |
|---|---------|---------|
| 1 | Oracle SQL for AI pipelines | queries, joins, and dataset extraction via `python-oracledb` against a local/test Oracle instance |
| 2 | Performance-aware querying | indexes, execution plans, pagination; secure handling of sensitive data pulled into a pipeline |
| 3 | FastAPI middleware architecture | a service layer routing a request through the Stage 1B deterministic path, a Stage 4B model, or a Stage 5/6 agent, backed by Oracle data |
| 4 | API engineering practices | auth/authz hooks, input validation, retries & timeouts, caching, structured logging, error handling |
| 5 | Wiring into MLOps/CI | the FastAPI service built, tested, and deployed through the Stage 6 CI/CD pipeline |

## Conventions

Python 3.10+. Adds `fastapi`, `uvicorn`, `python-oracledb`, `pydantic`. Needs
a local or free-tier Oracle instance (Oracle XE via Docker, or Oracle Cloud
Always Free) — set this up in session 1 before writing any queries. Run every
session with the 8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md).
Keep `notes.md`.

## Working files planned for this stage

```
Stage_6B_Oracle_Middleware_Engineering/
  code/
    db.py               # session 1 — python-oracledb connection + sample queries/joins
    query_perf.py         # session 2 — indexed vs. unindexed query comparison, pagination
    middleware_app.py     # session 3 — FastAPI app: deterministic / model / agent routing
    api_hardening.py       # session 4 — auth, validation, retries, caching, logging added to middleware_app
    Dockerfile / ci config # session 5 — wired into Stage 6's CI/CD
  notes.md
```

## Done with Stage 6B when

- [ ] You've written a join query against Oracle and pulled the result into a
      Python pipeline via `python-oracledb`.
- [ ] You can explain one performance decision you made (an index, a
      pagination strategy) and why it mattered at scale.
- [ ] `middleware_app.py` has 2-3 endpoints that route between deterministic
      logic, a trained model, and an LLM/agent call, backed by real Oracle data.
- [ ] Those endpoints have auth, input validation, retries/timeouts, caching,
      and structured logging — and you tested at least one failure path
      (bad auth, invalid input, a timed-out dependency).
- [ ] The service builds and deploys through the same CI/CD pipeline as
      Stage 6.

## Where this connects

- **Back to Stage 1B:** the deterministic fast path becomes one of the
  middleware's routing branches.
- **Back to Stage 4B:** a classical/fine-tuned model becomes another branch.
- **Back to Stage 5/6:** the multi-agent system and its guardrails/eval sit
  behind the LLM branch of this same service.
- **Forward to Stage 7:** this is the exposure layer for the capstone system.
