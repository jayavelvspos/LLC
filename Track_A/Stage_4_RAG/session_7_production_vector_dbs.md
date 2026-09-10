# Session 7 — Production Vector DBs: pgvector & Qdrant (~45 min)

**Objective:** move the corpus out of an in-process index (Chroma/FAISS) into a
real vector database — **pgvector** or **Qdrant** — with server-side metadata
filtering, and understand what that buys you and what it costs.

**Prerequisites:** Session 3 (`store.py`) and Session 4 (`rag.py`) complete.
Docker installed (both options run in a container).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 6's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | In-process vs server vector DB; what a real DB adds |
| 10–30 | `code/store_qdrant.py` (or `store_pg.py`) — same interface as `store.py`, backed by a container |
| 30–40 | Point `rag.py` at it; add a metadata filter; restart the process |
| 40–45 | Notes — measure recall/latency at two `ef` settings |

---

## Concepts  <!-- step 2 -->

- **In-process (Chroma, FAISS)** lives in your Python process: great for
  building and tests, but no concurrent clients, no durability guarantees, and
  filtering happens *after* the vector search in Python.
- **Server DB (pgvector, Qdrant)** is a separate process you talk to over the
  network: survives restarts, serves many clients, and pushes **filtering into
  the query** so a filtered search still returns a full top-k.

| | pgvector | Qdrant |
|---|---|---|
| What it is | a Postgres extension | a purpose-built vector DB |
| Store | a `vector(1024)` column in a normal table | a *collection* of *points* (`id` + `vector` + `payload`) |
| Similarity | `<=>` (cosine distance) operator in SQL | metric set on the collection; `search()` API |
| ANN index | `CREATE INDEX ... USING hnsw (embedding vector_cosine_ops)` | HNSW, built automatically |
| Filtering | `WHERE` clause (SQL) | `Filter(must=[FieldCondition(...)])` |
| You also get | joins, transactions, everything SQL | native hybrid search, quantization, payload indexes |
| Run it | `docker run ... pgvector/pgvector:pg16` | `docker run -p 6333:6333 -v $(pwd)/qdrant_storage:/qdrant/storage qdrant/qdrant` |

- **HNSW knobs (both):** `m` and `ef_construct` at build time, `ef` (Qdrant) /
  `hnsw.ef_search` (pgvector) at query time. Higher `ef` → better recall, higher
  latency. This is a **recall vs latency** dial, tuned empirically.
- **Pre-filter vs post-filter:** pre-filter (restrict the candidate set, *then*
  search — Qdrant, pgvector `WHERE`) always returns up to k results. Post-filter
  (search, then drop non-matching hits — the in-process pattern) can return
  fewer than k, or none.
- **Hybrid search:** fuse dense (embedding) results with sparse
  (BM25 / SPLADE keyword) results via **Reciprocal Rank Fusion**. Qdrant does
  this natively; in pgvector you add a `tsvector` column and fuse in SQL.
  Helps rare terms, codes, and names that dense retrieval blurs. (You'll lean
  on this in Session 8.)

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- pgvector README — indexing, operators, `hnsw`:
  <https://github.com/pgvector/pgvector>.
- Qdrant docs — *Quickstart* and *Filtering*:
  <https://qdrant.tech/documentation/concepts/filtering/>.
- LangChain docs — `PGVector` and `QdrantVectorStore` integrations (if you go
  through LangChain rather than the raw clients).

**Video (pick one, ~15–25 min):**
- Search *"pgvector tutorial postgres"* or *"Qdrant crash course"* — focus on
  collection/table setup, the ANN index, and a filtered query.

**Reference:**
- `qdrant-client` Python SDK README; `psycopg` + pgvector Python usage.

---

## Track_B link (step 3)

**Light, non-blocking.** The ANN index (HNSW) is graph-based nearest-neighbour
search, and the `ef`/recall/latency relationship is empirical — you tune it by
measuring, not by deriving it. The distance metric itself is the same cosine
footing from Session 1. Note *"revisit in Track_B: approximate nearest neighbour
— HNSW, recall@k vs exact search"* and continue.

---

## Worked example — same query, in-process vs Qdrant with a filter  <!-- step 4 -->

`code/vdb_demo.py`:

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from embed import embed            # session 1

client = QdrantClient(url="http://localhost:6333")
DIM = 1024

client.recreate_collection("corpus",
    vectors_config=VectorParams(size=DIM, distance=Distance.COSINE))

