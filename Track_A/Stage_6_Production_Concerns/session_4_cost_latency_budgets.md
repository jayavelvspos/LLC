# Session 4 — Cost & Latency Budgets (~45 min)

**Objective:** put a cost and latency budget on each route, cut spend with
caching and batching, and measure p50/p95 latency and $/request from real
traffic.

**Prerequisites:** Session 3 complete. Stage 0 Session 5 (cost math).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Budgets per route; the free wins before the trade-offs |
| 10–30 | `code/budgets.py` — per-route budget + prompt caching + batch path |
| 30–40 | Replay traffic; compute p50/p95 latency and $/request before/after |
| 40–45 | Notes |

---

## Concepts

- **Budget per route** — a chat route might allow $0.02 / 3s; a research route
  $0.50 / 60s. Enforce with the guards from Stage 5 Session 5 plus the API's
  advisory `task_budget`.
- **Free wins first** (no quality cost):
  - **Prompt caching** — mark the stable prefix (system prompt, tool list,
    retrieved corpus context) with `cache_control`; repeated calls read it at a
    fraction of the price. Verify via `usage.cache_read_input_tokens`.
  - **Input hygiene** — don't resend huge histories (Stage 3 summarization);
    trim retrieved context to what's cited.
  - **Output hygiene** — cap `max_tokens` sanely; ask for terse formats.
  - **Batch API** — for non-interactive bulk work (evals, backfills): ~50%
    cheaper, async.
- **Then trade-offs** — lower `effort`, a smaller model on sub-tasks, fewer
  retrieval chunks. Measure quality with Session 2's eval before keeping.
- **Percentiles** — report p50/p95/p99 latency, not the mean (LLM latency is
  long-tailed). $/request as mean and p95.
- **Judge cost per completed task**, not per call — a cheaper call that needs
  more turns isn't cheaper.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — the `claude-api` skill's **`cost-optimize`** guide (lever order,
  measured expectations). In Claude Code: `/claude-api cost-optimize`.
- Anthropic docs — *Prompt caching* (breakpoints, what invalidates, verifying):
  <https://docs.anthropic.com/en/docs/build-with-claude/prompt-caching>.
- Anthropic docs — *Message Batches* (50% cost, async):
  <https://docs.anthropic.com/en/docs/build-with-claude/batch-processing>.

**Video (pick one, ~10–20 min):**
- Search *"prompt caching Anthropic explained"* and *"p50 p95 p99 latency
  explained"*.

---

## Track_B link (step 3)

**Non-blocking but this is the moment it pays off.** Percentiles, long-tailed
distributions, and $/request as an expectation are `Track_B/Math_stat`
probability. If "why report p95 not mean" isn't obvious, **switch** 20–30 min to
distributions & percentiles, then return. Otherwise note the revisit.

---

## Worked example — caching + budget + percentiles

```python
# 1. cache the stable prefix on every model call
resp = client.messages.create(
    model="claude-opus-5", max_tokens=800,
    system=[{"type": "text", "text": BIG_STABLE_SYSTEM_PROMPT,
             "cache_control": {"type": "ephemeral"}}],
    messages=[...])
assert resp.usage.cache_read_input_tokens > 0   # after the first call

# 2. per-route budget
ROUTES = {"chat": dict(max_usd=0.02, max_s=3), "research": dict(max_usd=0.50, max_s=60)}

# 3. percentiles from the request-end logs (session 1)
import numpy as np
lat = [r["latency_ms"] for r in load_jsonl("logs.jsonl") if r["event"] == "request_end"]
print("p50", np.percentile(lat, 50), "p95", np.percentile(lat, 95), "p99", np.percentile(lat, 99))
```

**Expected output** (before/after caching + trimming, research route):

```
before:  p50 6100ms  p95 14200ms  p99 22000ms   mean $/req 0.146
after :  p50 3900ms  p95  9100ms  p99 15000ms   mean $/req 0.058
eval mean_score: 1.44 -> 1.43   (within noise - quality held)
```

Read it: caching the corpus/system prefix and trimming context roughly halved
cost and cut p95 latency ~35%, with no measurable quality drop on the eval.
That's a free win; keep it.

---

## Build

- Add `cache_control` to the stable prefix at every model call in `research.py`;
  confirm `cache_read_input_tokens > 0` on repeat calls.
- Define `ROUTES` budgets; enforce them via the Stage 5 `Budget` guard.
- Move the eval runner (Session 2) to the Batch API; note the cost drop.
- Replay ~30 logged questions; compute p50/p95/p99 latency and mean/p95
  $/request before and after your changes. Run Session 2's eval to confirm
  quality held. Put the numbers in `notes.md`.

---

## Quick test (step 7 — answer from memory, then check)

1. What's a per-route budget and how do you enforce it?
2. List three free wins (no quality cost).
3. How do you verify prompt caching is actually working?
4. Why report p95 latency instead of the mean?
5. Why measure cost per completed task, not per call?

<details><summary>Answers</summary>

1. A cost + latency ceiling for a class of request (e.g. chat $0.02/3s); enforce
   with the app budget guard plus the API's advisory `task_budget`.
2. Any three: prompt caching of the stable prefix, input hygiene (trim history/
   context), output hygiene (sane `max_tokens`, terse formats), Batch API for
   bulk work.
3. `usage.cache_read_input_tokens > 0` on repeat calls; if it's always 0, a
   silent invalidator is in the prefix.
4. LLM latency is long-tailed; the mean hides the slow requests users actually
   feel. p95/p99 describe the tail.
5. A cheaper call that needs extra turns/retries to finish the job can cost more
   end to end.

</details>

---

## Done when

- [ ] Prompt caching is on and verified for the stable prefix.
- [ ] Each route has an enforced cost + latency budget.
- [ ] You have before/after p50/p95/p99 latency and $/request from replayed
      traffic.
- [ ] The eval confirms quality held after the cost cuts.

## Pitfalls

- **A timestamp or per-request id in the cached prefix** — silently kills the
  cache; `cache_read_input_tokens` stays 0.
- **Cost cuts without an eval re-run** — you won't notice the quality you traded
  away.
- **Optimising the mean** — the tail is the user experience.

## Carries to next session

Fast and affordable. Session 5 makes it safe against bad input, bad output, and
injection.
