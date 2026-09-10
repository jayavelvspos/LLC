# How to run every session (the loop) — Stage 4B

Use this same 8-step loop for **every** session in **Stage 4B — Classical ML,
Deep Learning & Fine-Tuning** (and every other stage). It fits in ~45 minutes
*when no Track_B detour is needed*. Keep a timer — the boxes exist to stop you
rabbit-holing on step 2 and skipping steps 5–8, which is where the learning
actually happens.

| # | Step | Min | Mode | Produces |
|---|------|-----|------|----------|
| 0 | Recall last session | 3 | active | spoken/written answers to the previous session's Quick test |
| 1 | Orient | 2 | — | you can state this session's goal + its "Done when" list |
| 2 | Learn the concept | 8 | passive→active | margin notes in `notes.md` |
| 3 | Locate the Track_B footing | 2* | active | a decision: no link / revisit later / switch now |
| 4 | Study the worked example | 7 | active | a correct output *prediction*, then the real run |
| 5 | Practise: modify, break, build | 12 | active | the session's deliverable + 2–3 deliberate experiments |
| 6 | Connect to real systems | 4 | active | 2–3 sentences in `notes.md` in your own words |
| 7 | Retrieval check | 5 | active | written answers to this session's Quick test, from memory |
| 8 | Close | 2 | active | ticked checklist + a "surprises / open questions / Track_B?" note |

Total: 45 min. *Step 3 is 2 min for the check; a Track_B switch is a separate
20–30 min timebox and the session resumes after. Sessions 4–6 (PyTorch,
Hugging Face, PEFT) may legitimately run long — let them, and note the
overrun rather than cutting the worked example short.

---

## How to do each step well

### 0 — Recall last session
Skip only for Session 1. Otherwise answer the **previous** session's Quick test
from memory, then check yourself. Missed one? Copy it into `notes.md` under
"revisit".

### 1 — Orient
Read this session's **Objective** and **Done when**. Don't start until you can
say in one sentence what "finished" looks like.

### 2 — Learn the concept
Read the **Concepts** section, then **one** primary resource. One. The session
file is the source of truth; the resource is support.

### 3 — Locate the Track_B footing
Read the session's **Track_B link** section and pick: no link / note a revisit /
switch now. This stage has the heaviest Track_B footing of any Track_A stage
so far — don't skip this step here.

### 4 — Study the worked example
Write your predicted output **first**, then run it and diff. The gap is the
signal — especially for training curves and metrics, where intuition is often
wrong until you've seen a few runs.

### 5 — Practise: modify, break, build
Build the named deliverable (type it), then run 2–3 deliberate experiments —
change one thing, predict, run, confirm.

### 6 — Connect to real systems
2–3 sentences in `notes.md`: where does this show up in a production AI system,
in your own words?

### 7 — Retrieval check
Close everything. Answer the **Quick test** from memory in writing. Grade
yourself. Wrong/blank → `notes.md` "revisit".

### 8 — Close
Tick **Done when**. Add three lines to `notes.md`: Surprised me / Still unclear /
Needs a Track_B deep-dive (which topic).

---

## Standing rules

- **Timebox hard.** Overrunning step 2 is the classic failure.
- **Active > passive.** Steps 4, 5, 7 are non-negotiable.
- **`notes.md` is the deliverable that outlasts the code.**
- **One resource per session.**

---

## Track_B footing for this stage

This stage **is** the pull-in point for `Track_B/Core_ML`, `Track_B/Deep_Learning`,
and `Track_B/NLP` — scaffold those folders (if not already done) when this
stage starts:

| This stage's concept | Track_B topic | Blocking? |
|---|---|---|
| Feature engineering, train/test split, overfitting | `Core_ML` (features & labels, cross-validation, regularization) | can block — switch if the "why" of a split or a regularizer doesn't land |
| Precision/recall/F1/ROC-AUC/confusion matrix | `Core_ML` (evaluation metrics) | can block — these are easy to memorize and hard to apply without the underlying confusion-matrix logic |
| Forward/backward propagation, gradient descent, loss functions | `Deep_Learning` (perceptron, forward/backward prop, gradient descent, loss functions) + `Math_stat` calculus | can block — PyTorch's `.backward()` is opaque without this |
| Optimizers, learning rate, batch/epoch, dropout, batch norm | `Deep_Learning` | usually non-blocking — note and revisit |
| Tokenization, embeddings, attention, transformers (for Hugging Face) | `NLP` (tokenization, word/vector embeddings, attention, transformers) | can block for session 5–6 if attention is still a black box |
| LoRA / PEFT mechanics (why fine-tune a subset of weights) | `Deep_Learning` (transfer learning) + `Math_stat` linear algebra (low-rank decomposition) | usually non-blocking for using LoRA; blocking if you want to understand *why* it works |

Unlike Stage 5B, most rows here **can** block — this stage is the first place
Track_A's "build first" philosophy meets material where the math genuinely
gates understanding. Don't force through a session that's stopped making
sense; take the Track_B detour.
