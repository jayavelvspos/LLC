# Session 1 — LCEL & Prompt Templates (~45 min)

**Objective:** build a chain with the LangChain Expression Language (`|`),
parameterise it with `ChatPromptTemplate`, parse the output into a typed object,
and run it over many inputs with `.batch` / `.stream`.

**Prerequisites:** Stage 5 complete. `pip install langchain langchain-anthropic`.

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md).

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | What LCEL is; the `Runnable` interface |
| 10–30 | `code/lcel_chain.py` — `prompt | model | parser`, then `.batch` |
| 30–40 | Add a parser; break the template; stream |
| 40–45 | Notes |

---

## Concepts  <!-- step 2 -->

- **LCEL** composes **Runnables** with `|`. `a | b` means "run `a`, feed its
  output to `b`". Every piece — a prompt template, a model, an output parser, a
  plain function (`RunnableLambda`) — is a Runnable with the same interface:
  `.invoke(x)`, `.batch([x, ...])`, `.stream(x)`, plus async `.ainvoke` etc.
- **`ChatPromptTemplate`** turns `{variables}` + role structure into messages:
  `ChatPromptTemplate.from_messages([("system", "..."), ("human", "{question}")])`.
  `.invoke({"question": ...})` → a list of messages.
- **Output parsers** are the last link: `StrOutputParser` (just the text),
  `PydanticOutputParser` / `.with_structured_output(Model)` (a validated
  object), `JsonOutputParser`.
- A chain is itself a Runnable — you can nest chains, put them in a dict for
  `RunnableParallel` (Session 2), or wrap them as a LangGraph node.
- **Why bother** (vs raw SDK calls): uniform `.batch`/`.stream`/async, automatic
  tracing hooks (Session 4), and swappable pieces (change the model, keep the
  chain).

---

## Learning resources  <!-- step 2 -->

**Primary (official, stable):**
- LangChain docs — *LangChain Expression Language (LCEL)* concept page:
  <https://python.langchain.com/docs/concepts/lcel/>.
- LangChain docs — *Prompt templates* and *Output parsers*:
  <https://python.langchain.com/docs/concepts/prompt_templates/>.

**Video (pick one, ~10–20 min):**
- Search *"LangChain LCEL explained"* — focus on the `|` pipe and the Runnable
  interface, not the older `LLMChain` API.

**Reference:**
- `langchain-anthropic` README — `ChatAnthropic(model="claude-opus-5")`.

---

## Track_B link (step 3)

**None.** LCEL is function composition with a shared interface — engineering,
not maths. Note "no Track_B link" and continue.

---

## Worked example — a typed extraction chain  <!-- step 4 -->

`code/lcel_chain.py`:

```python
from pydantic import BaseModel, Field
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate

class Ticket(BaseModel):
    category: str = Field(description="one of: bug, billing, feature, other")
    urgency: int = Field(description="1 (low) to 5 (critical)")
    summary: str

model = ChatAnthropic(model="claude-opus-5", max_tokens=1024)
prompt = ChatPromptTemplate.from_messages([
    ("system", "Classify the support message into a Ticket."),
    ("human", "{message}"),
])
chain = prompt | model.with_structured_output(Ticket)

print(chain.invoke({"message": "I've been charged twice this month, fix it now"}))

msgs = [
    {"message": "the export button does nothing on Safari"},
    {"message": "can you add dark mode?"},
]
for t in chain.batch(msgs):
    print(t.category, t.urgency, "|", t.summary)
```

**Expected output** (values vary):

```
category='billing' urgency=4 summary='Customer double-charged this month'
bug 2 | Export button unresponsive in Safari
feature 1 | Request for a dark mode option
```

Read it: the same `chain` object handled one input (`.invoke`) and a list
(`.batch`) with no code change, and every result is a validated `Ticket`, not a
string you have to parse.

---

## Build: `code/lcel_chain.py`  <!-- step 5 -->

Build the chain above. Experiments:
1. **Swap the parser.** Replace `.with_structured_output(Ticket)` with
   `| StrOutputParser()`. Note what `.invoke` returns now, and why the typed
   version is safer downstream.
2. **Break the template.** Reference `{messge}` (typo) in the prompt and call
   `.invoke({"message": ...})`. Read the error — LCEL fails at template render,
   before any API call. Cheap failure.
3. **Stream.** Build a `prompt | model | StrOutputParser()` chain and iterate
   `chain.stream({"message": ...})`. Confirm you get text chunks (same idea as
   Stage 0 Session 4, now framework-level).

---

## Quick test (step 7 — answer from memory, then check)

1. What does `a | b` mean in LCEL?
2. Name four methods every Runnable has.
3. What does `ChatPromptTemplate.from_messages([...]).invoke({...})` return?
4. Two things an output parser can give you instead of a raw string.
5. One concrete reason to use an LCEL chain instead of a raw `client.messages.create`.

<details><summary>Answers</summary>

1. Run `a`, pass its output as the input to `b` — left-to-right composition.
2. `.invoke`, `.batch`, `.stream`, `.ainvoke` (also `.abatch`, `.astream`).
3. A list of formatted messages (system/human/…), ready to pass to a chat model.
4. A validated Pydantic object (`with_structured_output` / `PydanticOutputParser`)
   or parsed JSON (`JsonOutputParser`); also just the trimmed text
   (`StrOutputParser`).
5. Any one: uniform `.batch`/`.stream`/async, automatic tracing, swappable
   model/parser without touching call sites.

</details>

---

## Done when  <!-- step 8 -->

- [ ] `lcel_chain.py` runs a `prompt | model | parser` chain via `.invoke` and
      `.batch`.
- [ ] You've seen a template typo fail *before* an API call.
- [ ] You've streamed a chain's output.
- [ ] You can explain what `|` builds, from memory.

## Pitfalls

- **Mixing old and new APIs** — `LLMChain`, `SequentialChain` are legacy; use
  `|` and Runnables.
- **Forgetting the parser** — a bare `prompt | model` returns an
  `AIMessage`, not a string; add `StrOutputParser` or a structured parser.
- **`with_structured_output` on an unsupported combo** — check it returns your
  model type, not a dict, for your LangChain version.

## Carries to next session

A chain is a Runnable. Session 2 composes Runnables into **branches** (routing)
and **parallel** groups (fan-out/fan-in).
