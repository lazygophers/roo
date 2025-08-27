---
name: new_task
title: new_task 委派规范
description: "定义 new_task 工具的消息格式规范，包含任务定义、执行边界和输出要求"
category: rule
tags: [任务委派, 消息格式, 规范]
---

## new_task 委派规范

### 三段式 Message 格式设计

**整体结构**:

```
message: |
  ---
  # 元数据部分
  metadata:
    task_id: "TASK-2025-001"
    task_id_list: ["TASK-2025-000"]  # 父任务ID链
    tags: ["performance", "cache"]

  ---
  # 任务定义部分
  task:
    description: "一句话描述任务目标"
    context: {任务上下文信息}
    requirements: {具体需求列表}
    boundaries: {执行边界}
    acceptance: {验收标准}
    execution: {执行计划}

  ---
  # 输出规范部分
  output:
    format: {输出格式要求}
    validation: {验证规则}
    deliverables: {交付物清单}
```

---

## 详细 Schema 规范

### 1. 元数据部分 (metadata)

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

### 2. 任务定义部分 (task)

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
```

### 3. 输出规范部分 (output)

```yaml
output:
  # 格式要求
  format:
    structure?: object            # 输出结构要求
      sections?: [string]         # 必须包含的章节
      template?: string           # 输出模板

    # 内容要求
    content_requirements?: [string]  # 内容要求
    style_guide?: string         # 风格指南

    # 文档要求
    documentation?: object       # 文档要求
      api_docs?: boolean          # 是否需要API文档
      user_guide?: boolean        # 是否需要用户指南
      examples?: boolean          # 是否需要示例

    # 代码要求
    code_standards?: object       # 代码标准
      linting?: boolean           # 是否需要代码检查
      formatting?: boolean        # 是否需要格式化
      comments?: boolean          # 是否需要注释

  # 验证规则
  validation:
    # 自动验证
    automated_tests?: [string]   # 自动测试要求
    test_coverage?: string        # 测试覆盖率要求

    # 手动验证
    manual_checks?: [string]      # 手动检查项
    review_criteria?: [string]   # 审查标准

    # 验证环境
    test_environment?: object     # 测试环境要求
      os?: string                # 操作系统
      dependencies?: [string]     # 依赖项
      configuration?: object     # 配置要求

  # 交付物清单
  deliverables:
    files?: [object]              # 文件交付物
      - path: string             # 文件路径
        type: string             # 文件类型
        description?: string     # 文件描述
        required: boolean        # 是否必需

    # 功能交付物
    features?: [string]          # 功能列表
    endpoints?: [object]         # API端点
      - method: string           # HTTP方法
        path: string             # 路径
        description: string       # 描述

    # 文档交付物
    documentation?: [object]      # 文档列表
      - title: string            # 文档标题
        format: string           # 格式
        location: string         # 位置

    # 测试交付物
    tests?: [object]             # 测试交付物
      - type: string            # 测试类型
        coverage?: string        # 覆盖范围
        framework: string        # 测试框架

    # 其他交付物
    artifacts?: [object]         # 其他产物
      - name: string            # 产物名称
        type: string            # 类型
        location: string        # 位置

  # 报告要求
  reporting:
    progress_updates?: [string]   # 进度更新要求
    final_report?: object        # 最终报告要求
      sections?: [string]        # 报告章节
      metrics?: [string]         # 需要报告的指标
      format?: string            # 报告格式
