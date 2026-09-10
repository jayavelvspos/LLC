from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=200,
    messages=[{"role": "user", "content": "Name three primary colors."}],
)

# See every block the model returned, in order
print("block types :", [b.type for b in resp.content])

# Pull the text block by type, not by position
text = next(b.text for b in resp.content if b.type == "text")

print("id          :", resp.id)
print("model       :", resp.model)
print("role        :", resp.role)
print("stop_reason :", resp.stop_reason)
print("text        :", text)
print("input_tokens:", resp.usage.input_tokens)
print("output_tokens:", resp.usage.output_tokens)