# LazyAI Studio 部署指南

## 概述

LazyAI Studio 支持多种部署方式，包括本地开发、Docker 容器化部署和云端部署。本文档详细说明了各种部署场景的配置和操作方法。

## 系统要求

### 最低要求
- **CPU**: 1 核心
- **内存**: 512MB
- **存储**: 1GB 可用空间
- **操作系统**: Linux, macOS, Windows

### 推荐配置
- **CPU**: 2+ 核心
- **内存**: 2GB+
- **存储**: 10GB+ 可用空间
- **网络**: 稳定的互联网连接

### 软件依赖
- **Python**: 3.12+
- **Node.js**: 18+ (开发环境)
- **Docker**: 20+ (容器化部署)
- **Git**: 2.0+ (源码管理)

## 环境配置

### 环境变量

LazyAI Studio 支持灵活的环境配置，通过环境变量适配不同的部署场景。

#### 核心环境变量

```bash
# 环境类型配置
ENVIRONMENT=local          # 环境类型: local(本地) / remote(远程)
DEBUG=false               # 调试模式: true/false
LOG_LEVEL=INFO           # 日志级别: DEBUG/INFO/WARNING/ERROR

# 服务配置
HOST=0.0.0.0             # 服务绑定地址
PORT=8000                # 服务端口
WORKERS=1                # 工作进程数量

# CORS 配置 (仅 remote 环境)
CORS_ORIGINS=*           # 允许的跨域源
CORS_ALLOW_CREDENTIALS=true  # 允许携带凭据

# 数据存储配置
DATABASE_PATH=/app/data/lazyai.db  # 数据库文件路径
CACHE_TTL=3600           # 缓存过期时间(秒)

# 性能优化配置
CACHE_ENABLED=true       # 启用缓存系统
ULTRA_MODE=false         # 超高性能模式
FILE_WATCH=true          # 文件监听功能
```

#### 环境类型说明

**Local Environment (local)**
- 允许所有 CORS 源 (`*`)
- 启用详细日志和调试功能
- 适用于本地开发和测试

**Remote Environment (remote)**
- 可配置的 CORS 安全策略
- 优化的生产环境配置
- 适用于生产部署

### 配置文件

#### 1. 环境配置文件

创建 `.env` 文件：

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
vim .env
```

**本地开发配置示例**:
```env
ENVIRONMENT=local
DEBUG=true
LOG_LEVEL=DEBUG
HOST=127.0.0.1
PORT=8000
```

**生产环境配置示例**:
```env
ENVIRONMENT=remote
DEBUG=false
LOG_LEVEL=INFO
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=false
CACHE_TTL=7200
ULTRA_MODE=true
```

## 部署方式

### 1. 本地开发部署

#### 快速启动

```bash
# 安装所有依赖
make install

# 启动完整开发环境
make dev

# 或分别启动前后端
make backend-dev    # 后端服务 (端口 8000)
make frontend-dev   # 前端服务 (端口 3000)
```

#### 性能优化版本

```bash
# 启动高性能后端
make backend-dev-optimized

# 启动生产构建版本
make run
```

#### 单独测试

```bash
# 运行全部测试
make test

# 后端测试
make test-backend

# 前端测试
make test-frontend

# 性能测试
make benchmark
```

### 2. Docker 容器化部署

#### 标准 Docker 部署

```bash
# 构建镜像
make docker-build

# 启动服务
make docker-up

# 完整部署 (构建+启动)
make docker-deploy
```

#### Docker Compose 配置

`docker-compose.yml` 配置示例：

```yaml
version: '3.8'

services:
  lazyai-studio:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ENVIRONMENT=remote
      - DEBUG=false
      - LOG_LEVEL=INFO
      - CORS_ORIGINS=https://yourdomain.com
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs
    restart: unless-stopped
    deploy:
      resources:
        limits:
          memory: 512M
          cpus: '0.5'
        reservations:
          memory: 256M
          cpus: '0.25'
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 40s
```

#### 多阶段构建优化

Dockerfile 采用三阶段构建策略：

1. **前端构建阶段**: 使用 Node.js 构建 React 应用
2. **后端构建阶段**: 使用 Python 安装依赖和配置
3. **运行时阶段**: 使用精简的运行时镜像

**构建特性**:
- 多级缓存优化
- Alpine Linux 基础镜像 (~50MB)
- 非 root 用户运行
- 虚拟环境隔离
- 安全扫描支持

### 3. 云端部署

#### 容器注册表

**GitHub Container Registry**:

```bash
# 从 GitHub Packages 拉取镜像
docker pull ghcr.io/lazygophers/roo:latest

