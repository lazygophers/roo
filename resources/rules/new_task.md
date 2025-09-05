---
name: new_task
title: new_task 委派规范
description: "定义 new_task 工具的消息格式规范，包含任务定义、执行边界和响应要求"
category: rule
tags: [任务委派, 消息格式, 规范]
---

# new_task 委派规范

## 工具参数

````xml
<new_task>
  <mode>模式 slug</mode>
  <message>
    metadata:
      task_id?: string
      task_id_list?: [string]
      category: string
      tags?: [string]
      assignee?: string
    task:
      description: string
      context:
        reason: string
        relevant_files?: [string]
        user_persona?: string
      requirements:
        functional?: [string]
        non_functional?: [string]
      boundaries:
        allowed_files?: [string]
        disallowed_patterns?: [string]
      acceptance:
        criteria?: [string]
    response:
      format:
        required_sections: ["task_status", "completion_time", "context_info"]
        template: |
          ```yaml
          task_status: string
          completion_time: string
          context_info:
            metadata:
              task_id: string
              category: string
            execution_summary:
              start_time: string
              end_time: string
              duration: string
          results:
            deliverables: object
            next_steps?: [string]
            lessons_learned?: [string]
          ```
      content_requirements:
        - "必须使用标准 yaml 格式"
        - "保持缩进一致"
        - "所有字段必须有清晰的描述"
  </message>
  <todos>...</todos>
</new_task>
````

**必填参数**：

- `mode`: 目标模式 slug
- `message`: 任务定义和响应格式
- `todos`: 子任务清单

## 模式选择指南

### 核心模式总览

| 模式              | 职责                     | 适用任务                       |
| ----------------- | ------------------------ | ------------------------------ |
| `orchestrator`    | 系统级任务调度与决策中枢 | 复杂任务分解、多模式协作       |
| `architect`       | 系统架构与技术选型专家   | 架构设计、技术栈选型、重构规划 |
| `code` / `code-*` | 多语言代码实现与优化专家 | 功能开发、代码重构、测试编写   |
| `debug`           | 问题诊断与调试专家       | Bug 追踪、性能分析、错误修复   |
| `doc-writer`      | 文档创作与维护专家       | API 文档、技术文档、用户手册   |
| `ask`             | 知识解释与技术教学专家   | 概念解释、技术原理、学习指导   |

### 任务类型匹配

| 任务类型   | 推荐模式          | 特征                                   |
| ---------- | ----------------- | -------------------------------------- |
| 系统级任务 | `orchestrator`    | 需要分解为多个子任务，涉及多个专业领域 |
| 架构设计   | `architect`       | 系统架构设计、技术栈选型、重构规划     |
| 代码实现   | `code` / `code-*` | 功能开发、代码重构、测试编写、Bug 修复 |
| 问题诊断   | `debug`           | Bug 追踪、性能分析、错误修复           |
| 文档相关   | `doc-writer`      | API 文档生成、技术文档编写、用户手册   |
| 知识获取   | `ask`             | 概念解释、技术原理说明、学习路径规划   |

## 协作流程

### 标准协作流程

1. **任务接收** → `orchestrator`：分析任务复杂度，识别所需专业领域
2. **任务分解** → `orchestrator`：创建子任务清单，确定依赖关系，分配执行模式
3. **专业执行** → 各专业模式：按领域执行，必要时模式间协作
4. **结果汇总** → `orchestrator`：收集结果，验证完成度，准备交付
