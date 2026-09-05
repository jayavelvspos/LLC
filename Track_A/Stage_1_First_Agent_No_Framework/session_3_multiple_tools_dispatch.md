# Session 3 — Multiple Tools & Dispatch (~45 min)

**Objective:** give the agent 3 tools, route calls through a name→function
dispatch table, and handle multiple `tool_use` blocks in one turn.

**Prerequisites:** Session 2 complete (`agent_loop.py` runs a one-tool loop).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Dispatch tables; keeping schema + function in sync |
| 10–30 | Write `code/tools.py` — 3 tools + `TOOLS` list + `DISPATCH` dict |
| 30–40 | Wire it into the loop; trigger a parallel tool call |
| 40–45 | Notes |

---

## Concepts

- With many tools you need a **dispatch table**: `DISPATCH = {"get_weather":
  get_weather, ...}`. The loop does `DISPATCH[block.name](**block.input)`.
- Keep each tool's **schema** and **function** next to each other so they don't
  drift. A mismatch (schema says `city`, function expects `location`) is a
  `TypeError` at call time.
- The model may emit **parallel `tool_use`** blocks when calls are independent
  (e.g. weather in 3 cities). Execute them (order doesn't matter), return all
  results in one user message.
- Good tool design: few tools, sharp non-overlapping descriptions, flat input
  schemas, and results that are short strings the model can read.
- `tool_choice` defaults to `"auto"` (model decides). Leave it there for a
  general agent.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Tool use*, "Best practices for tool definitions" and
  "Parallel tool use":
  <https://docs.anthropic.com/en/docs/build-with-claude/tool-use>.
- Anthropic — *Building effective agents* (tool-surface design):
  <https://www.anthropic.com/research/building-effective-agents>.

**Video (pick one, ~10–20 min):**
- Search *"LLM agent multiple tools routing python"* — focus on the dispatch
  pattern.

---

## Track_B link (step 3)

**None.** Dispatch is a dictionary lookup. Note "no Track_B link" and continue.

---

## Worked example — 3 tools, one parallel turn

`code/tools.py` (shape):

```python
def get_weather(city: str) -> str: ...
def word_count(text: str) -> str: ...
def calculator(expression: str) -> str:
    return str(eval(expression, {"__builtins__": {}}, {}))   # toy; see pitfalls

TOOLS = [
    {"name": "get_weather", "description": "...", "input_schema": {...}},
    {"name": "word_count",  "description": "...", "input_schema": {...}},
    {"name": "calculator",  "description": "Evaluate a arithmetic expression.",
     "input_schema": {"type": "object",
                      "properties": {"expression": {"type": "string"}},
                      "required": ["expression"], "additionalProperties": False}},
]
DISPATCH = {"get_weather": get_weather, "word_count": word_count, "calculator": calculator}
```

Prompt: *"Compare the temperatures in Paris, Oslo, and Lagos and tell me the
range."*

**Expected output** (shape):

```
  step 1: get_weather({'city': 'Paris'})     <- three tool_use blocks
  step 1: get_weather({'city': 'Oslo'})         in ONE assistant turn
  step 1: get_weather({'city': 'Lagos'})
  step 2: calculator({'expression': '31 - 3'})
The range is 28 C: Lagos 31 C, Oslo 3 C.
```

Read it: three independent weather calls came back in a single turn (parallel),
you returned three `tool_result` blocks in one user message, then the model did
one more step and answered.

---

## Build

Build `tools.py` and import `TOOLS` / `DISPATCH` into `agent_loop.py`. Then:
- Give two tools **overlapping descriptions** → watch the model pick the wrong
  one; fix by sharpening the descriptions.
- Prompt something needing all 3 tools in sequence.
- Return a huge string from a tool (10 KB) → watch `input_tokens` jump and note
  the cost implication (results are context you pay for every subsequent step).

---

## Quick test (step 7 — answer from memory, then check)

1. What does the dispatch table map, and how does the loop use it?
2. Why keep a tool's schema and function together?
3. When does the model emit parallel `tool_use` blocks, and how do you respond?
4. Name two properties of a well-designed tool.
5. What does returning a very large tool result cost you?

<details><summary>Answers</summary>

1. Tool `name` → the Python function. The loop calls
   `DISPATCH[block.name](**block.input)`.
2. So the JSON Schema and the function signature don't drift apart; a mismatch
   is a runtime `TypeError`.
3. When the calls are independent. Execute all, return all `tool_result` blocks
   in **one** user message.
4. Any two of: sharp non-overlapping description, flat input schema, short
   readable string result, few tools overall.
5. Every subsequent model call resends it as input tokens — large results
   inflate cost and latency for the rest of the run.

</details>

---

## Done when

- [ ] The agent has 3 working tools routed via `DISPATCH`.
- [ ] You've seen one assistant turn with multiple `tool_use` blocks handled
      correctly.
- [ ] You've seen a wrong-tool pick caused by vague descriptions, then fixed it.
- [ ] You can explain the parallel-tool response rule from memory.

## Pitfalls

- **`eval()` on model input is dangerous.** The toy `calculator` restricts
  builtins; for anything real use `ast.literal_eval` or a parser. Note this in
  `notes.md` as a security item.
- **Unbounded tool output** is a silent cost leak — cap/truncate result strings.
- **Too many tools** degrades selection. Keep the set small.

## Carries to next session

The agent picks among tools. Session 4 makes it survive tools that fail, bad
arguments, and timeouts.
