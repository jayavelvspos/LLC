# NLP Foundations

A hands-on learning workspace, following the same pattern as `../Math_stat/`.
Scaffolded 2026-09-10 — **folder structure and topic map only, `notes.md` /
`exercises.py` content not yet written.** Pulled in when Track_A's RAG (Stage
4) or `Stage_4B_Classical_ML_DL_FineTuning/` sessions need it (just-in-time,
per `../CLAUDE.md`), or on request.

## Folder map

| Folder | Topics | Why it matters for AI/ML engineering |
|---|---|---|
| `01_text_preprocessing` | Tokenization, Lemmatization, Stemming, Stop Words, N-Grams | the first thing every NLP pipeline does to raw text |
| `02_classical_text_representation` | Bag of Words, Count Vectorizer, TF-IDF | text as numbers, before embeddings existed — still used for baselines and sparse retrieval |
| `03_pos_and_ner` | POS Tagging, Named Entity Recognition | structured extraction from unstructured text |
| `04_embeddings_and_similarity` | Word Embeddings, Vector Embeddings, Word2Vec / GloVe, Cosine Similarity | the bridge from text to the vector-space math in `../Math_stat/01_linear_algebra` |
| `05_attention_transformers_llms` | Attention Mechanism, Self-Attention, Transformers, Encoder-Decoder, Language Models, LLMs | how a modern LLM actually processes a sequence |

## How to use each folder (once content exists)

1. Read `notes.md` first — intuition and formulas, kept short.
2. Run `exercises.py` (`py 01_text_preprocessing\exercises.py`) — worked
   examples with real numbers/text, dependency-free where the concept allows
   it (e.g. a from-scratch tokenizer, TF-IDF, or bag-of-words).
3. Do the `TODO` functions yourself before reading the `# solution` comment.
   Re-run — it self-checks with `assert`.
4. Move to the next folder in order (01 -> 05).

## Where this connects

- **Forward to Track_A:** Stage 4 (RAG) uses embeddings/retrieval as an API
  black box first; this folder is where the black box gets opened. Stage 4B
  session 5 (Hugging Face) uses tokenizers and pipelines built on these ideas.
- **Back to `Math_stat`:** `04_embeddings_and_similarity` is the direct
  companion to `01_linear_algebra` (cosine similarity, vector space).
