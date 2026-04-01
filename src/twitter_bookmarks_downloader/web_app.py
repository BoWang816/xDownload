"""
Web 应用：提供登录、浏览书签、选择下载视频的完整界面
"""
from __future__ import annotations

import asyncio
import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from uuid import uuid4

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from yt_dlp import YoutubeDL

from .config import Settings
from .history import load_history, save_history


# 全局状态管理
class AppState:
    def __init__(self):
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None
        self.is_logged_in = False
        self.bookmarks: List[Dict[str, Any]] = []
        self.download_tasks: Dict[str, Dict[str, Any]] = {}


app_state = AppState()


# API 模型
class LoginRequest(BaseModel):
    username: str
    password: str
    email: Optional[str] = None


class DownloadRequest(BaseModel):
    tweet_ids: List[str]


def create_web_app(settings: Settings) -> FastAPI:
    app = FastAPI(title="Twitter Bookmarks Downloader Web")

    @app.on_event("startup")
    async def startup():
        """启动时初始化 Playwright"""
        app_state.playwright = await async_playwright().start()
        app_state.browser = await app_state.playwright.chromium.launch(headless=False)
    
    @app.on_event("shutdown")
    async def shutdown():
        """关闭时清理资源"""
        if app_state.context:
            await app_state.context.close()
        if app_state.browser:
            await app_state.browser.close()
        if app_state.playwright:
            await app_state.playwright.stop()


    @app.post("/api/login")
    async def login(request: LoginRequest):
        """处理用户登录"""
        try:
            storage_state_path = settings.storage_state
            
            # 检查是否有已保存的登录状态
            if storage_state_path.exists():
                app_state.context = await app_state.browser.new_context(
                    storage_state=str(storage_state_path)
                )
            else:
                app_state.context = await app_state.browser.new_context()
            
            app_state.page = await app_state.context.new_page()
            
            # 检查是否已登录
            await app_state.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            if "login" not in app_state.page.url:
                app_state.is_logged_in = True
                return {"success": True, "message": "使用已保存的登录状态"}
            
            # 执行登录流程
            await app_state.page.goto("https://twitter.com/i/flow/login", wait_until="networkidle")
            
            # 输入用户名
            await app_state.page.fill('input[name="text"]', request.username)
            await app_state.page.click('div[role="button"][data-testid="LoginForm_Login_Button"]')
            await asyncio.sleep(2)

            
            # 处理可能的用户名确认
            try:
                await app_state.page.wait_for_selector('input[name="text"]', timeout=3000)
                value = request.email or request.username
                await app_state.page.fill('input[name="text"]', value)
                await app_state.page.click('div[role="button"][data-testid="ocfEnterTextNextButton"]')
                await asyncio.sleep(2)
            except:
                pass
            
            # 输入密码
            await app_state.page.fill('input[name="password"]', request.password)
            await app_state.page.click('div[data-testid="LoginForm_Login_Button"]')
            
            # 等待登录完成
            await app_state.page.wait_for_url("https://twitter.com/home*", timeout=30000)
            
            # 保存登录状态
            await app_state.context.storage_state(path=str(storage_state_path))
            app_state.is_logged_in = True
            
            return {"success": True, "message": "登录成功"}
        
        except Exception as e:
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": f"登录失败: {str(e)}"}
            )


    @app.get("/api/bookmarks")
    async def get_bookmarks(limit: int = 50):
        """获取书签列表"""
        if not app_state.is_logged_in or not app_state.page:
            raise HTTPException(status_code=401, detail="请先登录")
        
        try:
            await app_state.page.goto("https://twitter.com/i/bookmarks", wait_until="networkidle")
            
            bookmarks = []
            seen_ids = set()
            scroll_attempts = 0
            max_scrolls = 20
            
            while len(bookmarks) < limit and scroll_attempts < max_scrolls:
                # 提取推文信息
                tweets = await app_state.page.evaluate("""
                    () => {
                        const articles = document.querySelectorAll('article[data-testid="tweet"]');
                        return Array.from(articles).map(article => {
                            const link = article.querySelector('a[href*="/status/"]');
                            const text = article.querySelector('[data-testid="tweetText"]');
                            const user = article.querySelector('[data-testid="User-Name"]');
                            const video = article.querySelector('video');
                            const images = article.querySelectorAll('img[src*="media"]');
                            
                            if (!link) return null;
                            
                            const url = link.href.split('?')[0];
                            const match = url.match(/\\/status\\/(\\d+)/);
                            if (!match) return null;

                            
                            return {
                                id: match[1],
                                url: url,
                                text: text ? text.textContent : '',
                                author: user ? user.textContent.split('@')[0].trim() : 'Unknown',
                                hasVideo: !!video,
                                hasImages: images.length > 0,
                                imageCount: images.length,
                                thumbnail: video ? video.poster : (images.length > 0 ? images[0].src : null)
                            };
                        }).filter(t => t !== null);
                    }
                """)
                
                # 添加新推文
                for tweet in tweets:
                    if tweet['id'] not in seen_ids and (tweet['hasVideo'] or tweet['hasImages']):
                        seen_ids.add(tweet['id'])
                        bookmarks.append(tweet)
                
                # 滚动加载更多
                await app_state.page.mouse.wheel(0, 2000)
                await asyncio.sleep(2)
                scroll_attempts += 1
            
            app_state.bookmarks = bookmarks[:limit]
            return {"success": True, "bookmarks": app_state.bookmarks}
        
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"获取书签失败: {str(e)}")


    @app.post("/api/download")
    async def download_videos(request: DownloadRequest, background_tasks: BackgroundTasks):
        """下载选中的视频"""
        if not app_state.is_logged_in:
            raise HTTPException(status_code=401, detail="请先登录")
        
        task_id = str(uuid4())
        app_state.download_tasks[task_id] = {
            "status": "pending",
            "total": len(request.tweet_ids),
            "completed": 0,
            "failed": 0,
            "items": []
        }
        
        background_tasks.add_task(
            _download_task,
            task_id,
            request.tweet_ids,
            settings
        )
        
        return {"success": True, "task_id": task_id}

    @app.get("/api/download/{task_id}")
    async def get_download_status(task_id: str):
        """查询下载任务状态"""
        if task_id not in app_state.download_tasks:
            raise HTTPException(status_code=404, detail="任务不存在")
        
        return app_state.download_tasks[task_id]


    @app.get("/api/status")
    async def get_status():
        """获取应用状态"""
        return {
            "logged_in": app_state.is_logged_in,
            "bookmarks_count": len(app_state.bookmarks),
            "download_tasks": len(app_state.download_tasks)
        }

    @app.get("/", response_class=HTMLResponse)
    async def index():
        """主页面"""
        return WEB_UI_HTML

    return app


