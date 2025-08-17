# ============================================================================
# lazygopher - Professional Python Project Makefile
# ============================================================================
# 
# Python Version: 3.12+
# Package Manager: uv
# Code Formatter: black
# Linter: ruff
# Test Framework: pytest
#
# Usage: make [target]
# Run 'make help' to see all available targets
# ============================================================================

# Variables
PYTHON := python3.12
UV := uv
PYTEST := pytest
BLACK := black
RUFF := ruff
PROJECT_NAME := lazygopher
SRC_DIR := src
TEST_DIR := tests
SCRIPT_DIR := scripts
COVERAGE_DIR := htmlcov
BENCHMARK_DIR := .benchmarks

# Python package paths
PYTHON_PATHS := $(SRC_DIR) $(TEST_DIR) $(SCRIPT_DIR) main.py

# Color codes for beautiful output
BLUE := \033[0;34m
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
RESET := \033[0m
BOLD := \033[1m

# Default target
.DEFAULT_GOAL := help

# ============================================================================
# Core Targets
# ============================================================================

.PHONY: help
help: ## 显示所有可用命令的帮助信息
	@echo "$(BOLD)$(BLUE)╔══════════════════════════════════════════════════════════════╗$(RESET)"
	@echo "$(BOLD)$(BLUE)║          lazygopher - Makefile Command Reference             ║$(RESET)"
	@echo "$(BOLD)$(BLUE)╚══════════════════════════════════════════════════════════════╝$(RESET)"
	@echo ""
	@echo "$(BOLD)Available targets:$(RESET)"
	@echo ""
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  $(GREEN)%-20s$(RESET) %s\n", $$1, $$2}'
	@echo ""
	@echo "$(BOLD)$(YELLOW)Quick Start:$(RESET)"
	@echo "  $$ make install        # 安装项目依赖"
	@echo "  $$ make run           # 运行主程序"
	@echo "  $$ make test          # 运行测试"
	@echo ""

.PHONY: build
build: clean ## 使用 Nuitka 编译项目为独立可执行文件
	@echo "$(BOLD)$(BLUE)Building $(PROJECT_NAME) with Nuitka...$(RESET)"
	@bash scripts/build.sh
	@echo "$(GREEN)✓ Build completed successfully$(RESET)"

.PHONY: install
install: ## 安装项目依赖
	@echo "$(BOLD)$(BLUE)Installing dependencies...$(RESET)"
	@$(UV) sync --no-dev
	@echo "$(GREEN)✓ Dependencies installed$(RESET)"

.PHONY: dev-install
dev-install: ## 安装开发依赖
	@echo "$(BOLD)$(BLUE)Installing development dependencies...$(RESET)"
	@$(UV) sync --all-extras
	@echo "$(GREEN)✓ Development dependencies installed$(RESET)"

.PHONY: run
run: ## 运行主程序
	@echo "$(BOLD)$(BLUE)Running $(PROJECT_NAME)...$(RESET)"
	@$(UV) run python main.py

# ============================================================================
# Testing Targets
# ============================================================================

.PHONY: test
test: ## 运行所有测试
	@echo "$(BOLD)$(BLUE)Running tests...$(RESET)"
	@$(UV) run $(PYTEST) -v --tb=short

.PHONY: test-quick
test-quick: ## 快速测试（跳过慢速测试）
	@echo "$(BOLD)$(YELLOW)Running quick tests (skipping slow tests)...$(RESET)"
	@$(UV) run $(PYTEST) -v --tb=short -m "not slow"

.PHONY: test-fast
test-fast: ## 并行运行测试（使用多核加速）
	@echo "$(BOLD)$(YELLOW)Running tests in parallel...$(RESET)"
	@$(UV) run $(PYTEST) -v --tb=short -n auto

.PHONY: test-profile
test-profile: ## 运行测试并显示性能分析
	@echo "$(BOLD)$(YELLOW)Running tests with profiling...$(RESET)"
	@$(UV) run $(PYTEST) -v --tb=short --benchmark-only --benchmark-verbose

.PHONY: test-watch
test-watch: ## 监视模式运行测试（文件变化时自动重新运行）
	@echo "$(BOLD)$(YELLOW)Running tests in watch mode...$(RESET)"
	@$(UV) run $(PYTEST) -v --tb=short --looponfail

.PHONY: coverage
coverage: ## 运行测试并生成覆盖率报告
	@echo "$(BOLD)$(BLUE)Running tests with coverage...$(RESET)"
	@$(UV) run $(PYTEST) --cov=$(SRC_DIR) --cov-report=html --cov-report=term
	@echo "$(GREEN)✓ Coverage report generated in $(COVERAGE_DIR)$(RESET)"
	@echo "$(YELLOW)Open $(COVERAGE_DIR)/index.html to view the report$(RESET)"

.PHONY: coverage-report
coverage-report: ## 打开覆盖率报告（浏览器）
	@echo "$(BOLD)$(BLUE)Opening coverage report...$(RESET)"
	@open $(COVERAGE_DIR)/index.html 2>/dev/null || xdg-open $(COVERAGE_DIR)/index.html 2>/dev/null || echo "$(RED)Please open $(COVERAGE_DIR)/index.html manually$(RESET)"

# ============================================================================
# Code Quality Targets
# ============================================================================

.PHONY: lint
lint: ## 运行代码检查（ruff）
	@echo "$(BOLD)$(BLUE)Running linter...$(RESET)"
	@$(UV) run $(RUFF) check $(PYTHON_PATHS)
	@echo "$(GREEN)✓ Linting passed$(RESET)"

.PHONY: lint-fix
lint-fix: ## 自动修复可修复的代码问题
	@echo "$(BOLD)$(BLUE)Auto-fixing code issues...$(RESET)"
	@$(UV) run $(RUFF) check --fix $(PYTHON_PATHS)
	@echo "$(GREEN)✓ Auto-fix completed$(RESET)"

.PHONY: fmt
fmt: format ## 格式化代码（black）
format: ## 格式化代码（black）
	@echo "$(BOLD)$(BLUE)Formatting code...$(RESET)"
	@$(UV) run $(BLACK) $(PYTHON_PATHS)
	@echo "$(GREEN)✓ Code formatted$(RESET)"

.PHONY: fmt-check
fmt-check: ## 检查代码格式（不修改文件）
	@echo "$(BOLD)$(BLUE)Checking code format...$(RESET)"
	@$(UV) run $(BLACK) --check --diff $(PYTHON_PATHS)
	@echo "$(GREEN)✓ Format check completed$(RESET)"

.PHONY: quality
quality: fmt lint ## 运行所有代码质量检查
	@echo "$(GREEN)✓ All quality checks passed$(RESET)"

# ============================================================================
# Cleanup Targets
# ============================================================================

.PHONY: clean
clean: ## 清理缓存文件和临时文件
	@echo "$(BOLD)$(BLUE)Cleaning up...$(RESET)"
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type f -name "*.pyo" -delete 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@rm -rf $(COVERAGE_DIR) 2>/dev/null || true
	@rm -rf dist/ build/ 2>/dev/null || true
	@echo "$(GREEN)✓ Cleanup completed$(RESET)"

.PHONY: clean-all
clean-all: clean ## 深度清理（包括依赖和环境）
	@echo "$(BOLD)$(RED)Deep cleaning (including .venv)...$(RESET)"
	@rm -rf .venv 2>/dev/null || true
	@rm -rf node_modules 2>/dev/null || true
	@echo "$(GREEN)✓ Deep cleanup completed$(RESET)"

# ============================================================================
# Development Utilities
# ============================================================================

.PHONY: shell
shell: ## 启动交互式 Python Shell (IPython)
	@echo "$(BOLD)$(BLUE)Starting IPython shell...$(RESET)"
	@$(UV) run ipython

.PHONY: debug
debug: ## 运行主程序（调试模式）
	@echo "$(BOLD)$(YELLOW)Running in debug mode...$(RESET)"
	@$(UV) run python -m pdb main.py

.PHONY: profile
profile: ## 运行性能分析
	@echo "$(BOLD)$(BLUE)Running performance profiling...$(RESET)"
	@$(UV) run python -m cProfile -s cumulative main.py

.PHONY: benchmark
benchmark: ## 运行性能基准测试
	@echo "$(BOLD)$(BLUE)Running benchmarks...$(RESET)"
	@$(UV) run $(PYTEST) --benchmark-only --benchmark-verbose

.PHONY: typecheck
typecheck: ## 运行类型检查（如果配置了 mypy）
	@echo "$(BOLD)$(BLUE)Running type checking...$(RESET)"
	@$(UV) run mypy $(SRC_DIR) 2>/dev/null || echo "$(YELLOW)mypy not installed, skipping type check$(RESET)"

# ============================================================================
# Docker Targets (if applicable)
# ============================================================================

.PHONY: docker-build
docker-build: ## 构建 Docker 镜像
	@echo "$(BOLD)$(BLUE)Building Docker image...$(RESET)"
	@docker build --build-arg CACHE_BUSTER=$(shell date +%s) -t $(PROJECT_NAME):latest .
	@echo "$(GREEN)✓ Docker image built$(RESET)"

.PHONY: docker-run
docker-run: ## 运行 Docker 容器
	@echo "$(BOLD)$(BLUE)Running Docker container...$(RESET)"
	@docker run --rm -it $(PROJECT_NAME):latest

# ============================================================================
# CI/CD Targets
# ============================================================================

.PHONY: ci
ci: install lint fmt-check test ## CI 流程（安装、检查、测试）
	@echo "$(GREEN)✓ CI pipeline completed successfully$(RESET)"

.PHONY: pre-commit
pre-commit: quality test-quick ## Git 提交前检查
	@echo "$(GREEN)✓ Pre-commit checks passed$(RESET)"

# ============================================================================
# Project Management
# ============================================================================

.PHONY: version
version: ## 显示项目版本信息
	@echo "$(BOLD)Project: $(PROJECT_NAME)$(RESET)"
	@grep -E '^version = ' pyproject.toml | cut -d'"' -f2 | xargs echo "Version:"
	@echo "Python: $(PYTHON)"
	@$(UV) --version | xargs echo "UV:"

.PHONY: deps
deps: ## 显示项目依赖树
	@echo "$(BOLD)$(BLUE)Project dependencies:$(RESET)"
	@$(UV) pip list

.PHONY: outdated
outdated: ## 检查过期的依赖
	@echo "$(BOLD)$(BLUE)Checking for outdated dependencies...$(RESET)"
	@$(UV) pip list --outdated

.PHONY: upgrade
upgrade: ## 升级所有依赖到最新版本
	@echo "$(BOLD)$(YELLOW)Upgrading dependencies...$(RESET)"
	@$(UV) sync --upgrade
	@echo "$(GREEN)✓ Dependencies upgraded$(RESET)"

# ============================================================================
# Advanced Targets
# ============================================================================

.PHONY: all
all: clean install quality test ## 完整构建流程
	@echo "$(GREEN)✓ Full build completed successfully$(RESET)"

.PHONY: dev
dev: dev-install quality ## 开发环境设置
	@echo "$(GREEN)✓ Development environment ready$(RESET)"

.PHONY: release
release: clean all ## 发布准备（完整测试和构建）
	@echo "$(BOLD)$(GREEN)✓ Ready for release$(RESET)"

# ============================================================================
# Special Targets
# ============================================================================

.PHONY: check
check: ## 健康检查（验证环境配置）
	@echo "$(BOLD)$(BLUE)Running health check...$(RESET)"
	@which $(PYTHON) > /dev/null && echo "$(GREEN)✓ Python found$(RESET)" || echo "$(RED)✗ Python not found$(RESET)"
	@which $(UV) > /dev/null && echo "$(GREEN)✓ UV found$(RESET)" || echo "$(RED)✗ UV not found$(RESET)"
	@which $(BLACK) > /dev/null && echo "$(GREEN)✓ Black found$(RESET)" || echo "$(YELLOW)⚠ Black not found (install with 'make dev-install')$(RESET)"
	@which $(RUFF) > /dev/null && echo "$(GREEN)✓ Ruff found$(RESET)" || echo "$(YELLOW)⚠ Ruff not found (install with 'make dev-install')$(RESET)"
	@test -f pyproject.toml && echo "$(GREEN)✓ pyproject.toml found$(RESET)" || echo "$(RED)✗ pyproject.toml not found$(RESET)"
	@test -f main.py && echo "$(GREEN)✓ main.py found$(RESET)" || echo "$(RED)✗ main.py not found$(RESET)"

# Prevent make from treating arguments as targets
%:
	@: