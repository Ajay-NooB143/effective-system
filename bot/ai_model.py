import os
import random
from openai import OpenAI

_client_ai = None


def _get_client():
    global _client_ai
    if _client_ai is None:
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("OPENAI_API_KEY environment variable is not set")
        _client_ai = OpenAI(api_key=api_key)
    return _client_ai


def ai_predict(features):
    """
    Uses GPT-4 to predict BUY/SELL/HOLD.
    Falls back to random if OpenAI is unavailable.
    features: list — e.g. [price]
    Returns: (signal, confidence)
    """
    try:
        price = features[0] if features else 0
        prompt = f"""You are a professional trading AI.
Current price: {price}
Based on this price, should a trader BUY, SELL, or HOLD?
Reply with ONLY one word: BUY, SELL, or HOLD.
Then on a new line, reply with a confidence score between 0.0 and 1.0.
Example:
BUY
0.82
"""
        openai_client = _get_client()
        response = openai_client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=20,
            temperature=0.3,
        )
        text = response.choices[0].message.content.strip().split("\n")
        signal = text[0].strip().upper()
        try:
            confidence = float(text[1].strip()) if len(text) > 1 else 0.7
        except ValueError:
            confidence = 0.7

        if signal not in ["BUY", "SELL", "HOLD"]:
            signal = "HOLD"
            confidence = 0.5

        return signal, confidence

    except Exception as e:
        print(f"[AI Error] {e} — falling back to random")
        prob = random.uniform(0, 1)
        if prob > 0.6:
            return "BUY", prob
        elif prob < 0.4:
            return "SELL", prob
        else:
            return "HOLD", prob
