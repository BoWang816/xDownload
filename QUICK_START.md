# 快速开始指南

## 🚀 在服务器上部署（Python 3.8+）

### 步骤 1: 拉取最新代码

```bash
cd /path/to/xDownload
git pull origin master
```

### 步骤 2: 清理旧环境

```bash
rm -rf .venv
```

### 步骤 3: 启动应用

```bash
./start_web.sh
```

应用将在 `http://your-server-ip:10000` 上运行。

## ✅ 系统要求

- Python 3.8 或更高版本（无需升级到 3.10）
- Ubuntu 20.04 / Debian / CentOS 等 Linux 系统
- 至少 512MB 内存
- 稳定的网络连接

## 📝 使用说明

### 1. 登录

- 打开浏览器访问 `http://your-server-ip:10000`
- 输入 Twitter 用户名和密码
- 可选：输入邮箱（用于额外验证）
- 勾选"记住用户名和密码"（下次自动填充）

### 2. 获取书签

- 点击"刷新书签"按钮
- 系统会自动获取包含视频的书签

### 3. 下载视频

- 选择想要下载的视频
- 点击"下载选中"按钮
- 查看下载进度

### 4. 查看下载的文件

下载的视频保存在 `downloads/` 目录中。

## 🔧 常用命令

### 查看日志

```bash
# 实时查看日志
tail -f nohup.out
```

### 停止应用

```bash
# 查找进程
ps aux | grep run_web.py

# 停止进程
kill <PID>
```

### 后台运行

```bash
nohup ./start_web.sh > app.log 2>&1 &
```

### 检查应用状态

```bash
curl http://localhost:10000/api/status
```

## 🐛 故障排除

### 问题：Python 版本不对

```bash
python3 --version
# 应该是 3.8 或更高版本
```

### 问题：依赖安装失败

```bash
rm -rf .venv
./start_web.sh
```

### 问题：端口被占用

```bash
# 查找占用端口的进程
lsof -i :10000

# 停止进程
kill <PID>
```

### 问题：登录失败

- 检查用户名和密码是否正确
- 如果需要邮箱验证，请填写邮箱
- 查看日志：`tail -f app.log`

## 📚 更多文档

- [README.md](README.md) - 完整的项目文档

## 💡 提示

1. 首次登录后，cookies 会被保存，下次启动自动登录
2. 下载的视频会自动去重，不会重复下载
3. 支持最多 3 次重试，提高下载成功率
4. 可以同时选择多个视频批量下载

## 🎉 新特性

- ✅ 支持 Python 3.8+（无需升级到 3.10）
- ✅ 使用 twikit 库，更稳定可靠
- ✅ 异步 API，性能更好
- ✅ 简化的登录流程
- ✅ 自动保存和恢复登录状态
