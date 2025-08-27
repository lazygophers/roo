---
name: commit-convention
title: Git 提交规范
description: "遵循 Conventional Commits 规范的 Git 提交信息格式和工作流指南"
category: rule
priority: high
tags: [Git, 提交规范, Conventional Commits, 工作流]
sections:
  - "提交信息格式：规范化的提交信息结构"
  - "Git 工作流：提交、同步、推送、合并等流程"
  - "AI 核心能力：智能生成提交信息、自动推荐类型和作用域"
---

# Git 提交规范 (Git Commit Convention)

> 遵循 Conventional Commits 规范的 Git 提交信息格式和工作流指南

## 1. 提交信息格式 (Commit Message Format)

严格遵循 Conventional Commits 规范，格式如下：

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### 字段说明

- **类型 (type)**: **必须**。用于说明提交的类别。
  - **feat**: 新功能 (feature)
  - **fix**: 修复 bug
  - **docs**: 文档变更
  - **style**: 代码风格、格式修复 (不影响代码逻辑)
  - **refactor**: 代码重构 (既不是新增功能，也不是修复 bug)
  - **perf**: 性能优化
  - **test**: 增加或修改测试
  - **build**: 影响构建系统或外部依赖的更改 (例如: gulp, broccoli, npm)
  - **ci**: 更改持续集成文件和脚本 (例如: Travis, Circle, BrowserStack, SauceLabs)
  - **chore**: 其他不修改 `src` 或 `test` 文件的更改
  - **revert**: 撤销之前的提交
- **作用域 (scope)**: **可选**。用于标识提交影响的范围 (如: `view`, `component`, `api`)。
- **主题 (subject)**: **必须**。简短描述提交目的，不超过 50 字符。
  - 使用祈使句，如 "change" 而不是 "changed" 或 "changes"。
  - 首字母小写。
  - 结尾不加句号 (`.`)。
- **正文 (body)**: **可选**。提供更详细的上下文信息，如变更的动机、之前行为与当前行为的对比。
- **脚注 (footer)**: **可选**。用于包含元信息。
  - **BREAKING CHANGE**: 包含重大变更的说明。
  - **Closes #issue-number**: 关联并关闭指定的 issue。

### 样例

```
feat(api): add user authentication endpoint

- Implement JWT-based authentication strategy.
- Add '/login' and '/register' routes.
- Include password hashing using bcrypt.

Closes #123
BREAKING CHANGE: The user model now requires an 'encryptedPassword' field.
```

---

## 2. 工作流 (Workflows)

### 提交变更 (Workflow: Commit)

**目标**: 将工作区的变更安全、规范地提交到本地仓库。

**执行步骤**:

1. **检查状态 (Status Check)**
   - 执行 `git status -s` 命令
   - 确认当前 Git 工作区的状态
   - 前置条件:
     - **多仓库检测**: 自动扫描工作区识别所有 Git 仓库
     - **无变更处理**: 如果工作区干净，流程自动终止
2. **暂存文件 (Staging Files)**
   - 检查暂存区状态
   - 如果暂存区为空但存在未暂存变更，自动执行 `git add .`
3. **生成提交信息 (Message Generation)**
   - 执行 `git diff --staged` 获取暂存变更的详细差异
   - AI 分析差异内容，理解变更的意图和性质
   - 基于代码变更智能生成符合规范的提交信息
   - 核心能力:
     - 自动推荐 `type` 和 `scope`
     - 自动化 `subject` 和 `body` 撰写
     - 多语言支持（优先简体中文）
4. **执行提交 (Executing Commit)**
   - 在确认提交信息后，执行 `git commit -m "<generated_message>"`
   - 将暂存的变更作为原子操作记录到本地仓库
5. **推送到远程仓库 (Pushing to Remote)**
   - 检查是否存在远程跟踪分支
   - 如果存在，自动执行 `git push`
   - 保持本地与远程的及时同步

### 同步远程更新 (Workflow: Pull)

**目标**: 将远程分支的最新变更同步到本地，并保持提交历史清晰。

**执行步骤**:

1. **检查状态**: 确保工作区是干净的
2. **执行拉取**: 使用 `git pull --rebase origin <current-branch>`（默认使用 rebase 策略）
3. **处理冲突**: 如果发生冲突，转入冲突处理流程

### 推送本地变更 (Workflow: Push)

**目标**: 将本地已经提交的变更安全地推送到远程仓库。

**执行步骤**:

1. **确认本地状态**: 确保所有需要推送的变更都已经提交
2. **执行推送**: 使用 `git push origin <current-branch>`
3. **处理推送失败**: 如果推送被拒绝，自动转入同步远程更新流程

### 合并分支 (Workflow: Merge)

**目标**: 将一个分支的变更安全地合并到另一个分支。

**执行步骤**:

1. **切换目标分支**: 使用 `git checkout <target-branch>`
2. **同步目标分支**: 执行同步远程更新确保目标分支为最新
3. **执行合并**: 使用 `git merge <source-branch>`
4. **处理冲突**: 如果发生冲突，转入冲突处理流程
5. **推送合并结果**: 合并成功后执行推送本地变更

### 冲突处理 (Workflow: Conflict Resolution)

**目标**: 在用户指导下，清晰、安全地解决合并或变基时产生的代码冲突。

**执行步骤**:

1. **立即停止**: 停止自动化操作，并向用户报告冲突
2. **识别冲突**: 运行 `git status` 并读取冲突文件，展示冲突详情
3. **请求决策**: 提供解决方案选项
   - 使用 '我们的' (theirs) 版本解决所有冲突
   - 使用 '他们的' (ours) 版本解决所有冲突
   - 列出冲突文件，手动解决
   - 中止本次操作
4. **执行解决**: 根据用户决策执行相应的 `git` 命令
5. **完成后续**: 在用户确认冲突解决后，继续执行被中断的工作流

---

## 3. AI 核心能力 (AI Core Capabilities)

- **自动推荐 `type` 和 `scope`**: 基于代码变更的语义，智能推荐最合适的提交类型和影响范围。
- **自动化 `subject` 和 `body` 撰写**: 从 `diff` 信息中提炼核心变更点，生成简洁、清晰的主题和正文。
- **交互式引导**: 通过对话引导完成整个提交流程，降低心智负担，确保每一步都清晰可控。
- **多语言支持**: 优先生成简体中文，支持中英文切换。
- **智能暂存**: 自动检测变更状态，智能处理暂存操作。
- **自动同步**: 在必要时自动执行推送操作，保持本地与远程仓库同步。
