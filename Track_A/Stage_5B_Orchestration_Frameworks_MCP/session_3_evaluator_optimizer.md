# Session 3 — Evaluator–Optimizer Loop (~45 min)

**Objective:** build a generator + evaluator loop in LangGraph that improves an
output across rounds against explicit criteria and stops on **pass** or a
**budget** — the workhorse pattern for "first draft is never good enough".

**Prerequisites:** Session 2 complete. Stage 2 (LangGraph basics) and Stage 5
Session 7 (patterns catalog) helpful.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The loop: generate → evaluate → branch; what makes it terminate |
| 10–30 | `code/eval_optimizer.py` — LangGraph graph with a conditional edge |
| 30–40 | A machine-checkable task; a subjective one; a non-converging one |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **Two roles.** *Generator* produces a candidate. *Evaluator* scores it against
  **named criteria** and returns `{pass: bool, feedback: str}`. On fail, the
  feedback is fed back to the generator for the next round.
- **In LangGraph:** nodes `generate` and `evaluate`; a **conditional edge** from
  `evaluate` that goes to `END` if `pass` or the budget is spent, else back to
  `generate`. State carries `draft`, `feedback`, `round`, `history`.
- **Termination — you must guarantee it.** Stop on: evaluator passes, `round >=
  max_rounds`, cost/latency budget hit, or **no improvement** two rounds running
  (compare scores). Return the best attempt so far, not the last.
- **Criteria quality decides everything.** Mechanical checks (word count, JSON
  validity, required sections, regex) converge fast and honestly. Vague criteria
  ("make it better") never converge or rubber-stamp round 1.
- **Evaluator ≠ generator model, ideally.** A different model (or the same model
  with a rubric-only prompt and no view of its own reasoning) catches more.
- This is the same shape as Stage 6's LLM-as-judge and CI gating — build it well
  here.

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- Anthropic — *Building Effective Agents*, the **evaluator-optimizer** section:
  <https://www.anthropic.com/research/building-effective-agents>.
- LangGraph docs — *Workflows and agents* (evaluator-optimizer example) and
  *conditional edges*: <https://langchain-ai.github.io/langgraph/tutorials/workflows/>.

**Video (pick one, ~10–20 min):**
- Search *"LangGraph evaluator optimizer"* or *"reflection agent LangGraph"*.

---

## Track_B link (step 3)

**Light, non-blocking.** "Does the loop stop?" is absorbing-state reasoning;
"did it get better?" is a measurement question (define the score, compare
rounds). Note *"revisit in Track_B: `05_decision_and_orchestration_math`
(absorbing states) + statistics (defining and comparing a quality score)"* and
continue.

---

## Worked example — constrained copy that must pass a checker  <!-- step 4 -->

`code/eval_optimizer.py`:

```python
from typing import TypedDict
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic

model = ChatAnthropic(model="claude-opus-5", max_tokens=1024)

BRIEF = "Write a release note for feature X: 2 sentences, <= 45 words, no exclamation marks."

class S(TypedDict):
    draft: str
    feedback: str
    round: int
    best: tuple[int, str]   # (violations, text)

def check(text: str) -> list[str]:
    v = []
    if text.count(".") < 2 and text.count("!") == 0: v.append("need 2 sentences")
    if len(text.split()) > 45: v.append("over 45 words")
    if "!" in text: v.append("has exclamation mark")
    return v

def generate(s: S) -> S:
    fix = f"\nFix these issues: {s['feedback']}" if s.get("feedback") else ""
    r = model.invoke(f"{BRIEF}{fix}\n\nPrevious draft:\n{s.get('draft','')}")
    return {"draft": r.content if isinstance(r.content, str) else r.content[0]["text"],
            "round": s["round"] + 1}

def evaluate(s: S) -> S:
    v = check(s["draft"])
    best = s.get("best") or (99, "")
    if len(v) < best[0]:
        best = (len(v), s["draft"])
    return {"feedback": ", ".join(v), "best": best}

def route(s: S) -> str:
    return END if not s["feedback"] or s["round"] >= 4 else "generate"

g = StateGraph(S)
g.add_node("generate", generate); g.add_node("evaluate", evaluate)
g.set_entry_point("generate")
g.add_edge("generate", "evaluate")
g.add_conditional_edges("evaluate", route, {"generate": "generate", END: END})
app = g.compile()

out = app.invoke({"draft": "", "feedback": "", "round": 0, "best": (99, "")})
print("rounds:", out["round"], "| final violations:", check(out["best"][1]))
print(out["best"][1])
```

**Expected output** (shape):

```
rounds: 2 | final violations: []
Feature X lets you pin frequently used filters to the sidebar. Pinned filters persist across sessions and sync to every device on your account.
```

Read it: round 1 usually trips one rule (word count, or a stray "!"); the
evaluator's feedback goes back into `generate`; round 2 passes. The graph
returns `best`, so a later worse round can't lose you the good draft.

---

## Build: `code/eval_optimizer.py`  <!-- step 5 -->

Build the graph. Experiments:
1. **Mechanical criteria.** Use the checker above. Log rounds-to-pass over 10
   different features. What's the distribution?
2. **Subjective criteria.** Swap `check()` for an LLM evaluator with a 3-point
   rubric ("specific, not vague / active voice / no marketing adjectives").
   Does it converge? Does it ever pass a clearly-bad draft? Tighten the rubric.
3. **Non-convergence.** Set an impossible brief ("2 sentences AND exactly 200
   words AND <= 20 words"). Confirm the budget stops it at round 4 and returns
   the least-bad attempt.

---

## Quick test (step 7 — answer from memory, then check)

1. What are the two roles, and what does the evaluator return?
2. In LangGraph, which construct sends the loop back to `generate` or to `END`?
3. List three things that should be able to terminate the loop.
4. Why return `best` instead of the last draft?
5. What kind of criteria converge honestly, and what kind don't?

<details><summary>Answers</summary>

1. Generator (produces a candidate) and evaluator (scores it against named
   criteria, returns `{pass, feedback}`).
2. A **conditional edge** from the `evaluate` node whose routing function returns
   `"generate"` or `END`.
3. Any three: evaluator passes; `round >= max_rounds`; cost/latency budget hit;
   no score improvement for N rounds.
4. A later round can regress; `best` guarantees you keep the strongest draft
   seen.
5. Mechanical/checkable criteria (counts, schema, regex) converge honestly;
   vague criteria never converge or rubber-stamp the first draft.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `eval_optimizer.py` improves an output across ≥2 rounds against explicit
      criteria.
- [ ] It provably terminates on both pass and budget, and returns the best
      attempt.
- [ ] You've compared a mechanical evaluator to an LLM-rubric one.
- [ ] You can explain what guarantees termination, from memory.

## Pitfalls

- **No budget** — an evaluator that's never satisfied loops until it crashes or
  bankrupts you.
- **Vague rubric** — "make it better" isn't a criterion.
- **Returning the last draft** — keep and return `best`.
- **Same model, same prompt for eval** — give the evaluator a rubric-only view.

## Carries to next session

A loop you can trust to stop. Session 4 wires **LangSmith** in so every round of
every run is a trace you can inspect and score against a dataset.
