# Twitter 书签视频下载器

> 一个功能完整的 Twitter/X 书签视频下载工具，支持 Web 界面、命令行和 Docker 部署

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📖 目录

- [主要特性](#主要特性)
- [快速开始](#快速开始)
- [详细使用](#详细使用)
- [功能说明](#功能说明)
- [Docker 完整指南](#docker-完整指南)
- [中国大陆部署](#中国大陆部署)
- [故障排除](#故障排除)
- [常见问题](#常见问题)
- [更新日志](#更新日志)
- [项目结构](#项目结构)

---

## 🌟 主要特性

### 🌐 Web 可视化界面（推荐）

- **表单登录**：无需配置文件，直接在网页输入账号密码
- **卡片式浏览**：缩略图、作者、文本预览一目了然
- **智能筛选**：自动识别包含视频或图片的推文
- **批量选择**：支持单选、多选、全选操作
- **实时下载**：后台异步下载，前端实时显示进度
- **响应式设计**：支持桌面和移动端

### 🤖 命令行批量下载

- **自动化批量下载**：无人值守批量处理
- **定时任务集成**：支持 cron 定时运行
- **监控模式**：持续运行，自动下载新增书签
- **灵活配置**：丰富的参数和环境变量支持

### 🔐 智能登录管理

- **自动保存状态**：首次登录后自动保存
- **免密码登录**：下次启动自动复用登录状态
- **邮箱验证支持**：处理 Twitter 的邮箱验证流程
- **错误处理**：清晰的错误提示和重试机制

### 📥 可靠下载功能

- **基于 yt-dlp**：使用成熟的下载工具
- **自动重试**：下载失败自动重试
- **断点续传**：支持中断后继续下载
- **历史记录**：自动去重，跳过已下载内容

### 🐳 Docker 容器化部署

- **一键部署**：使用 docker-compose 快速启动
- **多种模式**：Web、CLI、仪表盘三种运行模式
- **数据持久化**：自动挂载数据卷
- **生产就绪**：适合服务器长期运行
- **镜像优化**：使用 Chromium，镜像仅 800MB

---

## 🚀 快速开始

### Web 界面（推荐）

最简单的使用方式，5 分钟上手：

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd twitter-bookmarks-downloader

# 2. 一键启动
chmod +x start_web.sh
./start_web.sh

# 3. 打开浏览器访问 http://localhost:10000
```

**使用流程：**
1. **登录** - 在网页输入 Twitter 用户名和密码
2. **浏览** - 自动加载书签，查看缩略图和内容
3. **选择** - 点击卡片选择，或使用全选按钮
4. **下载** - 点击"下载选中"，查看实时进度
5. **完成** - 文件保存在 `downloads` 目录

### 命令行模式

适合自动化和批量下载：

```bash
# 1. 安装依赖
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
playwright install chromium

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写账号信息

# 3. 运行下载
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 50
```

### Docker 部署

生产环境推荐使用 Docker：

```bash
# 方式 1：使用 Makefile（最简单）
make docker-build    # 构建镜像
make docker-up       # 启动容器
make docker-logs     # 查看日志

# 方式 2：使用 docker-compose
docker compose build
docker compose up web

# 方式 3：使用构建脚本
./docker-build.sh
docker compose up web
```

**访问应用：**
- Web 应用：http://localhost:10000
- 仪表盘：http://localhost:8080

---

## 📚 详细使用

### 安装依赖

#### 本地安装

```bash
# 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装 Python 依赖
pip install -r requirements.txt
pip install -e .

# 安装 Playwright 浏览器
playwright install chromium
```

#### 系统要求

- Python 3.11+
- 2GB+ 内存
- 5GB+ 磁盘空间

### 环境配置

创建 `.env` 文件（Web 模式可选，CLI 模式必填）：

```bash
# Twitter 账号信息
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com  # 可选，用于验证

# 下载配置
DOWNLOAD_DIR=downloads
STORAGE_STATE_FILE=storage_state.json
HISTORY_FILE=download_history.json

# 浏览器配置
HEADLESS=true
SCROLL_TIMEOUT=2.5

# 抓取配置
BOOKMARK_LIMIT=0  # 0 表示不限制

# 下载配置
SKIP_EXISTING=true
MAX_DOWNLOAD_RETRIES=3
RETRY_DELAY=5

# 监控模式
WATCH_MODE=false
WATCH_INTERVAL=120
```

### 命令参数

#### Web 应用

```bash
# 启动 Web 应用
python -m twitter_bookmarks_downloader.cli serve-web [OPTIONS]

# 或使用简化脚本
python run_web.py
```

**选项：**
- `--host TEXT` - 监听地址（默认：0.0.0.0）
- `--port INTEGER` - 监听端口（默认：10000）

#### 命令行下载

```bash
python -m twitter_bookmarks_downloader.cli download-bookmarks [OPTIONS]
```

**常用选项：**
- `--limit INTEGER` - 最多抓取推文数量（0=不限）
- `--headless/--no-headless` - 是否无头运行浏览器
- `--storage-state PATH` - 登录状态文件路径
- `--download-dir PATH` - 视频保存目录
- `--scroll-timeout FLOAT` - 滚动等待秒数
- `--history-file PATH` - 下载历史记录文件
- `--skip-existing/--no-skip-existing` - 跳过已下载的书签
- `--max-retries INTEGER` - 单条下载最大重试次数
- `--retry-delay FLOAT` - 下载重试间隔秒数
- `--watch/--no-watch` - 持续监测书签新增内容
- `--watch-interval FLOAT` - 监测模式下每轮间隔秒数

**示例：**

```bash
# 下载前 50 条书签
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 50

# 下载所有书签
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 0

# 监控模式，每 5 分钟检查一次
python -m twitter_bookmarks_downloader.cli download-bookmarks --watch --watch-interval 300

# 非无头模式（可以看到浏览器）
python -m twitter_bookmarks_downloader.cli download-bookmarks --no-headless
```

---

## 🎯 功能说明

### Web 界面功能

#### 登录页面
- 用户名/密码输入
- 可选邮箱验证
- 自动保存登录状态
- 错误提示

#### 书签浏览
- 卡片式展示
- 缩略图预览
- 作者信息
- 推文文本
- 媒体类型标签（视频/图片）

#### 下载功能
- 单选/多选
- 全选按钮
- 实时进度条
- 成功/失败统计
- 自动去重

### 命令行功能

#### 自动登录
- 首次登录保存状态
- 后续自动复用
- 支持邮箱验证
- 错误处理

#### 书签抓取
- 自动滚动加载
- 智能去重
- 限制数量
- 进度显示

#### 视频下载
- 基于 yt-dlp
- 自动重试
- 断点续传
- 历史记录
- 跳过已下载

#### 监控模式
- 定期轮询
- 自动下载新增
- 持续运行
- 可配置间隔

---

## 🐳 Docker 完整指南

### 构建镜像

#### 使用 Makefile

```bash
# 查看所有命令
make help

# 构建镜像
make docker-build

# 测试镜像
make docker-test

# 启动容器
make docker-up

# 查看日志
make docker-logs

# 停止容器
make docker-down

# 进入容器
make docker-shell
```

#### 使用 docker-compose

```bash
# 构建镜像
docker compose build

# 构建时不使用缓存
docker compose build --no-cache

# 查看镜像
docker images | grep twitter-bookmarks
```

#### 使用构建脚本

```bash
# 国际版
./docker-build.sh

# 中国大陆优化版（推荐）
./docker-build-cn.sh

# 构建指定标签
./docker-build.sh v1.0.0
```

### 运行容器

#### Web 应用模式

```bash
# 前台运行
docker compose up web

# 后台运行
docker compose up -d web

# 查看日志
docker compose logs -f web

# 停止服务
docker compose down
```

#### 命令行下载模式

```bash
# 启动下载器
docker compose --profile cli up downloader

# 后台运行
docker compose --profile cli up -d downloader

# 查看日志
docker compose --profile cli logs -f downloader
```

#### 仪表盘模式

```bash
# 启动仪表盘
docker compose --profile dashboard up dashboard

# 后台运行
docker compose --profile dashboard up -d dashboard
```

### 数据持久化

#### 挂载卷

```yaml
volumes:
  - ./downloads:/app/downloads      # 下载的视频文件
  - ./state:/app/state              # 登录状态和历史记录
```

#### 数据目录结构

```
.
├── downloads/                      # 下载的视频
│   ├── author_20260401_123456.mp4
│   └── author_20260402_789012.mp4
└── state/                          # 应用状态
    ├── storage_state.json          # 登录状态
    └── download_history.json       # 下载历史
```

### 容器管理

```bash
# 查看运行中的容器
docker compose ps

# 查看所有容器
docker ps -a

# 重启容器
docker compose restart web

# 停止容器
docker compose stop web

# 删除容器
docker compose down

# 删除容器和数据卷
docker compose down -v

# 查看容器资源使用
docker stats twitter-bookmarks-web

# 查看容器详细信息
docker inspect twitter-bookmarks-web
```

### 日志管理

```bash
# 查看日志
docker compose logs web

# 实时跟踪日志
docker compose logs -f web

# 查看最近 100 行
docker compose logs --tail=100 web

# 导出日志
docker compose logs web > logs.txt
```

### 镜像信息

- **基础镜像**: python:3.11-slim
- **浏览器**: Chromium（比 Firefox 减少 40% 大小）
- **镜像大小**: ~800MB
- **暴露端口**: 10000（Web）、8080（仪表盘）
- **工作目录**: /app
- **数据卷**: /app/downloads、/app/state

### 为什么需要浏览器？

Docker 镜像包含 Chromium 浏览器是必需的，因为：
1. **自动登录**：使用 Playwright 模拟真实用户登录 Twitter
2. **抓取书签**：Twitter 书签是动态加载的，需要浏览器执行 JavaScript 并滚动页面
3. **处理验证**：可能遇到邮箱验证等交互式流程

**优化说明：**
- 项目已从 Firefox 切换到 Chromium
- 镜像大小从 1.5GB 减少到 800MB（减少 40%）
- 构建时间减少约 50%
- 内存占用减少约 17%

---

## 🇨🇳 中国大陆部署

### 快速解决网络问题

在中国大陆使用 Docker 时，经常会遇到网络连接问题。以下是完整的解决方案：

#### 方式一：使用优化的构建脚本（推荐）

```bash
# 使用中国大陆优化版构建脚本
chmod +x docker-build-cn.sh
./docker-build-cn.sh
```

#### 方式二：使用优化的 Dockerfile

```bash
# 使用国内镜像源的 Dockerfile
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .
```

### 配置 Docker 镜像加速

#### Docker Desktop（macOS/Windows）

1. 打开 Docker Desktop
2. 点击设置图标 ⚙️
3. 选择 "Docker Engine"
4. 添加以下配置：

```json
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
```

5. 点击 "Apply & Restart"

#### Linux

编辑 `/etc/docker/daemon.json`：

```bash
sudo mkdir -p /etc/docker
sudo tee /etc/docker/daemon.json <<-'EOF'
{
  "registry-mirrors": [
    "https://mirror.ccs.tencentyun.com",
    "https://hub-mirror.c.163.com",
    "https://docker.mirrors.ustc.edu.cn"
  ]
}
EOF

sudo systemctl daemon-reload
sudo systemctl restart docker
```

### 推荐的镜像源

#### 1. 腾讯云（推荐）
```
https://mirror.ccs.tencentyun.com
```
- 速度快、稳定性好、无需注册

#### 2. 阿里云
```
https://[your-id].mirror.aliyuncs.com
```
- 需要注册阿里云账号获取专属加速地址
- 访问 https://cr.console.aliyun.com/ 获取

#### 3. 网易云
```
https://hub-mirror.c.163.com
```
- 无需注册、稳定可靠

#### 4. 中科大
```
https://docker.mirrors.ustc.edu.cn
```
- 教育网速度快、公益服务

---

## 🔧 故障排除

### 启动问题

#### start_web.sh 失败

**症状：**
```
TypeError: Secondary flag is not valid for non-boolean flag.
```

**原因：** Typer 0.12.5 版本的已知 bug

**解决方案：**

```bash
# 方式 1：使用更新后的启动脚本
./start_web.sh

# 方式 2：直接运行
source .venv/bin/activate
python run_web.py
```

### 登录问题

#### 登录失败

**可能原因：**
1. 用户名或密码错误
2. 账号需要邮箱验证
3. 网络连接问题
4. Twitter 安全检查

**解决方案：**
1. 检查用户名密码是否正确
2. 如果有邮箱验证，填写邮箱字段
3. 删除 `storage_state.json` 文件重试
4. 检查网络连接
5. 尝试在非 headless 模式下查看浏览器

### 依赖问题

#### Playwright 浏览器未安装

**症状：**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**解决方案：**
```bash
source .venv/bin/activate
playwright install chromium
```

#### 缺少 Python 依赖

**解决方案：**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

### 运行时问题

#### 书签加载慢或卡住

**解决方案：**
1. 等待页面完全加载（首次较慢）
2. 刷新页面重试
3. 减少加载数量（默认 50 条）

#### 下载失败

**可能原因：**
1. 推文不包含视频
2. 私密推文无法访问
3. 网络超时

**解决方案：**
1. 确认推文包含视频内容
2. 检查网络连接
3. 重试下载

### Docker 问题

#### 容器无法启动

```bash
# 查看日志
docker compose logs web

# 重新构建
docker compose build --no-cache web
```

#### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :10000

# 修改端口
docker compose up web -p 3000:10000
```

#### 权限问题

```bash
# 修改目录权限
chmod -R 755 downloads state
```

#### 网络超时（中国大陆）

**症状：**
```
ERROR: failed to solve: DeadlineExceeded: failed to fetch oauth token
```

**解决方案：**
1. 配置 Docker 镜像加速（见上文）
2. 使用 `./docker-build-cn.sh`
3. 使用 `Dockerfile.cn`

---

## ❓ 常见问题

### Q: Docker 镜像为什么这么大（800MB）？

A: 镜像包含了 Chromium 浏览器，这是必需的，因为：
- 项目使用 Playwright 自动化浏览器登录 Twitter
- 需要浏览器来抓取动态加载的书签内容
- 需要执行 JavaScript 来滚动页面获取所有书签

**注意：** 项目已从 Firefox 切换到 Chromium，镜像大小从 1.5GB 减少到 800MB（减少 40%）。

### Q: 可以不用浏览器吗？

A: 可以，但需要重写代码使用 Twitter API。这需要：
- 申请 Twitter Developer 账号和 API 密钥
- 重写登录和抓取逻辑
- 如果你愿意做这些工作，镜像可以减小到 ~200MB

### Q: 为什么从 Firefox 切换到 Chromium？

A: Chromium 的优势：
- 镜像大小减少 40%（从 1.5GB 到 800MB）
- 构建时间减少约 50%
- 内存占用减少约 17%
- 启动速度提升约 25%
- 系统依赖更少

### Q: Web 界面登录失败怎么办？

A: 检查用户名密码是否正确，如果账号有邮箱验证，请填写邮箱字段。删除 `storage_state.json` 文件重试。

### Q: 为什么有些书签没有显示？

A: Web 界面只显示包含视频或图片的书签，纯文本推文会被过滤。

### Q: 下载的文件保存在哪里？

A: 默认保存在项目根目录的 `downloads` 文件夹，可通过环境变量 `DOWNLOAD_DIR` 修改。

### Q: 可以同时下载多个视频吗？

A: 当前版本是顺序下载，后续版本会支持并发下载。

### Q: 支持下载图片吗？

A: 当前版本主要支持视频下载，图片下载功能正在开发中。

### Q: 如何在服务器上部署？

A: 推荐使用 Docker 部署：
```bash
docker compose up -d web
```

### Q: 如何设置定时任务？

A: 使用 cron 或系统定时任务：
```bash
# 每天凌晨 2 点运行
0 2 * * * cd /path/to/project && docker compose --profile cli up downloader
```

### Q: 如何备份数据？

A: 备份以下目录：
```bash
tar -czf backup.tar.gz downloads/ state/
```

### Q: 如何更新项目？

A: 拉取最新代码并重新构建：
```bash
git pull
docker compose build --no-cache
docker compose up -d web
```

### Q: 本地运行和 Docker 运行有什么区别？

A: 
- **本地运行**：更灵活，适合开发和调试
- **Docker 运行**：更稳定，适合生产环境和长期运行
- 功能完全一致，选择你喜欢的方式即可

---

## 📝 更新日志

### [未发布] - 2026-04-01

#### 优化 🚀
- 切换到 Chromium 浏览器，Docker 镜像大小从 1.5GB 减少到 800MB（减少 40%）
- 优化 Docker 系统依赖，移除不必要的包（如 wget, ca-certificates, libgtk-3-0）
- 更新所有文档，反映 Chromium 的使用
- 整合所有文档到 README，简化维护

#### 变更 🔧
- 将 `playwright.firefox` 改为 `playwright.chromium`（`web_app.py`, `cli.py`）
- 更新 `Dockerfile` 和 `Dockerfile.cn` 使用 Chromium
- 简化系统依赖列表，只保留 Chromium 必需的库
- 删除 docs 目录，所有文档合并到 README

### [0.2.0] - 2026-04-01

#### 新增功能 🎉

**Web 应用界面**
- ✨ 全新的 Web 界面 (`web_app.py`)
  - 可视化登录表单，无需配置环境变量
  - 卡片式书签浏览，支持缩略图预览
  - 多选/全选下载功能
  - 实时下载进度显示
  - 响应式设计，支持移动端

**命令行增强**
- 🚀 新增 `serve-web` 命令启动 Web 应用
- 📝 改进配置管理，Web 模式下可选环境变量

**Docker 支持**
- 🐳 完整的 Docker 支持
  - 优化的 Dockerfile
  - docker-compose 配置
  - 自动化构建脚本
  - 中国大陆优化版本

**文档完善**
- 📚 完善的文档系统
  - 详细使用指南
  - Docker 部署指南
  - 故障排除指南
  - 中国大陆部署指南

#### 改进优化 ⚡

**用户体验**
- 💡 简化启动流程，一键启动 Web 应用
- 🎨 美化界面设计，采用 Twitter 配色方案
- 📊 实时状态反馈，清晰的成功/失败提示

**技术架构**
- 🔄 采用 FastAPI 异步架构
- 🎭 使用 Playwright 异步 API
- 📦 后台任务处理下载队列
- 💾 自动保存登录状态

### [0.1.0] - 初始版本

#### 核心功能
- ✅ 自动登录 Twitter/X
- ✅ 抓取书签推文
- ✅ 下载视频内容
- ✅ 历史记录管理
- ✅ 监控模式
- ✅ 仪表盘查看
- ✅ Docker 支持

---

## 📁 项目结构

```
twitter-bookmarks-downloader/
├── src/twitter_bookmarks_downloader/
│   ├── __init__.py
│   ├── web_app.py          # Web 应用
│   ├── cli.py              # 命令行入口
│   ├── config.py           # 配置管理
│   ├── bookmark_scraper.py # 书签抓取
│   ├── downloader.py       # 视频下载
│   ├── login.py            # 登录管理
│   ├── dashboard.py        # 仪表盘
│   └── history.py          # 历史记录
├── downloads/              # 下载的视频（自动创建）
├── state/                  # 应用状态（自动创建）
├── .env.example            # 环境变量模板
├── .gitignore              # Git 忽略文件
├── .dockerignore           # Docker 忽略文件
├── Dockerfile              # Docker 镜像配置（Chromium）
├── Dockerfile.cn           # Docker 镜像配置（国内优化）
├── docker-compose.yml      # Docker 编排配置
├── docker-build.sh         # Docker 构建脚本
├── docker-build-cn.sh      # Docker 构建脚本（国内）
├── docker-test.sh          # Docker 测试脚本
├── Makefile                # Make 命令集合
├── run_web.py              # Web 应用启动脚本
├── start_web.sh            # 一键启动脚本
├── requirements.txt        # Python 依赖
├── pyproject.toml          # 项目配置
└── README.md               # 本文档
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📄 许可证

MIT License

## 🙏 致谢

- [Playwright](https://playwright.dev/) - 浏览器自动化
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - 视频下载
- [FastAPI](https://fastapi.tiangolo.com/) - Web 框架
- [Typer](https://typer.tiangolo.com/) - CLI 框架

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
