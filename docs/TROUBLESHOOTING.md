# 故障排除指南

本文档提供常见问题的解决方案。大部分内容已整合到 [主 README](../README.md#故障排除)。

## 快速链接

- [启动问题](#启动问题)
- [登录问题](#登录问题)
- [依赖问题](#依赖问题)
- [运行时问题](#运行时问题)
- [Docker 问题](#docker-问题)

---

## 启动问题

### start_web.sh 失败

**症状：**
```
TypeError: Secondary flag is not valid for non-boolean flag.
```

**原因：** Typer 0.12.5 版本的已知 bug

**解决方案：**

```bash
# 方式 1：使用更新后的启动脚本
./start_web.sh

# 方式 2：直接运行 Python 脚本
source .venv/bin/activate
python run_web.py

# 方式 3：手动启动
source .venv/bin/activate
python -c "
import uvicorn
import sys
sys.path.insert(0, 'src')
from twitter_bookmarks_downloader.config import Settings
from twitter_bookmarks_downloader.web_app import create_web_app
settings = Settings.from_env()
app = create_web_app(settings)
uvicorn.run(app, host='0.0.0.0', port=8000)
"
```

---

## 登录问题

### 登录失败

**可能原因：**
1. 用户名或密码错误
2. 账号需要邮箱验证
3. 网络连接问题
4. Twitter 安全检查

**解决方案：**
1. 检查用户名密码是否正确
2. 如果有邮箱验证，填写邮箱字段
3. 删除 `storage_state.json` 文件重试
4. 检查网络连接
5. 尝试在非 headless 模式下查看浏览器

---

## 依赖问题

### Playwright 浏览器未安装

**症状：**
```
playwright._impl._api_types.Error: Executable doesn't exist
```

**解决方案：**
```bash
source .venv/bin/activate
playwright install firefox
```

### 缺少 Python 依赖

**解决方案：**
```bash
source .venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

---

## 运行时问题

### 书签加载慢或卡住

**解决方案：**
1. 等待页面完全加载（首次较慢）
2. 刷新页面重试
3. 减少加载数量（默认 50 条）

### 下载失败

**可能原因：**
1. 推文不包含视频
2. 私密推文无法访问
3. 网络超时

**解决方案：**
1. 确认推文包含视频内容
2. 检查网络连接
3. 重试下载

---

## Docker 问题

### 容器无法启动

```bash
# 查看日志
docker compose logs web

# 重新构建
docker compose build --no-cache web
```

### 端口被占用

```bash
# 查找占用端口的进程
lsof -i :8000

# 修改端口
docker compose up web -p 3000:8000
```

### 权限问题

```bash
# 修改目录权限
chmod -R 755 downloads state
```

---

## 常用命令

```bash
# 查看 Python 版本
python3 --version

# 查看已安装的包
pip list

# 重新安装依赖
pip install -r requirements.txt --force-reinstall

# 清除 Python 缓存
find . -type d -name "__pycache__" -exec rm -r {} +
find . -type f -name "*.pyc" -delete

# 重新安装 Playwright
playwright install --force firefox
```

---

## 获取帮助

如果以上方法都无法解决问题：

1. 查看完整错误日志
2. 检查 [GitHub Issues](https://github.com/your-repo/issues)
3. 提交新的 Issue 并附上：
   - 错误信息
   - 操作步骤
   - 系统环境
   - Python 版本

---

**返回 [主文档](../README.md)**
