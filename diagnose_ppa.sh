#!/bin/bash

# 诊断 PPA 问题

echo "=========================================="
echo "诊断 PPA 配置"
echo "=========================================="

echo ""
echo "1. 检查 PPA 源文件："
echo "---"
if [ -f /etc/apt/sources.list.d/deadsnakes-ppa.list ]; then
    cat /etc/apt/sources.list.d/deadsnakes-ppa.list
else
    echo "文件不存在"
fi

echo ""
echo "2. 检查所有 deadsnakes 相关源："
echo "---"
grep -r "deadsnakes" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null || echo "未找到"

echo ""
echo "3. 测试网络连接到 PPA 服务器："
echo "---"
ping -c 2 ppa.launchpad.net || echo "无法连接"

echo ""
echo "4. 尝试手动获取包列表："
echo "---"
curl -I http://ppa.launchpad.net/deadsnakes/ppa/ubuntu/dists/focal/main/binary-amd64/Packages.gz 2>&1 | head -5

echo ""
echo "5. 检查 apt 缓存中的 python3.10："
echo "---"
apt-cache search python3.10 | head -10

echo ""
echo "6. 检查系统架构："
echo "---"
dpkg --print-architecture

echo ""
echo "7. 检查 Ubuntu 版本："
echo "---"
lsb_release -a

echo ""
echo "=========================================="
echo "诊断完成"
echo "=========================================="
