# Session 5 — Token Counting, Cost & Latency (~45 min)

**Objective:** measure what a call costs and how long it takes. Extend
`stream_prompt.py` to report tokens, USD cost, time-to-first-token, and total
time. This completes Stage 0.

**Prerequisites:** Session 4 complete (`stream_prompt.py` streams and prints
token counts).

**Method:** run this session with the 7-step loop in
[`_SESSION_METHOD.md`](_SESSION_METHOD.md). Start with step 0 — re-answer
Session 4's Quick test.

---

## Timebox

| Min | Activity |
|-----|----------|
| 0–10 | Count tokens *before* sending with `count_tokens` |
| 10–20 | Pricing math: `usage` → dollars |
| 20–35 | Add latency timing (TTFT + total) to `stream_prompt.py` |
| 35–45 | Run a small comparison, record numbers in `notes.md` |

---

## Concepts

### Counting tokens before you send

Use the API, not a third-party tokenizer (`tiktoken` is OpenAI's and will be
wrong for Claude):

```python
count = client.messages.count_tokens(
    model="claude-opus-5",
    messages=[{"role": "user", "content": prompt}],
)
print(count.input_tokens)  # what this prompt will cost as input
```

Useful for estimating cost and staying under context limits before spending
anything.

### Pricing math

`usage` gives `input_tokens` and `output_tokens`. Prices are per **1 million**
tokens:

| Model | Input $/1M | Output $/1M |
|-------|-----------|-------------|
| `claude-opus-5` | 5.00 | 25.00 |
| `claude-sonnet-5` | 2.00 | 10.00 |
| `claude-haiku-4-5` | 1.00 | 5.00 |

```
cost = (input_tokens / 1_000_000) * input_price
     + (output_tokens / 1_000_000) * output_price
```

Output tokens are ~5x the price of input tokens — long generations dominate the
bill. (Prompt caching and batching cut costs later; not a Stage 0 concern.)

### Latency terms

- **Time to first token (TTFT):** request sent → first text chunk arrives.
  Dominated by model "thinking" / queueing. This is what makes an app feel
  responsive.
- **Total time:** request sent → stream done. Grows with output length.

---

## Build: `code/costs.py`

```python
PRICING = {  # USD per 1M tokens: (input, output)
    "claude-opus-5":   (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_price, out_price = PRICING[model]
    return (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price
```

## Extend `code/stream_prompt.py`

Add timing around the stream and a cost line at the end:

```python
import time
from costs import estimate_cost

# ... inside main(), replacing the stream block ...

start = time.perf_counter()
ttft = None

with client.messages.stream(
    model=MODEL,
    max_tokens=1000,
    messages=[{"role": "user", "content": prompt}],
) as stream:
    for chunk in stream.text_stream:
        if ttft is None:
            ttft = time.perf_counter() - start
        print(chunk, end="", flush=True)
    final = stream.get_final_message()

total = time.perf_counter() - start
usd = estimate_cost(MODEL, final.usage.input_tokens, final.usage.output_tokens)

print("\n")
print(f"[stop_reason={final.stop_reason}]")
print(f"[tokens  in={final.usage.input_tokens}  out={final.usage.output_tokens}]")
print(f"[cost    ${usd:.6f}]")
print(f"[latency ttft={ttft:.2f}s  total={total:.2f}s]")
```

Run it:

```powershell
python code\stream_prompt.py "Explain cosine similarity in 3 sentences."
```

---

## Small comparison (35–45)

Run the *same* prompt against `claude-opus-5` and `claude-haiku-4-5` (change
`MODEL`). Record in `notes.md`:

| Model | in tok | out tok | cost | ttft | total |
|-------|--------|---------|------|------|-------|
| opus-5 | | | | | |
| haiku-4-5 | | | | | |

Now you have a concrete feel for the cost/latency/quality tradeoff you'll be
making for the rest of Track A.

---

## Learning resources

**Primary (official, stable):**
- Anthropic docs — *Token counting* (the `count_tokens` endpoint):
  <https://docs.anthropic.com/en/docs/build-with-claude/token-counting>.
- Anthropic — *Pricing* (current per-model $/1M rates; check this rather than
  trusting a cached table): <https://www.anthropic.com/pricing>.
- Anthropic docs — *Reducing latency*:
  <https://docs.anthropic.com/en/docs/test-and-evaluate/reduce-latency>.
- Anthropic docs — *Models overview* (context windows, which model for what):
  <https://docs.anthropic.com/en/docs/about-claude/models>.

**Video / reading (pick one, ~10–20 min):**
- Search *"time to first token TTFT explained"* — short explainers on the
  latency metrics that matter for LLM apps.
