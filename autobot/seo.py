"""SEO helpers building metadata, slugs and structured data."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List

import orjson
from slugify import slugify

from .db import Article, Lead
from .imaging import ImageAsset
from .research import EvidencePack

DEFAULT_CATEGORIES = ["Travel", "Airline", "Points"]
DEFAULT_TAGS = ["里程", "积分", "旅行攻略"]


def _select_category(lead: Lead) -> str:
    title = lead.title.lower()
    if any(keyword in title for keyword in ["card", "信用卡", "visa", "mastercard"]):
        return "Card"
    if any(keyword in title for keyword in ["hotel", "酒店"]):
        return "Hotel"
    if any(keyword in title for keyword in ["航", "air", "里程"]):
        return "Airline"
    return "Travel"


def _collect_tags(lead: Lead) -> List[str]:
    tags = set(DEFAULT_TAGS)
    for word in lead.title.replace("—", " ").replace("：", " ").split():
        cleaned = word.strip().strip("，。、()（）")
        if len(cleaned) >= 2:
            tags.add(cleaned)
    return sorted(tags)


def build_json_ld(article: Article, evidence_pack: EvidencePack, cover: ImageAsset, lead: Lead) -> str:
    faq = article.meta.get("faq") if isinstance(article.meta, dict) else []
    faq_items = []
    for item in faq:
        faq_items.append(
            {
                "@type": "Question",
                "name": item["question"],
                "acceptedAnswer": {"@type": "Answer", "text": item["answer"]},
            }
        )
    data = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": article.title[:110],
        "datePublished": datetime.utcnow().isoformat(),
        "inLanguage": "zh-CN",
        "author": {"@type": "Organization", "name": "Longbo Cloud"},
        "publisher": {
            "@type": "Organization",
            "name": "Longbo Cloud",
            "logo": {
                "@type": "ImageObject",
                "url": "https://longbo.cloud/wp-content/uploads/2024/01/logo.png",
            },
        },
        "image": {
            "@type": "ImageObject",
            "url": f"{cover.path}",
            "width": cover.width,
            "height": cover.height,
        },
        "mainEntityOfPage": lead.url,
    }
    if faq_items:
        data["mainEntity"] = {
            "@type": "FAQPage",
            "@context": "https://schema.org",
            "mainEntity": faq_items,
        }
    return orjson.dumps(data).decode("utf-8")


def build_seo_package(article: Article, evidence_pack: EvidencePack, cover: ImageAsset, lead: Lead) -> Dict[str, Any]:
    meta = article.meta if isinstance(article.meta, dict) else {}
    title_options = meta.get("title_options", [article.title])
    meta_descriptions = meta.get("meta_descriptions", [])
    chosen_title = title_options[0][:60]
    meta_description = (meta_descriptions[0] if meta_descriptions else article.excerpt)[:155]
    slug = slugify(article.title)[:90]
    category = _select_category(lead)
    tags = _collect_tags(lead)
    json_ld = build_json_ld(article, evidence_pack, cover, lead)

    article.title = chosen_title
    article.slug = slug
    article.json_ld = json_ld

    seo_package = {
        "title": chosen_title,
        "slug": slug,
        "meta_description": meta_description,
        "json_ld": json_ld,
        "category": category,
        "tags": tags,
        "internal_links": meta.get("internal_links", []),
        "cover_alt": cover.alt_text,
    }
    return seo_package


__all__ = ["build_seo_package"]
