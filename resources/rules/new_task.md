---
name: new_task
title: new_task 委派规范
description: "定义 new_task 工具的消息格式规范，包含任务定义、执行边界和响应要求"
category: rule
tags: [任务委派, 消息格式, 规范]
---

# new_task 委派规范

## 工具参数说明

`new_task` 工具接受以下参数：

```xml
<new_task>
  <mode>模式 slug</mode>  <!-- 必填：目标模式的 slug，如 "code"、"architect" 等 -->
  <message>
    metadata:
      # 元数据部分
      task_id?: string  # 唯一任务ID，格式: TASK-YYYY-NNN
      task_id_list?: [string]  # 父任务ID链
      category: string  # 必填: feature | bugfix | refactor | docs | research
      tags?: [string]  # 标签列表
      assignee?: string  # 指定的执行模式
      dependencies?: [string]  # 依赖的任务ID列表
    task:
      # 任务定义部分
      description: string  # 必填: 一句话描述任务目标
      context:
        reason: string  # 必填: 执行此任务的背景原因
        relevant_files?: [string]  # 相关文件路径
        user_persona?: string  # 用户角色
      requirements:
        functional?: [string]  # 功能需求
        non_functional?: [string]  # 非功能需求
      boundaries:
        allowed_files?: [string]  # 允许修改的文件
        disallowed_patterns?: [string]  # 禁止修改的模式
      acceptance:
        criteria?: [string]  # 验收标准
    response:
      # 响应格式部分
      format:
        structure:
          required_sections:
            - "task_status"
            - "completion_time"
            - "context_info"
          template: |
            ```yaml
            task_status: string
            completion_time: string
            context_info:
              metadata:
                task_id: string
                category: string
              execution_summary:
                start_time: string
                end_time: string
                duration: string
            results:
              deliverables: object
              next_steps?: [string]
              lessons_learned?: [string]
            ```
      content_requirements:
        - "必须使用标准 yaml 格式"
        - "保持缩进一致"
        - "所有字段必须有清晰的描述"
  </message>
  <todos>
    ...  # 任务清单
  </todos>
</new_task>
```

**参数说明**：

- `mode`：必填参数，指定要委派的目标模式，只能填写模式的 slug（如 `code`、`architect`、`debug` 等）
- `message`：必填参数，包含任务定义和返回要求的完整消息内容
  - **确保 yaml 格式正确、缩进正确**
- `todos`：必填参数，推荐的子任务清单，供子任务参考执行

## 单一 YAML 格式设计

**整体结构**:

```yaml
metadata:
  # 元数据部分
  task_id?: string # 唯一任务ID，格式: TASK-YYYY-NNN
  task_id_list?: [string] # 父任务ID链
  category: string # 必填: feature | bugfix | refactor | docs | research
  tags?: [string] # 标签列表
  assignee?: string # 指定的执行模式
  dependencies?: [string] # 依赖的任务ID列表
task:
  # 任务定义部分
  description: string # 必填: 一句话描述任务目标
  context:
    reason: string # 必填: 执行此任务的背景原因
    relevant_files?: [string] # 相关文件路径
    user_persona?: string # 用户角色
  requirements:
    functional?: [string] # 功能需求
    non_functional?: [string] # 非功能需求
  boundaries:
    allowed_files?: [string] # 允许修改的文件
    disallowed_patterns?: [string] # 禁止修改的模式
  acceptance:
    criteria?: [string] # 验收标准
response:
  # 响应格式部分
  format:
    structure:
      required_sections:
        - "task_status"
        - "completion_time"
        - "context_info"
      template: |
        ```yaml
        task_status: string
        completion_time: string
        context_info:
          metadata:
            task_id: string
            category: string
          execution_summary:
            start_time: string
            end_time: string
            duration: string
        results:
          deliverables: object
          next_steps?: [string]
          lessons_learned?: [string]
        ```
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
      - "所有字段必须有清晰的描述"
```

---

### 详细 Schema 规范

#### 1. 元数据部分 (metadata)

```yaml
metadata:
  # 任务标识信息
  task_id?: string # 唯一任务ID，格式: TASK-YYYY-NNN
  task_id_list?: [string] # 父任务ID链，用于追踪任务来源
  # 分类和标签
  category: string # 必填: feature | bugfix | refactor | docs | research
  tags?: [string] # 标签列表，用于分类和筛选
  # 协作信息
  assignee?: string # 指定的执行模式
  reviewer?: string # 审核者
  dependencies?: [string] # 依赖的任务ID列表
  # 自定义属性
  custom?: object # 自定义扩展字段
```

