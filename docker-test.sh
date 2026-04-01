#!/bin/bash
# Docker 测试脚本

set -e

echo "🧪 测试 Docker 镜像..."
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

IMAGE_NAME="twitter-bookmarks:latest"

# 测试 1: 检查镜像是否存在
echo -e "${YELLOW}测试 1:${NC} 检查镜像是否存在..."
if docker images | grep -q "twitter-bookmarks"; then
    echo -e "${GREEN}✓ 镜像存在${NC}"
else
    echo -e "${RED}✗ 镜像不存在，请先运行 docker-build.sh${NC}"
    exit 1
fi

# 测试 2: 检查 Python 环境
echo -e "${YELLOW}测试 2:${NC} 检查 Python 环境..."
docker run --rm "${IMAGE_NAME}" python --version
echo -e "${GREEN}✓ Python 环境正常${NC}"

# 测试 3: 检查依赖包
echo -e "${YELLOW}测试 3:${NC} 检查依赖包..."
docker run --rm "${IMAGE_NAME}" python -c "
import playwright
import fastapi
import yt_dlp
print('✓ 所有依赖包已安装')
"
echo -e "${GREEN}✓ 依赖包正常${NC}"

# 测试 4: 检查源代码
echo -e "${YELLOW}测试 4:${NC} 检查源代码..."
docker run --rm "${IMAGE_NAME}" python -c "
import sys
sys.path.insert(0, 'src')
from twitter_bookmarks_downloader import web_app
from twitter_bookmarks_downloader import config
print('✓ 源代码导入成功')
"
echo -e "${GREEN}✓ 源代码正常${NC}"

# 测试 5: 检查 Playwright 浏览器
echo -e "${YELLOW}测试 5:${NC} 检查 Playwright 浏览器..."
docker run --rm "${IMAGE_NAME}" playwright --version
echo -e "${GREEN}✓ Playwright 已安装${NC}"

# 测试 6: 检查数据目录
echo -e "${YELLOW}测试 6:${NC} 检查数据目录..."
docker run --rm "${IMAGE_NAME}" ls -la /app/downloads /app/state
echo -e "${GREEN}✓ 数据目录已创建${NC}"

echo ""
echo -e "${GREEN}🎉 所有测试通过！${NC}"
echo ""
echo "可以开始使用了："
echo "  docker compose up web"
echo ""
