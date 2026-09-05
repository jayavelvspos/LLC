# Session 1 — Embeddings as an API (~45 min)

**Objective:** turn text into vectors with an embeddings API, and confirm by
hand that related text lands closer together than unrelated text.

**Prerequisites:** Stage 3 complete. An embeddings API key (Voyage AI, Cohere,
OpenAI) or `pip install sentence-transformers` for a local model.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What an embedding is (black-box view): text → fixed-length vector |
| 10–25 | `code/embed.py` — embed a batch, print shapes |
| 25–40 | Cosine similarity by hand; rank a query against candidates |
| 40–45 | Notes — **and decide on the Track_B switch** |

---

## Concepts

- An **embedding model** maps text to a fixed-length vector (e.g. 1024 floats)
  such that semantically similar text → vectors pointing in similar directions.
- **Similarity** is usually **cosine similarity**: the cosine of the angle
  between two vectors. `1.0` = same direction, `0` = unrelated (orthogonal),
  `-1` = opposite. `cos(a,b) = (a·b) / (|a| |b|)`.
- Many APIs return **normalized** vectors (`|v| = 1`), so cosine similarity
  reduces to the dot product `a·b`.
- Black-box rule for now: call the API, get vectors, compare with cosine. You do
  **not** need to know how the model was trained. You **do** need cosine to make
  sense — that's the Track_B footing.
- Batch your calls (embed many texts per request); cache vectors (they don't
  change).

---

## Learning resources

**Primary (official, stable):**
- Voyage AI docs — *Embeddings quickstart* (Anthropic's recommended provider):
  <https://docs.voyageai.com/docs/embeddings>.
- Anthropic docs — *Embeddings* (why there's no first-party endpoint; provider
  guidance): <https://docs.anthropic.com/en/docs/build-with-claude/embeddings>.
- `sentence-transformers` docs (for a free local option):
  <https://www.sbert.net/>.

**Video (pick one, ~15–25 min):**
- Search *"what are embeddings vector explained"* — a visual on the
  "similar meaning → nearby vector" idea. **3Blue1Brown**'s dot-product /
  vectors material is the best companion to the Track_B topic.

---

## Track_B link (step 3) — **possible switch point**

Cosine similarity is `Track_B/Math_stat/01_linear_algebra` (dot product, vector
norm, angle between vectors). **Decide now:**

- If, after the worked example, the cosine numbers feel arbitrary — you can't
  say *why* 0.82 means "related" and 0.11 means "not" — **switch** to
  `Track_B/Math_stat/01_linear_algebra`, learn dot product + norm + cosine
  (20–30 min), then come back to step 4.
- If it already clicks, note *"revisit in Track_B: formal cosine similarity"*
  and continue. You'll get another chance to switch at Session 5.

---

## Worked example — rank candidates by similarity

`code/embed.py`:

```python
import numpy as np
# from voyageai import Client;  emb = Client().embed(texts, model="voyage-3").embeddings
# or: from sentence_transformers import SentenceTransformer; emb = model.encode(texts)

def cosine(a, b):
    a, b = np.asarray(a), np.asarray(b)
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b)))

query = "How do I reset my password?"
candidates = [
    "To change your password, open Settings > Security.",
    "Our refund policy allows returns within 30 days.",
    "Forgot your login? Use the 'reset credentials' link on the sign-in page.",
    "The office is closed on public holidays.",
]
vecs = embed([query] + candidates)          # your API call
qv, cvs = vecs[0], vecs[1:]
for text, cv in sorted(zip(candidates, cvs), key=lambda p: -cosine(qv, p[1])):
    print(f"{cosine(qv, cv):.3f}  {text}")
```

**Expected output** (values approximate; **order** is the point):

```
0.71  Forgot your login? Use the 'reset credentials' link on the sign-in page.
0.68  To change your password, open Settings > Security.
0.19  The office is closed on public holidays.
0.12  Our refund policy allows returns within 30 days.
```

Read it: the two password-related sentences rank top by a wide margin, despite
sharing few exact words with the query ("reset credentials" ≠ "reset my
password"). That semantic match — not keyword overlap — is what retrieval will
lean on.

---

## Build

- Build `embed.py` with `embed()` and `cosine()`.
- Add a near-duplicate pair and an unrelated sentence; predict the similarity
  ranking before running.
- Embed the **same** sentence twice → similarity should be ~1.0 (sanity check
  your pipeline).
- Try a query in different phrasing ("change password" vs "password reset" vs
  "I can't log in") → note how stable the top result is.
- Check whether your provider returns normalized vectors (`np.linalg.norm(v)` ≈
  1?). Note it.

---

## Quick test (step 7 — answer from memory, then check)

1. What does an embedding model produce, and what property does it have?
2. Write the cosine similarity formula.
3. What do cosine values of 1, 0, and -1 mean?
4. When does cosine similarity reduce to a dot product?
5. Why can retrieval match text that shares no keywords with the query?

<details><summary>Answers</summary>

1. A fixed-length vector per text, where semantically similar texts get vectors
   pointing in similar directions.
2. `cos(a,b) = (a · b) / (|a| · |b|)`.
3. `1` = same direction (very similar), `0` = orthogonal (unrelated), `-1` =
   opposite.
4. When the vectors are normalized (`|a| = |b| = 1`).
5. Similarity is computed on meaning-space vectors, not surface tokens; related
   concepts land near each other regardless of wording.

</details>

---

## Done when

- [ ] `embed.py` ranks candidates by cosine similarity, sensibly.
- [ ] Identical text scores ~1.0.
- [ ] You made and checked a similarity-ranking prediction.
- [ ] You've made the Track_B decision (switched, or logged a revisit) — and it's
      in `notes.md`.

## Pitfalls

- **Mixing embedding models** — vectors from different models aren't comparable.
  One model for the whole corpus + queries.
- **Not batching** — one API call per text is slow and costly.
- **Forgetting to normalize** when your similarity code assumes it.

## Carries to next session

You can turn text into comparable vectors. Session 2 prepares real documents —
splitting them into chunks worth embedding.
