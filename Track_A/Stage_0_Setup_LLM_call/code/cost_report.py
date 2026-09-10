import time
from dotenv import load_dotenv
from anthropic import Anthropic
from costs import estimate_cost

load_dotenv()
client = Anthropic()
#MODEL = "claude-opus-5"
MODEL = "claude-haiku-4-5"
PROMPT = "Summarize the plot of Romeo and Juliet in 120 words."

# 1. ESTIMATE input cost before spending a generation token
pre = client.messages.count_tokens(
    model=MODEL, messages=[{"role": "user", "content": PROMPT}],
)
est_in = estimate_cost(MODEL, pre.input_tokens, 0)
print(f"estimate: {pre.input_tokens} input tokens  ~${est_in:.6f} (input only)")

# 2. RUN with timing
start = time.perf_counter()
ttft = None
with client.messages.stream(
    model=MODEL, max_tokens=4096,
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
if total > ttft:
    print(f"rate    : {u.output_tokens / (total - ttft):.0f} output tok/s (incl. thinking tokens)")