---
name: new_task
title: new_task 委派规范
description: "定义 new_task 工具的消息格式规范，包含任务定义、执行边界和响应要求"
category: rule
tags: [任务委派, 消息格式, 规范]
---

# new_task 委派规范

## 工具参数说明

`new_task` 工具接受以下参数：

````xml
<new_task>
  <mode>模式 slug</mode>  <!-- 必填：目标模式的 slug，如 "code"、"architect" 等 -->
  <message>
    metadata:
      task_id?: string  # 唯一任务ID，格式: TASK-YYYY-NNN
      task_id_list?: [string]  # 父任务ID链
      category: string  # 必填: feature | bugfix | refactor | docs | research
      tags?: [string]  # 标签列表
      assignee?: string  # 指定的执行模式
    task:
      description: string  # 必填: 一句话描述任务目标
      context:
        reason: string  # 必填: 执行此任务的背景原因
        relevant_files?: [string]  # 相关文件路径
        user_persona?: string  # 用户角色
      requirements:
        functional?: [string]  # 功能需求
        non_functional?: [string]  # 非功能需求
      boundaries:
        allowed_files?: [string]  # 允许修改的文件
        disallowed_patterns?: [string]  # 禁止修改的模式
      acceptance:
        criteria?: [string]  # 验收标准
    response:
      format:
        required_sections:
          - "task_status"
          - "completion_time"
          - "context_info"
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
  <todos>
    ...  # 任务清单
  </todos>
</new_task>
````

**参数说明**：

- `mode`：必填，指定目标模式 slug（如 `code`、`architect`、`debug`）
- `message`：必填，包含任务定义和响应格式要求
- `todos`：必填，推荐子任务清单

## 标准 YAML 格式

````yaml
metadata:
  task_id?: string # 格式: TASK-YYYY-NNN
  category: string # feature | bugfix | refactor | docs | research
  tags?: [string]
  assignee?: string
task:
  description: string # 必填: 一句话描述任务目标
  context:
    reason: string # 必填: 执行背景原因
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
    required_sections:
      - "task_status"
      - "completion_time"
      - "context_info"
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
````

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

### 典型协作场景

**新功能开发**：

```
orchestrator → architect → code → debug → doc-writer
```

**系统重构**：

```
orchestrator → project-research → architect → code → giter
```

**问题排查**：

```
orchestrator → debug → code → ask → doc-writer
```

## 示例

### 基础示例 - 功能开发

```yaml
metadata:
  task_id: "TASK-2025-001"
  category: "feature"
  tags: ["api", "user-management"]
task:
  description: "为用户服务添加密码重置功能"
  context:
    reason: "用户反馈无法重置忘记的密码"
    relevant_files:
      - "src/services/user_service.py"
      - "tests/test_user_service.py"
  requirements:
    functional:
      - "发送密码重置邮件"
      - "验证重置令牌"
      - "更新用户密码"
    non_functional:
      - "令牌有效期1小时"
      - "邮件发送5分钟内"
  boundaries:
    allowed_files:
      - "src/services/user_service.py"
      - "tests/test_user_service.py"
  acceptance:
    criteria:
      - "邮件发送成功"
      - "令牌验证通过"
      - "密码更新成功"
response:
  format:
    required_sections:
      - "task_status"
      - "completion_time"
      - "context_info"
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
```

### 高级示例 - 架构重构

```yaml
metadata:
  task_id: "TASK-2025-002"
  category: "refactor"
  tags: ["architecture", "microservices"]
  assignee: "architect"
task:
  description: "将单体应用拆分为微服务架构"
  context:
    reason: "应用规模增长，单体架构难以维护"
    relevant_files:
      - "src/main.py"
      - "src/models/"
      - "src/services/"
  requirements:
    functional:
      - "识别服务边界"
      - "设计服务间通信"
      - "实现服务发现"
    non_functional:
      - "服务独立部署"
      - "故障隔离"
      - "水平扩展能力"
  boundaries:
    disallowed_patterns:
      - "直接数据库共享"
      - "紧耦合服务调用"
  acceptance:
    criteria:
      - "服务响应时间<100ms"
      - "系统可用性>99.9%"
      - "部署时间<5分钟"
response:
  format:
    required_sections:
      - "task_status"
      - "completion_time"
      - "context_info"
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
```
