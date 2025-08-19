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
4.  **建议的数量与排序**: 默认提供不少于 5 个 `suggest` 选项（越多越好），并将最推荐的选项置于首位。

**性能优化**

- **批量操作**:
  - 单个 `apply_diff` 处理多个修改
  - 合并多个 `read_file` 请求（最多 5 个）
  - 使用 `search_and_replace` 替代多次 `apply_diff`
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
