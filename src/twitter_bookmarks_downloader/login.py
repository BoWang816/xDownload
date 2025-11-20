from __future__ import annotations

from pathlib import Path
from typing import Optional

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError
from rich.console import Console


console = Console()


LOGIN_URL = "https://twitter.com/i/flow/login"


def storage_exists(storage_state: Path) -> bool:
    return storage_state.exists() and storage_state.stat().st_size > 0


def ensure_logged_in(
    page: Page,
    *,
    username: str,
    password: str,
    email: Optional[str],
    storage_state_path: Path,
) -> None:
    """
    确认已登录；若未登录则执行流程并保存 storage_state。
    """
    if _is_authenticated(page):
        console.log("[green]已复用登录状态[/green]")
        return

    console.log("[yellow]尝试执行登录流程…[/yellow]")
    page.goto(LOGIN_URL, wait_until="networkidle")

    page.fill('input[name="text"]', username)
    page.click('div[role="button"][data-testid="LoginForm_Login_Button"]')

    _handle_possible_username_confirmation(page, username, email)

    page.fill('input[name="password"]', password)
    page.click('div[data-testid="LoginForm_Login_Button"]')

    try:
        page.wait_for_url("https://twitter.com/home*", timeout=30000)
    except PlaywrightTimeoutError as exc:
        console.log("[red]登录可能失败，请检查账号验证状态[/red]")
        raise RuntimeError("Twitter 登录失败") from exc

    page.context.storage_state(path=str(storage_state_path))
    console.log(f"[green]登录成功，状态已保存至 {storage_state_path}[/green]")


def _is_authenticated(page: Page) -> bool:
    try:
        page.goto("https://twitter.com/home", wait_until="domcontentloaded")
        return "login" not in page.url
    except PlaywrightTimeoutError:
        return False


def _handle_possible_username_confirmation(page: Page, username: str, email: Optional[str]) -> None:
    """
    部分账号会要求再次输入用户名或邮箱确认。
    """
    try:
        page.wait_for_selector('input[name="text"]', timeout=5000)
    except PlaywrightTimeoutError:
        return

    # 如果仍在输入用户名的页面，就填入 email 或 username
    if "challenge" in page.url or page.is_visible('input[name="text"]'):
        value = email or username
        page.fill('input[name="text"]', value)
        page.click('div[role="button"][data-testid="ocfEnterTextNextButton"]')

