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
              task_id_list?: [string]
              category: string
              tags?: [string]
              assignee?: string
            execution_summary:
              start_time: string
              end_time: string
              duration: string
              mode_used: string
            results:
              deliverables: object
              changes_made?: [string]
              issues_resolved?: [string]
              performance_metrics?: object
              next_steps?: [string]
              lessons_learned?: [string]
          ```
      content_requirements:
        - "作为 attempt_completion 工具的 result 字段标准"
        - "标准 YAML 格式，2 空格缩进"
        - "时间字段 ISO 8601 格式"
        - "任务状态枚举值: completed/failed/partial"
        - "可选字段标记 '?:', 必填字段明确说明"
  </message>
  <todos>...</todos>
</new_task>
````

## 必填参数

- `mode`: 目标模式 slug
- `message`: 任务定义和响应格式
- `todos`: 子任务清单
