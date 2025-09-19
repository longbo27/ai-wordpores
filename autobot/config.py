"""Configuration management utilities for the Longbo Cloud autopublisher."""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = PROJECT_ROOT / "config"
ENV_FILE = PROJECT_ROOT / ".env"


class Settings(BaseModel):
    """Runtime configuration derived from environment variables."""

    wp_base_url: str = Field("https://longbo.cloud", alias="WP_BASE_URL")
    wp_user: str | None = Field(default=None, alias="WP_USER")
    wp_app_pass: str | None = Field(default=None, alias="WP_APP_PASS")
    openai_api_key: str | None = Field(default=None, alias="OPENAI_API_KEY")
    image_engine: str = Field("auto", alias="IMAGE_ENGINE")
    database_url: str = Field(default=f"sqlite:///{(PROJECT_ROOT / 'autobot.sqlite3').as_posix()}")
    assets_dir: Path = Field(default=PROJECT_ROOT / "autobot" / "assets")
    output_dir: Path = Field(default=PROJECT_ROOT / "output")
    logs_dir: Path = Field(default=PROJECT_ROOT / "autobot" / "logs")

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True


@dataclass(slots=True)
class ConfigBundle:
    settings: Settings
    sources: Dict[str, Any]
    schedule: Dict[str, Any]
    thresholds: Dict[str, Any]


def _read_yaml(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    with path.open("r", encoding="utf-8") as handle:
        content = yaml.safe_load(handle)
    return content or {}


def load_settings() -> Settings:
    load_dotenv(ENV_FILE)
    values: Dict[str, Any] = {}
    for field_name, field_info in Settings.model_fields.items():
        env_key = field_info.alias or field_name.upper()
        if env_key in os.environ:
            values[field_name] = os.environ[env_key]
    settings = Settings(**values)
    settings.assets_dir.mkdir(parents=True, exist_ok=True)
    settings.output_dir.mkdir(parents=True, exist_ok=True)
    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    return settings


def load_bundle() -> ConfigBundle:
    settings = load_settings()
    sources = _read_yaml(CONFIG_DIR / "sources.yml")
    schedule = _read_yaml(CONFIG_DIR / "schedule.yml")
    thresholds = _read_yaml(CONFIG_DIR / "thresholds.yml")
    return ConfigBundle(settings=settings, sources=sources, schedule=schedule, thresholds=thresholds)


__all__ = ["Settings", "ConfigBundle", "load_settings", "load_bundle", "PROJECT_ROOT", "CONFIG_DIR"]
