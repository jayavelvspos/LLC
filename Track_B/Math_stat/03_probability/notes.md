# Probability

## Why agents need this
LLMs output a probability distribution over possible next tokens — probability
*is* the mechanism. Beyond that: routing an agent to the right tool, deciding
how confident to be in an answer, and classic Bayesian reasoning (updating
belief given new evidence) all show up constantly in agent design.

## Concepts

**Probability basics** — a number between 0 and 1 (or 0%-100%) describing how
likely an event is. All probabilities for possible outcomes of one event sum
to 1.

**Conditional probability** — P(A | B): the probability of A *given that* B
has already happened. Written `P(A|B) = P(A and B) / P(B)`.
e.g. P(user wants weather | message contains "forecast").

**Bayes' Theorem** — flips a conditional probability around:
`P(A|B) = P(B|A) * P(A) / P(B)`.
This is how you update a belief with new evidence. Classic agent use: given a
tool-call result (evidence), how does that change the probability the agent's
current plan is correct? Also the backbone of simple spam/intent classifiers.

**Random variable & Expected value** — a random variable is a quantity whose
value depends on chance (e.g. "the cost of the next agent tool call," which
varies depending on which tool gets picked). Expected value is the
probability-weighted average of all possible outcomes:
`E[X] = sum(value * probability)`. Used to decide "on average, which tool
choice is cheaper/faster," even though any single call is uncertain.

**Softmax** — converts a list of raw scores into a probability distribution
that sums to 1: `softmax(x)_i = exp(x_i) / sum(exp(x_j))`. This is literally
how an LLM turns internal scores into next-token probabilities, and how an
agent router can turn "confidence scores" for different tools into a proper
probability distribution.

**Entropy** — measures uncertainty in a probability distribution:
`H(p) = -sum(p_i * log2(p_i))`. Low entropy = very confident/peaked
distribution (one option dominates). High entropy = the distribution is
spread out / the agent is unsure. Useful for deciding "should I ask the user a
clarifying question, or am I confident enough to proceed?"

## Order to learn
probability basics → conditional probability → Bayes' theorem → random
variable & expected value → softmax → entropy.
