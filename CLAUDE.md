# AI Learning Workspace (parent)

This directory is the root of a two-track learning project for building and
orchestrating AI agents. It contains two sibling projects, each with its own
`CLAUDE.md` describing its learning path and responsibility in detail:

- **`Track_A/`** — practical track. Hands-on agent building (direct LLM tool
  calling → LangGraph → RAG → multi-agent orchestration → production
  systems). Does not wait for Track_B to be finished.
- **`Track_B/`** — foundations track. Conceptual grounding (Math & Stats →
  NLP → ML → DL → Transformers & LLMs → Vector DB & Semantic Search → RAG).
  Currently contains `Math_stat/` (linear algebra, statistics, probability,
  calculus, decision/orchestration math).

## How the two tracks relate

They run **in parallel, not sequentially**. Track_A leads; Track_B is pulled
in just-in-time whenever something built in Track_A doesn't make sense or
misbehaves (e.g. bad RAG retrieval → go deep on cosine similarity/embeddings
in `Track_B/Math_stat`). Target split is roughly 60% Track_A / 40% Track_B,
reviewed and adjusted every couple of weeks rather than only at the end of
each stage.

When working in this workspace, treat `Track_A/CLAUDE.md` and
`Track_B/CLAUDE.md` as authoritative for what belongs in each track.
