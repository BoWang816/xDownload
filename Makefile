# Makefile for Twitter Bookmarks Downloader

.PHONY: help install dev test clean docker-build docker-up docker-down docker-test

# 默认目标
help:
	@echo "Twitter 书签下载器 - 可用命令："
	@echo ""
	@echo "  make install       - 安装依赖"
	@echo "  make dev           - 启动开发环境"
	@echo "  make test          - 运行测试"
	@echo "  make clean         - 清理临时文件"
	@echo ""
	@echo "  make docker-build  - 构建 Docker 镜像"
	@echo "  make docker-up     - 启动 Docker 容器"
	@echo "  make docker-down   - 停止 Docker 容器"
	@echo "  make docker-test   - 测试 Docker 镜像"
	@echo ""

# 安装依赖
install:
	@echo "📦 安装依赖..."
	python3 -m venv .venv
	. .venv/bin/activate && pip install -r requirements.txt
	. .venv/bin/activate && pip install -e .
	. .venv/bin/activate && playwright install firefox
	@echo "✅ 安装完成！"

# 启动开发环境
dev:
	@echo "🚀 启动开发环境..."
	. .venv/bin/activate && python run_web.py

# 运行测试
test:
	@echo "🧪 运行测试..."
	. .venv/bin/activate && python -m pytest tests/ -v

# 清理临时文件
clean:
	@echo "🧹 清理临时文件..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf build dist *.egg-info
	@echo "✅ 清理完成！"

# Docker 相关命令
docker-build:
	@echo "🐳 构建 Docker 镜像..."
	./docker-build.sh

docker-up:
	@echo "🚀 启动 Docker 容器..."
	docker compose up -d web
	@echo "✅ 容器已启动！访问 http://localhost:10000"

docker-down:
	@echo "🛑 停止 Docker 容器..."
	docker compose down
	@echo "✅ 容器已停止！"

docker-test:
	@echo "🧪 测试 Docker 镜像..."
	./docker-test.sh

docker-logs:
	@echo "📋 查看 Docker 日志..."
	docker compose logs -f web

docker-shell:
	@echo "🐚 进入 Docker 容器..."
	docker compose exec web bash

# 快速启动
quick-start: install dev

# 完整构建和测试
all: clean install docker-build docker-test
	@echo "🎉 完整构建完成！"
