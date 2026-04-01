#!/bin/bash
# Docker 构建脚本（中国大陆优化版）

set -e

echo "🐳 开始构建 Twitter 书签下载器 Docker 镜像（中国大陆优化）..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 镜像名称和标签
IMAGE_NAME="twitter-bookmarks"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}镜像名称:${NC} ${FULL_IMAGE_NAME}"
echo ""

# 检查 Docker 是否运行
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}✗ Docker 未运行，请先启动 Docker${NC}"
    exit 1
fi

# 配置国内镜像源
echo -e "${YELLOW}步骤 1/4:${NC} 配置 Docker 镜像加速..."
echo ""
echo "推荐配置以下镜像源之一："
echo "  - 阿里云: https://[your-id].mirror.aliyuncs.com"
echo "  - 腾讯云: https://mirror.ccs.tencentyun.com"
echo "  - 网易云: https://hub-mirror.c.163.com"
echo "  - 中科大: https://docker.mirrors.ustc.edu.cn"
echo ""
echo "配置方法："
echo "  1. Docker Desktop: Settings -> Docker Engine"
echo "  2. 添加以下配置："
echo '     "registry-mirrors": ["https://mirror.ccs.tencentyun.com"]'
echo "  3. 点击 Apply & Restart"
echo ""

read -p "是否已配置镜像加速？(y/n) " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}请先配置镜像加速后再运行此脚本${NC}"
    exit 1
fi

# 构建镜像
echo ""
echo -e "${YELLOW}步骤 2/4:${NC} 构建 Docker 镜像..."
docker build \
    --build-arg HTTP_PROXY=${HTTP_PROXY:-} \
    --build-arg HTTPS_PROXY=${HTTPS_PROXY:-} \
    --network=host \
    -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 镜像构建成功！${NC}"
else
    echo -e "${RED}✗ 镜像构建失败${NC}"
    echo ""
    echo "常见问题："
    echo "  1. 网络超时 - 请配置镜像加速或使用代理"
    echo "  2. 磁盘空间不足 - 清理 Docker 缓存: docker system prune"
    echo "  3. 权限问题 - 确保有 Docker 操作权限"
    exit 1
fi

echo ""

# 显示镜像信息
echo -e "${YELLOW}步骤 3/4:${NC} 镜像信息"
docker images "${IMAGE_NAME}" | grep "${IMAGE_TAG}"

echo ""

# 测试镜像
echo -e "${YELLOW}步骤 4/4:${NC} 测试镜像..."
docker run --rm "${FULL_IMAGE_NAME}" python -c "import sys; sys.path.insert(0, 'src'); from twitter_bookmarks_downloader import web_app; print('✓ 镜像测试通过')"

echo ""
echo -e "${GREEN}🎉 构建完成！${NC}"
echo ""
echo "使用方法："
echo ""
echo "  # 启动 Web 应用"
echo "  docker compose up web"
echo ""
echo "  # 或直接运行"
echo "  docker run -d -p 8000:8000 -v \$(pwd)/downloads:/app/downloads ${FULL_IMAGE_NAME}"
echo ""
