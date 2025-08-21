from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime, timezone

from .utils import utcnow, parse_ts, exponential_decay_weight, detect_crypto_symbols
from .sentiment import score_text

SOURCE_WEIGHTS = {
    "CoinDesk": 1.0,
    "Reuters Markets": 1.0,
    "CoinTelegraph": 0.8,
    "CryptoPanic": 0.5,
}


def dedupe_items(items: List[Dict]) -> List[Dict]:
    seen = set()
    deduped: List[Dict] = []
    for it in items:
        key = it.get("url")
        if not key or key in seen:
            continue
        seen.add(key)
        deduped.append(it)
    return deduped


def compute_item_weight(item: Dict, now: datetime) -> float:
    published_at = parse_ts(item["published_at"]) if isinstance(item.get("published_at"), str) else now
    age_hours = max(0.0, (now - published_at).total_seconds() / 3600.0)
    freshness = exponential_decay_weight(age_hours)
    src_w = SOURCE_WEIGHTS.get(item.get("source"), 0.8)
    symbol_bonus = 1.2 if detect_crypto_symbols(item.get("title", "")) else 1.0
    return freshness * src_w * symbol_bonus


def aggregate(items: List[Dict], history: List[Dict]) -> Dict:
    now = utcnow()
    items = dedupe_items(items)

    buckets = {"crypto": [], "global": []}
    for it in items:
        s = score_text(it.get("title", ""))
        w = compute_item_weight(it, now)
        cat = it.get("category")
        # Map social into crypto bucket
        if cat not in ("crypto", "global"):
            cat = "crypto"
        buckets[cat].append((s, w, it))

    def calc(b: List[Tuple[float, float, Dict]]) -> Tuple[float, float, float, int]:
        if not b:
            return 0.0, 0.0, 0.0, 0
        sw = sum(w for _, w, _ in b)
        if sw == 0:
            return 0.0, 0.0, 0.0, 0
        s_weighted = sum(s * w for s, w, _ in b) / sw
        # convert to [0,1]
        s01 = (s_weighted + 1.0) / 2.0
        # confidence
        unique_sources = len({item.get("source") for _, _, item in b})
        k = 10.0
        conf = (sw / (sw + k)) ** 0.5
        diversity_scale = min(1.0, (unique_sources / 4.0) ** 0.5)
        conf *= diversity_scale
        return s_weighted, s01, conf, len(b)

    c_raw, c01, c_conf, c_count = calc(buckets["crypto"])
    g_raw, g01, g_conf, g_count = calc(buckets["global"])

    combined_raw = 0.9 * c_raw + 0.1 * g_raw
    combined01 = (combined_raw + 1.0) / 2.0
    combined_conf = (c_conf * 0.9 + g_conf * 0.1)

    # Drivers: top positive/negative by s * w
    scored = []
    for cat, b in buckets.items():
        for s, w, it in b:
            scored.append((s * w, s, w, it))
    scored.sort(key=lambda x: x[0], reverse=True)
    positives = [
        {"title": it.get("title"), "url": it.get("url"), "source": it.get("source"), "weight": round(w, 4)}
        for _, s, w, it in scored if s > 0
    ][:3]
    negatives = [
        {"title": it.get("title"), "url": it.get("url"), "source": it.get("source"), "weight": round(w, 4)}
        for _, s, w, it in reversed(scored) if s < 0
    ][:3]

    updated_at = now.isoformat()

    summary = {
        "crypto_sentiment": round(c01, 4),
        "global_sentiment": round(g01, 4),
        "combined_sentiment": round(combined01, 4),
        "confidence": round(combined_conf, 4),
        "counts": {"crypto": c_count, "global": g_count},
    }

    # History update
    history_entry = {
        "ts": updated_at,
        "crypto": round(c01, 4),
        "global": round(g01, 4),
        "combined": round(combined01, 4),
        "counts": {"crypto": c_count, "global": g_count},
    }

    history = (history or [])[-95:]  # keep ~4 days hourly
    history.append(history_entry)

    result = {
        "version": "v1",
        "updated_at": updated_at,
        "summary": summary,
        "history": history,
        "drivers": {"positive": positives, "negative": negatives},
        "notes": {"warnings": []},
    }

    return result 