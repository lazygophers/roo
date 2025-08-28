# Makefile for Roo Project
# 使用 UV 包管理工具

.PHONY: help setup install run run-backend run-frontend build test clean

# 默认目标
help:
	@echo "可用命令:"
	@echo "  setup      - 初始化开发环境"
	@echo "  install    - 安装项目依赖"
	@echo "  run        - 启动应用（前后端）"
	@echo "  run-backend- 仅启动后端服务"
	@echo "  run-frontend - 仅启动前端服务"
	@echo "  build      - 构建应用"
	@echo "  test       - 运行测试"
	@echo "  clean      - 清理构建文件和缓存"

# 初始化开发环境
setup:
	@echo "初始化开发环境..."
	uv sync
	cd app/frontend && yarn install

# 安装依赖
install:
	@echo "安装项目依赖..."
	uv sync
	cd app/frontend && yarn install

# 启动应用（前后端）
run:
	@echo "启动应用（前后端）..."
	@echo "后端服务将在 http://localhost:8000 启动"
	@echo "前端服务将在 http://localhost:5173 启动"
	@echo "按 Ctrl+C 停止服务"
	# 在后台启动后端
	@uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
	# 启动前端
	cd app/frontend && yarn run dev

# 仅启动后端
run-backend:
	@echo "启动后端服务..."
	@echo "访问地址: http://localhost:8000"
	@echo "API文档: http://localhost:8000/docs"
	@uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 仅启动前端
run-frontend:
	@echo "启动前端服务..."
	@echo "访问地址: http://localhost:5173"
	cd app/frontend && yarn run dev

# 构建应用
build:
	@echo "构建应用..."
	@echo "构建前端..."
	cd app/frontend && yarn run build
	@echo "前端构建完成"

# 运行测试
test:
	@echo "运行测试..."
	@echo "运行 Python 测试..."
	uv run pytest tests/ -v
	@echo "运行前端测试..."
	cd app/frontend && yarn test

# 清理构建文件和缓存
clean:
	@echo "清理构建文件和缓存..."
	@echo "清理 Python 缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	@echo "清理前端构建文件..."
	rm -rf app/frontend/dist
	rm -rf app/frontend/node_modules/.vite
	@echo "清理 UV 缓存..."
	uv cache clean
	@echo "清理完成"

# 开发模式快捷命令
dev: run

# 生产环境构建
prod-build: build
	@echo "生产环境构建完成"

# 检查依赖
check:
	@echo "检查依赖..."
	uv pip check
	cd app/frontend && yarn audit

# 更新依赖
update:
	@echo "更新依赖..."
	uv pip update
	cd app/frontend && yarn update