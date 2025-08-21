from typing import Dict
import re

from .utils import detect_crypto_symbols

POSITIVE_TERMS = {
    "bullish", "surge", "rally", "partnership", "integration", "listing", "mainnet",
    "upgrade", "breakout", "approval", "wins", "funding", "adoption", "record"
}
NEGATIVE_TERMS = {
    "bearish", "drop", "plunge", "hack", "exploit", "rug", "rugpull", "delay",
    "lawsuit", "sec", "suit", "ban", "outage", "liquidation", "selloff", "panic"
}

# Crypto-specific bonuses/penalties
LEXICON_BONUS = {"listing": 0.2, "mainnet": 0.2, "partnership": 0.15, "approval": 0.15}
LEXICON_PENALTY = {"rug": -0.5, "exploit": -0.4, "sec": -0.2, "lawsuit": -0.3}


def clamp(v: float, lo: float = -1.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, v))


def score_text(text: str) -> float:
    t = text.lower()
    pos = sum(1 for w in POSITIVE_TERMS if w in t)
    neg = sum(1 for w in NEGATIVE_TERMS if w in t)
    base = 0.0
    if pos or neg:
        base = (pos - neg) / max(3, pos + neg)
    # Adjust using lexicon
    for k, v in LEXICON_BONUS.items():
        if k in t:
            base += v
    for k, v in LEXICON_PENALTY.items():
        if k in t:
            base += v
    # Cashtag/contract presence mild boost to magnitude confidence on weighting side
    return clamp(base) 