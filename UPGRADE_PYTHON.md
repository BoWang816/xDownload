# Python 升级指南

## 问题说明

`twitter-api-client` 库要求 Python >= 3.10.10，但 Ubuntu 20.04 默认使用 Python 3.8.10。

## 升级步骤

### 1. 在服务器上拉取最新代码

```bash
cd /path/to/xDownload
git pull origin master
```

### 2. 运行升级脚本

```bash
chmod +x upgrade_python.sh
./upgrade_python.sh
```

升级脚本会自动完成以下操作：
- 添加 deadsnakes PPA 源
- 安装 Python 3.10
- 安装 pip for Python 3.10
- 验证安装结果

### 3. 删除旧的虚拟环境

```bash
rm -rf .venv
rm -f .venv/installed
```

### 4. 启动应用

```bash
./start_web.sh
```

启动脚本会自动：
- 检测 Python 版本（需要 >= 3.10）
- 创建新的虚拟环境（使用 Python 3.10）
- 安装所有依赖
- 启动 Web 应用

## 验证安装

检查 Python 版本：

```bash
python3.10 --version
# 应该输出: Python 3.10.x
```

检查 pip 版本：

```bash
python3.10 -m pip --version
# 应该输出: pip x.x.x from ... (python 3.10)
```

## 手动升级（如果脚本失败）

如果自动升级脚本失败，可以手动执行以下命令：

```bash
# 1. 更新包列表
sudo apt update

# 2. 安装必要的依赖
sudo apt install -y software-properties-common

# 3. 添加 deadsnakes PPA
sudo add-apt-repository -y ppa:deadsnakes/ppa
sudo apt update

# 4. 安装 Python 3.10
sudo apt install -y python3.10 python3.10-venv python3.10-dev python3.10-distutils

# 5. 安装 pip
curl -sS https://bootstrap.pypa.io/get-pip.py | sudo python3.10

# 6. 验证安装
python3.10 --version
python3.10 -m pip --version
```

## 常见问题

### Q: 升级后原来的 Python 3.8 还能用吗？

A: 可以。Python 3.10 是额外安装的，不会影响系统默认的 Python 3.8。两个版本可以共存。

### Q: 如何在不同 Python 版本之间切换？

A: 使用完整的命令名：
- Python 3.8: `python3.8` 或 `python3`
- Python 3.10: `python3.10`

### Q: 虚拟环境需要重新创建吗？

A: 是的。因为 Python 版本变化，需要删除旧的虚拟环境并重新创建。

### Q: 依赖需要重新安装吗？

A: 是的。`start_web.sh` 脚本会自动处理依赖安装。

## 故障排除

### 错误：add-apt-repository: command not found

```bash
sudo apt install -y software-properties-common
```

### 错误：Unable to locate package python3.10

确保已添加 deadsnakes PPA：

```bash
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt update
```

### 错误：pip 安装失败

手动安装 pip：

```bash
curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
sudo python3.10 get-pip.py
rm get-pip.py
```

## 联系支持

如果遇到问题，请提供以下信息：
- 操作系统版本：`cat /etc/os-release`
- Python 版本：`python3 --version` 和 `python3.10 --version`
- 错误日志：完整的错误信息