```

---

## 不同模式的特化字段

### Code 模式特化字段

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

### Architect 模式特化字段

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

### Debug 模式特化字段

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

## 模式选择指南

### 核心模式职责总览

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

### 基于任务类型的模式选择指南

#### 1. 系统级任务（复杂、多步骤）

- **适合模式**: `orchestrator`
- **任务特征**:
  - 需要分解为多个子任务
  - 涉及多个专业领域
  - 需要复杂的依赖管理
  - 需要用户决策确认

#### 2. 架构设计任务

- **适合模式**: `architect`
- **任务特征**:
  - 系统架构设计
  - 技术栈选型
  - 重构规划
  - 性能方案设计

#### 3. 代码实现任务

- **适合模式**: `code` / `code-*`
- **任务特征**:
  - 功能开发
  - 代码重构
  - 测试编写
  - Bug 修复

#### 4. 知识获取任务

- **适合模式**: `ask`
- **任务特征**:
  - 概念解释
  - 技术原理说明
  - 学习路径规划
  - 代码逻辑解读

#### 5. 问题诊断任务

- **适合模式**: `debug`
- **任务特征**:
  - Bug 追踪
  - 性能分析
  - 错误修复
  - 调试策略制定

#### 6. 文档相关任务

- **适合模式**: `doc-writer`
- **任务特征**:
  - API 文档生成
  - 技术文档编写
  - 用户手册制作
  - 文档标准化

#### 7. 版本控制任务

- **适合模式**: `giter`
- **任务特征**:
  - Git 工作流设计
  - 分支策略制定
  - 版本发布管理
  - 协作流程优化

#### 8. 研究分析任务

- **适合模式**: `researcher`
- **任务特征**:
  - 技术趋势分析
  - 解决方案评估
  - 知识体系构建
  - 创新方案研究

#### 9. 代码库分析任务

- **适合模式**: `project-research`
- **任务特征**:
  - 架构深度分析
  - 技术债务评估
  - 代码质量度量
  - 重构可行性分析

#### 10. 模式开发任务

- **适合模式**: `mode-writer`
- **任务特征**:
  - 新模式设计
  - 模式架构优化
  - 协作机制设计
  - 模式标准化

#### 11. 知识管理任务

- **适合模式**: `memory`
- **任务特征**:
  - 记忆库维护
  - 知识结构化
  - 信息检索优化
  - 知识关联建立

### 模式协作流程

#### 标准协作流程

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

#### 典型协作场景

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

#### 协作最佳实践

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

## 多层次示例体系

### 基础示例 - 简单功能开发

```yaml
---
metadata:
  task_id: "TASK-2025-001"
  task_id_list: ["TASK-2025-000"] # 来自父任务
  category: "feature"
  tags: ["api", "user-management"]
---
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
---
output:
  format:
    code_standards:
      linting: true
      comments: true

  validation:
    automated_tests:
      - "单元测试覆盖所有功能"
      - "集成测试验证邮件发送"
    test_coverage: "95%"

  deliverables:
    files:
      - path: "src/services/user_service.py"
        required: true
      - path: "tests/test_user_service.py"
        required: true
```

### 中级示例 - 架构重构

```yaml
---
metadata:
  task_id: "TASK-2025-002"
  task_id_list: ["TASK-2025-000", "TASK-2025-001"] # 任务链
  category: "refactor"
  tags: ["architecture", "microservices"]
  assignee: "architect"
---
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
---
output:
  format:
    documentation:
      api_docs: true
      user_guide: true
    structure:
      sections:
        - "架构设计文档"
        - "API规范"
        - "部署指南"

  validation:
    automated_tests:
      - "集成测试"
      - "性能测试"
      - "混沌工程测试"

  deliverables:
    documentation:
      - title: "微服务架构设计"
        format: "markdown"
        location: "docs/architecture/"
    files:
      - path: "docker-compose.yml"
        required: true
      - path: "k8s/"
        required: true
```

### 高级示例 - 研究项目

```yaml
---
metadata:
  task_id: "TASK-2025-003"
  task_id_list: ["TASK-2025-000", "TASK-2025-001", "TASK-2025-002"] # 完整任务链
  category: "research"
  tags: ["ai", "optimization", "performance"]
  assignee: "researcher"
  dependencies: ["TASK-2025-001", "TASK-2025-002"]
---
task:
  description: "研究并实现AI模型推理优化方案"

  context:
    reason: "当前模型推理延迟过高，影响用户体验"
    background: "模型规模增长带来性能挑战"
    problem_statement: "需要在保持精度的前提下，将推理延迟降低50%"

    relevant_files:
      - "models/production_model.py"
      - "benchmark/performance_tests.py"
      - "docs/model_architecture.md"

    references:
      - "https://arxiv.org/abs/2301.02698"
      - "https://pytorch.org/tutorials/intermediate/quantization.html"

    environment:
      hardware: "NVIDIA A100"
      framework: "PyTorch 2.0"

    constraints:
      - "模型精度损失<2%"
      - "兼容现有API"
      - "零停机部署"

  requirements:
    functional:
      - "评估模型量化方案"
      - "实现推理引擎优化"
      - "设计A/B测试框架"
      - "建立性能监控"
    non_functional:
      - "推理吞吐量提升100%"
      - "GPU利用率>80%"
      - "内存占用减少30%"
    technical:
      - "支持FP16/INT8量化"
      - "实现动态批处理"
      - "模型并行推理"
    research:
      - "对比TensorRT/ONNX Runtime"
      - "评估知识蒸馏效果"
      - "研究稀疏化方案"

  boundaries:
    allowed_patterns:
      - "模型优化算法"
      - "性能测试代码"
    disallowed_patterns:
      - "修改模型架构"
      - "改变训练数据"
    time_limit: "4周"
    resource_limits:
      gpu_hours: "1000"
      storage: "1TB"

  acceptance:
    criteria:
      - "P99延迟<50ms"
      - "吞吐量>1000 QPS"
      - "精度损失<2%"
    quality_standards:
      code_coverage: "90%"
      bug_tolerance: "0 critical"

  execution:
    phases:
      - "文献调研和方案设计"
      - "原型开发和测试"
      - "性能优化和调优"
      - "生产部署和监控"
    subtasks:
      - name: "量化方案评估"
        description: "对比不同量化技术的效果"
        estimated_time: "1周"
      - name: "推理引擎优化"
        description: "实现自定义推理优化"
        estimated_time: "2周"
        dependencies: ["量化方案评估"]

    approach: |
      1. 使用TensorRT进行模型优化
      2. 实现动态批处理和请求调度
      3. 部署多实例负载均衡
      4. 建立实时性能监控

    alternatives:
      - "使用ONNX Runtime + OpenVINO"
      - "自研推理引擎"

    risks:
      - description: "量化精度损失过大"
        impact: "高"
        probability: "中"
        mitigation: "使用混合精度量化"
      - description: "优化后稳定性问题"
        impact: "高"
        probability: "低"
        mitigation: "渐进式部署和回滚机制"
