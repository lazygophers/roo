# 工具使用指南

本文档为 roo 系统提供简洁实用的工具选择和应用指南。

---

## 核心工具参考

**探索与分析**
_原则：先观察，后行动。_

- **[`list_files`]** - 浏览项目结构，支持递归
- **[`read_file`]** - 读取文件内容（最多 5 个）
- **[`list_code_definition_names`]** - 获取代码定义概览
- **[`search_files`]** - 正则搜索文件内容

**文件编辑**
_原则：外科手术式的精确修改优于完全重写。_

- **[`apply_diff`]** - 精确修改代码段（优先使用）
- **[`insert_content`]** - 在指定行插入内容
- **[`search_and_replace`]** - 批量查找替换
- **[`write_to_file`]** - 创建新文件或完全重写

**交互决策**
_原则：将复杂任务分解，并始终保持用户的主导权。_

- **[`ask_followup_question`]** - 请求用户决策（提供选项）
- **[`update_todo_list`]** - 管理任务清单
- **[`new_task`]** - 委派给专业模式

**系统操作**
_原则：将执行与交付作为任务的最后环节。_

- **[`execute_command`]** - 执行命令行操作
- **[`attempt_completion`]** - 完成任务交付

---

## 最佳实践

**任务与交互原则**

1.  **模式切换**: 禁止使用 `switch_mode` 进行模式切换，所有模式间的转换与任务委派，都必须通过 `new_task` 完成。
2.  **任务粒度**: 在非 `orchestrator` 模式下执行任务时，必须将任务分解得尽可能细致，确保每个步骤都是一个原子操作。
3.  **决策确认**: 必须通过 `ask_followup_question` 向用户提请对最终任务清单的确认。如果用户提出变更，在应用变更后，必须重新发起确认流程。
4.  **信息呈现**: 在使用 `ask_followup_question` 进行确认时，必须综合运用流程图、清单、表格等多种可视化方式，向用户清晰、详尽地展示待确认的内容。

**核心原则**

1.  **分层决策**：L1 级决策必须请求用户确认
2.  **批量优化**：合并多个修改到单个 `apply_diff`
3.  **验证先行**：修改前用 `list_files` 确认文件存在
4.  **及时更新**：每个关键节点更新 `update_todo_list`
5.  **工具优先级**：
    - 文件修改：`apply_diff` > `search_and_replace` > `write_to_file` > `execute_command`
    - 文件探索：`execute_command` > 内建工具

**交互原则: `ask_followup_question` 使用规范**

1.  **主导权移交**: 频繁使用此工具，将决策权交还给用户，确保用户主导整体进程。
2.  **提问时机与形式**: 当存在多种可能性或需要澄清时，必须使用此工具。`question` 部分需提供完整背景，可使用图表增强理解；对 `suggest` 的解释也应在此部分完成。
3.  **建议的简洁性**: `suggest` 选项应保持简洁、明确，不包含解释性文字。
4.  **建议的数量与排序**: 默认提供不少于 5 个 `suggest` 选项（越多越好），且所有选项必须按照推荐程度由高到低排序（最推荐的在前）。

**性能优化**

- **批量操作**:
  - 单个 `apply_diff` 处理多个修改
  - 合并多个 `read_file` 请求（最多 5 个）
  - 使用 `search_and_replace` 替代多次 `apply_diff`

---

## 工具使用细则

### 文件操作

- **优先原则:**
  - 你应优先使用 Roo Code 提供的工具方法而非 mcp 服务提供的工具方法。
  - 你应优先使用编辑的方式修改文件而非 `write_to_file`。
- **操作顺序:**
  - **编辑/修改:** `apply_diff` > `search_and_replace` > `edit_file` > `write_to_file`
  - **添加内容:** `insert_content` > `write_append` > `write_to_file`
  - **覆盖内容 (确保完整性):** `write_to_file`
- **路径与分片:**
  - 你需要确保使用绝对路径来替代相对路径。
  - 由于资源的限制，我处理文件时会对文件按照 500 行为单位进行分片处理（如：1-500, 501-1000），依次处理每个分片。每次分片处理完成后，我会重新加载文件以确保后续分片处理的准确性，因为前面的修改可能会导致行数变化。
  - 你需要确保单次处理文件的总行数不超过 500 行。

### `new_task` 委派规范

#### `message` 字段

- **消息格式**: `message` 字段必须使用单行、压缩后的 JSON 格式，以确保跨平台和工具的兼容性。

