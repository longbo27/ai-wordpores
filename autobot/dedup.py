"""Deduplication helpers to avoid reprocessing known leads."""
from __future__ import annotations

from typing import Iterable, List

from rich.console import Console
from sqlmodel import select

from .db import Article, Lead, session_scope

console = Console()


def filter_new_leads(leads: Iterable[Lead]) -> List[Lead]:
    if not leads:
        return []
    with session_scope() as session:
        existing_urls = {
            row[0]
            for row in session.exec(select(Lead.url))
        }
    new_leads: List[Lead] = []
    for lead in leads:
        if lead.url in existing_urls:
            console.log(f"Skipping duplicate lead: {lead.url}")
            continue
        new_leads.append(lead)
    return new_leads


__all__ = ["filter_new_leads"]
