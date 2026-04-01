from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


load_dotenv()


@dataclass(frozen=True)
class Settings:
    username: str
    password: str
    email: str | None
    download_dir: Path
    storage_state: Path
    headless: bool
    scroll_timeout: float
    limit: int
    history_file: Path
    skip_existing: bool
    max_retries: int
    retry_delay: float
    watch: bool
    watch_interval: float

    @staticmethod
    def from_env() -> "Settings":
        username = os.getenv("TWITTER_USERNAME", "").strip()
        password = os.getenv("TWITTER_PASSWORD", "").strip()
        email = os.getenv("TWITTER_EMAIL", "").strip() or None
        download_dir = Path(os.getenv("DOWNLOAD_DIR", "downloads")).expanduser()
        storage_state = Path(os.getenv("STORAGE_STATE_FILE", "storage_state.json")).expanduser()
        headless = os.getenv("HEADLESS", "true").lower() not in {"0", "false", "no"}
        scroll_timeout = float(os.getenv("SCROLL_TIMEOUT", "2.5"))
        limit = int(os.getenv("BOOKMARK_LIMIT", "0"))
        history_file = Path(os.getenv("HISTORY_FILE", "download_history.json")).expanduser()
        skip_existing = os.getenv("SKIP_EXISTING", "true").lower() not in {"0", "false", "no"}
        max_retries = int(os.getenv("MAX_DOWNLOAD_RETRIES", "3"))
        retry_delay = float(os.getenv("RETRY_DELAY", "5"))
        watch = os.getenv("WATCH_MODE", "false").lower() in {"1", "true", "yes"}
        watch_interval = float(os.getenv("WATCH_INTERVAL", "120"))

        # Web 应用模式下允许不提供用户名密码（在界面输入）
        # if not username or not password:
        #     raise RuntimeError("需要在环境变量中提供 TWITTER_USERNAME 与 TWITTER_PASSWORD")

        download_dir.mkdir(parents=True, exist_ok=True)
        history_file.parent.mkdir(parents=True, exist_ok=True)

        return Settings(
            username=username,
            password=password,
            email=email,
            download_dir=download_dir,
            storage_state=storage_state,
            headless=headless,
            scroll_timeout=scroll_timeout,
            limit=limit,
            history_file=history_file,
            skip_existing=skip_existing,
            max_retries=max_retries,
            retry_delay=retry_delay,
            watch=watch,
            watch_interval=watch_interval,
        )

