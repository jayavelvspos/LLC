# Session 3 — Unsupervised Learning & Class Imbalance (~45 min)

**Objective:** cluster the same dataset without using its labels, evaluate
the clustering against the labels you *do* have (for learning purposes
only), and apply a real technique for handling class imbalance instead of
just diagnosing it (Session 2).

**Prerequisites:** Sessions 1-2 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 2's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Unsupervised learning; clustering (K-Means) |
| 10–20 | Class imbalance techniques |
| 20–35 | Build `code/clustering.py` |
| 35–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Unsupervised learning.** No labels at all — the algorithm finds
  structure in `X` alone. You use it when labels don't exist, are expensive
  to collect, or when you want to explore a dataset before deciding what to
  predict.
- **K-Means clustering.** Pick *k* (number of clusters). The algorithm places
  *k* centroids, assigns every point to its nearest centroid, recomputes
  centroids as the mean of their assigned points, repeats until stable.
  Result: every row gets a cluster id — but **no cluster is inherently
  "malignant" or "benign"**; a cluster label is just an index the algorithm
  assigned, not a class name.
- **Evaluating clustering against known labels (a learning device, not
  something you'd always have).** Today's dataset happens to have labels, so
  you can sanity-check: do the two clusters roughly line up with the two
  real classes? In a real unsupervised problem you often don't have this
  luxury and instead use internal metrics (e.g. silhouette score) or domain
  judgment.
- **Choosing *k*.** The "elbow method" — plot within-cluster variance
  (`inertia_`) against *k*, look for where adding another cluster stops
  helping much.
- **Class imbalance** (revisited from Session 2's threshold experiment).
  Beyond adjusting the decision threshold, two direct techniques:
  - **`class_weight="balanced"`** — tell the model to penalize mistakes on
    the minority class more heavily during training, instead of treating
    every mistake equally.
  - **Resampling** — oversample the minority class (duplicate/synthesize
    examples) or undersample the majority class, so training data is more
    balanced. Simple oversampling (with replacement) is the version you'll
    build today; SMOTE (synthetic minority oversampling) is the common
    production technique, worth knowing by name even if you don't implement
    it from scratch here.
- **Reinforcement learning** (name-level, not hands-on here): a third
  paradigm alongside supervised/unsupervised — an agent learns by taking
  actions in an environment and receiving reward signals, not from a fixed
  labeled dataset. Out of scope for this stage's hands-on work; noted so you
  can place it correctly against the other two.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- scikit-learn docs — *Clustering* (`KMeans` section):
  <https://scikit-learn.org/stable/modules/clustering.html#k-means>.

**Video (pick one, ~15 min):**
- StatQuest with Josh Starmer — search *"StatQuest K-means clustering"*.

---

## Track_B link (step 3)

**Usually non-blocking.** Clustering's distance math is the same vector-space
intuition as `Track_B/Math_stat/01_linear_algebra` (Euclidean distance is a
close cousin of the norm you already used for cosine similarity in RAG).
Note *"revisit in Track_B: Core_ML unsupervised learning for algorithms
beyond K-Means"* and continue unless the centroid-update loop itself doesn't
make sense — then switch now.

---

## Worked example — cluster, then check against labels  <!-- step 4 -->

```python
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
from baseline_model import scaler, X_train, y_train

X_scaled = scaler.transform(X_train)

kmeans = KMeans(n_clusters=2, random_state=42, n_init=10).fit(X_scaled)
clusters = kmeans.labels_

# adjusted_rand_score: how well do cluster assignments line up with the
# real labels, correcting for chance agreement (1.0 = perfect, 0.0 = random)
print("cluster vs. label agreement:", adjusted_rand_score(y_train, clusters))
print("cluster sizes:", (clusters == 0).sum(), (clusters == 1).sum())
print("actual class sizes:", (y_train == 0).sum(), (y_train == 1).sum())
```

**Expected output** (values vary):

```
cluster vs. label agreement: 0.67
cluster sizes: 179 276
actual class sizes: 168 287
```

Read it: an agreement score well above 0 (but below 1) means K-Means found
structure that partially — not perfectly — lines up with the real diagnosis,
using *only* the feature values, never the labels. That's the point:
unsupervised structure isn't the same thing as your target, but it can be
close when the target is genuinely reflected in the feature geometry.

---

## Build: `code/clustering.py`  <!-- step 5 -->

Build the clustering example above, then:
1. Try `n_clusters` from 2 to 6 and print `kmeans.inertia_` for each —
   eyeball where the "elbow" is.
2. Handle class imbalance on this dataset two ways: retrain Session 1's
   `LogisticRegression` with `class_weight="balanced"`, and separately with
   a simple random-oversample of the minority class in `X_train`/`y_train`.
   Compare recall on the minority class (Session 2's `eval_report.py`
   metrics) for: the original Session 1 model, the `class_weight="balanced"`
   version, and the oversampled version.

Experiments:
1. **Cluster on a deliberately imbalanced subset** — drop most of one class
   before clustering, and see whether K-Means still finds two roughly-equal
   clusters (it will — it has no concept of your original class sizes).
2. **Compare `class_weight="balanced"` vs. oversampling.** Do they move
   recall by similar amounts? Which hurts precision more, on this dataset?
3. **Re-run K-Means with a different `random_state`.** Confirm cluster *ids*
   (0 vs 1) can flip even though the groupings are the same — cluster
   indices are arbitrary labels, not stable identities.

---

## Quick test (step 7 — answer from memory, then check)

1. What's the core difference between supervised and unsupervised learning?
2. Why can't you call a K-Means cluster "the malignant cluster" just because
   it happens to contain mostly malignant examples?
3. Name two direct techniques for handling class imbalance (beyond shifting
   the decision threshold).
4. What does the elbow method help you choose?
5. Where does reinforcement learning fit relative to supervised/unsupervised
   — what's its defining difference?

<details><summary>Answers</summary>

1. Supervised learning learns from labeled examples (`X` -> known `y`);
   unsupervised learning finds structure in `X` alone, with no labels.
2. The cluster id is just an index the algorithm assigned based on feature
   geometry; it has no inherent meaning. It only *correlates* with the real
   label if the label happens to be reflected in that geometry — checking
   that correlation (as in the worked example) is a diagnostic, not a
   guarantee for a new/different clustering run.
3. `class_weight="balanced"` (penalize minority-class mistakes more) and
   resampling (oversample minority / undersample majority; SMOTE for a
   smarter synthetic version).
4. The number of clusters (*k*) — where adding more clusters stops
   meaningfully reducing within-cluster variance.
5. It learns from actions and reward signals in an environment, not from a
   fixed labeled (or unlabeled) dataset — an ongoing feedback loop rather
   than a fixed batch of examples.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `clustering.py` runs K-Means on the unlabeled training features and
      reports agreement against the real labels.
- [ ] You've compared inertia across several values of *k*.
- [ ] You've retrained the Session 1 baseline with `class_weight="balanced"`
      and with oversampling, and compared minority-class recall across all
      three versions.
- [ ] You can explain why a cluster id isn't a class label.

## Pitfalls

- **Treating cluster ids as if they were class predictions.** They're not —
  they're arbitrary indices from an algorithm that never saw your labels.
- **Only fixing imbalance on the training set, then evaluating on an
  artificially rebalanced test set too.** Rebalance training data; leave the
  test set as a realistic reflection of the real class distribution.
- **Picking *k* by "what I expect the answer to be" instead of the data.**
  Defeats the purpose of an unsupervised method.

## Carries to next session

Session 4 leaves scikit-learn for PyTorch — same problem class
(classification), but you'll build the forward/backward pass yourself
instead of calling `.fit()`.
