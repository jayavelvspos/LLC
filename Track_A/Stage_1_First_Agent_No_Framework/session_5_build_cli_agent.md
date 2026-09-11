# Session 5 — Build & Harden the CLI Agent (~45 min)

**Objective:** assemble everything into `agent.py` — a command-line agent that
takes a question, chains tool calls, recovers from failures, logs a transcript,
and prints a final answer. This is the Stage 1 deliverable.

**What you'll learn:**
- Structuring an agent into a testable, reusable module layout
- Config as named constants instead of magic numbers
- A CLI with a verbose flag and a max-steps override
- Writing a per-run JSONL transcript
- Writing a system prompt that tells the agent to admit "I can't answer"

**Prerequisites:** Sessions 1–4 complete.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Design: module layout, CLI, config constants |
| 10–35 | Write `code/agent.py`, importing `tools.py` |
| 35–43 | Run 3–4 tasks of increasing complexity; watch the transcript |
| 43–45 | Notes + tick the Stage 1 checklist |

---

## Concepts

- **Module layout:** `tools.py` (tool defs + dispatch + wrapper), `agent.py`
  (loop + CLI + logging). Keep the agent loop pure — input `str`, output `str` —
  so it's testable and reusable in Stage 2.
- **Config as constants** at the top: `MODEL`, `MAX_ITERATIONS`,
  `TOOL_TIMEOUT_S`, `MAX_RESULT_CHARS`. No magic numbers buried in the loop.
- **CLI:** question from `sys.argv` or `input()`; a `--verbose` flag to print
  steps; a `--max-steps` override for experiments.
- **Transcript:** one JSONL file per run under `code/runs/`, named by timestamp.
- **System prompt:** a short one telling the agent what it is, which tools it
  has, and to say so when it can't answer rather than guessing.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Building effective agents* (re-read now that you've built one —
  the "agent" vs "workflow" distinction lands differently):
  <https://www.anthropic.com/research/building-effective-agents>.
- Anthropic Cookbook — a full `tool_use` agent notebook, end to end:
  <https://github.com/anthropics/anthropic-cookbook>.

**Video (optional, ~15–30 min):**
- Search *"agent from scratch python project structure"* — for the packaging,
  not the agent logic (you have that).

---

## Track_B link (step 3)

**None.** Note "no Track_B link" and continue. (Next stage's link is also
"none" — Track_B starts mattering at Stage 4.)

---

## Worked example — the shape of `agent.py`

```python
"""CLI agent: LLM + loop + tools, no framework."""
import sys, json, time, pathlib
from datetime import datetime
from dotenv import load_dotenv
from anthropic import Anthropic
from tools import TOOLS, run_tool

load_dotenv()
client = Anthropic()

MODEL = "claude-opus-5"
MAX_ITERATIONS = 10
SYSTEM = ("You are a CLI assistant with tools for weather, arithmetic, and text "
          "stats. Use them when needed. If no tool can answer, say so plainly.")

def run_agent(question: str, verbose=False, max_steps=MAX_ITERATIONS) -> str:
    run_log = pathlib.Path("code/runs") / f"{datetime.now():%Y%m%d-%H%M%S}.jsonl"
    run_log.parent.mkdir(parents=True, exist_ok=True)
    def log(rec): run_log.open("a").write(json.dumps(rec) + "\n")

    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        resp = client.messages.create(model=MODEL, max_tokens=1500,
                                      system=SYSTEM, tools=TOOLS, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})
        log({"step": step, "stop_reason": resp.stop_reason,
             "in": resp.usage.input_tokens, "out": resp.usage.output_tokens})

        if resp.stop_reason != "tool_use":
            return resp.content[0].text

        results = []
        for b in (x for x in resp.content if x.type == "tool_use"):
            if verbose: print(f"  [{step}] {b.name}({b.input})")
            r = run_tool(b.name, b.input)
            log({"step": step, "tool": b.name, "args": b.input, "is_error": r["is_error"]})
            results.append({"type": "tool_result", "tool_use_id": b.id,
                            "content": r["content"], "is_error": r["is_error"]})
        messages.append({"role": "user", "content": results})

    return "[stopped: hit max steps]"

if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    q = " ".join(args) or input("Ask: ")
    print("\n" + run_agent(q, verbose="--verbose" in sys.argv))
```

**Expected output** (`--verbose`, a 3-step task):

```
  [1] get_weather({'city': 'Paris'})
  [2] get_weather({'city': 'Tokyo'})
  [3] calculator({'expression': '(14 + 9) / 2'})
The average of the two is about 11.5 C (Paris 14 C, Tokyo 9 C).
```

---

## Build

Finish `agent.py`. Run these four, checking the transcript each time:
1. Single-tool: *"What's the weather in Oslo?"*
2. Two sequential tools: *"Weather in the city with the Colosseum?"*
3. Parallel + reduce: *"Range of temperatures across Paris, Cairo, Reykjavik?"*
4. No tool fits: *"Who won the 2019 Cricket World Cup?"* → it should say it
   can't, not hallucinate.

Then one hardening pass: confirm the iteration cap fires, confirm a raising
tool recovers, confirm `runs/*.jsonl` is complete.

---

## Quick test (step 7 — answer from memory, then check)

1. Why keep `run_agent` as `str -> str` with no printing inside?
2. What are the four config constants and why hoist them?
3. What should the agent do when no tool can answer?
4. What's in the run transcript, and where does it go?
5. Two independent backstops keep this agent from running forever / crashing —
   name them.

<details><summary>Answers</summary>

1. So it's unit-testable and can be dropped into Stage 2's graph unchanged;
   I/O belongs at the CLI boundary.
2. `MODEL`, `MAX_ITERATIONS`, `TOOL_TIMEOUT_S`, `MAX_RESULT_CHARS` — hoisted so
   behavior is tunable in one place, no magic numbers in the loop.
3. Say so plainly (per the system prompt), not guess or hallucinate.
4. Every model turn (stop_reason, tokens) and tool call (name, args, error
   flag), as JSONL under `code/runs/<timestamp>.jsonl`.
5. The `MAX_ITERATIONS` cap (Session 2) and the per-tool `run_tool` wrapper with
   `is_error` + timeout (Session 4).

</details>

---

## Done when

- [ ] All four test tasks behave correctly, including the "can't answer" one.
- [ ] A complete JSONL transcript is written per run.
- [ ] Iteration cap and tool-error recovery both demonstrated.
- [ ] `run_agent` is importable and side-effect-free apart from logging.
- [ ] Stage 1 checklist in `README.md` is fully ticked.

## Pitfalls

- **Printing inside the loop** couples it to the CLI — pass `verbose` and print
  at the edges.
- **One growing transcript file forever** — one file per run.
- **Skipping the "no tool fits" test** — that's the case most likely to
  hallucinate in production.

## Carries to next stage

You have a working agent and a feel for what the loop, state handling, and
routing cost you to maintain by hand. **Stage 2** rebuilds this exact agent in
LangGraph so you can see precisely which of those the framework takes over.
