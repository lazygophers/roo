# Searx 代理与缓存 MCP 服务

这是一个基于 Python 的 MCP (Model-Copilot-Protocol) 服务，其核心功能是作为 Searx 的代理，提供负载均衡、请求缓存和统一入口。项目通过标准输入/输出 (stdio) 进行通信，并使用 `uv` 进行包管理，已完全容器化，可通过 Docker 快速部署。

## 功能特性

- **Searx 代理**: 代理对多个 Searx 实例的请求，提供负载均衡和故障转移。
- **高级缓存**: 支持内存和磁盘两级缓存，可大幅提升重复查询的响应速度，详情请见 [docs/cache.md](docs/cache.md)。
- **灵活配置**: 支持通过 `config.yaml` 和环境变量进行配置，详情请见 [docs/config.md](docs/config.md)。
- **MCP/stdio 通信**: 通过 JSON-RPC 2.0 协议在 stdio 上进行通信。
- **uv 包管理**: 使用现代化、高速的 `uv` 工具来管理 Python 依赖。
- **Docker 支持**: 提供多阶段 `Dockerfile`，用于构建轻量级、安全的生产镜像。
- **Debug 模式**: 支持 `--debug` 标志，用于输出详细的日志信息，方便开发和调试。
- **非 Root 容器**: Docker 容器默认使用非 root 用户运行，增强安全性。
- **核心工具集**: 提供 `search`, `search_suggestions`, `get_cache_info` 等一系列围绕 Searx 的核心工具...
- **文件操作工具集**: 提供 `read_file`, `write_file`, `list_files`, `delete_file` 等文件操作工具，但仅在非 Docker 环境下可用。

## 本地运行

请确保您已安装 Python 3.12+ 和 `uv`。

1.  **初始化环境**

    ```shell
    uv sync
    ```

2.  **运行服务**

    执行主脚本来启动服务：

    ```shell
    uv run main.py
    ```

    要以 debug 模式运行，请添加 `--debug` 标志：

    ```shell
    uv run main.py --debug
    ```

## 配置

项目主要通过 `config.yaml` 文件和环境变量进行配置。您可以设置 Searx 实例、缓存策略、日志级别等。

详细的配置选项和说明，请参阅 [`docs/config.md`](docs/config.md)。

## Docker 运行

1.  **构建 Docker 镜像**

    在项目根目录中，使用以下命令构建镜像。我们将镜像命名为 `lazygopher`。

    ```shell
    docker build -t lazygopher .
    ```

2.  **运行 Docker 容器**

    以交互模式 (`-i`) 运行容器，以便我们可以通过 stdin 发送请求：

    ```shell
    docker run -i --rm lazygopher
    ```

## 如何使用

该服务通过 stdin 接收 JSON-RPC 2.0 请求。您可以调用 `get_timestamp` 和 `search` 等工具。

#### 示例 1: 获取秒级时间戳（基础示例）

1.  **准备请求**

    创建一个名为 `request_timestamp.json` 的文件，内容如下。

    ```json
    {
      "jsonrpc": "2.0",
      "method": "get_timestamp",
      "params": {},
      "id": 1
    }
    ```

2.  **发送请求**

    ```shell
    cat request_timestamp.json | uv run main.py
    ```

3.  **预期响应**

    ```json
    { "jsonrpc": "2.0", "result": 1755063481, "id": 1 }
    ```

#### 示例 2: 使用 Searx 进行查询（核心功能）

1.  **准备请求**

    创建一个名为 `request_search.json` 的文件，指定查询关键词和可选参数（如 `categories`）。

    ```json
    {
      "jsonrpc": "2.0",
      "method": "search",
      "params": {
        "query": "What is Model-Copilot-Protocol?",
        "categories": "general"
      },
      "id": 2
    }
    ```

2.  **发送请求**

    ```shell
    cat request_search.json | uv run main.py
    ```

3.  **预期响应**

    服务将返回一个包含搜索结果的 JSON 对象：

    ```json
    {
      "jsonrpc": "2.0",
      "result": {
        "query": "What is Model-Copilot-Protocol?",
        "results": [
          {
            "title": "MCP: A Protocol for Copilot-Model Communication",
            "url": "https://example.com/mcp-protocol",
            "content": "The Model-Copilot-Protocol (MCP) is a standardized communication protocol..."
          }
        ],
        "number_of_results": 1,
        "suggestions": ["mcp protocol", "model copilot protocol explained"]
      },
      "id": 2
    }
    ```

## 文件操作工具 (File Operation Tools)

本服务提供了一系列文件操作工具。为了更清晰地展示，我们将它们整理成如下表格：

| 工具 (Tool)         | 描述 (Description)                             |
| :------------------ | :--------------------------------------------- |
| `read_file`         | 读取指定文件的内容。                           |
| `write_file`        | 将内容写入指定文件，如果文件不存在则创建。     |
| `list_files`        | 列出指定目录下的文件和子目录。                 |
| `delete_file`       | 删除指定的文件或目录。                         |
| `move_file`         | 移动文件或目录到新的位置。                     |
| `copy_file`         | 复制文件或目录到新的位置。                     |
| `create_directory`  | 创建一个新的目录。                             |
| `get_file_metadata` | 获取文件或目录的元数据（如大小、修改时间等）。 |

**重要限制**:

- **可用性**: 这些工具仅在 **非 Docker 环境** 下加载和可用。
- **安全考量**: 当服务在 Docker 容器中运行时，这些文件操作工具将被 **完全禁用**。这是为了防止容器内的服务意外访问或修改宿主机的文件系统，从而确保系统的安全性和隔离性。

## MCP 服务配置样例

以下是一个 `mcp_server_config.json` 的配置示例，用于将名为 `github` 的 MCP 服务与一个 Docker 容器关联起来。

```json
{
  "mcpServers": {
    "github": {
      "command": "docker",
      "args": ["run", "--rm", "-it", "lazygopher:latest"],
      "alwaysAllow": ["get_pull_request"]
    }
  }
}
```

**关键字段说明:**

- `mcpServers`: 定义所有 MCP 服务的配置。
- `github`: 服务的唯一名称。
- `command`: 启动服务所需执行的命令（例如 `docker`, `python`）。
- `args`: 传递给 `command` 的参数列表。
- `alwaysAllow`: 一个工具名称的列表，这些工具在执行时将无需用户确认，可被自动授权。

## 工具文档

- [记忆库工具](./docs/tools/memory_tools.md)
