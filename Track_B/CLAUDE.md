# Track B — Foundations

Parent workspace: `D:\AI` (see `..\CLAUDE.md` for how this relates to Track A).

## Responsibility

Build systematic conceptual grounding for AI/agent work. Runs in parallel
with `Track_A`, not before it — pulled in just-in-time when something in
Track_A doesn't make sense, plus a dedicated ongoing share of study time
(roughly 40%) so foundations don't get perpetually deprioritized once
Track_A "just works."

## Learning path (stages)

1. **Math & Statistics Basics** — `Math_stat/` (in progress). Linear algebra,
   statistics, probability, calculus, decision/orchestration math. Each topic
   folder has `notes.md` (intuition + why it matters for agents) and
   `exercises.py` (dependency-free Python, worked examples + TODO exercises
   with self-checking asserts).
2. **NLP Fundamentals**
3. **Machine Learning Basics**
4. **Deep Learning Basics**
5. **Transformers & LLMs**
6. **Vector DB & Semantic Search**
7. **RAG** (conceptual side — practical RAG building happens in `Track_A`)

Each future stage gets its own folder here (sibling to `Math_stat/`),
following the same notes.md + exercises.py pattern established in
`Math_stat/`, unless a post-stage review changes the method.

## Working style

- Watch a short intuition-first video before coding a topic (3Blue1Brown for
  linear algebra/calculus, StatQuest for statistics/probability).
- Do the `TODO` exercises yourself before reading the solution comment.
- After finishing a stage, review what worked before starting the next —
  the method here is expected to evolve, not stay fixed.
- Don't scaffold a stage's materials before the user is ready to start it.
