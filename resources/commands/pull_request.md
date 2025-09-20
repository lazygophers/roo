---
name: pull_request
description: "Pull Request 标准工作流 - 创建高质量的代码合并请求"
category: "git"
scenario: "代码合并"
argument-hint: <target_branch>
---

# Pull Request 标准工作流

## 工作流概述

创建标准化的 Pull Request，确保代码质量、文档完整性和团队协作效率。

## 工作流步骤

### 1. 分支准备检查

- 确保当前分支基于最新的目标分支
- 检查分支命名规范（feat/xxx, fix/xxx, refactor/xxx）
- 验证本地提交历史的清洁性

### 2. 代码质量验证

- 运行自动化测试套件
- 执行代码静态分析
- 检查代码覆盖率要求
- 验证构建流程无错误

### 3. PR 信息生成

- **标题格式**: `type(scope): 简明扼要的描述`
- **描述内容**: 包含变更摘要、测试计划、相关Issue链接
- **标签分类**: 自动添加适当的标签（feature、bugfix、enhancement等）

### 4. 审查准备

- 生成变更文件清单
- 标识潜在的风险点
- 准备演示或测试指导
- 设置合适的审查者

## 执行方式

**委托模式**: `giter` 模式执行 PR 创建

**输入参数**:

- `target_branch`: 目标合并分支（默认为 main/master）
- 自动检测变更范围和影响

## 质量标准

- PR 描述信息完整且准确
- 所有自动化检查通过
- 代码变更逻辑清晰
- 符合团队编码规范

## 协作流程

- 及时响应审查意见
- 保持 PR 规模适中
- 确保 CI/CD 流程通过
- 维护清晰的沟通记录