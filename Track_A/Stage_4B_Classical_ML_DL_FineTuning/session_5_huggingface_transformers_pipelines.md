# Session 5 — Hugging Face `transformers` Pipelines (~45 min)

**Objective:** solve three real NLP tasks — classification, named entity
recognition, and summarization — on real text using pretrained Hugging Face
pipelines, and understand what a `pipeline()` call is doing under the hood
(tokenize -> model -> decode).

**What you'll learn:**
- What `pipeline()` wraps: tokenize -> model -> decode
- Pretrained models and the Hugging Face Hub
- Model choice as a latency/cost/accuracy tradeoff
- Task-specific output shapes (classification, NER, summarization)
- Truncation and max input length

**Prerequisites:** Sessions 1-4 complete. `pip install transformers`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 4's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–15 | Pipelines: tokenize -> model -> decode; the model hub; task-specific pipelines |
| 15–35 | Build `code/hf_pipelines.py` |
| 35–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **`pipeline()`** is Hugging Face's high-level API: give it a task name
  (`"sentiment-analysis"`, `"ner"`, `"summarization"`, ...) and, optionally,
  a specific model; it downloads a pretrained model + its matching
  **tokenizer**, and wraps tokenize -> model forward pass -> decode into one
  callable.
- **Tokenization, concretely.** The tokenizer splits text into subword
  tokens and maps each to an integer id the model was trained on (this is
  the black box `count_tokens` used back in Stage 0, now visible: call
  `tokenizer.tokenize("...")` yourself and see the pieces).
- **Pretrained models.** Every model behind these pipelines was already
  trained (often fine-tuned for the specific task) by someone else and
  published on the Hugging Face Hub. You're not training anything this
  session — you're using a network someone else already built, the same way
  Stage 4's embeddings were an API you called, not trained.
- **Model choice = a latency/cost/accuracy tradeoff**, same shape as Stage
  0's model-pricing tradeoff: a small model (`distilbert-base-...`) runs
  fast on CPU with a small accuracy cost vs. a larger model.
- **Task-specific output shapes.** Each pipeline task returns a different
  structure: sentiment-analysis returns a label + confidence score per
  input; NER returns a list of `{entity, word, score, start, end}` spans;
  summarization returns generated text, not a classification — read the
  output shape before assuming what a `dict`/`list` contains.
- **Truncation & max length.** Every model has a fixed maximum input length
  (in tokens, not characters). Text longer than that gets truncated (or
  errors) unless you handle it — relevant the moment you feed it a real
  support-ticket thread instead of one short sentence.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Hugging Face docs — *Pipelines for inference*:
  <https://huggingface.co/docs/transformers/pipeline_tutorial>.

**Video (pick one, ~15 min):**
- Search *"Hugging Face pipeline tutorial transformers"* — a quick tour of
  `pipeline()` across a few task types.

---

## Track_B link (step 3)

**Can block.** If "what is the model actually doing with a token id" or
"what is attention" is still a black box, switch to
`Track_B/NLP/01_text_preprocessing` and `05_attention_transformers_llms`
now — this session uses those models without opening them, which is fine
for using pipelines, but you should know what you're choosing not to look
at yet.

---

## Worked example — three tasks, one text corpus  <!-- step 4 -->

```python
from transformers import pipeline

tickets = [
    "I was charged twice this month, $49.99 both times, please refund me.",
    "The export button does nothing on Safari, using macOS Sonoma.",
    "Contacted by John Smith from Acme Corp about a billing dispute on invoice #4471.",
]

classifier = pipeline("sentiment-analysis")
for t in tickets:
    print(classifier(t))

ner = pipeline("ner", grouped_entities=True)
print(ner(tickets[2]))

summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
long_thread = (
    "Customer reports being charged twice for their subscription this month. "
    "Support confirmed a duplicate transaction on the 3rd and 5th of the month "
    "for $49.99 each. Customer requests a refund of the duplicate charge and "
    "asks for confirmation once processed. Support has escalated to billing."
)
print(summarizer(long_thread, max_length=30, min_length=10))
```

**Expected output** (exact scores/wording vary by model/version):

