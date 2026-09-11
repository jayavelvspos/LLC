# Session 3 — Vector Store CRUD (~45 min)

**Objective:** load embedded chunks into a vector store and run top-k similarity
queries; add, update, and delete entries.

**What you'll learn:**
- What a vector store does: nearest-k search over `(id, vector, text, metadata)`
- Local vs. hosted options (Chroma, FAISS, Pinecone, Weaviate, pgvector)
- CRUD on a vector store: add, query, delete, upsert
- Choosing `k`, and metadata filtering to narrow the search space

**Prerequisites:** Session 2 complete (`chunk.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What a vector store does: store vectors + metadata, return nearest-k |
| 10–30 | `code/store.py` — build index from chunks; `search(query, k)` |
| 30–40 | Add / delete a chunk; re-query; metadata filtering |
| 40–45 | Notes |

---

## Concepts

- A **vector store** holds `(id, vector, text, metadata)` rows and answers
  "given this query vector, return the k most similar rows" fast (approximate
  nearest neighbor for big corpora; exact for small).
- **Local options:** Chroma (persistent, simple API), FAISS (in-memory, fast,
  no metadata filtering built in). Hosted: Pinecone, Weaviate, pgvector.
- **CRUD:** `add(ids, vectors, texts, metadatas)`, `query(vector, k, filter)`,
  `delete(ids)`, `update`/upsert. Re-embedding a changed chunk + upsert is the
  normal "edit" path.
- **`k`** (how many chunks to retrieve) is a key knob: too low → miss the answer;
  too high → noise and prompt bloat. Start at 4–6.
- **Metadata filter:** restrict the search (e.g. `source == "policy.md"`, or
  `date >= 2025`). Turns retrieval from "search everything" into "search the
  right subset".

---

## Learning resources

**Primary (official, stable):**
- Chroma docs — *Getting started* (collections, add, query, where-filters):
  <https://docs.trychroma.com/>.
- LangChain docs — *Vector stores* concept + the retriever interface:
  <https://python.langchain.com/docs/concepts/vectorstores/>.
- FAISS wiki — *Getting started* (if you use FAISS).

**Video (pick one, ~10–20 min):**
- Search *"Chroma vector database tutorial python"*.

---

## Track_B link (step 3)

**None directly** — but the store is *running* the cosine/inner-product math
from Session 1 at scale. If Session 1's Track_B revisit is still open and you
have time, this is a fine moment. Otherwise note and continue.

---

## Worked example — index and search

`code/store.py` (Chroma):

```python
import chromadb
from embed import embed          # session 1

client = chromadb.PersistentClient(path="code/chroma")
col = client.get_or_create_collection("corpus", metadata={"hnsw:space": "cosine"})

def index(chunks):
    col.add(ids=[f"{c['meta']['source']}:{c['meta']['chunk']}" for c in chunks],
            documents=[c["text"] for c in chunks],
            embeddings=embed([c["text"] for c in chunks]),
            metadatas=[c["meta"] for c in chunks])

def search(query, k=5, where=None):
    res = col.query(query_embeddings=embed([query]), n_results=k, where=where)
    return list(zip(res["documents"][0], res["metadatas"][0], res["distances"][0]))

for doc, meta, dist in search("how do I set up my dev environment?", k=3):
    print(f"{dist:.3f}  {meta['source']}#{meta['chunk']}  {doc[:80]}...")
```

**Expected output** (shape; lower distance = more similar for cosine space):

```
0.21  onboarding.md#1  Step 3: set up your dev environment by running ...
0.34  onboarding.md#2  After the environment is ready, clone the main repo ...
0.55  security.md#4    Development machines must have disk encryption enabled ...
```

Read it: the top hits are the onboarding chunks that actually describe setup;
`security.md#4` is topically adjacent but clearly further away.

---

## Build

- Build `store.py`; index your Session 2 chunks.
- Run 3 real questions about your corpus at `k = 2, 5, 10`. For each, note: is
  the answer-bearing chunk in the results? Where does it rank?
- `delete` the top chunk for one query, re-search → confirm the next-best takes
  its place. Re-`add` it.
- Add a `where={"source": "<one file>"}` filter → confirm results are restricted.
- Edit a chunk's text, re-embed, upsert → confirm the new text is returned.

---

## Quick test (step 7 — answer from memory, then check)

1. What does a vector store store, and what query does it answer?
2. What's the trade-off in choosing `k`?
3. How do you "edit" a chunk in the store?
4. What does a metadata filter do to a search?
5. Chroma vs FAISS — one practical difference.

<details><summary>Answers</summary>

1. Rows of `(id, vector, text, metadata)`; it answers "the k rows whose vectors
   are most similar to this query vector".
2. Too low → the answer chunk may be missed; too high → irrelevant chunks add
   noise and cost.
3. Re-embed the new text and upsert under the same id (add + delete, or
   update).
4. Restricts the candidate set to rows matching the filter before ranking by
   similarity.
5. Chroma persists and supports metadata `where` filters out of the box; FAISS
   is in-memory, very fast, and has no built-in metadata filtering.

</details>

---

## Done when

- [ ] `store.py` indexes chunks and returns ranked results with distances.
- [ ] You've recorded, for 3 questions, whether/where the answer chunk appears
      at k = 2/5/10.
- [ ] delete + re-add and a metadata filter both demonstrated.
- [ ] You can state the `k` trade-off from memory.

## Pitfalls

- **Query embedded with a different model than the corpus** — garbage results.
- **Wrong distance space** (L2 vs cosine) — set it explicitly on the collection.
- **Re-indexing without clearing** — duplicate ids or stale chunks.

## Carries to next session

Retrieval works in isolation. Session 4 wires it to generation: retrieved chunks
→ prompt → cited answer.
