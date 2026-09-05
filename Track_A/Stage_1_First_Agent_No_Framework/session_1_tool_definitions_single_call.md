# Session 1 — Tool Definitions & a Single Tool Call (~45 min)

**Objective:** define a tool, send it to the model, and hand-drive one full
`tool_use` → `tool_result` → final-answer round trip. No loop yet.

**Prerequisites:** Stage 0 complete (you can make a `messages.create` call and
read `stop_reason`, `usage`, `content`).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What a tool is: a JSON schema + a function you own |
| 10–25 | Write `code/single_tool.py` — one tool, one call, read the `tool_use` block |
| 25–40 | Run the tool, send the `tool_result`, get the final answer |
| 40–45 | Notes |

---

## Concepts

- A **tool** is two things: (1) a **definition** you send to the API —
  `name`, `description`, `input_schema` (JSON Schema); and (2) a **function in
  your code** that actually does the work. The model never runs code — it only
  *asks* you to, by name, with arguments.
- When the model wants a tool, the response has **`stop_reason == "tool_use"`**
  and `content` contains a `tool_use` block: `.id`, `.name`, `.input` (already a
  dict).
- You run the matching function, then send a **new `user` message** containing a
  `tool_result` block: `{"type": "tool_result", "tool_use_id": <id>,
  "content": <string result>}`. Add `"is_error": true` if it failed.
- The model reads the result and usually replies with `stop_reason ==
  "end_turn"` and the final text.
- `description` is prompt engineering: it's how the model decides *whether* and
  *how* to call the tool. Vague description → wrong or skipped calls.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Tool use (function calling) overview* and *How to implement
  tool use*: <https://docs.anthropic.com/en/docs/build-with-claude/tool-use>.
- Anthropic — *courses* repo, the **Tool use** course:
  <https://github.com/anthropics/courses>.
- Anthropic Cookbook — `tool_use/` notebooks:
  <https://github.com/anthropics/anthropic-cookbook>.

**Video (pick one, ~15–30 min):**
- Search *"Anthropic Claude tool use python tutorial"* — pick one using the raw
  `anthropic` SDK, not a framework.

---

## Track_B link (step 3)

**None.** Defining a schema and wiring a function is engineering. Note "no
Track_B link" and continue.

---

## Worked example — one round trip, by hand

`code/single_tool.py`:

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

TOOLS = [{
    "name": "get_weather",
    "description": "Get the current temperature for a city, in Celsius.",
    "input_schema": {
        "type": "object",
        "properties": {"city": {"type": "string", "description": "City name"}},
        "required": ["city"],
        "additionalProperties": False,
    },
}]

def get_weather(city: str) -> str:            # the real function you own
    fake = {"Paris": 14, "Lagos": 31, "Oslo": 3}
    return f"{fake.get(city, 20)} C"

messages = [{"role": "user", "content": "What's the weather in Lagos right now?"}]

r1 = client.messages.create(model="claude-opus-5", max_tokens=400,
                            tools=TOOLS, messages=messages)
print("turn 1 stop_reason:", r1.stop_reason)          # -> tool_use
tu = next(b for b in r1.content if b.type == "tool_use")
print("wants:", tu.name, tu.input)                     # -> get_weather {'city': 'Lagos'}

# run it, feed the result back
result = get_weather(**tu.input)
messages.append({"role": "assistant", "content": r1.content})
messages.append({"role": "user", "content": [
    {"type": "tool_result", "tool_use_id": tu.id, "content": result}
]})

r2 = client.messages.create(model="claude-opus-5", max_tokens=400,
                            tools=TOOLS, messages=messages)
print("turn 2 stop_reason:", r2.stop_reason)           # -> end_turn
print(r2.content[0].text)
```

**Expected output** (wording varies):

```
turn 1 stop_reason: tool_use
wants: get_weather {'city': 'Lagos'}
turn 2 stop_reason: end_turn
It's currently about 31 C in Lagos.
```

Read it: the model **paused** to ask for a tool (turn 1), you executed it and
appended both the assistant's `tool_use` and your `tool_result`, and the model
**resumed** with the answer (turn 2). That pause/resume is the entire mechanic
an agent loop automates.

---

## Build

Extend `single_tool.py`: add a second required field to the schema
(`units: "C" | "F"`), regenerate, and confirm the model now fills it. Then
**break it on purpose**:
- delete the `description` → watch the model call it wrong or not at all.
- return a `tool_result` with a wrong `tool_use_id` → read the API error.
- skip appending `r1.content` (the assistant turn) → read that error too.

---

## Quick test (step 7 — answer from memory, then check)

1. What two separate things make up "a tool"?
2. What is `stop_reason` when the model wants a tool, and where are the details?
3. What message role carries a `tool_result`, and which id must it reference?
4. Before sending the `tool_result`, what else must you append to `messages`?
5. Why does the tool `description` matter for correctness?

<details><summary>Answers</summary>

1. A **definition** sent to the API (`name`, `description`, `input_schema`) and
   a **function in your code** that performs the work.
2. `"tool_use"`. The `tool_use` block in `content` has `.id`, `.name`,
   `.input` (a dict).
3. A `user` message, containing a `tool_result` block whose `tool_use_id`
   matches the `tool_use` block's `.id`.
4. The assistant turn — `{"role": "assistant", "content": r1.content}` — so the
   `tool_result` has something to answer.
5. It's the only signal the model has for *whether* and *how* to call the tool;
   a vague description causes skipped or malformed calls.

</details>

---

## Done when

- [ ] `single_tool.py` completes a `tool_use` → `tool_result` → `end_turn` cycle.
- [ ] You've read a real `tool_use` block's `.name` and `.input`.
- [ ] You've seen at least two of the deliberate breakages and their errors.
- [ ] You can recite the cycle without looking.

## Pitfalls

- **`.input` is already a dict** — don't `json.loads` it. (Do avoid raw string
  matching on the serialized form; escaping varies.)
- **Forgetting the assistant turn** before the `tool_result` is the #1 first
  error — the conversation must read user → assistant(tool_use) → user(result).
- **`tool_result.content` is a string** (or a list of blocks), not a raw object.

## Carries to next session

You've done one round trip by hand. Session 2 wraps it in a `while` loop so the
model can take many tool steps before answering.
