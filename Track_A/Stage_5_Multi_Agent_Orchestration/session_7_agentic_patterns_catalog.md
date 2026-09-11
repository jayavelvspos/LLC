# Session 7 — Agentic Patterns Catalog (~45 min)

**Objective:** recognise and implement the core agentic patterns — prompt
chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer
(workflows), plus ReAct, reflection, and planning (single-agent) — and be able
to pick the right one for a task instead of defaulting to "a big agent".

**What you'll learn:**
- Workflow (fixed control flow) vs. agent (LLM decides) and when to prefer each
- The five workflow patterns: chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer
- The single-agent patterns: ReAct, reflection/self-critique, planning
- Choosing the simplest pattern that fits, and never adding one without a concrete failure it fixes

**Prerequisites:** Sessions 1–2 complete (hand-off, supervisor). This is an
**extension session** — it pairs naturally right after Session 2; it's numbered
7 only to avoid renumbering the build.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Workflow vs agent; the five workflow patterns |
| 10–30 | `code/patterns.py` — implement chain / route / parallel-vote / evaluator-optimizer |
| 30–40 | Run route + vote + evaluator-optimizer; record where each earns its cost |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

**Workflow** = control flow is fixed in code; LLM calls fill in the steps.
**Agent** = the LLM decides what to do next. Prefer a workflow whenever the
steps are knowable in advance — it's cheaper, more predictable, easier to trace.

**Workflow patterns** (Anthropic, *Building Effective Agents*):

| Pattern | Shape | Use when | You've seen it in |
|---|---|---|---|
| **Prompt chaining** | fixed sequence of LLM calls, optional gate check between | task decomposes into stable ordered steps | Stage 0 roles_demo |
| **Routing** | classify the input → send to a specialised prompt / tool / model | inputs fall into distinct kinds handled differently | Session 2 supervisor |
| **Parallelization** | *sectioning* (independent sub-tasks in parallel) or *voting* (same task N times, aggregate) | subtasks are independent, or you want consensus / higher recall | Session 4 fan-out |
| **Orchestrator-workers** | an orchestrator LLM decomposes dynamically, delegates, synthesises | you can't predict the sub-tasks up front | Session 3 |
| **Evaluator-optimizer** | generator produces → evaluator critiques vs criteria → loop | output has checkable quality criteria and first drafts often miss them | Stage 5B Session 3 (deep) |

**Single-agent patterns** (the model drives):

- **ReAct** — repeat **Reason** (a thought) → **Act** (a tool call) → **Observe**
  (the result) until done. Your Stage 1 loop *is* ReAct.
- **Reflection / self-critique** — after answering, the model grades its own
  output against a rubric and revises. A one-shot evaluator-optimizer.
- **Planning** — the model writes an explicit plan first, executes step by step,
  and re-plans when a step fails.

**Choosing:** simplest thing that works. Fixed steps → workflow. Unknown number
or shape of steps → agent. Never add a pattern without a concrete failure it
fixes.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Anthropic — *Building Effective Agents* (the canonical catalogue; workflows vs
  agents, when not to): <https://www.anthropic.com/research/building-effective-agents>.
- Anthropic — *How we built our multi-agent research system*:
  <https://www.anthropic.com/engineering/multi-agent-research-system>.
- LangGraph docs — *Workflows and agents* (prebuilt implementations of each
  pattern): <https://langchain-ai.github.io/langgraph/tutorials/workflows/>.

**Video (pick one, ~15–30 min):**
- Search *"Anthropic building effective agents"* — the talk walks each pattern
  with diagrams.

---

## Track_B link (step 3)

**Light, non-blocking.** Routing is an expected-value decision (pick the branch
with the best expected outcome per cost); voting/aggregation is ensemble
statistics (majority vote reduces variance). Note *"revisit in Track_B:
`05_decision_and_orchestration_math` — routing as EV; majority-vote / ensemble
variance"* and continue.

---

## Worked example — one task, three patterns  <!-- step 4 -->

`code/three_ways.py` — task: *"Draft a product announcement for <X>. Under 120
words. No hype words (revolutionary, game-changing, seamless, cutting-edge)."*

