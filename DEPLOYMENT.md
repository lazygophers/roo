# 🚀 LazyAI Studio 部署指南

## 🔧 本地开发部署

LazyAI Studio 支持简单的本地开发和生产部署：

### 🚀 快速启动

#### 开发环境
```bash
# 安装依赖
make install

# 启动开发环境（前端 + 后端）
make dev
```

#### 生产环境
```bash
# 构建前端
make build

# 启动生产服务器
make run
```

### 📦 详细命令

查看所有可用命令：
```bash
make help
```

### 🔧 配置说明

#### 环境要求
- Python 3.12+
- Node.js 18+
- UV (Python 包管理器)
- Yarn (前端包管理器)

#### 项目结构
- **后端**：FastAPI 应用，运行在 8000 端口
- **前端**：React 应用，开发时运行在 3000 端口，生产时静态文件由后端服务

### 🚀 部署流程

#### 标准开发流程

1. **安装依赖**：`make install`
2. **开发**：`make dev` 启动开发环境
3. **测试**：`make test` 运行测试套件
4. **构建**：`make build` 构建生产版本
5. **部署**：`make run` 启动生产服务器

#### 性能优化版本

项目提供高性能优化版本：
```bash
# 启动优化版本后端
make backend-dev-optimized

# 运行性能基准测试
make benchmark
```

### 📊 监控和日志

#### 健康检查
- 检查端点：`http://localhost:8000/api/health`
- API 文档：`http://localhost:8000/docs`

#### 访问地址

部署成功后可通过以下地址访问：
- 🏠 主应用：http://localhost:8000
- 📖 API 文档：http://localhost:8000/docs
- 💚 健康检查：http://localhost:8000/api/health

### 🧪 测试

运行测试套件：
```bash
# 运行所有测试
make test

# 快速测试（跳过慢速测试）
make test-fast

# 完整测试套件（包含覆盖率）
make test-full

# 生成覆盖率报告
make test-coverage
```

### 🔍 故障排除

#### 常见问题

1. **依赖安装失败**：确保 UV 和 Yarn 已正确安装
2. **端口占用**：检查 8000 和 3000 端口是否被占用
3. **前端构建失败**：检查 Node.js 版本是否满足要求

#### 检查系统环境
```bash
make check
```

#### 查看项目信息
```bash
make info
```

---

🤖 **LazyGophers 出品** - 让 AI 替你思考，让工具替你工作！