## Twitter 书签视频下载器

该项目提供一个 Python/Playwright 工具，支持自动登录 Twitter（X），抓取账户书签中的推文，并使用 `yt-dlp` 自动下载推文内的视频资源。后续可直接封装为 Docker 镜像部署。

### 功能概览
- 使用 Playwright 自动化登录，首登后会在本地保存 `storage_state.json`，下次复用免登录。
- 自动滚动 `https://twitter.com/i/bookmarks` 页面，提取推文链接（支持限制数量）。
- 调用 `yt-dlp`（内置 Twitter 解析器）下载推文中存在的视频，支持断点续下、失败重试。
- 通过下载历史（`download_history.json`）实现去重，避免重复抓取与重复下载。
- 支持实时监测模式，定期轮询书签页并自动下载新增内容。
- 自带 FastAPI 仪表盘，可查看当前配置与下载历史。
- CLI 选项可配置下载目录、滚动超时、最大抓取数量、是否无头运行等。

### 快速开始
1. **准备 Python 环境**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   pip install -e .
   playwright install
   ```
2. **配置环境变量**（复制 `.env.example` 为 `.env` 并填写）：
   - `TWITTER_USERNAME`
   - `TWITTER_PASSWORD`
   - `TWITTER_EMAIL`（如账号触发安全验证时必填）
   - `DOWNLOAD_DIR`（可选，默认 `downloads`）
   - `HISTORY_FILE`（默认 `download_history.json`）
   - `MAX_DOWNLOAD_RETRIES`、`RETRY_DELAY`、`SKIP_EXISTING` 等
   - `WATCH_MODE`、`WATCH_INTERVAL`
3. **运行 CLI**
   ```bash
   python -m twitter_bookmarks_downloader.cli download-bookmarks \
     --limit 50 \
     --headless true
   ```
4. **启动仪表盘（可选）**
   ```bash
   python -m twitter_bookmarks_downloader.cli serve-dashboard --port 8080
   ```

### 命令行参数
- `--limit`：最多抓取的书签推文条数，`0` 表示不限。
- `--headless`：无头模式，调试时可设为 `false`。
- `--storage-state`：登录状态文件路径，默认 `storage_state.json`。
- `--download-dir`：视频下载目录。
- `--scroll-timeout`：滚动加载等待秒数。
- `--history-file`：下载历史记录存储路径。
- `--skip-existing/--no-skip-existing`：是否跳过历史里已成功的书签。
- `--max-retries`、`--retry-delay`：单条下载失败后重复尝试的次数与间隔。
- `--watch/--no-watch`、`--watch-interval`：开启实时监控模式及轮询间隔。

#### 仪表盘
- `serve-dashboard` 命令会启动 FastAPI + 原生 HTML 页面，曝光以下接口：
  - `/`：可视化页面，展示当前配置与历史下载表格。
  - `/api/config`、`/api/history`：供自定义脚本拉取信息。
- 默认监听 `0.0.0.0:8080`，可通过 `--host`、`--port` 参数调整。

### Docker（可选）
项目根目录包含示例 `Dockerfile`，可直接构建：
```bash
docker build -t twitter-bookmarks .
docker run --rm -it \
  -e TWITTER_USERNAME=xxx \
  -e TWITTER_PASSWORD=yyy \
  -e TWITTER_EMAIL=zzz \
  -v $PWD/downloads:/app/downloads \
  -p 8080:8080 \
  twitter-bookmarks \
  serve-dashboard --port 8080
```

或使用 `docker-compose.yml` 批量管理挂载与环境变量：
```bash
export TWITTER_USERNAME=xxx
export TWITTER_PASSWORD=yyy
# 先启动下载器
docker compose up --build twitter-bookmarks
# 另起一个终端启动仪表盘
docker compose up --build dashboard
```

### CI
仓库包含 `.github/workflows/ci.yml`，在 GitHub Actions 上会执行依赖安装、Playwright 浏览器部署与 `python -m compileall` 静态语法检查，确保提交可编译。

### 注意事项
- 建议开启 2FA 的账号提前准备 App 认证；当前示例未实现验证码/短信自动处理。
- 下载内容需遵守 Twitter 使用条款与版权政策。
- 大量书签会触发滚动等待，可调大 `--scroll-timeout` 或分批下载。