# 运行容器
docker run -d \
  --name lazyai-studio \
  -p 8000:8000 \
  -e ENVIRONMENT=remote \
  -e CORS_ORIGINS=https://yourdomain.com \
  -v $(pwd)/data:/app/data \
  ghcr.io/lazygophers/roo:latest
```

#### 云平台部署

**AWS ECS**:
```json
{
  "family": "lazyai-studio",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "256",
  "memory": "512",
  "containerDefinitions": [
    {
      "name": "lazyai-studio",
      "image": "ghcr.io/lazygophers/roo:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {
          "name": "ENVIRONMENT",
          "value": "remote"
        },
        {
          "name": "LOG_LEVEL",
          "value": "INFO"
        }
      ]
    }
  ]
}
```

**Google Cloud Run**:
```yaml
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: lazyai-studio
spec:
  template:
    metadata:
      annotations:
        autoscaling.knative.dev/maxScale: "10"
    spec:
      containerConcurrency: 80
      containers:
      - image: ghcr.io/lazygophers/roo:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "remote"
        - name: PORT
          value: "8000"
        resources:
          limits:
            cpu: "1"
            memory: "512Mi"
```

**Kubernetes**:
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: lazyai-studio
spec:
  replicas: 2
  selector:
    matchLabels:
      app: lazyai-studio
  template:
    metadata:
      labels:
        app: lazyai-studio
    spec:
      containers:
      - name: lazyai-studio
        image: ghcr.io/lazygophers/roo:latest
        ports:
        - containerPort: 8000
        env:
        - name: ENVIRONMENT
          value: "remote"
        - name: CORS_ORIGINS
          value: "https://yourdomain.com"
        resources:
          limits:
            memory: "512Mi"
            cpu: "500m"
          requests:
            memory: "256Mi"
            cpu: "250m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 5
          periodSeconds: 5
```

## 性能优化

### 1. 缓存配置

LazyAI Studio 包含多级缓存系统：

**L1 缓存 (内存)**:
```python
# 配置内存缓存
MEMORY_CACHE_SIZE = 1000
MEMORY_CACHE_TTL = 3600
```

**L2 缓存 (Redis)** (可选):
```env
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_TTL=7200
```

**L3 缓存 (磁盘)**:
```env
DISK_CACHE_PATH=/app/data/cache
DISK_CACHE_SIZE=1GB
```

### 2. 数据库优化

**文件监听优化**:
```env
# 禁用文件监听 (生产环境)
FILE_WATCH=false

# 批量更新间隔
BATCH_UPDATE_INTERVAL=60
```

**索引优化**:
```python
# 数据库索引配置
INDEX_FIELDS = ['slug', 'category', 'tags']
INDEX_REBUILD_INTERVAL = 3600
```

### 3. 超高性能模式

启用超高性能模式：

```env
ULTRA_MODE=true
CACHE_PRELOAD=true
ASYNC_PROCESSING=true
```

**性能对比**:
- 标准模式: ~100 请求/秒
- 优化模式: ~500 请求/秒
- 超高性能模式: ~1000 请求/秒

## CI/CD 集成

### GitHub Actions 自动部署

项目包含完整的 CI/CD 流水线：

**触发条件**:
- Push 到 master 分支
- 版本标签发布
- 文件变更检测

**构建优化**:
- pnpm 缓存 (~40-70% 性能提升)
- Docker BuildKit 缓存
- 多级依赖缓存
- 智能构建跳过

**部署流程**:
```yaml
# .github/workflows/docker-build.yml
name: Docker Build and Deploy
on:
  push:
    branches: [master]
    tags: ['v*']

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    - name: Build and Push
      uses: docker/build-push-action@v5
      with:
        context: .
        push: true
        tags: ghcr.io/lazygophers/roo:latest
        cache-from: type=gha
        cache-to: type=gha,mode=max
```

