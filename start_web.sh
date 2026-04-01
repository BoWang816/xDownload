#!/bin/bash
# 快速启动 Web 应用

echo "🚀 启动 Twitter 书签下载器 Web 应用..."
echo ""

# 检查虚拟环境
if [ ! -d ".venv" ]; then
    echo "⚠️  未找到虚拟环境，正在创建..."
    python3 -m venv .venv
fi

# 激活虚拟环境
source .venv/bin/activate

# 安装依赖
echo "📦 检查依赖..."
pip install -q -r requirements.txt
pip install -q -e .

# 安装 Playwright 浏览器
echo "🌐 检查 Playwright 浏览器..."
playwright install firefox

echo ""
echo "✅ 准备完成！"
echo ""

# 启动应用（使用简单脚本）
python run_web.py
