# Track A — Practical Agent Building

Parent workspace: `D:\AI` (see `..\CLAUDE.md` for how this relates to Track B).

## Responsibility

Build real, working agents hands-on, starting immediately — do not wait for
Track_B's foundations to be finished. Treat underlying concepts (embeddings,
vector search, transformers) as black-box APIs at first; go deep on a concept
only when something built here doesn't work or doesn't make sense, then pull
that concept in from `Track_B` just-in-time.

## Learning path

1. **Direct LLM API + tool/function calling** — no framework yet. Understand
   what "an agent" fundamentally is: an LLM call plus a loop plus tools.
2. **LangGraph basics** — nodes, edges, state. Build a single-tool graph.
3. **Add a second tool + basic memory.**
4. **RAG** — treat the vector DB and embeddings as an API call at first;
   revisit `Track_B/Math_stat/01_linear_algebra` (cosine similarity) if
   retrieval quality doesn't make sense.
5. **Multi-agent / multi-node orchestration** — routing between sub-agents.
   Relates to `Track_B/Math_stat/05_decision_and_orchestration_math`
   (Markov chains, expected-value routing).
6. **Production concerns** — logging, evals, retries, cost/latency tracking,
   deployment.

## Working style

- Prefer building something runnable over reading docs end-to-end.
- When a result surprises you (bad retrieval, overconfident/hallucinated
  answers, unclear cost/latency behavior), stop and go deep on the relevant
  Track_B concept before continuing — don't just patch around it.
- Review progress roughly every 2 weeks: what did building surface that
  needs deeper understanding, and did recent Track_B learning change how you
  build?
