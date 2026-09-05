# Decision & Orchestration Math

## Why this folder exists
This wasn't in the original list, but it's the math that shows up specifically
when *orchestrating* agents (routing between tools/sub-agents, modeling
workflow state, deciding under uncertainty) rather than just building a single
model. It's a light, practical add-on to probability — no new heavy theory.

## Concepts

**Markov chain (basic)** — a system that moves between a fixed set of
"states," where the probability of the next state depends only on the current
state (not the full history). An agent's workflow is naturally a Markov chain:
states like `thinking -> tool_call -> observing -> responding -> done`, each
with transition probabilities. Useful for modeling/simulating agent behavior
and reasoning about how often each state is visited.

**Transition matrix** — the table of probabilities of moving from each state
to each other state. Row i, column j = P(next state is j | current state is
i). Each row must sum to 1.

**Expected value for decisions** — already covered in probability, but here
applied specifically to *routing*: given multiple possible next actions, each
with a probability of success and a cost/reward, expected value tells you
which action is best *on average* over many decisions — the same logic behind
picking which tool/sub-agent to call, or whether to retry vs. give up.

**Decision under uncertainty (basic)** — when an orchestrator must choose an
action without knowing the outcome in advance, comparing expected values (or
expected utility, if some outcomes matter more than their raw cost implies)
is the standard first tool. This is the mathematical seed of what a
"policy" is in reinforcement learning — you don't need RL theory, just this
intuition.

## Order to learn
Markov chain intuition → transition matrix → simulate a few steps → expected
value applied to routing decisions (ties back to `03_probability`).
