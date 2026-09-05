# Session 2 — The Agent Loop (~45 min)

**Objective:** turn the single round trip into a loop that keeps running tools
until the model produces a final answer — with a hard cap so it can't run
forever.

**Prerequisites:** Session 1 complete (`single_tool.py` works).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 1's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | The loop shape: call → if `tool_use`, run + append, repeat → else stop |
| 10–30 | Write `code/agent_loop.py` |
| 30–40 | Add the max-iteration guard; force a multi-step task |
| 40–45 | Notes |

---

## Concepts

- **An agent is a loop.** Pseudocode:

  ```
  while True:
      resp = model(messages, tools)
      append assistant turn
      if resp.stop_reason != "tool_use":
          return resp            # final answer
      for each tool_use block:
          run it, collect tool_result
      append one user message with ALL tool_results
      if iterations >= MAX: break # safety cap
  ```

- One assistant message can contain **several `tool_use` blocks** (parallel
  tools). Run them all, return **all** results in **one** user message.
- **Termination:** normally the model stops asking for tools and returns
  `end_turn`. But bugs, bad tools, or loops can keep it going — so a
  `MAX_ITERATIONS` cap is mandatory, not optional.
- The full `messages` list is the agent's entire memory. It grows every step;
  you resend all of it each call (managing that growth is Stage 3).

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Tool use*, the "Handling the tool use and tool result
  content blocks" and multi-turn sections:
  <https://docs.anthropic.com/en/docs/build-with-claude/tool-use>.
- Anthropic Cookbook — `tool_use/` agentic examples (customer-service-style
  loops): <https://github.com/anthropics/anthropic-cookbook>.
- Anthropic — *Building effective agents* (concepts: loop vs workflow):
  <https://www.anthropic.com/research/building-effective-agents>.

**Video (pick one, ~15–30 min):**
- Search *"build an AI agent from scratch python no framework"* — focus on the
  `while` loop and stop condition, ignore any framework-specific parts.

---

## Track_B link (step 3)

**None** (optional preview only). The max-iteration cap is a crude version of
reasoning about termination — `Track_B/Math_stat/05_decision_and_orchestration_math`
covers loops and absorbing states properly, but you don't need it here. Note
"no Track_B link" and continue.

---

## Worked example — a 3-line-idea loop

`code/agent_loop.py` (core):

```python
MAX_ITERATIONS = 8

def run_agent(user_msg: str) -> str:
    messages = [{"role": "user", "content": user_msg}]
    for step in range(1, MAX_ITERATIONS + 1):
        resp = client.messages.create(
            model="claude-opus-5", max_tokens=1000,
            tools=TOOLS, messages=messages,
        )
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":
            return resp.content[0].text                      # final answer

        results = []
        for block in resp.content:
            if block.type == "tool_use":
                print(f"  step {step}: {block.name}({block.input})")
                out = DISPATCH[block.name](**block.input)     # DISPATCH from session 3; for now, one tool
                results.append({"type": "tool_result",
                                "tool_use_id": block.id, "content": str(out)})
        messages.append({"role": "user", "content": results})

    return "[stopped: hit MAX_ITERATIONS]"
```

Give it a task that needs two steps, e.g. *"What's the weather in the city where
the Eiffel Tower is?"* — the model calls a `find_landmark_city` tool, then
`get_weather`.

**Expected output** (shape):

```
  step 1: find_landmark_city({'landmark': 'Eiffel Tower'})
  step 2: get_weather({'city': 'Paris'})
It's about 14 C in Paris right now.
```

Read it: two tool steps, then `stop_reason` flips to `end_turn` and the loop
returns. Nothing decides "two steps" in advance — the model asks for what it
needs until it doesn't.

---

## Build

Build `agent_loop.py` with **one** tool for now (Session 3 adds more). Then:
- Lower `MAX_ITERATIONS` to `1` and give it a 2-step task → confirm it returns
  the `[stopped: ...]` sentinel instead of hanging.
- Add a deliberately broken tool that always returns `"try again"` → watch the
  model loop until the cap. This is *why* the cap exists.
- Print `resp.usage` each step and watch `input_tokens` climb.

---

## Quick test (step 7 — answer from memory, then check)

1. In one sentence: what is an agent?
2. What condition ends the loop normally?
3. Why is a `MAX_ITERATIONS` cap mandatory?
4. The model returns 3 `tool_use` blocks in one turn. How many `user` messages
   do you send back, and containing what?
5. What is the agent's "memory" during a run?

<details><summary>Answers</summary>

1. An LLM call inside a loop that runs tools until the model returns a final
   answer.
2. `resp.stop_reason != "tool_use"` (normally `"end_turn"`).
3. Bad tools, model mistakes, or oscillation can keep the model asking for
   tools forever; the cap bounds cost and guarantees the loop halts.
4. **One** `user` message containing **all three** `tool_result` blocks.
5. The full `messages` list, resent on every call and appended to each step.

</details>

---

## Done when

- [ ] `agent_loop.py` completes a task that needs ≥2 sequential tool calls.
- [ ] With `MAX_ITERATIONS = 1`, a 2-step task returns the stop sentinel, no hang.
- [ ] You've watched a broken tool drive the loop to the cap.
- [ ] You can state the loop's normal termination condition from memory.

## Pitfalls

- **Splitting parallel results across messages** silently teaches the model to
  stop making parallel calls. One user message, all results.
- **Appending `resp.content` as a string** instead of the block list breaks the
  next turn. Append the list.
- **No cap** = a runaway bill. Always cap.

## Carries to next session

The loop works with one tool. Session 3 adds a dispatch table so it can pick
among several, and handles parallel `tool_use` cleanly.
