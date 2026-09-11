# Session 4 — API Engineering Practices (~45 min)

**Objective:** harden Session 3's service to production API standards: auth,
real input validation, retries/timeouts on the fallback path, response
caching, structured logging, and consistent error handling — then prove
each one works by deliberately triggering its failure case.

**What you'll learn:**
- Authentication vs. authorization as request-time dependencies
- Input validation beyond types (Pydantic validators, business rules)
- Retries with exponential backoff, and why timeouts are still separate
- Caching with a TTL, and the staleness tradeoff it introduces
- Structured JSON logging with a `request_id`, and a global exception handler

**Prerequisites:** Session 3 complete (`middleware_app.py`). `pip install
tenacity`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 3's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Auth, validation, retries/timeouts, caching, logging, error handling — the six requirements |
| 10–35 | Build `code/api_hardening.py` |
| 35–45 | Break each one on purpose; notes |

---

## Concepts  <!-- step 2 -->

- **Auth (authentication) as a dependency.** An API-key check
  (`X-API-Key` header, compared against a known value) is the simplest real
  version: a `Depends(require_api_key)` that raises `HTTPException(401)` on
  a missing/wrong key, applied to every route that needs protection. Real
  systems use OAuth2/JWT; the *shape* — a dependency that runs before your
  route body and can reject the request — is identical.
- **Authz (authorization)** goes one step further than "is this caller
  known": *what* is this caller allowed to do. Even with a valid API key, a
  read-only client shouldn't be able to hit `POST /tickets/{id}/classify`
  if that's meant for an internal service only — check a role/scope claim,
  not just presence of a key.
- **Input validation beyond types.** FastAPI's type hints (Session 3) catch
  "not an integer." A Pydantic **validator** catches business rules: a
  ticket body that's empty, a category outside the known set, a string over
  some length limit — reject these with a clear 422 before they reach a
  model or an LLM call.
- **Retries with backoff.** A transient failure (a network blip, a rate
  limit) calling the fallback LLM shouldn't fail the whole request
  immediately. Retry a few times with **exponential backoff** (wait longer
  between each attempt) so you don't hammer an already-struggling
  dependency. `tenacity`'s `@retry` decorator does this in a few lines.
- **Timeouts.** Every external call (DB, model, LLM) needs an explicit
  timeout, separate from retries — retrying an already-slow call without a
  timeout just means waiting even longer before eventually giving up (or
  never giving up). Fail fast, then decide whether to retry.
- **Caching.** If the same ticket is classified twice, don't pay for the
  model/LLM call twice — cache by a hash of the input, with a **TTL** (time
  to live) so stale results eventually expire. The tradeoff: a cached
  result can go stale if the underlying ticket is edited — decide, per use
  case, whether that's acceptable or whether the cache key needs to include
  an update timestamp.
