# Python MCP 服务

这是一个基于 Python 的 MCP (Model-Copilot-Protocol) 服务模板，它通过标准输入/输出 (stdio) 进行通信，并使用 `uv` 进行包管理。项目已完全容器化，可通过 Docker 快速部署。

## 功能特性

- **MCP/stdio 通信**: 通过 JSON-RPC 2.0 协议在 stdio 上进行通信。
- **uv 包管理**: 使用现代化、高速的 `uv` 工具来管理 Python 依赖。
- **Docker 支持**: 提供多阶段 `Dockerfile`，用于构建轻量级、安全的生产镜像。
- **Debug 模式**: 支持 `--debug` 标志，用于输出详细的日志信息，方便开发和调试。
- **非 Root 容器**: Docker 容器默认使用非 root 用户运行，增强安全性。
- **工具示例**: 包含一个可配置的 `get_timestamp` 工具，支持秒级和毫秒级时间戳。

- **记忆工具集**: 提供一套完整的 `memory-*` 工具，用于管理和操作记忆库，详情请见 [`memory.md`](dosc/memory.md)。

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

## Docker 运行

1.  **构建 Docker 镜像**

    在项目根目录中，使用以下命令构建镜像。我们将镜像命名为 `python-mcp-server`。

    ```shell
    docker build -t python-mcp-server .
    ```

2.  **运行 Docker 容器**

    以交互模式 (`-i`) 运行容器，以便我们可以通过 stdin 发送请求：

    ```shell
    docker run -i --rm python-mcp-server
    ```

## 如何使用

该服务通过 stdin 接收 JSON-RPC 2.0 请求。您可以根据需求调用 `get_timestamp` 工具。

#### 示例 1: 获取秒级时间戳（默认）

1.  **准备请求**

    创建一个名为 `request_seconds.json` 的文件，内容如下。`params` 为空对象时，默认返回秒级时间戳。

    ```json
    {
      "jsonrpc": "2.0",
      "method": "get_timestamp",
      "params": {},
      "id": 1
    }
    ```

2.  **发送请求**

    无论是本地运行还是通过 Docker 运行，您都可以使用 `cat` 和管道将请求发送到服务：

    ```shell
    cat request_seconds.json | python main.py
    ```

    或者对于 Docker 容器：

    ```shell
    cat request_seconds.json | docker run -i --rm python-mcp-server
    ```

3.  **预期响应**

    服务将返回一个以秒为单位的 **整数** Unix 时间戳：

    ```json
    { "jsonrpc": "2.0", "result": 1755063481, "id": 1 }
    ```

#### 示例 2: 获取毫秒级时间戳

1.  **准备请求**

    创建一个名为 `request_milliseconds.json` 的文件，将 `milliseconds` 参数设置为 `true`。

    ```json
    {
      "jsonrpc": "2.0",
      "method": "get_timestamp",
      "params": {
        "milliseconds": true
      },
      "id": 2
    }
    ```

2.  **发送请求**

    ```shell
    cat request_milliseconds.json | python main.py
    ```

    或者对于 Docker 容器：

    ```shell
    cat request_milliseconds.json | docker run -i --rm python-mcp-server
    ```

3.  **预期响应**

    服务将返回一个以毫秒为单位的 **整数** Unix 时间戳：

    ```json
    { "jsonrpc": "2.0", "result": 1755063481123, "id": 2 }
    ```

## MCP 服务配置样例

`mcp_services.examples.yaml` 文件展示了如何配置 MCP 服务。核心变更是，所有服务现在都统一在 `mcpServers` 顶级键下进行管理。

每个服务都作为 `mcpServers` 对象的一个子属性，以其唯一的服务名（例如 `uv`）作为键。这种结构使得配置更加清晰和模块化。

以下是一个配置示例，展示了 `uv` 服务的具体设置：

```yaml
mcpServers:
  # 'uv' 服务示例
  # 该服务通过 'uv mcp' 命令启动，当前处于启用状态。
  uv:
    type: stdio
    command: uv
    args: ["mcp"]
    disabled: false
```

**关键字段说明:**

- **`type`**: 定义服务的通信方式（例如 `stdio`）。
- **`command`**: 启动服务所需执行的命令。
- **`args`**: 传递给命令的参数列表。
- **`disabled`**: 一个布尔值，用于控制该服务是否启用。`false` 表示启用，`true` 表示禁用。

您可以参考此结构，将示例复制到您自己的配置文件中，并根据需求进行调整，以快速设置和管理您的 MCP 服务。
