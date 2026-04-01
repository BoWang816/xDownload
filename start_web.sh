#!/bin/bash
# 启动 Twitter 书签下载器 Web 应用

set -e

echo "=========================================="
echo "启动 Twitter 书签下载器 Web 应用"
echo "=========================================="

# 检测 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        PYTHON_CMD="python3"
        echo "✓ 使用 Python $PYTHON_VERSION"
    else
        echo "✗ 错误: 需要 Python 3.8 或更高版本"
        echo "当前版本: Python $PYTHON_VERSION"
        echo ""
        echo "请升级 Python 到 3.8 或更高版本"
        exit 1
    fi
elif command -v python &> /dev/null; then
    PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d. -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d. -f2)
    
    if [ "$PYTHON_MAJOR" -ge 3 ] && [ "$PYTHON_MINOR" -ge 8 ]; then
        PYTHON_CMD="python"
        echo "✓ 使用 Python $PYTHON_VERSION"
    else
        echo "✗ 错误: 需要 Python 3.8 或更高版本"
        echo "当前版本: Python $PYTHON_VERSION"
        echo ""
        echo "请升级 Python 到 3.8 或更高版本"
        exit 1
    fi
else
    echo "✗ 错误: 未找到 Python"
    exit 1
fi

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo ""
    echo "未找到虚拟环境，正在创建..."
    $PYTHON_CMD -m venv .venv
    echo "✓ 虚拟环境创建完成"
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source .venv/bin/activate

# 检查是否需要安装依赖
if [ ! -f ".venv/installed" ]; then
    echo ""
    echo "正在安装依赖..."
    pip install --upgrade pip
    pip install -r requirements.txt
    touch .venv/installed
    echo "✓ 依赖安装完成"
fi

# 创建必要的目录
mkdir -p downloads
mkdir -p .twitter_state

echo ""
echo "=========================================="
echo "✓ 启动应用..."
echo "=========================================="
echo ""

# 启动应用
$PYTHON_CMD run_web.py
