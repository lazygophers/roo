# 🛠️ LazyAI Studio 开发指南

> LazyGophers 出品 - 让开发更懒人化！

## 🎯 项目结构

```
LazyAI Studio/
├── app/                    # 后端 FastAPI 应用
│   ├── core/              # 核心服务
│   ├── models/            # 数据模型
│   └── routers/           # API 路由
├── frontend/              # 前端 React 应用
│   ├── src/              # 源代码
│   ├── build/            # 构建输出
│   └── public/           # 静态资源
├── resources/             # 配置资源
│   ├── models/           # AI 模式定义
│   ├── commands/         # 命令定义
│   ├── rules/            # 规则文件
│   └── hooks/            # 钩子文件
├── docs/                 # 项目文档
├── logs/                 # 日志文件
└── Makefile              # 构建脚本
```

## 🚀 开发环境搭建

### 系统要求
- Python 3.12+
- Node.js 16+
- npm 或 yarn
- UV (Python 包管理器)

### 快速开始
```bash
# 1. 克隆仓库
git clone <repository-url>
cd lazyai-studio

# 2. 检查环境
make check

# 3. 安装依赖
make install

# 4. 启动开发服务器
make dev
```

## 🔧 开发命令

### 依赖管理
```bash
make install           # 安装所有依赖
make backend-install   # 只安装后端依赖
make frontend-install  # 只安装前端依赖
```

### 开发服务器
```bash
make run              # 生产模式启动
make dev              # 开发模式启动（后端集成前端）
make backend-dev      # 只启动后端开发服务器
make frontend-dev     # 只启动前端开发服务器（热重载）
```

### 构建和测试
```bash
make build            # 构建生产版本
make test             # 运行所有测试
make test-backend     # 运行后端测试
make test-frontend    # 运行前端测试
make test-integration # 运行集成测试
```

### 清理和维护
```bash
make clean            # 清理所有构建文件
make clean-frontend   # 清理前端构建文件
make clean-backend    # 清理后端缓存
```

## 🏗️ 后端开发

### 技术栈
- **框架**: FastAPI
- **数据库**: TinyDB (本地文件数据库)
- **文件监控**: Watchdog
- **配置管理**: PyYAML
- **日志**: Python logging + 自定义格式

### API 结构
```
/api/
├── /models          # AI 模式管理
├── /commands        # 命令管理
├── /rules           # 规则管理
├── /hooks           # 钩子管理
├── /roles           # 角色管理
├── /deploy          # 部署管理
└── /health          # 健康检查
```

### 添加新 API 端点
1. 在 `app/models/schemas.py` 中定义数据模型
2. 在 `app/core/` 中实现业务逻辑服务
3. 在 `app/routers/` 中创建路由
4. 在 `app/routers/__init__.py` 中注册路由

### 开发技巧
- 使用 `make backend-dev` 启动开发服务器，支持热重载
- 查看 `logs/` 目录下的日志文件进行调试
- API 文档自动生成：http://localhost:8000/docs

## 🎨 前端开发

### 技术栈
- **框架**: React 18 + TypeScript
- **UI 库**: Ant Design
- **状态管理**: React Hooks
- **HTTP 客户端**: Axios
- **路由**: React Router

### 开发流程
1. 使用 `make frontend-dev` 启动开发服务器
2. 修改 `frontend/src/` 下的源文件
3. 浏览器会自动刷新显示更改

### 组件结构
```
frontend/src/
├── components/       # 通用组件
├── pages/           # 页面组件
├── services/        # API 服务
├── types/           # TypeScript 类型定义
├── utils/           # 工具函数
└── App.tsx          # 主应用组件
```

## 🧪 测试

### 后端测试
```bash
# 运行所有后端测试
make test-backend

# 运行特定测试文件
uv run pytest tests/test_specific.py -v

# 生成覆盖率报告
uv run pytest tests/ --cov=app --cov-report=html
```

### 前端测试
```bash
# 运行前端测试
make test-frontend

# 交互式测试模式
cd frontend && npm test

# 生成覆盖率报告
cd frontend && npm test -- --coverage
```

### 集成测试
```bash
# 运行前后端集成测试
make test-integration

# 或者直接运行脚本
uv run python test_integration.py
```

## 📦 部署

### 生产构建
```bash
# 构建前端和准备部署
make build

# 启动生产服务器
make run

# 完整部署流程
make deploy
```

### 配置管理
- 模式配置：`resources/models/*.yaml`
- 命令配置：`resources/commands/*.md`
- 规则配置：`resources/rules*/*.md`

### 生成配置文件
```bash
# 生成合并的模型配置
uv run python merge.py

# 查看生成的配置
ls -la custom_models.yaml
```

## 🐛 调试技巧

### 后端调试
- 查看日志：`tail -f logs/roo_api.log`
- 检查 API：`curl http://localhost:8000/api/health`
- 数据库状态：`ls -la data/`

### 前端调试
- 开发者工具：F12
- 网络请求：查看 Network 标签
- React 组件：使用 React Developer Tools

### 常见问题
1. **端口冲突**：使用 `lsof -i :8000` 检查端口占用
2. **依赖问题**：删除 `node_modules` 和 `.venv`，重新安装
3. **构建失败**：检查 Node.js 和 Python 版本

## 📚 开发规范

### 代码风格
- **Python**: 遵循 PEP 8，使用 Black 格式化
- **TypeScript**: 使用 Prettier 格式化
- **提交信息**: 遵循 Conventional Commits

### 提交流程
```bash
# 1. 创建功能分支
git checkout -b feature/amazing-feature

# 2. 提交更改
git commit -m "feat: 添加超级懒人功能"

# 3. 推送分支
git push origin feature/amazing-feature

# 4. 创建 Pull Request
```

## 🤝 贡献指南

1. **Fork** 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 确保所有测试通过：`make test`
5. 提交 Pull Request
6. 等待代码审查

## 📞 获取帮助

- 查看帮助：`make help`
- 项目信息：`make info`
- 系统检查：`make check`
- GitHub Issues：提交问题和建议

---

> 💡 **Remember**: 我们不是在偷懒，我们是在优化人类的工作方式！

*Happy Coding! 🚀*