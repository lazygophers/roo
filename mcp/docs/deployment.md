# 部署指南

本文档详细介绍了 MCP 服务器的各种部署方式，包括本地部署、Docker 部署以及生产环境部署。

## 📋 目录

- [部署前准备](#部署前准备)
- [本地部署](#本地部署)
- [Docker 部署](#docker-部署)
- [生产环境部署](#生产环境部署)
- [配置管理](#配置管理)
- [监控与日志](#监控与日志)
- [性能优化](#性能优化)
- [故障排查](#故障排查)

## 部署前准备

### 系统要求

- **操作系统**: Linux/macOS/Windows
- **Python**: 3.12 或更高版本
- **内存**: 最少 512MB，推荐 1GB+
- **存储**: 最少 100MB 可用空间

### 依赖安装

```bash
# 安装 uv 包管理器
curl -LsSf https://astral.sh/uv/install.sh | sh

# 验证安装
uv --version
```

### 环境变量

根据需要设置以下环境变量：

```bash
# 配置文件路径
export MCP_CONFIG_PATH=/path/to/config.yaml

# 日志级别
export MCP_LOG_LEVEL=INFO

# 数据存储路径
export MCP_DATA_PATH=/var/lib/mcp-server
```

## 本地部署

### 1. 源码部署

```bash
# 克隆项目
git clone https://github.com/lazygophers/roo.git
cd roo/mcp

# 安装依赖
uv sync

# 启动服务
uv run main
```

### 2. 使用不同的传输模式

#### STDIO 模式

```bash
# 启动 STDIO 模式
uv run main --transport stdio

# 测试连接
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | uv run main
```

#### SSE 模式

```bash
# 启动 SSE 模式
uv run main --transport sse --port 8000

# 测试连接
curl http://localhost:8000/tools/list
```

#### HTTP Stream 模式

```bash
# 启动 HTTP Stream 模式
uv run main --transport http-stream --port 8000

# 测试连接
curl -N http://localhost:8000/stream
```

## Docker 部署

### 1. 构建 Docker 镜像

```bash
# 构建镜像
docker build -t mcp-server:latest .

# 或者使用 uv 构建
docker build --build-arg UV_VERSION=latest -t mcp-server:latest .
```

### 2. 运行容器

#### STDIO + Docker 模式

```bash
# 运行容器
docker run -it --rm \
  -v $(pwd)/config.yaml:/app/config.yaml \
  mcp-server:latest \
  --transport stdio
```

#### SSE + Docker 模式

```bash
# 运行容器
docker run -d \
  --name mcp-server-sse \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v /var/lib/mcp-server:/app/data \
  mcp-server:latest \
  --transport sse \
  --port 8000
```

#### HTTP Stream + Docker 模式

```bash
# 运行容器
docker run -d \
  --name mcp-server-http \
  -p 8000:8000 \
  -v $(pwd)/config.yaml:/app/config.yaml \
  -v /var/lib/mcp-server:/app/data \
  mcp-server:latest \
  --transport http-stream \
  --port 8000
```

### 3. Docker Compose 部署

创建 `docker-compose.yml` 文件：

```yaml
version: "3.8"

services:
  mcp-server:
    image: mcp-server:latest
    container_name: mcp-server
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - ./config.yaml:/app/config.yaml:ro
      - mcp-data:/app/data
    environment:
      - MCP_LOG_LEVEL=INFO

volumes:
  mcp-data:
```

启动服务：

```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

## 生产环境部署

### 1. 使用 systemd（Linux）

创建服务文件 `/etc/systemd/system/mcp-server.service`：

```ini
[Unit]
Description=MCP Server
After=network.target

[Service]
Type=simple
User=mcp
Group=mcp
WorkingDirectory=/opt/mcp-server
Environment=PATH=/opt/mcp-server/.venv/bin
ExecStart=/opt/mcp-server/.venv/bin/python main \
  --config /etc/mcp-server/config.yaml \
  --transport http-stream \
  --port 8000
Restart=always
RestartSec=10

# 安全设置
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/var/lib/mcp-server

[Install]
WantedBy=multi-user.target
```

安装和启动服务：

```bash
# 创建用户和目录
sudo useradd -r -s /bin/false mcp
sudo mkdir -p /opt/mcp-server /var/lib/mcp-server /etc/mcp-server
sudo chown -R mcp:mcp /opt/mcp-server /var/lib/mcp-server

# 复制文件
sudo cp -r . /opt/mcp-server/
sudo cp config.yaml /etc/mcp-server/

# 安装依赖
cd /opt/mcp-server
sudo -u mcp uv sync

# 启动服务
sudo systemctl daemon-reload
sudo systemctl enable mcp-server
sudo systemctl start mcp-server

# 检查状态
sudo systemctl status mcp-server
```

### 2. 使用 Nginx 反向代理

创建 Nginx 配置 `/etc/nginx/sites-available/mcp-server`：

```nginx
upstream mcp_backend {
    server 127.0.0.1:8000;
    keepalive 32;
}

server {
    listen 80;
    server_name mcp.example.com;

    # 重定向到 HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name mcp.example.com;

    # SSL 配置
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # 安全头
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";

    # 限制请求大小
    client_max_body_size 10M;


    # SSE 端点
    location /sse {
        proxy_pass http://mcp_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;

        # SSE 特定配置
        proxy_buffering off;
        proxy_cache off;
    }

    # HTTP Stream 端点
    location /stream {
        proxy_pass http://mcp_backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # API 端点
    location / {
        proxy_pass http://mcp_backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # 超时设置
        proxy_connect_timeout 5s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}
```

启用配置：

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/mcp-server /etc/nginx/sites-enabled/

# 测试配置
sudo nginx -t

# 重启 Nginx
sudo systemctl restart nginx
```

### 3. 使用 Kubernetes

创建 `deployment.yaml`：

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: mcp-server
  labels:
    app: mcp-server
spec:
  replicas: 3
  selector:
    matchLabels:
      app: mcp-server
  template:
    metadata:
      labels:
        app: mcp-server
    spec:
      containers:
        - name: mcp-server
          image: mcp-server:latest
          ports:
            - containerPort: 8000
          env:
            - name: MCP_LOG_LEVEL
              value: "INFO"
          volumeMounts:
            - name: config
              mountPath: /app/config.yaml
              subPath: config.yaml
            - name: data
              mountPath: /app/data
          resources:
            requests:
              memory: "256Mi"
              cpu: "250m"
            limits:
              memory: "512Mi"
              cpu: "500m"
      volumes:
        - name: config
          configMap:
            name: mcp-config
        - name: data
          persistentVolumeClaim:
            claimName: mcp-data
---
apiVersion: v1
kind: Service
metadata:
  name: mcp-service
spec:
  selector:
    app: mcp-server
  ports:
    - port: 80
      targetPort: 8000
  type: ClusterIP
---
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: mcp-ingress
  annotations:
    nginx.ingress.kubernetes.io/rewrite-target: /
    cert-manager.io/cluster-issuer: letsencrypt-prod
spec:
  tls:
    - hosts:
        - mcp.example.com
      secretName: mcp-tls
  rules:
    - host: mcp.example.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: mcp-service
                port:
                  number: 80
---
apiVersion: v1
kind: ConfigMap
metadata:
  name: mcp-config
data:
  config.yaml: |
    server:
      name: "mcp-server"
      version: "1.0.0"

    transport:
      type: "http-stream"
      host: "0.0.0.0"
      port: 8000

    storage:
      type: "lancedb"
      path: "/app/data"

    tools:
      enabled: true
      auto_discover: true

    logging:
      level: "INFO"
      format: "json"
---
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: mcp-data
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 1Gi
```

部署到集群：

```bash
# 应用配置
kubectl apply -f deployment.yaml

# 查看状态
kubectl get pods -l app=mcp-server
kubectl get service mcp-service
kubectl get ingress mcp-ingress
```

## 配置管理

### 1. 配置文件结构

```yaml
# config.yaml
server:
  name: "my-mcp-server"
  version: "1.0.0"

transport:
  type: "http-stream" # stdio, sse, http-stream
  host: "0.0.0.0"
  port: 8000

storage:
  type: "lancedb" # lancedb, duckdb, tinydb
  path: "./data"

tools:
  enabled: true
  auto_discover: true
  directories:
    - "./tools"

logging:
  level: "INFO"
  format: "text"
  # stdio 模式默认不输出日志，其他模式默认输出到控制台
```

### 2. 环境变量覆盖

环境变量会覆盖配置文件中的同名设置：

```bash
# 覆盖传输类型
export MCP_TRANSPORT_TYPE=sse

# 覆盖端口
export MCP_PORT=8080

# 覆盖存储路径
export MCP_STORAGE_PATH=/custom/path
```

### 3. 配置热更新

支持配置文件热更新，无需重启服务：

```bash
# 修改配置文件后发送 SIGHUP 信号
kill -HUP $(pidof mcp_server)

# 或者使用 HTTP 端点
curl -X POST http://localhost:8000/reload-config \
  -H "Authorization: Bearer your-api-key"
```

## 日志配置

### 1. 日志配置

```yaml
logging:
  level: "INFO" # DEBUG, INFO, WARNING, ERROR
  format: "text" # 文本格式
  # stdio 模式默认不输出日志，其他模式默认输出到控制台
```

### 2. 不同传输模式的日志行为

- **stdio 模式**: 默认不输出日志
- **sse 模式**: 默认输出到控制台
- **http-stream 模式**: 默认输出到控制台

## 性能优化

### 1. 资源限制

```yaml
# 在配置文件中设置
performance:
  max_connections: 1000
  request_timeout: 30
  worker_processes: 4

storage:
  cache_size: "1GB"
  connection_pool_size: 10
```

### 2. 缓存策略

```yaml
cache:
  enabled: true
  ttl: 300 # 5分钟
  max_size: 1000
  backend: "memory" # memory, redis
```

### 3. 连接池配置

```yaml
database:
  pool_size: 20
  max_overflow: 30
  pool_timeout: 30
  pool_recycle: 3600
```

## 故障排查

### 1. 常见问题

#### 服务无法启动

```bash
# 检查日志
journalctl -u mcp-server -f

# 检查配置
uv run main --validate-config

# 检查端口占用
netstat -tulpn | grep :8000
```

#### 连接超时

```bash
# 检查防火墙
sudo ufw status

# 检查网络连通性
telnet localhost 8000

# 检查代理设置
env | grep -i proxy
```

#### 存储问题

```bash
# 检查存储路径权限
ls -la /var/lib/mcp-server/

# 检查磁盘空间
df -h

# 修复数据库
uv run mcp-server --repair-database
```

### 2. 调试模式

启用调试模式：

```bash
export MCP_LOG_LEVEL=DEBUG
uv run main --debug
```

### 3. 性能分析

使用内置的性能分析工具：

```bash
# 生成性能报告
uv run main --profile --duration 60

# 查看内存使用
uv run main --memory-profile
```

### 4. 备份与恢复

```bash
# 备份数据
uv run mcp-server --backup --output /backup/mcp-backup-$(date +%Y%m%d).tar.gz

# 恢复数据
uv run mcp-server --restore --input /backup/mcp-backup-20240101.tar.gz
```

## 升级指南

### 1. 版本升级

```bash
# 停止服务
sudo systemctl stop mcp-server

# 备份数据
cp -r /var/lib/mcp-server /var/lib/mcp-server.backup

# 更新代码
cd /opt/mcp-server
git pull origin main

# 更新依赖
sudo -u mcp uv sync

# 迁移数据库（如果需要）
uv run mcp-server --migrate

# 启动服务
sudo systemctl start mcp-server
```

### 2. 回滚操作

```bash
# 停止服务
sudo systemctl stop mcp-server

# 恢复数据
sudo rm -rf /var/lib/mcp-server
sudo mv /var/lib/mcp-server.backup /var/lib/mcp-server

# 回滚代码
cd /opt/mcp-server
git checkout v1.0.0

# 重启服务
sudo systemctl start mcp-server
```

## 安全建议

1. **使用 HTTPS**: 生产环境必须使用 SSL/TLS
2. **API 密钥**: 设置强密码并定期更换
3. **网络隔离**: 使用防火墙限制访问
4. **定期更新**: 及时更新依赖包和安全补丁
5. **日志审计**: 启用日志并定期审查
6. **备份策略**: 实施定期备份和恢复测试
