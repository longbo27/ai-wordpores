"""Image generation utilities using Pillow to create compliant assets."""
from __future__ import annotations

from datetime import datetime
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

from .config import PROJECT_ROOT, load_settings
from .db import ImageAsset, Lead
from .planner import ContentPlan


WIDTH = 1200
HEIGHT = 630


COLORS = [
    (24, 92, 167),
    (5, 128, 176),
    (28, 52, 84),
    (92, 61, 147),
    (25, 102, 52),
]


def _draw_background(draw: ImageDraw.ImageDraw) -> None:
    for idx, color in enumerate(COLORS):
        draw.rectangle([
            (idx * WIDTH / len(COLORS), 0),
            ((idx + 1) * WIDTH / len(COLORS), HEIGHT),
        ], fill=color, outline=None)


def _draw_text(draw: ImageDraw.ImageDraw, hero: str) -> None:
    font = ImageFont.load_default()
    strapline = "Longbo Cloud — Fly, Card, Point"
    draw.text((40, 40), strapline, fill=(255, 255, 255), font=font)
    wrapped = []
    buffer = ""
    for char in hero:
        buffer += char
        if len(buffer) >= 12:
            wrapped.append(buffer)
            buffer = ""
    if buffer:
        wrapped.append(buffer)
    for idx, line in enumerate(wrapped[:4]):
        draw.text((40, 120 + idx * 60), line, fill=(255, 255, 255), font=font)


def generate_cover_package(lead: Lead, plan: ContentPlan) -> ImageAsset:
    settings = load_settings()
    assets_dir = settings.assets_dir
    assets_dir.mkdir(parents=True, exist_ok=True)
    image = Image.new("RGB", (WIDTH, HEIGHT))
    draw = ImageDraw.Draw(image)
    _draw_background(draw)
    _draw_text(draw, plan.hero_message[:48])

    filename = f"cover-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}.webp"
    path = assets_dir / filename
    image.save(path, format="WEBP", quality=85, method=6)

    alt_text = f"抽象旅行主题封面图，标题：{plan.hero_message[:30]}"
    asset = ImageAsset(
        lead_id=lead.id or 0,
        kind="cover",
        path=str(path.relative_to(PROJECT_ROOT)),
        alt_text=alt_text,
        width=WIDTH,
        height=HEIGHT,
    )
    return asset


__all__ = ["generate_cover_package"]
