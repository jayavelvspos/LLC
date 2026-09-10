# Session 2 — Chunking & Loading (~45 min)

**Objective:** split real documents into retrievable chunks with useful
metadata, and understand how chunk size and overlap change what retrieval can
find.

**Prerequisites:** Session 1 complete. Put 5–15 documents (markdown, text, or
PDF) in `corpus/`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why chunk at all; size vs overlap trade-offs |
| 10–30 | `code/chunk.py` — load `corpus/`, split, attach metadata |
| 30–40 | Compare 3 chunk sizes on the same doc; eyeball the chunks |
| 40–45 | Notes |

---

## Concepts

- You retrieve **chunks**, not whole documents — the chunk is the unit that gets
  embedded, matched, and stuffed into the prompt.
- **Chunk size:** too small → a chunk lacks enough context to answer; too large
  → one chunk covers many topics, dilutes the embedding, wastes prompt space.
  Typical starting point: 300–800 tokens.
- **Overlap:** repeat the last ~10–20% of a chunk at the start of the next so a
  fact split across a boundary still appears whole somewhere.
- **Split on structure first** (headings, paragraphs), then by size — don't cut
  mid-sentence if avoidable. `RecursiveCharacterTextSplitter` does this.
- **Metadata per chunk:** source filename, section/heading, position, maybe a
  date. You'll filter and cite with it later.
- **Loading ≠ chunking.** *Loaders* turn a file (PDF, HTML, `.docx`, a URL, a
  Notion export) into raw `Document` objects with `page_content` + `metadata`;
  *splitters* then cut those into chunks. LangChain's `langchain_community`
  loaders (`DirectoryLoader`, `PyPDFLoader`, `WebBaseLoader`,
  `UnstructuredMarkdownLoader`) save you writing a parser per format — the
  splitter and everything downstream stays the same.
- **Token vs character splitting.** `RecursiveCharacterTextSplitter` counts
  characters by default; `.from_tiktoken_encoder(...)` or
  `SentenceTransformersTokenTextSplitter` count *tokens*, which is what your
  embedding model and prompt budget actually care about.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Contextual Retrieval* (why naive chunking loses context, and a
  fix): <https://www.anthropic.com/news/contextual-retrieval>.
- LangChain docs — *Text splitters* (`RecursiveCharacterTextSplitter`,
  token-based splitters):
  <https://python.langchain.com/docs/concepts/text_splitters/>.
- LangChain docs — *Document loaders* (`DirectoryLoader`, `PyPDFLoader`,
  `WebBaseLoader`): <https://python.langchain.com/docs/concepts/document_loaders/>.

**Video (pick one, ~10–20 min):**
- Search *"RAG chunking strategies explained"* — focus on size/overlap effects.

---

## Track_B link (step 3)

**None.** Chunking is text processing. Note "no Track_B link" and continue.
(Your Track_B decision from Session 1 still stands — if you flagged a revisit,
it's still on the backlog.)

---

## Worked example — split and inspect

`code/chunk.py`:

```python
from pathlib import Path
from langchain_text_splitters import RecursiveCharacterTextSplitter

def load_and_chunk(corpus="corpus", size=600, overlap=100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=size, chunk_overlap=overlap,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "])
    chunks = []
    for path in Path(corpus).glob("**/*.md"):
        text = path.read_text(encoding="utf-8")
        for i, piece in enumerate(splitter.split_text(text)):
            chunks.append({"text": piece,
                           "meta": {"source": path.name, "chunk": i}})
    return chunks

cs = load_and_chunk()
print(f"{len(cs)} chunks")
for c in cs[:2]:
    print("---", c["meta"], "\n", c["text"][:200], "...")
```

**Expected output** (shape):

```
84 chunks
--- {'source': 'onboarding.md', 'chunk': 0}
 # Onboarding guide  New hires should complete the following in week one ...
--- {'source': 'onboarding.md', 'chunk': 1}
 ... complete in week one. Step 3: set up your dev environment by running ...
```

Note the overlap: the end of chunk 0 ("complete ... in week one") reappears at
the start of chunk 1.

### Same thing, via LangChain loaders

Once `corpus/` has more than markdown (PDFs, HTML), swap the hand-rolled file
walk for a loader and split the loaded `Document`s directly — metadata like
`source` and `page` comes attached:

```python
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

docs = DirectoryLoader("corpus", glob="**/*.pdf", loader_cls=PyPDFLoader).load()
splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
    chunk_size=600, chunk_overlap=100)
chunks = splitter.split_documents(docs)          # -> list[Document], metadata preserved
print(len(chunks), chunks[0].metadata)           # {'source': 'corpus/handbook.pdf', 'page': 0}
```

`split_documents` (not `split_text`) keeps each chunk's `metadata` — you get
`source` and `page` for free, which is what you'll cite from in Session 4.

---

## Build

- Build `chunk.py`; run it on `corpus/`.
- Run with `size` = 200, 600, 1500 (same overlap ratio). Read 3 chunks from each.
  Which size would let you answer a specific question from your corpus? Write the
  observation.
- Set `overlap=0`, find a fact that sits near a boundary, and show it gets
  split. Restore overlap; show it's whole again.
- Add a `section` field to metadata by tracking the last seen `## ` heading.
- Add one non-markdown file to `corpus/` (a PDF or an HTML page). Load it with
  the matching LangChain loader and confirm `split_documents` carries `source`
  (and `page` for PDFs) onto every chunk.
- Re-run with `.from_tiktoken_encoder(chunk_size=600, ...)` and compare the
  chunk count to the character-based split — same `chunk_size` number, different
  actual chunk lengths, because tokens ≠ characters.

---

## Quick test (step 7 — answer from memory, then check)

1. What is the unit of retrieval, and why not whole documents?
2. What goes wrong with chunks that are too small? Too large?
3. What is overlap for?
4. What should you split on before falling back to raw size?
5. Name three useful pieces of chunk metadata.

<details><summary>Answers</summary>

1. The chunk — it's what gets embedded, matched, and put in the prompt. Whole
   docs are too big and too topically mixed to embed or fit well.
2. Too small: not enough context to answer. Too large: mixed topics dilute the
   embedding and waste prompt space.
3. So a fact split across a chunk boundary still appears intact in at least one
   chunk.
4. Document structure — headings, then paragraphs, then sentences — before
   cutting purely by character/token count.
5. Any three: source filename, section/heading, chunk index/position, date,
   author.

</details>

---

## Done when

- [ ] `chunk.py` produces chunks with `source` + position metadata.
- [ ] You've compared 3 chunk sizes and written which fits your corpus.
- [ ] You've demonstrated a boundary-split fact and fixed it with overlap.
- [ ] You can state the size and overlap trade-offs from memory.

## Pitfalls

- **One giant chunk per document** — retrieval can't localize the answer.
- **Cutting mid-sentence / mid-table** — hurts both embedding and readability.
- **No source metadata** — you can't cite or filter later.

## Carries to next session

Chunks with metadata, ready to embed. Session 3 puts them in a vector store and
queries it.
