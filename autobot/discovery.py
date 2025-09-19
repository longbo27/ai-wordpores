"""Lead discovery from RSS/JSON sources."""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Iterable, List

import feedparser
from rich.console import Console

from .config import ConfigBundle
from .db import Lead

console = Console()


def _normalize_datetime(entry: Dict) -> datetime | None:
    if "published_parsed" in entry and entry["published_parsed"]:
        try:
            return datetime(*entry["published_parsed"][:6])
        except TypeError:
            return None
    if "updated_parsed" in entry and entry["updated_parsed"]:
        try:
            return datetime(*entry["updated_parsed"][:6])
        except TypeError:
            return None
    return None


def discover_leads(bundle: ConfigBundle) -> List[Lead]:
    feeds: Iterable[Dict] = bundle.sources.get("feeds", [])
    leads: List[Lead] = []
    for feed_config in feeds:
        url = feed_config.get("url")
        if not url:
            continue
        parsed = feedparser.parse(url)
        entries = parsed.get("entries", [])
        if not entries:
            continue
        entry = entries[0]
        title = entry.get("title", "Untitled")
        link = entry.get("link", url)
        summary = entry.get("summary", "")
        published_at = _normalize_datetime(entry)
        lead = Lead(
            url=link,
            title=title,
            source=feed_config.get("name", parsed.get("feed", {}).get("title", "Unknown")),
            summary=summary,
            published_at=published_at,
            score=float(feed_config.get("score", 1.0)),
        )
        leads.append(lead)
        console.log(f"Discovered lead from {lead.source}: {lead.title}")
        if len(leads) >= bundle.thresholds.get("max_leads_per_batch", 1):
            break
    return leads


__all__ = ["discover_leads"]
