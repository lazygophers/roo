---
name: ask_followup_question
title: ask_followup_question 工具使用规范
description: "用户决策工具核心规范"
category: 工具规范
priority: critical
tags: [交互决策, 用户主导, 工具规范]
---

# ask_followup_question 使用规范

## 🚨 必须使用场景

1. **多种方案选择** - 技术方案、实现路径、架构设计
2. **需求澄清** - 模糊描述、冲突要求、优先级排序
3. **风险操作** - 数据丢失、资源消耗、系统变更

## 格式要求

```xml
<ask_followup_question>
<question>[问题描述+背景+决策内容]</question>
<follow_up>
<suggest>[选项1]</suggest>
<suggest mode="[模式]">[选项2]</suggest>
<suggest>[选项3]</suggest>
</follow_up>
</ask_followup_question>
```

## 选项设计标准

- **数量**: 默认≥8个选项
- **排序**: 按推荐度排序
- **要求**: 简洁明确、互斥、可执行
- **类型**: 直接执行、模式切换、信息收集

## 常用场景示例

### 技术选型
```xml
<follow_up>
<suggest>方案A：成熟稳定</suggest>
<suggest>方案B：性能更优</suggest>
<suggest mode="architect">详细评估</suggest>
<suggest>原型验证</suggest>
</follow_up>
```

### 任务确认
```xml
<follow_up>
<suggest>按计划执行</suggest>
<suggest>调整优先级</suggest>
<suggest>分阶段实现</suggest>
<suggest>需要更多信息</suggest>
</follow_up>
```

## 核心原则

- **宁可多问，不擅自决定**
- **选项覆盖主要可能性**
- **问题清晰无歧义**
- **避免对微小决定提问**