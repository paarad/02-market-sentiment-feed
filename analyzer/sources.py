from typing import Dict, List, Optional, Tuple
from datetime import datetime, timezone
import os
import feedparser

from .utils import http_get, normalize_url, utcnow, load_headers_cache, save_headers_cache

CRYPTOPANIC_TOKEN = os.getenv("CRYPTOPANIC_TOKEN")

# Each item: {title, url, source, published_at, category}
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
		# Prefer summary if available for sentiment context
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
	return fetch_rss("https://www.coindesk.com/arc/outboundfeeds/rss/", "CoinDesk", "crypto")


def fetch_cointelegraph() -> List[Dict]:
	return fetch_rss("https://cointelegraph.com/rss", "CoinTelegraph", "crypto")


def fetch_reuters_markets() -> List[Dict]:
	return fetch_rss("https://feeds.reuters.com/reuters/marketsNews", "Reuters Markets", "global")


def fetch_decrypt() -> List[Dict]:
	return fetch_rss("https://decrypt.co/feed", "Decrypt", "crypto")


def fetch_cryptoslate() -> List[Dict]:
	return fetch_rss("https://cryptoslate.com/feed/", "CryptoSlate", "crypto")


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


def fetch_all_sources() -> List[Dict]:
	items: List[Dict] = []
	items.extend(fetch_coindesk())
	items.extend(fetch_cointelegraph())
	items.extend(fetch_reuters_markets())
	items.extend(fetch_decrypt())
	items.extend(fetch_cryptoslate())
	items.extend(fetch_crypto_panic())
	return items 