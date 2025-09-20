---
name: mode-specification
title: 模式规范说明
description: "AI Code中自定义模式的结构和配置规范文档，定义模式的构成要素、YAML属性详情、文件/目录设置特定于模式的指令等完整规范"
category: 规范
priority: critical
tags: [模式定义, 配置规范, AI Code, 自定义模式]
sections:
  - "模式的构成要素：slug、name、description、roleDefinition等"
  - "YAML属性详情：每个属性的用途、格式、用法说明"
  - "通过文件/目录设置特定于模式的指令"
  - "模式选择策略：根据任务性质选择最专业模式"
core_attributes:
  - "slug：唯一内部标识符"
  - "name：显示名称"
  - "description：用途摘要"
  - "roleDefinition：核心身份和专业知识"
  - "groups：允许工具集和文件访问权限"
  - "whenToUse：自动化决策指导"
  - "customInstructions：特定行为指南"
example_yaml: |
  slug: doc-engineer
  name: 📝 文档工程师
  description: 一个专门用于编写和编辑技术文档的模式。
  roleDefinition: 你是一位专注于清晰文档的技术作家。
  whenToUse: 当需要编写或编辑文档时使用此模式。
  customInstructions: 在文档中应注重清晰性和完整性。
  groups:
    - read
    - - edit
      - fileRegex: \.(md|mdx)$
        description: 仅限 Markdown 文件
    - browser
---

# 模式规范说明

本文档定义了 AI Code 中自定义模式的结构和配置规范。

## 模式的构成要素

自定义模式由多个关键属性定义。理解这些概念将帮助您有效地定制 AI 的行为。

| 属性                 | 概念性描述                                                                                              |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| `slug`               | 模式的**唯一内部标识符**。AI Code 使用它来引用模式，特别是用于关联通过文件/目录设置的特定于模式的指令。 |
| `name`               | 模式在 AI Code 我界面中显示的**显示名称**。这应该是人类可读和描述性的。                                 |
| `description`        | 在模式选择器 UI 中显示的模式用途的**简短、我友好的摘要**。                                              |
| `roleDefinition`     | 定义模式的**核心身份和专业知识**。这段文字被放置在系统提示的开头。                                      |
| `groups`             | 定义模式的**允许工具集和文件访问权限**。                                                                |
| `whenToUse`          | 为 AI 的**自动化决策提供指导**，特别是在模式选择和任务编排方面。                                        |
| `customInstructions` | 模式的**特定行为指南**或规则。                                                                          |

```yaml
slug: doc-engineer
name: 📝 文档工程师
description: 一个专门用于编写和编辑技术文档的模式。
roleDefinition: 你是一位专注于清晰文档的技术作家。
whenToUse: 当需要编写或编辑文档时使用此模式。
customInstructions: 在文档中应注重清晰性和完整性。
groups:
  - read
  - - edit
    - fileRegex: \.(md|mdx)$
      description: 仅限 Markdown 文件
  - browser
```

### YAML 属性详情

##### `slug`

- **用途:** 模式的唯一标识符。
- **格式:** 必须匹配模式 `/^[a-zA-Z0-9-]+$/` (只允许字母、数字和连字符)。
- **用法:** 内部使用，以及在特定于模式的规则的文件/目录名中使用

##### `name`

- **用途:** 在 AI Code UI 中显示的名称。
- **格式:** 可以包含空格和正确的大小写。优先使用中文，并在名字开头添加一个合适的 emoji

##### `description`

- **用途:** 在模式选择器 UI 中模式名称下方显示的简短、我友好的摘要。

##### `roleDefinition`

- **用途:** 模式的角色、专业知识和个性的详细描述。
- **位置:** 当模式激活时，此文本将放置在系统提示的开头。

##### `groups`

- **用途:** 定义模式可以访问哪些工具组以及任何文件限制的列表。
- **可用工具组 (字符串):** `"read"`, `"edit"`, `"browser"`, `"command"`, `"mcp"`。
- **"edit" 组的文件限制:**
  - 要应用文件限制, "edit" 条目变成一个双元素列表, 其中第一个元素是 `"edit"`, 第二个是定义限制的对象。且长度不可以大于 2。
  - `fileRegex`: 一个正则表达式字符串，用于控制模式可以编辑哪些文件。
  - `description`: 一个描述限制的可选字符串。

##### `whenToUse`

- **用途:** 为 AI 的自动化决策提供指导，特别是在模式选择和任务编排方面。
- **用法:** 此字段由 AI 用于自动化决策，**不会在模式选择器 UI 中显示**。

##### `customInstructions`

- **用途:** 包含模式其他行为准则的字符串。
- **位置:** 此文本添加在系统提示的末尾。

### 通过文件/目录设置特定于模式的指令

除了 `customInstructions` 属性，您还可以通过工作区中的文件为特定于模式的指令提供指令。
