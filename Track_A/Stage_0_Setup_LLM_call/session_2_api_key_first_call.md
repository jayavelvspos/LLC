# Session 2 — API Key & First Authenticated Call (~45 min)

**Objective:** get an API key, load it safely from `.env`, and make your first
successful `messages.create` call. Understand every field that comes back.

**Prerequisites:** Session 1 complete (venv active, SDK installed, `.env` ready).

**Method:** run this session with the 7-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 1's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Create an API key in the Anthropic Console, put it in `.env` |
| 10–25 | Write `code/hello_claude.py` — load key, create client, one call |
| 25–40 | Inspect the response object field by field |
| 40–45 | Trigger and read one error on purpose |

---

## Steps

### 1. Get the key (0–10)

1. Go to `console.anthropic.com` → **API Keys** → **Create Key**.
2. Copy it once (you can't see it again) and paste into `.env`:

```
ANTHROPIC_API_KEY=sk-ant-...
```

3. Make sure you have a little credit / billing set up, or calls return a 400.

### 2. First call (10–25)

`code/hello_claude.py`:

```python
import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()  # reads .env into environment variables

client = Anthropic()  # picks up ANTHROPIC_API_KEY from the environment

resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=200,
    messages=[
        {"role": "user", "content": "In two sentences, what is an LLM agent?"}
    ],
)

print(resp.content[0].text)
```

Run it:

```powershell
python code\hello_claude.py
```

You should see two sentences of text.

### 3. Inspect the response (25–40)

Add this and re-run:

```python
print("id:        ", resp.id)
print("model:     ", resp.model)
print("role:      ", resp.role)
print("stop_reason:", resp.stop_reason)
print("usage:     ", resp.usage)
print("content:   ", resp.content)
```

Understand each:

- **`resp.content`** — a *list* of content blocks, not a string. Plain text
  answers are one `TextBlock`; `.content[0].text` is the text. Later stages add
  `tool_use` blocks to this list.
- **`resp.stop_reason`** — why generation stopped:
  - `end_turn` — the model finished normally.
  - `max_tokens` — you hit the `max_tokens` cap; output is cut off mid-thought.
  - `tool_use` — the model wants to call a tool (Stage 1).
- **`resp.usage`** — `input_tokens` and `output_tokens` for this call. This is
  what you'll turn into a dollar figure in Session 5.
- **`resp.id`** / **`resp.model`** — useful for logging and debugging later.

Try setting `max_tokens=10` and re-run: watch `stop_reason` flip to
`max_tokens` and the answer get chopped.

### 4. Break it on purpose (40–45)

Temporarily set a bad key in code (`Anthropic(api_key="sk-ant-bogus")`) and run.
Note the exception type and message. Restore the real setup after. Knowing what
an auth failure looks like now saves confusion later.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Anthropic API fundamentals* course, notebooks **"Getting started"
  + "The messages format"**: <https://github.com/anthropics/courses> →
  `anthropic_api_fundamentals`. Your first call and the response shape,
  step by step.
- Anthropic docs — *Messages API* reference (skim the "Response" section for the
  field list): <https://docs.anthropic.com/en/api/messages>.
- Anthropic Cookbook — the intro notebooks under
  <https://github.com/anthropics/anthropic-cookbook>.

**Video (pick one, ~15–30 min):**
- **Anthropic** (official YouTube channel) — search *"Anthropic Claude API
  quickstart"*.
- Search *"Claude API Python tutorial 2025"* — pick one that uses the
  `anthropic` package directly (not LangChain, not a wrapper).

---

## Track_B link (step 3)

**None.** Sending an authenticated HTTP request and reading fields off the
response object is engineering, not math. Note "no Track_B link" and continue.

---

## Worked example — read every field of a response

`code/inspect_response.py`:

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=60,
    messages=[{"role": "user", "content": "Name three primary colors."}],
)

print("id          :", resp.id)
print("model       :", resp.model)
print("role        :", resp.role)
print("stop_reason :", resp.stop_reason)
print("block type  :", resp.content[0].type)
print("text        :", resp.content[0].text)
print("input_tokens:", resp.usage.input_tokens)
print("output_tokens:", resp.usage.output_tokens)
```

**Expected output** (text and token counts vary slightly):

```
id          : msg_01AbCdEfGhIjKlMnOpQrStUv
model       : claude-opus-5
role        : assistant
stop_reason : end_turn
block type  : text
text        : Red, blue, and yellow are the three primary colors.
input_tokens: 14
output_tokens: 13
```

Now set `max_tokens=4` and re-run — `stop_reason` becomes `max_tokens` and the
`text` is chopped mid-sentence. That contrast is the whole lesson: `stop_reason`
tells you *why* the model stopped, and `end_turn` is the only "clean" one for
plain text.

---

## Quick test (step 6 — answer from memory, then check)

1. `resp.content` — what type is it, and how do you get the answer string?
2. Name the `stop_reason` values and what each means.
3. Where does `Anthropic()` get the API key from, and how did it get there?
4. What's in `resp.usage`, and why will you care in Session 5?
5. Is `max_tokens` optional? What happens if the answer would run longer than it?

<details><summary>Answers</summary>

1. A **list** of content blocks (not a string). For a plain answer,
   `resp.content[0].text`.
2. `end_turn` = finished normally; `max_tokens` = hit the output cap, truncated;
   `tool_use` = the model wants to call a tool (Stage 1).
3. From the `ANTHROPIC_API_KEY` environment variable, which `load_dotenv()`
   loaded from `.env`.
4. `input_tokens` and `output_tokens` for the call — the raw numbers you turn
   into a dollar cost.
5. Required. Output is cut off mid-text and `stop_reason` becomes `max_tokens`.

</details>

---

## Done when

- [ ] `hello_claude.py` prints a real answer from `claude-opus-5`.
- [ ] You can say what `resp.content`, `resp.stop_reason`, and `resp.usage` hold.
- [ ] You've seen `stop_reason == "max_tokens"` by forcing it.
- [ ] You've seen one authentication error and recognize it.

## Pitfalls

- **`resp.content` is a list.** `print(resp.content)` shows block objects;
  `resp.content[0].text` is the string.
- **`max_tokens` is required** and is a hard ceiling — the model isn't "aiming"
  for it, it just gets cut. Don't set it tiny unless you mean to.
- **Key not loading:** if `Anthropic()` raises about a missing key, `load_dotenv()`
  didn't find `.env` (wrong working directory) or the line in `.env` is
  misspelled.

## Carries to next session

A working client and a mental model of the response object. Next: shaping the
*input* with roles and parameters.
