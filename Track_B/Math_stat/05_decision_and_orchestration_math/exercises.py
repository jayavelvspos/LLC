"""
Decision & Orchestration Math — run me: py exercises.py
"""

import random

# ---------------------------------------------------------------------------
# Markov chain — modeling agent workflow states
# ---------------------------------------------------------------------------
states = ["thinking", "tool_call", "observing", "responding", "done"]

# transition_matrix[state][next_state] = probability
transition_matrix = {
    "thinking":   {"tool_call": 0.7, "responding": 0.3},
    "tool_call":  {"observing": 1.0},
    "observing":  {"thinking": 0.4, "responding": 0.6},
    "responding": {"done": 1.0},
    "done":       {"done": 1.0},  # absorbing state
}

# sanity check: every state's outgoing probabilities sum to 1
for state, transitions in transition_matrix.items():
    total = sum(transitions.values())
    assert abs(total - 1.0) < 1e-9, f"{state} transitions sum to {total}, not 1"

def next_state(current_state, matrix, rng):
    options = list(matrix[current_state].items())
    r = rng.random()
    cumulative = 0.0
    for state_name, prob in options:
        cumulative += prob
        if r <= cumulative:
            return state_name
    return options[-1][0]  # floating point fallback

def simulate_run(start_state, matrix, rng, max_steps=20):
    path = [start_state]
    current = start_state
    for _ in range(max_steps):
        if current == "done":
            break
        current = next_state(current, matrix, rng)
        path.append(current)
    return path

rng = random.Random(42)  # fixed seed so output is reproducible
print("Simulated agent runs (state sequences):")
for i in range(5):
    print(f"  run {i}:", " -> ".join(simulate_run("thinking", transition_matrix, rng)))

# ---------------------------------------------------------------------------
# Expected value applied to routing / tool choice
# ---------------------------------------------------------------------------
def expected_value(outcomes):
    return sum(value * prob for value, prob in outcomes)

# Orchestrator must pick a sub-agent to handle a task.
# Each has a probability of success and a "value" if it succeeds (e.g. -cost, or quality score)
sub_agent_A = {"success_prob": 0.9, "value_if_success": 10, "value_if_fail": -5}
sub_agent_B = {"success_prob": 0.6, "value_if_success": 20, "value_if_fail": -2}

def expected_value_of_agent(agent):
    p = agent["success_prob"]
    return expected_value([
        (agent["value_if_success"], p),
        (agent["value_if_fail"], 1 - p),
    ])

ev_a = expected_value_of_agent(sub_agent_A)
ev_b = expected_value_of_agent(sub_agent_B)

print("\nExpected value of routing to sub_agent_A:", ev_a)
print("Expected value of routing to sub_agent_B:", ev_b)
print("-> route to whichever has the higher expected value, even though B has a bigger",
      "\n   payoff, its lower success rate may make A the better long-run choice (or vice versa)")

# ---------------------------------------------------------------------------
# TODO exercises
# ---------------------------------------------------------------------------

def count_state_visits(paths, state_name):
    """TODO: given a list of simulated paths (each a list of state names),
    return how many times state_name appears across all paths in total."""
    # solution:
    # return sum(path.count(state_name) for path in paths)
    pass

# sample_paths = [["thinking", "tool_call", "observing", "responding", "done"],
#                 ["thinking", "responding", "done"]]
# assert count_state_visits(sample_paths, "thinking") == 2
# assert count_state_visits(sample_paths, "tool_call") == 1

def best_choice_by_expected_value(agents):
    """TODO: agents is a dict like {"A": {...}, "B": {...}} (same shape as
    sub_agent_A/B above). Return the key of the agent with the highest
    expected value, using expected_value_of_agent()."""
    # solution:
    # return max(agents, key=lambda name: expected_value_of_agent(agents[name]))
    pass

# assert best_choice_by_expected_value({"A": sub_agent_A, "B": sub_agent_B}) in ("A", "B")

print("\nFill in the TODO functions above, uncomment their asserts, and re-run.")
