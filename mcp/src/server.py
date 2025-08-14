# -*- coding: utf-8 -*-
"""
This module implements the core MCP server logic.

It listens for JSON-RPC 2.0 requests via stdin, processes them,
and sends responses to stdout. Logging is directed to stderr.
"""

import json
import logging
import sys
from typing import Any, Callable, Dict, Union

from src.tools import memory, timestamp


def run_server() -> None:
    """
    Runs the main server loop, processing JSON-RPC requests from stdin.

    This function continuously listens for incoming data, parses it as
    JSON-RPC, dispatches to the appropriate tool, and returns the result.
    """
    tools: Dict[str, Callable[..., Any]] = {
        "get_timestamp": timestamp.get_timestamp,
        "memory-init-workspace": memory.memory_init_workspace,
        "memory-query-kb": memory.memory_query_kb,
        "memory-update-context": memory.memory_update_context,
        "memory-add-to-kb": memory.memory_add_to_kb,
        "memory-cleanup-workspace": memory.memory_cleanup_workspace,
        "memory-get-status": memory.memory_get_status,
        "memory-dump": memory.memory_dump,
        "memory-search": memory.memory_search,
        "memory-backup": memory.memory_backup,
        "memory-restore": memory.memory_restore,
    }

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
