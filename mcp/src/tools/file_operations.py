# -*- coding: utf-8 -*-
"""
此模块提供了核心的文件操作功能，并将其封装为 MCP (Model-Controlled Program) Tools。
这些工具旨在提供一个标准化的接口来与文件系统进行交互，包括读写、列出和删除文件/目录。
每个函数都包含了健壮的错误处理，以应对文件不存在、权限问题等常见的 I/O 异常。

核心功能:
- read_file: 读取指定路径的文件内容。
- write_file: 将内容写入指定路径的文件。
- list_files: 列出指定目录的内容，支持递归。
- delete_file: 删除指定路径的文件或目录。

MCP Tool 封装:
- 每个核心函数都对应一个 MCP Tool 定义，包含了名称、描述和输入/输出模式。
- 所有 Tool 定义被收集在 `file_operation_tools` 列表中，以便于动态加载和使用。
"""

import os
import shutil
from typing import List, Dict, Any, Union, Callable

# 定义 MCP Tool 的基本结构
MCPTool = Dict[str, Any]

def read_file(path: str) -> str:
    """
    读取并返回文件的内容。

    Args:
        path (str): 目标文件的绝对或相对路径。

    Returns:
        str: 文件内容。

    Raises:
        FileNotFoundError: 如果文件在指定路径下不存在。
        PermissionError: 如果没有权限读取文件。
        Exception: 其他底层 I/O 错误。
    """
    try:
        with open(path, 'r', encoding='utf-8') as f:
            return f.read()
    except (FileNotFoundError, PermissionError) as e:
        # 重新抛出预期的异常，以便上层调用者可以进行精细化处理
        raise e
    except Exception as e:
        # 捕获其他可能的异常并封装
        raise IOError(f"读取文件 '{path}' 时发生未知错误: {e}") from e

def write_file(path: str, content: str) -> bool:
    """
    将指定内容写入文件。如果文件已存在，则覆盖；如果不存在，则创建。

    Args:
        path (str): 目标文件的路径。
        content (str): 要写入文件的内容。

    Returns:
        bool: 操作成功返回 True。

    Raises:
        PermissionError: 如果没有权限写入文件。
        Exception: 其他底层 I/O 错误。
    """
    try:
        # 确保目录存在
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except PermissionError as e:
        raise e
    except Exception as e:
        raise IOError(f"写入文件 '{path}' 时发生未知错误: {e}") from e

def list_files(path: str, recursive: bool = False) -> List[str]:
    """
    列出指定目录下的文件和子目录。

    Args:
        path (str): 目标目录的路径。
        recursive (bool): 如果为 True，则递归列出所有子目录的内容。
                          默认为 False。

    Returns:
        List[str]: 目录下的文件和目录名列表。

    Raises:
        FileNotFoundError: 如果目录不存在。
        PermissionError: 如果没有权限访问目录。
    """
    if not os.path.isdir(path):
        raise FileNotFoundError(f"目录不存在: '{path}'")
    if not os.access(path, os.R_OK):
        raise PermissionError(f"无权限访问目录: '{path}'")

    if recursive:
        result = []
        for root, dirs, files in os.walk(path):
            for name in files:
                result.append(os.path.join(root, name))
            for name in dirs:
                result.append(os.path.join(root, name))
        return result
    else:
        return os.listdir(path)

def delete_file(path: str) -> bool:
    """
    删除指定路径的文件或目录（及其内容）。

    Args:
        path (str): 要删除的文件或目录的路径。

    Returns:
        bool: 操作成功返回 True。

    Raises:
        FileNotFoundError: 如果文件或目录不存在。
        PermissionError: 如果没有权限删除。
    """
    try:
        if os.path.isfile(path) or os.path.islink(path):
            os.remove(path)
        elif os.path.isdir(path):
            shutil.rmtree(path)
        else:
            # 路径存在但既不是文件也不是目录（例如，损坏的符号链接）
            raise FileNotFoundError(f"路径存在但无法确定类型，无法删除: '{path}'")
        return True
    except FileNotFoundError:
        # 明确地重新抛出，因为这是一个预期的失败场景
        raise
    except PermissionError as e:
        raise e
    except Exception as e:
        raise IOError(f"删除 '{path}' 时发生未知错误: {e}") from e

