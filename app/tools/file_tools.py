"""
文件工具集
使用装饰器自动注册文件相关的MCP工具
"""
from app.tools.registry import file_tool, mcp_category


# 注册文件工具分类
@mcp_category(
    category_id="file",
    name="文件操作工具",
    description="文件读写、路径处理、文件管理等文件系统操作工具",
    icon="📁",
    enabled=True,
    sort_order=3
)
def register_file_category():
    """注册文件工具分类"""
    pass


@file_tool(
    name="read",
    description="Read file content from specified path",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "File path"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding",
                "default": "utf-8"
            },
            "max_lines": {
                "type": "integer",
                "description": "Maximum lines to read (0 means unlimited)",
                "default": 0,
                "minimum": 0
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["file", "read", "content"],
        "examples": [
            {"file_path": "config.yaml"},
            {"file_path": "/etc/hosts", "encoding": "utf-8"},
            {"file_path": "large_file.txt", "max_lines": 100}
        ]
    }
)
def read():
    """Read file content from specified path"""
    pass


@file_tool(
    name="write",
    description="Write content to file at specified path",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "File path"
            },
            "content": {
                "type": "string",
                "description": "Content to write"
            },
            "encoding": {
                "type": "string",
                "description": "File encoding",
                "default": "utf-8"
            },
            "mode": {
                "type": "string",
                "description": "Write mode",
                "enum": ["write", "append"],
                "default": "write"
            },
            "create_dirs": {
                "type": "boolean",
                "description": "Auto create directories",
                "default": True
            }
        },
        "required": ["file_path", "content"]
    },
    metadata={
        "tags": ["file", "write", "create"],
        "examples": [
            {"file_path": "output.txt", "content": "Hello World"},
            {"file_path": "log.txt", "content": "New entry\\n", "mode": "append"}
        ]
    }
)
def write():
    """Write content to file at specified path"""
    pass


@file_tool(
    name="ls_dir",
    description="List files and subdirectories in specified directory",
    schema={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Directory path"
            },
            "show_hidden": {
                "type": "boolean",
                "description": "Show hidden files",
                "default": False
            },
            "recursive": {
                "type": "boolean",
                "description": "Recursively list subdirectories",
                "default": False
            },
            "file_info": {
                "type": "boolean",
                "description": "Include detailed file information",
                "default": False
            }
        },
        "required": ["directory_path"]
    },
    metadata={
        "tags": ["directory", "file_list", "browse"],
        "examples": [
            {"directory_path": "."},
            {"directory_path": "/home/user", "show_hidden": True},
            {"directory_path": "src", "recursive": True, "file_info": True}
        ]
    }
)
def ls_dir():
    """List files and subdirectories in specified directory"""
    pass


@file_tool(
    name="new_dir",
    description="Create new directory (supports creating nested directories)",
    schema={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "Directory path to create"
            },
            "parents": {
                "type": "boolean",
                "description": "Create parent directories",
                "default": True
            }
        },
        "required": ["directory_path"]
    },
    metadata={
        "tags": ["directory", "create", "folder"],
        "examples": [
            {"directory_path": "new_folder"},
            {"directory_path": "path/to/deep/folder", "parents": True}
        ]
    }
)
def new_dir():
    """Create new directory (supports creating nested directories)"""
    pass


@file_tool(
    name="del_file",
    description="Delete specified file or empty directory",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "Path to file or directory to delete"
            },
            "force": {
                "type": "boolean",
                "description": "Force delete (including non-empty directories)",
                "default": False
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["delete", "file", "directory"],
        "examples": [
            {"file_path": "temp.txt"},
            {"file_path": "temp_folder", "force": True}
        ]
    }
)
def del_file():
    """Delete specified file or empty directory"""
    pass


@file_tool(
    name="info",
    description="Get detailed information of file or directory",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "File or directory path"
            },
            "checksum": {
                "type": "boolean",
                "description": "Calculate file checksum",
                "default": False
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["file_info", "properties", "status"],
        "examples": [
            {"file_path": "document.pdf"},
            {"file_path": "important.txt", "checksum": True}
        ]
    }
)
def info():
    """Get detailed information of file or directory"""
    pass


@file_tool(
    name="get_sec_info",
    description="Get file tool security configuration, including accessible directory permissions",
    schema={
        "type": "object",
        "properties": {
            "config_type": {
                "type": "string",
                "description": "Configuration type",
                "enum": ["readable", "writable", "forbidden", "limits"],
                "default": "readable"
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Paths to query (empty returns all configurations)",
                "default": []
            }
        },
        "required": []
    },
    metadata={
        "tags": ["security", "config", "permissions", "directory_management"],
        "examples": [
            {"config_type": "readable", "paths": ["/home/user", "/tmp"]},
            {"config_type": "forbidden", "paths": ["/etc", "/bin"]}
        ]
    }
)
def get_sec_info():
    """Get file tool security configuration, including accessible directory permissions"""
    pass


@file_tool(
    name="update_sec_limits",
    description="Update file security limit configuration (max file size, max read lines, strict mode)",
    schema={
        "type": "object",
        "properties": {
            "limit_type": {
                "type": "string",
                "description": "Limit type",
                "enum": ["max_file_size", "max_read_lines", "strict_mode"]
            },
            "value": {
                "description": "Limit value (size in bytes, lines as integer, strict mode as boolean)"
            }
        },
        "required": ["limit_type", "value"]
    },
    metadata={
        "tags": ["security", "config", "limits", "parameter_setting"],
        "examples": [
            {"limit_type": "max_file_size", "value": 104857600},
            {"limit_type": "max_read_lines", "value": 5000},
            {"limit_type": "strict_mode", "value": True}
        ]
    }
)
def update_sec_limits():
    """Update file security limit configuration (max file size, max read lines, strict mode)"""
    pass


@file_tool(
    name="reload_sec_config",
    description="Reload file security configuration (refresh in-memory config from database)",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["security", "config", "reload"],
        "examples": [{}]
    }
)
def reload_sec_config():
    """Reload file security configuration (refresh in-memory config from database)"""
    pass