#### 2. 任务定义部分 (task)

```yaml
task:
  # 核心描述
  description: string       # 必填: 一句话清晰描述任务目标
  summary?: string          # 详细描述（1-3段）
  # 上下文信息
  context:
    reason: string         # 必填: 执行此任务的背景原因
    background?: string    # 背景故事或历史信息
    problem_statement?: string  # 解决什么问题
    # 相关资源
    relevant_files?: [string]     # 相关文件路径
    relevant_code?: string         # 关键代码片段
    references?: [string]         # 参考资料、文档链接
    # 用户和场景
    user_persona?: string          # 目标用户角色
    use_cases?: [string]          # 使用场景列表
    stakeholder?: [string]        # 相关利益方
    # 环境信息
    environment?: object           # 执行环境信息
    constraints?: [string]        # 已知的约束条件
  # 具体需求
  requirements:
    # 功能需求
    functional?: [string]         # 功能性需求列表
    non_functional?: [string]     # 非功能性需求（性能、安全等）
    # 技术要求
    technical?: [string]          # 技术规范要求
    compliance?: [string]         # 合规性要求
    # 约束条件
    must_haves?: [string]         # 必须满足的需求
    nice_to_haves?: [string]      # 最好有的需求
    # 用户故事格式（可选）
    user_stories?: [string]       # 用户故事格式: "作为X，我想要Y，以便Z"
  # 执行边界
  boundaries:
    # 文件权限
    allowed_files?: [string]      # 允许修改的文件列表
    readonly_files?: [string]     # 只读文件列表
    disallowed_files?: [string]   # 禁止访问的文件
    # 模式约束
    allowed_patterns?: [string]    # 允许修改的代码模式
    disallowed_patterns?: [string] # 禁止修改的模式
    # 技术栈约束
    tech_stack?: object           # 技术栈限制
      language?: string           # 编程语言
      framework?: string          # 框架
      libraries?: [string]        # 库限制
      version_constraints?: string # 版本约束
    # 时间和资源
    time_limit?: string           # 时间限制
    resource_limits?: object      # 资源限制
      memory?: string             # 内存限制
      cpu?: string                # CPU限制
  # 验收标准
  acceptance:
    criteria?: [string]           # 验收标准列表
    test_requirements?: [string]   # 测试要求
    performance_targets?: object  # 性能目标
      response_time?: string      # 响应时间要求
      throughput?: string         # 吞吐量要求
      availability?: string       # 可用性要求
    # 质量标准
    quality_standards?: object    # 质量标准
      code_coverage?: string      # 代码覆盖率
      complexity_limit?: string   # 复杂度限制
      bug_tolerance?: string      # 缺陷容忍度
    # 演示要求
    demo_requirements?: [string]  # 演示要求
  # 执行计划
  execution:
    # 任务分解
    phases?: [string]             # 执行阶段
    subtasks?: [object]           # 子任务列表
      - name: string              # 子任务名称
        description: string       # 子任务描述
        estimated_time?: string   # 预估时间
        dependencies?: [string]   # 依赖的子任务
    # 实现策略
    approach?: string             # 实现方法描述
    alternatives?: [string]       # 备选方案
    # 风险评估
    risks?: [object]              # 风险评估
      - description: string      # 风险描述
        impact: string           # 影响程度
        probability: string       # 发生概率
        mitigation: string        # 缓解措施
    # 回滚计划
    rollback_plan?: string        # 回滚策略
    # 检查点
    checkpoints?: [string]        # 关键检查点
  # 任务清单管理
  todo?: object                   # 任务清单规范
    # 格式规范
    # - [ ] 待办任务 (未开始)
    # - [-] 进行中任务 (正在执行)
    # - [x] 已完成任务 (已完成)
    items?: [object]              # 任务项列表
      - id: string                # 任务唯一标识
        title: string             # 任务标题
        description?: string      # 任务描述
        status: enum              # 任务状态: pending | in_progress | completed
        priority?: enum           # 优先级: low | medium | high | critical
        assignee?: string         # 负责人/模式
        dependencies?: [string]   # 依赖的任务ID
        estimated_time?: string    # 预估时间
        actual_time?: string      # 实际用时
        due_date?: string         # 截止日期
        tags?: [string]           # 标签
        metadata?: object         # 自定义元数据
    # 状态管理
    state_management?: object      # 状态管理规则
      auto_transition?: boolean    # 是否自动转换状态
      state_triggers?: object     # 状态触发条件
        pending_to_in_progress?: [string]  # 从待办到进行的条件
        in_progress_to_completed?: [string] # 从进行到完成的条件
    # 最佳实践
    best_practices?: [string]     # 最佳实践建议
      - "任务描述应简洁明确"
      - "每个任务应该是可独立验证的"
      - "及时更新任务状态"
      - "保持任务粒度适中"
      - "记录任务执行过程中的关键决策"
    # 任务组织
    organization?: object        # 任务组织方式
      groups?: [object]          # 任务分组
        - name: string           # 分组名称
          tasks: [string]        # 包含的任务ID
          description?: string   # 分组描述
      milestones?: [object]      # 里程碑
        - name: string           # 里程碑名称
          date: string           # 目标日期
          tasks: [string]        # 关联任务
```

