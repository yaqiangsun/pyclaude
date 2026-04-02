"""
Model cost utilities.

Model pricing information.
"""

from typing import Dict, Optional


# Model pricing per 1M tokens
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "claude-opus-4-5": {
        "input": 15.0,
        "output": 75.0,
    },
    "claude-sonnet-4-5": {
        "input": 3.0,
        "output": 15.0,
    },
    "claude-haiku-4-5": {
        "input": 0.8,
        "output": 4.0,
    },
}


def get_model_pricing(model: str) -> Optional[Dict[str, float]]:
    """Get pricing for model.

    Args:
        model: Model name

    Returns:
        Pricing dict or None
    """
    model_lower = model.lower()
    for key, pricing in MODEL_PRICING.items():
        if key in model_lower:
            return pricing
    return None


def estimate_cost(
    model: str,
    input_tokens: int,
    output_tokens: int,
) -> Optional[float]:
    """Estimate cost for API call.

    Args:
        model: Model name
        input_tokens: Input token count
        output_tokens: Output token count

    Returns:
        Estimated cost in USD
    """
    pricing = get_model_pricing(model)
    if not pricing:
        return None

    input_cost = (input_tokens / 1_000_000) * pricing["input"]
    output_cost = (output_tokens / 1_000_000) * pricing["output"]
    return input_cost + output_cost


__all__ = [
    "MODEL_PRICING",
    "get_model_pricing",
    "estimate_cost",
]