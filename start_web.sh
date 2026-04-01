#!/bin/bash
# 快速启动 Web 应用

echo "🚀 启动 Twitter 书签下载器 Web 应用..."
echo ""

# 检查 Python 命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD=python3
elif command -v python &> /dev/null; then
    PYTHON_CMD=python
else
    echo "❌ 错误：未找到 Python 解释器"
    echo "请安装 Python 3.11 或更高版本"
    exit 1
fi

echo "✓ 使用 Python: $PYTHON_CMD"

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    $PYTHON_CMD -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt
pip install -q -e .

# 安装 Playwright 浏览器
echo "🌐 检查 Playwright 浏览器..."
playwright install chromium

echo ""
echo "✅ 准备完成！"
echo ""

# 启动应用（使用简单脚本）
$PYTHON_CMD run_web.py
