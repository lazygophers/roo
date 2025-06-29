import os
import platform
import tempfile
from pathlib import Path
import appdirs
import psutil

from config import app_name
from croe import mcp


@mcp.tool()
async def user_home_directory() -> str:
    """获取当前用户的主目录路径。

    Returns:
        str: 用户主目录的字符串表示
    """
    return str(Path.home())


@mcp.tool()
async def hostname() -> str:
    """获取当前系统的主机名（节点名）。

    Returns:
        str: 系统的主机名
    """
    return os.uname().nodename


@mcp.tool()
async def user_config_directory() -> str:
    """获取用户配置目录路径。

    Returns:
        str: 用户配置目录路径字符串
    """
    return appdirs.user_config_dir(appname=app_name)


@mcp.tool()
async def user_cache_directory() -> str:
    return appdirs.user_cache_dir(appname=app_name)


@mcp.tool()
async def temp_directory() -> str:
    """获取系统的临时目录路径。

    Returns:
        str: 系统的临时目录路径字符串
    """
    return tempfile.gettempdir()


@mcp.tool()
async def os() -> str:
    """获取操作系统名称。

    Returns:
        str: 操作系统名称（如：Linux/Windows/Darwin）
    """
    return platform.system()


@mcp.tool()
async def os_arch() -> str:
    """获取操作系统的架构。

    Returns:
        str: 系统架构（如：x86_64/aarch64）
    """
    return platform.machine()


@mcp.tool()
async def os_version() -> str:
    """获取操作系统版本信息。

    Returns:
        str: 操作系统具体版本字符串
    """
    return platform.version()


@mcp.tool()
async def cpu_count() -> int:
    """获取系统中的CPU核心数量。

    Returns:
        int: 逻辑CPU核心总数
    """
    return os.cpu_count()


@mcp.tool()
async def cpu_freq() -> float:
    """获取当前CPU频率。

    Returns:
        float: 当前CPU频率（单位：MHz）
    """
    return psutil.cpu_freq().current


@mcp.tool()
async def cpu_percent() -> float:
    """获取当前CPU使用百分比。

    Returns:
        float: CPU使用百分比（0.0-100.0）
    """
    return psutil.cpu_percent()


@mcp.tool()
async def mem_total() -> int:
    """获取系统总内存容量。

    Returns:
        int: 总内存大小（单位：字节）
    """
    return psutil.virtual_memory().total


@mcp.tool()
async def mem_percent() -> float:
    """获取当前内存使用百分比。

    Returns:
        float: 内存使用百分比（0.0-100.0）
    """
    return psutil.virtual_memory().percent


@mcp.tool()
async def mem_used() -> int:
    """获取已使用的内存量。

    Returns:
        int: 已使用内存大小（单位：字节）
    """
    return psutil.virtual_memory().used


@mcp.tool()
async def disk_total() -> int:
    """获取根目录所在磁盘的总空间大小。

    Returns:
        int: 磁盘总空间（单位：字节）
    """
    return psutil.disk_usage("/").total


@mcp.tool()
async def disk_usage(path: str = "") -> dict:
    """获取指定路径的磁盘使用情况。

    Args:
        path (str, optional): 要查询的路径，默认为空字符串（根目录）

    Returns:
        dict: 包含total、used、free等键的磁盘使用情况字典
    """
    return psutil.disk_usage(path)


@mcp.tool()
async def disk_partitions(all: bool = False) -> list:
    """获取磁盘分区信息列表。

    Args:
        all (bool, optional): 是否包含所有分区，默认False

    Returns:
        list: 磁盘分区信息列表
    """
    return psutil.disk_partitions(all)


# 新增系统运行时间（秒）
@mcp.tool()
async def system_uptime() -> int:
    """获取系统持续运行时间。

    Returns:
        int: 系统启动以来的秒数
    """
    return int(psutil.boot_time())


# 新增网络接口信息
@mcp.tool()
async def network_interfaces() -> dict:
    """获取网络接口详细信息。

    Returns:
        dict: 网络接口名称到地址信息的映射字典
    """
    return psutil.net_if_addrs()


# 新增运行中的进程列表
@mcp.tool()
async def running_processes() -> list:
    """获取当前运行中的进程列表及其资源使用情况。

    Returns:
        list: 进程信息字典列表，包含以下字段：
            - pid (int): 进程ID
            - name (str): 进程名称
            - status (str): 进程状态
            - cpu_percent (float): CPU使用百分比
            - memory_percent (float): 内存使用百分比
    """
    return [
        {
            "pid": p.info["pid"],
            "name": p.info["name"],
            "status": p.info["status"],
            "cpu_percent": p.info["cpu_percent"],
            "memory_percent": p.info["memory_percent"],
        }
        for p in psutil.process_iter(
            ["pid", "name", "status", "cpu_percent", "memory_percent"]
        )
    ]
