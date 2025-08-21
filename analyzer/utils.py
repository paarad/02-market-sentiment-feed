import json
import os
import re
import time
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional, Tuple

import requests
from dateutil import parser as dateparser
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

# Project constants (replace placeholders)
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "<YOUR_GITHUB_USERNAME>")
REPO_NAME = os.getenv("REPO_NAME", "<YOUR_REPO_NAME>")
PAGES_FEED_URL = os.getenv(
    "PAGES_FEED_URL",
    f"https://{GITHUB_USERNAME}.github.io/{REPO_NAME}/feed.json",
)

DEFAULT_HALF_LIFE_HOURS = 6.0

USER_AGENT = (
    f"MarketSentimentFeed/0.1 (+https://github.com/{GITHUB_USERNAME}/{REPO_NAME})"
)

CACHE_DIR = os.path.join("analyzer", ".cache")
HEADERS_CACHE_PATH = os.path.join(CACHE_DIR, "headers.json")

class FetchError(Exception):
    pass


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def to_iso8601(dt: datetime) -> str:
    return dt.astimezone(timezone.utc).isoformat()


def parse_ts(value: str) -> datetime:
    return dateparser.parse(value).astimezone(timezone.utc)


def normalize_url(url: str) -> str:
    url = url.strip()
    url = re.sub(r"#.*$", "", url)
    return url


def load_headers_cache() -> Dict[str, Dict[str, str]]:
    try:
        with open(HEADERS_CACHE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}


def save_headers_cache(data: Dict[str, Dict[str, str]]) -> None:
    os.makedirs(CACHE_DIR, exist_ok=True)
    with open(HEADERS_CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


@retry(
    reraise=True,
    wait=wait_exponential(multiplier=0.5, min=1, max=10),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type(FetchError),
)
def http_get(url: str, headers: Optional[Dict[str, str]] = None, timeout: int = 15) -> Tuple[int, Dict[str, str], bytes]:
    try:
        resp = requests.get(url, headers={"User-Agent": USER_AGENT, **(headers or {})}, timeout=timeout)
    except requests.RequestException as e:
        raise FetchError(str(e))
    if resp.status_code >= 500:
        raise FetchError(f"Server error {resp.status_code}")
    return resp.status_code, dict(resp.headers), resp.content


def exponential_decay_weight(age_hours: float, half_life_hours: float = DEFAULT_HALF_LIFE_HOURS) -> float:
    if age_hours <= 0:
        return 1.0
    return 0.5 ** (age_hours / half_life_hours)


def save_json(path: str, data: Any) -> None:
    dirname = os.path.dirname(path)
    if dirname:  # Only create directory if path has a directory component
        os.makedirs(dirname, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_json(path: str) -> Optional[Any]:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def detect_crypto_symbols(text: str) -> bool:
    # Detect cashtags like $BTC or contract addresses 0x...
    return bool(re.search(r"\$[A-Z]{2,6}\b", text)) or bool(re.search(r"\b0x[a-fA-F0-9]{6,}\b", text)) 