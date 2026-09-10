# Session 8 — Multi-Agent Frameworks: CrewAI, AutoGen, Agno (~45 min)

**Objective:** build the same small system — a **Multi-Agent Content Crew** that
researches, writes, and edits a short article — in **CrewAI**, compare it head to
head with the LangGraph supervisor from Sessions 2–3, and skim **AutoGen** and
**Agno** so you can choose a framework on purpose.

**Prerequisites:** Sessions 1–6 complete (you have the LangGraph version to
compare against). Extension session — do it after the Stage 5 build.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What every framework must provide; where they differ |
| 10–30 | `code/crew_content.py` — 3 role agents, 3 tasks, run it |
| 30–40 | Sequential vs hierarchical; ground the researcher with the Stage 4 retriever |
| 40–45 | Fill the comparison table; notes |

---

## Concepts  <!-- step 2 -->

Every multi-agent framework has to provide the same five things — **roles**,
**task decomposition**, a **turn-taking / hand-off mechanism**, **tool calling**,
and a **termination condition**. They differ in *how much state you own* and
*how control flow is expressed*.

| Framework | Building blocks | Control flow | Best at |
|---|---|---|---|
| **LangGraph** | nodes, edges, a typed `State` | explicit graph you design | complex stateful flows; when you need to *reason about* the graph |
| **CrewAI** | `Agent` (role, goal, backstory, tools, llm), `Task` (description, expected_output, agent), `Crew` (process=`sequential`\|`hierarchical`) | a task list, or a manager LLM (`hierarchical`) that delegates | standing up a role-based pipeline fast |
| **AutoGen** (`autogen-agentchat`) | `AssistantAgent`, `UserProxyAgent`, a team / `GroupChatManager` that picks the next speaker | agents **converse**; the manager routes turns | code-execution loops, human-in-the-loop |
| **Agno** | `Agent` (model, tools, instructions), `Team` | lightweight; minimal abstraction | latency- and cost-sensitive builds; model-agnostic |

- **CrewAI `hierarchical` process** adds a manager agent — that's CrewAI's
  supervisor, and it costs extra LLM calls per round (the manager reasons about
  delegation every step).
- **Framework caution** (Anthropic): every abstraction layer hides the actual
  prompts and responses. Turn on verbose / telemetry, and know how to drop to
  raw SDK calls when the framework fights you.
- **Choosing:** LangGraph for stateful control flow; CrewAI for quick role
  pipelines; AutoGen for conversational / code-exec / HITL; Agno when the
  framework's own overhead matters; raw SDK (Stage 1) when none of them fit.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- CrewAI docs — *Quickstart*, *Crews*, *Hierarchical process*:
  <https://docs.crewai.com/>.
- Microsoft AutoGen docs — *AgentChat* teams and termination:
  <https://microsoft.github.io/autogen/stable/>.
- Agno docs — *Agents* and *Teams*: <https://docs.agno.com/>.
- Anthropic — *Building Effective Agents* (the "frameworks add layers" caution).

**Video (pick one, ~15–30 min):**
- Search *"CrewAI crash course"* or *"LangGraph vs CrewAI vs AutoGen"*.

---

## Track_B link (step 3)

**None.** This session is framework ergonomics — APIs, not maths. Note "no
Track_B link" and continue.

---

## Worked example — the content crew in CrewAI  <!-- step 4 -->

`code/crew_content.py`:

```python
from crewai import Agent, Task, Crew, Process

researcher = Agent(role="Researcher", goal="Gather 4-5 accurate facts on the topic",
    backstory="Meticulous; never invents figures.", llm="claude-opus-5", verbose=True)
writer = Agent(role="Writer", goal="Turn the facts into a 150-word article",
    backstory="Plain, concrete prose.", llm="claude-opus-5", verbose=True)
editor = Agent(role="Editor", goal="Tighten and fact-align the draft",
    backstory="Cuts fluff; flags unsupported claims.", llm="claude-opus-5", verbose=True)

topic = "why vector databases use approximate nearest-neighbour search"
t1 = Task(description=f"Research: {topic}", expected_output="5 bullet facts", agent=researcher)
t2 = Task(description="Write the 150-word article from the facts", expected_output="article", agent=writer)
t3 = Task(description="Edit for length and accuracy", expected_output="final article", agent=editor)

crew = Crew(agents=[researcher, writer, editor], tasks=[t1, t2, t3],
            process=Process.sequential, verbose=True)
print(crew.kickoff())
```

