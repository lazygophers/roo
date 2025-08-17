# 配置管理

本文档旨在阐述本应用的配置策略，并详细说明所有相关的配置参数。

## 1. 配置策略

本应用采用了一套分层的配置系统，其优先级顺序如下：

1.  **环境变量 (最高优先级)**: 在应用运行时注入的设置。
2.  **配置文件 (`config.yaml`)**: 应用的基础配置文件。
3.  **代码内默认值 (最低优先级)**: 在源代码中定义的备用值。

## 2. 核心应用配置

这些参数直接控制应用的核心功能。

| 参数         | 环境变量                | `config.yaml` 键  | 默认值 | 描述                                 |
| :----------- | :---------------------- | :---------------- | :----- | :----------------------------------- |
| SearX 主机   | `SEARX_HOSTS`           | `searx_hosts`     | `[]`   | 用于负载均衡的 SearX 实例 URL 列表。 |
| 启用缓存     | `SEARX_CACHE_ENABLED`   | `cache_enabled`   | `true` | 启用或禁用对 SearX 请求的缓存。      |
| 缓存有效期   | `SEARX_CACHE_TTL`       | `cache_ttl`       | `3600` | 缓存的存活时间（秒）。               |
| 内存缓存     | `SEARX_CACHE_MEMORY_MB` | `cache_memory_mb` | `50`   | 最大内存缓存的大小（MB）。           |
| 磁盘缓存     | `SEARX_CACHE_DISK_MB`   | `cache_disk_mb`   | `200`  | 最大磁盘缓存的大小（MB）。           |
| 请求超时     | `SEARX_TIMEOUT`         | `timeout`         | `10`   | 对 SearX API 的请求超时时间（秒）。  |
| 最大重试次数 | `SEARX_MAX_RETRIES`     | `max_retries`     | `3`    | 请求失败时的最大重试次数。           |

### 命令行参数

| 参数      | 描述                 |
| :-------- | :------------------- |
| `--debug` | 启用详细的调试日志。 |

## 3. 部署与环境

本部分描述了应用的构建和运行环境。

- **部署单元**: 应用被打包成一个名为 `lazygopher` 的独立可执行文件，并置于一个极简的 Docker 镜像中 (`gcr.io/distroless/cc-debian12`)。
- **服务启动**: 该 Docker 镜像 (`lazygopher:latest`) 被配置为一个名为 `github` 的 MCP 服务器来运行。
- **启动命令**: `docker run --rm -it lazygopher:latest`
- **工具权限**: `get_pull_request` 工具被默认允许执行。

## 4. 项目依赖

核心依赖项在 `pyproject.toml` 文件中进行管理。

- **核心依赖**: `pyyaml`, `pydantic`, `requests`
- **开发工具**: `hatchling`, `black`, `ruff`, `pytest`
