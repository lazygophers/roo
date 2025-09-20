---
name: git_commit
description: "Git 提交标准工作流 - 智能生成 Conventional Commits 规范提交"
category: "git"
scenario: "代码提交"
argument-hint: <scope>
---

# Git 提交标准工作流

## 工作流概述

智能分析代码变更，生成符合 Conventional Commits 规范的提交信息，确保提交历史清晰、规范。

## 工作流步骤

### 1. 代码变更分析

- 自动检测变更文件类型和范围
- 分析变更性质（新增、修改、删除）
- 识别影响的模块和功能

### 2. 提交类型判断

- **feat**: 新功能
- **fix**: Bug 修复
- **docs**: 文档更新
- **style**: 代码格式调整
- **refactor**: 代码重构
- **test**: 测试相关
- **chore**: 构建工具、辅助工具变动

### 3. 生成提交信息

- 格式: `type(scope): description`
- 自动生成简洁明了的描述
- 包含必要的上下文信息

## 执行方式

**委托模式**: `giter` 模式执行智能提交

**输入参数**:

- `scope`: 用户指定的影响范围（可选）
- 默认自动推断当前变更文件的范围
