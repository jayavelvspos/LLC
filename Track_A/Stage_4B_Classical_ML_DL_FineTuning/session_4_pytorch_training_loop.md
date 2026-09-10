# Session 4 — Deep Learning Fundamentals: A PyTorch Training Loop (~45 min)

**Objective:** build and train a small neural network on the same dataset
from Sessions 1-3, writing the training loop explicitly (forward pass, loss,
backward pass, optimizer step) so every piece that `.fit()` hid in
scikit-learn is now visible and named.

**Prerequisites:** Sessions 1-3 complete. `pip install torch` (CPU build is
fine for this dataset's size).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 3's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–15 | Perceptron -> network; forward pass; loss; backward pass; gradient descent |
| 15–20 | Optimizers, epochs/batches/learning rate, dropout, batch norm |
| 20–40 | Build `code/torch_training_loop.py` |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Perceptron.** The atomic unit: take inputs, multiply each by a learned
  weight, sum them plus a bias, pass the result through an **activation
  function**. One perceptron is basically logistic regression's math
  (weights, bias, sigmoid). A **neural network** is many of these, arranged
  in layers, each layer's output feeding the next.
- **Activation functions.** Without one, stacking layers is pointless — a
  chain of linear operations collapses into one linear operation. `ReLU`
  (`max(0, x)`) is the standard choice for hidden layers (fast, avoids some
  gradient problems). `Sigmoid` squashes to `(0, 1)` — used at the *output*
  layer for binary classification, turning a raw score into a probability.
- **Forward pass.** Feed a batch of inputs through every layer in order,
  producing predictions. Nothing about training happens here — it's pure
  computation, `model(x)`.
- **Loss function.** Compares predictions to true labels with a single
  number to minimize. Binary Cross-Entropy (`BCELoss`) is standard for
  binary classification — it penalizes a confident *wrong* prediction far
  more than a hedging one.
- **Backward pass (backpropagation).** PyTorch's autograd walks the forward
  computation graph in reverse, computing **the gradient of the loss with
  respect to every weight** — how much nudging each individual weight would
  change the loss. `loss.backward()` does this in one call; you never
  hand-derive the calculus, but you should be able to say what it computed.
- **Gradient descent / optimizer.** Nudge every weight a small step in the
  direction that *reduces* the loss: `weight -= learning_rate * gradient`.
  `optim.SGD` does exactly this; `optim.Adam` does a smarter, adaptive
  version (per-weight learning rates that adjust over time) — the practical
  default for most training today.
- **Epoch vs. batch.** One **epoch** = one full pass over the training data.
  Data is usually split into **batches** (e.g. 32 samples) — the model's
  weights update after each batch, not just once per epoch. **Learning
  rate** controls the size of each update step: too high and training
  diverges/oscillates; too low and it crawls.
- **Dropout.** During training, randomly zero out a fraction of neurons each
  forward pass (e.g. 20%). Forces the network not to over-rely on any single
  neuron — a regularization technique, directly analogous to Session 1-3's
  overfitting concern, now applied inside the network itself.
- **Batch normalization.** Normalizes a layer's outputs (mean 0, variance 1)
  before the next layer sees them, per batch. Stabilizes and usually speeds
  up training, especially in deeper networks.
- **Vanishing gradients.** In deep networks, gradients can shrink toward
  zero as they're propagated back through many layers (especially with
  saturating activations like sigmoid in hidden layers), so early layers
  barely update. `ReLU` in hidden layers and batch norm are two of the
  standard mitigations — you won't hit this badly at today's small scale,
  but you should recognize the name and cause.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- PyTorch docs — *Learn the Basics: Build the Neural Network* and
  *Optimization Loop*: <https://pytorch.org/tutorials/beginner/basics/intro.html>
  (the "Build Model" and "Optimization" pages specifically).

**Video (pick one, ~15–20 min):**
- 3Blue1Brown — search *"3Blue1Brown neural network backpropagation"* (the
  "Essence of neural networks" series, episodes 1 and 3 give the intuition
  fastest).

---

## Track_B link (step 3)

**Can block.** `.backward()` is opaque without at least the intuition of
"gradient = direction of steepest increase, so step the opposite way." If
that's shaky, switch to `Track_B/Deep_Learning/02_training_mechanics` and
`Track_B/Math_stat/04_calculus` now — this is the single most
math-load-bearing session in the stage.

---

## Worked example — a 2-layer network, explicit loop  <!-- step 4 -->

