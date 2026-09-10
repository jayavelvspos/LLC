# Session 1 — Rules, Regex, Heuristics & Scoring (~45 min)

**Objective:** catalog the deterministic techniques that can replace a model
call (regex, lookup tables, heuristics, scoring functions), then classify a
batch of sample inputs into "handle deterministically" vs. "needs the model"
using Stage 0's cost/latency numbers as the yardstick.

**Prerequisites:** Stage 1 complete (the CLI agent with tools). Stage 0
Session 5 (`costs.py`, cost/latency numbers) — you'll reuse that math here.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Stage 1's last Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The deterministic toolbox: regex, lookup tables, heuristics, scoring |
| 10–20 | The decision boundary — Stage 0's cost/latency numbers as the yardstick |
| 20–35 | Build `code/fast_path_rules.py` |
| 35–45 | Classify a sample batch, record the split, notes |

---

## Concepts  <!-- step 2 -->

- **Regex pattern matching** — extract or validate structured pieces of text
  (an order ID, a date, an email, a yes/no) with zero API calls. Correct 100%
  of the time it matches; matches nothing it wasn't written for.
- **Lookup tables / rule tables** — a `dict` (or small config file) mapping
  known inputs -> known outputs. FAQ answers, status-code explanations,
  command aliases. Config-driven, no training, instantly auditable.
- **Heuristics** — hand-tuned rules of thumb combining a few signals ("message
  under 8 words, ends in a question mark, contains a known product name" ->
  probably a simple product question). Cheaper to write than to train a
  model, and you can read exactly why it fired.
- **Scoring functions** — a weighted sum of signals producing a confidence
  score, then a threshold decides the path:
  `score = w1*signal1 + w2*signal2 + ...` ; `score >= threshold` -> handle
  deterministically, else escalate. This is the bridge between "one hard
  rule" and "ask the model" — a tunable dial, not a binary switch.
- **The cost/latency boundary.** Stage 0 gave you real numbers: a rule costs
  ~$0 and ~0ms; a model call costs real cents and real seconds (TTFT +
  total). The question this session answers for a given input class isn't
  "can a rule handle this?" but **"does a rule handle this accurately enough
  that paying nothing beats paying for a model call?"**
