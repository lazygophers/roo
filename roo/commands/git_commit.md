---
name: git_commit
description: "遵循 Conventional Commits 规范，智能生成并提交代码变更。"
argument-hint: <scope>
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

## 2. 工作流 (Workflow)

本指令严格遵循在 `giter` 模式中定义的 `Commit` 工作流，通过一系列自动化和智能化的步骤，将工作区的变更安全、规范地提交到本地乃至远程仓库。

### **执行步骤 (Execution Steps)**

#### 1. **检查状态 (Status Check)**

- **动作**: 执行 `git status -s` 命令。
- **目的**: 确认当前 Git 工作区的状态，检查是否存在未跟踪、已修改或已暂存的文件。
- **前置条件**:
  - **多仓库检测**: 在执行任何操作前，会自动扫描工作区以识别所有 Git 仓库。如果发现多个，将通过 `new_task` 委托 `orchestrator` 模式，将对每个仓库的操作分解为独立的子任务。
  - **无变更处理**: 如果 `git status` 显示工作区是干净的（没有变更），流程将自动终止，并向您报告无需提交。

#### 2. **暂存文件 (Staging Files)**

- **动作**: 检查暂存区状态。
- **目的**: 确保所有需要提交的变更都已被纳入暂存区。
- **智能暂存**: 如果检测到暂存区为空，但工作目录中存在未暂存的变更，系统将自动执行 `git add .` 将所有当前变更添加到暂存区。

#### 3. **生成提交信息 (Message Generation)**

- **动作**:
  1.  执行 `git diff --staged` 获取所有暂存变更的详细差异。
  2.  AI 分析差异内容，理解变更的意图和性质。
- **目的**: 基于代码变更，**智能生成**一条完全符合 **Conventional Commits** 规范的提交信息。
- **核心能力**:
  - **自动推荐 `type` 和 `scope`**: 基于代码变更的语义，智能推荐最合适的提交类型和影响范围。
  - **自动化 `subject` 和 `body` 撰写**: 从 `diff` 信息中提炼核心变更点，生成简洁、清晰的主题和正文。
  - **多语言支持**: 优先生成**简体中文**，如果无法生成，则依次降级至**中文**和**英文**。
- **交互式确认**:
  - **提请审批**: 通过 `ask_followup_question` 向您展示生成的提交信息草稿，请求您的确认。
  - **提供丰富选项**:
    - **直接提交**: 接受草稿并立即执行。
    - **编辑信息**: 在提交前手动优化草稿。
    - **重新生成**: 如果对草稿不满意，可要求重新生成。
    - **添加脚注**: 引导您轻松添加 `BREAKING CHANGE` 或 `Closes #issue` 等元信息。
    - **取消操作**: 随时可以安全地中止提交流程。

#### 4. **执行提交 (Executing Commit)**

- **动作**: 在您确认提交信息后，执行 `git commit -m "<generated_message>"` 命令。
- **目的**: 将暂存的变更连同规范的提交信息，作为一个原子操作永久记录到本地仓库的版本历史中。

#### 5. **推送到远程仓库 (Pushing to Remote)**

- **动作**:
  1.  检查是否存在远程跟踪分支 (`remote tracking branch`)。
  2.  如果存在，则执行 `git push` 命令。
- **目的**: 将本地的最新提交同步到共享的远程仓库，使其对团队其他成员可见。
- **说明**: 此步骤是自动的，旨在保持本地与远程的及时同步，但仅在检测到有效的远程分支时触发。

---

## 3. AI 核心能力 (AI Core Capabilities)

- **自动推荐 `type` 和 `scope`**: 基于代码变更的语义，智能推荐最合适的提交类型和影响范围。
- **自动化 `subject` 和 `body` 撰写**: 从 `diff` 信息中提炼核心变更点，生成简洁、清晰的主题和正文。
- **交互式引导**: 通过对话引导我完成整个提交流程，降低心智负担，确保每一步都清晰可控。
