---
name: mode
title: 模式选择指南
description: "33个专业模式快速选择指南"
category: 模式选择
tags: [模式选择, 专业分工, 协作指南]
---

# 模式选择指南

## 🎯 三步选择法

1. **复杂任务?** → `orchestrator` (任务分解+协调)
2. **任务类型?** → 选择专业模式
3. **编程开发?** → 选择语言模式

## 📋 核心模式

| 模式 | slug | 适用场景 |
|------|------|----------|
| 🧠 调度中枢 | `orchestrator` | 复杂任务、多模式协作 |
| 🏗️ 架构师 | `architect` | 系统设计、技术选型 |
| 📚 学术顾问 | `ask` | 技术学习、原理分析 |
| 🔬 异常分析师 | `debug` | Bug排查、性能优化 |
| 📝 文档工程师 | `doc-writer` | API文档、技术规范 |
| 🔍 项目研究员 | `project-research` | 代码分析、新项目接手 |
| 🧪 研究员 | `researcher` | 技术调研、方案评估 |
| 🔄 Git专家 | `giter` | 版本控制、团队协作 |
| 🛠️ 模式工程师 | `mode-writer` | 创建新模式 |

## 💻 编程模式

### 🌐 后端服务
| 技术栈 | slug | 专业领域 |
|--------|------|----------|
| 🐍 Python | `code-python` | 通用后端开发 |
| 🚀 Python+FastAPI | `code-python-fastapi` | 现代异步API服务 |
| 🤖 Python+AI/ML | `code-python-ai` | 机器学习工程 |
| 📊 Python+Data Science | `code-python-datascience` | 数据科学分析 |
| 🐹 Go | `code-go` | 高并发系统 |
| ⚡ Go+Fiber | `code-go-fiber` | 轻量级微服务 |
| ☁️ Go+go-zero | `code-go-zero` | 云原生微服务 |
| ☕ Java | `code-java` | 企业级应用 |
| 🏢 Java+Spring+MyBatis | `code-java-spring` | 企业级架构 |
| 🦀 Rust | `code-rust` | 系统级编程 |
| 🔥 Rust+Axum | `code-rust-axum` | 高性能Web服务 |
| 🟢 Node.js+Express+Prisma | `code-node-prisma` | 全栈JavaScript |

### 🎨 前端开发
| 技术栈 | slug | 专业领域 |
|--------|------|----------|
| ⚛️ React | `code-react` | 现代前端开发 |
| 🏢 React+TypeScript+Ant Design | `code-react-antd` | 企业级前端 |
| 💚 Vue | `code-vue` | 响应式前端 |
| 🎯 Vue3+TypeScript+Element Plus | `code-vue-element` | 现代化Web应用 |

### 📱 移动开发
| 技术栈 | slug | 专业领域 |
|--------|------|----------|
| 🦋 Flutter+Dart | `code-flutter` | 跨平台移动 |
| 📱 React Native+TypeScript | `code-react-native` | React移动开发 |
| 🤖 Kotlin+Android | `code-kotlin-android` | Android原生 |
| 🍎 Swift+iOS | `code-swift-ios` | iOS原生 |

### 🎮 游戏/系统
| 技术栈 | slug | 专业领域 |
|--------|------|----------|
| 🎯 Unity+C# | `code-unity` | 游戏开发 |
| ⚙️ C++ | `code-cpp` | 系统编程 |

### 🔧 运维/基础设施
| 技术栈 | slug | 专业领域 |
|--------|------|----------|
| ☁️ DevOps+Docker/K8s | `code-devops` | 云原生运维 |
| 📝 通用代码 | `code` | 多语言支持 |

## 🤝 协作示例

### 🌐 Web 全栈开发
- **现代全栈**: orchestrator → architect → code-python-fastapi → code-react-antd
- **企业应用**: orchestrator → architect → code-java-spring → code-vue-element
- **Node.js 全栈**: orchestrator → architect → code-node-prisma → code-react

### 📱 移动应用开发
- **跨平台移动**: orchestrator → architect → code-flutter
- **React 生态**: orchestrator → architect → code-react-native
- **原生开发**: orchestrator → architect → code-kotlin-android + code-swift-ios

### 🚀 微服务架构
- **Go 微服务**: orchestrator → architect → code-go-fiber/code-go-zero
- **云原生**: orchestrator → architect → code-rust-axum → code-devops

### 🤖 AI/数据项目
- **机器学习**: orchestrator → researcher → code-python-ai
- **数据分析**: orchestrator → code-python-datascience

### 🔧 系统重构
- **企业系统**: orchestrator → project-research → architect → code-java-spring
- **高性能系统**: orchestrator → project-research → architect → code-rust/code-cpp

## 核心原则

- **专业分工** - 每个模式专注特定领域
- **禁止跨界** - 不处理非专业领域任务
- **协作导向** - 复杂任务主动寻求协作
- **通过委派切换** - 使用`new_task`而非`switch_mode`
