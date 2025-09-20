# LazyAI Studio Makefile
# LazyGophers 组织 - 让构建和部署更懒人化！

.PHONY: help install dev build clean test deploy frontend-install frontend-dev frontend-build backend-dev backend-install all docker-build docker-up docker-down docker-logs docker-clean docker-restart docker-deploy

# 默认目标
help:
	@echo "🚀 LazyAI Studio - LazyGophers 懒人构建工具"
	@echo ""
	@echo "📦 安装命令:"
	@echo "  install           安装所有依赖（前端+后端）"
	@echo "  backend-install   仅安装后端依赖"
	@echo "  frontend-install  仅安装前端依赖"
	@echo ""
	@echo "🔧 开发命令:"
	@echo "  run                   构建并启动生产服务器"
	@echo "  dev                   启动完整开发环境（前端+后端）"
	@echo "  backend-dev           仅启动后端开发服务器"
	@echo "  backend-dev-optimized ⚡启动高性能优化版本服务器"
	@echo "  frontend-dev          仅启动前端开发服务器"
	@echo ""
	@echo "🏗️  构建命令:"
	@echo "  build            构建前端生产版本"
	@echo "  frontend-build   构建前端静态文件"
	@echo ""
	@echo "🧪 测试命令:"
	@echo "  test             运行所有测试（前端+后端）"
	@echo "  test-fast        运行快速测试（跳过慢速测试）"
	@echo "  test-full        运行完整测试套件（包含集成测试）"
	@echo "  test-backend     运行后端测试"
	@echo "  test-frontend    运行前端测试"
	@echo "  test-coverage    生成测试覆盖率报告"
	@echo "  test-watch       启动测试监听模式"
	@echo ""
	@echo "🚀 部署命令:"
	@echo "  deploy           部署到生产环境"
	@echo ""
	@echo "⚡ 性能优化命令:"
	@echo "  benchmark             运行性能基准测试对比"
	@echo "  benchmark-original    测试原始服务性能"
	@echo "  benchmark-optimized   测试优化服务性能"
	@echo "  benchmark-clean       清理性能测试进程"
	@echo ""
	@echo "🐳 Docker 命令:"
	@echo "  docker-build     构建 Docker 镜像"
	@echo "  docker-up        启动 Docker 容器（低资源消耗配置）"
	@echo "  docker-down      停止 Docker 容器"
	@echo "  docker-restart   重启 Docker 容器"
	@echo "  docker-logs      查看 Docker 容器日志"
	@echo "  docker-clean     清理 Docker 资源"
	@echo "  docker-deploy    一键 Docker 部署（构建+启动）"
	@echo ""
	@echo "📦 GitHub Actions:"
	@echo "  github-check     检查 GitHub Actions 工作流"
	@echo "  github-release   创建新版本发布"
	@echo ""
	@echo "🧹 清理命令:"
	@echo "  clean            清理所有构建文件"
	@echo "  clean-frontend   清理前端构建文件"
	@echo "  clean-backend    清理后端缓存"

# ========== 安装依赖 ==========
install: backend-install frontend-install
	@echo "✅ 所有依赖安装完成！懒人开发环境就绪 🛋️"

backend-install:
	@echo "📦 安装后端依赖..."
	uv sync
	@echo "✅ 后端依赖安装完成"

frontend-install:
	@echo "📦 安装前端依赖..."
	cd frontend && yarn install
	@echo "✅ 前端依赖安装完成"

# ========== 开发环境 ==========
run: build
	@echo "🚀 启动生产服务器..."
	@echo "💡 服务启动后，请查看控制台中的访问地址指引"
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

dev:
	@echo "🚀 启动完整开发环境 (前端 + 后端)..."
	@echo "💡 将并行启动前端开发服务器 (3000端口) 和后端API服务器 (8000端口)"
	@echo "🔗 前端: http://localhost:3000"
	@echo "🔗 后端: http://localhost:8000"
	@echo ""
	@echo "⏱️  启动中，请稍等..."
	$(MAKE) -j2 backend-dev frontend-dev

backend-dev:
	@echo "🚀 启动后端开发服务器..."
	@echo "💡 服务启动后，请查看控制台中的访问地址指引"
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 启动优化版本服务器
backend-dev-optimized:
	@echo "⚡ 启动优化版本后端服务器 (高性能模式)..."
	@echo "💡 使用懒加载、LRU缓存、无文件监控等优化技术"
	@echo "💡 服务启动后，请查看控制台中的访问地址指引"
	uv run uvicorn app.main_optimized:app --reload --host 0.0.0.0 --port 8000

backend-optimized: backend-dev-optimized

