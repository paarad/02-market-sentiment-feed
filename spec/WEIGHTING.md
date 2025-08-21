### Weighting and Aggregation

- **Freshness decay**: Half-life 6h. Weight multiplier: `0.5 ** (age_hours / 6)`.
- **Source weights**: `1.0` major (CoinDesk, Reuters), `0.8` mid (CoinTelegraph), `0.5` social (CryptoPanic).
- **Cashtags / contracts**: +20% weight when `$TICKER` or `0x...` present in title.
- **Sentiment**: Lightweight rule-based classifier with crypto lexicon adjustments.
- **Buckets**: 90% crypto, 10% global in combined sentiment.
- **Normalization**: Convert raw `[-1,1]` to `[0,1]` via `(s + 1) / 2`.
- **Confidence**: `sqrt(Σw / (Σw + k))` with `k = 10`, scaled by source diversity via `min(1, sqrt(unique_sources / 4))`.
- **Drivers**: Top 3 positive and negative by `s * w` with metadata. 