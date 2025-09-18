"""
文件工具集
使用装饰器自动注册文件相关的MCP工具
"""
from app.core.mcp_tool_registry import file_tool


@file_tool(
    name="read",
    description="读取指定路径的文件内容",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件路径"
            },
            "encoding": {
                "type": "string",
                "description": "文件编码",
                "default": "utf-8"
            },
            "max_lines": {
                "type": "integer",
                "description": "最大读取行数（0表示无限制）",
                "default": 0,
                "minimum": 0
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["文件", "读取", "内容"],
        "examples": [
            {"file_path": "config.yaml"},
            {"file_path": "/etc/hosts", "encoding": "utf-8"},
            {"file_path": "large_file.txt", "max_lines": 100}
        ]
    }
)
def read():
    """读取指定路径的文件内容"""
    pass


@file_tool(
    name="write",
    description="写入内容到指定路径的文件",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "要写入的内容"
            },
            "encoding": {
                "type": "string",
                "description": "文件编码",
                "default": "utf-8"
            },
            "mode": {
                "type": "string",
                "description": "写入模式",
                "enum": ["write", "append"],
                "default": "write"
            },
            "create_dirs": {
                "type": "boolean",
                "description": "是否自动创建目录",
                "default": True
            }
        },
        "required": ["file_path", "content"]
    },
    metadata={
        "tags": ["文件", "写入", "创建"],
        "examples": [
            {"file_path": "output.txt", "content": "Hello World"},
            {"file_path": "log.txt", "content": "New entry\\n", "mode": "append"}
        ]
    }
)
def write():
    """写入内容到指定路径的文件"""
    pass


@file_tool(
    name="ls_dir",
    description="列出指定目录下的文件和子目录",
    schema={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "目录路径"
            },
            "show_hidden": {
                "type": "boolean",
                "description": "是否显示隐藏文件",
                "default": False
            },
            "recursive": {
                "type": "boolean",
                "description": "是否递归列出子目录",
                "default": False
            },
            "file_info": {
                "type": "boolean",
                "description": "是否包含文件详细信息",
                "default": False
            }
        },
        "required": ["directory_path"]
    },
    metadata={
        "tags": ["目录", "文件列表", "浏览"],
        "examples": [
            {"directory_path": "."},
            {"directory_path": "/home/user", "show_hidden": True},
            {"directory_path": "src", "recursive": True, "file_info": True}
        ]
    }
)
def ls_dir():
    """列出指定目录下的文件和子目录"""
    pass


@file_tool(
    name="new_dir",
    description="创建新目录（支持创建多级目录）",
    schema={
        "type": "object",
        "properties": {
            "directory_path": {
                "type": "string",
                "description": "要创建的目录路径"
            },
            "parents": {
                "type": "boolean",
                "description": "是否创建父目录",
                "default": True
            }
        },
        "required": ["directory_path"]
    },
    metadata={
        "tags": ["目录", "创建", "文件夹"],
        "examples": [
            {"directory_path": "new_folder"},
            {"directory_path": "path/to/deep/folder", "parents": True}
        ]
    }
)
def new_dir():
    """创建新目录（支持创建多级目录）"""
    pass


@file_tool(
    name="del_file",
    description="删除指定的文件或空目录",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "要删除的文件或目录路径"
            },
            "force": {
                "type": "boolean",
                "description": "强制删除（包括非空目录）",
                "default": False
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["删除", "文件", "目录"],
        "examples": [
            {"file_path": "temp.txt"},
            {"file_path": "temp_folder", "force": True}
        ]
    }
)
def del_file():
    """删除指定的文件或空目录"""
    pass


@file_tool(
    name="info",
    description="获取文件或目录的详细信息",
    schema={
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "文件或目录路径"
            },
            "checksum": {
                "type": "boolean",
                "description": "是否计算文件校验和",
                "default": False
            }
        },
        "required": ["file_path"]
    },
    metadata={
        "tags": ["文件信息", "属性", "状态"],
        "examples": [
            {"file_path": "document.pdf"},
            {"file_path": "important.txt", "checksum": True}
        ]
    }
)
def info():
    """获取文件或目录的详细信息"""
    pass


@file_tool(
    name="get_sec_info",
    description="获取文件工具安全配置信息，包括可访问的目录权限设置",
    schema={
        "type": "object",
        "properties": {
            "config_type": {
                "type": "string",
                "description": "配置类型",
                "enum": ["readable", "writable", "forbidden", "limits"],
                "default": "readable"
            },
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "要查询的路径列表（为空时返回所有配置）",
                "default": []
            }
        },
        "required": []
    },
    metadata={
        "tags": ["安全", "配置", "权限", "目录管理"],
        "examples": [
            {"config_type": "readable", "paths": ["/home/user", "/tmp"]},
            {"config_type": "forbidden", "paths": ["/etc", "/bin"]}
        ]
    }
)
def get_sec_info():
    """获取文件工具安全配置信息，包括可访问的目录权限设置"""
    pass


@file_tool(
    name="update_sec_limits",
    description="更新文件安全限制配置（最大文件大小、最大读取行数、严格模式）",
    schema={
        "type": "object",
        "properties": {
            "limit_type": {
                "type": "string",
                "description": "限制类型",
                "enum": ["max_file_size", "max_read_lines", "strict_mode"]
            },
            "value": {
                "description": "限制值（大小为字节数，行数为整数，严格模式为布尔值）"
            }
        },
        "required": ["limit_type", "value"]
    },
    metadata={
        "tags": ["安全", "配置", "限制", "参数设置"],
        "examples": [
            {"limit_type": "max_file_size", "value": 104857600},
            {"limit_type": "max_read_lines", "value": 5000},
            {"limit_type": "strict_mode", "value": True}
        ]
    }
)
def update_sec_limits():
    """更新文件安全限制配置（最大文件大小、最大读取行数、严格模式）"""
    pass


@file_tool(
    name="reload_sec_config",
    description="重新加载文件安全配置（从数据库刷新内存中的配置）",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["安全", "配置", "重载"],
        "examples": [{}]
    }
)
def reload_sec_config():
    """重新加载文件安全配置（从数据库刷新内存中的配置）"""
    pass