# 任务管理指南

> AI 系统任务分解、评估与执行的核心规范。

---

## 核心理念

**任务管理哲学**

- **简洁明了:** 所有描述、要求和交付物都应简洁清晰，避免冗余信息。
- **精准匹配:** 仅提供与任务直接相关的上下文，确保信息高度聚焦。
- **模式驱动:** 基于任务性质智能选择最适合的专业模式。
- **价值导向:** 每个任务都应明确其价值点和预期产出。

---

## 任务评估与分解

**任务分解原则**

- **单一职责:** 每个子任务只做一件事。
- **原子性:** 任务应是不可再分的最小执行单元。
- **独立验证:** 子任务的结果应能被独立测试和验收。
- **简洁性:** 任务描述和要求必须简洁明了，避免歧义。

---

## 任务调度与模式选择

**通用准则**

- **规划先行:** 任何复杂任务在执行前，都必须由 `orchestrator` 模式进行分解，并通过 `ask_followup_question` 提请用户确认任务清单。
- **专业分工:** 根据任务性质，通过 `new_task` 委派给最合适的专业模式。

**核心模式职责**

| 模式 Slug          | 名称            | 核心职责与用途                                               | 模型选择指导                          |
| ------------------ | --------------- | ------------------------------------------------------------ | ------------------------------------- |
| `orchestrator`     | 🧠 Brain        | 任务分解、复杂决策、多步骤规划。                             | 适合复杂推理和规划能力的模型          |
| `architect`        | 🏗️ 顶尖架构师   | 系统架构设计、技术选型评估、重构规划等顶层设计活动。         | 需要强大技术理解和设计能力的模型      |
| `code` / `code-*`  | 🪄 代码魔法师   | 各类代码的编写、功能实现与调试。                             | 根据编程语言选择对应的专用模型        |
| `ask`              | 📚 学术顾问     | 代码解释、概念探索和技术学习，提供详尽的图文答案。           | 适合教学和解释能力强的模型            |
| `debug`            | 🔬 异常分析师   | 追踪 Bug、诊断错误和解决复杂问题。                           | 需要逻辑分析和推理能力的模型          |
| `doc-writer`       | ✍️ 文档工程师   | 创建、更新或改进项目文档。                                   | 适合写作和组织能力强的模型            |
| `giter`            | ⚙️ 版本控制专家 | 执行版本控制操作，如提交、变基和分支管理。                   | 熟悉 Git 工作流的模型                 |
| `researcher`       | 📚 首席研究员   | 系统化整理技术知识、进行技术方案对比分析或构建领域知识体系。 | 需要强大信息整合和分析能力的模型      |
| `project-research` | 🔍 项目研究员   | 深入了解一个代码库，进行技术选型或重构前的分析。             | 适合代码理解和模式识别的模型          |
| `mode-writer`      | ✍️ 模式工程大师 | 为精心设计、创建、重构或优化一个模式。                       | 需要元编程和系统设计能力的模型        |
| `memory`           | 🧠 记忆中枢     | 以自动化、规范化的方式初始化记忆库或清理临时记忆。           | 适合结构化处理和记忆管理的模型        |

---

## 通用工作流与最佳实践

### 任务与交互原则

1. **模式切换**: 禁止使用 `switch_mode` 进行模式切换，所有模式间的转换与任务委派，都必须通过 `new_task` 完成。
2. **任务粒度**: 在非 `orchestrator` 模式下执行任务时，必须将任务分解得尽可能细致，确保每个步骤都是一个原子操作。
3. **决策确认**: 必须通过 `ask_followup_question` 向用户提请对最终任务清单的确认。如果用户提出变更，在应用变更后，必须重新发起确认流程。
4. **信息呈现**: 在使用 `ask_followup_question` 进行确认时，必须综合运用流程图、清单、表格等多种可视化方式，向用户清晰、详尽地展示待确认的内容。
5. **模式专业化**: 严格遵循专业分工原则，确保每个模式只处理其擅长的领域，超出能力范围的任务必须通过 `new_task` 委派。
6. **上下文精简**: 在任务委派和执行过程中，仅传递与任务直接相关的上下文信息，避免信息过载。