#### 3. 响应格式部分 (response)

```yaml
response:
  # 响应格式部分
  format:
    structure:
      required_sections:
        - "task_status"
        - "completion_time"
        - "context_info"
      template: |
        ```yaml
        task_status: string
        completion_time: string
        context_info:
          metadata:
            task_id: string
            category: string
          execution_summary:
            start_time: string
            end_time: string
            duration: string
        results:
          deliverables: object
          next_steps?: [string]
          lessons_learned?: [string]
        ```
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
      - "所有字段必须有清晰的描述"
```

---

### 不同模式的特化字段

#### Code 模式特化字段

```yaml
# 在 task.boundaries.tech_stack 中增加
code_specific:
  # 编码规范
  coding_standards:
    design_patterns?: [string] # 期望使用的设计模式
    architecture_pattern?: string # 架构模式
    naming_convention?: string # 命名规范
  # 测试要求
  testing:
    unit_test_framework?: string # 单元测试框架
    integration_tests?: boolean # 是否需要集成测试
    mocking_required?: boolean # 是否需要模拟
  # 代码质量
  quality_metrics:
    cyclomatic_complexity?: number # 圈复杂度上限
    lines_of_code?: number # 代码行数限制
    duplication_threshold?: number # 重复代码阈值
```

#### Architect 模式特化字段

```yaml
# 在 task.requirements 中增加
architecture_specific:
  # 设计原则
  design_principles?: [string]    # SOLID、KISS等
  scalability_requirements?: string # 可扩展性要求
  # 架构决策
  architectural_decisions?: [object] # 架构决策记录
    - decision: string           # 决策内容
      rationale: string          # 决策理由
      alternatives: [string]    # 备选方案
  # 文档要求
  documentation_requirements:
    diagrams_required?: [string] # 需要的图表类型
    api_specification_level?: string # API规范级别
```

#### Debug 模式特化字段

```yaml
# 在 task.context 中增加
debug_specific:
  # 问题信息
  issue_details:
    error_message?: string # 错误信息
    stack_trace?: string # 堆栈跟踪
    reproduction_steps?: [string] # 复现步骤
  # 调试环境
  debug_environment:
    debugging_tools?: [string] # 调试工具
    log_levels?: [string] # 日志级别
    monitoring_setup?: boolean # 是否需要监控
```

---

### 模式选择指南

#### 核心模式职责总览

