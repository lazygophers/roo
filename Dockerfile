# 多阶段构建 Dockerfile - 完全自包含的前端+后端构建
# 第一阶段：前端构建 - 使用轻量级alpine镜像但增加足够内存
FROM node:18-alpine AS frontend-builder

# 设置环境变量进行内存优化
ENV NODE_ENV=production
ENV DISABLE_ESLINT_PLUGIN=true
ENV GENERATE_SOURCEMAP=false
ENV INLINE_RUNTIME_CHUNK=false

# 安装必要的构建工具
RUN apk add --no-cache python3 make g++ git

# 设置工作目录
WORKDIR /app

# 仅复制package文件以利用Docker缓存
COPY frontend/package*.json ./frontend/
WORKDIR /app/frontend

# 安装依赖（优化网络和缓存）
RUN npm ci --only=production=false \
    --silent \
    --no-audit \
    --no-fund \
    --maxsockets 1

# 复制前端源码
COPY frontend/ ./

# 构建前端 - 使用分片构建减少内存压力
RUN NODE_OPTIONS="--max-old-space-size=2048" \
    DISABLE_ESLINT_PLUGIN=true \
    GENERATE_SOURCEMAP=false \
    npm run build

# 第二阶段：Python后端
FROM python:3.12-alpine AS backend

# 设置环境变量
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# 安装系统依赖
RUN apk add --no-cache \
    gcc \
    musl-dev \
    libffi-dev \
    && rm -rf /var/cache/apk/*

# 创建非特权用户
RUN addgroup -g 1000 appgroup && \
    adduser -u 1000 -G appgroup -s /bin/sh -D appuser

# 设置工作目录
WORKDIR /app

# 安装uv包管理器
RUN pip install uv

# 复制Python项目配置
COPY pyproject.toml uv.lock ./

# 安装Python依赖
RUN uv sync --frozen --no-dev

# 复制后端源代码
COPY app/ ./app/

# 复制前端构建产物
COPY --from=frontend-builder /app/frontend/build ./frontend/build

# 验证前端文件存在
RUN ls -la ./frontend/build/ && echo "前端构建产物复制成功"

# 更改所有权
RUN chown -R appuser:appgroup /app

# 切换到非特权用户
USER appuser

# 暴露端口
EXPOSE 8000

# 启动命令
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]