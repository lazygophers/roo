---
name: merge_request
description: "Merge Request 标准工作流 - GitLab 环境下的代码合并请求"
category: "git"
scenario: "代码合并"
argument-hint: <target_branch>
---

# Merge Request 标准工作流

## 工作流概述

在 GitLab 环境中创建标准化的 Merge Request，确保代码质量和团队协作流程的标准化。

## 工作流步骤

### 1. 分支状态检查

- 验证源分支基于最新的目标分支
- 检查分支命名约定（feature/xxx, hotfix/xxx, release/xxx）
- 确认本地变更已正确提交

### 2. 管道验证

- 触发 GitLab CI/CD 管道
- 验证单元测试和集成测试
- 检查代码质量门禁
- 确认安全扫描通过

### 3. MR 内容构建

- **标题规范**: `type(scope): 功能描述`
- **描述模板**: 变更说明、测试验证、影响评估
- **里程碑关联**: 链接相关 Issue 和 Epic
- **审查者指派**: 根据代码变更范围自动指派

### 4. 合并策略

- 选择合适的合并方式（merge commit、squash、rebase）
- 配置自动删除源分支
- 设置合并条件检查
- 验证目标分支保护规则

## 执行方式

**委托模式**: `giter` 模式执行 MR 创建

**输入参数**:

- `target_branch`: 目标合并分支（默认为 main/develop）
- 自动分析变更内容和影响范围

## 质量保证

- 所有管道检查必须通过
- 代码审查完成且批准
- 合并冲突已解决
- 文档更新完整

## GitLab 特性

- 利用 GitLab CI/CD 集成
- 支持多级审批流程
- 自动化部署触发
- 变更追踪和回滚机制