| 模式 Slug                  | 名称            | 核心职责与用途                                                                                                                                                                    | 工具权限                            | 工作流特点                                                                                                                                                                       | 协作关系                                                                                                             |
| -------------------------- | --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **`orchestrator`**         | 🧠 Brain        | **系统级任务调度与决策中枢**<br>- 复杂任务智能分解与依赖分析<br>- 多模式协作流程设计<br>- L1 级决策评估与用户确认<br>- 任务执行路径优化与资源调配<br>- 跨模式上下文传递与状态同步 | 全部工具<br>(除 MCP 服务工具)       | 1. **分析先行**：深度理解需求后再分解<br>2. **可视化确认**：使用流程图/表格展示方案<br>3. **分层决策**：关键决策点必须用户确认<br>4. **动态调整**：根据执行反馈优化后续任务      | ↑ **输入**：所有用户需求<br>↓ **输出**：向各专业模式委派任务<br>↔ **协作**：监控各模式执行状态                       |
| **`architect`**            | 🏗️ 顶尖架构师   | **系统架构与技术选型专家**<br>- 整体架构设计与评估<br>- 技术栈选型与对比分析<br>- 重构策略制定与规划<br>- 系统边界定义与模块划分<br>- 性能与可扩展性方案设计                      | 仅限 `.md` 文件<br>(文档与架构设计) | 1. **顶层设计**：关注系统整体而非实现细节<br>2. **方案对比**：提供多维度技术选型分析<br>3. **渐进细化**：从概念到详细设计逐步深入<br>4. **标准导向**：遵循业界最佳实践与设计模式 | ↑ **输入**：来自 orchestrator 的架构需求<br>→ **输出**：架构文档与技术方案<br>↓ **指导**：为 code 模式提供设计指导   |
| **`code`**<br>**`code-*`** | 🪄 代码魔法师   | **多语言代码实现与优化专家**<br>- 通用代码实现与功能开发<br>- 代码重构与性能优化<br>- 单元测试编写与质量保证<br>- 技术债务清理与规范重构<br>- 跨语言代码转换与适配                | 全部工具<br>(代码专用)              | 1. **工程化思维**：追求代码质量与可维护性<br>2. **设计模式**：熟练运用各类设计模式<br>3. **测试驱动**：编写完备的测试用例<br>4. **持续优化**：主动发现并修复代码坏味道           | ↑ **输入**：来自 architect 的设计方案<br>← **协作**：与 debug 模式配合排查问题<br>→ **输出**：高质量代码实现         |
| **`ask`**                  | 📚 学术顾问     | **知识解释与技术教学专家**<br>- 复杂概念深度解析与教学<br>- 技术原理系统性阐述<br>- 学习路径规划与指导<br>- 代码逻辑详细解读<br>- 技术问答与知识普及                              | 全部工具<br>(知识检索专用)          | 1. **由浅入深**：从基础概念到高级应用<br>2. **图文并茂**：使用图表、示例增强理解<br>3. **场景化教学**：结合实际应用场景讲解<br>4. **互动引导**：鼓励提问与深入探讨               | ↑ **输入**：用户的学习与理解需求<br>→ **输出**：系统化的知识内容<br>↔ **协作**：为其他模式提供知识支持               |
| **`debug`**                | 🔬 异常分析师   | **问题诊断与调试专家**<br>- 复杂 Bug 追踪与定位<br>- 性能瓶颈分析与优化<br>- 错误模式识别与修复<br>- 调试策略制定与执行<br>- 异常处理机制设计                                     | 全部工具<br>(诊断分析专用)          | 1. **系统化诊断**：从症状到根因的完整分析<br>2. **数据驱动**：基于日志、指标进行问题定位<br>3. **预防导向**：建立错误预防机制<br>4. **知识沉淀**：将调试经验转化为最佳实践       | ↑ **输入**：来自 code 或其他模式的问题<br>→ **输出**：问题诊断报告与修复方案<br>↔ **协作**：与 code 模式配合修复问题 |
| **`doc-writer`**           | ✍️ 文档工程师   | **文档创作与维护专家**<br>- API 文档自动生成与维护<br>- 技术文档结构化编写<br>- 用户手册与使用指南<br>- 文档标准化与规范制定<br>- 文档版本管理与更新                              | 仅限 `.md` 文件<br>(文档专用)       | 1. **结构化思维**：确保文档逻辑清晰完整<br>2. **用户导向**：从使用者角度组织内容<br>3. **持续更新**：与代码变更保持同步<br>4. **标准化**：遵循文档编写规范与最佳实践             | ↑ **输入**：来自各模式的文档需求<br>← **协作**：从代码中提取文档信息<br>→ **输出**：标准化技术文档                   |
| **`giter`**                | ⚙️ 版本控制专家 | **Git 工作流与版本管理专家**<br>- 分支策略设计与执行<br>- 提交规范制定与检查<br>- 代码审查流程管理<br>- 版本发布与标签管理<br>- 协作冲突解决与协调                                | 仅限 `.md` 文件<br>(Git 流程文档)   | 1. **流程规范**：建立标准化的 Git 工作流<br>2. **历史追溯**：确保变更历史清晰可追踪<br>3. **协作优化**：提升团队开发协作效率<br>4. **风险控制**：管理版本发布与回滚策略          | ↑ **输入**：团队协作需求<br>↔ **协作**：为所有模式提供版本控制指导<br>→ **输出**：Git 工作流规范                     |
| **`researcher`**           | 📚 首席研究员   | **技术调研与知识体系构建专家**<br>- 技术趋势分析与预测<br>- 解决方案对比与评估<br>- 领域知识体系构建<br>- 技术栈演进路径规划<br>- 创新方案研究与验证                              | 全部工具<br>(研究分析专用)          | 1. **系统性研究**：全面调研技术生态<br>2. **数据驱动**：基于客观数据进行分析<br>3. **前瞻性**：关注技术发展趋势<br>4. **实用性**：提供可落地的技术建议                           | ↑ **输入**：技术选型与研究需求<br>→ **输出**：技术调研报告<br>↔ **协作**：为 architect 提供技术支持                  |
| **`project-research`**     | 🔍 项目研究员   | **代码库分析与技术评估专家**<br>- 代码架构深度分析<br>- 技术债务识别与评估<br>- 代码质量度量与报告<br>- 重构可行性分析<br>- 技术栈一致性检查                                      | 全部工具<br>(代码分析专用)          | 1. **深度分析**：理解代码结构与设计思想<br>2. **量化评估**：使用指标衡量代码质量<br>3. **风险识别**：发现潜在问题与改进点<br>4. **实用建议**：提供具体可行的改进方案             | ↑ **输入**：项目代码库<br>→ **输出**：代码分析报告<br>↔ **协作**：为重构和优化提供依据                               |
| **`mode-writer`**          | ✍️ 模式工程大师 | **模式设计与开发框架专家**<br>- 新模式设计与开发<br>- 模式架构优化与重构<br>- 模式间协作机制设计<br>- 模式性能优化与调优<br>- 模式标准化与规范制定                                | 仅限 `.md` 文件<br>(模式定义文档)   | 1. **元编程思维**：设计和优化模式本身<br>2. **系统化设计**：构建可扩展的模式架构<br>3. **标准化**：建立模式开发规范<br>4. **创新驱动**：探索新的模式设计范式                     | ↑ **输入**：新功能或改进需求<br>→ **输出**：新模式定义<br>↔ **协作**：与 orchestrator 设计协作机制                   |
| **`memory`**               | 🧠 记忆中枢     | **知识管理与记忆系统专家**<br>- 记忆库初始化与维护<br>- 知识结构化存储<br>- 信息检索与快速访问<br>- 临时记忆清理与管理<br>- 知识关联与推荐                                        | 全部工具<br>(仅限记忆相关)          | 1. **结构化存储**：建立清晰的知识分类<br>2. **高效检索**：支持快速信息查找<br>3. **自动维护**：定期清理和优化存储<br>4. **智能关联**：建立知识间的联系                           | ↑ **输入**：各类知识信息<br>↔ **协作**：为所有模式提供知识支持<br>→ **输出**：结构化知识库                           |

