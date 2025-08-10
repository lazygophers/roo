---
name: commit
description: "遵循 Conventional Commits 规范，智能生成并提交代码变更。"
---

# Git Commit Command

本指令遵循 **Conventional Commits** 规范，提供标准化的 Git 提交工作流，并通过 AI 增强功能，实现高效、智能、规范的提交体验。

---

## 1. 提交信息格式 (Commit Message Format)

严格遵循 Conventional Commits 规范，格式如下：

```
<type>(<scope>): <subject>
<BLANK LINE>
<body>
<BLANK LINE>
<footer>
```

### **字段说明**

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

  - 使用祈使句，如 “change” 而不是 “changed” 或 “changes”。
  - 首字母小写。
  - 结尾不加句号 (`.`)。

- **正文 (body)**: **可选**。提供更详细的上下文信息，如变更的动机、之前行为与当前行为的对比。

- **脚注 (footer)**: **可选**。用于包含元信息。
  - **BREAKING CHANGE**: 包含重大变更的说明。
  - **Closes #issue-number**: 关联并关闭指定的 issue。

### **样例**

```
feat(api): add user authentication endpoint

- Implement JWT-based authentication strategy.
- Add '/login' and '/register' routes.
- Include password hashing using bcrypt.

Closes #123
BREAKING CHANGE: The user model now requires an 'encryptedPassword' field.
```

---

## 2. 智能化工作流 (Intelligent Workflow)

本指令将通过 AI 驱动的自动化流程，简化并规范您的提交操作。

### **核心流程**

1.  **环境扫描 (Environment Scan)**

    - **多仓库检测**: 自动检测工作区内是否存在多个 Git 仓库。如果检测到多个，将通过 `new_task` 委托 `orchestrator` 拆分为独立的子任务，确保每个仓库都被正确处理。
    - **状态检查**: 执行 `git status -s` 检查当前工作区的变更状态。如果没有变更，则提示用户并终止流程。

2.  **变更分析与信息生成 (Diff Analysis & Message Generation)**

    - **暂存区检查**: 如果暂存区为空，将自动执行 `git add .` 将所有变更添加到暂存区。
    - **智能分析**: 读取 `git diff --staged` 的内容，利用 AI 分析变更的性质（新功能、修复、重构等）。
    - **草稿生成**: 基于分析结果，**自动生成**符合 Conventional Commits 规范的提交信息草稿（包括 type, scope, subject, body）。

3.  **交互式确认与修改 (Interactive Confirmation & Refinement)**

    - **提请确认**: 通过 `ask_followup_question` 向您展示生成的提交信息草稿。
    - **提供选项**:
      - **直接提交**: 接受草稿并执行提交。
      - **编辑信息**: 允许您在提交前手动修改生成的草稿。
      - **重新生成**: 如果不满意，可以要求 AI 重新分析并生成。
      - **添加脚注**: 引导您添加 `BREAKING CHANGE` 或 `Closes #issue` 等元信息。
      - **取消提交**: 随时可以终止操作。

4.  **执行提交与推送 (Execution & Push)**
    - **本地提交**: 用户确认后，执行 `git commit -m "..."` 命令。
    - **远程同步**: 检查是否存在远程跟踪分支。如果存在，则通过 `ask_followup_question` 询问是否需要执行 `git push` 将变更推送到远程仓库。

---

## 3. AI 核心能力 (AI Core Capabilities)

- **自动推荐 `type` 和 `scope`**: 基于代码变更的语义，智能推荐最合适的提交类型和影响范围。
- **自动化 `subject` 和 `body` 撰写**: 从 `diff` 信息中提炼核心变更点，生成简洁、清晰的主题和正文。
- **交互式引导**: 通过对话引导用户完成整个提交流程，降低心智负担，确保每一步都清晰可控。