frontend-dev:
	@echo "🚀 启动前端开发服务器..."
	@echo "💡 前端将在 http://localhost:3000 启动"
	@echo "🔗 后端 API 代理到 http://localhost:8000"
	cd frontend && yarn start

frontend-dev-yarn:
	@echo "🚀 启动前端开发服务器 (Yarn)..."
	cd frontend && yarn start

# ========== 构建生产版本 ==========
build: frontend-build
	@echo "🏗️ 生产构建完成！准备部署 🚀"

frontend-build:
	@echo "🏗️ 构建前端生产版本..."
	cd frontend && yarn run build
	@echo "✅ 前端构建完成，静态文件位于 frontend/build/"

frontend-build-yarn:
	@echo "🏗️ 构建前端生产版本 (Yarn)..."
	cd frontend && yarn build

# ========== 测试 ==========
test: test-backend test-frontend
	@echo "🎉 所有测试完成！"

test-backend:
	@echo "🧪 运行后端测试..."
	uv run pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing

test-backend-unit:
	@echo "🧪 运行后端单元测试..."
	uv run pytest tests/test_*.py -v -m "not integration and not slow"

test-backend-integration:
	@echo "🧪 运行后端集成测试..."
	uv run pytest tests/test_integration*.py -v -m integration

test-frontend:
	@echo "🧪 运行前端测试..."
	cd frontend && yarn run test:ci

test-frontend-watch:
	@echo "🧪 运行前端测试 (监听模式)..."
	cd frontend && yarn run test:watch

test-frontend-coverage:
	@echo "🧪 运行前端测试 (覆盖率报告)..."
	cd frontend && yarn run test:coverage

# 快速测试 (跳过慢速测试)
test-fast:
	@echo "⚡ 运行快速测试..."
	uv run pytest tests/ -v -m "not slow" --tb=short
	cd frontend && yarn run test:ci

# 完整测试套件 (包含集成和慢速测试)
test-full:
	@echo "🚀 运行完整测试套件..."
	@echo "📊 后端测试 (包含集成测试)..."
	uv run pytest tests/ -v --cov=app --cov-report=html --cov-report=term-missing --cov-fail-under=80
	@echo "📊 前端测试 (包含覆盖率)..."
	cd frontend && yarn run test:coverage
	@echo "🎉 完整测试套件完成！"

# 测试覆盖率报告
test-coverage:
	@echo "📊 生成测试覆盖率报告..."
	uv run pytest tests/ --cov=app --cov-report=html --cov-report=term-missing --cov-report=xml
	cd frontend && yarn run test:coverage
	@echo "📈 覆盖率报告已生成："
	@echo "  - 后端: htmlcov/index.html"
	@echo "  - 前端: frontend/coverage/lcov-report/index.html"

# 监听模式测试
test-watch:
	@echo "👀 启动测试监听模式..."
	uv run pytest tests/ -v --tb=short -f

# ========== 部署 ==========
deploy: build
	@echo "🚀 部署完成！LazyAI Studio 已上线"

# ========== 清理 ==========
clean: clean-frontend clean-backend
	@echo "🧹 清理完成！项目回到初始状态"

clean-frontend:
	@echo "🧹 清理前端构建文件..."
	rm -rf frontend/build
	rm -rf frontend/node_modules/.cache
	@echo "✅ 前端清理完成"

