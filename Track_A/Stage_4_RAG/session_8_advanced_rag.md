# Session 8 — Advanced RAG: Query Transformation, Hybrid & Fusion (~45 min)

**Objective:** raise retrieval quality with query-side techniques (multi-query,
HyDE, RAG-fusion), chunk-side techniques (parent-document, contextual chunks),
and hybrid dense+sparse search — and adopt each **only if the eval number
moves**. This produces the "Advanced RAG with Reranking" example.

**What you'll learn:**
- Query-side techniques: multi-query, HyDE, RAG-fusion, decomposition
- Chunk-side techniques: parent-document, sentence-window, contextual retrieval
- Hybrid dense+sparse search fused with Reciprocal Rank Fusion
- Adopting a technique only when it moves your Session 6 eval numbers

**Prerequisites:** Session 6 (`eval_rag.py`, `eval_set.jsonl`) and Session 7
(a real vector store) complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 7's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The two weak points of plain RAG: the query, and the chunk |
| 10–30 | `code/advanced_rag.py` — switchable retrieval strategies |
| 30–40 | Run each strategy through `eval_rag.py`; tabulate the numbers |
| 40–45 | Notes — which strategy you adopt, and why |

---

## Concepts  <!-- step 2 -->

Plain RAG retrieves on the **raw user question** against **independently
embedded chunks**. Advanced RAG attacks one or both.

**Query-side (rewrite what you search with):**

| Technique | What it does | Helps when |
|---|---|---|
| **Multi-query** | LLM rewrites the question into N paraphrases; retrieve for each; union the hits | terse or ambiguous questions |
| **HyDE** | LLM drafts a *hypothetical answer*; embed **that** and retrieve — a fake passage matches real passages better than a question does | jargon gaps between question and corpus wording |
| **RAG-fusion** | multi-query + **Reciprocal Rank Fusion** to merge the ranked lists into one | you want multi-query's recall without ballooning top-k |
| **Decomposition** | split a multi-part question into sub-questions; retrieve + answer each; compose | "compare X and Y and cite the policy" style questions |

**Chunk-side (change what you match / return):**

| Technique | Embed | Return | Why |
|---|---|---|---|
| **Parent-document** | small child chunks | the larger parent chunk | precise match, full context |
| **Sentence-window** | single sentences | the sentence ± k neighbours | pinpoint the hit, keep surrounding context |
| **Contextual retrieval** (Anthropic) | chunk **with an LLM-written context blurb prepended** | the chunk | fixes "this paragraph makes no sense out of its section" |

**Hybrid search:** fuse dense (embedding) with sparse (BM25) via RRF. Dense
blurs exact tokens — codes, IDs, rare names, error strings; BM25 nails them.

**Reranking (Session 5) stacks on top of all of the above.** "Advanced RAG with
reranking" = use multi-query / hybrid to build a *wide* candidate set, then a
cross-encoder reranker to trim it to the final k.

**The rule:** every technique adds latency and (for the LLM-based ones) cost per
query. Adopt one only when `eval_rag.py` shows it moved hit-rate or faithfulness
on a **held-out** set.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Anthropic — *Contextual Retrieval*:
  <https://www.anthropic.com/news/contextual-retrieval>.
- LangChain docs — `MultiQueryRetriever`, `ParentDocumentRetriever`,
  `EnsembleRetriever` (hybrid), `LongContextReorder`:
  <https://python.langchain.com/docs/how_to/#retrievers>.
- HyDE — *Precise Zero-Shot Dense Retrieval without Relevance Labels*
  (Gao et al., 2022): <https://arxiv.org/abs/2212.10496>.

**Video (pick one, ~15–30 min):**
- Search *"RAG fusion reciprocal rank fusion explained"* or *"advanced RAG
  techniques"* — focus on multi-query + RRF and parent-document.

---

## Track_B link (step 3)

**Light, non-blocking.** Reciprocal Rank Fusion, `precision@k`, and MRR are
ranking statistics; the hit-rate deltas you read off the eval are the same
precision/recall ideas as Session 6. Note *"revisit in Track_B: rank fusion
(RRF), precision@k / MRR"* and continue.

---

## Worked example — multi-query + RRF on failing questions  <!-- step 4 -->

`code/rag_fusion.py`:

```python
from anthropic import Anthropic
from store import search            # session 3 / 7

client = Anthropic()

def rewrites(question, n=4):
    msg = client.messages.create(
        model="claude-opus-5", max_tokens=1024,
        messages=[{"role": "user", "content":
            f"Give {n} alternative search queries for: {question}\n"
            f"One per line, no numbering."}],
    )
    text = next(b.text for b in msg.content if b.type == "text")
    return [question] + [ln.strip() for ln in text.splitlines() if ln.strip()]

def rrf(ranked_lists, k=60):
    scores = {}
    for lst in ranked_lists:
        for rank, doc_id in enumerate(lst):
            scores[doc_id] = scores.get(doc_id, 0) + 1 / (k + rank)
    return sorted(scores, key=scores.get, reverse=True)

def fusion_retrieve(question, k=5):
    lists = [[h.id for h in search(q, k=10)] for q in rewrites(question)]
    return rrf(lists)[:k]
```

Compare on a question `rag.py` currently fails:

```
plain top-5   : ['policy.md#3', 'policy.md#4', 'faq.md#1', 'policy.md#5', 'faq.md#2']
                -> answer chunk (onboarding.md#1) NOT present
fusion top-5  : ['onboarding.md#1', 'faq.md#1', 'onboarding.md#2', 'policy.md#3', 'faq.md#2']
                -> answer chunk now rank 1

hit-rate on eval_set.jsonl:  plain 0.62  ->  fusion 0.79
```

Read it: three of the four rewrites phrased the question in wording closer to
`onboarding.md`; RRF rewarded the chunk that showed up across several lists even
though no single list ranked it first.

---

## Build: `code/advanced_rag.py`  <!-- step 5 -->

Wrap `rag.py`'s retriever with a `--strategy` switch:
`plain | multiquery | hyde | fusion | hybrid | parent`. Every strategy returns
the same shape (a ranked list of chunk ids), so `eval_rag.py` scores them
identically.

Experiments:
1. **Bake-off.** Run all strategies over `eval_set.jsonl`. Tabulate:
   | strategy | hit-rate | faithfulness | median latency | $/query |
   Adopt the one that best trades quality for cost — or keep `plain` if nothing
   beats it enough to justify the latency.
2. **Stack.** Best retriever + the Session 5 reranker. Re-run the eval. Check
   previously-**passing** questions didn't regress.
3. **HyDE both ways.** Find one eval question where HyDE helps and one where it
   hurts (it hallucinates a misleading pseudo-doc on niche topics). Explain each
   in `notes.md`.

---

## Quick test (step 7 — answer from memory, then check)

1. What does multi-query retrieval change, and why does it help?
2. HyDE embeds *what*, and why is that better than embedding the question?
3. What does Reciprocal Rank Fusion take as input, and what does it reward?
4. Parent-document retriever: what's embedded vs what's returned, and why split
   them?
5. When does hybrid (dense + BM25) beat pure dense retrieval?
6. What's the rule for adopting any advanced technique?

<details><summary>Answers</summary>

1. It retrieves on several LLM-generated paraphrases of the question and unions
   the results — covers wording the original question missed.
2. A hypothetical answer the LLM drafts. A fake passage is structurally more
   like the real passages in the corpus than a question is, so it matches
   better.
3. Several ranked lists of the same items; it rewards items that appear near the
   top across *multiple* lists (score `Σ 1/(k + rank)`).
4. Small child chunks are embedded (precise matching); the larger parent chunk
   is returned (enough context to answer). Small-to-match, large-to-read.
5. When the query hinges on exact tokens — codes, IDs, error strings, rare
   names — that dense embeddings smear together.
6. Only adopt it if the eval (`hit-rate` / faithfulness) improves on a held-out
   set by enough to justify the added latency and cost.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `advanced_rag.py` offers ≥3 retrieval strategies switchable by flag.
- [ ] You have a table of hit-rate / faithfulness / latency / cost per strategy
      on `eval_set.jsonl`.
- [ ] You adopted or rejected each strategy **based on the number**, written in
      `notes.md`.
- [ ] You can explain RRF and HyDE from memory.

## Pitfalls

- **Adding techniques without measuring** — every one costs latency; some cost
  an extra LLM call per query. The eval is the judge.
- **Tuning on the test set** — keep a held-out slice of `eval_set.jsonl` you
  never look at while iterating.
- **Multi-query cost blow-up** — N× retrieval plus a rewrite call. Cache
  rewrites for repeated questions.
- **Parent chunks blowing the context budget** — a big parent per hit can
  overflow the prompt; cap how many you return.

## Carries to next session

Stage 4's deliverable is now a **measured, tunable** retriever with a strategy
bake-off recorded. This closes Stage 4 — carry the eval habit (change one thing,
re-measure) into every stage that follows.
