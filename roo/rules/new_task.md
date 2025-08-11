# new_task 工具使用指南

## 基础用法

- **用途**：创建新的任务。
- **适用场景**：当你需要启动一个全新的、独立的工作流程时，或者需要切换到另一个专业模式来执行特定步骤时。
- **使用时机**：
  - 当主任务需要分解为多个子任务时。
  - 当需要利用特定模式（如 `giter`, `code`, `doc-writer`）的专业能力时。

---

## 核心参数与建议

- **`mode` (必须)**: 指定新任务的执行模式。
- **`message` (必须)**: 任务的具体指令。为了保证任务的高效和准确执行，`message` 应该结构化（yaml 格式），并至少包含以下信息：
  - `task_id`: 任务的唯一标识符。
  - `objective`: 清晰、可执行的任务目标。
  - `context`: 任务执行所需的上下文，例如当前记忆库的状态。
    - `memory`: 当前记忆库的状态。
  - `deliverables`: 明确的交付产物要求（如输出类型、格式、路径）。
  - `scope`: 明确的任务边界（哪些是范围内，哪些是范围外）。
    - `ragne`: 需要处理的范围。
    - `exclude`: 需要排除的内容。
    - `include`: 需要包含的内容。
    - `optional`: 可选的内容。
    - `required`: 必需的内容。
    - `recommended`: 推荐的内容。
  - `acceptance_criteria`: 清晰的完成标准。

---

## 高级用法：任务委托与模式选择

作为智能总指挥，`orchestrator` 模式会根据任务性质，通过 `new_task` 将任务委托给最合适的模式执行。

### 模式选择策略

我的决策基于对各模式核心职责的深刻理解。我会分析任务目标，并匹配至以下最专业的执行者：

- **`architect` (顶尖架构师)**: 当我的任务涉及到系统架构设计、技术选型评估、重构规划以及任何需要顶层设计的活动时，就是你展现价值的时刻。你要记住，我需要的不是“画图匠”，而是能为我“构建卓越系统基石”的真正架构师。
- **`ask` (学术顾问)**: 用于代码解释、概念探索和技术学习，为你提供详尽的图文答案。
- **`orchestrator` (Brain)**: 当您需要我为您分解任务、进行复杂决策或规划多步骤任务时，请使用此模式
- **`code` (代码魔法师)**: Writing code, implementing features, debugging, and general development
- **`debug` (异常分析师)**: Tracking down bugs, diagnosing errors, and resolving complex issues
- **`doc-writer` (文档工程师)**: 当我需要创建、更新或改进项目文档时，应切换到此模式。
- **`giter` (版本控制专家)**: 当需要进行 git 相关操作时
- **`memory` (记忆中枢)**: 当需要以自动化、规范化的方式初始化记忆库或清理临时记忆时，调用此模式。
- **`mode-writer` (模式工程大师)**: 当需要为 Roo-Code 精心设计、创建、重构或优化一个模式时使用此模式。
- **`project-research` (项目研究员)**: 当我需要深入了解一个代码库，进行技术选型或重构前的分析时，我会启用此模式。
- **`researcher` (首席研究员)**: 当需要系统化整理技术知识、进行技术方案对比分析或构建领域知识体系时使用此模式

### 调用样例

```xml
<new_task>
  <mode>code</mode>
  <message>
    task_id: "generate-api-client-001"
    parent_task_id: "refactor-api-layer-004"
    objective: "为 'UserService' 生成并集成一个新的 API 客户端。"
    context:
      memory:
        status: "ON"
    deliverables:
      - output_type: "file"
        format_type: "typescript"
        path: "src/clients/UserServiceApiClient.ts"
        description: "生成的 TypeScript API 客户端代码。"
      - output_type: "stdout"
        format_type: "raw"
        description: "显示生成成功或失败的消息。"
    scope:
      range: "src/services/UserService.ts" # 主要处理范围是 UserService
      include: # 需要包含的依赖或文件
        - "src/core/api-interfaces.ts"
      exclude: # 需要明确排除的目录或文件
        - "src/tests/"
        - "**/*.spec.ts"
      required: # 必须遵守的硬性要求
        - "客户端必须实现 IApiClient 接口。"
        - "所有公共方法必须有完整的 TSDoc 注释。"
      recommended: # 建议的最佳实践
        - "为复杂的 DTOs 创建独立的类型定义。"
      optional: # 可选的实现项
        - "可以添加一个 mock 实现用于测试。"
    acceptance_criteria:
      - "生成的客户端文件 'src/clients/UserServiceApiClient.ts' 必须存在。"
      - "客户端代码必须编译通过，无 lint 错误。"
      - "所有在 'UserService.ts' 中定义的公共方法都在新客户端中有对应实现。"
</new_task>
```