async def _download_task(task_id: str, tweet_ids: List[str], settings: Settings):
    """后台下载任务"""
    task = app_state.download_tasks[task_id]
    task["status"] = "running"
    
    history = load_history(settings.history_file)
    download_dir = settings.download_dir
    download_dir.mkdir(parents=True, exist_ok=True)

    
    ydl_opts = {
        "outtmpl": str(download_dir / "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"),
        "format": "bv*+ba/best",
        "quiet": True,
        "no_warnings": True,
        "merge_output_format": "mp4",
    }
    
    for tweet_id in tweet_ids:
        url = f"https://twitter.com/i/status/{tweet_id}"
        
        try:
            with YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                filename = ydl.prepare_filename(info)
                
                task["completed"] += 1
                task["items"].append({
                    "tweet_id": tweet_id,
                    "status": "success",
                    "filename": Path(filename).name
                })
                
                # 更新历史记录
                history[tweet_id] = {
                    "url": url,
                    "saved_file": filename,
                    "downloaded_at": datetime.utcnow().isoformat() + "Z"
                }
        
        except Exception as e:
            task["failed"] += 1
            task["items"].append({
                "tweet_id": tweet_id,
                "status": "failed",
                "error": str(e)
            })
    
    save_history(settings.history_file, history)
    task["status"] = "completed"



