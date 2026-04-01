#!/bin/bash
# Docker 构建脚本

set -e

echo "🐳 开始构建 Twitter 书签下载器 Docker 镜像..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 镜像名称和标签
IMAGE_NAME="twitter-bookmarks"
IMAGE_TAG="${1:-latest}"
FULL_IMAGE_NAME="${IMAGE_NAME}:${IMAGE_TAG}"

echo -e "${BLUE}镜像名称:${NC} ${FULL_IMAGE_NAME}"
echo ""

# 构建镜像
echo -e "${YELLOW}步骤 1/3:${NC} 构建 Docker 镜像..."
docker build -t "${FULL_IMAGE_NAME}" .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}✓ 镜像构建成功！${NC}"
else
    echo -e "${RED}✗ 镜像构建失败${NC}"
    exit 1
fi

echo ""

# 显示镜像信息
echo -e "${YELLOW}步骤 2/3:${NC} 镜像信息"
docker images "${IMAGE_NAME}" | grep "${IMAGE_TAG}"

echo ""

# 测试镜像
echo -e "${YELLOW}步骤 3/3:${NC} 测试镜像..."
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
echo "  docker run -d -p 10000:10000 -v \$(pwd)/downloads:/app/downloads ${FULL_IMAGE_NAME}"
echo ""
echo "  # 查看完整文档"
echo "  cat DOCKER.md"
echo ""