---
output:
  format:
    content_requirements:
      - "详细的性能对比报告"
      - "部署和维护指南"
      - "性能监控dashboard"
    documentation:
      api_docs: true
      examples: true

  validation:
    automated_tests:
      - "性能基准测试"
      - "准确性验证测试"
      - "负载测试"
      - "稳定性测试"
    test_coverage: "95%"
    test_environment:
      os: "Ubuntu 20.04"
      dependencies:
        - "NVIDIA driver 515"
        - "Docker 20.10"

  deliverables:
    files:
      - path: "models/optimized_model.py"
        required: true
      - path: "inference_engine/"
        required: true
      - path: "benchmark/results/"
        required: true
      - path: "monitoring/dashboard/"
        required: true

    documentation:
      - title: "AI模型优化研究报告"
        format: "PDF"
        location: "docs/research/"
      - title: "性能优化技术文档"
        format: "markdown"
        location: "docs/optimization/"

    artifacts:
      - name: "优化模型文件"
        type: "model"
        location: "models/optimized/"
      - name: "性能测试数据集"
        type: "dataset"
        location: "data/test_sets/"

  reporting:
    progress_updates:
      - "周报"
      - "里程碑演示"
    final_report:
      sections:
        - "执行摘要"
        - "技术方案"
        - "性能对比"
        - "部署指南"
        - "后续优化建议"
      format: "markdown"
```

---

## 编写指南和最佳实践

### 编写原则

1. **简洁明确**

   - 每个字段只包含必要信息
   - 避免冗余描述
   - 使用标准术语

2. **结构化思维**

   - 按照元数据 → 任务 → 输出的逻辑组织
   - 相关字段分组放置
   - 使用层级关系表达复杂信息

3. **可扩展性**
   - 使用 `custom` 字段添加扩展信息
   - 保持向后兼容
   - 支持版本升级

### 最佳实践

1. **元数据部分**

   - 始终填写 `category`
   - 使用 `task_id_list` 追踪任务来源链
   - 使用 `tags` 提高任务可发现性
   - 记录 `dependencies` 管理任务依赖

2. **任务定义部分**

   - `description` 必须简洁明了
   - `context.reason` 解释任务价值
   - `requirements` 区分功能和非功能需求
   - `boundaries` 明确限制条件

3. **输出规范部分**
   - 明确定义交付物
   - 设置可验证的验收标准
   - 指定文档和测试要求

### 常见模式

1. **迭代开发**

   ```yaml
   execution:
     phases:
       - "MVP开发"
       - "功能扩展"
       - "性能优化"
   ```

2. **A/B 测试**

   ```yaml
   acceptance:
     demo_requirements:
       - "准备A/B测试方案"
       - "设置流量分配"
   ```

3. **迁移任务**
   ```yaml
   execution:
     rollback_plan: "保留原系统24小时"
     checkpoints:
       - "数据迁移完成"
       - "功能验证通过"
   ```

### 工具集成

1. **与 Jira 集成**

   ```yaml
   metadata:
     custom:
       jira_ticket: "PROJ-1234"
       epic_link: "PROJ-1000"
   ```

2. **与 CI/CD 集成**

   ```yaml
   output:
     validation:
       test_environment:
         ci_pipeline: "github-actions"
         deployment_env: "staging"
   ```

3. **监控集成**
   ```yaml
   output:
     reporting:
       metrics:
         - "performance_metrics"
         - "error_rates"
         - "user_satisfaction"
   ```

---
