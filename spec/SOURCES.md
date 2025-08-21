### Sources

- **CryptoPanic** (optional; requires `CRYPTOPANIC_TOKEN`): trending/rising crypto news and social. Categorized as crypto or social.
- **CoinDesk RSS**: `https://www.coindesk.com/arc/outboundfeeds/rss/?outputType=xml` (crypto)
- **CoinTelegraph RSS**: `https://cointelegraph.com/rss` (crypto)
- **Reuters Markets RSS**: `https://feeds.reuters.com/reuters/marketsNews` (global macro)

Notes:
- RSS fetches include basic conditional headers when available; if not supported, full fetch proceeds.
- If any source fails, the system continues and retains the last feed snapshot to avoid empty publishes. 