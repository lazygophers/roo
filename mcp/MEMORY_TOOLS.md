# Memory Tools API 参考文档

本文档详细介绍了记忆库（Memory）相关工具的 API 接口，旨在为开发者提供清晰、准确的调用指南。所有接口均遵循 JSON-RPC 2.0 规范。

[TOC]

## `memory_init_workspace`

### 功能描述

为指定的任务 ID 创建一个隔离的、全新的工作区目录。这通常是处理新任务时的第一个步骤，用于存放该任务相关的所有临时文件和状态。

### 参数

| 参数名    | 类型   | 描述                   | 是否必须 |
| --------- | ------ | ---------------------- | -------- |
| `task_id` | `string` | 当前任务的唯一标识符。 | 是       |

### 返回值

成功执行后，返回一个包含工作区路径的 JSON 对象。

| 字段   | 类型   | 描述                     |
| ------ | ------ | ------------------------ |
| `path` | `string` | 创建成功的工作区的绝对路径。 |

### JSON-RPC 2.0 示例

#### 请求

```json
{
  "jsonrpc": "2.0",
  "method": "memory_init_workspace",
  "params": {
    "task_id": "task-12345-abcde"
  },
  "id": 1
}
```

#### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "path": "/tmp/nexus_workspace/task-12345-abcde"
  },
  "id": 1
}
```

## `memory_add`

### 功能描述

向知识库中添加一个新的知识条目。每个条目包含具体内容、一份简短的摘要和一组用于检索的标签。

### 参数

| 参数名    | 类型            | 描述                         | 是否必须 |
| --------- | --------------- | ---------------------------- | -------- |
| `content` | `string`        | 知识条目的详细内容。         | 是       |
| `summary` | `string`        | 对内容的简短摘要。           | 是       |
| `tags`    | `array[string]` | 一组用于分类和检索的标签。   | 否       |

### 返回值

成功添加后，返回一个包含新创建的知识条目 ID 和摘要的 JSON 对象。

| 字段      | 类型     | 描述                   |
| --------- | -------- | ---------------------- |
| `id`      | `string` | 新知识条目的唯一标识符。 |
| `summary` | `string` | 添加的知识条目的摘要。   |

### JSON-RPC 2.0 示例

#### 请求

```json
{
  "jsonrpc": "2.0",
  "method": "memory_add",
  "params": {
    "content": "Docker 是一个开源的应用容器引擎，让开发者可以打包他们的应用以及依赖包到一个可移植的容器中。",
    "summary": "Docker 容器化技术",
    "tags": ["docker", "container", "devops"]
  },
  "id": 2
}
```

#### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "id": "kb-generated-uuid",
    "summary": "Docker 容器化技术"
  },
  "id": 2
}
```

## `memory_query`

### 功能描述

根据提供的关键词在知识库中进行检索。系统会返回与关键词最匹配的知识条目列表。

### 参数

| 参数名    | 类型   | 描述                     | 是否必须 |
| --------- | ------ | ------------------------ | -------- |
| `query`   | `string` | 用于检索的查询关键词。   | 是       |
| `top_k`   | `integer`| 返回最匹配的结果数量，默认为 3。 | 否       |

### 返回值

返回一个包含匹配结果列表的 JSON 对象。

| 字段      | 类型          | 描述                                                         |
| --------- | ------------- | ------------------------------------------------------------ |
| `results` | `array[object]` | 匹配的知识条目列表，每个条目包含 `id`, `summary`, `content`。 |

### JSON-RPC 2.0 示例

#### 请求

```json
{
  "jsonrpc": "2.0",
  "method": "memory_query",
  "params": {
    "query": "python http",
    "top_k": 1
  },
  "id": 3
}
```

#### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "results": [
      {
        "id": "kb-001",
        "summary": "Python HTTP 请求库",
        "content": "在 Python 中，使用 `requests` 库可以方便地发送 HTTP 请求。"
      }
    ]
  },
  "id": 3
}
```

## `memory_delete`

### 功能描述

从知识库中删除一个指定的知识条目。

### 参数

| 参数名 | 类型   | 描述                       | 是否必须 |
| ------ | ------ | -------------------------- | -------- |
| `kb_id`  | `string` | 要删除的知识条目的唯一标识符。 | 是       |

### 返回值

成功删除后，返回一个包含确认信息和被删除条目 ID 的 JSON 对象。

| 字段      | 类型     | 描述                     |
| --------- | -------- | ------------------------ |
| `status`  | `string` | 操作结果，例如 "success"。 |
| `id`      | `string` | 被删除的知识条目的 ID。    |

### JSON-RPC 2.0 示例

#### 请求

```json
{
  "jsonrpc": "2.0",
  "method": "memory_delete",
  "params": {
    "kb_id": "kb-002"
  },
  "id": 4
}
```

#### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "id": "kb-002"
  },
  "id": 4
}
```

## `memory_cleanup`

### 功能描述

清理指定任务的工作区。此操作会永久删除与任务 ID 相关联的整个目录及其所有内容，用于在任务完成后释放资源。

### 参数

| 参数名    | 类型   | 描述                         | 是否必须 |
| --------- | ------ | ---------------------------- | -------- |
| `task_id` | `string` | 需要清理其工作区的任务的唯一标识符。 | 是       |

### 返回值

成功清理后，返回一个包含确认信息的 JSON 对象。

| 字段     | 类型     | 描述                     |
| -------- | -------- | ------------------------ |
| `status` | `string` | 操作结果，例如 "success"。 |
| `path`   | `string` | 已被删除的工作区的路径。   |

