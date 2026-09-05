# Statistics

## Why agents need this
Once an agent is running in production, you need to answer: "is it working
well?" That means summarizing distributions of latency, cost, token counts,
and quality scores across many runs — exactly what descriptive statistics do.

## Concepts

**Mean** — the average: sum of values / count. Sensitive to outliers (one
30-second timeout wrecks your "average latency").

**Median** — the middle value when sorted. Robust to outliers — often a better
single number for latency/cost reporting than the mean.

**Mode** — the most frequent value. Useful for categorical agent data, e.g.
"which tool does the agent call most often?"

**Variance** — average of squared differences from the mean. Measures spread.
Squared units make it hard to interpret directly (hence std dev).

**Standard deviation** — square root of variance, back in the original units.
"Typical distance from the mean." Small std dev = consistent agent behavior;
large std dev = unpredictable (some runs fast, some very slow).

**Percentiles / Quantiles** — the value below which a given % of data falls.
p50 = median. **p95 / p99 latency** are the numbers you actually report for
production systems, because mean hides rare-but-bad outliers that users feel.

**Correlation (Pearson)** — a number from -1 to 1 measuring how two variables
move together. e.g. does prompt length correlate with response latency or
cost? +1 = perfectly together, -1 = perfectly opposite, 0 = unrelated.
Correlation is not causation — a classic and important caveat.

## Order to learn
mean → median → mode → variance → standard deviation → percentiles →
correlation.
