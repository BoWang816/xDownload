from __future__ import annotations

import time
from pathlib import Path
from typing import Optional

import typer
import uvicorn
from playwright.sync_api import sync_playwright
from rich.console import Console

from .bookmark_scraper import collect_tweet_urls
from .config import Settings
from .dashboard import create_dashboard_app
from .downloader import download_videos
from .login import ensure_logged_in, storage_exists
from .web_app import create_web_app


app = typer.Typer(help="Twitter 书签视频下载工具")
console = Console()


@app.command("download-bookmarks")
def download_bookmarks(
    limit: int = typer.Option(0, help="最多抓取推文数量，0 表示无限制"),
    headless: bool = typer.Option(True, "--headless/--no-headless", help="是否无头运行浏览器"),
    storage_state: Optional[Path] = typer.Option(None, help="登录状态文件"),
    download_dir: Optional[Path] = typer.Option(None, help="视频保存目录"),
    scroll_timeout: Optional[float] = typer.Option(None, help="滚动等待秒数"),
    history_file: Optional[Path] = typer.Option(None, help="下载历史记录文件"),
    skip_existing: bool = typer.Option(True, "--skip-existing/--no-skip-existing", help="跳过已下载的书签"),
    max_retries: Optional[int] = typer.Option(None, help="单条下载最大重试次数"),
    retry_delay: Optional[float] = typer.Option(None, help="下载重试间隔秒数"),
    watch: bool = typer.Option(False, "--watch/--no-watch", help="持续监测书签新增内容"),
    watch_interval: Optional[float] = typer.Option(None, help="监测模式下每轮间隔秒数"),
) -> None:
    """
    抓取书签并下载包含视频的推文。
    """
    settings = Settings.from_env()

    # CLI 选项优先于 .env，使用默认值
    storage_state = storage_state or settings.storage_state
    download_dir = download_dir or settings.download_dir
    scroll_timeout = scroll_timeout if scroll_timeout is not None else settings.scroll_timeout
    history_file = history_file or settings.history_file
    max_retries = max_retries if max_retries is not None else settings.max_retries
    retry_delay = retry_delay if retry_delay is not None else settings.retry_delay
    watch_interval = watch_interval if watch_interval is not None else settings.watch_interval

    download_dir.mkdir(parents=True, exist_ok=True)
    history_file.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as pw:
        browser = pw.firefox.launch(headless=headless)
        context_kwargs = {}
        if storage_exists(storage_state):
            context_kwargs["storage_state"] = str(storage_state)

        context = browser.new_context(**context_kwargs)
        page = context.new_page()

        ensure_logged_in(
            page,
            username=settings.username,
            password=settings.password,
            email=settings.email,
            storage_state_path=storage_state,
        )

        rounds = 0
        try:
            while True:
                rounds += 1
                console.log(f"[bold]开始第 {rounds} 轮书签扫描[/bold]")
                urls = collect_tweet_urls(
                    page,
                    limit=limit,
                    scroll_timeout=scroll_timeout,
                )
                console.log(f"本轮共获取 {len(urls)} 条书签")

                downloaded = download_videos(
                    urls,
                    download_dir=download_dir,
                    history_file=history_file,
                    skip_existing=skip_existing,
                    max_retries=max_retries,
                    retry_delay=retry_delay,
                )
                console.log(f"[green]本轮新增下载 {downloaded} 个文件[/green]")

                if not watch:
                    break

                console.log(f"[cyan]监控模式等待 {watch_interval} 秒后继续…[/cyan]")
                time.sleep(watch_interval)
        except KeyboardInterrupt:
            console.log("[yellow]检测到中断，退出监控模式[/yellow]")

        browser.close()


@app.command("serve-dashboard")
def serve_dashboard(
    host: str = typer.Option("0.0.0.0", help="监听地址"),
    port: int = typer.Option(8080, help="监听端口"),
) -> None:
    """
    运行 FastAPI 仪表盘，查看配置与历史记录。
    """
    settings = Settings.from_env()
    fastapi_app = create_dashboard_app(settings)
    uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


@app.command("serve-web")
def serve_web(
    host: str = typer.Option("0.0.0.0", help="监听地址"),
    port: int = typer.Option(8000, help="监听端口"),
) -> None:
    """
    运行 Web 应用，提供登录、浏览书签、选择下载的完整界面。
    """
    settings = Settings.from_env()
    fastapi_app = create_web_app(settings)
    uvicorn.run(fastapi_app, host=host, port=port, log_level="info")


def main() -> None:
    app()


if __name__ == "__main__":
    main()

