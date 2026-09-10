import os
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()                       # reads .env into environment variables
client = Anthropic()                # picks up ANTHROPIC_API_KEY from the environment

resp = client.messages.create(
    model="claude-opus-5",
    max_tokens=1024,
    messages=[
        {"role": "user", "content": "In two sentences, what is an LLM agent?"}
    ],
)

text = next(b.text for b in resp.content if b.type == "text")
print(text)
print("---")
print("stop_reason:", resp.stop_reason, "| usage:", resp.usage)
