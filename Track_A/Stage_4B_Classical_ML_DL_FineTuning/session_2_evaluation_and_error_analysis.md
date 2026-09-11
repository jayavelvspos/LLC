# Session 2 — Evaluation & Error Analysis (~45 min)

**Objective:** go beyond accuracy — compute precision, recall, F1, ROC-AUC,
and a confusion matrix for Session 1's baseline, run cross-validation, and
write a short error analysis naming a specific class of mistake the model
makes.

**What you'll learn:**
- Confusion matrix, precision, recall, F1-score, ROC-AUC
- Why the precision/recall tradeoff is a business decision, not a math one
- k-fold cross-validation and what it catches that one split misses
- How to do error analysis on actual misclassified examples

**Prerequisites:** Session 1 complete (`baseline_model.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 1's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–15 | Why accuracy lies; confusion matrix; precision/recall/F1/ROC-AUC |
| 15–20 | Cross-validation |
| 20–35 | Build `code/eval_report.py` |
| 35–45 | Write the error analysis; notes |

---

## Concepts  <!-- step 2 -->

- **Confusion matrix.** A 2x2 (for binary classification) table of actual vs.
  predicted: true positives, false positives, true negatives, false
  negatives. Every other classification metric is computed from these four
  numbers.
- **Accuracy** = `(TP + TN) / total`. Misleading on imbalanced data: a
  dataset that's 95% one class gets 95% "accuracy" by always predicting that
  class, having learned nothing.
- **Precision** = `TP / (TP + FP)` — of everything you *predicted* positive,
  how much was actually positive. High precision = few false alarms.
- **Recall** = `TP / (TP + FN)` — of everything that *was* actually
  positive, how much did you catch. High recall = few misses.
- **The precision/recall tradeoff is a business decision, not a math one.**
  On this session's dataset (cancer diagnosis), a false negative (missed
  malignant case) is far worse than a false positive (unnecessary follow-up
  test) — so you'd tune the model to favor recall even at some cost to
  precision. A spam filter might weigh it the other way.
- **F1-score** = harmonic mean of precision and recall — one number when you
  need to summarize both, but it hides *which* one is weak. Prefer looking
  at precision and recall separately when the tradeoff matters.
- **ROC-AUC** — plots true-positive rate vs. false-positive rate across every
  possible decision threshold, then measures the area under that curve (1.0
  = perfect ranking, 0.5 = random). Unlike accuracy/precision/recall, it
  doesn't depend on picking one threshold — it measures how well the model
  *ranks* positives above negatives overall.
- **Cross-validation (k-fold).** Instead of one train/test split, split the
  data into *k* folds, train on `k-1` and test on the remaining fold, rotate,
  average the *k* scores. Gives a more reliable estimate than a single split
  and a sense of variance ("how much does performance swing across
  different data")— catches a lucky/unlucky single split.
- **Error analysis.** Don't stop at a metric — pull the *specific
  misclassified examples* and look for a pattern (e.g. "every false negative
  has one particular feature near the decision boundary"). That pattern is
  what tells you whether to engineer a new feature, collect more data, or
  accept the error rate.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- scikit-learn docs — *Model evaluation: quantifying the quality of
  predictions*: <https://scikit-learn.org/stable/modules/model_evaluation.html>
  (skim `classification_report`, `confusion_matrix`, `roc_auc_score`).

**Video (pick one, ~15–20 min):**
- StatQuest with Josh Starmer — search *"StatQuest precision recall"* and/or
  *"StatQuest ROC and AUC"*.

---

## Track_B link (step 3)

**Can block.** These metrics are easy to memorize as formulas and hard to
apply correctly without the underlying confusion-matrix logic. If a metric's
formula doesn't map cleanly to "what does this actually tell me," switch to
`Track_B/Core_ML/05_evaluation_metrics` now.

---

## Worked example — a full evaluation report  <!-- step 4 -->

```python
from sklearn.metrics import (
    classification_report, confusion_matrix, roc_auc_score,
)
from sklearn.model_selection import cross_val_score
from baseline_model import model, scaler, X_train, X_test, y_train, y_test

y_pred = model.predict(scaler.transform(X_test))
y_proba = model.predict_proba(scaler.transform(X_test))[:, 1]

print(confusion_matrix(y_test, y_pred))
print(classification_report(y_test, y_pred, target_names=["malignant", "benign"]))
print("ROC-AUC:", roc_auc_score(y_test, y_proba))

scores = cross_val_score(model, scaler.transform(X_train), y_train, cv=5)
print("5-fold CV accuracy: mean=%.3f  std=%.3f" % (scores.mean(), scores.std()))
```

**Expected output** (values vary):

```
[[41  2]
 [ 1 70]]
              precision    recall  f1-score   support
   malignant       0.98      0.95      0.96        43
      benign       0.97      0.99      0.98        71

ROC-AUC: 0.996
5-fold CV accuracy: mean=0.978  std=0.012
```

Read it: 2 false positives, 1 false negative in this run — the confusion
matrix's raw counts are what precision/recall/F1 are computed from. The
5-fold CV mean is close to the single-split test accuracy, with a small std
— this split wasn't a fluke.

---

## Build: `code/eval_report.py`  <!-- step 5 -->

Build the report above against Session 1's `baseline_model.py`. Then pull the
**actual misclassified rows** (`X_test[y_test != y_pred]`) and print their
feature values next to the correctly classified rows' typical range for at
least one feature. Write **2-3 sentences of error analysis**: what, if
anything, do the misclassified examples have in common?

Experiments:
1. **Shift the decision threshold.** Instead of `model.predict` (threshold
   0.5), threshold `y_proba` yourself at `0.3` and recompute precision/
   recall. Confirm recall goes up and precision goes down (or vice versa at
   `0.7`) — this is the tradeoff from Concepts, made concrete.
2. **Simulate imbalance.** Drop 90% of one class from `X_train`/`y_train`
   (keep `X_test` as-is) and retrain. Watch accuracy stay high while
   recall on the now-rare class collapses — the "always predict majority"
   trap.
3. **Compare CV std across `k`.** Run `cross_val_score` with `cv=3` and
   `cv=10`. Note how the mean and std change.

---

## Quick test (step 7 — answer from memory, then check)

1. What four numbers does every classification metric come from?
2. Give a concrete scenario where you'd optimize for recall over precision,
   and one where you'd do the opposite.
3. What does ROC-AUC measure that accuracy/precision/recall don't?
4. What problem does k-fold cross-validation catch that a single train/test
   split can miss?
5. What's the actual deliverable of "error analysis" — a number, or
   something else?

<details><summary>Answers</summary>

1. True positives, false positives, true negatives, false negatives — the
   confusion matrix.
2. Recall over precision: missing a real case is costly (cancer diagnosis,
   fraud detection). Precision over recall: false alarms are costly and
   real cases can be caught another way (spam filter annoying users, a
   support-ticket auto-escalation flooding a human queue).
3. How well the model *ranks* positives above negatives across every
   threshold, not just at one fixed cutoff.
4. A single split can be lucky or unlucky by chance; k-fold averages over
   k different splits and reports variance, giving a more reliable and
   honest estimate.
5. A specific, named pattern in what the model gets wrong — not just a
   metric number, but an actionable insight (a feature, a data segment, a
   boundary case) about *why*.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `eval_report.py` prints a confusion matrix, full classification
      report, ROC-AUC, and 5-fold CV mean/std for the baseline model.
- [ ] You've pulled the actual misclassified rows and written 2-3 sentences
      of error analysis naming a real pattern (or explicitly noting there
      isn't one).
- [ ] You've shifted the decision threshold and watched precision/recall
      move in opposite directions.
- [ ] You can explain, from memory, why accuracy alone can be misleading on
      imbalanced data.

## Pitfalls

- **Reporting only accuracy.** On any remotely imbalanced dataset this is
  close to meaningless — always pair it with precision/recall or a
  confusion matrix.
- **Cross-validating on the test set.** `cross_val_score` in the worked
  example runs on `X_train` — the test set stays untouched until final
  reporting.
- **Treating F1 as the whole story.** It hides *which* of precision/recall
  is weak; look at both when the tradeoff has real consequences.

## Carries to next session

Session 3 stays on this same dataset/evaluation toolkit but drops the
labels — unsupervised learning, and a direct look at the class-imbalance
problem this session's threshold-shift experiment previewed.
