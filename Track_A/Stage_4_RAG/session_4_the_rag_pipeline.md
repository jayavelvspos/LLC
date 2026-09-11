# Session 4 — The RAG Pipeline (~45 min)

**Objective:** connect retrieval to generation — retrieve top-k chunks, put them
in the prompt, and get an answer that cites which chunks it used.

**What you'll learn:**
- The retrieve -> augment -> generate shape
- Grounding prompt design: numbered context, "answer only from context," citations
- Prompt-engineered citations vs. Anthropic's Citations feature
- Why a refusal to answer beats a confident hallucination

**Prerequisites:** Session 3 complete (`store.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The retrieve → augment → generate shape; grounding prompt design |
| 10–35 | `code/rag.py` — end-to-end `answer(question)` with citations |
| 35–43 | Test on questions that are / aren't answerable from the corpus |
| 43–45 | Notes |

---

## Concepts

- **RAG = retrieve, augment, generate.** Retrieve k chunks for the question,
  paste them into the prompt as labelled context, ask the model to answer
  **using only that context** and cite the chunk ids it used.
- **Grounding prompt** essentials: number/id each chunk; instruct "answer only
  from the context; if the context doesn't contain the answer, say so"; require
  citations like `[onboarding.md#1]`.
- **Two provider paths for citations:** (a) prompt-engineered — you ask for
  `[id]` markers and parse them; (b) Anthropic's **Citations** feature — pass
  each chunk as a `document` content block with `citations: {enabled: true}` and
  the response comes back split into cited spans with exact source locations.
  Start with (a), try (b).
- **Refusal to answer is a feature.** "The provided documents don't cover this"
  beats a confident hallucination.
- This is a function first (`answer(q) -> {text, citations}`); wrapping it as a
  LangGraph tool/node is a small later step.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Citations* (document blocks, `citations: {enabled: true}`,
  cited-span response shape):
  <https://docs.anthropic.com/en/docs/build-with-claude/citations>.
- Anthropic Cookbook — RAG notebooks (`skills/retrieval_augmented_generation/`
  or `third_party/`): <https://github.com/anthropics/anthropic-cookbook>.
- Anthropic — *Contextual Retrieval* (prompt + retrieval quality):
  <https://www.anthropic.com/news/contextual-retrieval>.

**Video (pick one, ~15–25 min):**
- Search *"build RAG from scratch python"* — focus on the prompt assembly step.

---

## Track_B link (step 3)

**None** for the pipeline wiring. Note "no Track_B link" and continue. (The
diagnostic Track_B work comes in Session 5.)

---

## Worked example — `answer()` with parsed citations

`code/rag.py`:

```python
import re
from anthropic import Anthropic
from store import search

client = Anthropic()
SYSTEM = ("Answer the question using ONLY the numbered context. "
          "Cite sources inline as [source#chunk]. "
          "If the context does not contain the answer, reply exactly: "
          "\"Not covered by the provided documents.\"")

def answer(question: str, k: int = 5) -> dict:
    hits = search(question, k=k)
    context = "\n\n".join(f"[{m['source']}#{m['chunk']}] {doc}"
                          for doc, m, _ in hits)
    resp = client.messages.create(
        model="claude-opus-5", max_tokens=800, system=SYSTEM,
        messages=[{"role": "user",
                   "content": f"Context:\n{context}\n\nQuestion: {question}"}])
    text = resp.content[0].text
    cited = sorted(set(re.findall(r"\[([\w.\-]+#\d+)\]", text)))
    return {"text": text, "citations": cited,
            "retrieved": [f"{m['source']}#{m['chunk']}" for _, m, _ in hits]}

if __name__ == "__main__":
    import sys
    r = answer(" ".join(sys.argv[1:]))
    print(r["text"], "\n\ncited:", r["citations"], "\nretrieved:", r["retrieved"])
```

**Expected output** (answerable question):

```
Run `make dev-setup` from the repo root, then start the services with
`docker compose up`. [onboarding.md#1]

cited: ['onboarding.md#1']
retrieved: ['onboarding.md#1', 'onboarding.md#2', 'security.md#4', ...]
```

And for an out-of-corpus question:

```
Not covered by the provided documents.
```

---

## Build

- Build `rag.py`. Test 6 questions: 4 answerable, 2 not. Confirm the 2
  unanswerable ones get the refusal line, not a guess.
- Compare `k = 3` vs `k = 8` on the same question — does the answer change? do
  citations change?
- Swap the parsed-citation approach for Anthropic **Citations** (document
  blocks) on one question; compare the precision of the cited spans.
- Log `retrieved` vs `citations` — when the model cites only 1 of 5 retrieved
  chunks, the other 4 were prompt bloat. Note the cost angle.

---

## Quick test (step 7 — answer from memory, then check)

1. Spell out RAG's three steps.
2. Name three things the grounding prompt must do.
3. Why is "I can't answer from these docs" a good outcome?
4. Two ways to produce citations with Claude.
5. What does it tell you when only 1 of `k` retrieved chunks is cited?

<details><summary>Answers</summary>

1. Retrieve relevant chunks; augment the prompt with them as context; generate
   an answer constrained to that context.
2. Any three: label/id each chunk; restrict the answer to the context; require
   inline citations; define an explicit "not covered" response.
3. It prevents confident hallucination when the corpus genuinely lacks the
   answer — a wrong answer is worse than an honest gap.
4. Prompt-engineered `[id]` markers you parse; or Anthropic's Citations feature
   with `document` blocks and `citations: {enabled: true}`.
5. The other retrieved chunks were noise/bloat for that question — a signal to
   lower `k` or improve retrieval precision.

</details>

---

## Done when

- [ ] `rag.py` answers corpus questions with citations and refuses
      out-of-corpus ones.
- [ ] You've compared two `k` values and noted the effect.
- [ ] You've tried Anthropic Citations on at least one question.
- [ ] You can recite RAG's three steps.

## Pitfalls

- **No "not covered" instruction** → the model fills gaps with training-data
  guesses.
- **Unlabelled context** → the model can't cite precisely.
- **Huge `k`** → cost and latency up, often with no accuracy gain.

## Carries to next session

The pipeline works — until retrieval returns the wrong chunks. Session 5 is
about diagnosing and fixing that, and is the likely Track_B deep-dive point.
