# Session 6 — Deployment (~45 min)

**Objective:** serve the Stage 5 research assistant as a streaming HTTP API with
concurrency control, config/secrets handling, versioning, dashboards, and at
least one alert. Stage 6 deliverable.

**Prerequisites:** Sessions 1–5 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | API shape: sync vs streaming endpoints; deployment checklist |
| 10–35 | `code/service.py` — FastAPI app wrapping `research.py` with SSE streaming |
| 35–43 | Load a few concurrent requests; define dashboards + one alert |
| 43–45 | Notes + tick the Stage 6 checklist |

---

## Concepts

- **Endpoints:**
  - `POST /research` — returns the full brief (long; use with a client timeout
    or a job id + poll).
  - `GET/POST /research/stream` — Server-Sent Events: stream progress
    (`step`, partial draft) so the client sees life immediately. Streaming also
    dodges request-timeout limits.
  - `GET /healthz` — liveness; `GET /readyz` — checks the model API and vector
    store.
- **LangServe** — if the app is an LCEL/LangGraph runnable, `add_routes(app,
  chain)` gives you `/invoke`, `/batch`, `/stream`, and `/stream_events` (SSE)
  plus a schema and a playground for free. Use it when the runnable *is* the
  API; hand-write FastAPI routes when you need custom endpoints, auth, or
  queueing logic.
- **Packaging** — a `Dockerfile` (slim Python base, `pip install -r
  requirements.txt`, non-root user, `uvicorn` entrypoint) so the same image runs
  locally and in any cloud. `docker compose` to bring up the service + Qdrant +
  Phoenix together.
- **Where it runs** — a container platform on any cloud: **AWS** (ECS/Fargate,
  App Runner, EKS), **GCP** (Cloud Run, GKE), **Azure** (Container Apps, AKS).
  For the *model* itself you can also go managed: **Amazon Bedrock** /
  **SageMaker** or **Vertex AI** host Claude behind the same SDK with an
  `AnthropicBedrock` / `AnthropicVertex` client (IAM instead of an API key) —
  useful when the rest of the stack already lives in that cloud.
- **Concurrency** — an async worker pool or a semaphore capping in-flight
  agent runs (each is expensive); a queue with backpressure (429 when full).
- **Config & secrets** — everything from env / a secrets manager, never in code;
  `ANTHROPIC_API_KEY`, model ids, budgets, corpus path. A typed settings object.
- **Versioning** — tag the deployed build; put the version + git sha in every
  response and log line; keep prompts/configs versioned so you can roll back.
- **Dashboards** — request rate, error rate, p50/p95 latency, $/request and
  $/hour, cache-hit rate, eval score trend (from CI), breaker state.
- **Alerts** — start with one that matters: error rate > X% for 5 min, or
  $/hour over budget, or p95 latency > threshold.
- **Rollout** — deploy behind a flag / canary; watch the dashboards; roll back
  on the alert.

---

## Learning resources

**Primary (official, stable):**
- FastAPI docs — *First steps*, *Concurrency and async*, *Server-Sent Events*
  (via `StreamingResponse`): <https://fastapi.tiangolo.com/>.
- LangServe docs — *`add_routes`*, streaming endpoints, the playground:
  <https://python.langchain.com/docs/langserve/>.
- Docker docs — *Python language guide* (`Dockerfile`, multi-stage, non-root):
  <https://docs.docker.com/language/python/>.
- Anthropic docs — *Streaming* (SSE event types to relay):
  <https://docs.anthropic.com/en/docs/build-with-claude/streaming>.
- Google SRE Book — *Monitoring Distributed Systems* (the four golden signals):
  <https://sre.google/sre-book/monitoring-distributed-systems/>.

**Video (pick one, ~15–30 min):**
- Search *"FastAPI streaming response SSE tutorial"* and *"four golden signals
  monitoring"*.

---

## Track_B link (step 3)

**Non-blocking.** Dashboard reading is applied statistics — rates, percentiles,
trends, and knowing when a spike is noise vs a real regression
(`Track_B/Math_stat` statistics & probability). Note the revisit and continue.

---

## Worked example — streaming endpoint

`code/service.py` (core):

