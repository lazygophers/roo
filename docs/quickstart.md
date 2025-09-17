# ⚡ LazyAI Studio 快速开始

> 5 分钟上手 LazyGophers 的 AI 智能工作室！

## 🚀 30 秒快速启动

```bash
# 一键安装并启动
make install && make run
```

访问 http://localhost:8000 开始使用！

## 📋 分步指南

### 1️⃣ 环境检查
```bash
make check
```
确保 Python 3.12+、Node.js 16+ 和 uv 已安装。

### 2️⃣ 安装依赖
```bash
make install
```
自动安装前端和后端所有依赖。

### 3️⃣ 启动应用

#### 生产模式（推荐）
```bash
make run
```
- 前端：http://localhost:8000/
- API：http://localhost:8000/docs

#### 开发模式
```bash
# 前端开发（热重载）
make frontend-dev   # 端口 3000

# 后端开发（集成前端）
make backend-dev    # 端口 8000
```

## 🎯 核心功能体验

### 1. AI 模式管理
- 访问配置管理界面
- 选择需要的 AI 模式（如 architect、code-python 等）
- 一键部署到 VS Code 扩展

### 2. 命令系统
12 个预置命令，让开发更懒人：
- `/git_commit` - 智能提交
- `/architect` - 架构设计  
- `/debug` - 系统调试
- `/python` - Python 开发
- `/react` - React 开发
- 更多命令...

### 3. 规则引擎
智能规则系统，为不同场景提供专门的 AI 行为指导。

## 🛠️ 常用命令

```bash
# 📦 依赖管理
make install           # 安装所有依赖
make clean             # 清理构建文件

# 🚀 启动服务
make run               # 生产模式
make dev               # 开发模式

# 🏗️ 构建部署
make build             # 构建前端
make deploy            # 部署应用

# 🧪 测试验证
make test              # 运行测试
make test-integration  # 集成测试

# 📚 帮助信息
make help              # 查看所有命令
make info              # 项目信息
```

## 🔧 故障排除

### 端口被占用
```bash
lsof -ti:8000 | xargs kill -9
make run
```

### 依赖问题
```bash
make clean
make install
```

### 前端构建失败
```bash
make clean-frontend
make frontend-install
make build
```

## 📚 进阶使用

- 📖 [完整开发指南](./DEVELOPMENT.md)
- 🐹 [LazyGophers 哲学](./LAZY_PHILOSOPHY.md)
- 🏢 [组织介绍](../.github/ORGANIZATION.md)

## 🤝 获取帮助

遇到问题？
1. 查看 `make help`
2. 阅读开发文档
3. 提交 GitHub Issue

---

> 🎉 **欢迎来到 LazyAI Studio！** 让 AI 替你思考，让工具替你工作！

*Happy Lazy Coding! 🛋️*