from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import os
import feedparser

from .utils import http_get, normalize_url, utcnow, load_headers_cache, save_headers_cache

CRYPTOPANIC_TOKEN = os.getenv("CRYPTOPANIC_TOKEN")
ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY")

# Each item: {title, url, source, published_at, category, text?}
# category in {"crypto", "global", "social"}

headers_cache = load_headers_cache()


def fetch_rss(url: str, source_name: str, category: str) -> List[Dict]:
	cond_headers = {}
	cache_key = f"{source_name}:{url}"
	cached = headers_cache.get(cache_key, {})
	if "ETag" in cached:
		cond_headers["If-None-Match"] = cached["ETag"]
	if "Last-Modified" in cached:
		cond_headers["If-Modified-Since"] = cached["Last-Modified"]

	status, resp_headers, content = http_get(url, headers=cond_headers)
	if status == 304:
		return []

	# Update cache with fresh validators
	new_cache = {}
	if "ETag" in resp_headers:
		new_cache["ETag"] = resp_headers["ETag"]
	if "Last-Modified" in resp_headers:
		new_cache["Last-Modified"] = resp_headers["Last-Modified"]
	if new_cache:
		headers_cache[cache_key] = new_cache
		save_headers_cache(headers_cache)

	parsed = feedparser.parse(content)
	items: List[Dict] = []
	for e in parsed.entries[:75]:
		link = normalize_url(getattr(e, "link", ""))
		title = getattr(e, "title", "")
		desc = getattr(e, "summary", None) or getattr(e, "description", None) or ""
		dt_struct = getattr(e, "published_parsed", None) or getattr(e, "updated_parsed", None)
		if dt_struct:
			published = datetime(*dt_struct[:6], tzinfo=timezone.utc)
		else:
			published = utcnow()
		if not link or not title:
			continue
		items.append({
			"title": title if len(title) <= 240 else title[:237] + "...",
			"text": desc if len(desc or "") <= 1000 else (desc or "")[:997] + "...",
			"url": link,
			"source": source_name,
			"published_at": published.isoformat(),
			"category": category,
		})
	return items


def fetch_coindesk() -> List[Dict]:
	try:
		return fetch_rss("https://www.coindesk.com/arc/outboundfeeds/rss/", "CoinDesk", "crypto")
	except Exception:
		return []


def fetch_cointelegraph() -> List[Dict]:
	try:
		return fetch_rss("https://cointelegraph.com/rss", "CoinTelegraph", "crypto")
	except Exception:
		return []


def fetch_reuters_markets() -> List[Dict]:
	try:
		return fetch_rss("https://feeds.reuters.com/reuters/marketsNews", "Reuters Markets", "global")
	except Exception:
		return []


def fetch_bloomberg_markets() -> List[Dict]:
	try:
		return fetch_rss("https://feeds.bloomberg.com/markets/news.rss", "Bloomberg Markets", "global")
	except Exception:
		return []


def fetch_cnbc_markets() -> List[Dict]:
	try:
		return fetch_rss("https://www.cnbc.com/id/100003114/device/rss/rss.html", "CNBC Markets", "global")
	except Exception:
		return []


def fetch_marketwatch() -> List[Dict]:
	try:
		return fetch_rss("https://feeds.content.dowjones.io/public/rss/mw_realtimeheadlines", "MarketWatch", "global")
	except Exception:
		return []


def fetch_yahoo_finance() -> List[Dict]:
	try:
		return fetch_rss("https://feeds.finance.yahoo.com/rss/2.0/headline?s=^DJI,^GSPC,^IXIC&region=US&lang=en-US", "Yahoo Finance", "global")
	except Exception:
		return []


def fetch_decrypt() -> List[Dict]:
	try:
		return fetch_rss("https://decrypt.co/feed", "Decrypt", "crypto")
	except Exception:
		return []


def fetch_cryptoslate() -> List[Dict]:
	try:
		return fetch_rss("https://cryptoslate.com/feed/", "CryptoSlate", "crypto")
	except Exception:
		return []


def fetch_crypto_panic() -> List[Dict]:
	if not CRYPTOPANIC_TOKEN:
		return []
	url = f"https://cryptopanic.com/api/v1/posts/?token={CRYPTOPANIC_TOKEN}&filter=rising"
	status, headers, content = http_get(url)
	import json
	data = json.loads(content.decode("utf-8"))
	items: List[Dict] = []
	for p in data.get("results", [])[:100]:
		link = normalize_url(p.get("url") or "")
		title = p.get("title") or ""
		published_raw = p.get("published_at") or p.get("created_at")
		if not link or not title:
			continue
		items.append({
			"title": title,
			"text": p.get("domain") or "",
			"url": link,
			"source": "CryptoPanic",
			"published_at": (published_raw or utcnow().isoformat()),
			"category": "social" if p.get("source", {}).get("domain") in {"twitter.com", "x.com"} else "crypto",
		})
	return items

# Market indicators