### 核心原则

1. **分层决策**: L1 级决策必须请求用户确认
2. **批量优化**: 合并多个修改到单个 `apply_diff`
3. **验证先行**: 修改前用 `list_files` 确认文件存在
4. **及时更新**: 每个关键节点更新 `update_todo_list`
5. **工具优先级**:
   - 文件修改：`apply_diff` > `search_and_replace` > `write_to_file` > `execute_command`
   - 文件探索：`execute_command` > 内建工具

### `ask_followup_question` 使用规范

1. **主导权移交**: 频繁使用此工具，将决策权交还给用户，确保用户主导整体进程。
2. **提问时机与形式**: 当存在多种可能性或需要澄清时，必须使用此工具。`question` 部分需提供完整背景，可使用图表增强理解；对 `suggest` 的解释也应在此部分完成。
3. **建议的简洁性**: `suggest` 选项应保持简洁、明确，不包含解释性文字。
4. **建议的数量与排序**: 默认提供不少于 8 个 `suggest` 选项（越多越好），且所有选项必须按照推荐程度由高到低排序（最推荐的在前）。

### 性能优化

- **批量操作**:
  - 单个 `apply_diff` 处理多个修改
  - 合并多个 `read_file` 请求（最多 5 个）

### `new_task` 委派规范

**`message` 字段**

- **消息格式**: `message` 字段的格式为 `任务要求：{{内容}}\n返回要求：{{内容}}`。

  - `任务要求`：一个单行、压缩后的 JSON 字符串，遵循下文定义的 `New Task Message Schema`。
  - `返回要求`：一个单行、压缩后的 JSON Schema 字符串，定义了任务的交付物结构。用于任务完成后，子任务向付任务输出的交付物结构定义。

**`任务要求`字段规范**

```json
{
  "title": "New Task Message Schema",
  "description": "定义了向特定模式委派新任务的结构。**允许添加额外的自定义属性，但所有属性名必须是可阅读、明确且无歧义的，以确保交付物的可理解性。**",
  "type": "object",
  "properties": {
    "description": {
      "type": "string",
      "description": "对任务核心目标的**一句话精准描述**。简洁明了，直奔主题。例如：\"为'user-service'添加Redis缓存层\"。"
    },
    "context": {
      "type": "object",
      "description": "提供任务执行所需的**背景信息和上下文**，帮助执行模式更好地理解任务。**仅包含与任务直接相关的信息**，避免冗余。",
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
    }
  },
  "required": ["description", "requirements", "boundaries"]
}
```

**`返回要求` 字段规范**

- **压缩格式**: `返回要求` 的内容必须是**压缩后的单行 JSON 格式字符串**，不允许换行或格式化缩进。
- **字符串转义**: 作为 JSON 字符串值，内部的双引号必须使用反斜杠转义（`\"`）。
- **返回格式**: 返回格式是 JSON Schema，定义了任务的最终交付物结构。
- **自定义属性**: 允许在 schema 中添加**非 JSON Schema 标准定义**的自定义属性，以满足特定任务需求。
- **扩展性说明**
  - **命名规范**: 所有自定义属性名必须：
    - 使用 **camelCase** 或 **snake_case** 命名
    - 保持**语义明确**，避免缩写或模糊表述
    - 使用**英文命名**，确保跨团队协作的一致性
- **JsonSchema**:
  ```json
  {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "title": "Task Output Schema",
    "description": "定义了任务最终交付物的结构，确保交付物是结构化、可机读的。允许添加额外的自定义属性，但所有属性名必须是可阅读、明确且无歧义的。",
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "description": "任务执行状态，必须是 'success', 'failure', 或 'partial_success' 之一。",
        "enum": ["success", "failure", "partial_success"]
      },
      "summary": {
        "type": "string",
        "description": "对任务执行结果的简要描述，清晰传达核心产出或问题。"
      },
      "artifacts": {
        "type": "array",
        "description": "任务执行过程中生成或修改的文件列表。",
        "items": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "文件的相对路径。"
            },
            "description": {
              "type": "string",
              "description": "对文件变更内容的简要说明。"
            }
          },
          "required": ["path"]
        }
      },
      "metrics": {
        "type": "object",
        "description": "用于衡量任务执行效果的量化指标。",
        "properties": {
          "coverage": {
            "type": "number",
            "description": "代码测试覆盖率。"
          }
        }
      },
      "errors": {
        "type": "array",
        "description": "当 status 为 'failure' 或 'partial_success' 时，提供详细的错误信息列表。",
        "items": {
          "type": "object",
          "properties": {
            "code": {
              "type": "string",
              "description": "错误码。"
            },
            "message": {
              "type": "string",
              "description": "具体的错误描述。"
            }
          },
          "required": ["message"]
        }
      },
      "warnings": {
        "type": "array",
        "description": "执行过程中产生的警告信息列表。",
        "items": {
          "type": "string"
        }
      }
    },
    "required": ["status", "summary"],
    "additionalProperties": true
  }
  ```
