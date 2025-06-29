import os
import platform
import tempfile
from pathlib import Path
import appdirs
import psutil

from config import app_name
from croe import mcp

@mcp.tool(
	name="user_home_directory",
	title="Get User Home Directory",
	description="Get the path to the user's home directory",
)
async def user_home_directory() -> str:
	return str(Path.home())

@mcp.tool(
	name="hostname",
	title="Get Hostname",
	description="Get the hostname of the machine",
)
async def hostname() -> str:
	return os.uname().nodename

@mcp.tool(
	name="user_config_directory",
	title="Get User Config Directory",
	description="Get the path to the user's config directory",
)
async def user_config_directory() -> str:
	return appdirs.user_config_dir(appname=app_name)

@mcp.tool(
	name="user_cache_directory",
	title="Get User Cache Directory",
	description="Get the path to the user's cache directory",
)
async def user_cache_directory() -> str:
	return appdirs.user_cache_dir(appname=app_name)

@mcp.tool(
	name="temp_directory",
	title="Get Temp Directory",
	description="Get the path to the temporary directory",
)
async def temp_directory() -> str:
	return tempfile.gettempdir()

@mcp.tool(
	name="os",
	title="Get OS",
	description="Get the OS",
)
async def os() -> str:
	return platform.system()

@mcp.tool(
	name="os_arch",
	title="Get Arch",
	description="Get the arch",
)
async def os_arch() -> str:
	return platform.machine()

@mcp.tool(
	name="os_version",
	title="Get OS Version",
	description="Get the OS version",
)
async def os_version() -> str:
	return platform.version()

@mcp.tool(
	name="cpu_count",
	title="Get CPU Count",
	description="Get the number of CPUs",
)
async def cpu_count() -> int:
	return os.cpu_count()

@mcp.tool(
	name="cpu_freq",
	title="Get CPU Frequency",
	description="Get the CPU frequency",
)
async def cpu_freq() -> float:
	return psutil.cpu_freq().current

@mcp.tool(
	name="cpu_percent",
	title="Get CPU Percent",
	description="Get the CPU percent",
)
async def cpu_percent() -> float:
	return psutil.cpu_percent()

@mcp.tool(
	name="mem_total",
	title="Get Memory Total",
	description="Get the total memory",
)
async def mem_total() -> int:
	return psutil.virtual_memory().total

@mcp.tool(
	name="mem_percent",
	title="Get Memory Percent",
	description="Get the memory percent",
)
async def mem_percent() -> float:
	return psutil.virtual_memory().percent

@mcp.tool(
	name="mem_used",
	title="Get Memory Used",
	description="Get the memory used",
)
async def mem_used() -> int:
	return psutil.virtual_memory().used

@mcp.tool(
	name="disk_total",
	title="Get Disk Total",
	description="Get the disk total",
)
async def disk_total() -> int:
	return psutil.disk_usage("/").total

@mcp.tool(
	name="disk_usage",
	title="Get Disk Usage",
	description="Get the disk usage",
)
async def disk_usage(path: str = "") -> dict:
	return psutil.disk_usage(path)

@mcp.tool(
	name="disk_partitions",
	title="Get Disk Partitions",
	description="Get the disk partitions",
)
async def disk_partitions(all: bool = False) -> list:
	return psutil.disk_partitions(all)