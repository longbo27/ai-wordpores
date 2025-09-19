"""WordPress publisher with local fallback for drafts."""
from __future__ import annotations

import json
import shutil
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import httpx
from rich.console import Console

from .config import PROJECT_ROOT, Settings
from .db import Article, ImageAsset, Lead
from .taxonomy import TaxonomyManager

console = Console()


@dataclass(slots=True)
class PublishResult:
    status: str
    url: str
    platform: str
    remote_id: str | None = None
    meta: Dict[str, Any] | None = None


class Publisher:
    def __init__(self, settings: Settings) -> None:
        self.settings = settings
        self.taxonomy = TaxonomyManager(settings)

    def publish(
        self,
        article: Article,
        cover: ImageAsset,
        seo_package: Dict[str, Any],
        lead: Lead,
    ) -> Dict[str, Any]:
        if self.settings.wp_user and self.settings.wp_app_pass:
            try:
                return self._publish_wordpress(article, cover, seo_package, lead)
            except Exception as exc:  # pragma: no cover - network failure fallback
                console.log(f"[red]WordPress publish failed: {exc}; falling back to local draft[/red]")
        return self._save_local_draft(article, cover, seo_package, lead)

    def _publish_wordpress(
        self,
        article: Article,
        cover: ImageAsset,
        seo_package: Dict[str, Any],
        lead: Lead,
    ) -> Dict[str, Any]:
        client = httpx.Client(base_url=self.settings.wp_base_url, timeout=30)
        auth = (self.settings.wp_user, self.settings.wp_app_pass)
        taxonomy_ids = self.taxonomy.resolve(client, auth)
        category_name = seo_package.get("category", "Travel")
        category_id = taxonomy_ids.categories.get(category_name)
        tag_ids = [taxonomy_ids.tags.get(tag) for tag in seo_package.get("tags", []) if taxonomy_ids.tags.get(tag)]

        cover_path = PROJECT_ROOT / cover.path
        media_headers = {"Content-Type": "image/webp", "Content-Disposition": f"attachment; filename={Path(cover.path).name}"}
        media_resp = client.post(
            "/wp-json/wp/v2/media",
            content=cover_path.read_bytes(),
            headers=media_headers,
            auth=auth,
        )
        media_resp.raise_for_status()
        media_data = media_resp.json()
        featured_id = media_data.get("id")

        html = article.html + f'<script type="application/ld+json">{seo_package["json_ld"]}</script>'
        payload = {
            "title": seo_package["title"],
            "slug": seo_package["slug"],
            "status": "publish",
            "content": html,
            "excerpt": article.excerpt,
            "featured_media": featured_id,
            "categories": [category_id] if category_id else [],
            "tags": tag_ids,
            "meta": {"_longbo_internal_links": json.dumps(seo_package.get("internal_links", []))},
        }
        post_resp = client.post("/wp-json/wp/v2/posts", json=payload, auth=auth)
        post_resp.raise_for_status()
        data = post_resp.json()
        url = data.get("link", "")
        console.log(f"[green]已发布文章：{url}[/green]")
        return {
            "status": "published",
            "url": url,
            "platform": "wordpress",
            "remote_id": str(data.get("id")),
            "meta": {"featured_media": featured_id},
        }

    def _save_local_draft(
        self,
        article: Article,
        cover: ImageAsset,
        seo_package: Dict[str, Any],
        lead: Lead,
    ) -> Dict[str, Any]:
        html = article.html + f'<script type="application/ld+json">{seo_package["json_ld"]}</script>'
        output_dir = self.settings.output_dir
        output_dir.mkdir(parents=True, exist_ok=True)
        slug = seo_package["slug"]
        html_path = output_dir / f"{slug}.html"
        json_path = output_dir / f"{slug}.json"
        image_output = output_dir / Path(cover.path).name
        shutil.copyfile(PROJECT_ROOT / cover.path, image_output)
        html_path.write_text(html, encoding="utf-8")
        json_payload = {
            "title": seo_package["title"],
            "slug": slug,
            "excerpt": article.excerpt,
            "meta_description": seo_package["meta_description"],
            "category": seo_package["category"],
            "tags": seo_package["tags"],
            "internal_links": seo_package.get("internal_links", []),
            "cover_image": str(image_output),
            "cover_alt": seo_package.get("cover_alt"),
            "source_url": lead.url,
        }
        json_path.write_text(json.dumps(json_payload, ensure_ascii=False, indent=2), encoding="utf-8")
        console.log(f"[yellow]草稿已生成：{html_path}[/yellow]")
        return {
            "status": "draft",
            "url": str(html_path),
            "platform": "local",
            "meta": json_payload,
        }


__all__ = ["Publisher"]
