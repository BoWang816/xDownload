#!/bin/bash

# 修复 PPA 添加问题的脚本

echo "=========================================="
echo "修复 deadsnakes PPA"
echo "=========================================="

# 手动添加 PPA 源
echo "步骤 1: 手动添加 PPA 源..."
echo "deb http://ppa.launchpad.net/deadsnakes/ppa/ubuntu focal main" | sudo tee /etc/apt/sources.list.d/deadsnakes-ppa.list
echo "deb-src http://ppa.launchpad.net/deadsnakes/ppa/ubuntu focal main" | sudo tee -a /etc/apt/sources.list.d/deadsnakes-ppa.list

# 添加 GPG 密钥
echo "步骤 2: 添加 GPG 密钥..."
sudo apt-key adv --keyserver keyserver.ubuntu.com --recv-keys F23C5A6CF475977595C89F51BA6932366A755776

# 更新包列表
echo "步骤 3: 更新包列表..."
sudo apt update

# 检查 python3.10 是否可用
echo "步骤 4: 检查 Python 3.10 是否可用..."
if apt-cache show python3.10 &>/dev/null; then
    echo "✓ Python 3.10 包可用"
    
    # 安装 Python 3.10
    echo "步骤 5: 安装 Python 3.10..."
    sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils
    
    # 安装 pip
    echo "步骤 6: 安装 pip..."
    curl -sS https://bootstrap.pypa.io/get-pip.py -o /tmp/get-pip.py
    sudo python3.10 /tmp/get-pip.py
    rm -f /tmp/get-pip.py
    
    # 验证
    echo ""
    echo "=========================================="
    echo "✓ 安装完成！"
    echo "=========================================="
    python3.10 --version
    python3.10 -m pip --version
    
    echo ""
    echo "接下来运行: rm -rf .venv && ./start_web.sh"
else
    echo "✗ Python 3.10 包仍然不可用"
    echo ""
    echo "请检查："
    echo "1. 网络连接是否正常"
    echo "2. 是否可以访问 ppa.launchpad.net"
    echo "3. 尝试使用国内镜像源"
    exit 1
fi
