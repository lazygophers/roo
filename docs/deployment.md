# 部署指南

## 概述

本指南详细说明如何在不同环境中部署 Roo 配置管理系统，包括开发环境、测试环境和生产环境的部署方案。

## 系统要求

### 最低系统要求
- **操作系统**: macOS 10.15+, Linux (Ubuntu 18.04+), Windows 10+
- **Python**: 3.12 或更高版本
- **Node.js**: 16.x 或更高版本
- **内存**: 最少 2GB RAM
- **存储**: 最少 1GB 可用空间

### 推荐配置
- **Python**: 3.12.x (最新稳定版)
- **Node.js**: 20.x LTS
- **内存**: 4GB+ RAM
- **存储**: 5GB+ SSD 存储
- **网络**: 稳定的互联网连接

## 开发环境部署

### 1. 环境准备

#### 安装 Python 和 UV
```bash
# macOS (使用 Homebrew)
brew install python@3.12
pip install uv

# Linux (Ubuntu)
sudo apt update
sudo apt install python3.12 python3.12-pip
pip3 install uv

# Windows  
# 从 python.org 下载并安装 Python 3.12
pip install uv
```

#### 安装 Node.js
```bash
# macOS
brew install node@20

# Linux
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt-get install -y nodejs

# Windows
# 从 nodejs.org 下载并安装 LTS 版本
```

### 2. 后端服务部署

#### 克隆项目
```bash
git clone https://github.com/your-org/roo-config-management.git
cd roo-config-management
```

#### 安装依赖
```bash
# 使用 UV 安装 Python 依赖
uv sync

# 验证安装
uv run python --version
uv run python -c "import fastapi; print('FastAPI installed successfully')"
```

#### 启动后端服务
```bash
# 开发模式 (自动重载)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 验证服务
curl http://localhost:8000/docs
```

### 3. 前端应用部署

#### 安装依赖
```bash
cd frontend
npm install

# 验证安装
npm list react typescript
```

#### 启动前端应用
```bash
# 开发模式
npm start

# 应用将在 http://localhost:3000 启动
```

### 4. 开发环境验证

#### 健康检查
```bash
# 后端健康检查
curl http://localhost:8000/health

# 前端访问测试
curl http://localhost:3000

# API 功能测试
curl -X POST http://localhost:8000/api/models \
  -H "Content-Type: application/json" \
  -d '{}'
```

## 生产环境部署

### 1. Docker 部署 (推荐)

#### 创建 Dockerfile
```dockerfile
# 多阶段构建 - 后端
FROM python:3.12-slim as backend

WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen

COPY app ./app
EXPOSE 8000
CMD ["uv", "run", "uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```dockerfile
# 多阶段构建 - 前端
FROM node:20-alpine as frontend

WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci --only=production

COPY frontend ./
RUN npm run build

FROM nginx:alpine
COPY --from=frontend /app/build /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

#### Docker Compose 配置
```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    ports:
      - "8000:8000"
    environment:
      - PYTHONPATH=/app
      - DEBUG=false
    volumes:
      - ./resources:/app/resources:ro
      - ./config_database.json:/app/config_database.json
    restart: unless-stopped
    
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile.frontend
    ports:
      - "80:80"
    depends_on:
      - backend
    environment:
      - REACT_APP_API_URL=http://backend:8000
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    ports:
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    depends_on:
      - frontend
      - backend
    restart: unless-stopped
```

#### 部署命令
```bash
# 构建和启动
docker-compose build
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 2. 传统部署方式

#### 后端部署
```bash
# 创建系统服务用户
sudo useradd --system --shell /bin/bash roo-backend
sudo mkdir -p /opt/roo-backend
sudo chown roo-backend:roo-backend /opt/roo-backend

# 部署代码
sudo -u roo-backend git clone https://github.com/your-org/roo-config-management.git /opt/roo-backend
cd /opt/roo-backend
sudo -u roo-backend uv sync

# 创建 systemd 服务
sudo tee /etc/systemd/system/roo-backend.service > /dev/null <<EOF
[Unit]
Description=Roo Configuration Management Backend
After=network.target

[Service]
Type=exec
User=roo-backend
Group=roo-backend
WorkingDirectory=/opt/roo-backend
Environment=PATH=/opt/roo-backend/.venv/bin
ExecStart=/opt/roo-backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable roo-backend
sudo systemctl start roo-backend
```

#### 前端部署
```bash
# 构建前端
cd frontend
npm run build

