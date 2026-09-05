# Session 1 — Why Multi-Agent? A Minimal Hand-off (~45 min)

**Objective:** build two specialized agents where one hands work to the other,
and be able to say when that's worth it versus one agent with more tools.

**Prerequisites:** Stage 4 complete (you have a RAG agent to reuse as a worker).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What a "sub-agent" is; costs multi-agent adds |
| 10–30 | `code/handoff.py` — planner agent → writer agent |
| 30–40 | Compare against a single agent with both skills as tools |
| 40–45 | Notes |

---

## Concepts

- A **sub-agent** is its own LLM + prompt + tools + (optionally) loop, invoked
  as a step by another agent. In LangGraph it's a node — often a compiled
  sub-graph.
- **Why split:** distinct skills/tools/prompts that would bloat one system
  prompt; isolation (a worker's messy context doesn't pollute others);
  parallelism; using a cheaper model for grunt work.
- **What it costs:** more LLM calls (each hand-off is ≥1 extra call), more
  places to fail, harder to trace, routing overhead, and a real risk of loops.
- **Default to one agent.** Reach for multi-agent when the task genuinely fans
  out, or when one context window can't hold the work, or when sub-tasks need
  different models/tools.
- **Hand-off** = pass a sub-task (and only the context it needs) to a worker,
  get a result back, continue.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Building effective agents* (workflows vs agents; orchestrator-
  workers; when NOT to): <https://www.anthropic.com/research/building-effective-agents>.
- Anthropic — *How we built our multi-agent research system* (engineering
  blog): <https://www.anthropic.com/engineering/multi-agent-research-system>.
- LangGraph docs — *Multi-agent* concepts:
  <https://langchain-ai.github.io/langgraph/concepts/multi_agent/>.

**Video (pick one, ~15–25 min):**
- **LangChain** channel — search *"LangGraph multi-agent supervisor"*.

---

## Track_B link (step 3)

**None yet.** Note "no Track_B link" and continue — routing math starts in
Session 2.

---

## Worked example — planner → writer

`code/handoff.py`:

```python
from anthropic import Anthropic
client = Anthropic()

def planner(topic: str) -> list[str]:
    r = client.messages.create(model="claude-opus-5", max_tokens=400,
        system="Output 3-5 terse bullet points that a short brief on the topic must cover. Bullets only.",
        messages=[{"role": "user", "content": topic}])
    return [l.strip("-• ") for l in r.content[0].text.splitlines() if l.strip()]

def writer(topic: str, outline: list[str]) -> str:
    r = client.messages.create(model="claude-opus-5", max_tokens=800,
        system="Write a tight 150-word brief that covers every outline point. No preamble.",
        messages=[{"role": "user",
                   "content": f"Topic: {topic}\nOutline:\n" + "\n".join(outline)}])
    return r.content[0].text

topic = "trade-offs of server-side vs client-side rendering"
outline = planner(topic)
print("OUTLINE:", outline)
print("\nBRIEF:\n", writer(topic, outline))
```

**Expected output** (shape):

```
OUTLINE: ['what SSR vs CSR means', 'TTFB and SEO', 'interactivity and client cost',
          'hydration', 'when to pick each']
BRIEF:
 Server-side rendering builds HTML on the server ... [~150 words covering all 5]
```

Read it: two focused prompts, each doing one job well, connected by a plain
Python hand-off (the outline). No framework needed to see the pattern.

---

## Build

- Build `handoff.py`.
- Build a **single-agent** version: one system prompt "plan then write", one
  call. Compare output quality, token cost, and latency on 3 topics.
- Add a third role (`fact_checker` that flags unsupported claims) and hand off to
  it after `writer`. Note how each hand-off adds a call.
- Write 2–3 sentences: for *this* task, did splitting help or just cost more?

---

## Quick test (step 7 — answer from memory, then check)

1. What is a sub-agent, concretely?
2. Give three reasons to split work across agents.
3. Give three costs multi-agent adds.
4. What's the default, and when do you deviate?
5. What does a "hand-off" pass, and what should it *not* pass?

<details><summary>Answers</summary>

1. Its own LLM + prompt + tools (+ maybe loop), invoked as a step by another
   agent — a node / sub-graph in LangGraph.
2. Any three: distinct skills/tools/prompts, context isolation, parallelism,
   cheaper model for grunt work, context-window limits.
3. Any three: extra LLM calls per hand-off, more failure points, harder
   tracing, routing overhead, loop risk.
4. One agent by default; deviate when the task fans out, exceeds one context
   window, or needs different models/tools per sub-task.
5. It passes the sub-task plus only the context that sub-task needs; it should
   not dump the whole conversation/state.

</details>

---

## Done when

- [ ] `handoff.py` runs planner → writer and produces a brief.
- [ ] You've compared it to a single-agent version on cost, latency, quality.
- [ ] You've added a third role and seen the extra call.
- [ ] You can list three costs of multi-agent from memory.

## Pitfalls

- **Splitting for its own sake** — if one prompt does it well, keep one agent.
- **Passing full state to every worker** — defeats the isolation benefit and
  inflates cost.
- **No plan for combining results** — decide the reduce step up front.

## Carries to next session

You did a hard-coded hand-off. Session 2 replaces the fixed order with a
supervisor that *decides* which worker runs next.
