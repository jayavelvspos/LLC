# Stage 5 — Multi-Agent Orchestration

**Stage goal:** split work across specialized agents coordinated by a
supervisor. Build a research assistant where a supervisor routes sub-tasks to a
retriever, an analyzer, and a writer — and understand routing, hand-offs,
parallel fan-out, and the failure modes (oscillation, non-termination, cost
blow-ups) that multi-agent systems introduce.

Six core sessions + two extensions, ~45 minutes each.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Why multi-agent? A minimal hand-off](session_1_why_multi_agent.md) | 2 agents, one hands off to the other; frameworks landscape; when it's worth it |
| 2 | [The supervisor / router](session_2_supervisor_router.md) | a supervisor node picks the next worker from structured output |
| 3 | [Worker sub-agents & hand-off](session_3_worker_subagents_handoff.md) | sub-graphs as nodes; shared vs isolated state; results returned |
| 4 | [Parallel fan-out & aggregation](session_4_parallel_fanout_aggregation.md) | run workers concurrently, reduce their outputs into one |
| 5 | [Failure modes](session_5_failure_modes.md) | oscillation, non-termination, cost blow-ups — with guards |
| 6 | [Build the research assistant](session_6_build_research_assistant.md) | `research.py` — the Stage 5 deliverable, the Tool-Calling Research Agent example |
| 7 | [Agentic patterns catalog](session_7_agentic_patterns_catalog.md) | chain / route / parallelize / orchestrator-worker / evaluator-optimizer + ReAct / reflection / planning, as reusable code |
| 8 | [Multi-agent frameworks: CrewAI, AutoGen, Agno](session_8_multiagent_frameworks.md) | the Multi-Agent Content Crew in CrewAI; head-to-head with the LangGraph supervisor |

**Sessions 7–8 are extensions.** 7 (patterns) pairs naturally right after
Session 2; 8 (frameworks) after Session 6. They're numbered last to avoid
renumbering the build.

## Conventions

Python 3.10+. Builds on Stage 2–4 (graph, memory, RAG as a tool). `claude-opus-5`
for the supervisor; consider `claude-haiku-4-5` or `claude-sonnet-5` for
high-volume workers (cost). **Frameworks:** LangGraph is the spine (sessions
1–7); session 8 adds **CrewAI** (primary), with **AutoGen** and **Agno** for
comparison. Run every session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

## Working files produced in this stage

```
Stage_5_Multi_Agent_Orchestration/
  code/
    handoff.py       # session 1
    supervisor.py    # session 2
    workers.py       # session 3 — retriever / analyzer / writer sub-agents
    fanout.py        # session 4
    guards.py        # session 5 — step caps, budgets, loop detection
    research.py      # session 6 — the deliverable
    patterns.py      # session 7 — chain / route / parallel-vote / evaluator-optimizer
    three_ways.py    # session 7 — one task, three patterns
    crew_content.py  # session 8 — the content crew in CrewAI
  notes.md
```

## Done with Stage 5 when

- [ ] `research.py "a research question"` produces a written brief assembled by
      a supervisor delegating to ≥3 workers.
- [ ] At least one stage of the work runs workers **in parallel** and reduces
      their results.
- [ ] The system cannot loop forever or blow past a cost/step budget — there are
      explicit guards, and you've seen them fire.
- [ ] You can explain routing as a decision (expected value) and hand-offs as a
      state machine — pulled from
      `Track_B/Math_stat/05_decision_and_orchestration_math` if needed.
- [ ] You can state, from your own runs, when multi-agent beat a single agent
      and when it just added cost.
- [ ] (Session 7) You can name the five workflow patterns and pick one for a
      given task, with `patterns.py` implementing them as reusable functions.
- [ ] (Session 8) You've built the content crew in CrewAI, run it sequential and
      hierarchical, and filled a LangGraph-vs-CrewAI-vs-(AutoGen/Agno) table.
