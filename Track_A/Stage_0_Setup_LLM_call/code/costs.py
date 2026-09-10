PRICING = {  # USD per 1M tokens: (input, output)
    "claude-opus-5":   (5.00, 25.00),
    "claude-sonnet-5": (2.00, 10.00),
    "claude-haiku-4-5": (1.00, 5.00),
}

def estimate_cost(model: str, input_tokens: int, output_tokens: int) -> float:
    in_price, out_price = PRICING[model]
    return (input_tokens / 1_000_000) * in_price + (output_tokens / 1_000_000) * out_price