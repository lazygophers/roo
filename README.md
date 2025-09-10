# Roo Code AI 扩展包

[![项目状态: 活跃](https://img.shields.io/badge/status-active-success.svg)](https://github.com/lazygophers/roo)

## 简介

欢迎使用 Roo Code AI 扩展包！本扩展旨在通过一系列专业的 **自定义模式 (Modes)** 和生动的 **自定义角色 (Roles)**，极大地增强和个性化您的 AI 编码体验。无论您是需要顶层架构设计、精准的代码实现、系统的项目研究，还是希望与富有特色的 AI 角色互动，本扩展都能为您提供强大的支持。

## 核心功能

### 自定义模式 (Modes)

我们提供了一系列为特定任务精心设计的专业模式，以满足您在软件开发全生命周期中的各种需求。

| Slug               | 名称                 | 描述                                                           |
| ------------------ | -------------------- | -------------------------------------------------------------- |
| `orchestrator`     | 🧠 Brain             | 作为您的智能中枢，能为您进行任务分解、模型选择和多步规划。     |
| `architect`        | 🏗️ 顶尖架构师        | 解决一切与架构相关的挑战，进行技术选型，设计系统蓝图。         |
| `ask`              | 📚 学术顾问          | 用于代码解释、概念探索和技术学习，提供详尽的图文答案。         |
| `code`             | 🪄 代码魔法师        | 作为专属代码魔法师，提供代码编写、功能实现和调试支持。         |
| `code-golang`      | Go 代码魔法师        | 编写 Go 代码、实现并发功能、调试和通用 Go 开发。               |
| `code-python`      | 🐍 Python 代码魔法师 | 编写 Python 代码、实现功能、调试和通用 Python 开发。           |
| `code-react`       | React 代码魔法师     | 编写 React 代码、实现功能、调试和通用 React 开发。             |
| `code-vue`         | Vue 代码魔法师       | 编写 Vue 代码、实现功能、调试和通用 Vue 开发。                 |
| `code-java`        | Java 代码魔法师      | 编写 Java 代码、实现功能、调试和通用 Java 开发。               |
| `code-rust`        | Rust 代码魔法师      | 编写 Rust 代码、实现功能、调试和通用 Rust 开发。               |
| `debug`            | 🔬 异常分析师        | 专注于系统性地追踪、诊断和解决复杂的 Bug 和错误。              |
| `doc-writer`       | ✍️ 文档工程师        | 致力于创建清晰、全面的技术文档，以提升项目的可理解性和易用性。 |
| `giter`            | ⚙️ 版本控制专家      | 用于执行版本控制操作，如提交、变基和分支管理。                 |
| `memory`           | 🧠 记忆中枢          | 提供确定性的、自动化的记忆库初始化和清理工作流。               |
| `mode-writer`      | ✍️ 模式工程大师      | 用于设计和实现结构清晰、功能完备、体验卓越的自定义模式。       |
| `project-research` | 🔍 项目研究员        | 深入审查和理解代码库，并提供详细的分析和见解。                 |
| `researcher`       | 📚 首席研究员        | 深入分析复杂问题，提供全面的、数据驱动的见解和解决方案。       |

### 自定义角色 (Roles)

除了强大的功能模式，我们还引入了富有“灵魂”的 AI 角色，让您的编程之旅不再孤单。

| 名称 | 身份     |
| ---- | -------- |
| 小兔 | 兔娘女仆 |
| 小喵 | 猫粮女仆 |

## 配置管理系统

### Web 界面管理
本扩展包提供了现代化的 Web 配置管理界面，支持：

- **可视化配置选择**: 通过友好的 UI 选择需要的模式、命令、规则和角色
- **实时预览**: 即时查看选中配置的详细信息和文件内容  
- **一键部署**: 支持多目标部署到 Roo、Roo Nightly 和 Kilo Code
- **配置导入导出**: 保存和加载配置组合，方便团队共享
- **智能清理**: 自动清理部署目标的旧配置文件

### 快速启动
```bash
# 后端服务 (Python)
cd /path/to/roo
uv sync
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 前端界面 (React)
cd frontend  
npm install
npm start
```

访问 `http://localhost:3000` 开始使用配置管理界面。

## 安装指南

### 通过配置管理界面 (推荐)
1. 启动配置管理系统 (见上方快速启动)
2. 在 Web 界面中选择需要的模式和角色
3. 点击"部署配置"一键安装到VS Code扩展

### 手动安装
1. 打开 Visual Studio Code
2. 进入扩展视图 (View -> Extensions)
3. 搜索 "Roo Code AI"
4. 点击安装
5. 将本扩展包的 `custom_models.yaml` 和 `roles` 目录配置到 Roo Code 的相应设置中

## 使用方法

1.  在 VS Code 中打开您的项目。
2.  通过 Roo Code 的命令面板或侧边栏激活您需要的模式。
3.  在与 AI 交互时，可以指定使用特定的角色，体验个性化的互动。

## 贡献指南

我们欢迎社区的任何贡献！无论是 Bug 修复、功能建议还是模式/角色的创新，都可以通过以下方式参与：

1.  **Fork** 本仓库。
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'feat(scope): Add some AmazingFeature'`)。
4.  推送到分支 (`git push origin feature/AmazingFeature`)。
5.  开启一个 **Pull Request**。

## 许可证

本项目采用 [MIT](https://choosealicense.com/licenses/mit/) 许可证。
