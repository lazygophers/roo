# LazyAI Studio

[![项目状态: 活跃](https://img.shields.io/badge/status-active-success.svg)](https://github.com/lazygophers/lazyai-studio)
[![组织: LazyGophers](https://img.shields.io/badge/org-LazyGophers-blue.svg)](https://github.com/lazygophers)
[![许可证: MIT](https://img.shields.io/badge/license-MIT-green.svg)](https://choosealicense.com/licenses/mit/)

> 🚀 **LazyGophers 出品** - 让 AI 开发更智能，让开发者更懒人！

## 简介

欢迎使用 **LazyAI Studio**！这是 LazyGophers 组织为懒人开发者精心打造的 AI 智能工作室。

我们的理念是：**让 AI 替你思考，让工具替你工作，让你做个聪明的懒人！** 🛋️

本项目通过一系列专业的 **智能模式 (Modes)**、**个性角色 (Roles)** 和 **便捷命令 (Commands)**，为您提供完整的 AI 开发解决方案。从顶层架构设计到精确代码实现，从项目研究到文档编写，LazyAI Studio 让复杂的开发工作变得简单而高效。

## 🐹 关于 LazyGophers

**LazyGophers** 是一个致力于为开发者提供智能开发工具的开源组织。我们相信：

- 🧠 **智能优于蛮力** - 用 AI 解决重复性工作
- 🛠️ **工具优于手工** - 让自动化处理琐碎任务  
- 😎 **高效优于忙碌** - 专注核心创造而非基础劳动
- 🎯 **简单优于复杂** - 复杂的问题需要简单的解决方案

我们的使命是让每个开发者都能成为"聪明的懒人" - 通过智能工具提升效率，将时间投入到真正重要的创新工作中。

### 组织项目

- 🏗️ **LazyAI Studio** - AI 智能工作室 (本项目)
- 🔧 **LazyDevOps** - 自动化运维工具链 (规划中)
- 📱 **LazyMobile** - 移动开发加速器 (规划中)
- 🌐 **LazyCloud** - 云服务管理平台 (规划中)

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

### 🚀 快速启动

#### 一键启动 (推荐)
```bash
# 安装依赖、构建前端、启动服务器
make install && make run
```
访问 `http://localhost:8000` 开始使用！

#### 开发模式
```bash
# 前端开发 (热重载)
make frontend-dev   # 访问 http://localhost:3000

# 后端开发 (集成前端)
make backend-dev    # 访问 http://localhost:8000
```

#### 手动启动
```bash
# 1. 安装依赖
make install

# 2. 构建前端
make build

# 3. 启动服务器
make run
```

### 📋 可用命令

LazyAI Studio 提供了完整的 Makefile 命令集，让开发更加懒人化：

```bash
# 📦 安装依赖
make install           # 安装所有依赖（前端+后端）
make backend-install   # 仅安装后端依赖
make frontend-install  # 仅安装前端依赖

# 🚀 启动服务
make run              # 构建并启动生产服务器
make dev              # 启动开发环境
make backend-dev      # 启动后端开发服务器
make frontend-dev     # 启动前端开发服务器

# 🏗️ 构建项目
make build            # 构建前端生产版本
make frontend-build   # 构建前端静态文件

# 🧪 运行测试
make test             # 运行所有测试
make test-backend     # 运行后端测试
make test-frontend    # 运行前端测试
make test-integration # 运行集成测试

# 🚀 部署项目
make deploy           # 部署到生产环境

# 🧹 清理文件
make clean            # 清理所有构建文件
make clean-frontend   # 清理前端构建文件
make clean-backend    # 清理后端缓存

# 🔍 其他工具
make check            # 检查系统环境
make info             # 显示项目信息
make help             # 显示帮助信息
```

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

## 🤝 加入 LazyGophers

欢迎所有认同"聪明的懒人"理念的开发者加入我们！

### 贡献方式
- 🐛 **发现 Bug** - 帮助我们发现和修复问题，让工具更可靠
- ✨ **提升功能** - 添加让开发者更懒的新特性
- 🎭 **设计角色** - 创造有趣的 AI 角色，让编程更有温度
- 🧠 **优化模式** - 改进现有模式，提升 AI 辅助效果
- 📖 **完善文档** - 让更多懒人能够快速上手

### 贡献流程
1. **Fork** 本仓库
2. 创建您的懒人分支 (`git checkout -b feature/SuperLazyFeature`)
3. 提交更改 (`git commit -m 'feat: 添加超级懒人功能'`)
4. 推送到分支 (`git push origin feature/SuperLazyFeature`)
5. 开启 **Pull Request** 并描述您的懒人创新

### 行为准则
- 🎯 **效率至上** - 代码要解决实际问题，提升开发效率
- 🧠 **AI 优先** - 优先考虑 AI 和自动化解决方案  
- 😊 **友善交流** - 保持开放和友善的社区氛围
- 📚 **持续学习** - 分享经验，共同成长为更智能的懒人

## 许可证

本项目采用 [MIT](https://choosealicense.com/licenses/mit/) 许可证。
