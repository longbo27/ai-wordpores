"""High-level orchestration for the autonomous publishing workflow."""
from __future__ import annotations

import logging
from typing import Any, Dict, List

from rich.console import Console

from .config import ConfigBundle, load_bundle
from sqlmodel import select

from .db import Article, ImageAsset, Lead, Publish, session_scope
from .dedup import filter_new_leads
from .discovery import discover_leads
from .imaging import generate_cover_package
from .planner import build_plan
from .publisher import Publisher
from .research import gather_evidence
from .rules import apply_rules
from .seo import build_seo_package
from .writer import compose_article

logger = logging.getLogger(__name__)
console = Console()


class AutobotOrchestrator:
    """Coordinates the discovery-to-publication pipeline."""

    def __init__(self, bundle: ConfigBundle | None = None) -> None:
        self.bundle = bundle or load_bundle()
        self.publisher = Publisher(self.bundle.settings)

    def run_once(self) -> List[Dict[str, Any]]:
        console.log("[bold green]Starting Longbo Cloud autopublisher batch[/bold green]")
        results: List[Dict[str, Any]] = []
        leads = discover_leads(self.bundle)
        new_leads = filter_new_leads(leads)
        if not new_leads:
            console.log("No new leads discovered; exiting batch.")
            return results

        for lead in new_leads:
            console.log(f"Processing lead: {lead.title}")
            lead = self._ensure_lead(lead)
            evidence_pack = gather_evidence(lead)
            plan = build_plan(lead, evidence_pack)
            article = compose_article(lead, plan, evidence_pack)
            article = apply_rules(article, plan, evidence_pack)
            cover = generate_cover_package(lead, plan)
            seo_package = build_seo_package(article, evidence_pack, cover, lead)
            publish_result = self.publisher.publish(article, cover, seo_package, lead)
            results.append(publish_result)
            self._persist_run(lead, article, cover, publish_result)
        console.log("[bold green]Batch complete[/bold green]")
        return results

    def _ensure_lead(self, lead: Lead) -> Lead:
        with session_scope() as session:
            existing = session.exec(select(Lead).where(Lead.url == lead.url)).first()
            if existing:
                return existing
            session.add(lead)
            session.commit()
            session.refresh(lead)
            return lead

    def _persist_run(
        self,
        lead: Lead,
        article: Article,
        cover: ImageAsset,
        publish_result: Dict[str, Any],
    ) -> None:
        with session_scope() as session:
            if not lead.id:
                session.add(lead)
                session.commit()
                session.refresh(lead)
            article.lead_id = lead.id or 0
            cover.lead_id = lead.id or 0

            existing_article = session.exec(
                select(Article).where(Article.slug == article.slug)
            ).first()
            if existing_article:
                existing_article.lead_id = article.lead_id
                existing_article.title = article.title
                existing_article.html = article.html
                existing_article.excerpt = article.excerpt
                existing_article.status = article.status
                existing_article.json_ld = article.json_ld
                existing_article.meta = article.meta
                session.add(existing_article)
                article = existing_article
            else:
                session.add(article)

            session.add(cover)
            session.commit()
            session.refresh(article)
            session.refresh(cover)
            publish = Publish(
                article_id=article.id or 0,
                platform=publish_result.get("platform", "wordpress"),
                remote_id=publish_result.get("remote_id"),
                url=publish_result.get("url"),
                status=publish_result.get("status", "draft"),
                meta=publish_result.get("meta"),
            )
            session.add(publish)
            session.commit()


__all__ = ["AutobotOrchestrator"]
