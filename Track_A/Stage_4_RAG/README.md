# Stage 4 — RAG (Retrieval-Augmented Generation)

**Stage goal:** ground the agent's answers in your own documents. Build a Q&A
agent that retrieves relevant chunks, generates an answer with citations, and is
measured on a small eval set — treating embeddings and the vector store as
API calls at first, and going deep on the math only when retrieval misbehaves.

Six ~45-minute sessions, in order.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Embeddings as an API](session_1_embeddings_as_an_api.md) | text → vectors; similar text → nearby vectors, checked by hand |
| 2 | [Chunking & loading](session_2_chunking_and_loading.md) | documents split into chunks with metadata; size/overlap understood |
| 3 | [Vector store CRUD](session_3_vector_store_crud.md) | add / query / delete; top-k retrieval working |
| 4 | [The RAG pipeline](session_4_the_rag_pipeline.md) | retrieve → context → grounded answer with citations |
| 5 | [Retrieval quality & failure](session_5_retrieval_quality_and_failure.md) | diagnose bad retrieval; top-k, filters, re-ranking; the Track_B deep-dive point |
| 6 | [Evaluating RAG](session_6_evaluating_rag.md) | retrieval hit-rate + answer-faithfulness numbers — the deliverable |

## Conventions

Python 3.10+. **Embeddings:** Anthropic has no first-party embeddings endpoint —
use an embeddings API (Anthropic recommends **Voyage AI**, `voyageai`;
alternatives: Cohere, OpenAI, or local `sentence-transformers`). **Vector
store:** start local with **Chroma** or **FAISS**. `claude-opus-5` for
generation. Run every session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

## Working files produced in this stage

```
Stage_4_RAG/
  corpus/                 # the documents you'll answer questions over
  code/
    embed.py              # session 1 — embedding + similarity helpers
    chunk.py              # session 2
    store.py              # session 3 — vector store wrapper
    rag.py                # session 4 — the pipeline
    rerank.py             # session 5
    eval_rag.py           # session 6
    eval_set.jsonl        # session 6 — labelled questions
  notes.md
```

## Done with Stage 4 when

- [ ] `rag.py "a question about the corpus"` returns an answer that cites the
      chunk(s) it used.
- [ ] `eval_rag.py` reports a retrieval hit-rate and an answer-faithfulness
      score on `eval_set.jsonl`.
- [ ] You can explain cosine similarity well enough to say *why* a bad
      retrieval was bad — pulled from `Track_B/Math_stat/01_linear_algebra` if
      needed.
- [ ] You've improved the hit-rate at least once by changing chunking, top-k,
      a metadata filter, or re-ranking — and the eval number moved.
