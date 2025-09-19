# 🚀 LazyAI Studio 部署指南

## CI/CD 自动化部署

LazyAI Studio 配置了完整的 CI/CD 自动化部署流程，支持以下功能：

### 🔄 自动触发条件

- **推送到 master 分支**：自动构建、测试、发布 Docker 镜像并创建新版本
- **推送到 luoxin 分支**：自动构建、测试、发布 Docker 镜像并创建新版本
- **创建 Pull Request**：自动构建预览镜像并运行测试
- **推送 git 标签 (v*)**：基于标签构建特定版本镜像

### 📦 Docker 镜像发布

每次推送到主分支时，系统会：

1. 运行完整的测试套件（前端 + 后端）
2. 构建多架构 Docker 镜像（linux/amd64, linux/arm64）
3. 推送到 GitHub Container Registry
4. 自动创建 GitHub Release
5. 发送部署成功通知

### 🏷️ 版本管理

- **自动版本递增**：每次发布自动递增补丁版本号
- **标签命名规范**：采用 `v{major}.{minor}.{patch}` 格式
- **镜像标签**：支持 `latest`、`v1.2.3`、分支名等多种标签

## 🐳 Docker 部署方式

### 方式一：使用最新镜像

```bash
# 拉取最新镜像
docker pull ghcr.io/luoxin/roo:latest

# 运行容器
docker run -d \
  --name lazyai-studio \
  -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  ghcr.io/luoxin/roo:latest
```

### 方式二：使用 Docker Compose（推荐）

#### 开发环境
```bash
# 使用本地构建
make docker-deploy
```

#### 生产环境
```bash
# 使用发布的镜像
docker-compose -f docker-compose.prod.yml up -d
```

### 方式三：指定版本部署

```bash
# 部署特定版本
docker pull ghcr.io/luoxin/roo:v1.0.0
docker run -d \
  --name lazyai-studio \
  -p 8000:8000 \
  ghcr.io/luoxin/roo:v1.0.0
```

## 🔧 GitHub 仓库配置

### 分支保护建议

建议在 GitHub 仓库设置中配置以下分支保护规则：

#### master 分支保护
- ✅ 限制推送到匹配的分支
- ✅ 要求 pull request 审查
- ✅ 要求状态检查通过
  - `test (ubuntu-latest)`
  - `docker (ubuntu-latest)`
- ✅ 要求分支是最新的
- ✅ 限制推送（仅管理员）

#### luoxin 分支保护
- ✅ 要求状态检查通过
  - `test (ubuntu-latest)`
  - `docker (ubuntu-latest)`
- ✅ 要求分支是最新的

### 必需的 Secrets

CI/CD 流程使用以下 GitHub Secrets：

- `GITHUB_TOKEN`（自动提供）：用于推送镜像到 GHCR

### 权限配置

确保 GitHub Actions 有以下权限：
- `contents: write` - 创建 Release
- `packages: write` - 推送 Docker 镜像
- `pull-requests: write` - 添加 PR 评论

## 🚀 部署流程

### 标准发布流程

1. **开发**：在 feature 分支开发功能
2. **测试**：创建 PR 到 master 分支
   - 自动运行测试和构建预览镜像
   - 代码审查
3. **合并**：PR 合并到 master
   - 自动运行完整测试套件
   - 构建多架构 Docker 镜像
   - 推送到 GHCR
   - 创建新版本 Release
4. **部署**：使用发布的镜像部署到生产环境

### 热修复流程

紧急修复可以直接推送到 luoxin 分支：

1. **修复**：在 hotfix 分支修复问题
2. **推送**：直接推送到 luoxin 分支
   - 自动触发完整 CI/CD 流程
   - 立即发布新版本
3. **同步**：将修复合并回 master 分支

## 📊 监控和日志

### 健康检查

Docker 容器配置了健康检查：
- 检查端点：`http://localhost:8000/api/health`
- 检查间隔：30秒
- 超时时间：10秒
- 重试次数：3次

### 日志收集

容器日志映射到宿主机：
- 应用日志：`./logs/`
- 数据文件：`./data/`

### 访问地址

部署成功后可通过以下地址访问：
- 🏠 主应用：http://localhost:8000
- 📖 API 文档：http://localhost:8000/docs
- 💚 健康检查：http://localhost:8000/api/health

## 🔍 故障排除

### 查看容器日志
```bash
docker logs lazyai-studio
```

### 查看构建状态
访问 GitHub Actions 页面查看详细的构建日志和状态。

### 常见问题

1. **镜像拉取失败**：确保有正确的 GHCR 访问权限
2. **容器启动失败**：检查端口占用和卷挂载路径
3. **健康检查失败**：检查容器内应用是否正常启动

---

🤖 **LazyGophers 出品** - 让 AI 替你思考，让工具替你工作！