# Session 1 — Feature Engineering & Train/Test Split (~45 min)

**Objective:** build a scikit-learn classification baseline on a real small
dataset, with a proper train/test split and feature scaling — the foundation
every later session in this stage builds on.

**What you'll learn:**
- Features & labels; supervised learning
- Train/test splits and `stratify`
- Feature engineering: scaling, encoding, avoiding data leakage
- Why a baseline model exists and what has to justify replacing it

**Prerequisites:** Stage 4 complete (RAG). `pip install scikit-learn`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Stage 4's last Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–15 | Features & labels; supervised learning; why split before touching features |
| 15–20 | Feature engineering: scaling, encoding, leakage |
| 20–40 | Build `code/baseline_model.py` |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Features & labels.** A **feature** is one measured input column (e.g.
  "tumor radius"); the **feature matrix** `X` is all features for all rows.
  The **label** `y` is what you're predicting. Supervised learning = learn a
  function from `X` to `y` using examples where `y` is already known.
- **Train/test split.** Hold out a slice of your labeled data (e.g. 20%) that
  the model never sees during training. Accuracy on the *training* set tells
  you nothing about how the model does on new data — only the held-out test
  set does. This is the single most important habit in this whole stage.
- **`stratify`.** For classification, split so both sets keep the same class
  proportions as the full dataset — otherwise a small or imbalanced dataset
  can give you a test set with almost no examples of the minority class.
- **Feature engineering** here means: **scaling** (put features on comparable
  ranges — many models, including plain logistic regression, are sensitive
  to feature scale) and, for categorical data, **encoding** (turn categories
  into numbers a model can use — not needed for today's dataset, but you'll
  hit it constantly in real tabular data).
- **Data leakage.** Fit the scaler (and any encoder) **only on the training
  set**, then apply it unchanged to the test set. Fitting on the full dataset
  before splitting leaks test-set information into training — your test
  accuracy becomes an overestimate of real-world performance.
- **Baseline model.** A simple, fast, interpretable model (logistic
  regression here) trained first, before anything fancier. It's the number
  everything else in this stage — the deep-learning model in Session 4, the
  fine-tuned model in Session 6 — has to beat to justify its extra
  complexity and cost.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- scikit-learn docs — *Getting Started*:
  <https://scikit-learn.org/stable/getting_started.html> (skim `Pipeline`,
  `train_test_split`, `StandardScaler`).

**Video (pick one, ~15–20 min):**
- Search *"train test split explained scikit-learn"* — focus on *why*, not
  just the API call.

---

## Track_B link (step 3)

**Can block.** If "why hold out data the model never trains on" doesn't feel
obvious yet, switch to `Track_B/Core_ML/01_ml_foundations` and
`04_model_validation` now — this stage's later sessions all assume this
lands. If it does feel obvious, note *"revisit in Track_B: Core_ML
foundations/model_validation for the formal treatment"* and continue.

---

## Worked example — a scikit-learn baseline  <!-- step 4 -->

```python
from sklearn.datasets import load_breast_cancer
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

data = load_breast_cancer()
X, y = data.data, data.target   # 569 samples, 30 features, 0=malignant 1=benign

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42
)

scaler = StandardScaler().fit(X_train)          # fit on train ONLY
X_train_scaled = scaler.transform(X_train)
X_test_scaled = scaler.transform(X_test)

model = LogisticRegression(max_iter=5000).fit(X_train_scaled, y_train)

print("train accuracy:", model.score(X_train_scaled, y_train))
print("test accuracy: ", model.score(X_test_scaled, y_test))
```

**Expected output** (values vary slightly by scikit-learn version):

```
train accuracy: 0.989
test accuracy:  0.982
```

Read it: train and test accuracy are close — a first sign the model isn't
just memorizing. If train were near-perfect and test much lower, that would
be overfitting (Session 2 gives you the tools to catch this more rigorously
than eyeballing two numbers).

---

## Build: `code/baseline_model.py`  <!-- step 5 -->

Build the pipeline above. This is the dataset and baseline model Sessions
2-3 reuse — keep the file importable (`X_train`, `X_test`, `y_train`,
`y_test`, `model`, `scaler` as module-level names or a `main()` you can call
from).

Experiments:
1. **Skip `stratify`.** Re-split without it a few times (different
   `random_state`) and check the class balance in `y_test` each time — see
   it wobble.
2. **Skip scaling.** Train the same `LogisticRegression` on unscaled `X_train`
   directly. Compare test accuracy — on this dataset the gap may be small,
   but note *why* scale still matters (some features span 0-2500, others
   0-0.2; the optimizer converges differently).
3. **Leak on purpose.** Fit the scaler on the *full* `X` (train+test
   combined) instead of train only, then re-check test accuracy. On this
   dataset the effect is subtle — the point is recognizing the mistake in
   your own code, not seeing a dramatic number change.

---

## Quick test (step 7 — answer from memory, then check)

1. What's the difference between a feature and a label?
2. Why does training accuracy alone tell you nothing about generalization?
3. What does `stratify=y` protect against?
4. Where exactly should the scaler be fit, and what goes wrong if you fit it
   somewhere else?
5. What is a baseline model for, and what has to justify replacing it with
   something more complex?

<details><summary>Answers</summary>

1. A feature is a measured input (one column of `X`); the label is the
   target you're predicting (`y`).
2. The model can memorize the training data; only performance on data it
   never saw (the test set) estimates real-world performance.
3. An unlucky split where the test set has a very different class balance
   than the training set (especially bad with a rare class).
4. Fit only on the training set, then apply (`.transform`, not `.fit`) to the
   test set. Fitting on the full dataset leaks test-set statistics into
   training and inflates your reported test accuracy.
5. It's the fast, interpretable number a more complex model (deep learning,
   fine-tuning) has to beat — complexity has to earn its cost/latency/
   maintenance overhead.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `baseline_model.py` trains a scaled `LogisticRegression` with a
      stratified train/test split and prints both accuracies.
- [ ] You've reproduced a data-leakage mistake on purpose and can explain
      what's wrong with it.
- [ ] You can state, from memory, why the scaler must be fit on train only.

## Pitfalls

- **Fitting anything (scaler, encoder, feature selector) on the full
  dataset before splitting.** Always split first.
- **Judging a model by training accuracy alone.** It's not evidence of
  anything by itself.
- **Not setting `random_state`.** Without it, "did my change help?" is
  confounded by a different random split each run.

## Carries to next session

`baseline_model.py`'s trained model and `X_test`/`y_test` are what Session 2
evaluates properly — accuracy alone is about to be shown as an incomplete,
sometimes misleading metric.
