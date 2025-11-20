from __future__ import annotations

from typing import Set, List

from playwright.sync_api import Page
from rich.console import Console


BOOKMARK_URL = "https://twitter.com/i/bookmarks"
console = Console()


def collect_tweet_urls(
    page: Page,
    *,
    limit: int = 0,
    scroll_timeout: float = 2.5,
) -> list[str]:
    page.goto(BOOKMARK_URL, wait_until="networkidle")

    seen: Set[str] = set()
    collected: List[str] = []
    idle_rounds = 0

    def _extract() -> None:
        urls = page.eval_on_selector_all(
            'a[href*="/status/"][role="link"]',
            "els => Array.from(new Set(els.map(el => el.href.split('?')[0])))",
        )
        for url in urls:
            if "/status/" in url and url not in seen:
                seen.add(url)
                collected.append(url)

    while True:
        _extract()
        console.log(f"已发现 {len(collected)} 条书签")

        if limit and len(collected) >= limit:
            break

        last_height = page.evaluate("document.body.scrollHeight")
        page.mouse.wheel(0, 2000)
        page.wait_for_timeout(scroll_timeout * 1000)
        new_height = page.evaluate("document.body.scrollHeight")

        if new_height <= last_height:
            idle_rounds += 1
        else:
            idle_rounds = 0

        if idle_rounds >= 3:
            console.log("[yellow]检测到已滑动到底部或无更多内容[/yellow]")
            break

    return collected[:limit] if limit else collected

