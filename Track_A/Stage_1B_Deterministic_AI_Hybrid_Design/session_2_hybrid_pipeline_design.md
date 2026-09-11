# Session 2 — Hybrid Pipeline Design (~45 min)

**Objective:** wire Session 1's deterministic scorer into the Stage 1 CLI
agent as a real fast path, so most requests never reach the model; formalize
the pattern (validate -> short-circuit -> call model -> validate output) and
measure the cost/latency actually saved.

**What you'll learn:**
- The four-stage hybrid pattern: validate -> short-circuit -> call model -> validate output
- Why the model should be the fallback, not the default
- Handling borderline/near-miss scores as a signal, not an error
- Measuring the actual $ and time a fast path saves vs. an all-model baseline

**Prerequisites:** Session 1 complete (`fast_path_rules.py`). Stage 1's CLI
agent.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 1's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The hybrid pattern: validate -> short-circuit -> call model -> validate output |
| 10–30 | Build `code/hybrid_agent.py` |
| 30–40 | Run the comparison, measure savings |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **The hybrid pattern**, four stages every request goes through:
  1. **Validate input** — reject or normalize malformed input *before* any
     expensive step (empty string, wrong type, obviously junk).
  2. **Short-circuit** — run Session 1's scorer. Above threshold, resolve the
     request deterministically and return immediately. This is the default
     path for a well-designed hybrid system, not a fallback.
  3. **Call the model** — only for what step 2 didn't confidently resolve.
  4. **Validate output** — check the model's answer against a schema or
     guardrail (does it look like a real answer, not empty/malformed/
     off-policy) before it's returned or acted on.
- **This inverts Stage 1's assumption.** Stage 1's agent loop calls the model
  on every turn by default. Here the model is the **fallback**, not the
  default — the deterministic path is what runs most of the time in a
  well-tuned system.
- **Borderline handling.** A score just under threshold isn't an error —
  it's supposed to fall through to the model. Log these "near-misses"
  separately; they're your signal for which new rules to add later.
- **Measuring the split.** For a batch of real requests, track: % routed
  deterministic vs. model, and the $ + time you spent vs. what you'd have
  spent sending everything to the model (Stage 0's `estimate_cost`, applied
  only to the requests that *actually* skipped the model).

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Anthropic docs — *Increasing reliability* / structured output validation
  patterns: <https://docs.anthropic.com/en/docs/test-and-evaluate/strengthen-guardrails>
  (skim the input/output validation framing — full guardrail depth is
  Stage 6).

**Video (pick one, ~10–15 min):**
- Search *"LLM router pattern cost optimization"* — short explainers on
  routing a fraction of traffic away from the model.

---

## Track_B link (step 3)

**Light, non-blocking.** Deciding the deterministic/model split across a
*stream* of requests (not just one input) is an expected-value question —
`Track_B/Math_stat/05_decision_and_orchestration_math` (expected cost across
a distribution). Note *"revisit in Track_B: expected-value routing"* and
continue; today's version is just counting real requests, not modeling a
distribution.

---

## Worked example — a hybrid triage handler  <!-- step 4 -->

```python
from fast_path_rules import score_refund, THRESHOLD
# ... plus your Session 1 client/model setup (Stage 0 style) ...

def validate_input(text: str) -> str | None:
    text = text.strip()
    if not text:
        return None
    return text

def validate_output(answer: str) -> bool:
    return bool(answer) and len(answer) < 2000  # not empty, not runaway

def handle(text: str) -> str:
    clean = validate_input(text)
    if clean is None:
        return "[rejected: empty input]"

    score = score_refund(clean)
    if score >= THRESHOLD:
        return "[deterministic] Refund request logged — a human will follow up."

    # fall through to the model
    answer = call_model(clean)          # your Stage 0/1 model call
    if not validate_output(answer):
        return "[rejected: model output failed validation]"
    return f"[model] {answer}"

for text in ["", "charged twice, $49.99 both times", "what's your return policy?"]:
    print(handle(text))
```

**Expected output** (model text varies):

```
[rejected: empty input]
[deterministic] Refund request logged — a human will follow up.
[model] Our return policy allows returns within 30 days of purchase...
```

Read it: the empty string never reaches the scorer or the model — rejected at
step 1. The refund message never reaches the model — resolved at step 2. Only
the genuinely open-ended question pays for a model call.

---

## Build: `code/hybrid_agent.py`  <!-- step 5 -->

Wire Session 1's scorer into a slimmed version of the Stage 1 CLI agent
following the four-stage pattern above. Run it over the same batch you used
in Session 1, plus a few new inputs. Report, for the whole run: requests
rejected at input validation, resolved deterministically, sent to the model,
and rejected at output validation — plus the $ and time saved vs. sending
every non-rejected request to the model.

Experiments:
1. **Feed it a borderline near-miss** (score just under threshold) and
   confirm it correctly falls through to the model rather than erroring.
2. **Break output validation on purpose** — temporarily set the model's
   `max_tokens` very low or inject a truncated fake response, and confirm
   `validate_output` catches it instead of returning garbage.
3. **Compute the counterfactual.** For your batch, print what it *would*
   have cost/taken if `THRESHOLD` were set to `1.1` (i.e. nothing ever
   short-circuits) — that's your baseline to compare savings against.

---

## Quick test (step 7 — answer from memory, then check)

1. Name the four stages of the hybrid pattern, in order.
2. Why does the model sit at stage 3, not stage 1?
3. What should happen to a request that scores just under the threshold —
   and why is that not a bug?
4. What does "validate output" check for, concretely?
5. What two numbers do you compare to measure what the fast path actually
   saved?

<details><summary>Answers</summary>

1. Validate input -> short-circuit (deterministic scorer) -> call model ->
   validate output.
2. Because in a well-tuned hybrid system the deterministic path should
   resolve most traffic; the model is the fallback for what's left, not the
   default for everything.
3. It falls through to the model — that's correct behavior, since the score
   didn't clear the confidence bar. It's also a useful signal: log these
   near-misses to find new rules worth adding.
4. That the model's answer isn't empty, isn't malformed, and isn't
   runaway/off-policy — a basic schema/sanity check before acting on or
   returning it.
5. What you actually spent (only the requests that reached the model) vs.
   what you would have spent sending every request to the model (the
   counterfactual baseline).

</details>

---

## Done when  <!-- step 8 -->

- [ ] `hybrid_agent.py` implements all four stages and runs end-to-end on a
      batch of real inputs.
- [ ] You've measured actual $ and time saved vs. the all-model baseline for
      that batch.
- [ ] You've deliberately broken output validation and watched it catch a
      bad response.
- [ ] You can state the four-stage pattern from memory, and why the model
      sits at stage 3.

## Pitfalls

- **Skipping input validation because "the scorer will catch it anyway."**
  It won't — an empty string or garbage input can still score arbitrarily
  under a poorly written rule. Validate first.
- **No output validation at all.** A model call can still fail, return
  empty, or hit `max_tokens` mid-answer; treat its output as untrusted until
  checked, same as any external call.
- **Silently dropping near-misses.** They're free signal for improving the
  rule set — log them, don't discard them.

## Carries to next session

Stage 1B is complete. Stage 4B (later) revisits this same
validate/short-circuit/call/validate shape when deciding whether a task
needs a classical/fine-tuned model instead of a general LLM call; Stage 6B's
FastAPI middleware turns this pattern into an actual routing layer across
deterministic, ML, and agent paths.