```python
import torch
import torch.nn as nn
from baseline_model import scaler, X_train, y_train, X_test, y_test

X_train_t = torch.tensor(scaler.transform(X_train), dtype=torch.float32)
y_train_t = torch.tensor(y_train, dtype=torch.float32).unsqueeze(1)
X_test_t = torch.tensor(scaler.transform(X_test), dtype=torch.float32)
y_test_t = torch.tensor(y_test, dtype=torch.float32).unsqueeze(1)

model = nn.Sequential(
    nn.Linear(30, 16),
    nn.ReLU(),
    nn.Dropout(0.2),
    nn.Linear(16, 1),
    nn.Sigmoid(),
)
loss_fn = nn.BCELoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

for epoch in range(50):
    model.train()
    optimizer.zero_grad()             # clear old gradients
    preds = model(X_train_t)          # forward pass
    loss = loss_fn(preds, y_train_t)  # compute loss
    loss.backward()                   # backward pass: compute gradients
    optimizer.step()                  # gradient descent: update weights

    if epoch % 10 == 0:
        print(f"epoch {epoch:2d}  loss={loss.item():.4f}")

model.eval()
with torch.no_grad():
    test_preds = (model(X_test_t) > 0.5).float()
    accuracy = (test_preds == y_test_t).float().mean().item()
print("test accuracy:", accuracy)
```

**Expected output** (values vary run to run):

```
epoch  0  loss=0.6931
epoch 10  loss=0.1842
epoch 20  loss=0.0931
epoch 30  loss=0.0612
epoch 40  loss=0.0451
test accuracy: 0.9737
```

Read it: loss starts near `0.69` (≈ `ln(2)`, what you'd expect from a
random-guessing binary classifier) and drops as weights update. Test
accuracy in the same ballpark as Session 1's logistic regression — for a
dataset this small and this linearly separable, the extra complexity of a
neural net buys you little to nothing. That's an honest, expected result,
not a failure.

---

## Build: `code/torch_training_loop.py`  <!-- step 5 -->

Build the loop above, then extend it to print test accuracy every 10 epochs
too (not just training loss), so you can watch both curves.

Experiments:
1. **Crank the learning rate.** Try `lr=1.0`. Watch loss diverge or
   oscillate instead of decreasing — this is what "too high" looks like,
   concretely.
2. **Remove dropout.** Train with and without `nn.Dropout(0.2)`, same seed,
   and compare the *gap* between final training loss and test accuracy —
   dropout should narrow overfitting on a run where it appears.
3. **Add `nn.BatchNorm1d(16)`** after the first `Linear` layer (before
   `ReLU`). Compare how many epochs it takes to reach a given loss vs.
   without it.

---

## Quick test (step 7 — answer from memory, then check)

1. What does a single perceptron compute?
2. Put these in the order they happen in one training step: backward pass,
   optimizer step, forward pass, zero the gradients.
3. What does `loss.backward()` actually compute?
4. What's the difference between an epoch and a batch?
5. Name one thing dropout does and one thing batch normalization does.

<details><summary>Answers</summary>

1. A weighted sum of its inputs plus a bias, passed through an activation
   function.
2. Zero the gradients -> forward pass -> backward pass -> optimizer step.
3. The gradient of the loss with respect to every weight in the network —
   how much changing each weight would change the loss.
4. An epoch is one full pass over the entire training set; a batch is a
   subset of the training set the model processes (and updates weights on)
   in one step — many batches make up one epoch.
5. Dropout randomly zeroes a fraction of neurons during training to prevent
   over-reliance on any one of them (regularization). Batch normalization
   normalizes a layer's outputs per batch, stabilizing and typically
   speeding up training.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `torch_training_loop.py` trains end-to-end with an explicit
      forward/loss/backward/step loop (no hidden `.fit()`), and prints
      decreasing loss plus a final test accuracy.
- [ ] You've made training diverge on purpose with too high a learning rate.
- [ ] You can name, in order, the four steps of one training iteration.
- [ ] You can explain what dropout and batch normalization each do, from
      memory.

## Pitfalls

- **Forgetting `optimizer.zero_grad()`.** Gradients accumulate across calls
  by default in PyTorch — skip this and each step's update is corrupted by
  every previous step's gradient too.
- **Forgetting `model.eval()` / `torch.no_grad()` at inference time.**
  Dropout and batch norm behave differently in train vs. eval mode; leaving
  the model in train mode during evaluation gives noisy, wrong numbers.
- **Judging a tiny/simple dataset's neural net against its scikit-learn
  baseline and expecting a big win.** Deep learning's advantage shows up on
  large, high-dimensional, unstructured data (text, images) — not
  necessarily on 30 tabular features and 569 rows. The comparison itself is
  the lesson.

## Carries to next session

Session 5 moves from tabular data to **text** — Hugging Face `transformers`
pipelines, where the "network" is already trained for you and the skill is
using it correctly, not building it from scratch.
