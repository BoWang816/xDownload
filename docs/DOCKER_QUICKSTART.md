# Docker 快速开始

## 🚀 三步启动

```bash
# 1. 构建
docker compose build

# 2. 启动
docker compose up web

# 3. 访问
# 打开浏览器访问 http://localhost:8000
```

## 📋 常用命令

### 构建镜像

```bash
# 使用 docker compose
docker compose build

# 使用构建脚本
./docker-build.sh

# 使用 docker build
docker build -t twitter-bookmarks:latest .
```

### 运行容器

```bash
# Web 应用（前台）
docker compose up web

# Web 应用（后台）
docker compose up -d web

# 命令行下载器
docker compose --profile cli up downloader

# 仪表盘
docker compose --profile dashboard up dashboard
```

### 管理容器

```bash
# 查看运行状态
docker compose ps

# 查看日志
docker compose logs -f web

# 停止服务
docker compose down

# 重启服务
docker compose restart web
```

## 🔧 配置

### 环境变量

创建 `.env` 文件：

```bash
# Web 模式（可选）
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password

# CLI 模式（必填）
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email
```

### 数据持久化

默认挂载目录：
- `./downloads` - 下载的视频
- `./state` - 登录状态和历史

## 🎯 使用场景

### 场景 1：个人使用 Web 界面

```bash
docker compose up -d web
# 访问 http://localhost:8000
```

### 场景 2：服务器批量下载

```bash
# 配置 .env 文件
docker compose --profile cli up -d downloader
```

### 场景 3：监控和管理

```bash
# 启动 Web 应用和仪表盘
docker compose up -d web
docker compose --profile dashboard up -d dashboard
```

## 🌐 端口说明

- `8000` - Web 应用
- `8080` - 仪表盘

修改端口：

```yaml
# docker-compose.yml
services:
  web:
    ports:
      - "3000:8000"  # 改为 3000
```

## 📦 镜像大小优化

当前镜像大小约 1.5GB（包含 Firefox 浏览器）

查看镜像大小：
```bash
docker images twitter-bookmarks
```

## 🔍 故障排除

### 容器无法启动

```bash
# 查看日志
docker compose logs web

# 重新构建
docker compose build --no-cache web
```

### 端口被占用

```bash
# 修改端口
docker compose up web -p 3000:8000
```

### 权限问题

```bash
# 修改目录权限
chmod -R 755 downloads state
```

## 📚 更多信息

- 完整文档：[DOCKER.md](DOCKER.md)
- 故障排除：[TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- 使用指南：[USAGE_GUIDE.md](USAGE_GUIDE.md)

## 💡 小贴士

1. **首次构建**：需要下载 Firefox 浏览器，可能需要几分钟
2. **数据持久化**：确保挂载 `downloads` 和 `state` 目录
3. **资源限制**：建议至少分配 2GB 内存
4. **网络问题**：如果下载慢，可以使用国内镜像源

## 🎉 开始使用

```bash
# 一键启动
docker compose up -d web

# 查看日志
docker compose logs -f web

# 访问应用
open http://localhost:8000
```

就这么简单！🚀
