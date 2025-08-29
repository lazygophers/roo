# 项目基础配置

## 🛠️ 环境配置

### 虚拟环境
```yaml
venv_path: ".venv"
python_executables:
  - "uv python"
  - ".venv/bin/python"
```

### UV 包管理工具

| 操作 | 命令 | 说明 |
|------|------|------|
| 创建环境 | `uv sync` | 初始化虚拟环境并安装依赖 |
| 安装依赖 | `uv add <package>` | 添加新包到项目 |
| 运行程序 | `uv run <main.py>` | 在虚拟环境中执行脚本 |

### 网络请求工具

**curl 超时要求**：
- 所有 curl 命令必须设置超时时间（推荐 5 秒）
- 连接超时：`--connect-timeout 5`
- 总体超时：`--max-time 10`
- 示例：`curl --connect-timeout 5 --max-time 10 https://api.example.com`

### Makefile 优先使用

**通用指令原则**：
- 项目必须提供 [`Makefile`](Makefile)
- 所有通用指令应优先更新到 Makefile 中
- 禁止直接使用 `uv run` 等命令，应使用 `make <target>`
- Makefile 应包含常用操作：开发、测试、构建、部署等

**Makefile 目标示例**：
```makefile
# 开发环境
dev:
	uv run main.py

# 运行测试
test:
	uv run pytest

# 代码格式化
fmt:
	uv run ruff check --fix .
	uv run ruff format .

# 安装依赖
install:
	uv sync

# 构建项目
build:
	@echo "Building project..."
```

## 🏗️ 技术栈

### 主要技术
```yaml
languages:
  - python
  - vue

frameworks:
  backend: "fastapi"
  frontend: "vuepy"
  database: "tinydb"
```

## 📋 开发规范

### 质量要求
- **测试覆盖率**: ≥ 90%
- **代码质量**: 严格遵循代码规范
- **架构设计**: 合理的分层分包
- **开发方式**: 渐进式开发

### 开发流程
1. 实现最小化功能
2. 编写测试用例
3. 逐步扩展功能
4. 持续优化重构

## 🔒 决策授权

**必须获得用户授权的操作**:
- 更新任务清单
- 规划任务
- 确定任务执行顺序
- 确认技术方案

---

# 产品说明

## 📖 项目概述

这是一个帮助用户对多个 Roo Code 的规则配置进行自定义选择、组合的工具。

## 📁 目录结构

```
resources/
├── modes/                 # 模式配置目录
│   └── <mode-name>/       # 各模式配置
├── rules-<slug>/         # 模式特异性规则
├── rules/                 # 全局通用规则
└── hooks/                 # 钩子脚本
    ├── before.md          # 全局前置规则 ✨
    └── after.md           # 全局后置规则
```

## ⚙️ 功能特性

### 核心功能
- **自动索引**: 启动时扫描并生成数据库索引
- **实时监听**: 监听文件变化，自动更新索引
- **规则预览**: 选择后可预览规则内容
- **配置导出**: 支持导出配置文件

### 导出格式
- 参考文件: [`custom_mmodels.yaml`](custom_mmodels.yaml)
- 支持通过 Shell 指定配置导出内容
- 支持通过 Shell 指定配置生成规则