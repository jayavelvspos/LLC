# Session 5 — Retrieval Quality & Failure (~45 min)

**Objective:** learn to diagnose *why* retrieval returns the wrong chunks, and
fix it with top-k tuning, metadata filters, query rewriting, and re-ranking.
This is the session designed to send you into Track_B.

**Prerequisites:** Session 4 complete (`rag.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Failure taxonomy: missing, buried, off-topic, near-duplicate |
| 10–20 | **Track_B checkpoint** — does bad retrieval make sense to you? |
| 20–40 | Try fixes: query rewrite, filter, higher-k + re-rank |
| 40–45 | Notes |

---

## Concepts

- **Failure modes:**
  - *Missing* — the right chunk isn't in the top-k at all (k too low, chunking
    too coarse, embedding mismatch).
  - *Buried* — it's at rank 8 when you only pass 5 (raise k, then re-rank).
  - *Off-topic winners* — semantically close but wrong (needs a filter or a
    sharper query).
  - *Near-duplicates* — top-k is 5 copies of the same passage (dedupe / MMR).
- **Fixes, cheapest first:**
  1. **Query rewriting** — expand the user's question ("pw reset" → "how to
     reset account password login credentials") before embedding.
  2. **Metadata filter** — constrain to the relevant source/section/date.
  3. **Raise k + re-rank** — retrieve 20, then score each against the query with
     a cross-encoder / rerank API, keep top 5.
  4. **Re-chunk** — if the answer never sits cleanly in one chunk.
  5. **Better embedding model** — last resort; re-embeds everything.
- **Why cosine can mislead:** high-dimensional vectors, dominant "topic"
  directions, un-normalized magnitudes, stopword-heavy chunks. This is the
  Track_B footing.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Contextual Retrieval* (the reranking + contextual-chunk section):
  <https://www.anthropic.com/news/contextual-retrieval>.
- Voyage AI / Cohere docs — *Rerank* API (`rerank-2` / `rerank-3`):
  <https://docs.voyageai.com/docs/reranker>.
- LangChain docs — *MMR retrieval* and *contextual compression / rerankers*.

**Video (pick one, ~15–25 min):**
- Search *"RAG reranking cross encoder explained"*.
- **3Blue1Brown** — *"Dot products and duality"* / the linear algebra series, as
  the companion to the Track_B topic.

---

## Track_B link (step 3) — **the designed switch point**

`../CLAUDE.md` calls this out explicitly: *bad RAG retrieval → go deep on cosine
similarity / embeddings in `Track_B/Math_stat/01_linear_algebra`.*

**Do the checkpoint honestly.** Look at one real bad retrieval from your corpus.
Can you explain, in terms of vectors and angles, why the wrong chunk scored
higher? If not — **switch now** to `Track_B/Math_stat/01_linear_algebra`: dot
product, norm, cosine, projection, and why high dimensions are weird. 20–30 min,
then return. If you already had this from Session 1's switch, note it and
proceed to the fixes.

---

## Worked example — raise k, then re-rank

`code/rerank.py`:

```python
# import a rerank client, e.g. voyageai.Client().rerank(query, docs, model="rerank-2")

def retrieve_rerank(question, pre_k=20, final_k=5):
    hits = search(question, k=pre_k)                  # session 3
    docs = [d for d, _, _ in hits]
    scored = rerank(question, docs)                   # -> list of (index, relevance)
    keep = [hits[i] for i, _ in sorted(scored, key=lambda p: -p[1])[:final_k]]
    return keep
```

Compare on a question that was failing:

```
plain top-5:      ['policy.md#3', 'policy.md#4', 'faq.md#1', 'policy.md#5', 'faq.md#2']
                  -> answer chunk (onboarding.md#1) NOT present
k=20 + rerank-5:  ['onboarding.md#1', 'onboarding.md#2', 'faq.md#1', 'policy.md#3', 'faq.md#2']
                  -> answer chunk now rank 1
```

Read it: the answer chunk *was* retrievable (it was in the top-20) but the raw
embedding ranked it 9th; the reranker, which reads query+chunk together, pushed
it to the top.

---

## Build

- Collect 3 questions where `rag.py` currently gives a wrong or "not covered"
  answer. Classify each failure (missing / buried / off-topic / duplicate).
- Apply the matching fix and re-test:
  - buried → `retrieve_rerank`
  - off-topic → a `where` filter or a rewritten query
  - missing → raise k, or re-chunk that document
- Record before/after: did the answer become correct? did an unrelated question
  regress? (Keep a scratch list — Session 6 makes this a real eval.)

---

## Quick test (step 7 — answer from memory, then check)

1. Name the four retrieval failure modes.
2. What's the difference between "missing" and "buried", and the fix for each?
3. What does query rewriting do and when does it help?
4. How does a reranker differ from the initial embedding search?
5. In vector terms, give one reason a wrong chunk can out-score the right one.

<details><summary>Answers</summary>

1. Missing, buried, off-topic winners, near-duplicates.
2. Missing = not in top-k at all (raise k / re-chunk / fix embedding). Buried =
   in a larger top-k but below your cutoff (raise k, then rerank).
3. Expands/clarifies the query before embedding so it better matches the
   corpus's wording; helps with terse or jargon queries.
4. The embedding search scores query and chunk vectors independently; a
   reranker scores the query and chunk *together* (cross-encoder), which is more
   accurate but slower, so it's applied to a shortlist.
5. Any one: it shares a dominant topic direction, the query vector is pulled by
   stopwords/boilerplate, magnitudes aren't normalized, or the right chunk's
   signal is diluted by unrelated text in the same chunk.

</details>

---

## Done when

- [ ] 3 previously-failing questions classified and at least 2 fixed.
- [ ] A rerank step demonstrated to promote a buried answer chunk.
- [ ] The Track_B checkpoint is done — switched or explicitly logged as
      already-covered, in `notes.md`.
- [ ] You can name the four failure modes from memory.

## Pitfalls

- **Fixing one query, breaking three** — always re-test other questions.
- **Reranking a bad shortlist** — if `pre_k` doesn't contain the answer,
  reranking can't help. Raise `pre_k` first.
- **Skipping the Track_B checkpoint** because you're "close" — this is the one
  the workspace was designed around.

## Carries to next session

You have ad-hoc fixes and a scratch list of question outcomes. Session 6 turns
that into a real eval with numbers.