**Expected output** (shape):

```
[Researcher] ... 5 bullets
[Writer]     ... ~150-word draft
[Editor]     ... final article, 2 claims flagged
<final article text>
```

Read it: ~25 lines to express what took a multi-node graph in Sessions 2–3.
You gave up explicit state and routing control; you gained speed of assembly.

---

## Build: `code/crew_content.py`  <!-- step 5 -->

Build the crew above and run it. Experiments:

1. **Sequential → hierarchical.** Set `process=Process.hierarchical` (add
   `manager_llm="claude-opus-5"`). Watch the manager delegate. Compare total LLM
   calls and cost to the sequential run — the manager isn't free.
2. **Ground it.** Wrap your Stage 4 retriever as a CrewAI tool and give it to
   the researcher. Confirm the article now cites real corpus facts, not the
   model's priors.
3. **Port one step.** Re-implement just the *editor* in AutoGen **or** Agno.
   Note what was easier and what was harder than CrewAI.
4. **Comparison table** in `notes.md`:

   | framework | LOC | state control | routing style | observability | when I'd choose it |
   |---|---|---|---|---|---|
   | LangGraph | | | | | |
   | CrewAI | | | | | |
   | AutoGen *or* Agno | | | | | |

---

## Quick test (step 7 — answer from memory, then check)

1. CrewAI's three core objects and what each holds.
2. Sequential vs hierarchical process in CrewAI — what changes, and the cost
   implication.
3. How does AutoGen express multi-agent coordination differently from LangGraph?
4. Name one thing you give up moving LangGraph → CrewAI, and one you gain.
5. The framework-agnostic constant: what must every one of them provide?

<details><summary>Answers</summary>

1. `Agent` (role, goal, backstory, tools, llm), `Task` (description,
   expected_output, agent), `Crew` (the agents + tasks + a process).
2. Sequential runs tasks in listed order; hierarchical adds a manager LLM that
   decides delegation each round — more flexible, more LLM calls / higher cost.
3. AutoGen agents hold a **conversation** and a manager picks the next speaker;
   LangGraph routes via explicit edges over a shared typed state.
4. Give up: explicit state + control-flow design, fine-grained routing. Gain:
   far less code, opinionated defaults, faster to stand up.
5. Roles, task decomposition, a hand-off/turn-taking mechanism, tool calling,
   and a termination condition.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `crew_content.py` produces an article via ≥3 role agents.
- [ ] You've run both sequential and hierarchical and compared cost.
- [ ] One agent is grounded with the Stage 4 retriever (real citations).
- [ ] The comparison table is filled with a "when I'd choose this" per row.
- [ ] You can sketch the Session 2 supervisor's job in CrewAI from memory.

## Pitfalls

- **Framework hides the prompts** — run with `verbose=True` / telemetry so you
  can see and tune what's actually sent.
- **Hierarchical cost surprise** — the manager agent calls the model every
  delegation round.
- **Porting state-heavy LangGraph logic 1:1** — CrewAI's task model doesn't map
  cleanly onto a stateful graph; rethink, don't transliterate.
- **"More agents = better"** — always compare to the Session 6 single-supervisor
  baseline.

## Carries to next stage

You can choose a multi-agent framework deliberately. **Stage 5B** adds the
orchestration primitives underneath these (LCEL, routing, parallelism,
evaluator-optimizer) and connects agents to real systems via **MCP**. **Stage 6**
makes the whole thing production-grade.
