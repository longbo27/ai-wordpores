"""Monitoring utilities for optional reporting."""
from __future__ import annotations

from typing import Any, Dict, List

from rich.console import Console

console = Console()


def emit_summary(results: List[Dict[str, Any]]) -> None:
    for result in results:
        console.log(f"结果：{result.get('status')} -> {result.get('url')}")


__all__ = ["emit_summary"]
