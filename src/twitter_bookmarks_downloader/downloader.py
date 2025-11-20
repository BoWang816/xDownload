from __future__ import annotations

import re
import time
from datetime import datetime
from pathlib import Path
from typing import Iterable, Optional, Dict, Any

from rich.console import Console
from yt_dlp import YoutubeDL

from .history import load_history, save_history


console = Console()
STATUS_RE = re.compile(r"/status/(\\d+)")


def download_videos(
    urls: Iterable[str],
    *,
    download_dir: Path,
    history_file: Path,
    skip_existing: bool = True,
    max_retries: int = 3,
    retry_delay: float = 5.0,
) -> int:
    history = load_history(history_file)
    success_count = 0

    class Tracker:
        def __init__(self) -> None:
            self.last_file: Optional[str] = None

        def __call__(self, info: Dict[str, Any]) -> None:
            if info.get("status") == "finished":
                self.last_file = info.get("filename")

    tracker = Tracker()

    ydl_opts = {
        "outtmpl": str(download_dir / "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"),
        "format": "bv*+ba/best",
        "ignoreerrors": False,
        "noprogress": False,
        "quiet": True,
        "no_warnings": True,
        "writesubtitles": False,
        "merge_output_format": "mp4",
        "retries": 5,
        "progress_hooks": [tracker],
    }

    with YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            status_id = _extract_status_id(url)
            if skip_existing and status_id and status_id in history:
                console.log(f"[yellow]跳过已下载 {url}[/yellow]")
                continue

            success = _attempt_download(
                ydl=ydl,
                url=url,
                max_retries=max_retries,
                retry_delay=retry_delay,
            )

            if success and status_id:
                history[status_id] = {
                    "url": url,
                    "saved_file": tracker.last_file,
                    "downloaded_at": datetime.utcnow().isoformat() + "Z",
                }
                save_history(history_file, history)
                success_count += 1

    return success_count


def _attempt_download(
    *,
    ydl: YoutubeDL,
    url: str,
    max_retries: int,
    retry_delay: float,
) -> bool:
    for attempt in range(1, max_retries + 1):
        console.log(f"[cyan]下载 {url}（第 {attempt}/{max_retries} 次）[/cyan]")
        try:
            ydl.download([url])
            return True
        except Exception as exc:  # pylint: disable=broad-except
            console.log(f"[red]下载失败：{exc}[/red]")
            if attempt < max_retries:
                time.sleep(retry_delay)
    console.log(f"[red]放弃下载 {url}[/red]")
    return False


def _extract_status_id(url: str) -> Optional[str]:
    match = STATUS_RE.search(url)
    return match.group(1) if match else None

