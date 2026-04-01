# 使用指南

## 🚀 快速上手

### 第一步：安装

```bash
# 克隆项目
git clone <repository-url>
cd twitter-bookmarks-downloader

# 一键启动（推荐）
./start_web.sh
```

### 第二步：登录

1. 浏览器自动打开 `http://localhost:8000`
2. 输入你的 Twitter 用户名和密码
3. 如果账号需要邮箱验证，填写邮箱字段
4. 点击"登录"按钮

### 第三步：浏览书签

登录成功后，系统会自动加载你的书签：
- 每个书签显示为一个卡片
- 卡片包含：缩略图、作者、文本预览
- 右上角标签显示媒体类型（视频/图片）

### 第四步：选择下载

- **单选**：点击卡片或复选框
- **多选**：依次点击多个卡片
- **全选**：点击右上角"全选"按钮
- 下载按钮会显示已选数量

### 第五步：开始下载

1. 点击"下载选中"按钮
2. 查看实时进度条
3. 等待下载完成
4. 文件保存在 `downloads` 目录

## 💡 使用技巧

### 提高下载效率

1. **分批下载**：一次选择 10-20 个，避免超时
2. **刷新书签**：点击"刷新书签"加载更多内容
3. **查看历史**：已下载的内容会自动跳过

### 登录状态管理

- 首次登录成功后，状态保存在 `storage_state.json`
- 下次启动自动登录，无需重新输入密码
- 如需切换账号，删除该文件重新登录

### 文件管理

下载的文件命名格式：
```
作者名_日期_推文ID.mp4
```

例如：
```
elonmusk_20260401_1234567890.mp4
```

## 🔧 高级用法

### 命令行批量下载

适合自动化场景：

```bash
# 下载所有书签
python -m twitter_bookmarks_downloader.cli download-bookmarks

# 限制数量
python -m twitter_bookmarks_downloader.cli download-bookmarks --limit 100

# 监控模式（持续运行）
python -m twitter_bookmarks_downloader.cli download-bookmarks --watch --watch-interval 300
```

### 环境变量配置

创建 `.env` 文件：

```bash
# 账号信息
TWITTER_USERNAME=your_username
TWITTER_PASSWORD=your_password
TWITTER_EMAIL=your_email@example.com

# 下载配置
DOWNLOAD_DIR=~/Videos/Twitter
BOOKMARK_LIMIT=0
SKIP_EXISTING=true

# 监控模式
WATCH_MODE=false
WATCH_INTERVAL=120
```

### Docker 部署

```bash
# 构建镜像
docker build -t twitter-bookmarks .

# 运行 Web 应用
docker run -d \
  -p 8000:8000 \
  -v $(pwd)/downloads:/app/downloads \
  -v $(pwd)/storage_state.json:/app/storage_state.json \
  twitter-bookmarks \
  serve-web --port 8000
```

## 🐛 故障排除

### 登录失败

**问题**：提示"登录失败"
**解决**：
1. 检查用户名密码是否正确
2. 如果有邮箱验证，填写邮箱字段
3. 删除 `storage_state.json` 重试
4. 检查网络连接

### 书签加载慢

**问题**：加载书签很慢或卡住
**解决**：
1. 等待页面完全加载（首次较慢）
2. 刷新页面重试
3. 减少加载数量（默认 50 条）

### 下载失败

**问题**：某些视频下载失败
**解决**：
1. 检查推文是否包含视频
2. 某些私密推文可能无法下载
3. 网络问题导致超时，可重试

### 浏览器未启动

**问题**：Playwright 浏览器未安装
**解决**：
```bash
playwright install firefox
```

## 📚 更多资源

- [功能特性](FEATURES.md) - 详细功能说明
- [README](README.md) - 项目概述
- [Issues](https://github.com/your-repo/issues) - 问题反馈

## 🤝 获取帮助

遇到问题？
1. 查看本指南的故障排除部分
2. 查看项目 Issues
3. 提交新的 Issue 描述问题