- **The failure mode to respect:** a bad rule fails *silently and
  confidently* — it returns a wrong answer with no hint anything's off. A
  model asked the same ambiguous question may at least hedge. This is why
  scoring + a threshold (route uncertain cases to the model) beats a single
  brittle rule.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Python docs — `re` module HOWTO: <https://docs.python.org/3/howto/regex.html>
  (skim for `match`/`search`/named groups — that's all you need here).

**Video (pick one, ~10–15 min):**
- Search *"when to use rules vs machine learning"* — short explainers on the
  cost/accuracy/maintainability tradeoff between hand-written rules and a
  model.

---

## Track_B link (step 3)

**Light, non-blocking.** A scoring function with a threshold is, informally,
a tiny classifier — false positives and false negatives are exactly what
`Track_B/Core_ML/05_evaluation_metrics` (precision/recall/confusion matrix)
will formalize once that folder has content. Note *"revisit in Track_B:
Core_ML evaluation metrics for scoring the rule's own accuracy"* and
continue — you don't need the formal metrics to build a working threshold
today.

---

## Worked example — a support-ticket triage score  <!-- step 4 -->

```python
import re

REFUND_WORDS = {"refund", "charged twice", "chargeback", "money back"}
CANCEL_WORDS = {"cancel", "unsubscribe", "close my account"}

def score_refund(text: str) -> float:
    text = text.lower()
    score = 0.0
    if any(w in text for w in REFUND_WORDS):
        score += 0.7
    if re.search(r"\$\d+(\.\d{2})?", text):     # a dollar amount mentioned
        score += 0.2
    if "?" not in text:                          # a statement, not a question
        score += 0.1
    return min(score, 1.0)

THRESHOLD = 0.7

samples = [
    "I was charged twice this month, $49.99 both times",
    "can you explain what this $12 fee is for?",
    "how do I cancel my subscription",
]

for s in samples:
    sc = score_refund(s)
    route = "DETERMINISTIC (refund path)" if sc >= THRESHOLD else "MODEL (ambiguous)"
    print(f"{sc:.2f}  {route:<28}  {s}")
```

**Expected output** (exact scores depend on your weights):

```
0.90  DETERMINISTIC (refund path)  I was charged twice this month, $49.99 both times
0.20  MODEL (ambiguous)            can you explain what this $12 fee is for?
0.00  MODEL (ambiguous)            how do I cancel my subscription
```

Read it: line 1 crosses the threshold and never touches an LLM. Line 2 has a
dollar amount but no refund language — low score, correctly escalated. Line 3
matches nothing here (it needs `CANCEL_WORDS` in a real system) — a reminder
that a rule set has to be built and grown deliberately; it doesn't
generalize like a model does.

---

## Build: `code/fast_path_rules.py`  <!-- step 5 -->

Build the scorer above, then extend it to a second category using
`CANCEL_WORDS` (or one of your own). Run it over a batch of **15-20 sample
inputs** you write yourself (a realistic mix: some obviously deterministic,
some obviously not, a few deliberately borderline). Print, for the whole
batch: how many routed deterministic vs. model, and — using Stage 0's
`estimate_cost` / your measured TTFT — the $ and seconds you'd have spent if
*every* input had gone to the model instead.

Experiments:
1. **Move the threshold.** Try `0.5` and `0.9` on the same batch. Note how
   many borderline cases flip sides, and which threshold you'd trust in
   production.
2. **Break it on purpose.** Write one input designed to score high but that a
   human would clearly send to the model (e.g. sarcastic or negated: "don't
   you dare refund me"). Confirm the rule gets it wrong — this is the
   silent-failure mode from Concepts.
3. **Add a signal.** Add one more scoring signal (e.g. message length) and
   see if it changes any routing decisions.

---

## Quick test (step 7 — answer from memory, then check)

1. Name three deterministic techniques that can replace a model call, and one
   thing each is good for.
2. What does a scoring function's threshold actually decide?
3. Why is a single hard-coded rule riskier than a scoring function with a
   threshold?
4. What's the real yardstick for "is this worth a model call" — not vibes,
   the actual numbers?
5. What's the specific failure mode of a bad deterministic rule, and how does
   routing uncertain cases to the model mitigate it?

<details><summary>Answers</summary>

1. Any three of: regex (structured extraction/validation), lookup tables
   (known input -> known output), heuristics (hand-tuned combined signals),
   scoring functions (tunable confidence + threshold).
2. Whether an input is confident enough to handle deterministically, or
   should escalate to the model.
3. A single rule is binary and can't express "I'm not sure" — it fires
   confidently even when wrong. A scoring function can route low-confidence
   cases to the model instead of guessing.
4. Stage 0's cost/latency numbers: the $/1M-token price and measured
   TTFT/total time for the model call you'd otherwise make, compared against
   the rule's near-zero cost and latency.
5. It fails silently and confidently — wrong answer, no hint anything's off.
   Routing anything below the confidence threshold to the model means the
   model (which can hedge or reason about ambiguity) handles the cases the
   rule isn't sure about.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `fast_path_rules.py` scores a batch of 15-20 real sample inputs and
      routes each to "deterministic" or "model".
- [ ] You've measured the $ and time that batch would have cost if every
      input went to the model, using Stage 0's cost math.
- [ ] You've found at least one input where the rule is confidently wrong,
      and can explain why.
- [ ] You can state, from memory, the cost/latency yardstick for "is this
      worth a model call."

## Pitfalls

- **Tuning the threshold on the same batch you eyeballed to write the rules**
  — you'll overfit to your own examples. Write a couple of samples *after*
  finalizing the rule, specifically trying to fool it.
- **Conflating "matched a keyword" with "confident."** A single keyword hit
  is weak evidence; require multiple signals before crossing a high
  threshold.
- **Forgetting this needs maintenance.** Unlike a model, a rule set doesn't
  generalize to inputs you didn't anticipate — it needs to be revisited as
  new input patterns show up.

## Carries to next session

`fast_path_rules.py`'s scorer becomes the fast path wired into an actual
agent in Session 2 — the deterministic branch of a real
validate -> short-circuit -> call model -> validate output pipeline.
