# Session 4 — Streaming + the Stage 0 Build (~45 min)

**Objective:** stream a response token-by-token and package it as the Stage 0
deliverable: a script that takes a prompt and prints a streamed reply.

**Prerequisites:** Session 3 complete.

**Method:** run this session with the 7-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 3's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Why streaming — timeouts and UX |
| 10–30 | Build `code/stream_prompt.py` |
| 30–40 | Handle the prompt input (CLI arg or `input()`) and edge cases |
| 40–45 | Run it a few times, note the feel vs. non-streaming |

---

## Concepts

### Why stream

- **UX:** output appears immediately instead of after a multi-second pause.
- **Timeouts:** long or large responses can exceed HTTP timeouts on a single
  blocking request. Streaming keeps the connection alive. (This matters more as
  outputs get bigger in later stages.)

### The streaming API

Use the `client.messages.stream(...)` context manager:

```python
with client.messages.stream(
    model="claude-opus-5",
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for chunk in stream.text_stream:      # yields text as it arrives
        print(chunk, end="", flush=True)
    final = stream.get_final_message()     # full Message, with .usage etc.
```

- `stream.text_stream` yields plain text pieces — good enough for Stage 0.
- `stream.get_final_message()` gives you the assembled `Message` once done, so
  you can still read `usage` and `stop_reason` (used heavily in Session 5).

---

## Build: `code/stream_prompt.py`

```python
import sys
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-opus-5"

def get_prompt() -> str:
    # Prompt from command-line args if given, else ask interactively.
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:])
    return input("Prompt: ").strip()

def main() -> None:
    prompt = get_prompt()
    if not prompt:
        print("No prompt given.")
        sys.exit(1)

    print(f"\n--- {MODEL} ---\n")
    with client.messages.stream(
        model=MODEL,
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}],
    ) as stream:
        for chunk in stream.text_stream:
            print(chunk, end="", flush=True)
        final = stream.get_final_message()

    print("\n")
    print(f"[stop_reason={final.stop_reason} "
          f"in={final.usage.input_tokens} out={final.usage.output_tokens}]")

if __name__ == "__main__":
    main()
```

Run it both ways:

```powershell
python code\stream_prompt.py "Give me a 5-step plan to learn RAG."
python code\stream_prompt.py
```

---

## Compare to non-streaming (40–45)

Briefly: call `client.messages.create(...)` with the same prompt and notice you
wait, then get everything at once. Streaming is the same output, delivered
progressively. Jot the difference in `notes.md`.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Streaming Messages* (event types, SDK helpers):
  <https://docs.anthropic.com/en/docs/build-with-claude/streaming>.
- Anthropic — *Anthropic API fundamentals* course, the **streaming** notebook:
  <https://github.com/anthropics/courses> → `anthropic_api_fundamentals`.
- `anthropic` SDK README, *Streaming responses* section:
  <https://github.com/anthropics/anthropic-sdk-python#streaming-responses>
  (`text_stream`, `get_final_message`).

**Video (pick one, ~10–20 min):**
- Search *"OpenAI vs Anthropic streaming API python"* or *"stream LLM response
  python"* — the mechanics (iterate chunks, `flush=True`) are the same across
  providers; focus on the loop pattern.

---

## Track_B link (step 3)

**None.** Streaming is a transport and UX concern — server-sent events, an
iterator, terminal buffering. No `Track_B/Math_stat` fundamental underneath.
Note "no Track_B link" and continue.

---

## Worked example — streaming vs. blocking, side by side

`code/stream_vs_block.py`:

```python
import time
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
PROMPT = "Explain what an embedding is, in about 80 words."

# --- blocking ---
t0 = time.perf_counter()
resp = client.messages.create(
    model="claude-opus-5", max_tokens=300,
    messages=[{"role": "user", "content": PROMPT}],
)
print(f"[blocking] nothing visible for {time.perf_counter()-t0:.2f}s, then:")
print(resp.content[0].text, "\n")

# --- streaming ---
t0 = time.perf_counter()
first = None
with client.messages.stream(
    model="claude-opus-5", max_tokens=300,
    messages=[{"role": "user", "content": PROMPT}],
) as stream:
    for chunk in stream.text_stream:
        if first is None:
            first = time.perf_counter() - t0
            print(f"[streaming] first text after {first:.2f}s:")
        print(chunk, end="", flush=True)
    final = stream.get_final_message()
print(f"\n[streaming] done in {time.perf_counter()-t0:.2f}s "
      f"(out_tokens={final.usage.output_tokens})")
```

**Expected output** (timings vary by network/load):

```
[blocking] nothing visible for 4.11s, then:
An embedding is a list of numbers that represents a piece of data ...

[streaming] first text after 0.62s:
An embedding is a list of numbers ...        <- appears word by word
[streaming] done in 4.05s (out_tokens=95)
```

Same total time, same text — but streaming shows something in ~0.6s instead of
a 4s dead stare. That's why every chat UI streams.

---

## Quick test (step 6 — answer from memory, then check)

1. Give the two reasons to stream instead of making a blocking call.
2. Which construct gives you (a) incremental text and (b) the final
   `usage` / `stop_reason`?
3. Why `print(chunk, end="", flush=True)` — what does each of `end=""` and
   `flush=True` do?
4. Does streaming change total time or total token cost versus a blocking call?
5. Where in the code must `get_final_message()` be called?

<details><summary>Answers</summary>

1. (a) UX — first output in a fraction of a second instead of after a long
   pause; (b) it keeps the connection alive so long/large responses don't hit
   HTTP timeouts.
2. (a) the `stream.text_stream` iterator; (b) `stream.get_final_message()`.
3. `end=""` suppresses the newline Python adds per `print`; `flush=True` forces
   the terminal to show each piece immediately instead of buffering.
4. No — identical output, identical cost. Only the delivery is progressive
   (first token arrives much sooner).
5. Inside the `with client.messages.stream(...)` block, after the iteration
   loop.

</details>

---

## Done when

- [ ] `stream_prompt.py "question"` streams an answer to the terminal live.
- [ ] With no argument, it prompts interactively.
- [ ] After streaming it prints `stop_reason` and input/output token counts.
- [ ] You can explain the two reasons streaming is used.

## Pitfalls

- **`flush=True` matters.** Without it, terminal buffering can make output
  appear in chunks or all at once, hiding the streaming effect.
- **Don't rebuild what the SDK gives you.** Use `stream.text_stream` and
  `stream.get_final_message()` — don't hand-assemble events into a string.
- **`get_final_message()` is called inside the `with` block**, after the loop.

## Carries to next session

`stream_prompt.py` works but only reports raw token counts. Session 5 turns
those into money and adds latency measurement — completing Stage 0.
