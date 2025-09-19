"""Command line entry points for the Longbo Cloud autopublisher."""
from __future__ import annotations

import signal

import typer
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from rich.console import Console

from .config import load_bundle
from .monitor import emit_summary
from .orchestrator import AutobotOrchestrator
from .taxonomy import TaxonomyManager

app = typer.Typer(help="Longbo Cloud autonomous publishing toolkit")
console = Console()


def _create_scheduler(orchestrator: AutobotOrchestrator, times: list[str]) -> BlockingScheduler:
    scheduler = BlockingScheduler()
    for time_str in times:
        hour, minute = time_str.split(":")
        scheduler.add_job(orchestrator.run_once, CronTrigger(hour=int(hour), minute=int(minute)))
    return scheduler


@app.command()
def start(now: bool = typer.Option(False, "--now", help="立即执行一次完整流程")) -> None:
    bundle = load_bundle()
    orchestrator = AutobotOrchestrator(bundle)
    if now:
        results = orchestrator.run_once()
        emit_summary(results)
        return
    times = bundle.schedule.get("windows", ["08:00", "16:00"])
    scheduler = _create_scheduler(orchestrator, times)
    console.log("启动调度器，按计划运行批处理任务")

    def shutdown(signum, frame):  # pragma: no cover - runtime signal handling
        console.log("接收到退出信号，停止调度器")
        scheduler.shutdown()

    signal.signal(signal.SIGINT, shutdown)
    signal.signal(signal.SIGTERM, shutdown)
    scheduler.start()


@app.command()
def schedule() -> None:
    """启动每天 08:00 与 16:00 批处理计划任务。"""
    bundle = load_bundle()
    orchestrator = AutobotOrchestrator(bundle)
    times = bundle.schedule.get("windows", ["08:00", "16:00"])
    scheduler = _create_scheduler(orchestrator, times)
    console.log("计划任务已注册，按设定时间执行。")
    scheduler.start()


@app.command("sync-taxonomy")
def sync_taxonomy() -> None:
    bundle = load_bundle()
    manager = TaxonomyManager(bundle.settings)
    manager.resolve()
    console.log("分类和标签映射已更新。")


def main() -> None:
    app()


__all__ = ["app", "main"]