#### 基于任务类型的模式选择指南

##### 1. 系统级任务（复杂、多步骤）

- **适合模式**: `orchestrator`
- **任务特征**:
  - 需要分解为多个子任务
  - 涉及多个专业领域
  - 需要复杂的依赖管理
  - 需要用户决策确认

##### 2. 架构设计任务

- **适合模式**: `architect`
- **任务特征**:
  - 系统架构设计
  - 技术栈选型
  - 重构规划
  - 性能方案设计

##### 3. 代码实现任务

- **适合模式**: `code` / `code-*`
- **模式选择优先级**:
  - 当有明确编程语言时，优先使用对应的语言特化模式（如 `code-python`、`code-java`、`code-golang` 等）
  - 当没有明确编程语言或需要通用代码处理时，使用 `code` 模式
- **任务特征**:
  - 功能开发
  - 代码重构
  - 测试编写
  - Bug 修复

##### 4. 知识获取任务

- **适合模式**: `ask`
- **任务特征**:
  - 概念解释
  - 技术原理说明
  - 学习路径规划
  - 代码逻辑解读

##### 5. 问题诊断任务

- **适合模式**: `debug`
- **任务特征**:
  - Bug 追踪
  - 性能分析
  - 错误修复
  - 调试策略制定

##### 6. 文档相关任务

