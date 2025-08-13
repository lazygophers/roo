# MCP 服务使用说明

本文件旨在提供 roo 系统中集成的各类 MCP（Model-Copilot-Protocol）服务的基础用法说明和示例，以帮助开发者快速理解和上手使用。

## 服务概览

### Sequential Thinking (Mcp)

- **用途**：复杂问题的逐步分析
- **适用场景**：需求分析、方案设计、问题排查
- **使用时机**：当你遇到复杂逻辑或多步骤问题时

#### 基础用例

当你需要规划一个多步骤任务时，可以这样使用：

```xml
<use_mcp_tool>
  <server_name>sequentialthinking</server_name>
  <tool_name>sequentialthinking</tool_name>
  <arguments>
  {
    "thought": "第一步：分析我需求，明确核心目标是构建一个基于 Web 的实时聊天应用。",
    "nextThoughtNeeded": true,
    "thoughtNumber": 1,
    "totalThoughts": 5
  }
  </arguments>
</use_mcp_tool>
```

### Context 7 (Mcp)

- **用途**：查询最新的技术文档、API 参考和代码示例
- **适用场景**：技术调研、最佳实践获取
- **使用时机**：当你需要了解新技术或验证实现方案时

#### 基础用例

当你需要查找相关文档时，可以这样使用：

```xml
<use_mcp_tool>
  <server_name>context7</server_name>
  <tool_name>get-library-docs</tool_name>
  <arguments>
  {
    "context7CompatibleLibraryID": "/facebook/react",
    "topic": "hooks"
  }
  </arguments>
</use_mcp_tool>
```

### DeepWiki (Mcp)

- **用途**：检索背景知识、行业术语、常见架构和设计模式
- **适用场景**：研究、构思阶段需要理解技术原理和通识
- **使用时机**：当你遇到术语不清、原理未知、需引入通用范式时

#### 基础用例

当你需要了解“微服务架构”的基本概念时，可以这样使用：

```xml
<use_mcp_tool>
  <server_name>deepwiki</server_name>
  <tool_name>deepwiki_fetch</tool_name>
  <arguments>
  {
    "url": "微服务架构"
  }
  </arguments>
</use_mcp_tool>
```
