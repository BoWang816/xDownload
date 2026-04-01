# 快速开始 - 5 分钟上手

## 🚀 最快方式（推荐）

```bash
# 1. 克隆项目
git clone <your-repo-url>
cd twitter-bookmarks-downloader

# 2. 一键启动
chmod +x start_web.sh
./start_web.sh

# 3. 打开浏览器
# 访问 http://localhost:8000
```

就这么简单！🎉

## 📱 使用流程

### 步骤 1：登录
在网页中输入：
- 用户名
- 密码
- 邮箱（可选）

### 步骤 2：浏览
- 自动加载书签
- 查看缩略图
- 阅读推文内容

### 步骤 3：选择
- 点击卡片选择
- 或点击"全选"
- 查看已选数量

### 步骤 4：下载
- 点击"下载选中"
- 查看实时进度
- 等待完成

### 步骤 5：查看
文件保存在 `downloads` 目录

## 🎯 常用命令

### Web 界面（推荐）
```bash
# 方式 1：使用启动脚本
./start_web.sh

# 方式 2：直接运行
source .venv/bin/activate
python run_web.py

# 方式 3：自定义端口
# 编辑 run_web.py 修改端口号
```

### 命令行下载
```bash
# 下载前 50 条（需要先配置 .env）
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 50

# 下载所有
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 0

# 监控模式
python -m twitter_bookmarks_downloader.cli download-bookmarks --watch
```

### 查看历史
```bash
# 启动仪表盘
python -m twitter_bookmarks_downloader.cli serve-dashboard --port 8080

# 访问 http://localhost:8080
```

## 🔧 环境变量（可选）

创建 `.env` 文件：
```bash
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
DOWNLOAD_DIR=downloads
```

Web 模式下可以不配置，直接在界面输入。

## 🐛 遇到问题？

### 启动失败
如果 `start_web.sh` 失败，使用：
```bash
source .venv/bin/activate
python run_web.py
```

详细故障排除请查看 [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

## 📚 更多帮助

- [完整使用指南](USAGE_GUIDE.md)
- [功能特性](FEATURES.md)
- [更新日志](CHANGELOG.md)

## 💡 小贴士

1. **首次登录**：会保存状态，下次自动登录
2. **分批下载**：建议一次选 10-20 个
3. **刷新书签**：点击刷新加载更多
4. **查看历史**：已下载的会自动跳过

---

开始使用吧！有问题随时查看文档 📖
