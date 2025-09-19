"""Evidence gathering and fact extraction from discovered leads."""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from rich.console import Console

from .db import Lead

console = Console()


@dataclass(slots=True)
class EvidenceItem:
    fact_id: str
    text: str
    source_url: str


@dataclass(slots=True)
class EvidencePack:
    lead: Lead
    items: List[EvidenceItem]

    def as_citation_markup(self) -> str:
        return "".join(f"[{item.fact_id}]" for item in self.items)


SPLIT_CHARS = "。！？!?.\n"


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    sentences: List[str] = []
    buffer = ""
    for char in text:
        buffer += char
        if char in SPLIT_CHARS:
            sentences.append(buffer.strip())
            buffer = ""
    if buffer.strip():
        sentences.append(buffer.strip())
    return [s for s in sentences if len(s) > 2]


def gather_evidence(lead: Lead) -> EvidencePack:
    sentences = _split_sentences(lead.summary or "")
    if not sentences:
        sentences = [lead.title]
    items: List[EvidenceItem] = []
    for idx, sentence in enumerate(sentences[:5], start=1):
        fact_id = f"F{idx}"
        items.append(EvidenceItem(fact_id=fact_id, text=sentence.strip(), source_url=lead.url))
    console.log(f"Collected {len(items)} evidence items for lead")
    return EvidencePack(lead=lead, items=items)


__all__ = ["EvidenceItem", "EvidencePack", "gather_evidence"]
