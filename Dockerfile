# LazyAI Studio Dockerfile
# 多阶段构建：前端构建 -> 后端构建 -> 最终运行

# ========== 前端构建阶段 ==========
FROM node:22.19.0 AS frontend-builder

# 启用 corepack 并设置 pnpm
RUN corepack enable && corepack prepare pnpm@9.15.0 --activate

# 设置工作目录
WORKDIR /app/frontend

# 设置环境变量优化构建（不考虑性能限制）
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true
ENV GENERATE_SOURCEMAP=false
ENV CI=true
ENV PNPM_HOME=/usr/local/bin
ENV PATH=$PNPM_HOME:$PATH

# 复制依赖配置文件
COPY frontend/package.json frontend/pnpm-lock.yaml frontend/.npmrc ./

# 安装前端依赖（使用pnpm缓存挂载）
RUN --mount=type=cache,target=/root/.local/share/pnpm/store \
    pnpm install --frozen-lockfile --production=false

# 复制前端源码
COPY frontend/ ./

# 构建前端生产版本（使用缓存挂载）
RUN --mount=type=cache,target=/app/frontend/.next/cache \
    pnpm build

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

# 安装 uv (Python 包管理器) 使用缓存挂载
RUN --mount=type=cache,target=/root/.cache/pip \
    pip install uv

# 复制 Python 项目配置文件
COPY pyproject.toml uv.lock ./

# 创建虚拟环境并安装依赖（使用缓存挂载）
RUN --mount=type=cache,target=/root/.cache/uv \
    uv venv .venv && \
    uv sync --frozen

# ========== 最终运行阶段 ==========
FROM alpine:latest

# 设置环境变量（运行时优化）
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONOPTIMIZE=2
ENV PYTHONPATH=/app
ENV TZ=Asia/Shanghai

# LazyAI Studio 应用环境变量
ENV ENVIRONMENT=local
ENV DEBUG=false
ENV LOG_LEVEL=INFO
ENV HOST=0.0.0.0
ENV PORT=8000
ENV CORS_ORIGINS=*
ENV CORS_ALLOW_CREDENTIALS=true
ENV CACHE_TTL=3600

# 创建非root用户（Alpine方式）
RUN addgroup -g 1000 appuser && adduser -u 1000 -G appuser -s /bin/sh -D appuser

# 设置工作目录
WORKDIR /app

# 安装运行时必需的系统依赖（最小化版本）
RUN apk add --no-cache \
    curl \
    ca-certificates \
    tzdata \
    tini \
    libffi \
    python3 \
    gcc \
    musl-dev \
    linux-headers \
    && cp /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

# 从前端构建阶段复制构建后的静态文件
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# 从后端构建阶段复制构建后的依赖
COPY --from=backend-builder /app/pyproject.toml /app/uv.lock ./
COPY --from=backend-builder /app/.venv .venv

# 修复虚拟环境中的 Python 符号链接到 Alpine 系统路径
RUN cd /app/.venv/bin && \
    rm -f python python3 && \
    ln -s /usr/bin/python3 python && \
    ln -s /usr/bin/python3 python3

# 复制后端源码
COPY app/ ./app/
COPY resources/ ./resources/

# 创建必要的目录
RUN mkdir -p logs data/cache

# 设置权限并切换到非root用户
RUN chown -R appuser:appuser /app
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令（直接启动，不使用tini进行调试）
CMD ["/app/.venv/bin/python", "-m", "uvicorn", "app.main_optimized:app", \
    "--host", "0.0.0.0", "--port", "8000", \
    "--workers", "1", "--log-level", "warning"]