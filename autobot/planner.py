"""Content planning logic creating outlines and SEO briefs."""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import List

from rich.console import Console

from .db import Lead
from .research import EvidencePack

console = Console()


@dataclass(slots=True)
class Section:
    heading: str
    purpose: str


@dataclass(slots=True)
class ContentPlan:
    lead: Lead
    content_type: str
    sections: List[Section]
    internal_keywords: List[str]
    hero_message: str
    deal_deadline: datetime | None = None


DEFAULT_SECTIONS = [
    ("速览要点", "用3-5个要点概括政策与价值"),
    ("玩法解析", "介绍参与步骤和注意事项"),
    ("值不值得", "通过算账示例评估收益"),
    ("实用FAQ", "常见问题与答复"),
    ("总结与提醒", "呼吁关注更新或截止日期"),
]


KEYWORDS = ["航司里程", "信用卡积分", "酒店会籍", "里程票", "旅行攻略", "长程商务舱"]


def build_plan(lead: Lead, evidence_pack: EvidencePack) -> ContentPlan:
    summary_text = (lead.summary or "").lower()
    content_type = "flash" if "limited" in summary_text or "结束" in summary_text else "deep"
    internal_keywords = KEYWORDS[:5]
    hero_message = lead.title
    deal_deadline = None
    for item in evidence_pack.items:
        if "截止" in item.text or "截至" in item.text:
            deal_deadline = datetime.utcnow()
            break
    sections = [Section(heading=title, purpose=purpose) for title, purpose in DEFAULT_SECTIONS]
    console.log(f"Generated content plan with {len(sections)} sections")
    return ContentPlan(
        lead=lead,
        content_type=content_type,
        sections=sections,
        internal_keywords=internal_keywords,
        hero_message=hero_message,
        deal_deadline=deal_deadline,
    )


__all__ = ["Section", "ContentPlan", "build_plan"]
