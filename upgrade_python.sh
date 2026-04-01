#!/bin/bash

# 升级 Python 到 3.10 的脚本
# 适用于 Ubuntu 20.04

set -e

echo "=========================================="
echo "开始升级 Python 到 3.10"
echo "=========================================="

# 更新包列表
echo "步骤 1: 更新包列表..."
sudo apt update

# 安装必要的依赖
echo "步骤 2: 安装必要的依赖..."
sudo apt install -y software-properties-common

# 添加 deadsnakes PPA
echo "步骤 3: 添加 deadsnakes PPA..."
sudo add-apt-repository -y ppa:deadsnakes/ppa

# 更新包列表
echo "步骤 4: 再次更新包列表..."
sudo apt update

# 安装 Python 3.10
echo "步骤 5: 安装 Python 3.10..."
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils

# 安装 pip for Python 3.10
echo "步骤 6: 安装 pip for Python 3.10..."
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10

# 验证安装
echo ""
echo "=========================================="
echo "验证安装结果："
echo "=========================================="
python3.10 --version
python3.10 -m pip --version

echo ""
echo "=========================================="
echo "✓ Python 3.10 安装完成！"
echo "=========================================="
echo ""
echo "接下来的步骤："
echo "1. 创建新的虚拟环境："
echo "   python3.10 -m venv .venv"
echo ""
echo "2. 激活虚拟环境："
echo "   source .venv/bin/activate"
echo ""
echo "3. 安装依赖："
echo "   pip install -r requirements.txt"
echo ""
echo "4. 运行应用："
echo "   python run_web.py"
echo "=========================================="
