# Session 3 — Context Growth & Summarization (~45 min)

**Objective:** stop the message history (and per-turn cost) from growing without
bound — trim old turns, and replace them with a running summary.

**Prerequisites:** Session 2 complete. Re-read Stage 0 Session 5 (token cost).

**Method:** run this session with the 8-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why long threads get expensive and slow (input tokens ↑ every turn) |
| 10–25 | `trim_messages` — keep last N / last K tokens |
| 25–40 | A summarization node: fold old turns into a `summary`, drop them |
| 40–45 | Notes |

---

## Concepts

- Every turn resends the whole history as **input tokens**. A 100-turn thread
  can cost more in input than output. Latency rises too (TTFT grows with input).
- **Trimming:** `trim_messages(messages, max_tokens=..., strategy="last",
  token_counter=model)` keeps the most recent messages that fit. Cheap, lossy —
  old detail is just gone.
- **Summarization:** when history exceeds a threshold, call the model once to
  summarize the oldest chunk into a paragraph, store it in a `summary` state
  key, and remove those messages (return `RemoveMessage(id=...)` via the
  `add_messages` reducer). Prepend the summary to the system prompt.
- Trade-off: summarizing costs one extra model call now to save many
  inflated calls later — an expected-value decision (Track_B link).
- Keep the **first** user turn and the last few verbatim; summarize the middle.

---

## Learning resources

**Primary (official, stable):**
- LangChain Academy — *Introduction to LangGraph*, **Module 2** ("Chatbot with
  message summarization"): <https://academy.langchain.com/courses/intro-to-langgraph>.
- LangGraph docs — *Manage conversation history* / *Add summary of conversation*:
  <https://langchain-ai.github.io/langgraph/how-tos/memory/>.
- LangChain docs — `trim_messages` reference.

**Video (pick one, ~10–20 min):**
- **LangChain** channel — search *"LangGraph message summarization trim"*.

---

## Track_B link (step 3)

**Light, non-blocking.** Two angles: (a) the token-budget arithmetic is Stage 0
Session 5 material; (b) *when* to summarize is an expected-value call — cost of
one summary call now vs expected cost of carrying the history for the rest of
the thread — which is `Track_B/Math_stat/05_decision_and_orchestration_math`.
Note *"revisit in Track_B: expected value for the summarize/keep decision"* and
continue.

---

## Worked example — summarize when the thread gets long

```python
from langchain_core.messages import RemoveMessage

SUMMARIZE_AFTER = 12   # messages

def maybe_summarize(state):
    msgs = state["messages"]
    if len(msgs) <= SUMMARIZE_AFTER:
        return {}
    old, keep = msgs[:-6], msgs[-6:]
    prompt = ("Summarize this conversation so far in <=120 words, keeping "
              "names, decisions, and open tasks:\n" +
              "\n".join(f"{m.type}: {m.content}" for m in old))
    summary = plain_model.invoke(prompt).content
    return {"summary": summary,
            "messages": [RemoveMessage(id=m.id) for m in old]}
```

Wire `maybe_summarize` as a node before `model`; have `call_model` prepend
`state.get("summary","")` to the system prompt.

**Expected output** (after 14 turns, `stream_mode="updates"`):

```
{'maybe_summarize': {'summary': 'Jay is building a RAG agent; chose Chroma; ...',
                     'messages': [RemoveMessage x8]}}
{'model': {'messages': [AIMessage(content='...')]}}
# get_state shows 6 kept messages + a summary, not 14
```

Read it: eight old messages were removed and compressed into `summary`;
subsequent turns carry the paragraph instead of the raw history, so input tokens
plateau instead of climbing.

---

## Build

- Add `trim_messages` first (keep last ~800 tokens); run a 20-turn thread and
  chart input tokens per turn (should flatten).
- Then add the summarization node; compare: what does the agent *forget* under
  trimming vs summarization? Ask a question about turn 2 after turn 20 under
  each.
- Log per-turn `input_tokens` before/after — put the two curves in `notes.md`.

---

## Quick test (step 7 — answer from memory, then check)

1. Why does a long thread get expensive even if answers stay short?
2. What does `trim_messages` do, and what does it cost you?
3. How does summarization remove messages from state?
4. What's the trade-off that makes summarization an expected-value decision?
5. Which messages should you keep verbatim rather than summarize?

<details><summary>Answers</summary>

1. The full history is resent as input tokens every turn; input cost and TTFT
   grow with thread length.
2. Keeps the most recent messages within a token/'count budget; older detail is
   dropped entirely (lossy).
3. A node returns `RemoveMessage(id=...)` entries; the `add_messages` reducer
   applies the removals, and the summary text is stored in a separate key.
4. One extra model call now (the summary) vs the expected extra cost of carrying
   the raw history across all remaining turns.
5. The first user turn (task framing) and the last few turns (immediate
   context).

</details>

---

## Done when

- [ ] Per-turn input tokens flatten on a long thread instead of climbing.
- [ ] You've compared what trimming forgets vs what summarization keeps.
- [ ] The summary is injected into the system prompt and actually used.
- [ ] You can explain the summarize-vs-keep trade-off from memory.

## Pitfalls

- **Summarizing every turn** — only above a threshold, or you pay the summary
  tax constantly.
- **Dropping the first user turn** — the agent loses the task definition.
- **Counting tokens with the wrong counter** — use the model's tokenizer
  (Stage 0 Session 5 rule).

## Carries to next session

Context is bounded. Session 4 adds a human approval gate before side-effecting
tools.
