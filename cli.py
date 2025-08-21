import argparse
import os
from typing import List, Dict

from analyzer.sources import fetch_all_sources
from analyzer.aggregate import aggregate
from analyzer.utils import load_json, save_json

PUBLIC_FEED = os.path.join("public", "feed.json")
PUBLIC_HISTORY = os.path.join("public", "history.json")

SAMPLES_PATH = os.path.join("analyzer", "samples", "sample_items.json")


def run(window: str, offline: bool = False) -> int:
    os.makedirs("public", exist_ok=True)
    history = load_json(PUBLIC_HISTORY) or []

    if offline:
        items = load_json(SAMPLES_PATH) or []
    else:
        try:
            items = fetch_all_sources()
        except Exception as e:
            # Resilience: on failure, keep last snapshot
            items = []

    # If we failed to fetch and have no previous feed, fallback to samples
    if not items and not os.path.exists(PUBLIC_FEED):
        offline = True
        items = load_json(SAMPLES_PATH) or []

    result = aggregate(items, history)

    # Persist
    save_json(PUBLIC_FEED, result)
    save_json(PUBLIC_HISTORY, result.get("history", []))

    return 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Market Sentiment Feed CLI")
    parser.add_argument("--window", choices=["1h", "4h"], default="1h", help="Analysis window")
    parser.add_argument("--offline", action="store_true", help="Use bundled sample data")
    args = parser.parse_args()
    raise SystemExit(run(args.window, args.offline)) 