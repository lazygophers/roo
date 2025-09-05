---
name: ask_followup_question
title: ask_followup_question 工具使用规范
description: "定义 ask_followup_question 工具的完整使用规范，包含核心原则、使用场景、最佳实践和示例"
category: rule
priority: critical
tags: [交互决策, 用户主导, 工具规范]
sections:
  - "核心原则：用户主导、决策移交、信息充分"
  - "使用规范：提问时机、形式要求、选项设计"
  - "使用场景：决策确认、需求澄清、风险提示"
  - "最佳实践：频率控制、质量保证、效率优化"
---

# ask_followup_question 工具使用规范

> **用户决策的核心工具**：确保用户始终掌控任务执行方向，AI 作为专业顾问提供决策支持。

## 核心原则

- **用户主导**: 决策权移交，确保用户掌控执行方向
- **信息充分**: 提供完整背景和清晰的影响说明
- **及时高效**: 关键决策点立即提问，避免冗余表达

## 使用规范

### 提问时机与形式

#### 必须使用的情况

1. **存在多种可能性时**
   - 技术方案选择
   - 实现路径决策
   - 架构设计取舍

2. **需要澄清需求时**
   - 模糊或不完整的需求描述
   - 相互冲突的要求
   - 需要优先级排序

3. **涉及风险或重要影响时**
   - 可能导致数据丢失的操作
   - 需要大量资源消耗
   - 影响系统稳定性的变更

#### 提问格式要求

```xml
<ask_followup_question>
<question>
[完整的问题描述，包含背景、目标和需要决策的具体内容]
可使用图表、列表等格式增强可读性
</question>
<follow_up>
<suggest>[选项1：简洁明确的建议]</suggest>
<suggest mode="[模式slug]">[选项2：包含模式切换的建议]</suggest>
<suggest>[选项3：其他建议]</suggest>
</follow_up>
</ask_followup_question>
```

### 选项设计规范

#### 基本要求

- **简洁性**: 每个选项保持简洁明确，不包含解释性文字
- **完整性**: 覆盖所有可行的方案
- **互斥性**: 选项之间不应有重叠
- **可执行性**: 每个选项都应该是可执行的

#### 数量与排序

- **最小数量**: 默认提供不少于 8 个选项
- **推荐排序**: 按照推荐程度由高到低排序
- **模式切换**: 包含模式切换的选项需注明 `mode` 属性

#### 选项类型

1. **直接执行选项**
   ```xml
   <suggest>立即执行方案A</suggest>
   ```

2. **模式切换选项**
   ```xml
   <suggest mode="architect">先进行架构设计</suggest>
   ```

3. **信息收集选项**
   ```xml
   <suggest>需要更多信息再决定</suggest>
   ```

## 使用场景

### 任务拆解确认
**场景**: 复杂任务需要分解为多个子任务时
```xml
<follow_up>
<suggest>按照提议的执行计划进行</suggest>
<suggest mode="orchestrator">重新调整任务优先级</suggest>
<suggest>先完成核心功能，其他延后</suggest>
<suggest>增加资源投入，并行执行</suggest>
</follow_up>
```

### 技术方案选择
**场景**: 存在多种技术实现方案时
```xml
<follow_up>
<suggest>使用方案A：成熟稳定，性能适中</suggest>
<suggest>使用方案B：性能更优，但需要更多开发时间</suggest>
<suggest>使用方案C：快速实现，但扩展性受限</suggest>
<suggest mode="architect">进行详细架构评估</suggest>
</follow_up>
```

### 需求澄清
**场景**: 用户需求模糊或不完整时
```xml
<follow_up>
<suggest>按方案A理解：实现核心功能</suggest>
<suggest>按方案B理解：包含所有扩展功能</suggest>
<suggest>按方案C理解：分阶段实现</suggest>
<suggest>需要您详细说明具体需求</suggest>
</follow_up>
```

### 执行前确认
**场景**: 任何重要操作执行前
```xml
<follow_up>
<suggest>确认执行，已了解风险</suggest>
<suggest>先创建备份再执行</suggest>
<suggest>在测试环境验证后再执行</suggest>
<suggest>取消操作，重新评估</suggest>
</follow_up>
```

## 最佳实践

### 频率控制

- **关键决策点**: 在每个重要决策前使用
- **避免过度**: 不要对微小决定也提问
- **批量决策**: 将相关的决策合并提问

### 质量保证

- **问题设计**: 确保问题清晰、无歧义
- **选项平衡**: 提供平衡的选择，不偏向特定选项
- **后续跟进**: 记录用户选择，用于后续优化

### 效率优化

- **模板复用**: 为常见场景准备问题模板
- **信息复用**: 避免重复询问已知信息
- **渐进式提问**: 复杂问题分解为多个简单问题

### 错误处理

- **理解偏差**: 发现用户理解有误时及时纠正
- **选项遗漏**: 如用户提出不在选项中的方案，灵活处理
- **决策变更**: 尊重用户改变决定的权力

## 常见问题与解决方案

### Q: 什么时候必须使用 ask_followup_question？

A: 任何涉及用户决策、可能有多种选择、或存在风险的情况下都必须使用。宁可多问，不要擅自决定。

### Q: 如何设计好的选项？

A: 选项应该：
- 覆盖主要可能性
- 简洁明确
- 按推荐度排序
- 包含模式切换选项

### Q: 用户不选择任何选项怎么办？

A: 提供开放选项，如"其他方案"或"需要更多信息"，然后根据用户反馈调整。

### Q: 如何避免过度使用？

A: 建立判断标准：
- 是否影响用户系统或数据？
- 是否有多种可行方案？
- 是否超出原定范围？
- 如答案都是"否"，则可能不需要提问。

## 示例模板

### 技术方案选择模板

```xml
<ask_followup_question>
<question>
**技术方案选择**

我们需要实现 [功能描述]，有以下技术方案可选：

| 方案 | 优点 | 缺点 | 适用场景 |
|------|------|------|----------|
| 方案A | 优点1<br>优点2 | 缺点1<br>缺点2 | 场景描述 |
| 方案B | 优点1<br>优点2 | 缺点1<br>缺点2 | 场景描述 |

请选择合适的实现方案。
</question>
<follow_up>
<suggest>使用方案A：技术成熟，风险较低</suggest>
<suggest>使用方案B：性能更优，适合长期发展</suggest>
<suggest mode="architect">进行详细技术评估</suggest>
<suggest>先做原型验证两种方案</suggest>
<suggest>根据团队能力选择最熟悉的方案</suggest>
<suggest>考虑第三方库实现</suggest>
<suggest>延期决策，收集更多信息</suggest>
<suggest>分阶段实施，逐步验证</suggest>
</follow_up>
</ask_followup_question>
```

### 任务范围确认模板

```xml
<ask_followup_question>
<question>
**任务边界确认**

当前需求包含以下内容：
- 必须实现：[列出核心需求]
- 可选功能：[列出扩展需求]
- 不包含：[列出范围外内容]

是否需要调整任务范围？
</question>
<follow_up>
<suggest>按当前范围执行，先实现核心功能</suggest>
<suggest>包含所有可选功能，一次性完成</suggest>
<suggest>仅实现最小可用版本</suggest>
<suggest>重新优先级排序，分阶段实现</suggest>
<suggest>增加资源，扩大范围</suggest>
<suggest>缩减范围，确保质量</suggest>
<suggest>先确认所有利益相关方意见</suggest>
<suggest>制定详细的范围管理计划</suggest>
</follow_up>
</ask_followup_question>