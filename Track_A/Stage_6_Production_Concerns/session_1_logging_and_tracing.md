# Session 1 — Structured Logging & Tracing (~45 min)

**Objective:** make every run observable after the fact — a request id, a
structured log per step, and a trace you can open and inspect.

**Prerequisites:** Stage 5 complete (`research.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Logs vs traces vs metrics; what to record per LLM step |
| 10–30 | `code/obs.py` — structured JSON logging + request-id context + tracing |
| 30–40 | Run `research.py` through it; find a run by id; read its trace |
| 40–45 | Notes |

---

## Concepts

- **Structured logs** — one JSON object per event (`ts`, `request_id`, `stage`,
  `event`, `model`, `in_tok`, `out_tok`, `latency_ms`, `error`). Greppable,
  aggregatable. Never `print`.
- **Trace** — the tree of spans for one request (supervisor → worker → model
  call), with timing and I/O. LangSmith gives this for LangGraph automatically;
  OpenTelemetry is the vendor-neutral option.
- **Request id** — generated at the entry point, attached to every log line and
  span for that request (via `contextvars` so you don't thread it manually).
- **What to log per model call:** model, prompt tokens, completion tokens,
  latency, `stop_reason`, cost, and a hash or truncated copy of the prompt (mind
  PII — Session 5).
- **Log levels:** INFO for lifecycle, WARNING for retries/degradation, ERROR for
  failures. Sample DEBUG in prod.

---

## Learning resources

**Primary (official, stable):**
- `structlog` docs — *Getting started* (JSON renderer, context vars):
  <https://www.structlog.org/>.
- LangSmith docs — *Tracing* concepts and setup:
  <https://docs.smith.langchain.com/>.
- OpenTelemetry Python docs — *Getting started* (if going vendor-neutral):
  <https://opentelemetry.io/docs/languages/python/>.

**Video (pick one, ~10–20 min):**
- Search *"structlog python structured logging tutorial"* and *"LangSmith
  tracing walkthrough"*.

---

## Track_B link (step 3)

**None.** Observability plumbing. Note "no Track_B link" and continue.

---

## Worked example — request-scoped structured logs

`code/obs.py`:

```python
import contextvars, time, uuid, structlog

request_id = contextvars.ContextVar("request_id", default="-")

structlog.configure(processors=[
    structlog.contextvars.merge_contextvars,
    structlog.processors.add_log_level,
    structlog.processors.TimeStamper(fmt="iso"),
    structlog.processors.JSONRenderer(),
])
log = structlog.get_logger()

def new_request() -> str:
    rid = uuid.uuid4().hex[:12]
    request_id.set(rid)
    structlog.contextvars.bind_contextvars(request_id=rid)
    return rid

def log_model_call(stage, model, resp, ms):
    log.info("model_call", stage=stage, model=model,
             in_tok=resp.usage.input_tokens, out_tok=resp.usage.output_tokens,
             stop=resp.stop_reason, latency_ms=ms)
```

**Expected output** (one run's lines):

```json
{"event":"request_start","request_id":"a1b2c3d4e5f6","question":"...","level":"info","timestamp":"2026-09-05T10:00:00Z"}
{"event":"model_call","request_id":"a1b2c3d4e5f6","stage":"supervisor","model":"claude-opus-5","in_tok":812,"out_tok":40,"stop":"tool_use","latency_ms":730,"level":"info",...}
{"event":"model_call","request_id":"a1b2c3d4e5f6","stage":"retriever","model":"claude-haiku-4-5","in_tok":1900,"out_tok":210,"latency_ms":540,"level":"info",...}
{"event":"request_end","request_id":"a1b2c3d4e5f6","steps":7,"cost_usd":0.14,"latency_ms":6100,"level":"info",...}
```

Read it: `grep a1b2c3d4e5f6` reconstructs the entire run; sum `cost_usd` or
`out_tok` across `request_id`s for aggregates. No trace UI required, though the
LangSmith trace shows the same as a tree.

---

## Build

- Build `obs.py`; wrap `research.py`'s entry point with `new_request()` and log
  `request_start` / `request_end`.
- Add `log_model_call` at every model call site (supervisor + workers).
- Run 5 questions. Then: pick one `request_id`, reconstruct its timeline from
  logs alone. Compute total cost per request with a one-liner over the JSONL.
- Turn on LangSmith tracing; open one trace; find the slowest span.
- Force an error in a worker → confirm it logs at ERROR with the `request_id`.

---

## Quick test (step 7 — answer from memory, then check)

1. Difference between a log, a trace, and a metric.
2. Why a request id, and how do you propagate it without passing it everywhere?
3. List five fields to log on every model call.
4. What log level for a retry? For a fallback that succeeded?
5. Why not `print`?

<details><summary>Answers</summary>

1. Log = one timestamped event. Trace = the span tree for one request. Metric =
   an aggregated number over many requests (rate, p95, error %).
2. To tie every event and span of one request together; propagate via a
   `contextvar` bound at the entry point.
3. Any five: model, input tokens, output tokens, latency, `stop_reason`, cost,
   stage/span name, error.
4. Retry → WARNING. Fallback that then succeeded → WARNING (degraded but OK).
5. `print` is unstructured, unlevelled, no context, and not routable to a log
   sink — useless for aggregation or search.

</details>

---

## Done when

- [ ] Every run emits `request_start` / `model_call` / `request_end` JSON with a
      shared `request_id`.
- [ ] You reconstructed one run's timeline from logs only.
- [ ] A LangSmith (or OTel) trace of a run is viewable.
- [ ] Errors log at ERROR with the request id.

## Pitfalls

- **Logging full prompts with PII** — hash or redact (Session 5 revisits this).
- **Unbounded log volume** — sample DEBUG, keep INFO lean.
- **Request id not set on background tasks / threads** — re-bind the contextvar
  inside workers.

## Carries to next session

You can see what happened. Session 2 measures whether it was *good* — an eval
suite wired into CI.