# 配置 Nginx
sudo tee /etc/nginx/sites-available/roo-frontend > /dev/null <<EOF
server {
    listen 80;
    server_name your-domain.com;
    root /var/www/roo-frontend;
    index index.html;

    # 前端路由支持
    location / {
        try_files \$uri \$uri/ /index.html;
    }

    # API 代理
    location /api/ {
        proxy_pass http://localhost:8000/api/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
EOF

# 部署静态文件
sudo mkdir -p /var/www/roo-frontend
sudo cp -r build/* /var/www/roo-frontend/
sudo chown -R www-data:www-data /var/www/roo-frontend

# 启用站点
sudo ln -s /etc/nginx/sites-available/roo-frontend /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

### 3. HTTPS 配置

#### Let's Encrypt 证书
```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d your-domain.com

# 自动续期
sudo crontab -e
# 添加: 0 12 * * * /usr/bin/certbot renew --quiet
```

#### 手动证书配置
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/your/cert.pem;
    ssl_certificate_key /path/to/your/key.pem;
    
    # SSL 安全配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_prefer_server_ciphers on;
    
    # 其他配置...
}
```

## 环境配置

### 1. 环境变量

#### 后端环境变量
```bash
# .env 文件
DEBUG=false
API_HOST=0.0.0.0
API_PORT=8000
CORS_ORIGINS=["http://localhost:3000", "https://your-domain.com"]
LOG_LEVEL=INFO

# 数据库配置
DATABASE_PATH=./config_database.json

# 部署路径配置  
ROO_PATH=~/.roo
KILOCODE_PATH=~/.kilocode
```

#### 前端环境变量
```bash
# .env.production
REACT_APP_API_URL=https://api.your-domain.com
REACT_APP_VERSION=1.0.0
GENERATE_SOURCEMAP=false
```

### 2. 配置文件管理

#### 配置文件结构
```
config/
├── production.yaml      # 生产环境配置
├── staging.yaml         # 测试环境配置
├── development.yaml     # 开发环境配置
└── common.yaml          # 通用配置
```

#### 动态配置加载
```python
# config.py
import os
import yaml
from pathlib import Path

def load_config():
    env = os.getenv('ENVIRONMENT', 'development')
    config_file = Path(f'config/{env}.yaml')
    
    with open(config_file) as f:
        return yaml.safe_load(f)
```

## 监控和日志

### 1. 日志配置

#### 后端日志配置
```python
# logging_config.py
import logging.config

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'default': {
            'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        },
    },
    'handlers': {
        'file': {
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': '/var/log/roo-backend/app.log',
            'maxBytes': 10485760,  # 10MB
            'backupCount': 5,
            'formatter': 'default',
        },
    },
    'loggers': {
        '': {
            'handlers': ['file'],
            'level': 'INFO',
        },
    },
}
```

#### Nginx 访问日志
```nginx
# 自定义日志格式
log_format custom '$remote_addr - $remote_user [$time_local] '
                 '"$request" $status $bytes_sent '
                 '"$http_referer" "$http_user_agent"';

access_log /var/log/nginx/roo-access.log custom;
error_log /var/log/nginx/roo-error.log;
```

### 2. 监控配置

#### 健康检查端点
```python
# main.py
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "version": "1.0.0"
    }
```

#### Prometheus 指标
```python
# metrics.py
from prometheus_client import Counter, Histogram, generate_latest

REQUEST_COUNT = Counter('http_requests_total', 'Total HTTP requests')
REQUEST_DURATION = Histogram('http_request_duration_seconds', 'HTTP request duration')

@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    
    REQUEST_COUNT.inc()
    REQUEST_DURATION.observe(duration)
    
    return response
```

## 备份和恢复

### 1. 数据备份

#### 配置文件备份
```bash
#!/bin/bash
# backup.sh

BACKUP_DIR="/opt/backups/roo-config"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p "$BACKUP_DIR/$TIMESTAMP"

# 备份配置文件
cp -r /opt/roo-backend/resources "$BACKUP_DIR/$TIMESTAMP/"
cp /opt/roo-backend/config_database.json "$BACKUP_DIR/$TIMESTAMP/"

# 压缩备份
tar -czf "$BACKUP_DIR/backup_$TIMESTAMP.tar.gz" -C "$BACKUP_DIR" "$TIMESTAMP"
rm -rf "$BACKUP_DIR/$TIMESTAMP"

# 保留最近 30 天的备份
find "$BACKUP_DIR" -name "backup_*.tar.gz" -mtime +30 -delete
```

#### 自动备份配置
```bash
# 添加到 crontab
0 2 * * * /opt/scripts/backup.sh
```

### 2. 数据恢复

#### 恢复脚本
```bash
#!/bin/bash
# restore.sh

BACKUP_FILE=$1
if [ -z "$BACKUP_FILE" ]; then
    echo "Usage: $0 <backup_file>"
    exit 1
fi

# 停止服务
sudo systemctl stop roo-backend

# 恢复数据
tar -xzf "$BACKUP_FILE" -C /tmp/
cp -r /tmp/backup_*/resources /opt/roo-backend/
cp /tmp/backup_*/config_database.json /opt/roo-backend/

# 重启服务
sudo systemctl start roo-backend
```

## 安全配置

### 1. 网络安全

#### 防火墙配置
```bash
# UFW 配置
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp
sudo ufw deny 8000/tcp  # 只允许内部访问后端
```

#### Nginx 安全配置
```nginx
# 安全标头
add_header X-Frame-Options DENY;
add_header X-Content-Type-Options nosniff;
add_header X-XSS-Protection "1; mode=block";
add_header Referrer-Policy "strict-origin-when-cross-origin";

# 隐藏版本信息
server_tokens off;

# 限制请求大小
client_max_body_size 10M;

# 速率限制
limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
limit_req zone=api burst=20;
```

### 2. 应用安全

#### CORS 配置
```python
# main.py
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-domain.com"],
    allow_credentials=False,
    allow_methods=["POST", "GET"],
    allow_headers=["*"],
)
```

#### 输入验证
```python
# 文件路径验证
def validate_file_path(file_path: str) -> bool:
    # 防止路径遍历
    if ".." in file_path or file_path.startswith("/"):
        return False
    return True
```

## 故障排除

### 1. 常见问题

#### 后端无法启动
```bash
# 检查日志
sudo journalctl -u roo-backend -f

# 检查端口占用
sudo netstat -tlnp | grep 8000

# 检查依赖
uv run python -c "import fastapi, uvicorn"
```

#### 前端构建失败
```bash
# 清理缓存
npm cache clean --force
rm -rf node_modules package-lock.json
npm install

# 检查 Node.js 版本
node --version
npm --version
```

#### 数据库问题
```bash
# 检查数据库文件权限
ls -la config_database.json

# 重建数据库
rm config_database.json
# 重启应用，数据库会自动重建
```

### 2. 性能问题

#### 内存使用过高
```bash
# 监控内存使用
sudo systemctl status roo-backend
top -p $(pgrep -f uvicorn)

# 调整 worker 数量
# 修改 systemd 服务文件中的 --workers 参数
```

#### 响应时间慢
```bash
# 启用详细日志
export LOG_LEVEL=DEBUG

# 检查数据库大小
ls -lh config_database.json

# 重建索引
# 删除数据库文件重新扫描
```

## 维护指南

### 1. 定期维护任务

#### 日志清理
```bash
# 清理旧日志
find /var/log/roo-backend -name "*.log.*" -mtime +30 -delete
```

#### 数据库优化
```bash
# 定期重建数据库索引
# 可以考虑定期删除数据库文件让系统重新扫描
```

### 2. 更新部署

#### 滚动更新
```bash
# 更新代码
git pull origin main

# 安装新依赖
uv sync

# 重启服务
sudo systemctl restart roo-backend

# 验证服务
curl http://localhost:8000/health
```

#### 前端更新
```bash
cd frontend
npm install
npm run build
sudo cp -r build/* /var/www/roo-frontend/
```

## 扩展配置

### 1. 负载均衡

#### Nginx 负载均衡
```nginx
upstream backend {
    server 127.0.0.1:8000;
    server 127.0.0.1:8001;
    server 127.0.0.1:8002;
}

server {
    location /api/ {
        proxy_pass http://backend/api/;
    }
}
```

### 2. 高可用配置

#### 多实例部署
```bash
# 启动多个后端实例
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 &
uv run uvicorn app.main:app --host 0.0.0.0 --port 8001 &
uv run uvicorn app.main:app --host 0.0.0.0 --port 8002 &
```

这个详细的部署指南涵盖了从开发环境到生产环境的完整部署流程，包括安全配置、监控、备份和故障排除等关键方面。根据实际需求选择合适的部署方案。