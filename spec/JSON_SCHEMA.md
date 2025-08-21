### JSON Schema v1

- **version**: "v1"
- **updated_at**: ISO8601 timestamp (UTC)
- **summary**:
  - **crypto_sentiment**: number in [0,1]
  - **global_sentiment**: number in [0,1]
  - **combined_sentiment**: number in [0,1]
  - **confidence**: number in [0,1]
  - **counts**: { crypto: number, global: number }
- **history**: optional Array of entries
  - each entry: { ts, crypto, global, combined, counts:{crypto,global} }
- **drivers**:
  - **positive**: Array<{ title, url, source, weight }>
  - **negative**: Array<{ title, url, source, weight }>
- **notes**: { warnings: string[] }

Example:
```json
{
  "version": "v1",
  "updated_at": "2024-01-01T12:00:00Z",
  "summary": {
    "crypto_sentiment": 0.62,
    "global_sentiment": 0.51,
    "combined_sentiment": 0.61,
    "confidence": 0.42,
    "counts": { "crypto": 28, "global": 12 }
  },
  "history": [
    { "ts": "2024-01-01T10:00:00Z", "crypto": 0.58, "global": 0.52, "combined": 0.57, "counts": {"crypto": 22, "global": 10} },
    { "ts": "2024-01-01T11:00:00Z", "crypto": 0.60, "global": 0.51, "combined": 0.59, "counts": {"crypto": 25, "global": 11} }
  ],
  "drivers": {
    "positive": [
      { "title": "L2 mainnet upgrade drives adoption", "url": "https://example.com/a", "source": "CoinDesk", "weight": 0.83 },
      { "title": "Exchange lists new token", "url": "https://example.com/b", "source": "CoinTelegraph", "weight": 0.72 },
      { "title": "ETF approval momentum", "url": "https://example.com/c", "source": "Reuters Markets", "weight": 0.65 }
    ],
    "negative": [
      { "title": "Protocol exploit triggers selloff", "url": "https://example.com/d", "source": "CoinDesk", "weight": 0.79 },
      { "title": "SEC lawsuit weighs on sentiment", "url": "https://example.com/e", "source": "CoinTelegraph", "weight": 0.68 },
      { "title": "Service outage impacts users", "url": "https://example.com/f", "source": "CryptoPanic", "weight": 0.55 }
    ]
  },
  "notes": { "warnings": [] }
}
``` 