- **Structured logging.** Log JSON, not free-text sentences — every log
  line with the same fields (`request_id`, `route`, `method_used`,
  `latency_ms`, `status_code`) is queryable and aggregable, unlike a printf.
  A `request_id` generated per request and included in every log line for
  that request is what lets you trace one request's full path through logs
  later (the same idea as Stage 6's tracing, at the HTTP layer).
- **Consistent error handling.** A global exception handler
  (`@app.exception_handler(Exception)`) catches anything unhandled and
  returns the *same shaped* error JSON (`{"error": ..., "request_id": ...}`)
  instead of leaking a raw stack trace to the caller — and still logs the
  real exception server-side.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- FastAPI docs — *Security* (API key example) and *Handling Errors*:
  <https://fastapi.tiangolo.com/tutorial/security/> ·
  <https://fastapi.tiangolo.com/tutorial/handling-errors/>.
- `tenacity` docs — *Examples* (retry with exponential backoff):
  <https://tenacity.readthedocs.io/en/latest/>.

**Video (pick one, ~15 min):**
- Search *"API retry timeout exponential backoff explained"*.

---

## Track_B link (step 3)

**None.** Pure applied engineering. Note "no Track_B link" and continue.

---

## Worked example — hardening one endpoint  <!-- step 4 -->

```python
import hashlib, logging, time, uuid
from fastapi import FastAPI, HTTPException, Depends, Header, Request
from tenacity import retry, stop_after_attempt, wait_exponential

logging.basicConfig(level=logging.INFO)
log = logging.getLogger("middleware")

API_KEY = "dev-secret-key"
_cache: dict[str, tuple[str, float]] = {}
CACHE_TTL_SECONDS = 300

def require_api_key(x_api_key: str = Header(...)):
    if x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="invalid API key")

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=0.5, max=4))
def classify_with_llm_retrying(text: str) -> str:
    return classify_with_llm(text)   # from Session 3; may raise transiently

def cached_classify(text: str, fn) -> str:
    key = hashlib.sha256(text.encode()).hexdigest()
    hit = _cache.get(key)
    if hit and (time.time() - hit[1]) < CACHE_TTL_SECONDS:
        return hit[0]
    result = fn(text)
    _cache[key] = (result, time.time())
    return result

app = FastAPI()

@app.middleware("http")
async def log_requests(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start = time.perf_counter()
    response = await call_next(request)
    latency_ms = (time.perf_counter() - start) * 1000
    log.info('{"request_id": "%s", "path": "%s", "status": %d, "latency_ms": %.1f}',
              request_id, request.url.path, response.status_code, latency_ms)
    response.headers["X-Request-ID"] = request_id
    return response

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = request.headers.get("X-Request-ID", "unknown")
    log.error('{"request_id": "%s", "error": "%s"}', request_id, str(exc))
    from fastapi.responses import JSONResponse
    return JSONResponse(status_code=500, content={"error": "internal error", "request_id": request_id})

@app.post("/tickets/{ticket_id}/classify", dependencies=[Depends(require_api_key)])
def classify_ticket_hardened(ticket_id: int):
    ticket = get_ticket_by_id(get_connection(), ticket_id)
    if ticket is None:
        raise HTTPException(status_code=404, detail="ticket not found")
    if not ticket["body"].strip():
        raise HTTPException(status_code=422, detail="ticket body is empty")

    score = score_refund(ticket["body"])
    if score >= THRESHOLD:
        return {"ticket_id": ticket_id, "category": "billing", "method": "deterministic"}

    category = cached_classify(ticket["body"], classify_with_llm_retrying)
    return {"ticket_id": ticket_id, "category": category, "method": "llm"}
```

**Expected output** (a request without the header):

```
HTTP 401 {"detail": "invalid API key"}
```

**Expected output** (a valid request, second identical call within the TTL):

```
first call:  ~400ms, "method": "llm"
second call: ~2ms,   "method": "llm"   -- served from cache
```

Read it: the second identical call is orders of magnitude faster because it
never touched the model/LLM path at all — the cache did its job.

---

## Build: `code/api_hardening.py`  <!-- step 5 -->

Build the hardened endpoint above against your real Session 3 app. Add the
logging middleware and exception handler to the whole app, not just this
one route.

Experiments:
1. **Trigger every failure path deliberately:** missing API key (401), an
   empty ticket body (422), a ticket id that doesn't exist (404), and an
   unhandled exception (temporarily raise `RuntimeError` inside the route)
   — confirm each returns the right status code and a `request_id`.
2. **Force a retry.** Make `classify_with_llm` raise on its first two calls
   and succeed on the third (a simple counter). Confirm `tenacity` retries
   and the request still succeeds — check the timing shows the backoff
   delays.
3. **Prove the cache works and expires.** Call the same ticket twice quickly
   (fast, cached) then set `CACHE_TTL_SECONDS = 1`, wait two seconds, and
   call again (slow, recomputed).

---

## Quick test (step 7 — answer from memory, then check)

1. What's the difference between authentication and authorization?
2. Why do you need both a retry policy *and* a timeout — isn't one enough?
3. What's the risk a cache introduces, and what does the TTL do about it?
4. What does a `request_id` in structured logs let you do that free-text
   logs don't?
5. Why does the global exception handler return a generic error message
   instead of the real exception text to the caller?

<details><summary>Answers</summary>

1. Authentication confirms *who* the caller is (a valid API key/identity);
   authorization determines *what* that identity is allowed to do.
2. A timeout bounds how long you wait for one attempt; a retry policy
   decides whether/how many times to try again after a failure. Retrying
   without a timeout means each retry could hang indefinitely; a timeout
   without retries gives up after one transient blip that a retry would
   have recovered from.
3. A cached result can go stale if the underlying data changes after it was
   cached. The TTL bounds how long a stale result can be served before it's
   recomputed.
4. Trace every log line belonging to one specific request across the whole
   system, even across multiple services/log files — essential for
   debugging one user's specific failed request among thousands of others.
5. To avoid leaking internal details (stack traces, library names, internal
   paths) to an external caller, which is both an information-security risk
   and unhelpful noise — the real exception is still logged server-side,
   correlated by `request_id`.

</details>

---

## Done when  <!-- step 8 -->

- [ ] The classify endpoint requires a valid API key and rejects an invalid
      ticket body with the correct status codes.
- [ ] A transient LLM failure is retried with backoff and the request still
      succeeds.
- [ ] A repeated identical request is served from cache, measurably faster.
- [ ] Every request produces a structured log line with a `request_id`, and
      an unhandled exception returns a generic error while logging the real
      one.

## Pitfalls

- **Retrying a request that will never succeed** (e.g. a 401 or a malformed
  request) — only retry genuinely transient failures (timeouts, 5xx,
  connection errors), never validation/auth failures.
- **Caching without a TTL, or with one too long for the data's actual
  volatility.** Stale-forever is a real bug, not just a stale-for-a-while
  tradeoff.
- **Logging the raw request body or API key.** Structured logging still
  needs the same "don't log sensitive values" discipline as Session 2's
  database logging guidance.

## Carries to next session

This service is now correct and resilient for one instance running
locally. Session 5 containerizes it, adds a health check, and wires it into
Stage 6's CI/CD pipeline so it can actually be deployed and kept running.