# Web UI HTML
WEB_UI_HTML = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Twitter 书签下载器</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .card {
            background: white;
            border-radius: 16px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
        }
        h1 {
            color: #1da1f2;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #657786;
            margin-bottom: 30px;
        }

        .login-form {
            display: flex;
            flex-direction: column;
            gap: 15px;
            max-width: 400px;
        }
        input {
            padding: 12px 16px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 15px;
            transition: border-color 0.3s;
        }
        input:focus {
            outline: none;
            border-color: #1da1f2;
        }
        button {
            padding: 12px 24px;
            background: #1da1f2;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 15px;
            font-weight: bold;
            cursor: pointer;
            transition: background 0.3s;
        }
        button:hover {
            background: #1a91da;
        }
        button:disabled {
            background: #aab8c2;
            cursor: not-allowed;
        }
        .hidden { display: none; }
        .bookmarks-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }

        .bookmark-item {
            border: 2px solid #e1e8ed;
            border-radius: 12px;
            padding: 15px;
            cursor: pointer;
            transition: all 0.3s;
            position: relative;
        }
        .bookmark-item:hover {
            border-color: #1da1f2;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(29,161,242,0.2);
        }
        .bookmark-item.selected {
            border-color: #1da1f2;
            background: #e8f5fe;
        }
        .bookmark-thumbnail {
            width: 100%;
            height: 180px;
            object-fit: cover;
            border-radius: 8px;
            margin-bottom: 10px;
            background: #f5f8fa;
        }
        .bookmark-author {
            font-weight: bold;
            color: #14171a;
            margin-bottom: 5px;
        }
        .bookmark-text {
            color: #657786;
            font-size: 14px;
            line-height: 1.4;
            max-height: 60px;
            overflow: hidden;
        }

        .media-badge {
            position: absolute;
            top: 20px;
            right: 20px;
            background: rgba(29,161,242,0.9);
            color: white;
            padding: 4px 8px;
            border-radius: 4px;
            font-size: 12px;
            font-weight: bold;
        }
        .checkbox {
            position: absolute;
            top: 15px;
            left: 15px;
            width: 24px;
            height: 24px;
            accent-color: #1da1f2;
        }
        .action-bar {
            display: flex;
            gap: 10px;
            align-items: center;
            margin-bottom: 20px;
        }
        .status-message {
            padding: 12px 16px;
            border-radius: 8px;
            margin-bottom: 20px;
        }
        .status-success {
            background: #d4edda;
            color: #155724;
            border: 1px solid #c3e6cb;
        }
        .status-error {
            background: #f8d7da;
            color: #721c24;
            border: 1px solid #f5c6cb;
        }

        .status-info {
            background: #d1ecf1;
            color: #0c5460;
            border: 1px solid #bee5eb;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e1e8ed;
            border-radius: 4px;
            overflow: hidden;
            margin-top: 10px;
        }
        .progress-fill {
            height: 100%;
            background: #1da1f2;
            transition: width 0.3s;
        }
        .select-all {
            margin-left: auto;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h1>🐦 Twitter 书签下载器</h1>
            <p class="subtitle">登录后浏览书签，选择想要下载的视频</p>
            
            <div id="statusMessage"></div>
            
            <!-- 登录表单 -->
            <div id="loginSection">
                <div class="login-form">
                    <input type="text" id="username" placeholder="用户名" />
                    <input type="password" id="password" placeholder="密码" />
                    <input type="text" id="email" placeholder="邮箱（可选，用于验证）" />
                    <button onclick="login()">登录</button>
                </div>
            </div>

            
            <!-- 书签浏览区 -->
            <div id="bookmarksSection" class="hidden">
                <div class="action-bar">
                    <button onclick="loadBookmarks()">刷新书签</button>
                    <button onclick="downloadSelected()" id="downloadBtn" disabled>下载选中 (0)</button>
                    <button onclick="selectAll()" class="select-all">全选</button>
                </div>
                
                <div id="downloadProgress" class="hidden">
                    <div class="status-info">
                        <div>下载进度: <span id="progressText">0/0</span></div>
                        <div class="progress-bar">
                            <div class="progress-fill" id="progressFill" style="width: 0%"></div>
                        </div>
                    </div>
                </div>
                
                <div id="bookmarksGrid" class="bookmarks-grid"></div>
            </div>
        </div>
    </div>

    <script>
        let selectedIds = new Set();
        let bookmarks = [];
        let downloadTaskId = null;

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const email = document.getElementById('email').value;

            
            if (!username || !password) {
                showMessage('请填写用户名和密码', 'error');
                return;
            }
            
            showMessage('正在登录...', 'info');
            
            try {
                const response = await fetch('/api/login', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ username, password, email: email || null })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    showMessage('登录成功！正在加载书签...', 'success');
                    document.getElementById('loginSection').classList.add('hidden');
                    document.getElementById('bookmarksSection').classList.remove('hidden');
                    loadBookmarks();
                } else {
                    showMessage(data.message || '登录失败', 'error');
                }
            } catch (error) {
                showMessage('登录失败: ' + error.message, 'error');
            }
        }


        async function loadBookmarks() {
            showMessage('正在加载书签...', 'info');
            
            try {
                const response = await fetch('/api/bookmarks?limit=50');
                const data = await response.json();
                
                if (data.success) {
                    bookmarks = data.bookmarks;
                    renderBookmarks();
                    showMessage(`成功加载 ${bookmarks.length} 条书签`, 'success');
                } else {
                    showMessage('加载书签失败', 'error');
                }
            } catch (error) {
                showMessage('加载书签失败: ' + error.message, 'error');
            }
        }

        function renderBookmarks() {
            const grid = document.getElementById('bookmarksGrid');
            grid.innerHTML = '';
            
            bookmarks.forEach(bookmark => {
                const item = document.createElement('div');
                item.className = 'bookmark-item';
                if (selectedIds.has(bookmark.id)) {
                    item.classList.add('selected');
                }

                
                const mediaType = bookmark.hasVideo ? '视频' : `${bookmark.imageCount}张图片`;
                
                item.innerHTML = `
                    <input type="checkbox" class="checkbox" 
                           ${selectedIds.has(bookmark.id) ? 'checked' : ''}
                           onchange="toggleSelect('${bookmark.id}')">
                    <div class="media-badge">${mediaType}</div>
                    ${bookmark.thumbnail ? 
                        `<img src="${bookmark.thumbnail}" class="bookmark-thumbnail" />` :
                        '<div class="bookmark-thumbnail"></div>'}
                    <div class="bookmark-author">${bookmark.author}</div>
                    <div class="bookmark-text">${bookmark.text}</div>
                `;
                
                item.onclick = (e) => {
                    if (e.target.type !== 'checkbox') {
                        toggleSelect(bookmark.id);
                    }
                };
                
                grid.appendChild(item);
            });
            
            updateDownloadButton();
        }


        function toggleSelect(id) {
            if (selectedIds.has(id)) {
                selectedIds.delete(id);
            } else {
                selectedIds.add(id);
            }
            renderBookmarks();
        }

        function selectAll() {
            if (selectedIds.size === bookmarks.length) {
                selectedIds.clear();
            } else {
                bookmarks.forEach(b => selectedIds.add(b.id));
            }
            renderBookmarks();
        }

        function updateDownloadButton() {
            const btn = document.getElementById('downloadBtn');
            btn.textContent = `下载选中 (${selectedIds.size})`;
            btn.disabled = selectedIds.size === 0;
        }

        async function downloadSelected() {
            if (selectedIds.size === 0) return;
            
            showMessage(`开始下载 ${selectedIds.size} 个项目...`, 'info');

            
            try {
                const response = await fetch('/api/download', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ tweet_ids: Array.from(selectedIds) })
                });
                
                const data = await response.json();
                
                if (data.success) {
                    downloadTaskId = data.task_id;
                    document.getElementById('downloadProgress').classList.remove('hidden');
                    monitorDownload();
                } else {
                    showMessage('启动下载失败', 'error');
                }
            } catch (error) {
                showMessage('下载失败: ' + error.message, 'error');
            }
        }

        async function monitorDownload() {
            if (!downloadTaskId) return;
            
            try {
                const response = await fetch(`/api/download/${downloadTaskId}`);
                const task = await response.json();

                
                const progress = ((task.completed + task.failed) / task.total * 100).toFixed(0);
                document.getElementById('progressText').textContent = 
                    `${task.completed + task.failed}/${task.total} (成功: ${task.completed}, 失败: ${task.failed})`;
                document.getElementById('progressFill').style.width = progress + '%';
                
                if (task.status === 'completed') {
                    showMessage(`下载完成！成功: ${task.completed}, 失败: ${task.failed}`, 'success');
                    downloadTaskId = null;
                    selectedIds.clear();
                    renderBookmarks();
                } else {
                    setTimeout(monitorDownload, 1000);
                }
            } catch (error) {
                console.error('监控下载失败:', error);
            }
        }

        function showMessage(text, type) {
            const msg = document.getElementById('statusMessage');
            msg.className = `status-message status-${type}`;
            msg.textContent = text;
            msg.style.display = 'block';
            
            if (type === 'success' || type === 'error') {
                setTimeout(() => { msg.style.display = 'none'; }, 5000);
            }
        }

    </script>
</body>
</html>
"""
