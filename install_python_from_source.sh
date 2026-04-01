#!/bin/bash

# 从源码编译安装 Python 3.10
# 适用于 Ubuntu 20.04

set -e

PYTHON_VERSION="3.10.13"

echo "=========================================="
echo "从源码编译安装 Python ${PYTHON_VERSION}"
echo "=========================================="
echo "注意: 此过程需要 10-15 分钟"
echo ""

# 安装编译依赖
echo "步骤 1: 安装编译依赖..."
sudo apt update
sudo apt install -y build-essential zlib1g-dev libncurses5-dev libgdbm-dev \
    libnss3-dev libssl-dev libreadline-dev libffi-dev libsqlite3-dev \
    wget libbz2-dev liblzma-dev

# 下载 Python 源码
echo ""
echo "步骤 2: 下载 Python ${PYTHON_VERSION} 源码..."
cd /tmp
if [ ! -f "Python-${PYTHON_VERSION}.tgz" ]; then
    wget https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz
fi

# 解压
echo ""
echo "步骤 3: 解压源码..."
tar -xf Python-${PYTHON_VERSION}.tgz
cd Python-${PYTHON_VERSION}

# 配置
echo ""
echo "步骤 4: 配置编译选项..."
./configure --enable-optimizations --with-ensurepip=install

# 编译（使用多核加速）
echo ""
echo "步骤 5: 编译 Python（这可能需要 10-15 分钟）..."
make -j $(nproc)

# 安装
echo ""
echo "步骤 6: 安装 Python..."
sudo make altinstall

# 清理
echo ""
echo "步骤 7: 清理临时文件..."
cd /tmp
rm -rf Python-${PYTHON_VERSION}
rm -f Python-${PYTHON_VERSION}.tgz

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
echo "1. 删除旧的虚拟环境："
echo "   rm -rf .venv"
echo ""
echo "2. 运行启动脚本："
echo "   ./start_web.sh"
echo "=========================================="
