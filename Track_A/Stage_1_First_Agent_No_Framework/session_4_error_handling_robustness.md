# Session 4 — Error Handling & Robustness (~45 min)

**Objective:** make the loop survive the real world — tools that raise, bad
arguments from the model, slow tools — and log every step so you can debug it.

**What you'll learn:**
- Returning `tool_result` with `is_error: true` instead of crashing
- Validating tool arguments beyond what the schema catches
- Timing out a slow tool instead of letting it hang the run
- The difference between a tool error and an API error (retry vs. report)
- Structured transcript logging (JSONL) as the seed of observability

**Prerequisites:** Session 3 complete (`tools.py` + multi-tool loop).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Failure modes: tool raises, bad args, timeout, API error |
| 10–30 | Wrap tool execution: catch → `tool_result` with `is_error: true` |
| 30–40 | Add a per-tool timeout and a step transcript log |
| 40–45 | Notes |

---

## Concepts

- **A failed tool is not a crashed agent.** Catch the exception, return a
  `tool_result` with `"is_error": true` and a short message. The model reads it
  and usually recovers (retries differently, asks the user, or explains).
- **Bad arguments:** even with a schema, validate in the function. Missing key,
  wrong type, out-of-range → return `is_error: true` with what was wrong, not a
  stack trace.
- **Slow tools:** wrap calls with a timeout (`concurrent.futures` or signal);
  on timeout return `is_error: true`. Never let one tool hang the whole run.
- **API errors** (429, 5xx, network) are different from tool errors — retry
  those with backoff (most SDKs retry twice by default), don't feed them to the
  model as `tool_result`.
- **Transcript logging:** append every model turn, tool call, and tool result
  (with timings) to a structured log — JSONL is enough. This is the seed of
  Stage 6's observability.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Tool use*, "Handling errors" (`is_error`):
  <https://docs.anthropic.com/en/docs/build-with-claude/tool-use>.
- Anthropic docs — *Errors* (HTTP status codes, retries):
  <https://docs.anthropic.com/en/api/errors>.
- `anthropic` SDK README — the typed exception classes and `max_retries`:
  <https://github.com/anthropics/anthropic-sdk-python>.

**Video (pick one, ~10–20 min):**
- Search *"python tenacity retry backoff"* and *"graceful error handling LLM
  agent"*.

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue.

---

## Worked example — a tool wrapper that never crashes the loop

```python
import concurrent.futures as cf, json, time

def run_tool(name, args, timeout=10):
    fn = DISPATCH.get(name)
    if fn is None:
        return {"content": f"unknown tool {name!r}", "is_error": True}
    try:
        with cf.ThreadPoolExecutor(max_workers=1) as ex:
            out = ex.submit(lambda: fn(**args)).result(timeout=timeout)
        return {"content": str(out)[:4000], "is_error": False}
    except cf.TimeoutError:
        return {"content": f"{name} timed out after {timeout}s", "is_error": True}
    except TypeError as e:
        return {"content": f"bad arguments: {e}", "is_error": True}
    except Exception as e:
        return {"content": f"{name} failed: {type(e).__name__}: {e}", "is_error": True}

# in the loop:
for block in resp.content:
    if block.type == "tool_use":
        t0 = time.perf_counter()
        r = run_tool(block.name, block.input)
        log({"step": step, "tool": block.name, "args": block.input,
             "is_error": r["is_error"], "ms": round((time.perf_counter()-t0)*1000)})
        results.append({"type": "tool_result", "tool_use_id": block.id,
                        "content": r["content"], "is_error": r["is_error"]})
```

**Expected output** (a tool made to raise):

```
{"step": 1, "tool": "get_weather", "args": {"city": "Atlantis"}, "is_error": true, "ms": 2}
  -> model: "I couldn't get weather for Atlantis - it may not be a real city. Did you mean somewhere else?"
```

Read it: the tool raised, the wrapper turned it into `is_error: true`, the loop
continued, and the model handled it conversationally instead of the program
dying.

---

## Build

Add the wrapper to `agent_loop.py` plus a `log()` that appends JSONL to
`code/transcript.jsonl`. Then:
- Make `get_weather` raise for unknown cities → confirm graceful recovery.
- Add `time.sleep(30)` to one tool, set `timeout=3` → confirm timeout path.
- Feed the model a prompt that makes it pass a wrong type → confirm the
  `bad arguments` message comes back and the model corrects itself.
- Simulate an API 429 (temporarily set a tiny `max_retries=0` and a bad base
  URL) → note that this is a *different* failure class you retry, not a
  `tool_result`.

---

## Quick test (step 7 — answer from memory, then check)

1. A tool raises. What do you send back, and what does the model usually do?
2. How is an API error (429/5xx) handled differently from a tool error?
3. Why validate arguments inside the function if there's already a schema?
4. How do you stop one slow tool from hanging the whole run?
5. What belongs in the step transcript, and why keep it?

<details><summary>Answers</summary>

1. A `tool_result` with `"is_error": true` and a short message. The model reads
   it and recovers — retries differently, asks the user, or explains.
2. API errors are retried with backoff (SDK does 2 by default) at the transport
   level; they are never turned into a `tool_result`.
3. Schemas constrain shape but not semantics (ranges, real-world validity); the
   function is the last line of defense, and its message helps the model self-
   correct.
4. Run it with a timeout (thread/executor or signal); on timeout return
   `is_error: true`.
5. Every model turn, tool call (name + args), and result (ok/error + timing).
   It's how you debug non-deterministic runs and the seed of Stage 6 tracing.

</details>

---

## Done when

- [ ] A raising tool, a timing-out tool, and a bad-argument call are all
      handled without the process crashing.
- [ ] `code/transcript.jsonl` records every step with timings and error flags.
- [ ] You can name the difference between a tool error and an API error.

## Pitfalls

- **Catching `Exception` around the whole loop** hides which tool failed. Catch
  narrowly, inside the wrapper.
- **Leaking stack traces to the model** wastes tokens and confuses it — send a
  one-line reason.
- **Retrying tool errors forever** — the model may loop on a permanently broken
  tool. The Session 2 iteration cap is still your backstop.

## Carries to next session

The pieces exist — loop, tools, dispatch, error handling, logging. Session 5
assembles them into `agent.py`, the Stage 1 deliverable.