# upsert the chunks you already built in session 2/3
chunks = load_chunks()             # [{"text": ..., "meta": {"source": ...}}, ...]
vecs = embed([c["text"] for c in chunks])
client.upsert("corpus", [
    PointStruct(id=i, vector=v, payload=c["meta"] | {"text": c["text"]})
    for i, (c, v) in enumerate(zip(chunks, vecs))
])

q = "how do I reset my password?"
qv = embed([q])[0]

print("no filter:")
for h in client.query_points("corpus", query=qv, limit=3).points:
    print(f"  {h.score:.3f}  {h.payload['source']}")

print("filter source == 'faq.md':")
flt = Filter(must=[FieldCondition(key="source", match=MatchValue(value="faq.md"))])
for h in client.query_points("corpus", query=qv, query_filter=flt, limit=3).points:
    print(f"  {h.score:.3f}  {h.payload['source']}")
```

**Expected output** (scores vary; the behaviour is the point):

```
no filter:
  0.71  faq.md
  0.68  settings.md
  0.19  holidays.md
no filter:                         <- process restarted here, data still there
filter source == 'faq.md':
  0.71  faq.md
  0.55  faq.md
  0.41  faq.md
```

Read it: the collection **survived a process restart** (FAISS in-memory would
not), and the filter is applied *inside* the DB so you still get a full 3 hits —
all now from `faq.md`.

---

## Build: `code/store_qdrant.py` (or `code/store_pg.py`)  <!-- step 5 -->

Re-implement `store.py`'s interface — `add(chunks)` and `search(query, k, filter=None)`
— backed by a container. Keep the signatures identical so `rag.py` doesn't care
which store it's talking to; select via an env var (`STORE=qdrant|chroma`).

Experiments:
1. **Durability.** Add the corpus, kill the Python process, start it again, run a
   query. Qdrant/pgvector: still there. Point `rag.py` at in-memory FAISS and
   repeat: gone.
2. **Server-side filter.** Add a `source` (or `section`) filter to `search`.
   Take a question that pulled an off-topic chunk in Session 5 and show the
   filter removes it — with top-k still full.
3. **Recall vs latency.** Run your Session 6 eval questions at a low `ef`
   (e.g. 16) and a high one (e.g. 256). Record hit-rate and median latency at
   each. Which would you ship?

---

## Quick test (step 7 — answer from memory, then check)

1. Name two things a server vector DB gives you that an in-process index doesn't.
2. In pgvector, what does `<=>` compute, and what index do you create to make it
   fast?
3. In Qdrant, what are the three parts of a *point*?
4. Pre-filter vs post-filter: which can return fewer than k results, and which
   avoids that?
5. What does hybrid search fuse, and with what algorithm?

<details><summary>Answers</summary>

1. Any two: durability across restarts, concurrent clients, filtering pushed
   into the query (full top-k after filtering), horizontal scale, payload
   indexes, native hybrid search.
2. Cosine **distance** between two vectors; a `USING hnsw (... vector_cosine_ops)`
   index (an IVFFlat index is the other option).
3. An `id`, a `vector`, and a `payload` (the metadata + stored text).
4. Post-filter can return fewer than k (it drops hits after the search).
   Pre-filter restricts the candidate set first, so it still fills k.
5. Dense (embedding) results and sparse (BM25 / keyword) results, fused with
   Reciprocal Rank Fusion.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `rag.py` answers questions against Qdrant or pgvector running in Docker.
- [ ] A metadata filter, applied server-side, demonstrably changes the retrieved
      chunks — with top-k still full.
- [ ] The index survives a Python process restart (shown, not assumed).
- [ ] You can explain the `ef` / recall / latency tradeoff from your own two
      measurements.

## Pitfalls

- **Dimension mismatch** — the column / collection dimension must equal your
  embedding model's output. A silent mismatch = errors on insert or garbage
  scores.
- **No ANN index** — pgvector will happily sequential-scan every row. Create the
  `hnsw` index and `ANALYZE`.
- **Qdrant without a volume mount** — `docker run` with no `-v` loses the
  collection when the container stops.
- **Post-filtering a small top-k** — filter after retrieving 5 and you may get
  0. Pre-filter, or retrieve more.

## Carries to next session

A production-grade store with real filtering. Session 8 layers advanced
retrieval — query transformation, hybrid search, rank fusion — on top of it, and
measures each against the eval set.