- **适合模式**: `doc-writer`
- **任务特征**:
  - API 文档生成
  - 技术文档编写
  - 用户手册制作
  - 文档标准化

##### 7. 版本控制任务

- **适合模式**: `giter`
- **任务特征**:
  - Git 工作流设计
  - 分支策略制定
  - 版本发布管理
  - 协作流程优化

##### 8. 研究分析任务

- **适合模式**: `researcher`
- **任务特征**:
  - 技术趋势分析
  - 解决方案评估
  - 知识体系构建
  - 创新方案研究

##### 9. 代码库分析任务

- **适合模式**: `project-research`
- **任务特征**:
  - 架构深度分析
  - 技术债务评估
  - 代码质量度量
  - 重构可行性分析

##### 10. 模式开发任务

- **适合模式**: `mode-writer`
- **任务特征**:
  - 新模式设计
  - 模式架构优化
  - 协作机制设计
  - 模式标准化

##### 11. 知识管理任务

- **适合模式**: `memory`
- **任务特征**:
  - 记忆库维护
  - 知识结构化
  - 信息检索优化
  - 知识关联建立

#### 模式协作流程

##### 标准协作流程

1. **任务接收** → `orchestrator`
   - 分析任务复杂度
   - 识别所需专业领域
   - 制定任务分解策略
2. **任务分解** → `orchestrator`
   - 创建子任务清单
   - 确定任务依赖关系
   - 分配执行模式
3. **专业执行** → 各专业模式
   - 按专业领域执行
   - 必要时进行模式间协作
   - 保持上下文传递
4. **结果汇总** → `orchestrator`
   - 收集各子任务结果
   - 验证整体完成度
   - 准备最终交付

##### 典型协作场景

**场景 1: 新功能开发**

```
orchestrator → architect → code → debug → doc-writer
     ↓           ↓        ↓       ↓          ↓
  任务分解 → 架构设计 → 代码实现 → 测试调试 → 文档编写
```

**场景 2: 系统重构**

```
orchestrator → project-research → architect → code → giter
     ↓                ↓              ↓        ↓        ↓
  任务分解 → 代码库分析 → 重构方案设计 → 重构实施 → 版本管理
```

**场景 3: 问题排查**

```
orchestrator → debug → code → ask → doc-writer
     ↓         ↓       ↓      ↓          ↓
  任务分解 → 问题诊断 → 修复代码 → 知识补充 → 更新文档
```

##### 协作最佳实践

1. **明确边界**
   - 每个模式专注于自己的专业领域
   - 通过 `new_task` 进行任务委派
   - 避免模式职责重叠
2. **上下文传递**
   - 使用 `task_id_list` 追踪任务来源
   - 在 `metadata.dependencies` 中声明依赖
   - 保持信息精简但完整
3. **质量保证**
   - 每个模式输出前进行自检
   - 通过 `acceptance.criteria` 定义验收标准
   - 使用 `output.validation` 确保输出质量
4. **持续优化**
   - 记录协作中的问题和改进点
   - 定期优化模式间接口
   - 建立知识库沉淀经验

### 多层次示例体系

#### 基础示例 - 简单功能开发

```yaml
metadata:
  task_id: "TASK-2025-001"
  task_id_list: ["TASK-2025-000"] # 来自父任务
  category: "feature"
  tags: ["api", "user-management"]
task:
  description: "为用户服务添加密码重置功能"
  context:
    reason: "用户反馈无法重置忘记的密码"
    relevant_files:
      - "src/services/user_service.py"
      - "tests/test_user_service.py"
    user_persona: "后端开发工程师"
  requirements:
    functional:
      - "发送密码重置邮件"
      - "验证重置令牌"
      - "更新用户密码"
    non_functional:
      - "令牌有效期1小时"
      - "邮件发送5分钟内"
  boundaries:
    allowed_files:
      - "src/services/user_service.py"
      - "tests/test_user_service.py"
    tech_stack:
      language: "Python"
      framework: "FastAPI"
  acceptance:
    criteria:
      - "邮件发送成功"
      - "令牌验证通过"
      - "密码更新成功"
response:
  format:
    structure:
      required_sections:
        - "task_status"
        - "completion_time"
        - "context_info"
      template: |
        ```yaml
        task_status: string
        completion_time: string
        context_info:
          metadata:
            task_id: string
            category: string
          execution_summary:
            start_time: string
            end_time: string
            duration: string
        results:
          deliverables: object
          next_steps?: [string]
          lessons_learned?: [string]
        ```
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
      - "所有字段必须有清晰的描述"
```

