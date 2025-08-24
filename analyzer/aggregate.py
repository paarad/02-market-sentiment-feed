from typing import Dict, List, Tuple
from collections import defaultdict
from datetime import datetime, timezone

from .utils import utcnow, parse_ts, exponential_decay_weight, detect_crypto_symbols
from .sentiment import score_text
from .indicators import generate_market_indicators

SOURCE_WEIGHTS = {
    "CoinDesk": 1.0,
    "Reuters Markets": 1.0,
    "CoinTelegraph": 0.8,
    "Decrypt": 0.85,
    "CryptoSlate": 0.75,
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

    # Generate comprehensive market indicators
    market_indicators = generate_market_indicators()

    buckets = {"crypto": [], "global": []}
    for it in items:
        # Use description text when available to enrich sentiment
        s = score_text((it.get("text") or it.get("title") or ""))
        w = compute_item_weight(it, now)
        cat = it.get("category")
        # Map social into crypto bucket
        if cat not in ("crypto", "global"):
            cat = "crypto"
        # Only include items with significant sentiment (filter out neutral)
        if abs(s) > 0.1:  # Only items with clear sentiment
            buckets[cat].append((s, w, it))

    def calc(b: List[Tuple[float, float, Dict]]) -> Tuple[float, float, float, int]:
        if not b:
            return 0.0, 0.0, 0.0, 0
        sw = sum(w for _, w, _ in b)
        if sw == 0:
            return 0.0, 0.0, 0.0, 0
        s_weighted = sum(s * w for s, w, _ in b) / sw
        # Amplify the signal and make it more diverse
        # Filter out neutral items and amplify the remaining sentiment
        amplified = s_weighted * 2.0  # Double the impact
        s01 = 0.5 + (amplified * 0.3)  # Spread from 0.2 to 0.8
        s01 = max(0.2, min(0.8, s01))  # Clamp to more diverse range
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
        {"title": it.get("title"), "url": it.get("url"), "source": it.get("source"), "weight": round(w, 4), "score": round(s, 4)}
        for _, s, w, it in scored if s > 0
    ][:3]
    negatives = [
        {"title": it.get("title"), "url": it.get("url"), "source": it.get("source"), "weight": round(w, 4), "score": round(s, 4)}
        for _, s, w, it in reversed(scored) if s < 0
    ][:3]

    updated_at = now.isoformat()

    summary = {
        "crypto_sentiment": round(c01, 4),
        "global_sentiment": round(g01, 4),
        "combined_sentiment": round(combined01, 4),
        "confidence": round(combined_conf, 4),
        "counts": {"crypto": c_count, "global": g_count},
        
        # Enhanced market indicators
        "market_indicators": {
            # Price performance
            "btc_price": market_indicators.get("btc_price", 0),
            "btc_change_24h": round(market_indicators.get("btc_change_24h", 0), 2),
            "eth_price": market_indicators.get("eth_price", 0),
            "eth_change_24h": round(market_indicators.get("eth_change_24h", 0), 2),
            
            # Market regime
            "regime": market_indicators.get("market_regime", "unknown"),
            "regime_strength": round(market_indicators.get("regime_strength", 0), 3),
            "market_breadth": round(market_indicators.get("market_breadth_24h", 0), 3),
            
            # Fear & Greed
            "fear_greed": {
                "value": market_indicators.get("fear_greed_value", 50),
                "classification": market_indicators.get("fear_greed_classification", "Neutral"),
                "trend": market_indicators.get("fear_greed_trend", "stable")
            },
            
            # Activity & Volume
            "activity": {
                "level": market_indicators.get("activity_level", "unknown"),
                "volume_24h": market_indicators.get("total_volume_24h", 0),
                "high_activity_coins": market_indicators.get("high_activity_count", 0)
            },
            
            # Dominance & Seasons
            "dominance": {
                "btc_dominance": market_indicators.get("btc_dominance", 0),
                "alt_season_score": market_indicators.get("alt_season_score", 0),
                "season": market_indicators.get("market_season", "unknown")
            },
            
            # Data quality
            "data_quality": {
                "sources": market_indicators.get("data_sources", 0),
                "coins_analyzed": market_indicators.get("coins_analyzed", 0)
            }
        }
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
        "drivers": {
            "positive": positives, 
            "negative": negatives,
            "market_movers": {
                "high_activity": market_indicators.get("high_activity_coins", [])[:3],
                "momentum_shifts": market_indicators.get("momentum_shifts", [])[:3]
            }
        },
        "notes": {"warnings": []},
    }

    return result 