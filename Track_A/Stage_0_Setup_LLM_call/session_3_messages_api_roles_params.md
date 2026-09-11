# Session 3 — Messages API: Roles & Parameters (~45 min)

**Objective:** understand the `messages` list, the `system` prompt, and the
core sampling parameters. Build a short scripted multi-turn conversation.

**What you'll learn:**
- The `messages` list: alternating roles, and why the model is stateless
- The `system` prompt vs. a message
- `max_tokens`, `temperature`, and `stop_sequences`

**Prerequisites:** Session 2 complete (`hello_claude.py` works).

**Method:** run this session with the 7-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 2's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Roles: `system`, `user`, `assistant` — what each is for |
| 10–25 | Build `code/roles_demo.py` — a 3-turn conversation |
| 25–40 | Parameter sweep: `temperature`, `max_tokens`, `stop_sequences` |
| 40–45 | Write observations in `notes.md` |

---

## Concepts

### The `messages` list

A conversation is a Python list of `{"role": ..., "content": ...}` dicts that
**alternates** `user` / `assistant`:

```python
messages = [
    {"role": "user", "content": "My name is Jay."},
    {"role": "assistant", "content": "Nice to meet you, Jay."},
    {"role": "user", "content": "What's my name?"},
]
```

The model is stateless — it "remembers" only what you resend in `messages`
every call. To hold a conversation, you append the model's reply to the list
and send the whole thing again. (Managing that growth is a Stage 3 topic.)

### The `system` prompt

Passed as a top-level `system=` argument, *not* as a message. It sets role,
tone, constraints, and standing instructions:

```python
resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=300,
    system="You are a terse assistant. Answer in one sentence, no preamble.",
    messages=[{"role": "user", "content": "Explain embeddings."}],
)
```

### Parameters worth knowing now

| Param | Effect |
|-------|--------|
| `max_tokens` (required) | Hard ceiling on output length. Hitting it truncates. |
| `temperature` (0.0–1.0) | 0 = near-deterministic, focused. Higher = more varied/creative. Default is 1.0. |
| `stop_sequences` | List of strings; generation halts when one appears. `stop_reason` becomes `"stop_sequence"`. |
| `system` | Standing instructions (above). |