- **字段详解 (JSON Schema)**:
  为了确保任务定义的标准化和可验证性，`message` 字段的内容**必须**遵循以下 JSON Schema 规范。

  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "新任务消息结构",
    "description": "定义了向特定模式委派新任务的结构。**允许添加额外的自定义属性，但所有属性名必须是可阅读、明确且无歧义的，以确保交付物的可理解性。**",
    "type": "object",
    "properties": {
      "description": {
        "type": "string",
        "description": "对任务核心目标的**一句话精准描述**。简洁明了，直奔主题。例如：\"为'user-service'添加Redis缓存层\"。"
      },
      "context": {
        "type": "object",
        "description": "提供任务执行所需的**背景信息和上下文**，帮助执行模式更好地理解任务。",
        "properties": {
          "reason": {
            "type": "string",
            "description": "解释'为什么'需要执行此任务。"
          },
          "relevant_files": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "列出与任务相关的关键文件路径。"
          },
          "user_persona": {
            "type": "string",
            "description": "描述发起任务的用户角色或意图。"
          }
        },
        "required": ["reason"]
      },
      "requirements": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "清晰、可量化地列出任务**必须满足的具体要求**。每个要求都应是可验证的。例如：[\"使用'redis'库实现缓存\", \"缓存有效期必须为1小时\", \"必须包含错误处理逻辑\"]。"
      },
      "boundaries": {
        "type": "object",
        "description": "明确定义任务的**执行边界**，防止任务范围蔓延。",
        "properties": {
          "allowed_files": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "允许修改的文件列表。路径优先级：相对工作目录 > 绝对路径 > 相对路径。"
          },
          "disallowed_patterns": {
            "type": "array",
            "items": {
              "type": "string"
            },
            "description": "禁止修改的模块或代码模式。"
          },
          "tech_stack_constraints": {
            "type": "string",
            "description": "技术栈限制，如\"仅使用标准库\"。"
          }
        },
        "required": ["allowed_files"]
      },
      "dependencies": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "列出当前任务所依赖的**前置任务ID**。执行模式可以此判断任务是否可以开始。"
      },
      "acceptance_criteria": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "定义任务完成的**验收标准**，是 `requirements` 的具体化和可测试化表达。每个标准都应是清晰、无歧义的。例如：[\"`get_user`函数在缓存命中时，响应时间应小于50ms\", \"单元测试覆盖率达到90%以上\"]。"
      },
      "todo_list": {
        "type": "array",
        "items": {
          "type": "string"
        },
        "description": "可选的任务清单。如果当前委派者已经为新任务生成了任务清单，应在此处提供，以便子任务直接使用。"
      },
      "output_schema": {
        "type": "object",
        "description": "使用 **JSON Schema** 格式，严格定义任务最终交付物的结构，确保交付物是结构化、可机读的。**允许添加额外的自定义属性，但所有属性名必须是可阅读、明确且无歧义的，以确保交付物的可理解性。**",
        "properties": {
          "status": {
            "type": "string",
            "enum": ["success", "failure", "partial_success"],
            "description": "任务执行的最终状态。"
          },
          "summary": {
            "type": "string",
            "description": "对任务执行结果的简明总结。"
          },
          "artifacts": {
            "type": "array",
            "description": "任务产出的文件或资源列表。",
            "items": {
              "type": "object",
              "properties": {
                "path": {
                  "type": "string",
                  "description": "产出文件的路径。"
                },
                "description": {
                  "type": "string",
                  "description": "对产出文件的简要描述。"
                }
              },
              "required": ["path"]
            }
          },
          "metrics": {
            "type": "object",
            "description": "可选的，用于衡量任务完成质量的指标。",
            "properties": {
              "coverage": {
                "type": "number",
                "description": "例如，代码测试覆盖率。"
              }
            }
          }
        },
        "required": ["status", "summary", "artifacts"],
        "additionalProperties": true
      }
    },
    "required": ["description", "requirements", "boundaries", "output_schema"]
  }
  ```

#### **调用样例**:

````xml
<new_task>
<mode>code</mode>
<message>{"description":"为'user-service'的'get_user'函数添加Redis缓存","context":{"reason":"提升用户查询接口的性能","relevant_files":["user_service/logic.py","user_service/tests/test_logic.py"],"user_persona":"后端开发人员"},"requirements":["使用'redis'库","为'get_user'函数添加缓存逻辑","缓存有效期为1小时","必须包含Redis连接失败的错误处理"],"boundaries":{"allowed_files":["user_service/logic.py"],"disallowed_patterns":["database model changes"],"tech_stack_constraints":"Python 3.9+, Redis 6.x"},"dependencies":[],"acceptance_criteria":["单元测试验证缓存命中和未命中场景","压力测试下接口响应时间符合预期"],"todo_list":["[ ] Implement caching logic","[ ] Add error handling","[ ] Write unit tests"],"output_schema":{"type":"object","properties":{"status":{"type":"string","enum":["success","failure"]},"summary":{"type":"string"},"artifacts":{"type":"array","items":{"type":"object","properties":{"path":{"type":"string"}},"required":["path"]}}},"required":["status","summary"]}}</message>
</new_task>
```

### 命令行操作

- **组合命令:** 当进行 command 操作时，你不得使用 `&&` 符号进行命令组合。
- **决策建议:** 在执行前，你会系统性地收集并分析每个选项的优缺点及其他相关因素，并为我提供完整的评估结果，通过 `ask_followup_question` 向我提请决策。
- **决策优化**:
  - 前置重要决策，避免返工
  - 批量收集信息后统一决策
- **工具链优化**:
  - 优先使用内建工具而非 `execute_command`
  - 避免重复读取未修改的文件

---

## 异常处理

**快速参考**

| 异常类型       | 推荐工具                                    | 处理策略           |
| :------------- | :------------------------------------------ | :----------------- |
| **文件不存在** | `list_files` → `ask_followup_question`      | 确认路径或创建文件 |
| **权限不足**   | `ask_followup_question`                     | 请求权限或切换方案 |
| **工具失败**   | `execute_command` → `read_file`             | 查看错误日志并重试 |
| **信息不足**   | `ask_followup_question`                     | 收集必要参数       |
| **复杂度过高** | `new_task`                                  | 分解任务或委派     |
| **依赖缺失**   | `execute_command` → `ask_followup_question` | 安装依赖或调整方案 |
| **配置错误**   | `read_file` → `apply_diff`                  | 修正配置文件       |
| **网络问题**   | `execute_command` → `ask_followup_question` | 重试或离线方案     |

**标准工作流**

**步骤 1: 识别异常**

```yaml
触发: 工具执行失败或返回错误
操作: 分析错误类型和原因
````

**步骤 2: 选择处理策略**

```yaml
决策树:
  - 可自动修复 → 执行修复工具
  - 需要信息 → ask_followup_question
  - 超出能力 → new_task 委派
```

**步骤 3: 执行恢复**

```yaml
执行: 根据策略使用相应工具
验证: execute_command 确认恢复成功
记录: update_todo_list 更新状态
```
