# 项目基础配置

## 🛠️ 环境配置

### 虚拟环境

```yaml
# 虚拟环境配置
venv_path: ".venv"
python_executables:
  - "uv python"
  - ".venv/bin/python"
```

### UV 包管理

| 操作 | 命令 | 功能说明 |
|------|------|----------|
| 创建环境 | `uv sync` | 初始化虚拟环境并安装所有依赖 |
| 添加依赖 | `uv add <package>` | 将新包添加到项目依赖 |
| 运行程序 | `uv run <main.py>` | 在虚拟环境中执行脚本 |

### 网络请求规范

**curl 超时配置**：
- 强制要求所有 curl 命令设置超时
- 连接超时：`--connect-timeout 5`
- 总体超时：`--max-time 10`
- 标准格式：`curl --connect-timeout 5 --max-time 10 <URL>`

### Makefile 规范

**核心原则**：
- 项目必须提供 [`Makefile`](Makefile)
- 通用操作必须通过 Makefile 执行
- 禁止直接使用 `uv run` 等命令
- **禁止直接使用 `python` 或 `pip` 命令**
- **所有 Python 相关操作必须通过 `uv` 命令或 Makefile 目标执行**
- Makefile 需包含：开发、测试、构建、部署等目标

**标准 Makefile 模板**：
```makefile
# 开发环境运行
dev:
	uv run main.py

# 执行测试套件
test:
	uv run pytest

# 代码格式化和检查
fmt:
	uv run ruff check --fix .
	uv run ruff format .

# 安装/更新依赖
install:
	uv sync

# 项目构建
build:
	@echo "Building project..."
```

## 🏗️ 技术栈

```yaml
# 核心技术栈
languages:
  - python    # 后端语言
  - vue       # 前端框架

frameworks:
  backend: "fastapi"    # 后端框架
  frontend: "vuepy"     # 前端框架
  database: "tinydb"    # 数据库
```

## 📋 开发规范

### 质量标准

- **测试覆盖率**: ≥ 90%
- **代码质量**: 严格遵循代码规范
- **架构设计**: 合理的分层分包
- **开发方式**: 渐进式开发

### 开发流程

1. 实现最小化功能（MVP）
2. 编写完整的测试用例
3. 逐步扩展功能特性
4. 持续优化和重构

## 🔒 决策授权

**必须获得用户明确授权的操作**：
- 更新任务清单
- 规划任务执行路径
- 确定任务优先级
- 确认技术方案选择

---

## 📖 产品说明

### 项目定位

帮助用户对多个 Roo Code 规则配置进行自定义选择、组合的工具。

### 目录结构

```
resources/
├── modes/                    # 模式配置目录
│   └── <mode-name>/          # 各模式具体配置
├── rules-<slug>/            # 模式特异性规则
├── rules/                   # 全局通用规则
└── hooks/                   # 钩子脚本
    ├── before.md            # 全局前置规则 ✨
    └── after.md             # 全局后置规则

# 其他重要目录
logs/                         # 日志文件目录
    ├── app.log              # 应用程序日志
    ├── error.log             # 错误日志
    └── access.log            # 访问日志

data/                         # 数据库文件目录
    ├── database.json         # TinyDB 数据库文件
    ├── backup/               # 数据库备份目录
    └── cache/                # 缓存数据目录

tests/                        # 测试文件目录
    ├── unit/                 # 单元测试
    ├── integration/          # 集成测试
    └── fixtures/             # 测试数据
```

### 核心功能

- **自动索引**：启动时扫描并生成数据库索引
- **实时监听**：监听文件变化，自动更新索引
- **规则预览**：选择配置后可预览完整规则内容
- **配置导出**：支持导出完整的配置文件

### 导出规范

- 参考模板：[`custom_mmodels.yaml`](custom_mmodels.yaml)
- 支持通过 Shell 指定导出内容范围
- 支持通过 Shell 生成定制化规则