```
[{'label': 'NEGATIVE', 'score': 0.998}]
[{'label': 'NEGATIVE', 'score': 0.972}]
[{'label': 'NEUTRAL', 'score': 0.51}]   # or similar — sentiment models vary on neutral text

[{'entity_group': 'PER', 'word': 'John Smith', 'score': 0.99, ...},
 {'entity_group': 'ORG', 'word': 'Acme Corp', 'score': 0.98, ...}]

[{'summary_text': 'Customer was charged twice this month and wants a refund...'}]
```

Read it: the same three-line pattern (`pipeline(task)` then call it) solved
three structurally different problems. Compare this to Stage 1B Session 1's
hand-written `score_refund` regex/keyword scorer on similar text — the
pretrained model generalizes to phrasing you didn't anticipate; the
hand-written rule doesn't, but is free and instant. That tradeoff is the
throughline of this whole stage.

---

## Build: `code/hf_pipelines.py`  <!-- step 5 -->

Build the three-pipeline script above using your own set of 8-10 sample
texts (reuse or extend Stage 1B Session 1's support-ticket batch if you
still have it). Print, for each: which pipeline you ran, the raw output, and
one sentence on whether the result looks right to you.

Experiments:
1. **Time it.** Wrap each `pipeline(...)` construction and each call in
   `time.perf_counter()`. Note that pipeline *construction* (model download
   + load) is far slower than a single inference call — a real system loads
   the pipeline once at startup, not per-request.
2. **Force truncation.** Feed the summarizer a very long piece of text (a
   few thousand words — paste an article) without adjusting anything, and
   read whatever warning/behavior appears about truncation.
3. **Swap the model.** Pass a different `model=` to the sentiment pipeline
   (search the Hugging Face Hub for another `text-classification` model) and
   compare outputs on the same inputs.

---

## Quick test (step 7 — answer from memory, then check)

1. What three steps does `pipeline()` wrap into one callable?
2. What determines whether a pipeline call is fast or slow, beyond the
   input text itself?
3. Why might a summarization pipeline's output differ in *shape* from a
   sentiment-analysis pipeline's output?
4. What happens to text longer than a model's max input length if you don't
   handle it yourself?
5. Compare a Hugging Face sentiment pipeline to Stage 1B's hand-written
   `score_refund` scorer — what does each trade off against the other?

<details><summary>Answers</summary>

1. Tokenize the input, run it through the model's forward pass, decode the
   model's output into a human-readable result.
2. Which model you chose (size), whether it's already loaded (construction
   cost vs. per-call cost), and hardware (CPU vs. GPU).
3. Different tasks have different natural outputs — a classification task
   returns a label/score; a generative task (summarization) produces new
   text, not a category, so the output is a text string, not a class.
4. It gets truncated (or the call errors, depending on the pipeline/model) —
   the model literally never sees the truncated part.
5. The pretrained pipeline costs more (compute, dependency weight, possibly
   latency) but generalizes to phrasing/structure you didn't anticipate. The
   hand-written scorer is free and instant but only covers what you
   explicitly wrote rules for.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `hf_pipelines.py` runs classification, NER, and summarization on a
      real batch of your own text.
- [ ] You've measured that pipeline construction is far slower than a
      single call, and can explain why that matters for a real service.
- [ ] You've compared a Hugging Face pipeline's behavior against Stage 1B's
      hand-written scorer on similar input.
- [ ] You can name the three internal steps of `pipeline()` from memory.

## Pitfalls

- **Constructing a pipeline inside a request-handling loop.** Load it once,
  reuse it — this becomes directly relevant in Stage 6B's FastAPI service.
- **Assuming every pipeline's output has the same shape.** Check the actual
  return type/keys for the task you're using; don't copy-paste code across
  task types without checking.
- **Ignoring truncation warnings.** A silently truncated input produces a
  confidently wrong-looking result with no obvious error.

## Carries to next session

Session 6 takes one of these pretrained models and **changes its weights**
for a narrow task via PEFT/LoRA fine-tuning — the first time in this stage
you train something starting from a pretrained checkpoint instead of from
scratch (Session 4) or not at all (this session).