```python
from anthropic import Anthropic
client = Anthropic()
HYPE = {"revolutionary", "game-changing", "seamless", "cutting-edge"}
RULES = "under 120 words; contains none of: " + ", ".join(HYPE)

def call(prompt, system=None):
    m = client.messages.create(model="claude-opus-5", max_tokens=1024,
        system=system, messages=[{"role": "user", "content": prompt}])
    return next(b.text for b in m.content if b.type == "text")

def violations(text):
    v = []
    if len(text.split()) > 120: v.append("too long")
    if any(w in text.lower() for w in HYPE): v.append("hype word")
    return v

X = "a CLI that renders Markdown as slide decks"

# 1. single call
one = call(f"Write the announcement. Rules: {RULES}. Topic: {X}")

# 2. evaluator-optimizer
draft = one
for rnd in range(3):
    v = violations(draft)
    if not v: break
    draft = call(f"Revise to fix {v}. Keep it about {X}. Rules: {RULES}.\n\n{draft}")

# 3. prompt chain: outline -> draft -> trim
outline = call(f"3 bullet points an announcement of {X} must hit. Bullets only.")
chain = call(f"Write the announcement from this outline. Rules: {RULES}.\n{outline}")
chain = call(f"Cut to under 120 words, remove any hype words:\n\n{chain}")

for name, txt in [("single", one), ("eval-opt", draft), ("chain", chain)]:
    print(f"{name:9} violations={violations(txt)}  words={len(txt.split())}")
```

**Expected output** (shape):

```
single    violations=['too long']       words=134
eval-opt  violations=[]                  words=112
chain     violations=[]                  words=118
```

Read it: the single call often misses a hard constraint; the evaluator-optimizer
loop *closes* on it (it re-checks and revises); the chain gets there by making
"trim" its own dedicated step. Two different patterns, same fix, different cost
(eval-opt = 1 + up to 3 calls; chain = 3 calls always).

---

## Build: `code/patterns.py`  <!-- step 5 -->

Implement each as a small reusable function over the Anthropic client:
`prompt_chain(steps, x)`, `route(x, routes)`, `parallel_vote(prompt, n)`,
`evaluator_optimizer(task, check, max_rounds)`.

Experiments:
1. **Routing.** Build a 3-way router — *code question / factual lookup /
   creative* — each with its own system prompt. Feed 6 inputs, 2 per class, and
   one deliberate edge case. Log every misroute and why.
2. **Parallel vote.** Ask a question with one correct numeric answer 5 times,
   take the majority. Compare accuracy and cost to a single call over 10 trial
   questions. When is voting worth 5×?
3. **Evaluator-optimizer.** Pick a task with machine-checkable constraints
   (word count, required sections, valid JSON). Log rounds-to-pass. Then find a
   task where it never converges and add a `max_rounds` budget that returns the
   best attempt.

---

## Quick test (step 7 — answer from memory, then check)

1. Workflow vs agent — the one-line distinction.
2. What does prompt chaining trade away for reliability, and what guards it?
3. Routing: what are you classifying, and what varies per route?
4. Name the two forms of parallelization and what each is for.
5. Evaluator-optimizer: the two roles, and what makes it terminate?
6. ReAct expands to which three repeated steps?

<details><summary>Answers</summary>

1. Workflow = control flow fixed in code; agent = the LLM decides the next step.
2. Latency/flexibility (more calls, rigid order); a *gate* check between steps
   catches an error before it compounds down the chain.
3. The kind of input (its class); the system prompt / tool / model used to
   handle it.
4. *Sectioning* — independent sub-tasks run concurrently then combined;
   *voting* — the same task run N times and aggregated for consensus/recall.
5. A generator that produces and an evaluator that critiques against explicit
   criteria; it stops when the evaluator passes it or a round/cost budget is
   hit.
6. Reason (thought) → Act (tool call) → Observe (result).

</details>

---

## Done when  <!-- step 8 -->

- [ ] `patterns.py` implements ≥4 patterns as reusable functions.
- [ ] You've run routing, parallel-vote, and evaluator-optimizer and written
      where each earned its extra cost and where it didn't.
- [ ] Given a new task, you can name the pattern you'd use and why.
- [ ] You can list the five workflow patterns from memory.

## Pitfalls

- **Agent where a workflow would do** — unpredictable and pricier for no gain.
- **Vague evaluator criteria** — it never converges, or rubber-stamps
  everything. Make the check mechanical where possible.
- **Voting on open-ended tasks** — there's no majority to take.
- **Chains with no gate** — a bad step 2 poisons steps 3–5 silently.

## Carries to next session

A vocabulary of patterns. Session 8 shows how CrewAI / AutoGen / Agno package
these so you stop hand-rolling each one.
