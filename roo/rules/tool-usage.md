# 工具使用指南

本文档为 roo 系统提供简洁实用的工具选择和应用指南。

---

## 工具快速参考

### 核心工具分类

#### 🔍 探索与分析

- **[`list_files`](tool-usage.md:12)** - 浏览项目结构，支持递归
- **[`read_file`](tool-usage.md:13)** - 读取文件内容（最多 5 个）
- **[`list_code_definition_names`](tool-usage.md:14)** - 获取代码定义概览
- **[`search_files`](tool-usage.md:15)** - 正则搜索文件内容

#### ✏️ 文件编辑

- **[`apply_diff`](tool-usage.md:18)** - 精确修改代码段（优先使用）
- **[`insert_content`](tool-usage.md:19)** - 在指定行插入内容
- **[`search_and_replace`](tool-usage.md:20)** - 批量查找替换
- **[`write_to_file`](tool-usage.md:21)** - 创建新文件或完全重写

#### 🤝 交互决策

- **[`ask_followup_question`](tool-usage.md:24)** - 请求用户决策（提供选项）
- **[`update_todo_list`](tool-usage.md:25)** - 管理任务清单
- **[`new_task`](tool-usage.md:26)** - 委派给专业模式
- **[`sequentialthinking`](tool-usage.md:27)** - 复杂问题分析（MCP）

#### 🛠️ 系统操作

- **[`execute_command`](tool-usage.md:30)** - 执行命令行操作
- **[`use_mcp_tool`](tool-usage.md:31)** - 调用 MCP 服务工具
- **[`attempt_completion`](tool-usage.md:32)** - 完成任务交付

### 工具选择决策树

```
任务开始
├─ 需要了解项目？→ list_files + read_file + list_code_definition_names
├─ 需要用户决策？→ ask_followup_question（L1级决策）
├─ 任务复杂度高？→ sequentialthinking → 任务分解
├─ 修改文件？
│  ├─ 新建 → write_to_file
│  ├─ 精确修改 → apply_diff
│  ├─ 插入内容 → insert_content
│  └─ 批量替换 → search_and_replace
├─ 需要专业能力？→ new_task（委派专业模式）
└─ 完成任务 → update_todo_list + attempt_completion
```

---

## 场景化工具组合

### 常用工作流模式

#### 🚀 项目初始化

```yaml
流程: list_files → read_file(配置文件) → list_code_definition_names → update_todo_list
用途: 快速了解项目结构和依赖
```

#### 🐛 Bug 修复

```yaml
流程: read_file → search_files(影响范围) → apply_diff → execute_command(测试)
用途: 定位问题、修复代码、验证结果
```

#### 🏗️ 功能开发

```yaml
流程: sequentialthinking(设计) → write_to_file(新文件) → insert_content(添加功能) → execute_command(构建)
用途: 从设计到实现的完整开发流程
```

#### ♻️ 代码重构

```yaml
流程: list_code_definition_names → search_files → apply_diff(批量) → execute_command(测试)
用途: 系统化改进代码结构
```

#### 📝 文档更新

```yaml
流程: list_files → new_task(doc-writer) → write_to_file/apply_diff
用途: 委派给专业文档模式处理
```

### 工具组合速查

| 目标         | 推荐组合                                       | 关键点         |
| ------------ | ---------------------------------------------- | -------------- |
| **探索理解** | `list_files` → `read_file` → `search_files`    | 从整体到细节   |
| **精确修改** | `read_file` → `apply_diff` → `execute_command` | 先读后改再验证 |
| **批量操作** | `search_files` → `search_and_replace`          | 先搜索确认范围 |
| **创建功能** | `write_to_file` → `insert_content`             | 先框架后细节   |
| **复杂决策** | `sequentialthinking` → `ask_followup_question` | 分析后确认     |

---

## MCP 服务使用

### 核心 MCP 服务

#### Sequential Thinking
**用途**：复杂问题的逐步分析和深度思考
**场景**：需求分析、方案设计、问题排查、任务分解
**触发条件**：
- 任务复杂度评分 ≥ 60
- 涉及多系统集成
- 问题原因不明确
- 存在多种实现路径

```xml
<use_mcp_tool>
  <server_name>sequentialthinking</server_name>
  <tool_name>sequentialthinking</tool_name>
  <arguments>{
    "thought": "第一步：分析需求，明确核心目标...",
    "nextThoughtNeeded": true,
    "thoughtNumber": 1,
    "totalThoughts": 5
  }</arguments>
</use_mcp_tool>
```

#### Context7
**用途**：查询最新技术文档、API 参考、代码示例
**场景**：技术调研、最佳实践获取、新技术学习
**使用步骤**：
1. 先调用 `resolve-library-id` 获取库 ID
2. 再调用 `get-library-docs` 获取文档

