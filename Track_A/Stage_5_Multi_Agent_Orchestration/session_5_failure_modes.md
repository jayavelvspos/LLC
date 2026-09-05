# Session 5 — Failure Modes (~45 min)

**Objective:** make the multi-agent system safe — it can't oscillate forever,
can't blow past a step or cost budget, and degrades gracefully. Model the
routing as a state machine to reason about termination.

**Prerequisites:** Session 4 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The failure catalogue for multi-agent systems |
| 10–20 | **Track_B checkpoint** — can you reason about whether the loop terminates? |
| 20–40 | `code/guards.py` — step cap, cost budget, loop detection, timeouts |
| 40–45 | Notes |

---

## Concepts

- **Failure catalogue:**
  - *Oscillation* — supervisor bounces A→B→A→B without progress.
  - *Non-termination* — never emits `DONE` (bad prompt, unsatisfiable goal).
  - *Cost blow-up* — fan-out × retries × large contexts; a single run costs
    dollars.
  - *Silent degradation* — a worker fails, returns junk, others build on it.
  - *Context bloat* — shared state grows until routing itself is expensive.
- **Guards:**
  - **Hard step cap** on total supervisor turns → return best-effort result.
  - **Cost budget** — accumulate `usage` across all calls; stop at $X (the
    Anthropic API has an advisory `task_budget`; you also enforce your own).
  - **Loop detection** — if the last N routes repeat with no state delta,
    force-advance or abort.
  - **Per-worker timeout** and `is_error` handling (Stage 1 Session 4 pattern).
  - **Progress check** — each supervisor turn must change a monitored key;
    if not, count a "stall".
- **State-machine view:** routes are transitions between states
  (retrieve/analyze/write/done). `DONE` is an *absorbing* state. Ask: from any
  state, is `DONE` reachable, and is every cycle escapable? That's
  `Track_B/Math_stat/05_decision_and_orchestration_math` (Markov chains,
  absorbing states, hitting times).

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Building effective agents* ("When to use agents", guardrails) and
  the *multi-agent research system* post (their failure mitigations).
- Anthropic docs — *Task budgets* (advisory token ceiling for agentic loops):
  via the `claude-api` skill or
  <https://docs.anthropic.com/en/docs/build-with-claude/>.
- LangGraph docs — *Recursion limit*, *streaming for observability*.

**Video (pick one, ~10–20 min):**
- Search *"multi agent LLM failure modes infinite loop cost"*.

---

## Track_B link (step 3) — possible revisit point

If you can't confidently answer "will this system always reach `DONE`?" —
**switch** to `Track_B/Math_stat/05_decision_and_orchestration_math`: Markov
chains, absorbing states, expected steps to absorption. 20–30 min, then return
and use that vocabulary to justify your guards. Otherwise note the revisit and
continue.

---

## Worked example — a guarded supervisor loop

`code/guards.py` (core):

```python
class Budget:
    def __init__(self, max_steps=20, max_usd=0.50):
        self.steps = 0; self.usd = 0.0
        self.max_steps, self.max_usd = max_steps, max_usd
        self.recent = []
    def tick(self, route, usage, model):
        self.steps += 1
        self.usd += cost(model, usage.input_tokens, usage.output_tokens)  # Stage 0 S5
        self.recent = (self.recent + [route])[-4:]
        stalled = len(self.recent) == 4 and len(set(self.recent)) <= 1
        if self.steps >= self.max_steps: return "stop: step cap"
        if self.usd >= self.max_usd:     return "stop: budget"
        if stalled:                      return "stop: oscillation"
        return None

# in the supervisor node:
halt = budget.tick(route, resp.usage, MODEL)
if halt:
    return {"route": "DONE", "log": [f"[guard] {halt}; returning best effort"]}
```

**Expected output** (a deliberately unsatisfiable question):

```
-> retriever ... -> analyzer ... -> retriever ... -> analyzer ...
[guard] stop: oscillation; returning best effort
draft: "Based on available material, a partial answer: ..."
run cost: $0.11, 8 steps
```

Read it: without the guard this run never ends; the loop detector caught the
retriever↔analyzer bounce and returned a partial answer at a bounded cost.

---

## Build

- Add `Budget` to your supervisor graph. Set `max_steps=6`, `max_usd=0.05`.
- Craft three bad inputs: (a) unanswerable question → expect budget/step stop;
  (b) a prompt that makes the supervisor never say `DONE` → step cap;
  (c) an A↔B route → loop detector.
- Add a per-worker timeout; make one worker `sleep` → confirm it's caught and
  the run continues.
- Log total `usd` and `steps` for every run from now on.

---

## Quick test (step 7 — answer from memory, then check)

1. List four multi-agent failure modes.
2. What are the four guards, and what does each bound?
3. How does loop detection work in the example?
4. In state-machine terms, what property must `DONE` have and what must every
   cycle have?
5. Difference between the API's `task_budget` and your own budget guard?

<details><summary>Answers</summary>

1. Any four: oscillation, non-termination, cost blow-up, silent degradation,
   context bloat.
2. Step cap (total supervisor turns), cost budget (accumulated $ across all
   calls), loop detection (repeated routes with no progress), per-worker
   timeout (a stuck worker).
3. Keep the last N routes; if they're all the same (or a tight cycle) with no
   monitored-state change, declare a stall and stop.
4. `DONE` must be absorbing (reachable and terminal); every cycle must be
   escapable (a path out toward `DONE`).
5. `task_budget` is an advisory token ceiling the model paces itself against;
   your guard is a hard, enforced stop you control.

</details>

---

## Done when

- [ ] Step cap, cost budget, and loop detection all fire on crafted inputs.
- [ ] A stuck worker is caught by a timeout and the run continues.
- [ ] Every run logs total cost and step count.
- [ ] Track_B checkpoint done (switched or logged).

## Pitfalls

- **Guards that abort with nothing** — always return a best-effort result.
- **Cost tracked per worker but not summed** — the blow-up is in the total.
- **Loop detector too aggressive** — legitimate repeated `retriever` calls (with
  progress) shouldn't trip it; check for state delta, not just route repetition.

## Carries to next session

The system is safe. Session 6 assembles the guarded supervisor + real workers +
fan-out into `research.py`.
