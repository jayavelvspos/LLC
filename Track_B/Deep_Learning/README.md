# Deep Learning Foundations

A hands-on learning workspace, following the same pattern as `../Math_stat/`.
Scaffolded 2026-09-10 — **folder structure and topic map only, `notes.md` /
`exercises.py` content not yet written.** Pulled in when Track_A's
`Stage_4B_Classical_ML_DL_FineTuning/` needs it (just-in-time, per
`../CLAUDE.md`), or on request.

## Folder map

| Folder | Topics | Why it matters for AI/ML engineering |
|---|---|---|
| `01_neural_network_basics` | Perceptron, Neural Networks, Activation Functions | the atomic unit of every model you'll fine-tune |
| `02_training_mechanics` | Forward Propagation, Backward Propagation, Loss Functions, Gradient Descent, Optimizers | what actually happens inside `.backward()` / `optimizer.step()` |
| `03_training_practicalities` | Epochs / Batch Size / Learning Rate, Hyperparameter Tuning, Dropout, Batch Normalization, Vanishing Gradients | why a training run succeeds, stalls, or diverges |
| `04_architectures` | CNN, RNN / LSTM | the two architecture families behind vision and sequence models |
| `05_pretrained_and_transfer` | Pretrained Models, Transfer Learning, Fine-Tuning, SOTA Models, SOTA Techniques | why you fine-tune instead of training from scratch — and what PEFT/LoRA is doing |

## How to use each folder (once content exists)

1. Read `notes.md` first — intuition and formulas, kept short.
2. Run `exercises.py` (`py 01_neural_network_basics\exercises.py`) — worked
   examples with real numbers, dependency-free where the concept allows it
   (e.g. a from-scratch perceptron/forward-pass in plain Python).
3. Do the `TODO` functions yourself before reading the `# solution` comment.
   Re-run — it self-checks with `assert`.
4. Move to the next folder in order (01 -> 05).

## Where this connects

- **Forward to Track_A:** `Stage_4B_Classical_ML_DL_FineTuning/` sessions 4
  (PyTorch), 5 (Hugging Face), 6 (PEFT fine-tuning) build the real, library-backed
  versions of these concepts.
- **Back to `Math_stat`:** gradient descent leans on `04_calculus`; loss
  landscapes and weight matrices lean on `01_linear_algebra`.
