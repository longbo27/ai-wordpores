"""Taxonomy synchronization with WordPress."""
from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

import httpx

from .config import PROJECT_ROOT, Settings

CACHE_PATH = PROJECT_ROOT / "taxonomy_map.json"
DEFAULT_CATEGORIES = {
    "Airline": 0,
    "Card": 0,
    "Hotel": 0,
    "Points": 0,
    "Travel": 0,
    "Status Match": 0,
}

DEFAULT_TAGS = {
    "Aeroplan": 0,
    "United": 0,
    "Marriott": 0,
    "Hyatt": 0,
    "里程": 0,
    "积分": 0,
}


@dataclass(slots=True)
class TaxonomyMap:
    categories: Dict[str, int] = field(default_factory=lambda: DEFAULT_CATEGORIES.copy())
    tags: Dict[str, int] = field(default_factory=lambda: DEFAULT_TAGS.copy())

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {"categories": self.categories, "tags": self.tags}

    @classmethod
    def from_dict(cls, data: Dict[str, Dict[str, int]]) -> "TaxonomyMap":
        instance = cls()
        instance.categories.update(data.get("categories", {}))
        instance.tags.update(data.get("tags", {}))
        return instance


class TaxonomyManager:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    def resolve(self, client: httpx.Client | None = None, auth: tuple[str, str] | None = None) -> TaxonomyMap:
        if CACHE_PATH.exists():
            return TaxonomyMap.from_dict(json.loads(CACHE_PATH.read_text(encoding="utf-8")))
        taxonomy_map = TaxonomyMap()
        if client and auth:
            try:
                categories = client.get("/wp-json/wp/v2/categories?per_page=100", auth=auth).json()
                for cat in categories:
                    taxonomy_map.categories[cat.get("name", "")] = cat.get("id", 0)
                tags = client.get("/wp-json/wp/v2/tags?per_page=100", auth=auth).json()
                for tag in tags:
                    taxonomy_map.tags[tag.get("name", "")] = tag.get("id", 0)
            except Exception:
                pass
        CACHE_PATH.write_text(json.dumps(taxonomy_map.to_dict(), ensure_ascii=False, indent=2), encoding="utf-8")
        return taxonomy_map


__all__ = ["TaxonomyManager", "TaxonomyMap"]
