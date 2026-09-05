"""
Probability — run me: py exercises.py
"""

import math

# ---------------------------------------------------------------------------
# Probability basics
# ---------------------------------------------------------------------------
# Rolling a 6-sided die: probability of any single face
p_face = 1 / 6
print("P(rolling a 3):", p_face)

# ---------------------------------------------------------------------------
# Conditional probability
# ---------------------------------------------------------------------------
# Agent example: 100 past user messages.
# 30 contained the word "forecast". Of those, 27 actually wanted the weather tool.
# Overall, 40 of the 100 messages wanted the weather tool.
messages_total = 100
contains_forecast = 30
forecast_and_wants_weather = 27
wants_weather_total = 40

def conditional_probability(p_a_and_b, p_b):
    return p_a_and_b / p_b

p_forecast = contains_forecast / messages_total
p_wants_weather_and_forecast = forecast_and_wants_weather / messages_total

p_wants_weather_given_forecast = conditional_probability(
    p_wants_weather_and_forecast, p_forecast
)
print("\nP(wants_weather | contains 'forecast'):", p_wants_weather_given_forecast)

# ---------------------------------------------------------------------------
# Bayes' Theorem
# ---------------------------------------------------------------------------
def bayes_theorem(p_b_given_a, p_a, p_b):
    return (p_b_given_a * p_a) / p_b

# Reframe the same scenario with Bayes:
# P(wants_weather | forecast) = P(forecast | wants_weather) * P(wants_weather) / P(forecast)
p_wants_weather = wants_weather_total / messages_total
p_forecast_given_wants_weather = forecast_and_wants_weather / wants_weather_total

result = bayes_theorem(p_forecast_given_wants_weather, p_wants_weather, p_forecast)
print("Bayes' theorem gives the same answer:", result)

# ---------------------------------------------------------------------------
# Expected value — choosing between two tools by expected cost
# ---------------------------------------------------------------------------
def expected_value(outcomes):
    """outcomes: list of (value, probability) tuples."""
    return sum(value * prob for value, prob in outcomes)

# Tool A: 90% chance it costs $0.01, 10% chance it fails and costs $0.05 (retry)
tool_a_cost = expected_value([(0.01, 0.9), (0.05, 0.1)])
# Tool B: always costs $0.02 flat
tool_b_cost = expected_value([(0.02, 1.0)])

print("\nexpected cost of Tool A:", tool_a_cost)
print("expected cost of Tool B:", tool_b_cost)
print("-> Tool A is cheaper on average, even though it sometimes costs more per call")

# ---------------------------------------------------------------------------
# Softmax — turning raw scores into a probability distribution
# ---------------------------------------------------------------------------
def softmax(scores):
    exps = [math.exp(s) for s in scores]
    total = sum(exps)
    return [e / total for e in exps]

tool_scores = [2.0, 1.0, 0.1]  # raw "confidence" scores for 3 candidate tools
tool_probs = softmax(tool_scores)
print("\nsoftmax(tool_scores):", tool_probs)
print("sums to 1:", sum(tool_probs))

# ---------------------------------------------------------------------------
# Entropy — how confident/uncertain is that distribution?
# ---------------------------------------------------------------------------
def entropy(probs):
    return -sum(p * math.log2(p) for p in probs if p > 0)

confident_dist = [0.97, 0.02, 0.01]
uncertain_dist = [0.34, 0.33, 0.33]

print("\nentropy(confident_dist):", entropy(confident_dist))
print("entropy(uncertain_dist):", entropy(uncertain_dist))
print("-> higher entropy means the agent is less sure which tool to pick;")
print("   could be used as a signal to ask a clarifying question instead of guessing")

# ---------------------------------------------------------------------------
# TODO exercises
# ---------------------------------------------------------------------------

def complement(p):
    """TODO: return the probability of an event NOT happening, given P(event)."""
    # solution: return 1 - p
    pass

# assert complement(0.3) == 0.7

def joint_probability_independent(p_a, p_b):
    """TODO: probability of two INDEPENDENT events both happening."""
    # solution: return p_a * p_b
    pass

# assert joint_probability_independent(0.5, 0.5) == 0.25

print("\nFill in the TODO functions above, uncomment their asserts, and re-run.")
