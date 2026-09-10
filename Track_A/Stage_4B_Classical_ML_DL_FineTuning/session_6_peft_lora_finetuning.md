# Session 6 — PEFT Fine-Tuning (LoRA) vs. RAG & Prompting (~45 min)

**Objective:** fine-tune a small pretrained model with LoRA on a narrow
classification task, then measure — with real numbers, not vibes — how it
compares to zero-shot prompting a general model on the same task, and where
it sits relative to Stage 4's RAG approach.

**Prerequisites:** Sessions 1-5 complete. Stage 4 (RAG) complete, for the
comparison. `pip install peft`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 5's Quick test. This session may run long — let it; don't cut the
comparison short.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Transfer learning, full fine-tuning vs. PEFT, what LoRA actually does |
| 10–30 | Build `code/lora_finetune.py` — fine-tune + evaluate |
| 30–40 | Head-to-head vs. prompting (and vs. RAG, by reasoning) |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Transfer learning.** Start from a model already trained on a large,
  general task (here: a language model that already understands English
  text) instead of training from random weights (Session 4). You're
  transferring its general knowledge to your narrow task.
- **Full fine-tuning** updates *every* weight in the pretrained model. For
  even a "small" model (tens of millions of parameters), that means storing
  gradients and optimizer state for all of them — expensive in memory and
  slow, and every fine-tuned version is a full copy of the model.
- **PEFT (Parameter-Efficient Fine-Tuning) / LoRA.** Freeze the entire
  pretrained model. Inject small trainable "adapter" matrices alongside
  specific layers (commonly the attention projections). Concretely: instead
  of learning a full update `ΔW` to a weight matrix `W`, LoRA learns two
  much smaller matrices `A` and `B` such that `ΔW ≈ B·A` — a low-rank
  approximation of the update, controlled by a rank `r` (e.g. 8) you choose.
  Only `A` and `B` train; `W` never changes. Result: **a tiny fraction of
  the parameters** (often <1%) are trainable, training is far cheaper, and
  the "fine-tuned model" is really the frozen base plus a small adapter file
  you can swap in and out.
- **QLoRA** (name-level today): LoRA combined with a **quantized** (e.g.
  4-bit) frozen base model, cutting memory further — how people fine-tune
  genuinely large models on a single consumer GPU. Not needed for today's
  small model; know the name and the idea.
- **Why fine-tune at all, given RAG and prompting exist?** Three different
  tools for three different problems:
  - **Prompting** a general model — zero setup, pay per call, works
    immediately, but every call re-explains the task and pays for the
    model's full generality even on a narrow, repetitive job.
  - **RAG** (Stage 4) — grounds *open-ended* answers in a document set that
    changes over time; the model's weights never change, only what's
    retrieved and injected as context.
  - **Fine-tuning (LoRA)** — bakes a **narrow, stable, repetitive** task
    (like a fixed classification scheme) directly into the model's behavior.
    Best when: the task is well-defined and won't change often, you have
    enough labeled examples, and you'll run it enough times that the
    per-call cost/latency win outweighs the upfront training + maintenance
    cost.
