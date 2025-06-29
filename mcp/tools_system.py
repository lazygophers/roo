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
	return str(Path.home())

@mcp.tool()
async def hostname() -> str:
	return os.uname().nodename

@mcp.tool()
async def user_config_directory() -> str:
	return appdirs.user_config_dir(appname=app_name)

@mcp.tool()
async def user_cache_directory() -> str:
	return appdirs.user_cache_dir(appname=app_name)

@mcp.tool()
async def temp_directory() -> str:
	return tempfile.gettempdir()

@mcp.tool()
async def os() -> str:
	return platform.system()

@mcp.tool()
async def os_arch() -> str:
	return platform.machine()

@mcp.tool()
async def os_version() -> str:
	return platform.version()

@mcp.tool()
async def cpu_count() -> int:
	return os.cpu_count()

@mcp.tool()
async def cpu_freq() -> float:
	return psutil.cpu_freq().current

@mcp.tool()
async def cpu_percent() -> float:
	return psutil.cpu_percent()

@mcp.tool()
async def mem_total() -> int:
	return psutil.virtual_memory().total

@mcp.tool()
async def mem_percent() -> float:
	return psutil.virtual_memory().percent

@mcp.tool()
async def mem_used() -> int:
	return psutil.virtual_memory().used

@mcp.tool()
async def disk_total() -> int:
	return psutil.disk_usage("/").total

@mcp.tool()
async def disk_usage(path: str = "") -> dict:
	return psutil.disk_usage(path)

@mcp.tool()
async def disk_partitions(all: bool = False) -> list:
	return psutil.disk_partitions(all)