**手动发布**:
```bash
# 检查 CI/CD 状态
make github-check

# 发布新版本
make github-release VERSION=v1.0.0
```

## 监控和日志

### 1. 健康检查

**HTTP 端点**:
```bash
# 基础健康检查
curl http://localhost:8000/health

# 详细状态信息
curl http://localhost:8000/api/system/status
```

**响应示例**:
```json
{
  "status": "healthy",
  "uptime": 3600,
  "version": "2.0.0",
  "environment": "remote",
  "database": "connected",
  "cache": "active"
}
```

### 2. 日志管理

**日志配置**:
```env
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=/app/logs/app.log
LOG_ROTATION=daily
LOG_RETENTION=30d
```

**安全日志**:
- 防止日志注入攻击 (CWE-117)
- 敏感信息脱敏
- 结构化日志格式

### 3. 性能监控

**指标收集**:
```python
# 内置指标
response_time_histogram
request_count_total
error_rate_gauge
cache_hit_ratio
database_query_duration
```

**Prometheus 集成**:
```yaml
# prometheus.yml
scrape_configs:
  - job_name: 'lazyai-studio'
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/metrics'
```

## 故障排除

### 常见问题

**1. 端口冲突**:
```bash
# 检查端口占用
lsof -i :8000

# 修改端口配置
export PORT=8001
```

**2. 内存不足**:
```bash
# 启用超低内存模式
export ULTRA_MODE=true
export CACHE_SIZE=small
```

**3. 文件权限问题**:
```bash
# 修复权限
sudo chown -R $USER:$USER data/
chmod -R 755 data/
```

**4. 依赖安装失败**:
```bash
# 清理缓存
make clean

# 重新安装
make install
```

### 调试模式

**启用调试**:
```env
DEBUG=true
LOG_LEVEL=DEBUG
TRACE_ENABLED=true
```

**性能分析**:
```bash
# 启用性能分析
export PROFILING=true

# 生成性能报告
make benchmark-report
```

## 安全配置

### 1. 网络安全

**CORS 配置**:
```env
CORS_ORIGINS=https://yourdomain.com,https://api.yourdomain.com
CORS_ALLOW_CREDENTIALS=false
CORS_MAX_AGE=86400
```

**HTTPS 强制**:
```env
FORCE_HTTPS=true
SECURE_COOKIES=true
```

### 2. 数据安全

**加密配置**:
```env
ENCRYPTION_KEY=your-secret-key
DATABASE_ENCRYPTION=true
```

**备份策略**:
```bash
# 自动备份
BACKUP_ENABLED=true
BACKUP_SCHEDULE="0 2 * * *"  # 每日 2:00
BACKUP_RETENTION=7d
```

### 3. 访问控制

**API 限流**:
```env
RATE_LIMIT=1000/hour
BURST_LIMIT=10
```

**IP 白名单**:
```env
ALLOWED_IPS=192.168.1.0/24,10.0.0.0/8
```

## 更新升级

### 版本升级

**容器化升级**:
```bash
# 拉取最新镜像
docker pull ghcr.io/lazygophers/roo:latest

# 重新启动服务
docker-compose down
docker-compose up -d
```

**源码升级**:
```bash
# 备份数据
cp -r data/ data.backup/

# 更新代码
git pull origin master

# 重新安装依赖
make install

# 重启服务
make restart
```

### 数据迁移

**自动迁移**:
```python
# 启动时自动执行
AUTO_MIGRATE=true
MIGRATION_CHECK=true
```

**手动迁移**:
```bash
# 执行数据迁移
python -m app.migrate

# 验证迁移结果
python -m app.validate
```

## 技术支持

### 文档资源
- **API 文档**: `docs/api.md`
- **品牌指南**: `docs/BRANDING.md`
- **性能优化**: `PERFORMANCE_OPTIMIZATION.md`

### 社区支持
- **GitHub Issues**: https://github.com/lazygophers/roo/issues
- **讨论区**: GitHub Discussions
- **贡献指南**: CONTRIBUTING.md

### 企业支持
如需企业级部署支持，请通过项目主页联系 LazyGophers 团队。

---

本部署指南会根据项目发展和社区反馈持续更新。如有问题请参考最新版本文档或提交 Issue。