#### 中级示例 - 架构重构

```yaml
metadata:
  task_id: "TASK-2025-002"
  task_id_list: ["TASK-2025-000", "TASK-2025-001"] # 任务链
  category: "refactor"
  tags: ["architecture", "microservices"]
  assignee: "architect"
task:
  description: "将单体应用拆分为微服务架构"
  context:
    reason: "应用规模增长，单体架构难以维护"
    background: "现有应用超过10万行代码，部署时间长"
    problem_statement: "需要提高系统的可扩展性和团队开发效率"
    relevant_files:
      - "src/main.py"
      - "src/models/"
      - "src/services/"
      - "docker-compose.yml"
  requirements:
    functional:
      - "识别服务边界"
      - "设计服务间通信"
      - "实现服务发现"
      - "配置API网关"
    non_functional:
      - "服务独立部署"
      - "故障隔离"
      - "水平扩展能力"
    technical:
      - "使用容器化部署"
      - "实现配置中心"
      - "日志聚合"
  boundaries:
    disallowed_patterns:
      - "直接数据库共享"
      - "紧耦合服务调用"
    tech_stack:
      framework: "Spring Boot"
      communication: "gRPC"
      infrastructure: "Kubernetes"
  acceptance:
    criteria:
      - "服务响应时间<100ms"
      - "系统可用性>99.9%"
      - "部署时间<5分钟"
    performance_targets:
      response_time: "<100ms"
      throughput: "1000 req/s"
  execution:
    phases:
      - "服务拆分设计"
      - "基础架构搭建"
      - "服务迁移"
      - "测试和优化"
    risks:
      - description: "数据一致性"
        impact: "高"
        probability: "中"
        mitigation: "使用分布式事务"
  # 任务清单管理
  todo:
    items:
      - id: "T001"
        title: "服务拆分设计"
        description: "识别服务边界并设计服务拆分方案"
        status: "pending"
        priority: "high"
        assignee: "architect"
        estimated_time: "3天"
      - id: "T002"
        title: "基础架构搭建"
        description: "搭建微服务基础设施（服务发现、配置中心等）"
        status: "pending"
        priority: "high"
        assignee: "code"
        dependencies: ["T001"]
        estimated_time: "5天"
      - id: "T003"
        title: "服务迁移"
        description: "将现有功能迁移到微服务架构"
        status: "pending"
        priority: "medium"
        assignee: "code"
        dependencies: ["T001", "T002"]
        estimated_time: "10天"
    state_management:
      auto_transition: true
      state_triggers:
        pending_to_in_progress:
          - "架构设计文档完成"
          - "基础设施准备就绪"
        in_progress_to_completed:
          - "所有服务成功迁移"
          - "性能测试通过"
    organization:
      groups:
        - name: "设计阶段"
          tasks: ["T001"]
          description: "架构设计和规划"
        - name: "实施阶段"
          tasks: ["T002", "T003"]
          description: "基础设施搭建和服务迁移"
      milestones:
        - name: "架构设计完成"
          date: "2025-02-15"
          tasks: ["T001"]
        - name: "微服务上线"
          date: "2025-03-01"
          tasks: ["T002", "T003"]
  architecture_specific:
    design_principles:
      - "单一职责"
      - "松耦合"
      - "高内聚"
    documentation_requirements:
      diagrams_required:
        - "架构图"
        - "服务依赖图"
        - "部署图"
response:
  format:
    structure:
      required_sections:
        - "task_status"
        - "completion_time"
        - "context_info"
      template: |
        ```yaml
        task_status: string
        completion_time: string
        context_info:
          metadata:
            task_id: string
            category: string
          execution_summary:
            start_time: string
            end_time: string
            duration: string
        results:
          deliverables: object
          next_steps?: [string]
          lessons_learned?: [string]
        ```
    content_requirements:
      - "必须使用标准 yaml 格式"
      - "保持缩进一致"
      - "所有字段必须有清晰的描述"
```
