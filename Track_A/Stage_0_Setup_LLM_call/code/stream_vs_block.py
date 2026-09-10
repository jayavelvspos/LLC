import time
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()
PROMPT = "Explain what an embedding is, in about 80 words."

# --- blocking ---
t0 = time.perf_counter()
resp = client.messages.create(
    model="claude-opus-5", max_tokens=1024,
    messages=[{"role": "user", "content": PROMPT}],
)
print(f"[blocking] nothing visible for {time.perf_counter()-t0:.2f}s, then:")
print(next(b.text for b in resp.content if b.type == "text"), "\n")

# --- streaming ---
t0 = time.perf_counter()
first = None
with client.messages.stream(
    model="claude-opus-5", max_tokens=1024,
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