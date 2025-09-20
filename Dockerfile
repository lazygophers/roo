# LazyAI Studio Dockerfile
# 多阶段构建：前端构建 -> 后端构建 -> 最终运行

# ========== 前端构建阶段 ==========
FROM node:22.19.0 AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 设置环境变量优化构建（不考虑性能限制）
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true
ENV GENERATE_SOURCEMAP=false
ENV CI=true

# 复制前端源码
COPY frontend/ ./

# 安装前端依赖
RUN yarn install --frozen-lockfile --production=false

# 构建前端生产版本
RUN yarn build

# ========== 后端构建阶段 ==========
FROM python:3.12 AS backend-builder

# 设置工作目录
WORKDIR /app

# 安装系统依赖（构建阶段不考虑大小）
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    git \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv (Python 包管理器)
RUN pip install uv

# 复制 Python 项目配置文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖（构建阶段使用完整功能）
RUN uv venv .venv
RUN uv venv --seed
RUN uv sync --frozen --no-dev --no-install-project --no-install-workspace

# ========== 最终运行阶段 ==========
FROM alpine

# 设置环境变量（运行时优化）
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=2
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

# 创建非root用户（Alpine方式）
RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -s /bin/sh -D appuser

# 设置工作目录
WORKDIR /app

# 安装运行时必需的系统依赖（使用apk）
RUN apk add --no-cache \
    curl \
    ca-certificates \
    tzdata \
    tini \
    libffi \
    libressl-dev \
    musl-dev \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone \
    && apk del tzdata

# 从构建阶段复制虚拟环境
COPY --from=backend-builder /app/.venv /app/.venv

# 复制后端源码
COPY app/ ./app/
COPY resources/ ./resources/

# 从前端构建阶段复制构建后的静态文件
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# 创建必要的目录
RUN mkdir -p logs data/cache

# 设置权限并切换到非root用户
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 健康检查（最小化频率减少资源消耗）
HEALTHCHECK --interval=120s --timeout=3s --start-period=60s --retries=1 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 使用tini作为init进程（Alpine最佳实践）
ENTRYPOINT ["/sbin/tini", "--"]

# 启动命令（直接使用虚拟环境的相对路径）
CMD [".venv/bin/python", "-m", "uvicorn", "app.main_optimized:app", \
    "--host", "0.0.0.0", "--port", "8000", \
    "--workers", "1", "--log-level", "warning"]