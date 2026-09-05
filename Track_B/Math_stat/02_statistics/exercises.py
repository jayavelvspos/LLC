"""
Statistics — run me: py exercises.py
Agent use case: analyzing latency (ms) of 20 agent responses.
"""

import math

latencies_ms = [210, 195, 230, 205, 198, 220, 215, 190, 980, 208,
                 212, 199, 225, 207, 203, 216, 640, 202, 209, 211]

# ---------------------------------------------------------------------------
# Mean, Median, Mode
# ---------------------------------------------------------------------------
def mean(values):
    return sum(values) / len(values)

def median(values):
    s = sorted(values)
    n = len(s)
    mid = n // 2
    if n % 2 == 0:
        return (s[mid - 1] + s[mid]) / 2
    return s[mid]

def mode(values):
    counts = {}
    for v in values:
        counts[v] = counts.get(v, 0) + 1
    return max(counts, key=counts.get)

print("mean:", mean(latencies_ms))
print("median:", median(latencies_ms))
print("mode:", mode(latencies_ms))
print("-> notice mean is pulled up by the two slow outliers (980, 640);")
print("   median is a more honest 'typical' latency")

# ---------------------------------------------------------------------------
# Variance & Standard deviation (population version)
# ---------------------------------------------------------------------------
def variance(values):
    m = mean(values)
    return sum((x - m) ** 2 for x in values) / len(values)

def std_dev(values):
    return math.sqrt(variance(values))

print("\nvariance:", variance(latencies_ms))
print("std_dev:", std_dev(latencies_ms))

# ---------------------------------------------------------------------------
# Percentiles — what production dashboards actually show
# ---------------------------------------------------------------------------
def percentile(values, p):
    """p in [0, 100]. Simple nearest-rank method."""
    s = sorted(values)
    k = (len(s) - 1) * (p / 100)
    f = math.floor(k)
    c = math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] + (s[c] - s[f]) * (k - f)

print("\np50 (median):", percentile(latencies_ms, 50))
print("p95:", percentile(latencies_ms, 95))
print("p99:", percentile(latencies_ms, 99))

# ---------------------------------------------------------------------------
# Correlation — does prompt length predict latency?
# ---------------------------------------------------------------------------
prompt_lengths = [50, 45, 60, 52, 48, 58, 55, 44, 200, 51,
                   53, 47, 59, 50, 49, 56, 150, 48, 51, 52]

def correlation(x, y):
    mx, my = mean(x), mean(y)
    numerator = sum((xi - mx) * (yi - my) for xi, yi in zip(x, y))
    denominator = math.sqrt(sum((xi - mx) ** 2 for xi in x)) * \
                  math.sqrt(sum((yi - my) ** 2 for yi in y))
    return numerator / denominator

print("\ncorrelation(prompt_length, latency):",
      correlation(prompt_lengths, latencies_ms))
print("-> strong positive correlation: longer prompts tend to mean slower responses")

# ---------------------------------------------------------------------------
# TODO exercises
# ---------------------------------------------------------------------------

def sample_variance(values):
    """TODO: like variance(), but divide by (n - 1) instead of n.
    (This is the 'sample' version, used when your data is a sample of a
    bigger population rather than the whole population.)"""
    # solution:
    # m = mean(values)
    # return sum((x - m) ** 2 for x in values) / (len(values) - 1)
    pass

# assert abs(sample_variance([2, 4, 4, 4, 5, 5, 7, 9]) - 4.5714285714) < 1e-6

def range_spread(values):
    """TODO: return max(values) - min(values)."""
    # solution: return max(values) - min(values)
    pass

# assert range_spread([3, 7, 1, 9, 4]) == 8

print("\nFill in the TODO functions above, uncomment their asserts, and re-run.")