### JSON-RPC 2.0 示例

#### 请求

```json
{
  "jsonrpc": "2.0",
  "method": "memory_cleanup",
  "params": {
    "task_id": "task-12345-abcde"
  },
  "id": 5
}
```

#### 成功响应

```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "success",
    "path": "/tmp/nexus_workspace/task-12345-abcde"
  },
  "id": 5
}
## 管理工具

### `memory_get_status`

#### 功能描述

检查内存模块的整体运行状态。此工具用于快速诊断知识库和工作区是否正常加载和运行。

#### 参数

此工具无需任何参数。

#### 返回值

返回一个包含当前内存状态信息的 JSON 对象。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `status` | `string` | 整体状态，通常为 "ok"。 |
| `kb_status` | `string` | 知识库状态，例如 "loaded" 或 "unloaded"。 |
| `workspace_status` | `string` | 工作区状态，例如 "clean" (无活动工作区) 或 "active" (有活动工作区)。 |

#### JSON-RPC 2.0 示例

##### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "memory_get_status",
  "params": {},
  "id": 6
}
```

##### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "kb_status": "loaded",
    "workspace_status": "active"
  },
  "id": 6
}
```

### `memory_dump`

#### 功能描述

导出指定内存层级的完整内容。此工具主要用于调试，可以帮助开发者查看知识库或特定工作区的当前状态。

#### 参数

| 参数名 | 类型 | 描述 | 是否必须 |
| --- | --- | --- | --- |
| `level` | `string` | 要导出的内存层级。可选值为 'kb', 'workspace', 'all'。默认为 'all'。 | 否 |

#### 返回值

返回一个包含导出数据和状态的 JSON 对象。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `status` | `string` | 操作结果，例如 "ok"。 |
| `data` | `object` | 包含导出内容的 JSON 对象。其结构取决于 `level` 参数。 |

#### JSON-RPC 2.0 示例

##### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "memory_dump",
  "params": {
    "level": "kb"
  },
  "id": 7
}
```

##### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "data": {
      "kb-001": {
        "content": "在 Python 中，使用 `requests` 库可以方便地发送 HTTP 请求。",
        "summary": "Python HTTP 请求库",
        "tags": ["python", "http", "requests"]
      }
    }
  },
  "id": 7
}
```

### `memory_search`

#### 功能描述

在指定的内存层级中，根据关键词进行全局搜索。可用于在知识库和所有工作区中快速定位信息。

#### 参数

| 参数名 | 类型 | 描述 | 是否必须 |
| --- | --- | --- | --- |
| `query` | `string` | 用于搜索的查询关键词。 | 是 |
| `level` | `string` | 要搜索的内存层级。可选值为 'kb', 'workspace', 'all'。默认为 'all'。 | 否 |

#### 返回值

返回一个包含搜索结果列表的 JSON 对象。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `status` | `string` | 操作结果，例如 "ok"。 |
| `results` | `array[object]` | 匹配的条目列表。每个条目包含 `source`, `key`, 和 `value`。 |

#### JSON-RPC 2.0 示例

##### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "memory_search",
  "params": {
    "query": "fastapi",
    "level": "kb"
  },
  "id": 8
}
```

##### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "results": [
      {
        "source": "kb",
        "key": "kb-003",
        "value": {
          "content": "FastAPI 是一个现代、快速（高性能）的 Web 框架，用于构建 API。",
          "summary": "Python Web 框架",
          "tags": ["python", "fastapi", "web"]
        }
      }
    ]
  },
  "id": 8
}
```

### `memory_backup`

#### 功能描述

创建当前整个内存状态（包括知识库和所有工作区）的快照，并将其保存到一个带时间戳的备份文件中。

#### 参数

此工具无需任何参数。

#### 返回值

返回一个包含操作状态和备份文件路径的 JSON 对象。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `status` | `string` | 操作结果，例如 "ok"。 |
| `message` | `string` | 操作的描述性消息。 |
| `backup_path` | `string` | 生成的备份文件的绝对路径。 |

#### JSON-RPC 2.0 示例

##### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "memory_backup",
  "params": {},
  "id": 9
}
```

##### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "message": "Backup successful.",
    "backup_path": ".memory/backups/memory_backup_20250813_120000.json"
  },
  "id": 9
}
```

### `memory_restore`

#### 功能描述

从一个指定的备份文件中恢复整个内存状态。这是一个破坏性操作，将使用备份文件中的数据完全覆盖当前的知识库和工作区。

#### 参数

| 参数名 | 类型 | 描述 | 是否必须 |
| --- | --- | --- | --- |
| `backup_path` | `string` | 要从中恢复的备份文件的路径。 | 是 |

#### 返回值

返回一个包含操作状态和确认信息的 JSON 对象。

| 字段 | 类型 | 描述 |
| --- | --- | --- |
| `status` | `string` | 操作结果，例如 "ok"。 |
| `message` | `string` | 操作的描述性消息。 |

#### JSON-RPC 2.0 示例

##### 请求
```json
{
  "jsonrpc": "2.0",
  "method": "memory_restore",
  "params": {
    "backup_path": ".memory/backups/memory_backup_20250813_120000.json"
  },
  "id": 10
}
```

##### 成功响应
```json
{
  "jsonrpc": "2.0",
  "result": {
    "status": "ok",
    "message": "从 .memory/backups/memory_backup_20250813_120000.json 恢复成功"
  },
  "id": 10
}
```