clean-backend:
	@echo "🧹 清理后端缓存..."
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	rm -rf .pytest_cache
	rm -rf logs/*.log
	@echo "✅ 后端清理完成"

# ========== 快捷命令 ==========
# 懒人专用：一条命令启动完整开发环境
all: install build
	@echo "🎉 LazyAI Studio 完整环境准备就绪！"
	@echo "💡 运行 'make backend-dev' 启动服务器"
	@echo "🌐 访问 http://localhost:8000 查看应用"

# 超级懒人命令：全自动启动
lazy: install build backend-dev

# 检查系统环境
check:
	@echo "🔍 检查系统环境..."
	@command -v uv >/dev/null 2>&1 || { echo "❌ uv 未安装，请先安装 uv"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "❌ Node.js 未安装，请先安装 Node.js"; exit 1; }
	@command -v yarn >/dev/null 2>&1 || { echo "❌ yarn 未安装，请先安装 yarn"; exit 1; }
	@echo "✅ 系统环境检查通过"

# 显示项目信息
info:
	@echo "📊 LazyAI Studio 项目信息"
	@echo "=========================="
	@echo "项目名称: LazyAI Studio"
	@echo "组织: LazyGophers"
	@echo "版本: $(shell grep 'version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "后端: FastAPI + Python"
	@echo "前端: React + TypeScript + Ant Design"
	@echo "理念: 让 AI 替你思考，让工具替你工作！"

# 集成测试
test-integration:
	@echo "🧪 运行前后端集成测试..."
	uv run python test_integration.py

# ========== 性能优化相关 ==========
# 运行性能基准测试
benchmark:
	@echo "📊 运行性能基准测试..."
	@echo "💡 比较原始服务 vs 优化服务的性能差异"
	uv run python performance_benchmark.py

# 性能测试 - 原始版本
benchmark-original:
	@echo "📊 测试原始服务性能..."
	@echo "⏱️ 启动原始版本服务器进行性能测试"
	uv run uvicorn app.main:app --host 127.0.0.1 --port 8001 &
	@sleep 3
	@echo "🧪 运行负载测试..."
	@curl -s http://localhost:8001/api/health > /dev/null && echo "✅ 原始服务运行正常"
	@pkill -f "app.main:app" || true

# 性能测试 - 优化版本
benchmark-optimized:
	@echo "⚡ 测试优化服务性能..."
	@echo "⏱️ 启动优化版本服务器进行性能测试"
	uv run uvicorn app.main_optimized:app --host 127.0.0.1 --port 8002 &
	@sleep 3
	@echo "🧪 运行负载测试..."
	@curl -s http://localhost:8002/api/health > /dev/null && echo "✅ 优化服务运行正常"
	@curl -s http://localhost:8002/api/performance | python -m json.tool
	@pkill -f "app.main_optimized:app" || true

# 清理性能测试进程
benchmark-clean:
	@echo "🧹 清理性能测试相关进程..."
	@pkill -f "performance_benchmark" || true
	@pkill -f "app.main" || true
	@pkill -f "app.main_optimized" || true
	@echo "✅ 清理完成"

# ========== Docker 命令 ==========
# 构建 Docker 镜像
docker-build:
	@echo "🐳 构建 Docker 镜像（自动打包前端+后端）..."
	@echo "💡 这将自动构建前端并打包到后端服务中"
	docker build -t lazyai-studio:latest .
	@echo "✅ Docker 镜像构建完成"

# 启动 Docker 容器（低资源消耗配置）
docker-up:
	@echo "🐳 启动 Docker 容器（低资源消耗配置）..."
	@echo "💡 服务将在 http://localhost:8000 启动"
	@echo "⚡ 资源限制: CPU 25%, 内存 128MB"
	docker-compose up
	@echo "✅ Docker 容器已启动"
	@echo "🔗 访问: http://localhost:8000"

# 停止 Docker 容器
docker-down:
	@echo "🐳 停止 Docker 容器..."
	docker-compose down
	@echo "✅ Docker 容器已停止"

# 重启 Docker 容器
docker-restart:
	@echo "🔄 重启 Docker 容器..."
	docker-compose restart
	@echo "✅ Docker 容器已重启"

# 查看 Docker 容器日志
docker-logs:
	@echo "📋 查看 Docker 容器日志..."
	docker-compose logs -f

# 清理 Docker 资源
docker-clean:
	@echo "🧹 清理 Docker 资源..."
	docker-compose down -v
	docker system prune -f
	@echo "✅ Docker 资源清理完成"

# 一键 Docker 部署（构建+启动）
docker-deploy: docker-build docker-up
	@echo "🚀 Docker 一键部署完成！"
	@echo "🌐 应用已启动: http://localhost:8000"
	@echo "⚡ 资源优化: 最小内存和CPU占用"

# Docker 状态检查
docker-status:
	@echo "📊 Docker 容器状态:"
	docker-compose ps

# ========== GitHub Actions ==========
# 检查 GitHub Actions 工作流
github-check:
	@echo "🔍 检查 GitHub Actions 工作流..."
	@command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI 未安装，请先安装 GitHub CLI"; exit 1; }
	@echo "📋 工作流列表:"
	gh workflow list
	@echo ""
	@echo "📊 最近的工作流运行:"
	gh run list --limit 5

# 创建新版本发布
github-release:
	@echo "🚀 创建新版本发布..."
	@command -v gh >/dev/null 2>&1 || { echo "❌ gh CLI 未安装，请先安装 GitHub CLI"; exit 1; }
	@echo "💡 当前版本: $(shell grep 'version = ' pyproject.toml | cut -d'"' -f2)"
	@echo "📝 请手动创建发布版本："
	@echo "   gh release create v$(shell grep 'version = ' pyproject.toml | cut -d'"' -f2) --generate-notes"

# ========== 额外命令 ==========
# 显示版本信息
version:
	@echo "LazyAI Studio $(shell grep 'version = ' pyproject.toml | cut -d'"' -f2)"