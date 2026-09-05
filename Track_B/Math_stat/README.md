# Math & Statistics for Agent Creation & Orchestration

A hands-on learning workspace. No external libraries needed — everything runs with
plain Python 3 (you already have it via the `py` launcher: `py --version`).

## Folder map

| Folder | Topic | Why it matters for agents |
|---|---|---|
| `01_linear_algebra` | vectors, matrices, dot product, norms, cosine similarity | embeddings, semantic search, RAG retrieval |
| `02_statistics` | mean/median/mode, variance, std dev, correlation, percentiles | evaluating agent latency, cost, quality metrics |
| `03_probability` | probability, conditional probability, Bayes, entropy, softmax | token sampling, confidence, routing decisions, classifiers |
| `04_calculus` | derivative, gradient, gradient descent intuition | understanding how models are optimized/fine-tuned |
| `05_decision_and_orchestration_math` | Markov chains, expected value | agent state machines, tool-choice/routing under uncertainty |

## How to use each folder

1. Read `notes.md` first — intuition and formulas, kept short.
2. Run `exercises.py`:
   ```
   py 01_linear_algebra\exercises.py
   ```
   It prints worked examples so you see real numbers move through each formula.
3. Open `exercises.py` and do the `TODO` functions yourself before reading the
   `# solution` below each one. Re-run the file — it self-checks with `assert`.
4. Move to the next folder in order (01 → 05). Each builds a little on the last.

## Recommended intuition-first resources (watch before coding each section)

- Linear Algebra → 3Blue1Brown, *"Essence of Linear Algebra"* (YouTube)
- Statistics & Probability → StatQuest with Josh Starmer (YouTube)
- Calculus → 3Blue1Brown, *"Essence of Calculus"* (YouTube)

Watch the relevant short video for a topic, then immediately run and edit that
topic's `exercises.py`. Intuition + code beats reading a textbook cover to cover.
