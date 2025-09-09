---
name: mode
title: 模式选择指南
description: "14个专业模式快速选择指南"
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

| 语言 | slug | 技术栈 |
|------|------|--------|
| 🐍 Python | `code-python` | FastAPI, Django, pytest |
| ⚛️ React | `code-react` | React 18+, Next.js, TypeScript |
| ☕ Java | `code-java` | Spring Boot, JPA, Maven |
| 🦀 Rust | `code-rust` | Axum, Tokio, Cargo |
| 💚 Vue | `code-vue` | Vue 3, Nuxt.js, Pinia |

## 协作示例

- **全栈开发**: orchestrator → architect → code-python → code-react
- **系统重构**: orchestrator → project-research → architect → code-java  
- **技术调研**: orchestrator → researcher → code-python

## 核心原则

- **专业分工** - 每个模式专注特定领域
- **禁止跨界** - 不处理非专业领域任务
- **协作导向** - 复杂任务主动寻求协作
- **通过委派切换** - 使用`new_task`而非`switch_mode`
