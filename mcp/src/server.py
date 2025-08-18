"""
This module implements the core MCP server logic.

It listens for JSON-RPC 2.0 requests via stdin, processes them,
and sends responses to stdout. Logging is directed to stderr.
"""

import json
import logging
import sys
from collections.abc import Callable
from typing import Any

from src.tools import file_operations, memory, searx, timestamp
from src.utils.env_detector import is_running_in_docker


def get_tools() -> dict[str, Callable[..., Any]]:
    """
    构建并返回 MCP 服务器可用的工具集。

    根据运行环境（是否在 Docker 内），此函数会条件性地加载文件操作工具。

    :return: 一个从工具名映射到其可调用函数的字典。
    """
    # 基础工具集
    tools: dict[str, Callable[..., Any]] = {
        "get_timestamp": timestamp.get_timestamp,
        "searx_search": searx.search,
        "searx_suggestions": searx.search_suggestions,
        "searx_engines": searx.get_supported_engines,
        "save_core_memory": memory.save_core_memory,
        "save_knowledge_memory": memory.save_knowledge_memory,
        "save_working_memory": memory.save_working_memory,
        "search_memory": memory.search_memory,
        "get_memory_status": memory.get_memory_status,
        "set_memory_status": memory.set_memory_status,
    }

    # 条件性地加载文件操作工具
    if not is_running_in_docker():
        logging.info("非 Docker 环境，启用文件操作工具。")
        tools.update(file_operations.file_operation_tools)
    else:
        logging.info("Docker 环境，文件操作工具已禁用。")

    return tools


def run_server() -> None:
    """
    运行主服务器循环，处理来自 stdin 的 JSON-RPC 请求。

    此函数持续监听输入数据，将其解析为 JSON-RPC，分派给相应的工具，
    并返回结果。
    """
    tools = get_tools()

    for line in sys.stdin:
        if not line.strip():
            logging.info("Received empty line, assuming stdin closed. Exiting.")
            break

        request_id = None
        try:
            request = json.loads(line)
            request_id = request.get("id")

            if not all(k in request for k in ["jsonrpc", "method", "id"]):
                raise ValueError("Invalid JSON-RPC request structure.")

            if request["jsonrpc"] != "2.0":
                raise ValueError("Invalid JSON-RPC version.")

            method_name = request["method"]
            params = request.get("params", {})

            if method_name not in tools:
                raise NotImplementedError(f"Method '{method_name}' not found.")

            logging.info("Dispatching method '%s' with params: %s", method_name, params)
            tool_function = tools[method_name]

            # Assuming for now that params are passed as a dict
            result = tool_function(**params) if isinstance(params, dict) else tool_function(*params)

            response = {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id,
            }

        except json.JSONDecodeError:
            logging.error("Failed to decode JSON from stdin: %s", line.strip())
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32700, "message": "Parse error"},
                "id": request_id,
            }
        except (ValueError, TypeError, NotImplementedError) as e:
            logging.error("Error processing request: %s", e)
            error_code = -32601 if isinstance(e, NotImplementedError) else -32600
            response = {
                "jsonrpc": "2.0",
                "error": {"code": error_code, "message": str(e)},
                "id": request_id,
            }
        except Exception as e:
            logging.exception("An unexpected error occurred: %s", e)
            response = {
                "jsonrpc": "2.0",
                "error": {"code": -32603, "message": f"Internal error: {e}"},
                "id": request_id,
            }

        # Ensure response is a dictionary before sending
        if isinstance(response, dict):
            json.dump(response, sys.stdout)
            sys.stdout.write("\n")
            sys.stdout.flush()

    logging.info("Server loop finished.")
