# Session 3 — Reliability (~45 min)

**Objective:** make the system survive flaky dependencies — retries with
backoff, timeouts, fallbacks, circuit breakers, and idempotency keys.

**What you'll learn:**
- Transient vs. persistent failures
- Retry with backoff + jitter, and timeouts
- Fallbacks and circuit breakers
- Idempotency keys

**Prerequisites:** Session 2 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Failure classes: transient vs persistent; the five tactics |
| 10–35 | `code/reliability.py` — decorators/wrappers for each tactic |
| 35–43 | Inject failures; watch each tactic engage |
| 43–45 | Notes |

---

## Concepts

- **Transient** (retry): 429, 500/502/503, connection reset, timeout.
  **Persistent** (don't retry): 400, 401, 404, schema-invalid output.
- **Retry with backoff + jitter** — exponential (`1s, 2s, 4s`) plus random
  jitter to avoid thundering herd. Cap attempts (3–5). The Anthropic SDK
  retries twice by default; tune `max_retries` and add app-level retry around
  multi-step operations.
- **Timeout** — every external call gets one. Total-operation timeout too, so a
  slow chain doesn't exceed the client's patience.
- **Fallback** — a cheaper/simpler path when the primary fails: a smaller model,
  a cached answer, a canned "try later". For Claude Opus/Fable there's a
  server-side `fallbacks` parameter that routes on refusal; app-level fallback
  covers outages.
- **Circuit breaker** — after N consecutive failures to a dependency, stop
  calling it for a cooldown and fail fast; probe with one request after the
  cooldown. Prevents pile-ups.
- **Idempotency key** — client sends a unique key per logical request; the
  server dedupes retries so a double-submit doesn't run the agent (and bill)
  twice.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Errors* (status codes, which are retryable) and
  *Handling stop reasons*: <https://docs.anthropic.com/en/api/errors>.
- `tenacity` docs — retry, wait strategies, `retry_if_exception_type`:
  <https://tenacity.readthedocs.io/>.
- AWS Builders' Library — *Timeouts, retries and backoff with jitter* (vendor-
  neutral, canonical): search that title.
- Martin Fowler — *CircuitBreaker*.

**Video (pick one, ~10–20 min):**
- Search *"exponential backoff jitter circuit breaker explained"*.

---

## Track_B link (step 3)

**Non-blocking.** Retry counts and breaker thresholds are expected-cost tuning
(`05_decision_and_orchestration_math`): each retry costs latency and money for a
probability of success. Note *"revisit in Track_B: expected value of a retry"*
and continue.

---

## Worked example — the tactics as wrappers

`code/reliability.py` (core):

```python
import random, time, functools
from anthropic import APIStatusError, APIConnectionError, RateLimitError

RETRYABLE = (RateLimitError, APIConnectionError)

def with_retry(attempts=4, base=1.0):
    def deco(fn):
        @functools.wraps(fn)
        def wrap(*a, **k):
            for i in range(attempts):
                try:
                    return fn(*a, **k)
                except RETRYABLE as e:
                    if i == attempts - 1: raise
                    time.sleep(base * 2**i + random.random())
                except APIStatusError as e:
                    if e.status_code >= 500 and i < attempts - 1:
                        time.sleep(base * 2**i + random.random()); continue
                    raise                       # 4xx: don't retry
        return wrap
    return deco

class Breaker:
    def __init__(self, fails=5, cooldown=30):
        self.fails = fails; self.cooldown = cooldown
        self.count = 0; self.open_until = 0
    def call(self, fn, *a, **k):
        if time.time() < self.open_until:
            raise RuntimeError("circuit open")
        try:
            r = fn(*a, **k); self.count = 0; return r
        except Exception:
            self.count += 1
            if self.count >= self.fails:
                self.open_until = time.time() + self.cooldown
            raise
```

**Expected output** (429s injected, then a hard outage):

```
WARNING retry stage=retriever attempt=1 after=1.4s reason=RateLimitError
WARNING retry stage=retriever attempt=2 after=2.7s reason=RateLimitError
INFO    ok     stage=retriever attempt=3
...
ERROR   circuit open dependency=anthropic cooldown=30s
INFO    fallback stage=writer model=claude-haiku-4-5 reason="primary unavailable"
```

Read it: transient 429s were absorbed by backoff; a sustained outage tripped the
breaker (fail fast, no pile-up) and the writer fell back to a cheaper model
rather than erroring the whole request.

---

## Build

- Build `reliability.py` with `with_retry`, a `timeout` wrapper, `Breaker`, and
  a `with_fallback(primary, backup)` helper.
- Apply them to every model call in `research.py`.
- Inject failures with a test double: raise `RateLimitError` twice then succeed;
  raise `APIStatusError(400)` (must NOT retry); hang 60s (timeout fires); 6
  straight failures (breaker opens).
- Add an idempotency-key check to the entry point (dict of seen keys → cached
  result). Submit the same key twice → second returns cached, agent doesn't
  re-run.

---

## Quick test (step 7 — answer from memory, then check)

1. Which HTTP statuses do you retry, which do you not?
2. Why add jitter to backoff?
3. What does a circuit breaker prevent, and how does it recover?
4. Difference between a retry and a fallback.
5. What does an idempotency key protect against?

<details><summary>Answers</summary>

1. Retry: 429, 500/502/503, connection errors, timeouts. Don't retry: 400, 401,
   403, 404, and schema-invalid outputs.
2. To desynchronize many clients retrying at once (avoid a thundering-herd
   spike that re-triggers the failure).
3. Pile-ups of calls to a dead dependency; after N consecutive failures it
   "opens" (fails fast) for a cooldown, then probes with one request.
4. Retry = same call again, hoping it's transient. Fallback = a different,
   usually cheaper/simpler path when the primary keeps failing.
5. Duplicate execution from client retries / double-submits — the agent runs
   (and bills) once per logical request.

</details>

---

## Done when

- [ ] Retry, timeout, breaker, fallback, and idempotency all demonstrated with
      injected failures.
- [ ] A 400 is NOT retried; a 429 is.
- [ ] A duplicate idempotency key returns the cached result without re-running.
- [ ] You can classify retryable vs not from memory.

## Pitfalls

- **Retrying 4xx** — wastes time/money on a request that will never succeed.
- **Retry without a cap** — turns a blip into an outage amplifier.
- **Breaker with no probe** — stays open forever after one bad minute.
- **Idempotency cache that never expires** — bound it (TTL/size).

## Carries to next session

The system stays up. Session 4 keeps it affordable and fast — budgets, caching,
percentiles.