(There's also `top_p` / `top_k` — leave them alone; tune `temperature` only.)

---

## Build: `code/roles_demo.py`

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

SYSTEM = "You are a helpful study partner for someone learning to build AI agents."

# Start a conversation and keep appending to it.
messages = [
    {"role": "user", "content": "I'm on Stage 0: first LLM call. What should I make sure I understand before Stage 1?"},
]

def turn(messages):
    resp = client.messages.create(
        model="claude-opus-5",
        max_tokens=400,
        temperature=0.3,
        system=SYSTEM,
        messages=messages,
    )
    reply = resp.content[0].text
    messages.append({"role": "assistant", "content": reply})
    print("\nASSISTANT:", reply)
    print(f"[tokens in={resp.usage.input_tokens} out={resp.usage.output_tokens}]")
    return messages

messages = turn(messages)

# Follow-up that only makes sense if the prior turn is in context:
messages.append({"role": "user", "content": "Of those, which is most likely to trip me up? Just name one."})
messages = turn(messages)
```

Run it. Confirm the second answer refers back to the first — proof that context
comes from the `messages` list you resend.

---

## Parameter sweep (25–40)

1. Set `temperature=0.0`, run `roles_demo.py` twice. Answers should be nearly
   identical.
2. Set `temperature=1.0`, run twice. Answers should visibly differ.
3. Add `stop_sequences=["."]` to one call — watch it stop at the first period
   and `stop_reason` become `"stop_sequence"`.
4. Note how `input_tokens` grows on the second turn (it includes the whole
   conversation so far).

Write what you saw in `notes.md`.

---

## Learning resources

**Primary (official, stable):**
- Anthropic — *Anthropic API fundamentals* course, notebooks **"The messages
  format"** and **"Parameters"** (`temperature`, `max_tokens`,
  `stop_sequences`): <https://github.com/anthropics/courses> →
  `anthropic_api_fundamentals`.
- Anthropic docs — *System prompts* / *Giving Claude a role*:
  <https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/system-prompts>.
- Anthropic — *Prompt engineering interactive tutorial*, first few chapters
  (message structure, system prompts): <https://github.com/anthropics/courses>
  → `prompt_engineering_interactive_tutorial`.

**Video (pick one, ~15–30 min):**
- Search *"LLM temperature top_p explained"* — any clear visual explanation of
  how sampling parameters change output (concept transfers directly to Claude).
- **IBM Technology** channel — search *"IBM temperature LLM"* for a short
  conceptual take.

---

## Track_B link (step 3)

**Light, non-blocking.** `temperature` and sampling are about drawing the next
token from a **probability distribution** — higher temperature flattens the
distribution (more surprising tokens get picked), lower sharpens it toward the
most likely token. The fundamental is in `Track_B/Math_stat` probability
(distributions, sampling).

**Decision:** you can finish this session treating sampling as a black box —
run the `temperature` 0 vs 1 experiment and observe the behavior. Write
*"revisit in Track_B: probability distributions & how temperature reshapes
them"* in `notes.md`. **Do not switch now** unless you're genuinely curious and
have time — it isn't blocking.

---

## Worked example — one script, every concept

`code/params_demo.py`:

```python
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

def ask(system, messages, **params):
    resp = client.messages.create(
        model="claude-opus-5", max_tokens=params.pop("max_tokens", 200),
        system=system, messages=messages, **params,
    )
    return resp

# 1. system prompt changes behavior for the SAME user message
q = [{"role": "user", "content": "What is a vector database?"}]
print("TERSE  :", ask("Answer in exactly one sentence.", q).content[0].text)
print("VERBOSE:", ask("Answer in a detailed paragraph with an analogy.", q).content[0].text[:120], "...")

# 2. temperature: determinism vs variety
for t in (0.0, 1.0):
    outs = {ask(None, q, temperature=t, max_tokens=40).content[0].text for _ in range(2)}
    print(f"temp={t}: {len(outs)} distinct answer(s) out of 2 runs")

# 3. multi-turn: the model only knows what you resend
convo = [{"role": "user", "content": "Remember the number 42."}]
convo.append({"role": "assistant", "content": ask(None, convo).content[0].text})
convo.append({"role": "user", "content": "What number did I say?"})
print("RECALL :", ask(None, convo).content[0].text)

# 4. stop_sequences
r = ask(None, [{"role": "user", "content": "List three fruits, comma separated."}],
        stop_sequences=[","], max_tokens=50)
print("STOPPED:", repr(r.content[0].text), "| stop_reason =", r.stop_reason)
```

**Expected output** (wording varies; the *shape* is the point):

```
TERSE  : A vector database is a database that stores and searches data as high-dimensional numeric vectors by similarity.
VERBOSE: Imagine a library where books are placed on shelves not by title but by how similar their ideas are ...
temp=0.0: 1 distinct answer(s) out of 2 runs
temp=1.0: 2 distinct answer(s) out of 2 runs
RECALL : You said the number 42.
STOPPED: 'Apple' | stop_reason = stop_sequence
```

Takeaways: (1) `system` steers style without touching the user turn; (2)
`temperature=0` is ~reproducible, `1.0` varies; (3) "memory" is just the
`messages` list you resend; (4) `stop_sequences` cuts generation and is
reported via `stop_reason`.

---

## Quick test (step 6 — answer from memory, then check)

1. A model is stateless. So how does turn 3 "know" what happened in turn 1?
2. Where does the system prompt go in the request, and what is it for?
3. What are the ordering rules for the `messages` list?
4. Practical difference between `temperature=0` and `temperature=1`?
5. You pass `stop_sequences=["."]`. What happens to the output and to
   `stop_reason`? And why does `input_tokens` climb each turn?

<details><summary>Answers</summary>

1. It doesn't "know" anything — you resend the entire `messages` list every
   call. All context is what you include.
2. The top-level `system=` argument (not a message). It sets role, tone, and
   standing instructions/constraints.
3. Must start with `role: "user"` and alternate user / assistant. Two
   same-role messages in a row is an error.
4. `0` ≈ deterministic and repeatable; `1` produces visibly different output
   across runs.
5. Generation stops at the first `.`; `stop_reason` becomes `"stop_sequence"`.
   `input_tokens` climbs because every call resends the whole growing history.

</details>

---

## Done when

- [ ] `roles_demo.py` runs a 3-turn conversation where turn 2 depends on turn 1.
- [ ] You can explain why the model "remembers" earlier turns (you resend them).
- [ ] You've seen `temperature=0` vs `1` produce different variability.
- [ ] You've seen `input_tokens` rise as the conversation grows.

## Pitfalls

- **Roles must alternate.** Two `user` messages in a row (without an `assistant`
  between) is an error. First message must be `user`.
- **`system` is not a message.** Putting `{"role": "system", ...}` in `messages`
  is not how the base API works — use the `system=` argument.
- **Forgetting to append the reply** means every turn starts from scratch and
  the model looks like it has amnesia.

## Carries to next session

You can shape input and read output. Next: stream the output as it's generated
instead of waiting for the whole block — and that becomes the Stage 0
deliverable.
