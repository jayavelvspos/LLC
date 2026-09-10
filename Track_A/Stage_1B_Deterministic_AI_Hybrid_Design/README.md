# Stage 1B — Deterministic AI & Hybrid Design

**Stage goal:** build the instinct to reach for an LLM only when it adds
measurable value. Rules, regex, heuristics, lookup tables, and scoring
functions often beat a model call on cost, latency, predictability, and
auditability — this stage is about recognizing that boundary and designing
pipelines that use both.

Sits between Stage 1 (first agent) and Stage 2 (LangGraph basics). Numbered
**1B** so Stages 2 onward don't have to renumber. Short by design — two
sessions.

Two ~45-minute sessions, in order. See [`../ROADMAP.md`](../ROADMAP.md) for
the full stage description and [`../ROLE_GOAL.md`](../ROLE_GOAL.md) for why
this stage exists.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Rules, regex, heuristics & scoring](session_1_rules_regex_heuristics_scoring.md) | catalog of deterministic techniques; decide "deterministic vs. model" for a batch of sample inputs using Stage 0's cost/latency numbers as the yardstick |
| 2 | [Hybrid pipeline design](session_2_hybrid_pipeline_design.md) | deterministic pre/post-processing wrapped around an LLM call: validate -> short-circuit -> call model -> validate output |

## Conventions

Python 3.10+, stdlib only (`re` and plain Python) — no new dependency. Run
every session with the 8-step loop in [`_SESSION_METHOD.md`](_SESSION_METHOD.md).
Keep `notes.md`.

## Working files planned for this stage

```
Stage_1B_Deterministic_AI_Hybrid_Design/
  code/
    fast_path_rules.py   # session 1 — deterministic classifiers/heuristics for a sample input set
    hybrid_agent.py       # session 2 — Stage 1 agent + deterministic fast path, with savings measured
  notes.md
```

## Done with Stage 1B when

- [ ] You can list at least 3 real classes of request that should never reach
      an LLM, and why.
- [ ] `hybrid_agent.py` intercepts one such class before it reaches the model
      and you've measured the cost/latency saved (Stage 0's `costs.py`).
- [ ] You can explain the hybrid pattern: validate -> short-circuit -> call
      model -> validate output.

## Where this connects

- **Back to Stage 0:** the cost/latency numbers from Session 5 are the
  yardstick for "is this worth a model call."
- **Back to Stage 1:** the agent loop gets a deterministic branch instead of
  routing everything through the model.
- **Forward:** every later stage (RAG, multi-agent, middleware) should ask
  the same question before adding an LLM call — Stage 6B's middleware makes
  this explicit as a routing decision.