- Search *"how LLM tokens work tokenizer"* — a visual on why token counts ≠
  word counts (Anthropic's tokenizer differs from OpenAI's; that's why you use
  `count_tokens`, not `tiktoken`).

---

## Track_B link (step 3)

**Minimal, non-blocking.** The cost formula is unit arithmetic —
`tokens ÷ 1,000,000 × rate`. Nothing to detour for.

The connection *opens up later*: once you want to reason about the **expected**
cost or latency of a request across a whole workload (a distribution of prompt
sizes and output lengths), that's **expected value** — `Track_B/Math_stat`
probability, and `Track_B/Math_stat/05_decision_and_orchestration_math` for
cost-aware routing between models. Note *"revisit in Track_B: expected value for
cost/latency estimation"* in `notes.md` and finish the session.

---

## Worked example — estimate before you spend, measure after

`code/cost_report.py`:

```python
import time
from dotenv import load_dotenv
from anthropic import Anthropic
from costs import estimate_cost

load_dotenv()
client = Anthropic()
MODEL = "claude-opus-5"
PROMPT = "Summarize the plot of Romeo and Juliet in 120 words."

# 1. ESTIMATE input cost before sending a single billable generation token
pre = client.messages.count_tokens(
    model=MODEL, messages=[{"role": "user", "content": PROMPT}],
)
est_in = estimate_cost(MODEL, pre.input_tokens, 0)
print(f"estimate: {pre.input_tokens} input tokens  ~${est_in:.6f} (input only)")

# 2. RUN with timing
start = time.perf_counter()
ttft = None
with client.messages.stream(
    model=MODEL, max_tokens=400,
    messages=[{"role": "user", "content": PROMPT}],
) as stream:
    for chunk in stream.text_stream:
        if ttft is None:
            ttft = time.perf_counter() - start
    final = stream.get_final_message()
total = time.perf_counter() - start

# 3. ACTUAL cost from usage
u = final.usage
usd = estimate_cost(MODEL, u.input_tokens, u.output_tokens)
print(f"actual  : in={u.input_tokens} out={u.output_tokens}  ${usd:.6f}")
print(f"latency : ttft={ttft:.2f}s  total={total:.2f}s")
print(f"rate    : {u.output_tokens/ (total - ttft):.0f} output tok/s")
```

**Expected output** (numbers vary):

```
estimate: 22 input tokens  ~$0.000110 (input only)
actual  : in=22 out=176  $0.004510
latency : ttft=0.71s  total=3.94s
rate    : ~54 output tok/s
```

Read it: input was trivially cheap to *predict*; the bill is almost entirely
**output** tokens (176 × $25/1M ≫ 22 × $5/1M). `ttft` is the "app feels alive"
number; `total` grows with output length. Swap `MODEL` to `claude-haiku-4-5`
and the same run costs roughly 5× less — that is the tradeoff you now own.

---

## Quick test (step 6 — answer from memory, then check)

1. Why not use `tiktoken` to count tokens for Claude? What do you use instead?
2. Write the cost formula from a response's `usage`.
3. Input or output tokens — which usually dominates the bill, and why?
4. What does TTFT measure, and how is it different from total time?
5. Same prompt on `claude-opus-5` vs `claude-haiku-4-5`: rough cost difference,
   and what are you trading?

<details><summary>Answers</summary>

1. `tiktoken` is OpenAI's tokenizer — wrong counts for Claude. Use
   `client.messages.count_tokens`.
2. `cost = input_tokens/1e6 × input_price + output_tokens/1e6 × output_price`,
   with prices quoted per 1M tokens.
3. Output — it's priced ~5× input per token and generations are often longer
   than the prompt.
4. TTFT = request sent → first streamed text; it's the responsiveness number.
   Total time = request sent → stream finished, and it scales with output
   length.
5. Haiku 4.5 is ~5× cheaper (and usually lower latency); you trade some
   reasoning quality for it.

</details>

---

## Done when

- [ ] `stream_prompt.py` prints input tokens, output tokens, USD cost, TTFT,
      and total time after every run.
- [ ] You used `count_tokens` to estimate a prompt's input cost before sending.
- [ ] `notes.md` has the opus-vs-haiku comparison table filled in.
- [ ] You can explain why output tokens cost more and what TTFT measures.

## Pitfalls

- **Don't use `tiktoken`** — wrong tokenizer for Claude. Use
  `client.messages.count_tokens`.
- **TTFT must be captured on the first chunk only** — guard with
  `if ttft is None`.
- **`count_tokens` is itself an API call** (cheap, but not free and not
  instant). Don't call it in a tight loop.

## Stage 0 complete

Go back to `README.md` and tick the "Done with Stage 0" checklist. Then move to
Stage 1 (your first agent — LLM + loop + tools, no framework).
