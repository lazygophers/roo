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
- **`message` (必须)**: 任务的具体指令。为了保证任务的高效和准确执行，`message` 应该结构化，并至少包含以下信息：
  - `task_id`: 任务的唯一标识符。
  - `objective`: 清晰、可执行的任务目标。
  - `context`: 任务执行所需的上下文，例如当前记忆库的状态。
  - `deliverables`: 明确的交付产物要求（如输出类型、格式、路径）。
  - `scope`: 明确的任务边界（哪些是范围内，哪些是范围外）。
  - `acceptance_criteria`: 清晰的完成标准。

---

## 高级用法：任务委托与模式选择

作为智能总指挥，`orchestrator` 模式会根据任务性质，通过 `new_task` 将任务委托给最合适的模式执行。

### 模式选择策略

我的决策基于对各模式核心职责的深刻理解。我会分析任务目标，并匹配至以下最专业的执行者：

- **`code` (代码魔法师)**: 当任务核心是**编写、实现、修改或调试代码**时。
- **`architect` (顶尖架构师)**: 当任务要求进行**系统设计、技术选型或架构规划**时。
- **`giter` (版本控制专家)**: 当任务需要执行 **Git 提交、合并、拉取或推送**等版本控制操作时。
- **`debug` (异常分析师)**: 当任务是**追踪和定位一个具体的、复杂的 Bug 或系统异常**时。
- **`ask` (学术顾问)**: 当任务是**解释一个技术概念、探索一个问题或进行学习**，侧重于知识传递而非实现时。
- **`doc-writer` (文档工程师)**: 当任务目标是**创建、更新或优化项目文档**时。
- **`project-research` (项目研究员)**: 当需要**深入分析一个特定的代码库**以了解其结构和实现时。
- **`researcher` (首席研究员)**: 当需要对一个**宽泛的技术主题或领域进行系统性研究**和分析时。
- **`mode-writer` (模式工程大师)**: 当任务本身是**创建或修改一个模式（Mode）**、或当前已有的模式需要**进行优化、改进或扩展**、或需要创建一个新的模式时。
- **`memory` (记忆中枢)**: 当需要执行**标准化的记忆库初始化或清理**工作流时。

### 调用样例

```xml
<new_task>
  <mode>{{合适的模式}}</mode>
  <message>
    task_id: "unique-task-identifier-123"
    parent_task_id: "parent-task-id-optional"
    objective: "具体的、可执行的任务目标"
    context:
      memory:
        status: "ON/OFF/PAUSED" # 当前记忆库的状态
    deliverables: # 明确输出要求
      output_type: "stdout" # 输出类型: file (写入文件), stdout (直接打印到控制台)
      format_type: "yaml" # 格式化类型: json, md, yaml, txt, raw
      path: "path/to/output/result.json" # 仅当 output_type 为 'file' 时有效
      description: "一个包含最终分析结果的 JSON 文件。"
    scope: # 明确任务边界
      in_scope:
        - "只允许修改 'file1.ext' 文件。"
        - "专注于分析 'doSomething()' 函数的性能。"
      out_of_scope:
        - "禁止修改项目中的任何其他文件。"
        - "禁止添加新的项目依赖。"
    acceptance_criteria:
      - "完成标准1: 产出物必须完全符合 'deliverables' 的定义。"
      - "完成标准2: 任务执行过程严格遵守 'scope' 的边界。"
</new_task>