# Core ML (Machine Learning Foundations)

A hands-on learning workspace, following the same pattern as `../Math_stat/`.
Scaffolded 2026-09-10 — **folder structure and topic map only, `notes.md` /
`exercises.py` content not yet written.** Pulled in when Track_A's
`Stage_4B_Classical_ML_DL_FineTuning/` needs it (just-in-time, per
`../CLAUDE.md`), or on request.

## Folder map

| Folder | Topics | Why it matters for AI/ML engineering |
|---|---|---|
| `01_ml_foundations` | Features & Labels; Supervised / Unsupervised / Reinforcement Learning | the three learning paradigms — which one a problem even calls for |
| `02_classification_regression_clustering` | Classification, Regression, Clustering | the three core task types every ML problem reduces to |
| `03_feature_engineering` | Feature Engineering, Class Imbalance | turning raw data into signal a model can use; handling skewed real-world data |
| `04_model_validation` | Train/Test Split, Cross-Validation, Overfitting, Underfitting, Regularization | making sure a model's reported performance is real, not memorized |
| `05_evaluation_metrics` | Accuracy, Precision, Recall, F1-Score, ROC-AUC, Confusion Matrix | judging a model correctly — accuracy alone lies on imbalanced data |

## How to use each folder (once content exists)

1. Read `notes.md` first — intuition and formulas, kept short.
2. Run `exercises.py` (`py 01_ml_foundations\exercises.py`) — worked examples
   with real numbers, dependency-free where the concept allows it.
3. Do the `TODO` functions yourself before reading the `# solution` comment.
   Re-run — it self-checks with `assert`.
4. Move to the next folder in order (01 -> 05).

## Where this connects

- **Forward to Track_A:** `Stage_4B_Classical_ML_DL_FineTuning/` sessions 1-3
  build real scikit-learn models using these concepts on real data.
- **Back to `Math_stat`:** evaluation metrics and cross-validation lean on
  `02_statistics`; regularization leans lightly on `04_calculus`.
