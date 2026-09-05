# How to run every session — Stage 6

Run every session with the **8-step loop**. Full guidance:
[`../_TEMPLATES/SESSION_METHOD.md`](../_TEMPLATES/SESSION_METHOD.md).

| # | Step | Min | Produces |
|---|------|-----|----------|
| 0 | Recall last session | 3 | answers to the previous session's Quick test |
| 1 | Orient | 2 | you can state the goal + "Done when" |
| 2 | Learn the concept | 8 | notes in `notes.md` |
| 3 | Locate the Track_B footing | 2* | decision: no link / revisit later / switch now |
| 4 | Study the worked example | 7 | an output prediction, then the real run |
| 5 | Practise: modify, break, build | 12 | the deliverable + 2–3 experiments |
| 6 | Connect to real systems | 4 | 2–3 sentences in your own words |
| 7 | Retrieval check | 5 | Quick test answers from memory |
| 8 | Close | 2 | ticked checklist + surprises / Track_B flag |

Total ~45 min. *A Track_B switch at step 3 is a separate 20–30 min timebox.
**Non-negotiable:** steps 4, 5, 7.

---

## Track_B footing for this stage

Non-blocking throughout, but this is where the **statistics** and **probability**
topics in Track_B genuinely earn their place — schedule them in Track_B around
now if you haven't.

| This stage's concept | Track_B topic | Blocking? |
|---|---|---|
| Eval scores as noisy estimates — sample size, variance, "is this delta real" | `Track_B/Math_stat` statistics & probability (sampling, confidence intervals, significance) | no — but do it if you're making ship/no-ship calls on eval deltas |
| LLM-as-judge reliability / agreement | `Track_B/Math_stat` statistics (inter-rater agreement) | no |
| Latency percentiles (p50/p95/p99), $/request as an expectation | `Track_B/Math_stat` probability (distributions, percentiles, expectation) + `05_decision_and_orchestration_math` | no |
| Circuit-breaker thresholds, retry backoff as expected-cost tuning | `05_decision_and_orchestration_math` (expected value) | no |

Note the link each session and continue; put "trusting an eval delta" and
"reading p95" on the Track_B backlog explicitly.
