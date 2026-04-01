# Docker 中国大陆部署指南

## 🇨🇳 网络问题解决方案

在中国大陆使用 Docker 时，经常会遇到网络连接问题。本文档提供完整的解决方案。

## 🚀 快速解决

### 方式一：使用优化的构建脚本（推荐）

```bash
# 使用中国大陆优化版构建脚本
chmod +x docker-build-cn.sh
./docker-build-cn.sh
```

### 方式二：使用优化的 Dockerfile

```bash
# 使用国内镜像源的 Dockerfile
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .
```

### 方式三：配置镜像加速

配置 Docker 使用国内镜像源后，使用原始构建方式。

## 📋 详细步骤

### 1. 配置 Docker 镜像加速

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

### 2. 验证配置

```bash
# 查看配置
docker info | grep -A 5 "Registry Mirrors"

# 应该看到类似输出：
# Registry Mirrors:
#  https://mirror.ccs.tencentyun.com/
#  https://hub-mirror.c.163.com/
```

### 3. 构建镜像

配置完成后，使用以下任一方式构建：

```bash
# 方式 1：使用优化脚本
./docker-build-cn.sh

# 方式 2：使用优化 Dockerfile
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .

# 方式 3：使用原始方式（需要先配置镜像加速）
docker build -t twitter-bookmarks:latest .
```

## 🌐 推荐的镜像源

### 1. 腾讯云（推荐）
```
https://mirror.ccs.tencentyun.com
```
- 速度快
- 稳定性好
- 无需注册

### 2. 阿里云
```
https://[your-id].mirror.aliyuncs.com
```
- 需要注册阿里云账号
- 获取专属加速地址
- 速度很快

获取方式：
1. 访问 https://cr.console.aliyun.com/
2. 登录后在左侧菜单找到"镜像加速器"
3. 复制你的专属加速地址

### 3. 网易云
```
https://hub-mirror.c.163.com
```
- 无需注册
- 稳定可靠

### 4. 中科大
```
https://docker.mirrors.ustc.edu.cn
```
- 教育网速度快
- 公益服务

## 🔧 其他优化

### 使用代理

如果有代理服务器，可以配置 Docker 使用代理：

#### Docker Desktop

在 Docker Engine 配置中添加：

```json
{
  "proxies": {
    "http-proxy": "http://proxy.example.com:8080",
    "https-proxy": "http://proxy.example.com:8080",
    "no-proxy": "localhost,127.0.0.1"
  }
}
```

#### 构建时使用代理

```bash
docker build \
  --build-arg HTTP_PROXY=http://proxy.example.com:8080 \
  --build-arg HTTPS_PROXY=http://proxy.example.com:8080 \
  -t twitter-bookmarks:latest .
```

### pip 镜像源

Dockerfile.cn 已经配置了清华大学 pip 镜像源：

```dockerfile
RUN pip config set global.index-url https://pypi.tuna.tsinghua.edu.cn/simple
```

其他可用的 pip 镜像源：
- 阿里云：https://mirrors.aliyun.com/pypi/simple/
- 豆瓣：https://pypi.douban.com/simple/
- 中科大：https://pypi.mirrors.ustc.edu.cn/simple/

### apt 镜像源

Dockerfile.cn 已经配置了中科大 apt 镜像源。

## 🐛 常见问题

### 问题 1：连接超时

**症状：**
```
ERROR: failed to solve: DeadlineExceeded: failed to fetch oauth token
```

**解决方案：**
1. 配置 Docker 镜像加速
2. 使用 Dockerfile.cn
3. 使用代理

### 问题 2：下载速度慢

**解决方案：**
1. 尝试不同的镜像源
2. 使用阿里云专属加速地址
3. 检查网络连接

### 问题 3：镜像源不可用

**解决方案：**
1. 尝试其他镜像源
2. 检查镜像源是否在线
3. 更新 Docker 配置

### 问题 4：pip 安装失败

**解决方案：**
```bash
# 使用 Dockerfile.cn，它已配置 pip 镜像源
docker build -f Dockerfile.cn -t twitter-bookmarks:latest .
```

## 📊 性能对比

| 方式 | 下载速度 | 稳定性 | 配置难度 |
|------|---------|--------|---------|
| 直连 Docker Hub | 很慢/超时 | 差 | 简单 |
| 腾讯云镜像 | 快 | 好 | 简单 |
| 阿里云镜像 | 很快 | 很好 | 中等 |
| 代理 | 取决于代理 | 取决于代理 | 复杂 |

## ✅ 验证构建

构建完成后验证：

```bash
# 查看镜像
docker images twitter-bookmarks

# 测试运行
docker run --rm twitter-bookmarks:latest python --version

# 启动应用
docker compose up web
```

## 🎯 推荐方案

### 个人用户
1. 配置腾讯云镜像加速
2. 使用 docker-build-cn.sh 构建

### 企业用户
1. 申请阿里云专属加速地址
2. 配置企业代理
3. 使用 Dockerfile.cn

### 开发者
1. 配置多个镜像源
2. 使用 Dockerfile.cn
3. 本地缓存镜像

## 📚 参考资源

- [Docker 官方文档](https://docs.docker.com/)
- [阿里云镜像加速](https://cr.console.aliyun.com/)
- [腾讯云镜像加速](https://cloud.tencent.com/document/product/1207/45596)
- [清华大学 PyPI 镜像](https://mirrors.tuna.tsinghua.edu.cn/help/pypi/)

## 💡 小贴士

1. **首次构建**：可能需要 10-20 分钟，请耐心等待
2. **网络问题**：如果一次失败，可以多试几次
3. **缓存利用**：Docker 会缓存已下载的层，第二次构建会快很多
4. **磁盘空间**：确保有至少 5GB 可用空间
5. **定期清理**：使用 `docker system prune` 清理无用镜像

---

**返回 [主文档](README.md) | 查看 [Docker 完整指南](docs/DOCKER.md)**
