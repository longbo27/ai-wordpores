"""Default feed sources for airlines, hotels, banks and loyalty programs."""
from __future__ import annotations

from typing import List, Dict

DEFAULT_FEEDS: List[Dict[str, str | float]] = [
    {"name": "One Mile at a Time", "url": "https://onemileatatime.com/feed/", "score": 0.9},
    {"name": "Prince of Travel", "url": "https://princeoftravel.com/feed/", "score": 0.8},
    {"name": "Doctor of Credit", "url": "https://www.doctorofcredit.com/feed/", "score": 0.8},
    {"name": "Frequent Miler", "url": "https://frequentmiler.com/feed/", "score": 0.7},
    {"name": "AwardWallet Blog", "url": "https://awardwallet.com/blog/feed/", "score": 0.7},
]


def get_default_feeds() -> List[Dict[str, str | float]]:
    return DEFAULT_FEEDS


__all__ = ["get_default_feeds"]
