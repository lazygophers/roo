---
name: uv
title: UV包管理工具指南
description: "下一代Python包管理工具完整指南，提供极速的包解析、安装和编译功能，是pip、pip-tools和virtualenv的直接替代品"
category: tool-guide
tool: uv
priority: high
tags: [Python, 包管理, uv, 虚拟环境]
sections:
  - "核心特性：极致性能、一体化工具链、pip兼容"
  - "核心工作流：虚拟环境、依赖管理、命令执行"
  - "高级应用：依赖锁定、同步、缓存管理"
  - "与传统pip工作流对比"
features:
  - "速度比pip快10-100倍"
  - "单个可执行文件处理所有任务"
  - "完全兼容pip API"
  - "内置全局缓存机制"
  - "基于Rust构建，高性能且内存安全"
workflows:
  - "创建环境：uv venv"
  - "添加依赖：uv add <package>"
  - "运行命令：uv run <command>"
  - "编译锁定：uv pip compile"
  - "同步环境：uv pip sync"
---

# uv：下一代 Python 包管理工具

> `uv` 是一个用 Rust 编写的、速度极快的 Python 包解析器、安装器、编译器和解析器。它旨在成为 `pip`、`pip-tools` 和 `virtualenv` 的直接替代品，提供一个统一、高效的工具链。

---

## 核心特性

- **⚡️ 极致性能**: `uv` 的速度非常快，在安装和解析依赖时，通常比 `pip` 和 `pip-tools` 快 **10-100 倍**。
- **📦 一体化工具链**: 单个可执行文件 `uv` 即可处理虚拟环境创建、依赖安装、锁定和同步等所有常见任务。
- **🤝 `pip` 兼容**: `uv` 提供了 `uv pip` 子命令，与 `pip` 的 API 完全兼容，可以无缝集成到现有项目中。
- ** caching**: 内置全局缓存机制，避免重复下载包，进一步提升安装速度。
- **🦀 Rust 构建**: 基于 Rust 的高性能和内存安全特性，保证了工具的稳定性和可靠性。

---

## 🚀 核心工作流：从零到一

本节将引导你完成 `uv` 最推荐的现代化工作流，该工作流以 `pyproject.toml` 为核心，实现声明式的依赖管理。

### 1. 什么是虚拟环境？

> **虚拟环境**是一个独立的 Python 运行环境，它允许你为每个项目安装不同版本的包，而不会相互干扰。这是 Python 开发的最佳实践。

使用 `uv` 创建和激活虚拟环境非常简单：

```bash
# 在当前目录下创建一个名为 .venv 的虚拟环境
uv venv

# 激活虚拟环境 (只需执行一次)
# macOS / Linux
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 2. 什么是依赖管理？

> **依赖管理**是指声明、安装和维护项目所需外部库（包）的过程。`uv` 推荐使用 `pyproject.toml` 文件来集中管理这些依赖。

使用 `uv add` 命令可以轻松地向 `pyproject.toml` 添加并安装依赖：

```bash
# 更新虚拟环境
uv sync

# 添加一个生产依赖 (例如：fastapi)
# uv 会自动更新 pyproject.toml 并将其安装到 .venv
uv add fastapi

# 添加一个仅在开发时使用的依赖 (例如：pytest)
uv add pytest --dev

# 移除一个依赖
uv remove fastapi
```

**`pyproject.toml` 示例：**

`uv add` 命令会自动维护 `[project.dependencies]` 和 `[project.optional-dependencies.dev]` 这两个部分。

```toml
[project]
name = "my-project"
version = "0.0.1"
dependencies = [
    "rich",
]

[project.optional-dependencies]
dev = [
    "pytest",
]
```

### 3. 如何在环境中执行命令？

> **工作流**是指在虚拟环境中执行代码、运行测试等一系列操作。`uv run` 可以在不手动激活环境的情况下，直接在虚拟环境中执行命令。

```bash
# 在 .venv 环境中运行一个 Python 脚本
uv run python my_script.py

# 在 .venv 环境中运行测试
uv run pytest
```

---

## 🛠️ 高级应用与 Pip 兼容性

`uv` 完全兼容传统的 `requirements.txt` 工作流，并提供了一些强大的高级功能。

### 依赖锁定与同步

- **编译 (Compile)**: 将 `pyproject.toml` 或 `requirements.in` 中的高级依赖解析为具体的、可复现的 `requirements.txt` 文件。
  ```bash
  # 从 pyproject.toml 生成 requirements.txt
  uv pip compile pyproject.toml -o requirements.txt
  ```
- **同步 (Sync)**: 确保当前虚拟环境中的包与 `requirements.txt` 文件**完全一致**，不多不少。
  ```bash
  # 根据 requirements.txt 同步环境
  uv pip sync requirements.txt
  ```

### 缓存管理

`uv` 使用全局缓存来加速重复安装。

```bash
# 清理不再使用的缓存条目
uv cache clean
```

### 与 Pip 的工作流对比

下表清晰地展示了 `uv` 的现代化工作流与传统 `pip` 工作流的命令差异。

| 任务场景          | ✅ `uv` 现代化工作流 (`pyproject.toml`)     | 兼容 `pip` 的工作流 (`requirements.txt`)   |
| ----------------- | ------------------------------------------- | ------------------------------------------ |
| **创建环境**      | `uv venv`                                   | `python -m venv .venv`                     |
| **安装/添加依赖** | `uv add <pkg>`                              | `uv pip install <pkg>`                     |
| **从文件安装**    | `uv pip sync requirements.txt`              | `uv pip install -r requirements.txt`       |
| **锁定依赖**      | `uv pip compile pyproject.toml -o reqs.txt` | `uv pip freeze > requirements.txt`         |
| **执行命令**      | `uv run <cmd>`                              | `source .venv/bin/activate` 后执行 `<cmd>` |
