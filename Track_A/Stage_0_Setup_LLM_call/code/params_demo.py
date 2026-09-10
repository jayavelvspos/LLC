from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

def ask(system, messages, **params):
    kwargs = dict(
        model="claude-haiku-4-5",
        max_tokens=params.pop("max_tokens", 200),
        messages=messages,
        **params,
    )
    if system is not None:
        kwargs["system"] = system          # omit entirely when None
    return client.messages.create(**kwargs)

# 1. system prompt changes behavior for the SAME user message
q = [{"role": "user", "content": "What is a vector database?"}]
print("TERSE  :", ask("Answer in exactly one sentence.", q).content[0].text)
print("VERBOSE:", ask("Answer in a detailed paragraph with an analogy.", q).content[0].text[:120], "...")

# 2. temperature: determinism vs variety
# 2. temperature: only reachable via extra_body on this SDK; model may reject it
tq = [{"role": "user", "content": "In 10 words, what is a vector database?"}]
for t in (0.0, 1.0):
    try:
        outs = {
            client.messages.create(
                model="claude-haiku-4-5", max_tokens=60,
                messages=tq, extra_body={"temperature": t},
            ).content[0].text
            for _ in range(2)
        }
        print(f"temp={t}: {len(outs)} distinct answer(s) out of 2 runs")
    except Exception as e:
        print(f"temp={t}: rejected -> {type(e).__name__}: {e}")

# 3. multi-turn: the model only knows what you resend
convo = [{"role": "user", "content": "Remember the number 42."}]
convo.append({"role": "assistant", "content": ask(None, convo).content[0].text})
convo.append({"role": "user", "content": "What number did I say?"})
print("RECALL :", ask(None, convo).content[0].text)

# 4. stop_sequences
r = ask(None, [{"role": "user", "content": "List three fruits, comma separated."}],
        stop_sequences=[","], max_tokens=50)
print("STOPPED:", repr(r.content[0].text), "| stop_reason =", r.stop_reason)


SYSTEM = "You are a helpful study partner for someone learning to build AI agents."

messages = [
    {"role": "user", "content": "I'm on Stage 0: first LLM call. What should I make sure I understand before Stage 1?"},
]

def turn(messages):
    resp = client.messages.create(
        model="claude-opus-5",
        max_tokens=1024,
        system=SYSTEM,
        messages=messages,
    )
    reply = next(b.text for b in resp.content if b.type == "text")
    messages.append({"role": "assistant", "content": reply})
    print("\nASSISTANT:", reply)
    print(f"[tokens in={resp.usage.input_tokens} out={resp.usage.output_tokens}]")
    return messages

messages = turn(messages)

# Follow-up that only makes sense if the pri
messages.append({"role": "user", "content": "Of those, which is most likely to trip me up? Just name one."})
messages = turn(messages)