- **The real tradeoff to measure**, not assume: training/maintenance cost
  (data curation, retraining when the task's definition changes) vs. the
  per-call savings once trained. This session measures the per-call side
  directly; the training/maintenance side you evaluate by reasoning about
  your own task.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Hugging Face PEFT docs — *LoRA*:
  <https://huggingface.co/docs/peft/conceptual_guides/lora>.

**Video (pick one, ~15–20 min):**
- Search *"LoRA fine-tuning explained"* — focus on the low-rank
  `ΔW ≈ B·A` idea, not implementation minutiae.

---

## Track_B link (step 3)

**Usually non-blocking for using LoRA; can block if you want the "why it
works."** Low-rank decomposition is a `Track_B/Math_stat/01_linear_algebra`
idea (approximating a matrix with the product of two smaller ones) combined
with `Track_B/Deep_Learning/05_pretrained_and_transfer` (transfer learning).
Using `peft`'s `LoraConfig` doesn't require this — note *"revisit in
Track_B: low-rank decomposition"* and continue unless you want the deeper
understanding now.

---

## Worked example — LoRA fine-tune a ticket classifier  <!-- step 4 -->

```python
from datasets import Dataset
from transformers import (
    AutoTokenizer, AutoModelForSequenceClassification, TrainingArguments, Trainer,
)
from peft import LoraConfig, get_peft_model, TaskType

LABELS = ["billing", "bug", "feature", "other"]
label2id = {l: i for i, l in enumerate(LABELS)}

# a small labeled dataset for a narrow, fixed classification task
train_texts = [
    "I was charged twice this month, please refund me", "billing",
    "the export button does nothing on Safari", "bug",
    "can you add dark mode support", "feature",
    "invoice #4471 shows the wrong amount", "billing",
    "the app crashes when I upload a large file", "bug",
    "please add a way to export as CSV", "feature",
    "what are your business hours", "other",
    "my subscription renewed but I cancelled it last week", "billing",
    # ... extend to 40-60 examples for a real run; kept short here
]
texts = train_texts[0::2]
labels = [label2id[l] for l in train_texts[1::2]]
ds = Dataset.from_dict({"text": texts, "label": labels})

tokenizer = AutoTokenizer.from_pretrained("distilbert-base-uncased")
def tokenize(batch):
    return tokenizer(batch["text"], truncation=True, padding="max_length", max_length=32)
ds = ds.map(tokenize, batched=True)

base_model = AutoModelForSequenceClassification.from_pretrained(
    "distilbert-base-uncased", num_labels=len(LABELS)
)
lora_config = LoraConfig(
    task_type=TaskType.SEQ_CLS, r=8, lora_alpha=16, lora_dropout=0.1,
    target_modules=["q_lin", "v_lin"],   # distilbert's attention projections
)
model = get_peft_model(base_model, lora_config)
model.print_trainable_parameters()

args = TrainingArguments(
    output_dir="./lora_out", num_train_epochs=8, per_device_train_batch_size=4,
    learning_rate=1e-3, logging_steps=2, report_to=[],
)
trainer = Trainer(model=model, args=args, train_dataset=ds)
trainer.train()
```

**Expected output** (values vary):

```
trainable params: 147,456 || all params: 67,102,468 || trainable%: 0.2197
{'loss': 1.38, 'epoch': ...}
...
{'loss': 0.09, 'epoch': ...}
```

Read it: `trainable%` around 0.2% is LoRA's whole point made visible — you're
training a tiny fraction of a 67M-parameter model. Loss dropping toward 0
on this tiny training set shows the adapter is learning the mapping; on a
real fine-tune you'd hold out a validation set the same way Session 1-2
taught you to, and watch for overfitting given how little data you have.

---

## Build: `code/lora_finetune.py`  <!-- step 5 -->

Build the fine-tune above with a real labeled set of **40-60 examples**
across your 4 categories (reuse/extend Stage 1B's and Session 5's ticket
texts). Hold out 8-10 examples as a test set — **never trained on** — and
report accuracy/F1 on them (Session 2's tools).

Then build the **comparison**: on the same held-out test set, classify each
ticket by (a) your LoRA model, (b) a zero-shot prompt to `claude-haiku-4-5`
listing the four categories and asking for one word back (Stage 0/1 style
call). For each approach, record: accuracy on the test set, $ cost per
classification, and latency per classification. Print a small table.

Experiments:
1. **Change LoRA's rank.** Retrain with `r=2` and `r=32`. Compare
   `trainable_parameters()` and test accuracy — does more capacity help on
   this little data, or does it just overfit faster?
2. **Shrink the training set on purpose.** Cut it to 16 examples and re-run.
   Note where accuracy falls apart — this is the "enough labeled examples"
   condition from Concepts, made concrete.
3. **Reason about RAG.** You won't build this, but answer in `notes.md`: if
   this task were instead "answer an open-ended question about a specific
   customer's ticket history," would you reach for fine-tuning or RAG, and
   why?

---

## Quick test (step 7 — answer from memory, then check)

1. What does LoRA freeze, and what does it actually train?
2. What does the rank `r` control, and what's the tradeoff in raising it?
3. Give one task that's a good fit for fine-tuning and one that's a better
   fit for RAG — and say why for each.
4. What's the tradeoff fine-tuning makes: what do you pay upfront, and what
   do you save per call?
5. What condition, if missing, makes fine-tuning a bad choice regardless of
   how well it would otherwise fit the task?

<details><summary>Answers</summary>

1. Freezes the entire pretrained base model; trains only the small
   injected low-rank matrices (`A`/`B`, i.e. the adapter) at chosen layers.
2. The size/capacity of the low-rank approximation — higher `r` means more
   trainable parameters and more expressive adapters, but more compute and
   more overfitting risk on small datasets.
3. Fine-tuning fits a narrow, stable, repetitive task like fixed-category
   classification. RAG fits open-ended questions that need grounding in a
   document set that changes over time — the model's weights shouldn't (and
   with RAG, don't) need to change when the documents do.
4. Pay upfront: data curation, training compute/time, and ongoing
   maintenance (retraining if the task changes). Save per call: no
   per-request LLM API cost/latency once deployed, since inference runs
   locally on your own (small) model.
5. Not having enough labeled examples for the task — without them, the
   adapter overfits and doesn't generalize, no matter how well-suited the
   task otherwise is.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `lora_finetune.py` trains a LoRA adapter on a real 40-60 example
      labeled set and reports `trainable%` alongside test accuracy/F1.
- [ ] You've built the head-to-head comparison table (LoRA model vs.
      zero-shot prompting) with real accuracy, $ cost, and latency numbers
      on the same held-out test set.
- [ ] You've written, in `notes.md`, a fine-tuning-vs-RAG judgment call for
      a hypothetical open-ended task.
- [ ] You can state, from memory, what LoRA trains and why that's cheap.

## Pitfalls

- **Too little training data for the rank you chose.** A high-capacity
  adapter on 16 examples memorizes rather than generalizes — watch train
  loss go to ~0 while test accuracy stays flat or drops.
- **Comparing training cost to a single inference call's cost.** The honest
  comparison is training cost amortized over *however many times you'll
  actually run this classification* vs. paying per call forever — do that
  division explicitly rather than eyeballing it.
- **Reaching for fine-tuning because it's the "advanced" option.** Session
  4's lesson repeats here: complexity has to earn its cost. If prompting
  already hits your accuracy bar and call volume is low, it's the right
  choice, not the naive one.

## Carries to next stage

Stage 4B is complete. Stage 5 (multi-agent) and Stage 6 (production) build
systems that may call any of these three approaches — deterministic (1B),
classical/fine-tuned (4B), or LLM prompting/RAG — behind one interface;
Stage 6B's FastAPI middleware is where that routing decision becomes a real,
deployed service.