```xml
<use_mcp_tool>
  <server_name>context7</server_name>
  <tool_name>get-library-docs</tool_name>
  <arguments>{
    "context7CompatibleLibraryID": "/facebook/react",
    "topic": "hooks",
    "tokens": 10000
  }</arguments>
</use_mcp_tool>
```

#### GitHub
**用途**：代码仓库管理、PR 操作、Issue 管理
**常用操作**：
- `get_file_contents` - 获取仓库文件内容
- `create_pull_request` - 创建 PR
- `search_code` - 搜索代码
- `list_issues` - 列出 Issue

### MCP 服务决策矩阵

| 服务 | 主要场景 | 决策级别 | 优先级 |
|------|----------|----------|--------|
| **sequentialthinking** | 任务分解、方案设计 | L1 | 最高 |
| **context7** | 外部文档查询 | L3 | 高 |
| **github** | 仓库操作 | L2 | 高 |

---

## 最佳实践

### ✅ 推荐做法

1. **分层决策**：L1 级决策必须请求用户确认
2. **批量优化**：合并多个修改到单个 `apply_diff`
3. **验证先行**：修改前用 `list_files` 确认文件存在
4. **及时更新**：每个关键节点更新 `todo_list`
5. **工具优先级**：
   - 文件修改：`apply_diff` > `search_and_replace` > `write_to_file`
   - 文件探索：内建工具 > `execute_command`

### ❌ 避免反模式

#### 常见反模式速查

| 反模式 | 问题 | 正确做法 |
|--------|------|----------|
| **用 `write_to_file` 做小修改** | 效率低、风险高、意图模糊 | 使用 `apply_diff` 精确修改 |
| **用 `execute_command` 执行文件操作** | 平台依赖、解析困难 | 使用内建工具（`list_files`/`read_file`） |
| **无规划连续调用工具** | 逻辑混乱、效率低下 | 先用 `sequentialthinking` 规划 |
| **开放式 `ask_followup_question`** | 负担转移给用户 | 提供具体选项供选择 |

#### 反模式详解

**1. 文件修改反模式**
- ❌ 读取整个文件 → 内存修改 → `write_to_file` 覆盖
- ✅ 使用 `apply_diff` 进行外科手术式精确修改
- ✅ 使用 `search_and_replace` 进行批量替换
- ✅ 使用 `insert_content` 添加新内容

**2. 文件系统操作反模式**
- ❌ `execute_command` 执行 `ls`、`cat`、`mkdir`
- ✅ `list_files` 列出文件（支持递归和结构化）
- ✅ `read_file` 读取文件内容
- ✅ `write_to_file` 自动创建所需目录

**3. 工具调用反模式**
- ❌ 无目的反复 `read_file` 不同文件
- ✅ 复杂任务先用 `sequentialthinking` 分析
- ✅ 使用 `ask_followup_question` 确认方案
- ✅ 遵循工具组合模式组织操作

**4. 决策逃避反模式**
- ❌ 提出开放问题："接下来做什么？"
- ✅ 分析可能方案，通过 `suggest` 提供选项
- ✅ 主动用 `list_files`/`search_files` 探索
- ✅ 将找到的选项提供给用户确认

### 异常处理指南

#### 异常处理速查表

| 异常类型 | 推荐工具 | 处理策略 |
|----------|----------|----------|
| **文件不存在** | `list_files` → `ask_followup_question` | 确认路径或创建文件 |
| **权限不足** | `ask_followup_question` | 请求权限或切换方案 |
| **工具失败** | `execute_command` → `read_file` | 查看错误日志并重试 |
| **信息不足** | `ask_followup_question` | 收集必要参数 |
| **复杂度过高** | `sequentialthinking` → `new_task` | 分解任务或委派 |
| **依赖缺失** | `execute_command` → `ask_followup_question` | 安装依赖或调整方案 |
| **配置错误** | `read_file` → `apply_diff` | 修正配置文件 |
| **网络问题** | `execute_command` → `ask_followup_question` | 重试或离线方案 |

#### 异常处理工作流

**步骤 1: 识别异常**
```yaml
触发: 工具执行失败或返回错误
操作: 分析错误类型和原因
```

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

### 性能优化技巧

#### 批量操作优化
- 单个 `apply_diff` 处理多个修改（使用多个 SEARCH/REPLACE 块）
- 合并多个 `read_file` 请求（最多 5 个文件）
- 使用 `search_and_replace` 替代多次 `apply_diff`

#### 决策优化
- 前置重要决策，避免返工
- 批量收集信息后统一决策
- 使用决策矩阵减少决策次数

#### 工具链优化
- 优先使用内建工具而非 `execute_command`
- 复用工具组合模式
- 避免重复读取未修改的文件
