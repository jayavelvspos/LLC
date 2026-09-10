# Stage 4B — Classical ML, Deep Learning & Fine-Tuning

**Stage goal:** the non-LLM ML skillset — build, evaluate, and improve real
models — plus know when fine-tuning beats RAG/prompting. This is where the
`Track_B` Core ML / Deep Learning / NLP topic lists get scaffolded into real,
hands-on sessions instead of sitting as reference lists.

Sits between Stage 4 (RAG) and Stage 5 (multi-agent orchestration). Numbered
**4B** so Stage 5 onward doesn't have to renumber.

Six ~45-minute sessions, in order (Session 6 may run long). See
[`../ROADMAP.md`](../ROADMAP.md) for the full stage description and
[`../ROLE_GOAL.md`](../ROLE_GOAL.md) for why this stage exists.

| # | Session | Outcome |
|---|---------|---------|
| 1 | [Feature engineering & train/test split](session_1_feature_engineering_and_train_test_split.md) | a scikit-learn classification baseline on a real small dataset |
| 2 | [Evaluation & error analysis](session_2_evaluation_and_error_analysis.md) | precision/recall/F1/ROC-AUC, confusion matrix, cross-validation; a written error analysis of the Session 1 model |
| 3 | [Unsupervised learning & class imbalance](session_3_unsupervised_learning_and_class_imbalance.md) | clustering on the same dataset; two real techniques for handling class imbalance |
| 4 | [Deep learning fundamentals (PyTorch)](session_4_pytorch_training_loop.md) | an explicit training loop: forward/backward prop, loss, optimizer, epochs/batches, dropout, batch norm |
| 5 | [Hugging Face `transformers` pipelines](session_5_huggingface_transformers_pipelines.md) | pretrained pipelines for classification, NER, and summarization on real text |
| 6 | [PEFT fine-tuning (LoRA) vs. RAG & prompting](session_6_peft_lora_finetuning.md) | fine-tune a small pretrained model on a narrow task; head-to-head cost/quality/latency comparison vs. zero-shot prompting, reasoned comparison vs. Stage 4 RAG |

## Conventions

Python 3.10+. Adds `scikit-learn`, `torch`, `transformers`, `peft`,
`datasets`, `evaluate`. Run every session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Keep `notes.md`.

## Working files planned for this stage

```
Stage_4B_Classical_ML_DL_FineTuning/
  code/
    baseline_model.py     # session 1 — feature engineering + train/test split + a scikit-learn model
    eval_report.py         # session 2 — metrics + confusion matrix + cross-validation on baseline_model
    clustering.py           # session 3 — unsupervised learning on the same/related dataset
    torch_training_loop.py # session 4 — a small PyTorch net trained end-to-end
    hf_pipelines.py         # session 5 — Hugging Face pipelines for classification/NER/summarization
    lora_finetune.py        # session 6 — PEFT/LoRA fine-tune + comparison vs. Stage 4 RAG
  notes.md
```

## Done with Stage 4B when

- [ ] You've trained and evaluated a scikit-learn model with a full metrics
      report (not just accuracy) and can explain a specific error it makes.
- [ ] You've trained a small PyTorch model end-to-end and can name what each
      of forward pass / loss / backward pass / optimizer step does.
- [ ] A Hugging Face pipeline solves a real classification, NER, or
      summarization task on text you supplied.
- [ ] You've fine-tuned a model with LoRA/QLoRA and can state, with numbers,
      when it beats RAG/prompting for a given task and when it doesn't.

## Where this connects

- **Back to Stage 4 (RAG):** the fine-tuning comparison in session 6 is
  measured directly against the Stage 4 system on the same questions.
- **Back to Track_B:** Core_ML / Deep_Learning / NLP topic lists (see the
  `track-b-planned-topics` memory) get their first hands-on application here.
- **Forward to Stage 6 (extended):** the models trained here are what Stage
  6's added MLOps section (experiment tracking, model registry, drift
  monitoring) tracks in production.
- **Forward to Stage 6B:** a classical/fine-tuned model from this stage is a
  candidate to sit behind the FastAPI middleware alongside the LLM/agent path.
