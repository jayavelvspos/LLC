# Session 4 — Parallel Fan-out & Aggregation (~45 min)

**Objective:** run several workers concurrently (one per sub-task) and reduce
their outputs into one result — the map-reduce shape.

**Prerequisites:** Session 3 complete (`workers.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Map-reduce for agents; when fan-out is safe (independent sub-tasks) |
| 10–35 | `code/fanout.py` — dispatch N retrievers in parallel, merge notes |
| 35–43 | Measure wall-time and cost vs sequential |
| 43–45 | Notes |

---

## Concepts

- **Fan-out is valid when sub-tasks are independent** — e.g. "research each of
  these 5 outline points". A shared dependency (point 4 needs point 2's answer)
  breaks parallelism.
- **Map:** the supervisor produces a list of sub-tasks; the framework spawns a
  worker per item. In LangGraph this is `Send("retriever", {"subtask": s})` for
  each `s`, from a conditional edge.
- **Reduce:** all workers write to the same shared key (`notes`) through a
  reducer (`Annotated[list, add]`), so their results merge without a race. A
  final `aggregate` node dedupes/orders/summarizes.
- **Wall-time** drops toward the slowest single worker; **token cost** is
  roughly unchanged (same work, concurrent) — sometimes higher if you
  over-retrieve. Rate limits and $/minute are the real constraints.
- Bound concurrency (e.g. 5 at a time) so you don't hit API rate limits or a
  cost spike.

---

## Learning resources

**Primary (official, stable):**
- LangGraph docs — *Map-reduce / `Send` API*:
  <https://langchain-ai.github.io/langgraph/how-tos/map-reduce/>.
- LangChain Academy — *Introduction to LangGraph*, **Module 4** ("Map-reduce",
  "Parallelization").
- Anthropic — *Building effective agents* (parallelization: sectioning &
  voting).

**Video (pick one, ~10–20 min):**
- **LangChain** channel — search *"LangGraph map reduce Send"*.

---

## Track_B link (step 3)

**Light, non-blocking.** Total fan-out cost/latency is a sum/max of per-worker
random quantities — `Track_B/Math_stat` probability (expectation of a sum,
distribution of a max). Note *"revisit in Track_B: expected cost/time of N
parallel workers"* and continue.

---

## Worked example — parallel retrieval

`code/fanout.py` (core):

```python
from langgraph.types import Send

def dispatch(state):                       # conditional edge from supervisor
    return [Send("retriever", {"subtask": p}) for p in state["uncovered_points"]]

# retriever returns {"notes": [one entry]}; notes is Annotated[list, add]

def aggregate(state):
    seen, merged = set(), []
    for n in state["notes"]:
        key = n["point"]
        if key not in seen:
            seen.add(key); merged.append(n)
    return {"notes": merged, "log": [f"aggregated {len(merged)} notes"]}
```

**Expected output** (5 points, `stream_mode="updates"`):

```
{'retriever': {'notes': [note for point 1]}}     \
{'retriever': {'notes': [note for point 2]}}      |  arrive interleaved,
{'retriever': {'notes': [note for point 3]}}      |  near-simultaneously
{'retriever': {'notes': [note for point 4]}}      |
{'retriever': {'notes': [note for point 5]}}     /
{'aggregate': {'notes': [5 merged], 'log': ['aggregated 5 notes']}}
wall time: 6.2s   (sequential was 24.1s)   tokens: ~unchanged
```

Read it: five retrievers ran at once; the `add` reducer merged their `notes`
writes safely; `aggregate` deduped. ~4x faster, same token bill.

---

## Build

- Build `fanout.py`: supervisor emits `uncovered_points`, `dispatch` `Send`s one
  retriever each, `aggregate` merges.
- Time it vs the Session 3 sequential version on a 5-point question.
- Cap concurrency at 2 (batch the `Send`s) → observe wall-time rise, rate-limit
  risk fall.
- Introduce a dependency (point 5's brief references point 2) → show the
  parallel version produces a worse point 5. Note: fan-out needs independence.

---

## Quick test (step 7 — answer from memory, then check)

1. When is fan-out valid?
2. What is "map" and what is "reduce" here?
3. How do parallel workers write results without a race?
4. What happens to wall-time vs token cost under fan-out?
5. Why bound concurrency?

<details><summary>Answers</summary>

1. When the sub-tasks are independent of each other's outputs.
2. Map = spawn one worker per sub-task (`Send`). Reduce = merge all workers'
   writes to a shared key (via a reducer) and post-process in an aggregate node.
3. They all write the same key through a reducer (`Annotated[list, add]`), which
   defines a deterministic merge.
4. Wall-time drops toward the slowest single worker; total token cost is roughly
   unchanged (can rise if you over-retrieve).
5. To stay under API rate limits and avoid a cost/latency spike from too many
   simultaneous calls.

</details>

---

## Done when

- [ ] `fanout.py` runs N retrievers concurrently and merges their notes.
- [ ] You've measured the wall-time speedup and confirmed tokens ~flat.
- [ ] You've shown a dependency breaking the parallel version.
- [ ] You can define map and reduce from memory.

## Pitfalls

- **Fan-out over dependent sub-tasks** — silent quality loss.
- **No reducer on the shared result key** — concurrent-write error or lost
  results.
- **Unbounded `Send`s** — rate-limit 429s and a cost spike.

## Carries to next session

More agents + parallelism = more ways to loop and overspend. Session 5 is the
failure-modes session.