def fetch_binance_tickers(symbols: List[str] = ["BTCUSDT", "ETHUSDT", "SOLUSDT"]) -> List[Dict]:
	items: List[Dict] = []
	for sym in symbols:
		try:
			status, headers, content = http_get(f"https://api.binance.com/api/v3/ticker/24hr?symbol={sym}")
			if status != 200:
				continue
			import json
			data = json.loads(content.decode("utf-8"))
			pct = float(data.get("priceChangePercent", 0.0))
			close_time = int(data.get("closeTime", 0)) / 1000.0
			published = datetime.fromtimestamp(close_time, tz=timezone.utc) if close_time else utcnow()
			name = sym.replace("USDT", "")
			if pct >= 2.0:
				title = f"{name} up {pct:.1f}% 24h — rally"
			elif pct <= -2.0:
				title = f"{name} down {pct:.1f}% 24h — plunge"
			else:
				title = f"{name} {pct:+.1f}% 24h"
			items.append({
				"title": title,
				"url": f"https://www.binance.com/en/trade/{name}_USDT",
				"source": "Binance 24h",
				"published_at": published.isoformat(),
				"category": "crypto",
			})
		except Exception:
			continue
	return items


def fetch_coingecko_global() -> List[Dict]:
	# Global market cap % change
	try:
		status, headers, content = http_get("https://api.coingecko.com/api/v3/global")
		if status != 200:
			return []
		import json
		data = json.loads(content.decode("utf-8"))
		chg = (data.get("data", {}).get("market_cap_change_percentage_24h_usd") or 0.0)
		published = utcnow()
		if chg >= 1.0:
			title = f"Global crypto market cap up {chg:.1f}% — rally"
		elif chg <= -1.0:
			title = f"Global crypto market cap down {chg:.1f}% — selloff"
		else:
			title = f"Global crypto market cap {chg:+.1f}%"
		return [{
			"title": title,
			"url": "https://www.coingecko.com/en/global_charts",
			"source": "CoinGecko Global",
			"published_at": published.isoformat(),
			"category": "crypto",
		}]
	except Exception:
		return []


def fetch_fear_greed() -> List[Dict]:
	try:
		status, headers, content = http_get("https://api.alternative.me/fng/?limit=1&format=json")
		if status != 200:
			return []
		import json
		data = json.loads(content.decode("utf-8"))
		res = (data.get("data") or [])[0] if data.get("data") else None
		if not res:
			return []
		val = float(res.get("value", 0))
		cls = (res.get("value_classification") or "").lower()
		published = utcnow()
		if val >= 60:
			title = f"Fear & Greed {int(val)} (Greed) — bullish"
		elif val <= 40:
			title = f"Fear & Greed {int(val)} (Fear) — bearish"
		else:
			title = f"Fear & Greed {int(val)}"
		return [{
			"title": title,
			"url": "https://alternative.me/crypto/fear-and-greed-index/",
			"source": "Fear&Greed",
			"published_at": published.isoformat(),
			"category": "crypto",
		}]
	except Exception:
		return []


def fetch_etherscan_gas() -> List[Dict]:
	if not ETHERSCAN_API_KEY:
		return []
	status, headers, content = http_get(f"https://api.etherscan.io/api?module=gastracker&action=gasoracle&apikey={ETHERSCAN_API_KEY}")
	if status != 200:
		return []
	import json
	data = json.loads(content.decode("utf-8")).get("result", {})
	try:
		propose = float(data.get("ProposeGasPrice"))
		published = utcnow()
		word = "surge" if propose >= 50 else ("drop" if propose <= 10 else "")
		title = f"ETH gas {propose:.0f} gwei{(' — ' + word) if word else ''}"
		return [{
			"title": title,
			"url": "https://etherscan.io/gastracker",
			"source": "Etherscan Gas",
			"published_at": published.isoformat(),
			"category": "crypto",
		}]
	except Exception:
		return []


def fetch_binance_funding(symbols: List[str] = ["BTCUSDT", "ETHUSDT"]) -> List[Dict]:
	items: List[Dict] = []
	for sym in symbols:
		status, headers, content = http_get(f"https://fapi.binance.com/fapi/v1/premiumIndex?symbol={sym}")
		if status != 200:
			continue
		import json
		data = json.loads(content.decode("utf-8"))
		try:
			rate = float(data.get("lastFundingRate", 0.0)) * 100.0
			published = utcnow()
			name = sym.replace("USDT", "")
			title = f"{name} funding {rate:+.3f}%"
			items.append({
				"title": title,
				"url": f"https://www.binance.com/en/futures/{name}USDT",
				"source": "Binance Funding",
				"published_at": published.isoformat(),
				"category": "crypto",
			})
		except Exception:
			continue
	return items


def fetch_all_sources() -> List[Dict]:
	items: List[Dict] = []
	items.extend(fetch_coindesk())
	items.extend(fetch_cointelegraph())
	items.extend(fetch_reuters_markets())
	items.extend(fetch_bloomberg_markets())
	items.extend(fetch_cnbc_markets())
	items.extend(fetch_marketwatch())
	items.extend(fetch_yahoo_finance())
	items.extend(fetch_decrypt())
	items.extend(fetch_cryptoslate())
	items.extend(fetch_binance_tickers())
	items.extend(fetch_coingecko_global())
	items.extend(fetch_fear_greed())
	items.extend(fetch_etherscan_gas())
	items.extend(fetch_crypto_panic())
	items.extend(fetch_binance_funding())
	return items 