import random

def ai_predict(features):
    # Replace with real model later
    prob = random.uniform(0, 1)

    if prob > 0.6:
        return "BUY", prob
    elif prob < 0.4:
        return "SELL", prob
    else:
        return "HOLD", prob
