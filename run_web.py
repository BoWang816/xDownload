#!/usr/bin/env python3
"""直接运行 Web 应用的脚本"""

import sys
import uvicorn

# 添加 src 到路径
sys.path.insert(0, 'src')

from twitter_bookmarks_downloader.config import Settings
from twitter_bookmarks_downloader.web_app import create_web_app

if __name__ == "__main__":
    print("🚀 启动 Twitter 书签下载器 Web 应用...")
    print("📱 访问 http://localhost:8000")
    print("按 Ctrl+C 停止服务\n")
    
    settings = Settings.from_env()
    app = create_web_app(settings)
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
