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
import httpx

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
        self.cookies: Dict[str, str] = {}  # 存储 Twitter cookies


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
        print("=" * 60)
        print("🚀 启动 Twitter 书签下载器 Web 应用")
        print("=" * 60)
        print("[STARTUP] 初始化 Playwright...")
        app_state.playwright = await async_playwright().start()
        print("[STARTUP] 启动 Chromium 浏览器（无头模式）...")
        app_state.browser = await app_state.playwright.chromium.launch(headless=True)
        print("[STARTUP] ✓ 初始化完成！")
        print(f"[STARTUP] 访问 http://localhost:10000 开始使用")
        print("=" * 60)
    
    @app.on_event("shutdown")
    async def shutdown():
        """关闭时清理资源"""
        print("\n[SHUTDOWN] 正在关闭应用...")
        if app_state.context:
            print("[SHUTDOWN] 关闭浏览器上下文...")
            await app_state.context.close()
        if app_state.browser:
            print("[SHUTDOWN] 关闭浏览器...")
            await app_state.browser.close()
        if app_state.playwright:
            print("[SHUTDOWN] 停止 Playwright...")
            await app_state.playwright.stop()
        print("[SHUTDOWN] ✓ 清理完成，再见！")


    @app.post("/api/login")
    async def login(request: LoginRequest):
        """处理用户登录"""
        print(f"[LOGIN] 开始登录流程，用户名: {request.username}")
        try:
            storage_state_path = settings.storage_state
            
            # 检查是否有已保存的登录状态
            if storage_state_path.exists():
                print(f"[LOGIN] 发现已保存的登录状态: {storage_state_path}")
                app_state.context = await app_state.browser.new_context(
                    storage_state=str(storage_state_path)
                )
            else:
                print("[LOGIN] 创建新的浏览器上下文")
                app_state.context = await app_state.browser.new_context()
            
            app_state.page = await app_state.context.new_page()
            
            # 检查是否已登录
            print("[LOGIN] 检查是否已登录...")
            await app_state.page.goto("https://twitter.com/home", wait_until="domcontentloaded")
            await asyncio.sleep(2)
            
            current_url = app_state.page.url
            print(f"[LOGIN] 当前 URL: {current_url}")
            
            if "login" not in current_url and "home" in current_url:
                print("[LOGIN] ✓ 使用已保存的登录状态成功")
                
                # 提取 cookies
                print("[LOGIN] 提取 cookies...")
                cookies = await app_state.context.cookies()
                for cookie in cookies:
                    app_state.cookies[cookie['name']] = cookie['value']
                
                if 'auth_token' in app_state.cookies:
                    print(f"[LOGIN] ✓ 找到 auth_token")
                if 'ct0' in app_state.cookies:
                    print(f"[LOGIN] ✓ 找到 ct0 (CSRF token)")
                
                app_state.is_logged_in = True
                
                # 保存截图确认
                try:
                    await app_state.page.screenshot(path="debug_login_success.png")
                    print("[LOGIN] 已保存登录成功截图")
                except:
                    pass
                
                return {"success": True, "message": "使用已保存的登录状态"}
            
            # 执行登录流程
            print("[LOGIN] 开始执行登录流程...")
            await app_state.page.goto("https://twitter.com/i/flow/login", wait_until="networkidle")
            
            # 输入用户名
            print("[LOGIN] 输入用户名...")
            await app_state.page.fill('input[name="text"]', request.username)
            await app_state.page.click('div[role="button"][data-testid="LoginForm_Login_Button"]')
            await asyncio.sleep(2)

            
            # 处理可能的用户名确认
            print("[LOGIN] 检查是否需要邮箱验证...")
            try:
                await app_state.page.wait_for_selector('input[name="text"]', timeout=3000)
                value = request.email or request.username
                print(f"[LOGIN] 需要邮箱验证，输入: {value}")
                await app_state.page.fill('input[name="text"]', value)
                await app_state.page.click('div[role="button"][data-testid="ocfEnterTextNextButton"]')
                await asyncio.sleep(2)
            except Exception as e:
                print(f"[LOGIN] 无需邮箱验证: {e}")
                pass
            
            # 输入密码
            print("[LOGIN] 输入密码...")
            await app_state.page.fill('input[name="password"]', request.password)
            await app_state.page.click('div[data-testid="LoginForm_Login_Button"]')
            
            # 等待登录完成
            print("[LOGIN] 等待登录完成...")
            await app_state.page.wait_for_url("https://twitter.com/home*", timeout=30000)
            
            # 额外等待确保页面加载完成
            await asyncio.sleep(2)
            
            # 提取 cookies 用于 API 调用
            print("[LOGIN] 提取 cookies...")
            cookies = await app_state.context.cookies()
            for cookie in cookies:
                app_state.cookies[cookie['name']] = cookie['value']
            
            # 打印关键 cookies（用于调试）
            if 'auth_token' in app_state.cookies:
                print(f"[LOGIN] ✓ 找到 auth_token")
            if 'ct0' in app_state.cookies:
                print(f"[LOGIN] ✓ 找到 ct0 (CSRF token)")
            
            # 保存登录状态
            print(f"[LOGIN] 保存登录状态到: {storage_state_path}")
            await app_state.context.storage_state(path=str(storage_state_path))
            app_state.is_logged_in = True
            
            # 保存截图确认
            try:
                await app_state.page.screenshot(path="debug_login_new.png")
                print("[LOGIN] 已保存新登录截图")
            except:
                pass
            
            print("[LOGIN] ✓ 登录成功！")
            return {"success": True, "message": "登录成功"}
        
        except Exception as e:
            error_msg = f"登录失败: {str(e)}"
            print(f"[LOGIN] ✗ {error_msg}")
            import traceback
            traceback.print_exc()
            return JSONResponse(
                status_code=400,
                content={"success": False, "message": error_msg}
            )


    async def fetch_bookmarks_via_api(limit: int = 50) -> List[Dict[str, Any]]:
        """使用 Twitter API 获取书签"""
        print(f"[API] 使用 Twitter API 获取书签，限制: {limit}")
        
        if not app_state.cookies.get('auth_token') or not app_state.cookies.get('ct0'):
            raise Exception("缺少必要的 cookies (auth_token 或 ct0)")
        
        # Twitter GraphQL API endpoint
        url = "https://twitter.com/i/api/graphql/3XDB26fBve-MmjHaWTUZBQ/Bookmarks"
        
        headers = {
            "authorization": "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA",
            "x-csrf-token": app_state.cookies.get('ct0', ''),
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-active-user": "yes",
            "cookie": "; ".join([f"{k}={v}" for k, v in app_state.cookies.items()]),
        }
        
        variables = {
            "count": limit,
            "includePromotedContent": False
        }
        
        features = {
            "graphql_timeline_v2_bookmark_timeline": True,
            "responsive_web_graphql_exclude_directive_enabled": True,
            "verified_phone_label_enabled": False,
            "creator_subscriptions_tweet_preview_api_enabled": True,
            "responsive_web_graphql_timeline_navigation_enabled": True,
            "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
            "c9s_tweet_anatomy_moderator_badge_enabled": True,
            "tweetypie_unmention_optimization_enabled": True,
            "responsive_web_edit_tweet_api_enabled": True,
            "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
            "view_counts_everywhere_api_enabled": True,
            "longform_notetweets_consumption_enabled": True,
            "responsive_web_twitter_article_tweet_consumption_enabled": True,
            "tweet_awards_web_tipping_enabled": False,
            "freedom_of_speech_not_reach_fetch_enabled": True,
            "standardized_nudges_misinfo": True,
            "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
            "rweb_video_timestamps_enabled": True,
            "longform_notetweets_rich_text_read_enabled": True,
            "longform_notetweets_inline_media_enabled": True,
            "responsive_web_media_download_video_enabled": False,
            "responsive_web_enhance_cards_enabled": False
        }
        
        params = {
            "variables": json.dumps(variables),
            "features": json.dumps(features)
        }
        
        bookmarks = []
        
        async with httpx.AsyncClient() as client:
            try:
                print(f"[API] 发送请求到 Twitter API...")
                response = await client.get(url, headers=headers, params=params, timeout=30.0)
                response.raise_for_status()
                
                data = response.json()
                print(f"[API] ✓ 收到响应")
                
                # 解析响应
                instructions = data.get("data", {}).get("bookmark_timeline_v2", {}).get("timeline", {}).get("instructions", [])
                
                for instruction in instructions:
                    if instruction.get("type") == "TimelineAddEntries":
                        entries = instruction.get("entries", [])
                        
                        for entry in entries:
                            if entry.get("entryId", "").startswith("tweet-"):
                                content = entry.get("content", {})
                                item_content = content.get("itemContent", {})
                                tweet_results = item_content.get("tweet_results", {}).get("result", {})
                                
                                if not tweet_results:
                                    continue
                                
                                legacy = tweet_results.get("legacy", {})
                                user = tweet_results.get("core", {}).get("user_results", {}).get("result", {}).get("legacy", {})
                                
                                tweet_id = legacy.get("id_str", "")
                                text = legacy.get("full_text", "")
                                author = user.get("screen_name", "Unknown")
                                
                                # 检查是否有视频
                                media = legacy.get("extended_entities", {}).get("media", [])
                                has_video = False
                                video_url = None
                                thumbnail = None
                                
                                for m in media:
                                    if m.get("type") in ["video", "animated_gif"]:
                                        has_video = True
                                        thumbnail = m.get("media_url_https")
                                        # 获取最高质量的视频
                                        variants = m.get("video_info", {}).get("variants", [])
                                        max_bitrate = 0
                                        for variant in variants:
                                            if variant.get("content_type") == "video/mp4":
                                                bitrate = variant.get("bitrate", 0)
                                                if bitrate > max_bitrate:
                                                    max_bitrate = bitrate
                                                    video_url = variant.get("url")
                                        break
                                
                                if has_video and video_url:
                                    bookmarks.append({
                                        "id": tweet_id,
                                        "url": f"https://twitter.com/i/status/{tweet_id}",
                                        "text": text[:200],
                                        "author": author,
                                        "hasVideo": True,
                                        "videoUrl": video_url,
                                        "thumbnail": thumbnail
                                    })
                                    
                                    if len(bookmarks) >= limit:
                                        break
                        
                        if len(bookmarks) >= limit:
                            break
                
                print(f"[API] ✓ 解析到 {len(bookmarks)} 条包含视频的书签")
                return bookmarks
                
            except httpx.HTTPStatusError as e:
                print(f"[API] ✗ HTTP 错误: {e.response.status_code}")
                print(f"[API] 响应内容: {e.response.text[:500]}")
                raise Exception(f"Twitter API 请求失败: {e.response.status_code}")
            except Exception as e:
                print(f"[API] ✗ 错误: {str(e)}")
                import traceback
                traceback.print_exc()
                raise


    @app.get("/api/bookmarks")
    async def get_bookmarks(limit: int = 50):
        """获取书签列表"""
        print(f"[BOOKMARKS] 开始获取书签，限制: {limit}")
        if not app_state.is_logged_in:
            print("[BOOKMARKS] ✗ 未登录")
            raise HTTPException(status_code=401, detail="请先登录")
        
        try:
            # 使用 Twitter API 获取书签
            bookmarks = await fetch_bookmarks_via_api(limit)
            app_state.bookmarks = bookmarks
            
            print(f"[BOOKMARKS] ✓ 成功获取 {len(app_state.bookmarks)} 条书签")
            return {"success": True, "bookmarks": app_state.bookmarks}
        
        except Exception as e:
            error_msg = f"获取书签失败: {str(e)}"
            print(f"[BOOKMARKS] ✗ {error_msg}")
            import traceback
            traceback.print_exc()
            raise HTTPException(status_code=500, detail=error_msg)


    @app.post("/api/download")
    async def download_videos(request: DownloadRequest, background_tasks: BackgroundTasks):
        """下载选中的视频"""
        print(f"[DOWNLOAD] 开始下载任务，共 {len(request.tweet_ids)} 条")
        if not app_state.is_logged_in:
            print("[DOWNLOAD] ✗ 未登录")
            raise HTTPException(status_code=401, detail="请先登录")
        
        task_id = str(uuid4())
        app_state.download_tasks[task_id] = {
            "status": "pending",
            "total": len(request.tweet_ids),
            "completed": 0,
            "failed": 0,
            "items": []
        }
        
        print(f"[DOWNLOAD] 创建下载任务: {task_id}")
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
    print(f"[TASK-{task_id}] 开始后台下载任务，共 {len(tweet_ids)} 条")
    task = app_state.download_tasks[task_id]
    task["status"] = "running"
    
    history = load_history(settings.history_file)
    download_dir = settings.download_dir
    download_dir.mkdir(parents=True, exist_ok=True)
    
    for idx, tweet_id in enumerate(tweet_ids, 1):
        print(f"[TASK-{task_id}] [{idx}/{len(tweet_ids)}] 处理推文: {tweet_id}")
        
        try:
            # 从书签列表中查找视频 URL
            bookmark = next((b for b in app_state.bookmarks if b['id'] == tweet_id), None)
            
            if bookmark and bookmark.get('videoUrl'):
                # 直接下载视频 URL
                video_url = bookmark['videoUrl']
                print(f"[TASK-{task_id}] 使用直接链接下载")
                
                filename = f"{bookmark['author']}_{tweet_id}.mp4"
                filepath = download_dir / filename
                
                async with httpx.AsyncClient() as client:
                    response = await client.get(video_url, timeout=60.0)
                    response.raise_for_status()
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                
                task["completed"] += 1
                task["items"].append({
                    "tweet_id": tweet_id,
                    "status": "success",
                    "filename": filename
                })
                
                print(f"[TASK-{task_id}] ✓ 下载成功: {filename}")
                
                # 更新历史记录
                history[tweet_id] = {
                    "url": f"https://twitter.com/i/status/{tweet_id}",
                    "saved_file": str(filepath),
                    "downloaded_at": datetime.utcnow().isoformat() + "Z"
                }
            else:
                # 回退到 yt-dlp
                print(f"[TASK-{task_id}] 使用 yt-dlp 下载")
                url = f"https://twitter.com/i/status/{tweet_id}"
                
                ydl_opts = {
                    "outtmpl": str(download_dir / "%(uploader)s_%(upload_date)s_%(id)s.%(ext)s"),
                    "format": "bv*+ba/best",
                    "quiet": True,
                    "no_warnings": True,
                    "merge_output_format": "mp4",
                }
                
                with YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=True)
                    filename = ydl.prepare_filename(info)
                    
                    task["completed"] += 1
                    task["items"].append({
                        "tweet_id": tweet_id,
                        "status": "success",
                        "filename": Path(filename).name
                    })
                    
                    print(f"[TASK-{task_id}] ✓ 下载成功: {Path(filename).name}")
                    
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
            print(f"[TASK-{task_id}] ✗ 下载失败: {str(e)}")
    
    save_history(settings.history_file, history)
    task["status"] = "completed"
    print(f"[TASK-{task_id}] ✓ 任务完成！成功: {task['completed']}, 失败: {task['failed']}")



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
                    <label style="display: flex; align-items: center; gap: 8px; margin: 10px 0;">
                        <input type="checkbox" id="rememberMe" checked />
                        <span>记住用户名和密码</span>
                    </label>
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

        // 页面加载时恢复保存的用户名和密码
        window.addEventListener('DOMContentLoaded', () => {
            const savedUsername = localStorage.getItem('twitter_username');
            const savedPassword = localStorage.getItem('twitter_password');
            const savedEmail = localStorage.getItem('twitter_email');
            
            if (savedUsername) {
                document.getElementById('username').value = savedUsername;
            }
            if (savedPassword) {
                document.getElementById('password').value = savedPassword;
            }
            if (savedEmail) {
                document.getElementById('email').value = savedEmail;
            }
        });

        async function login() {
            const username = document.getElementById('username').value;
            const password = document.getElementById('password').value;
            const email = document.getElementById('email').value;
            const rememberMe = document.getElementById('rememberMe').checked;

            // 保存或清除用户名密码
            if (rememberMe) {
                localStorage.setItem('twitter_username', username);
                localStorage.setItem('twitter_password', password);
                if (email) {
                    localStorage.setItem('twitter_email', email);
                }
            } else {
                localStorage.removeItem('twitter_username');
                localStorage.removeItem('twitter_password');
                localStorage.removeItem('twitter_email');
            }

            
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
