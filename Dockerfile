# 使用 Chromium（比 Firefox 更轻量，镜像约 800MB）
FROM python:3.11-slim

# 环境变量
ENV PIP_NO_CACHE_DIR=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

WORKDIR /app

# 安装系统依赖（Playwright Chromium 需要）
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
      libnss3 libnspr4 libatk1.0-0 libatk-bridge2.0-0 \
      libcups2 libdrm2 libxkbcommon0 libxcomposite1 \
      libxdamage1 libxfixes3 libxrandr2 libgbm1 \
      libpango-1.0-0 libcairo2 libasound2 libatspi2.0-0 \
      fonts-liberation && \
    rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .
COPY pyproject.toml .

# 安装 Python 依赖
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# 安装 Playwright Chromium 浏览器
RUN playwright install chromium --with-deps

# 复制源代码
COPY src ./src
COPY run_web.py .

# 创建数据目录
RUN mkdir -p /app/downloads /app/state

# 暴露端口
EXPOSE 10000

# 默认启动 Web 应用
CMD ["python", "run_web.py"]

