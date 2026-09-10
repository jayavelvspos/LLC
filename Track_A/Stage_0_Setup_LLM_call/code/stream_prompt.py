import sys
from dotenv import load_dotenv
from anthropic import Anthropic

load_dotenv()
client = Anthropic()

MODEL = "claude-opus-5"

def get_prompt() -> str:
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