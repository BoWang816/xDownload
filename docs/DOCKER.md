# Docker 部署指南

## 🐳 快速开始

### 方式一：使用 Web 应用（推荐）

```bash
# 1. 构建镜像
docker compose build

# 2. 启动 Web 应用
docker compose up web

# 3. 访问 http://localhost:8000
```

### 方式二：命令行批量下载

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 填写账号信息

# 2. 启动下载器
docker compose --profile cli up downloader
```

### 方式三：启动仪表盘

```bash
docker compose --profile dashboard up dashboard
# 访问 http://localhost:8080
```

## 📦 构建镜像

### 基础构建

```bash
# 构建镜像
docker compose build

# 或使用 docker build
docker build -t twitter-bookmarks:latest .
```

### 多平台构建

```bash
# 构建支持多平台的镜像
docker buildx build --platform linux/amd64,linux/arm64 -t twitter-bookmarks:latest .
```

## 🚀 运行容器

### Web 应用模式

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

### 使用 docker run

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

## ⚙️ 环境变量配置

创建 `.env` 文件：

```bash
# Twitter 账号（Web 模式可选，CLI 模式必填）
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com

# 下载配置
DOWNLOAD_DIR=/app/downloads
STORAGE_STATE_FILE=/app/state/storage_state.json
HISTORY_FILE=/app/state/download_history.json

# 抓取配置
BOOKMARK_LIMIT=0
SCROLL_TIMEOUT=2.5

# 监控模式
WATCH_MODE=false
WATCH_INTERVAL=120

# 浏览器配置
HEADLESS=true
```

## 📂 数据持久化

### 挂载卷

```yaml
volumes:
  - ./downloads:/app/downloads      # 下载的视频文件
  - ./state:/app/state              # 登录状态和历史记录
```

### 数据目录结构

```
.
├── downloads/                      # 下载的视频
│   └── author_date_id.mp4
└── state/                          # 应用状态
    ├── storage_state.json          # 登录状态
    └── download_history.json       # 下载历史
```

## 🔧 常用命令

### 容器管理

```bash
# 查看运行中的容器
docker compose ps

# 查看日志
docker compose logs -f web

# 重启容器
docker compose restart web

# 停止并删除容器
docker compose down

# 停止并删除容器及数据卷
docker compose down -v
```

### 镜像管理

```bash
# 查看镜像
docker images | grep twitter-bookmarks

# 删除镜像
docker rmi twitter-bookmarks:latest

# 清理未使用的镜像
docker image prune -a
```

### 进入容器

```bash
# 进入运行中的容器
docker compose exec web bash

# 或使用 docker exec
docker exec -it twitter-bookmarks-web bash
```

## 🌐 网络配置

### 自定义端口

修改 `docker-compose.yml`：

```yaml
services:
  web:
    ports:
      - "3000:8000"  # 主机端口:容器端口
```

或使用环境变量：

```bash
# 修改主机端口
docker compose up web -p 3000:8000
```

### 反向代理

使用 Nginx 反向代理：

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

## 🔒 安全建议

### 1. 使用 Docker Secrets

```yaml
services:
  web:
    secrets:
      - twitter_username
      - twitter_password

secrets:
  twitter_username:
    file: ./secrets/username.txt
  twitter_password:
    file: ./secrets/password.txt
```

### 2. 限制资源使用

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

### 3. 只读文件系统

```yaml
services:
  web:
    read_only: true
    tmpfs:
      - /tmp
      - /app/.cache
```

## 📊 监控和日志

### 查看资源使用

```bash
# 查看容器资源使用
docker stats twitter-bookmarks-web

# 查看容器详细信息
docker inspect twitter-bookmarks-web
```

### 日志管理

```bash
# 查看最近 100 行日志
docker compose logs --tail=100 web

# 实时跟踪日志
docker compose logs -f web

# 导出日志
docker compose logs web > logs.txt
```

### 配置日志驱动

```yaml
services:
  web:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## 🚨 故障排除

### 容器无法启动

```bash
# 查看容器日志
docker compose logs web

# 检查容器状态
docker compose ps

# 重新构建镜像
docker compose build --no-cache web
```

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 修改端口映射
docker compose up web -p 3000:8000
```

### 权限问题

```bash
# 修改数据目录权限
chmod -R 755 downloads state

# 或在 Dockerfile 中设置用户
USER 1000:1000
```

### Playwright 浏览器问题

```bash
# 重新安装浏览器
docker compose exec web playwright install firefox

# 或重新构建镜像
docker compose build --no-cache
```

## 🎯 生产环境部署

### 使用 Docker Swarm

```bash
# 初始化 Swarm
docker swarm init

# 部署服务
docker stack deploy -c docker-compose.yml twitter-bookmarks

# 查看服务
docker service ls

# 扩展服务
docker service scale twitter-bookmarks_web=3
```

### 使用 Kubernetes

创建 `k8s-deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: twitter-bookmarks-web
spec:
  replicas: 2
  selector:
    matchLabels:
      app: twitter-bookmarks
  template:
    metadata:
      labels:
        app: twitter-bookmarks
    spec:
      containers:
      - name: web
        image: twitter-bookmarks:latest
        ports:
        - containerPort: 8000
        env:
        - name: DOWNLOAD_DIR
          value: /app/downloads
        volumeMounts:
        - name: downloads
          mountPath: /app/downloads
        - name: state
          mountPath: /app/state
      volumes:
      - name: downloads
        persistentVolumeClaim:
          claimName: downloads-pvc
      - name: state
        persistentVolumeClaim:
          claimName: state-pvc
```

## 📚 更多资源

- [Docker 官方文档](https://docs.docker.com/)
- [Docker Compose 文档](https://docs.docker.com/compose/)
- [Playwright Docker 指南](https://playwright.dev/docs/docker)

## 🤝 获取帮助

遇到问题？

1. 查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
2. 检查容器日志：`docker compose logs web`
3. 提交 Issue 并附上日志信息
