"""Compliance and content rules applied to generated articles."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from .config import PROJECT_ROOT
from .planner import ContentPlan
from .research import EvidencePack
from .db import Article

TEMPLATE_DIR = PROJECT_ROOT / "autobot" / "templates"


def _load_template(name: str) -> str:
    path = TEMPLATE_DIR / name
    if not path.exists():
        return ""
    return path.read_text(encoding="utf-8")


def apply_rules(article: Article, plan: ContentPlan, evidence_pack: EvidencePack) -> Article:
    disclaimer = _load_template("disclaimer.html")
    expired_banner = _load_template("expired_banner.html")

    if plan.deal_deadline and plan.deal_deadline < datetime.utcnow():
        article.title = article.title + "（已结束）"
        article.html = expired_banner + article.html

    if disclaimer and disclaimer not in article.html:
        article.html += disclaimer
    return article


__all__ = ["apply_rules"]
