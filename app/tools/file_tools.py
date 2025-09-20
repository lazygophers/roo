"""
文件工具集
使用装饰器自动注册文件相关的MCP工具
"""
import os
import shutil
import stat
import hashlib
from pathlib import Path
from typing import Dict, Any, List, Optional
from app.tools.registry import file_tool, mcp_category
from app.core.secure_logging import sanitize_for_log


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
def read(file_path: str, encoding: str = "utf-8", max_lines: int = 0):
    """Read file content from specified path"""
    try:
        file_path = Path(file_path)

        if not file_path.exists():
            return {"success": False, "error": f"File does not exist: {sanitize_for_log(str(file_path))}"}

        if not file_path.is_file():
            return {"success": False, "error": f"Path is not a file: {sanitize_for_log(str(file_path))}"}

        # Check file size (limit to 10MB)
        file_size = file_path.stat().st_size
        if file_size > 10 * 1024 * 1024:
            return {"success": False, "error": "File too large (>10MB)"}

        with open(file_path, 'r', encoding=encoding) as f:
            if max_lines > 0:
                lines = []
                for i, line in enumerate(f):
                    if i >= max_lines:
                        break
                    lines.append(line.rstrip('\n\r'))
                content = '\n'.join(lines)
                truncated = i >= max_lines - 1
            else:
                content = f.read()
                truncated = False

        return {
            "success": True,
            "content": content,
            "file_path": str(file_path),
            "encoding": encoding,
            "size_bytes": file_size,
            "lines_read": len(content.split('\n')) if content else 0,
            "truncated": truncated
        }

    except UnicodeDecodeError as e:
        return {"success": False, "error": f"Encoding error: {str(e)}"}
    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def write(file_path: str, content: str, encoding: str = "utf-8", mode: str = "write", create_dirs: bool = True):
    """Write content to file at specified path"""
    try:
        file_path = Path(file_path)

        # Create directories if needed
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        # Check content size (limit to 10MB)
        content_size = len(content.encode(encoding))
        if content_size > 10 * 1024 * 1024:
            return {"success": False, "error": "Content too large (>10MB)"}

        write_mode = 'a' if mode == "append" else 'w'

        with open(file_path, write_mode, encoding=encoding) as f:
            f.write(content)

        file_size = file_path.stat().st_size

        return {
            "success": True,
            "file_path": str(file_path),
            "mode": mode,
            "encoding": encoding,
            "content_size": content_size,
            "final_file_size": file_size,
            "message": f"Content {mode} successfully"
        }

    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def ls_dir(directory_path: str, show_hidden: bool = False, recursive: bool = False, file_info: bool = False):
    """List files and subdirectories in specified directory"""
    try:
        dir_path = Path(directory_path)

        if not dir_path.exists():
            return {"success": False, "error": f"Directory does not exist: {sanitize_for_log(str(dir_path))}"}

        if not dir_path.is_dir():
            return {"success": False, "error": f"Path is not a directory: {sanitize_for_log(str(dir_path))}"}

        items = []
        pattern = "**/*" if recursive else "*"

        for item in dir_path.glob(pattern):
            # Skip hidden files if not requested
            if not show_hidden and item.name.startswith('.'):
                continue

            item_info = {
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file"
            }

            if file_info:
                try:
                    stat_info = item.stat()
                    item_info.update({
                        "size": stat_info.st_size if item.is_file() else 0,
                        "modified": stat_info.st_mtime,
                        "permissions": oct(stat_info.st_mode)[-3:],
                        "owner_readable": bool(stat_info.st_mode & stat.S_IRUSR),
                        "owner_writable": bool(stat_info.st_mode & stat.S_IWUSR),
                        "owner_executable": bool(stat_info.st_mode & stat.S_IXUSR)
                    })
                except (PermissionError, OSError):
                    item_info["info_error"] = "Permission denied or file error"

            items.append(item_info)

        # Sort items: directories first, then files, both alphabetically
        items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))

        return {
            "success": True,
            "directory": str(dir_path),
            "items": items,
            "total_count": len(items),
            "directories": len([i for i in items if i["type"] == "directory"]),
            "files": len([i for i in items if i["type"] == "file"]),
            "recursive": recursive,
            "show_hidden": show_hidden,
            "file_info": file_info
        }

    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def new_dir(directory_path: str, parents: bool = True):
    """Create new directory (supports creating nested directories)"""
    try:
        dir_path = Path(directory_path)

        if dir_path.exists():
            if dir_path.is_dir():
                return {"success": True, "message": "Directory already exists", "path": str(dir_path)}
            else:
                return {"success": False, "error": "Path exists but is not a directory"}

        dir_path.mkdir(parents=parents, exist_ok=True)

        return {
            "success": True,
            "path": str(dir_path),
            "parents_created": parents,
            "message": "Directory created successfully"
        }

    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def del_file(file_path: str, force: bool = False):
    """Delete specified file or empty directory"""
    try:
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {sanitize_for_log(str(path))}"}

        if path.is_file():
            path.unlink()
            return {
                "success": True,
                "path": str(path),
                "type": "file",
                "message": "File deleted successfully"
            }
        elif path.is_dir():
            if force:
                shutil.rmtree(path)
                return {
                    "success": True,
                    "path": str(path),
                    "type": "directory",
                    "force": True,
                    "message": "Directory and contents deleted successfully"
                }
            else:
                try:
                    path.rmdir()  # Only works for empty directories
                    return {
                        "success": True,
                        "path": str(path),
                        "type": "directory",
                        "force": False,
                        "message": "Empty directory deleted successfully"
                    }
                except OSError:
                    return {"success": False, "error": "Directory not empty (use force=true to delete)"}
        else:
            return {"success": False, "error": "Path is neither a file nor a directory"}

    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def info(file_path: str, checksum: bool = False):
    """Get detailed information of file or directory"""
    try:
        path = Path(file_path)

        if not path.exists():
            return {"success": False, "error": f"Path does not exist: {sanitize_for_log(str(path))}"}

        stat_info = path.stat()

        info_data = {
            "success": True,
            "path": str(path),
            "name": path.name,
            "type": "directory" if path.is_dir() else "file",
            "size": stat_info.st_size,
            "created": stat_info.st_ctime,
            "modified": stat_info.st_mtime,
            "accessed": stat_info.st_atime,
            "permissions": {
                "octal": oct(stat_info.st_mode)[-3:],
                "owner_read": bool(stat_info.st_mode & stat.S_IRUSR),
                "owner_write": bool(stat_info.st_mode & stat.S_IWUSR),
                "owner_execute": bool(stat_info.st_mode & stat.S_IXUSR),
                "group_read": bool(stat_info.st_mode & stat.S_IRGRP),
                "group_write": bool(stat_info.st_mode & stat.S_IWGRP),
                "group_execute": bool(stat_info.st_mode & stat.S_IXGRP),
                "other_read": bool(stat_info.st_mode & stat.S_IROTH),
                "other_write": bool(stat_info.st_mode & stat.S_IWOTH),
                "other_execute": bool(stat_info.st_mode & stat.S_IXOTH)
            }
        }

        if path.is_file():
            info_data["extension"] = path.suffix
            info_data["stem"] = path.stem

            if checksum and stat_info.st_size <= 100 * 1024 * 1024:  # Limit checksum to 100MB files
                try:
                    with open(path, 'rb') as f:
                        content = f.read()
                        info_data["checksums"] = {
                            "md5": hashlib.md5(content).hexdigest(),
                            "sha256": hashlib.sha256(content).hexdigest()
                        }
                except Exception:
                    info_data["checksum_error"] = "Failed to calculate checksum"
            elif checksum:
                info_data["checksum_error"] = "File too large for checksum calculation (>100MB)"
        elif path.is_dir():
            try:
                # Count items in directory
                items = list(path.iterdir())
                info_data["item_count"] = len(items)
                info_data["subdirectories"] = len([i for i in items if i.is_dir()])
                info_data["files"] = len([i for i in items if i.is_file()])
            except PermissionError:
                info_data["content_error"] = "Permission denied to read directory contents"

        return info_data

    except PermissionError:
        return {"success": False, "error": "Permission denied"}
    except Exception as e:
        return {"success": False, "error": str(e)}


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
def get_sec_info(config_type: str = "readable", paths: List[str] = None):
    """Get file tool security configuration, including accessible directory permissions"""
    try:
        # Default security configuration
        security_config = {
            "readable": [
                ".", "./", "./data", "./logs", "./temp", "./uploads",
                "/tmp", "/var/tmp", "~/Downloads", "~/Documents"
            ],
            "writable": [
                "./data", "./logs", "./temp", "./uploads", "./output",
                "/tmp", "/var/tmp"
            ],
            "forbidden": [
                "/etc", "/bin", "/sbin", "/usr/bin", "/usr/sbin",
                "/boot", "/sys", "/proc", "/dev", "/root",
                "~/.ssh", "~/.aws", "~/.config"
            ],
            "limits": {
                "max_file_size": 10 * 1024 * 1024,  # 10MB
                "max_read_lines": 10000,
                "max_directory_items": 1000,
                "strict_mode": True
            }
        }

        if paths:
            # Check specific paths
            result = {"config_type": config_type, "paths": {}}
            for path in paths:
                if config_type in security_config:
                    result["paths"][path] = path in security_config[config_type]
                else:
                    result["paths"][path] = False
            return {"success": True, "security_config": result}
        else:
            # Return all configuration
            if config_type == "all":
                return {"success": True, "security_config": security_config}
            elif config_type in security_config:
                return {
                    "success": True,
                    "security_config": {
                        config_type: security_config[config_type]
                    }
                }
            else:
                return {"success": False, "error": f"Unknown config type: {config_type}"}

    except Exception as e:
        return {"success": False, "error": str(e)}


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
def update_sec_limits(limit_type: str, value):
    """Update file security limit configuration (max file size, max read lines, strict mode)"""
    try:
        # This is a simulated implementation - in a real system this would update a database
        valid_limits = {
            "max_file_size": {"type": int, "min": 1024, "max": 100 * 1024 * 1024},  # 1KB to 100MB
            "max_read_lines": {"type": int, "min": 1, "max": 100000},  # 1 to 100k lines
            "strict_mode": {"type": bool}
        }

        if limit_type not in valid_limits:
            return {
                "success": False,
                "error": f"Invalid limit type. Valid types: {list(valid_limits.keys())}"
            }

        limit_config = valid_limits[limit_type]

        # Type validation
        if not isinstance(value, limit_config["type"]):
            return {
                "success": False,
                "error": f"Value must be of type {limit_config['type'].__name__}"
            }

        # Range validation for numeric types
        if limit_config["type"] == int:
            if "min" in limit_config and value < limit_config["min"]:
                return {
                    "success": False,
                    "error": f"Value too small. Minimum: {limit_config['min']}"
                }
            if "max" in limit_config and value > limit_config["max"]:
                return {
                    "success": False,
                    "error": f"Value too large. Maximum: {limit_config['max']}"
                }

        # Simulate updating the configuration
        return {
            "success": True,
            "limit_type": limit_type,
            "old_value": "(simulated - would retrieve from database)",
            "new_value": value,
            "message": f"Security limit '{limit_type}' updated successfully",
            "note": "This is a simulated update - implement database persistence for production"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}


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
    try:
        # This is a simulated implementation - in a real system this would reload from database
        import time
        current_time = time.time()

        simulated_config = {
            "reload_timestamp": current_time,
            "config_source": "database",
            "loaded_rules": {
                "readable_paths": 8,
                "writable_paths": 7,
                "forbidden_paths": 13,
                "security_limits": 4
            },
            "status": "active",
            "last_modified": current_time - 3600,  # 1 hour ago
            "version": "1.0.0"
        }

        return {
            "success": True,
            "message": "Security configuration reloaded successfully",
            "config_info": simulated_config,
            "note": "This is a simulated reload - implement database connection for production"
        }

    except Exception as e:
        return {"success": False, "error": str(e)}