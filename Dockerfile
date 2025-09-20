# LazyAI Studio Dockerfile
# 多阶段构建：前端构建 -> 后端运行

# ========== 前端构建阶段 ==========
FROM node:22.19.0-alpine AS frontend-builder

# 设置工作目录
WORKDIR /app/frontend

# 设置环境变量优化构建
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true
ENV GENERATE_SOURCEMAP=false
ENV CI=true

# 复制前端包配置文件
COPY frontend/package.json frontend/yarn.lock ./

# 安装前端依赖
RUN yarn install --frozen-lockfile --production=false --network-timeout 100000

# 复制前端源码
COPY frontend/ ./

# 构建前端生产版本
RUN NODE_OPTIONS="--max-old-space-size=2048" \
    DISABLE_ESLINT_PLUGIN=true \
    GENERATE_SOURCEMAP=false \
    yarn build

# ========== 后端运行阶段 ==========
FROM python:3.12-slim

# 设置环境变量
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV UV_NO_CACHE=1

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 安装 uv (Python 包管理器)
RUN pip install uv

# 复制 Python 项目配置文件
COPY pyproject.toml uv.lock ./

# 安装 Python 依赖
RUN uv sync --frozen --no-dev

# 复制后端源码
COPY app/ ./app/
COPY resources/ ./resources/
COPY data/ ./data/

# 从前端构建阶段复制构建后的静态文件
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# 创建必要的目录
RUN mkdir -p logs data/cache

# 设置权限
RUN chmod -R 755 /app

# 暴露端口
EXPOSE 8000

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/api/health || exit 1

# 启动命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]