```python
import asyncio, json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic_settings import BaseSettings
from research import research_stream            # generator yielding (event, data)

class Settings(BaseSettings):
    anthropic_api_key: str
    model: str = "claude-opus-5"
    max_inflight: int = 4
    version: str = "dev"

cfg = Settings()
app = FastAPI()
sem = asyncio.Semaphore(cfg.max_inflight)

@app.get("/healthz")
def healthz(): return {"ok": True, "version": cfg.version}

@app.post("/research/stream")
async def research_stream_ep(q: str):
    if sem.locked() and sem._value == 0:
        raise HTTPException(429, "at capacity, retry shortly")
    async def gen():
        async with sem:
            async for event, data in research_stream(q):
                yield f"event: {event}\ndata: {json.dumps(data)}\n\n"
    return StreamingResponse(gen(), media_type="text/event-stream")
```

**Expected output** (`curl -N` on the stream endpoint):

```
event: step
data: {"n": 1, "route": "retriever"}

event: step
data: {"n": 4, "route": "writer"}

event: done
data: {"brief": "...", "sources": [...], "cost_usd": 0.14, "version": "2026.09.05-a1b2c3d"}
```

Read it: the client sees routing progress within a second and the final brief
when ready; the semaphore caps concurrent agent runs and returns 429 past
capacity instead of melting.

---

## Build

- Build `service.py`: `/research`, `/research/stream` (SSE), `/healthz`,
  `/readyz`. Typed `Settings` from env. Version string in every response + log.
- Wire in Stage 6's earlier work: `obs.py` (request id + logs), `reliability.py`
  wrappers, `budgets.py` per-route budgets, `guards.py` input/output guards.
- Fire 10 concurrent requests with `max_inflight=4` → confirm 4 run, others
  queue or get 429; check p95 in the logs.
- Write `dashboards/README.md`: the ~7 charts to build and the 1 alert to set
  first, with thresholds.
- Write a `Dockerfile` + `docker-compose.yml` (service + Qdrant + Phoenix).
  Build the image, run it, hit the stream endpoint from outside the container.
- (Optional) add LangServe `add_routes` for the raw runnable alongside your
  custom routes; compare the two.
- **End-to-End AI Copilot:** the finished `service.py` — RAG + multi-agent +
  guardrails + evals + tracing + budgets, containerised and streaming — *is*
  the copilot. Note in `notes.md` what a real deploy would still need (auth,
  a real queue, autoscaling, a CD pipeline).
- Tick every box in the Stage 6 `README.md` checklist.

---

## Quick test (step 7 — answer from memory, then check)

1. Why offer a streaming endpoint, not just a sync one?
2. How do you cap concurrent agent runs, and what happens past the cap?
3. Where do secrets and config come from, and where do they never go?
4. Why put a version string in every response and log line?
5. Name the four golden signals and one alert worth having on day one.

<details><summary>Answers</summary>

1. The client sees progress immediately, and streaming avoids single-request
   HTTP timeout limits on long runs.
2. A semaphore / worker-pool limit on in-flight runs; past the cap, queue with
   backpressure or return 429 — never unbounded concurrency.
3. From env vars / a secrets manager into a typed settings object; never
   hard-coded in source or committed.
4. So you can tie behavior (and regressions) to a specific build and roll back
   with confidence.
5. Latency, traffic, errors, saturation. Day-one alert: error rate > X% over
   5 min (or $/hour over budget, or p95 latency over threshold).

</details>

---

## Done when

- [ ] `service.py` serves sync + streaming research endpoints plus health
      checks.
- [ ] Observability, reliability, budgets, and guards from Sessions 1–5 are all
      wired in.
- [ ] Concurrency cap enforced; over-capacity returns 429.
- [ ] `dashboards/README.md` lists the charts and the first alert with
      thresholds.
- [ ] Stage 6 `README.md` checklist fully ticked.

## Pitfalls

- **Blocking the event loop** with a sync `research()` call inside an async
  handler — run it in a threadpool/executor or make the chain async.
- **No backpressure** — unbounded concurrency turns a traffic spike into a cost
  spike and a rate-limit storm.
- **Secrets in the image / repo** — env or secrets manager only.
- **Dashboards with no alert** — nobody watches a dashboard at 3am.

## Carries forward

You now have an observable, tested, reliable, budgeted, guarded, deployed
multi-agent system. That's the whole Stage 0→6 arc. The roadmap's **Stage 7**
is the capstone: point this stack at one genuinely complex problem end to end,
with a full eval harness and a written retrospective on which Track_B topics the
build forced you to learn.
