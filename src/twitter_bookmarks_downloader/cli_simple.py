"""简化版 CLI 用于测试"""
from __future__ import annotations

from typing import Annotated

import typer
import uvicorn

from .config import Settings
from .web_app import create_web_app

app = typer.Typer(help="Twitter 书签视频下载工具")


@app.command("serve-web")
def serve_web(
    host: Annotated[str, typer.Option(help="监听地址")] = "0.0.0.0",
    port: Annotated[int, typer.Option(help="监听端口")] = 8000,
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