- **完整示例**
  ```json
  {
    "type": "object",
    "properties": {
      "status": {
        "type": "string",
        "enum": ["success", "failure", "partial_success"],
        "description": "任务执行状态"
      },
      "summary": {
        "type": "string",
        "description": "执行结果摘要"
      },
      "artifacts": {
        "type": "array",
        "description": "修改的文件清单",
        "items": {
          "type": "object",
          "properties": {
            "path": {
              "type": "string",
              "description": "文件路径"
            },
            "action": {
              "type": "string",
              "enum": ["created", "modified", "deleted"],
              "description": "操作类型"
            },
            "linesChanged": {
              "type": "number",
              "description": "修改的代码行数"
            }
          },
          "required": ["path", "action"]
        }
      },
      "metrics": {
        "type": "object",
        "description": "性能指标",
        "properties": {
          "responseTimeImprovement": {
            "type": "string",
            "description": "响应时间改善百分比"
          },
          "cacheHitRate": {
            "type": "string",
            "description": "缓存命中率"
          },
          "testCoverage": {
            "type": "number",
            "description": "测试覆盖率"
          }
        }
      },
      "implementationDetails": {
        "type": "object",
        "description": "自定义字段：实现细节",
        "properties": {
          "cacheProvider": {
            "type": "string",
            "description": "使用的缓存提供商"
          },
          "ttlSeconds": {
            "type": "number",
            "description": "缓存过期时间（秒）"
          },
          "fallbackStrategy": {
            "type": "string",
            "description": "缓存失效时的降级策略"
          }
        }
      }
    },
    "required": ["status", "summary"],
    "additionalProperties": true
  }
  ```

**最佳实践**

1. **枚举约束**: 对状态类字段使用 `enum` 限定可选值，提高数据一致性。
2. **描述信息**: 为每个字段添加 `description`，提升 schema 的自文档性。
3. **默认值**: 为可选字段设置合理的 `default` 值，简化调用方处理。

**调用样例**:

```xml
<new_task>
<mode>code</mode>
<message>
  任务要求: {"description":"为'user-service'的'get_user'函数添加Redis缓存","context":{"reason":"提升用户查询接口的性能","relevant_files":["user_service/logic.py","user_service/tests/test_logic.py"],"user_persona":"后端开发人员"},"requirements":["使用'redis'库","为'get_user'函数添加缓存逻辑","缓存有效期为1小时","必须包含Redis连接失败的错误处理"],"boundaries":{"allowed_files":["user_service/logic.py"],"disallowed_patterns":["database model changes"],"tech_stack_constraints":"Python 3.9+, Redis 6.x"},"dependencies":[],"acceptance_criteria":["单元测试验证缓存命中和未命中场景","压力测试下接口响应时间符合预期"],"todo_list":["[ ] Implement caching logic","[ ] Add error handling","[ ] Write unit tests"]}
  返回要求: {"type":"object","properties":{"status":{"type":"string","enum":["success","failure","partial_success"]},"summary":{"type":"string"},"artifacts":{"type":"array","items":{"type":"object","properties":{"path":{"type":"string"},"description":{"type":"string"}},"required":["path"]}},"metrics":{"type":"object","properties":{"coverage":{"type":"number"}}}},"required":["status","summary","artifacts"],"additionalProperties":true}
  </message>
</new_task>
```
