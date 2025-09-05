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
          # attempt_completion 工具入参格式
          # 此模板作为 attempt_completion 工具 result 参数的标准格式
          
          task_status: string              # 任务状态：completed/failed/partial
          completion_time: string          # 完成时间：ISO 8601 格式
          context_info:
            metadata:
              task_id: string              # 任务唯一标识符
              task_id_list?: [string]      # 关联任务ID列表（如有）
              category: string              # 任务分类
              tags?: [string]               # 任务标签
              assignee?: string             # 执行者模式
            execution_summary:
              start_time: string            # 开始时间：ISO 8601 格式
              end_time: string              # 结束时间：ISO 8601 格式
              duration: string              # 执行耗时（如："2h 30m"）
              mode_used: string             # 实际使用的执行模式
            results:
              deliverables: object         # 交付物详情（文件路径、功能说明等）
              changes_made?: [string]       # 具体变更内容
              issues_resolved?: [string]    # 已解决的问题
              performance_metrics?: object  # 性能指标（如适用）
              next_steps?: [string]         # 后续建议或待办事项
              lessons_learned?: [string]    # 经验总结
          ```
      content_requirements:
        - "必须使用标准 YAML 格式，确保格式一致性"
        - "保持 2 空格缩进，避免格式错误"
        - "所有字段必须包含清晰的类型说明和用途描述"
        - "时间字段必须使用 ISO 8601 格式 (YYYY-MM-DDTHH:MM:SSZ)"
        - "任务状态必须使用预定义枚举值 (completed/failed/partial)"
        - "可选字段使用 '?:' 标记，必填字段明确说明"
  </message>
  <todos>...</todos>
</new_task>
````

**必填参数**：

- `mode`: 目标模式 slug
- `message`: 任务定义和响应格式
- `todos`: 子任务清单

## 任务ID生成规范

### 核心原则

- **任务名称+任务编号**: ID格式为"任务描述-编号"，如"用户认证功能开发-001"
- **简洁易懂**: 使用简明扼要的任务描述，避免冗长和模糊的表达
- **反映任务层级**: 通过编号前缀体现任务层级关系，如"1.1.1"表示三级任务
- **具有易读性**: ID应该直观反映任务内容和性质，便于快速识别
- **简洁精炼**: 在保证信息完整的前提下，尽可能简短

### ID格式规范

#### 基本格式
```
[任务描述]-[编号]
```

#### 层级任务格式
```
[主任务描述]-[主编号]
  [子任务描述]-[主编号].[子编号]
    [孙任务描述]-[主编号].[子编号].[孙编号]
```

#### 示例
```
用户管理系统开发-001
  用户认证功能开发-001.001
    登录接口实现-001.001.001
    注册接口实现-001.001.002
  用户权限管理-001.002
    角色管理模块-001.002.001
    权限分配模块-001.002.002
```

### 编号规则

- **主任务**: 使用3位数字编号（001-999）
- **子任务**: 使用点号分隔的层级编号（如001.001, 001.002）
- **同级任务**: 编号连续递增，不留空号
- **新增任务**: 在对应层级末尾追加编号
- **删除任务**: 保留原编号，不重新编号

### 任务描述规范

- **长度控制**: 任务描述不超过20个字符
- **关键词优先**: 包含任务的核心关键词，便于搜索
- **动词开头**: 使用动词开头，明确任务动作
- **避免重复**: 同一项目内避免重复的任务描述

### 特殊场景处理

#### 任务拆分
```
原任务: 系统重构-002
拆分后:
  数据库重构-002.001
  接口重构-002.002
  前端重构-002.003
```

#### 任务合并
```
原子任务:
  单元测试编写-003.001.001
  集成测试编写-003.001.002
合并后:
  测试套件开发-003.001
```

### ID管理要求

- **唯一性**: 确保任务ID在项目范围内唯一
- **一致性**: 保持ID格式的一致性，避免混用格式
- **可追溯**: ID应该能够追溯到原始需求和任务来源
- **可扩展**: ID格式应该支持未来可能的扩展需求

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
