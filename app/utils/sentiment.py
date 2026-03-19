"""
sentiment.py
------------
Lightweight sentiment/mood analyser using TextBlob.
Falls back to a simple keyword list if TextBlob is unavailable.

Returns:
    score: float  -1.0 (very negative) … 0.0 (neutral) … 1.0 (very positive)
    label: str    "positive" | "neutral" | "negative"
"""

try:
    from textblob import TextBlob
    _TEXTBLOB_AVAILABLE = True
except ImportError:
    _TEXTBLOB_AVAILABLE = False

# Fallback keyword sets
_NEGATIVE_KEYWORDS = {
    "sad", "anxious", "depressed", "hopeless", "worthless", "scared",
    "afraid", "overwhelmed", "stressed", "exhausted", "lonely", "hurt",
    "angry", "frustrated", "hate", "suicidal", "die", "panic", "terrible",
}
_POSITIVE_KEYWORDS = {
    "happy", "great", "good", "better", "hopeful", "excited", "grateful",
    "thankful", "calm", "okay", "fine", "relieved", "proud", "confident",
    "love", "wonderful", "amazing",
}


def analyze_sentiment(text: str) -> tuple[float, str]:
    """Return (score, label) for the given text."""
    if _TEXTBLOB_AVAILABLE:
        score = TextBlob(text).sentiment.polarity  # -1.0 to 1.0
    else:
        words = set(text.lower().split())
        neg_hits = len(words & _NEGATIVE_KEYWORDS)
        pos_hits = len(words & _POSITIVE_KEYWORDS)
        total = neg_hits + pos_hits
        if total == 0:
            score = 0.0
        else:
            score = (pos_hits - neg_hits) / total

    if score > 0.1:
        label = "positive"
    elif score < -0.1:
        label = "negative"
    else:
        label = "neutral"

    return round(score, 4), label
