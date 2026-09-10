# Session 2 — Routing & Parallelism (~45 min)

**Objective:** send an input to one of several specialised sub-chains
(`RunnableBranch`), and run independent sub-chains at once and merge their
results (`RunnableParallel`) — the two control-flow primitives under every
supervisor and fan-out.

**Prerequisites:** Session 1 complete (`lcel_chain.py`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Routing vs parallelism; the Runnables that express each |
| 10–30 | `code/routing.py` — classify → branch, and fan-out → merge |
| 30–40 | Add a fallback branch; time serial vs parallel |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Routing** = pick one path based on the input. In LCEL:
  - a **classifier chain** returns a label, then
  - `RunnableBranch((cond1, chain1), (cond2, chain2), default_chain)` runs the
    first branch whose condition is true.
  - Or a plain `RunnableLambda` that returns the chosen sub-chain (LangChain
    runs a returned Runnable — "dynamic routing").
- **Parallelism** = run independent chains on the same input and collect all
  outputs. `RunnableParallel({"a": chain_a, "b": chain_b})` (or just a dict in a
  `|` position) invokes both — concurrently where the runtime can — and returns
  `{"a": ..., "b": ...}`.
- **Fan-out then fan-in:** `RunnableParallel` is fan-out; a following
  `RunnableLambda`/chain that consumes the dict is fan-in (the merge/reduce
  step). Decide the merge *before* you fan out.
- **`RunnableLambda`** wraps any `f(x) -> y` as a Runnable so plain Python sits
  in a chain (parse, filter, format, choose).
- These map straight onto Stage 5: the supervisor is routing; the parallel
  retrieve step is `RunnableParallel` + a reducer.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- LangChain docs — *Routing* (how-to: `RunnableBranch` and custom-function
  routing): <https://python.langchain.com/docs/how_to/routing/>.
- LangChain docs — *Parallel* (`RunnableParallel`):
  <https://python.langchain.com/docs/how_to/parallel/>.

**Video (pick one, ~10–20 min):**
- Search *"LangChain RunnableBranch routing"* — a short walkthrough of classify-
  then-branch.

---

## Track_B link (step 3)

**Light, non-blocking.** Routing is an expected-value decision (which branch
gives the best result per unit cost); parallel fan-out/fan-in is DAG scheduling
(what can run at once, where they join). Note *"revisit in Track_B:
`05_decision_and_orchestration_math` — EV routing, DAG scheduling"* and continue.

---

## Worked example — classify, branch, and a parallel summary  <!-- step 4 -->

`code/routing.py`:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnableBranch, RunnableParallel, RunnableLambda

model = ChatAnthropic(model="claude-opus-5", max_tokens=1024)
def p(system): return ChatPromptTemplate.from_messages([("system", system), ("human", "{q}")]) | model | StrOutputParser()

classify = ChatPromptTemplate.from_messages([
    ("system", "Reply with exactly one word: code, math, or other."),
    ("human", "{q}"),
]) | model | StrOutputParser()

route = RunnableBranch(
    (lambda x: x["kind"].strip().lower().startswith("code"),  p("You are a terse senior engineer.")),
    (lambda x: x["kind"].strip().lower().startswith("math"),  p("You are a precise maths tutor. Show steps.")),
    p("Answer plainly in 2 sentences."),                       # default
)
router = {"kind": classify, "q": lambda x: x["q"]} | route

print(router.invoke({"q": "why does my recursion hit a stack overflow?"}))

# parallel: three independent takes on one input, merged
takes = RunnableParallel(
    pros=p("List 3 upsides. Bullets."),
    cons=p("List 3 downsides. Bullets."),
    verdict=p("One-sentence verdict."),
)
merged = takes | RunnableLambda(lambda d: f"PROS\n{d['pros']}\n\nCONS\n{d['cons']}\n\nVERDICT: {d['verdict']}")
print(merged.invoke({"q": "adopting a monorepo"}))
```

**Expected output** (shape):

```
<engineer-voiced answer about stack frames / base case>

PROS
- ...
CONS
- ...
VERDICT: ...
```

Read it: `classify` picks the lane, `RunnableBranch` runs only that lane's
prompt, and `RunnableParallel` runs three prompts on one input and hands a dict
to the merge step.

---

## Build: `code/routing.py`  <!-- step 5 -->

Build both pieces. Experiments:
1. **Fallback branch.** Feed the router a question that classifies as neither
   `code` nor `math`. Confirm the default branch runs. Then make `classify`
   return garbage and confirm the default still catches it.
2. **Serial vs parallel timing.** Run the three "takes" once through
   `RunnableParallel` and once as a manual `for` loop. Time both. Where does the
   speedup come from, and when is it zero?
3. **Dynamic routing.** Replace `RunnableBranch` with a `RunnableLambda` that
   *returns* the chosen sub-chain based on `x["kind"]`. Confirm LangChain
   invokes the returned Runnable.

---

## Quick test (step 7 — answer from memory, then check)

1. What does `RunnableBranch` do with its list of `(condition, runnable)` pairs?
2. What does `RunnableParallel` return, and how does it run its members?
3. What is the "fan-in" step, and when must you design it?
4. What does `RunnableLambda` let you put into a chain?
5. Which Stage 5 pieces are routing, and which are parallel fan-out?

<details><summary>Answers</summary>

1. Runs the runnable of the **first** pair whose condition returns true; falls
   through to the default if none match.
2. A dict of `{key: output}` for each member, run concurrently where the runtime
   allows.
3. The merge/reduce that consumes the parallel dict into one result; design it
   before fanning out so you know what shape each branch must return.
4. Any plain `f(x) -> y` Python function — parsing, filtering, formatting,
   choosing a sub-chain.
5. Routing = the supervisor picking the next worker. Parallel fan-out = the
   concurrent retrieve step + its reducer.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `routing.py` routes an input to one of ≥3 branches, including a default.
- [ ] It fans one input out to ≥3 parallel sub-chains and merges the dict.
- [ ] You've measured serial vs parallel and can say when parallel helps.
- [ ] You can name the routing and fan-out pieces of your Stage 5 system.

## Pitfalls

- **Classifier drift** — the label chain returns "Code." with punctuation/case;
  normalise before comparing, and always have a default branch.
- **No merge plan** — `RunnableParallel` output is a dict; something has to
  consume it.
- **Expecting parallelism for free** — chained-dependent steps can't overlap;
  only genuinely independent branches speed up.

## Carries to next session

Routing + parallel + merge. Session 3 uses them to build the
**evaluator–optimizer** loop: generate → critique → (route back or stop).
