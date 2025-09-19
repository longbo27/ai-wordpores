"""Database layer using SQLModel for persistence."""
from __future__ import annotations

from contextlib import contextmanager
from datetime import datetime
from typing import Any, Dict, Generator, Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Session, SQLModel, create_engine

from .config import Settings, load_settings


class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    kind: str
    status: str = Field(default="pending")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    payload: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))


class Lead(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    url: str = Field(index=True, unique=True)
    title: str
    source: str
    summary: str | None = None
    published_at: datetime | None = None
    score: float = 0.0
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Evidence(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(index=True)
    fact_id: str
    text: str
    source_url: str
    extracted_at: datetime = Field(default_factory=datetime.utcnow)


class Article(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(index=True)
    slug: str = Field(index=True, unique=True)
    title: str
    html: str
    excerpt: str
    status: str = Field(default="draft")
    json_ld: str | None = None
    meta: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class ImageAsset(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    lead_id: int = Field(index=True)
    kind: str = Field(default="cover")
    path: str
    alt_text: str
    width: int
    height: int
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Publish(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(index=True)
    platform: str = Field(default="wordpress")
    remote_id: str | None = None
    url: str | None = None
    status: str = Field(default="draft")
    meta: Dict[str, Any] | None = Field(default=None, sa_column=Column(JSON))
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Metric(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    article_id: int = Field(index=True)
    name: str
    value: float
    recorded_at: datetime = Field(default_factory=datetime.utcnow)


_engine = None


def get_engine(settings: Settings | None = None):
    global _engine
    if _engine is None:
        settings = settings or load_settings()
        _engine = create_engine(settings.database_url, echo=False)
        SQLModel.metadata.create_all(_engine)
    return _engine


@contextmanager
def session_scope(settings: Settings | None = None) -> Generator[Session, None, None]:
    engine = get_engine(settings)
    with Session(engine) as session:
        yield session


__all__ = [
    "Task",
    "Lead",
    "Evidence",
    "Article",
    "ImageAsset",
    "Publish",
    "Metric",
    "get_engine",
    "session_scope",
]
