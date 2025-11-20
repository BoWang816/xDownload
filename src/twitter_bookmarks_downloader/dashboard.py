from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from .config import Settings
from .history import load_history


def _history_list(path: Path) -> List[Dict[str, Any]]:
    history = load_history(path)
    items = []
    for tweet_id, info in history.items():
        item = {
            "tweet_id": tweet_id,
            "url": info.get("url"),
            "saved_file": info.get("saved_file"),
            "downloaded_at": info.get("downloaded_at"),
        }
        items.append(item)
    items.sort(
        key=lambda x: x.get("downloaded_at") or datetime.min.isoformat(),
        reverse=True,
    )
    return items


def create_dashboard_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Twitter Bookmark Downloader Dashboard")

    @app.get("/api/history")
    def history_api() -> Dict[str, Any]:
        return {"items": _history_list(settings.history_file)}

    @app.get("/api/config")
    def config_api() -> Dict[str, Any]:
        return {
            "download_dir": str(settings.download_dir),
            "history_file": str(settings.history_file),
            "headless": settings.headless,
            "scroll_timeout": settings.scroll_timeout,
            "limit": settings.limit,
            "watch": settings.watch,
            "watch_interval": settings.watch_interval,
        }

    @app.get("/", response_class=HTMLResponse)
    def dashboard_page() -> str:
        return DASHBOARD_HTML

    return app


DASHBOARD_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8" />
  <title>Twitter 书签下载监控</title>
  <style>
    body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 24px; background: #f7f7f9; color: #222; }
    h1 { margin-bottom: 8px; }
    .card { background: #fff; border-radius: 12px; padding: 16px 20px; margin-bottom: 24px; box-shadow: 0 6px 18px rgba(0,0,0,0.05); }
    table { width: 100%; border-collapse: collapse; }
    th, td { padding: 8px 10px; text-align: left; border-bottom: 1px solid #eee; }
    th { background: #fafafa; }
    .badge { display: inline-block; padding: 2px 10px; border-radius: 8px; font-size: 12px; background: #eef2ff; color: #3730a3; }
  </style>
</head>
<body>
  <h1>Twitter 书签下载监控</h1>
  <p>实时查看当前配置、历史下载记录，方便排查与追踪。</p>

  <div class="card" id="configCard">
    <h2>当前配置</h2>
    <pre id="configJson">加载中...</pre>
  </div>

  <div class="card">
    <h2>下载历史 <span class="badge" id="historyCount">0</span></h2>
    <table>
      <thead>
        <tr>
          <th>ID</th>
          <th>链接</th>
          <th>文件</th>
          <th>时间</th>
        </tr>
      </thead>
      <tbody id="historyBody">
        <tr><td colspan="4">加载中...</td></tr>
      </tbody>
    </table>
  </div>

  <script>
    async function refreshConfig() {
      const res = await fetch("/api/config");
      const json = await res.json();
      document.getElementById("configJson").textContent = JSON.stringify(json, null, 2);
    }
    async function refreshHistory() {
      const res = await fetch("/api/history");
      const json = await res.json();
      const body = document.getElementById("historyBody");
      body.innerHTML = "";
      json.items.forEach(item => {
        const tr = document.createElement("tr");
        tr.innerHTML = `
          <td>${item.tweet_id}</td>
          <td><a href="${item.url}" target="_blank">${item.url}</a></td>
          <td>${item.saved_file || ""}</td>
          <td>${item.downloaded_at || ""}</td>
        `;
        body.appendChild(tr);
      });
      document.getElementById("historyCount").textContent = json.items.length;
    }
    function init() {
      refreshConfig();
      refreshHistory();
      setInterval(refreshHistory, 10000);
    }
    document.addEventListener("DOMContentLoaded", init);
  </script>
</body>
</html>
"""