def move_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    移动文件或目录到指定位置。

    Args:
        source_path (str): 要移动的源文件或目录的路径。
        destination_path (str): 目标路径。

    Returns:
        Dict[str, Any]: 包含操作状态和结果的字典。
    """
    if not os.path.exists(source_path):
        return {"status": "error", "message": f"Source file not found: {source_path}"}
    if os.path.exists(destination_path):
        return {"status": "error", "message": f"Destination already exists: {destination_path}"}
    try:
        shutil.move(source_path, destination_path)
        return {"status": "success", "destination_path": destination_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def copy_file(source_path: str, destination_path: str) -> Dict[str, Any]:
    """
    复制文件或目录到指定位置。

    Args:
        source_path (str): 要复制的源文件或目录的路径。
        destination_path (str): 目标路径。

    Returns:
        Dict[str, Any]: 包含操作状态和结果的字典。
    """
    if not os.path.exists(source_path):
        return {"status": "error", "message": f"Source file not found: {source_path}"}
    if os.path.exists(destination_path):
        return {"status": "error", "message": f"Destination already exists: {destination_path}"}
    try:
        if os.path.isdir(source_path):
            shutil.copytree(source_path, destination_path)
        else:
            shutil.copy2(source_path, destination_path)
        return {"status": "success", "destination_path": destination_path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def create_directory(path: str) -> Dict[str, Any]:
    """
    创建新目录，支持创建多级目录。

    Args:
        path (str): 要创建的目录的路径。

    Returns:
        Dict[str, Any]: 包含操作状态和结果的字典。
    """
    if os.path.exists(path):
        return {"status": "error", "message": f"Directory already exists: {path}"}
    try:
        os.makedirs(path)
        return {"status": "success", "directory_path": path}
    except Exception as e:
        return {"status": "error", "message": str(e)}

def get_file_metadata(path: str) -> Dict[str, Any]:
    """
    获取文件或目录的元数据。

    Args:
        path (str): 目标文件或目录的路径。

    Returns:
        Dict[str, Any]: 包含操作状态和元数据（如果成功）或错误信息的字典。
    """
    if not os.path.exists(path):
        return {"status": "error", "message": f"File not found: {path}"}
    try:
        stat_info = os.stat(path)
        metadata = {
            "file_path": os.path.abspath(path),
            "size_bytes": stat_info.st_size,
            "last_modified_time": stat_info.st_mtime,
            "created_time": stat_info.st_ctime,
            "is_directory": os.path.isdir(path),
            "is_file": os.path.isfile(path),
        }
        return {"status": "success", "metadata": metadata}
    except Exception as e:
        return {"status": "error", "message": str(e)}

# ==============================================================================
# MCP Tool Definitions
# ==============================================================================

read_file_tool: MCPTool = {
    "name": "read_file",
    "description": "读取并返回指定路径的文件的全部内容。适用于处理文本文件。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "需要读取的文件的完整路径。"
            }
        },
        "required": ["path"]
    }
}

write_file_tool: MCPTool = {
    "name": "write_file",
    "description": "将指定的文本内容写入文件。如果文件已存在，其内容将被覆盖。如果文件不存在，将创建新文件。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要写入的文件的完整路径。"
            },
            "content": {
                "type": "string",
                "description": "要写入文件的文本内容。"
            }
        },
        "required": ["path", "content"]
    }
}

list_files_tool: MCPTool = {
    "name": "list_files",
    "description": "列出指定目录下的所有文件和子目录。可以选择是否进行递归列出。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要列出其内容的目录的路径。"
            },
            "recursive": {
                "type": "boolean",
                "description": "如果为 True，则递归地列出所有子目录的内容。",
                "default": False
            }
        },
        "required": ["path"]
    }
}

delete_file_tool: MCPTool = {
    "name": "delete_file",
    "description": "删除指定路径的文件或目录。如果删除的是目录，其所有内容也将被一并删除。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要删除的文件或目录的完整路径。"
            }
        },
        "required": ["path"]
    }
}

move_file_tool: MCPTool = {
    "name": "move_file",
    "description": "移动文件或目录到新的位置。",
    "input_schema": {
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "要移动的源文件或目录的路径。"
            },
            "destination_path": {
                "type": "string",
                "description": "移动的目标路径。"
            }
        },
        "required": ["source_path", "destination_path"]
    }
}

copy_file_tool: MCPTool = {
    "name": "copy_file",
    "description": "复制文件或目录到新的位置。会保留文件的元数据。",
    "input_schema": {
        "type": "object",
        "properties": {
            "source_path": {
                "type": "string",
                "description": "要复制的源文件或目录的路径。"
            },
            "destination_path": {
                "type": "string",
                "description": "复制的目标路径。"
            }
        },
        "required": ["source_path", "destination_path"]
    }
}

create_directory_tool: MCPTool = {
    "name": "create_directory",
    "description": "创建一个新目录。如果父目录不存在，也会一并创建。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "要创建的目录的完整路径。"
            }
        },
        "required": ["path"]
    }
}

get_file_metadata_tool: MCPTool = {
    "name": "get_file_metadata",
    "description": "获取指定文件或目录的详细元数据。",
    "input_schema": {
        "type": "object",
        "properties": {
            "path": {
                "type": "string",
                "description": "目标文件或目录的路径。"
            }
        },
        "required": ["path"]
    }
}

# 将所有工具定义收集到一个字典中，以便于 MCP 服务器加载
# 键是工具名，值是对应的可调用函数
file_operation_tools: Dict[str, Callable] = {
    "read_file": read_file,
    "write_file": write_file,
    "list_files": list_files,
    "delete_file": delete_file,
    "move_file": move_file,
    "copy_file": copy_file,
    "create_directory": create_directory,
    "get_file_metadata": get_file_metadata,
}