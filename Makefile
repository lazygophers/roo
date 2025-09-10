# LazyAI Studio Makefile
# LazyGophers 组织 - 让构建和部署更懒人化！

.PHONY: help install dev build clean test deploy frontend-install frontend-dev frontend-build backend-dev backend-install all

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
	@echo "  run              构建并启动生产服务器"
	@echo "  dev              启动完整开发环境（前端+后端）"
	@echo "  backend-dev      仅启动后端开发服务器"
	@echo "  frontend-dev     仅启动前端开发服务器"
	@echo ""
	@echo "🏗️  构建命令:"
	@echo "  build            构建前端生产版本"
	@echo "  frontend-build   构建前端静态文件"
	@echo ""
	@echo "🧪 测试命令:"
	@echo "  test             运行所有测试"
	@echo "  test-backend     运行后端测试"
	@echo "  test-frontend    运行前端测试"
	@echo ""
	@echo "🚀 部署命令:"
	@echo "  deploy           部署到生产环境"
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
	cd frontend && npm install
	@echo "✅ 前端依赖安装完成"

# ========== 开发环境 ==========
run: build
	@echo "🚀 启动生产服务器..."
	@echo "💡 服务启动后，请查看控制台中的访问地址指引"
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8000

dev: backend-dev

backend-dev:
	@echo "🚀 启动后端开发服务器 (集成前端)..."
	@echo "💡 服务启动后，请查看控制台中的访问地址指引"
	uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

frontend-dev:
	@echo "🚀 启动前端开发服务器..."
	@echo "💡 前端将在 http://localhost:3000 启动"
	@echo "🔗 后端 API 代理到 http://localhost:8000"
	cd frontend && npm start

frontend-dev-yarn:
	@echo "🚀 启动前端开发服务器 (Yarn)..."
	cd frontend && yarn start

# ========== 构建生产版本 ==========
build: frontend-build
	@echo "🏗️ 生产构建完成！准备部署 🚀"

frontend-build:
	@echo "🏗️ 构建前端生产版本..."
	cd frontend && npm run build
	@echo "✅ 前端构建完成，静态文件位于 frontend/build/"

frontend-build-yarn:
	@echo "🏗️ 构建前端生产版本 (Yarn)..."
	cd frontend && yarn build

# ========== 测试 ==========
test: test-backend

test-backend:
	@echo "🧪 运行后端测试..."
	uv run pytest tests/ -v

test-frontend:
	@echo "🧪 运行前端测试..."
	cd frontend && npm test -- --coverage --ci --watchAll=false

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
	@command -v npm >/dev/null 2>&1 || { echo "❌ npm 未安装，请先安装 npm"; exit 1; }
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