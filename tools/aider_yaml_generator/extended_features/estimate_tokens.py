import math


def estimate_tokens(total_chars: int, chars_per_token: float) -> int:
    if chars_per_token <= 0:
        return total_chars
    return math.ceil(total_chars / max(1e-9, chars_per_token))
