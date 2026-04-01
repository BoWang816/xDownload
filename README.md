# Twitter 书签视频下载器

> 一个功能完整的 Twitter/X 书签视频下载工具，支持 Web 界面、命令行和 Docker 部署

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)

## 📖 目录

- [主要特性](#主要特性)
- [快速开始](#快速开始)
  - [Web 界面](#web-界面推荐)
  - [命令行模式](#命令行模式)
  - [Docker 部署](#docker-部署)
- [详细使用](#详细使用)
  - [安装依赖](#安装依赖)
  - [环境配置](#环境配置)
  - [命令参数](#命令参数)
- [功能说明](#功能说明)
- [Docker 指南](#docker-完整指南)
- [故障排除](#故障排除)
- [项目结构](#项目结构)
- [常见问题](#常见问题)
- [更新日志](#更新日志)

---

## 🌟 主要特性

### 核心功能

- 🌐 **Web 可视化界面**
  - 表单登录，无需配置文件
  - 卡片式浏览书签（带缩略图、作者、文本）
  - 多选/全选下载功能
  - 实时下载进度显示
  - 响应式设计，支持移动端

- 🤖 **命令行批量下载**
  - 自动化批量下载
  - 支持定时任务集成
  - 监控模式持续运行
  - 灵活的参数配置

- 📊 **监控仪表盘**
  - 查看配置信息
  - 下载历史记录
  - API 接口支持

- 🔐 **智能登录**
  - 自动保存登录状态
  - 下次免登录
  - 支持邮箱验证

- 📥 **可靠下载**
  - 基于 yt-dlp
  - 支持重试和断点续传
  - 历史记录去重
  - 自动跳过已下载

- 🐳 **Docker 支持**
  - 一键容器化部署
  - 多种运行模式
  - 数据持久化
  - 生产环境就绪

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

# 3. 打开浏览器
# 访问 http://localhost:8000
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
playwright install firefox

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 填写账号信息

# 3. 运行下载
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 50

# 4. 监控模式（持续运行）
python -m twitter_bookmarks_downloader.cli download-bookmarks --watch
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

**🇨🇳 中国大陆用户：**

如果遇到网络问题，使用优化版本：

```bash
# 使用中国大陆优化的构建脚本
./docker-build-cn.sh

# 或使用优化的 Dockerfile
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .
```

详细说明请查看 [中国大陆部署指南](DOCKER_CN.md)

**访问应用：**
- Web 应用：http://localhost:8000
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
playwright install firefox
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
- `--port INTEGER` - 监听端口（默认：8000）

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

#### 仪表盘

```bash
python -m twitter_bookmarks_downloader.cli serve-dashboard [OPTIONS]
```

**选项：**
- `--host TEXT` - 监听地址（默认：0.0.0.0）
- `--port INTEGER` - 监听端口（默认：8080）

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

### 仪表盘功能

- 查看当前配置
- 下载历史列表
- 统计信息
- API 接口

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

#### 🇨🇳 中国大陆用户

如果遇到网络超时问题：

```bash
# 方式 1：使用优化脚本（推荐）
./docker-build-cn.sh

# 方式 2：使用优化 Dockerfile
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .

# 方式 3：配置镜像加速后使用原始方式
# 详见 DOCKER_CN.md
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

#### 使用 docker run

```bash
# 运行 Web 应用
docker run -d \
  --name twitter-bookmarks-web \
  -p 8000:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/state:/app/state \
  twitter-bookmarks:latest

# 运行命令行下载器
docker run -d \
  --name twitter-bookmarks-cli \
  -e TWITTER_USERNAME=your_username \
  -e TWITTER_PASSWORD=your_password \
  -e TWITTER_EMAIL=your_email \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/state:/app/state \
  twitter-bookmarks:latest \
  python -m twitter_bookmarks_downloader.cli download-bookmarks
```

### 环境变量配置

Docker 环境变量配置：

```yaml
# docker-compose.yml 或 .env 文件
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email
DOWNLOAD_DIR=/app/downloads
STORAGE_STATE_FILE=/app/state/storage_state.json
HISTORY_FILE=/app/state/download_history.json
BOOKMARK_LIMIT=0
SCROLL_TIMEOUT=2.5
WATCH_MODE=false
WATCH_INTERVAL=120
HEADLESS=true
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

### 网络配置

#### 自定义端口

```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "3000:8000"  # 主机端口:容器端口
```

#### 反向代理（Nginx）

```nginx
server {
    listen 80;
    server_name bookmarks.example.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 安全建议

#### 1. 使用环境变量

```bash
# 不要在镜像中硬编码密码
docker run -e TWITTER_USERNAME=xxx -e TWITTER_PASSWORD=yyy ...
```

#### 2. 限制资源使用

```yaml
services:
  web:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

#### 3. 使用非 root 用户

```dockerfile
# 在 Dockerfile 中添加
RUN useradd -m -u 1000 appuser
USER appuser
```

### 镜像信息

- **基础镜像**: python:3.11-slim
- **镜像大小**: ~1.5GB（包含 Firefox 浏览器）
- **暴露端口**: 8000（Web）、8080（仪表盘）
- **工作目录**: /app
- **数据卷**: /app/downloads、/app/state

---

## 🔧 故障排除

### 启动问题

#### start_web.sh 失败

**症状：**
```
TypeError: Secondary flag is not valid for non-boolean flag.
```

**解决方案：**

使用 `run_web.py` 脚本：

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
playwright install firefox
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
lsof -i :8000

# 修改端口
docker compose up web -p 3000:8000
```

#### 权限问题

```bash
# 修改目录权限
chmod -R 755 downloads state
```

### 常用命令

```bash
# 查看 Python 版本
python3 --version

# 查看已安装的包
pip list

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清除 Python 缓存
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 重新安装 Playwright
playwright install --force firefox
```

---

## 📁 项目结构

```
twitter-bookmarks-downloader/
├── src/twitter_bookmarks_downloader/
│   ├── __init__.py
│   ├── web_app.py          # Web 应用（新增）
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
├── .dockerignore           # Docker 忽略文件
├── Dockerfile              # Docker 镜像配置
├── docker-compose.yml      # Docker 编排配置
├── docker-build.sh         # Docker 构建脚本
├── docker-test.sh          # Docker 测试脚本
├── Makefile                # Make 命令集合
├── run_web.py              # Web 应用启动脚本
├── start_web.sh            # 一键启动脚本
├── requirements.txt        # Python 依赖
├── pyproject.toml          # 项目配置
└── README.md               # 本文档
```

---

## ❓ 常见问题

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

---

## 📝 更新日志

### [0.2.0] - 2026-04-01

#### 新增功能
- ✨ 全新的 Web 界面
  - 可视化登录表单
  - 卡片式书签浏览
  - 多选/全选下载
  - 实时进度显示
- 🐳 完整的 Docker 支持
  - 优化的 Dockerfile
  - docker-compose 配置
  - 自动化构建脚本
- 📚 完善的文档
  - 整合所有文档到 README
  - Docker 部署指南
  - 故障排除指南

#### 改进优化
- 💡 简化启动流程
- 🎨 美化界面设计
- 📊 实时状态反馈
- 🔄 异步架构优化

### [0.1.0] - 初始版本

#### 核心功能
- ✅ 自动登录 Twitter/X
- ✅ 抓取书签推文
- ✅ 下载视频内容
- ✅ 历史记录管理
- ✅ 监控模式
- ✅ 仪表盘查看

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

## 📞 联系方式

- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)
- 邮箱: your-email@example.com

---

**⭐ 如果这个项目对你有帮助，请给个 Star！**
