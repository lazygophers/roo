"""
系统工具集
使用装饰器自动注册系统相关的MCP工具
"""
import os
import platform
import psutil
import time
from typing import Dict, Any
from app.tools.registry import system_tool


@system_tool(
    name="get_info",
    description="Get LazyAI Studio system information including CPU, memory, OS, etc.",
    schema={
        "type": "object",
        "properties": {
            "detailed": {
                "type": "boolean",
                "description": "Return detailed information",
                "default": True
            },
            "include_performance": {
                "type": "boolean",
                "description": "Include performance metrics",
                "default": False
            }
        },
        "required": []
    },
    metadata={
        "tags": ["system", "monitoring", "performance", "LazyGophers"],
        "examples": [
            {"detailed": False},
            {"detailed": True, "include_performance": True}
        ]
    }
)
def get_info(detailed: bool = True, include_performance: bool = False):
    """Get LazyAI Studio system information including CPU, memory, OS, etc."""
    try:
        system_info: Dict[str, Any] = {
            "application": "LazyAI Studio - LazyGophers Organization",
            "timestamp": int(time.time()),
            "platform": {
                "system": platform.system(),
                "release": platform.release(),
                "version": platform.version(),
                "machine": platform.machine(),
                "processor": platform.processor()
            }
        }

        if detailed:
            # CPU information
            cpu_info = {
                "physical_cores": psutil.cpu_count(logical=False),
                "total_cores": psutil.cpu_count(logical=True),
                "max_frequency": f"{psutil.cpu_freq().max:.2f} MHz" if psutil.cpu_freq() else "Unknown",
                "current_frequency": f"{psutil.cpu_freq().current:.2f} MHz" if psutil.cpu_freq() else "Unknown"
            }

            # Memory information
            memory = psutil.virtual_memory()
            memory_info = {
                "total": f"{memory.total / (1024**3):.2f} GB",
                "available": f"{memory.available / (1024**3):.2f} GB",
                "used": f"{memory.used / (1024**3):.2f} GB",
                "percentage": f"{memory.percent}%"
            }

            # Disk information
            disk = psutil.disk_usage('/')
            disk_info = {
                "total": f"{disk.total / (1024**3):.2f} GB",
                "used": f"{disk.used / (1024**3):.2f} GB",
                "free": f"{disk.free / (1024**3):.2f} GB",
                "percentage": f"{(disk.used / disk.total) * 100:.1f}%"
            }

            system_info.update({
                "cpu": cpu_info,
                "memory": memory_info,
                "disk": disk_info,
                "python_version": platform.python_version(),
                "hostname": platform.node()
            })

        if include_performance:
            # Performance metrics
            performance_info = {
                "cpu_usage": f"{psutil.cpu_percent(interval=1)}%",
                "memory_usage": f"{psutil.virtual_memory().percent}%",
                "disk_io": psutil.disk_io_counters()._asdict() if psutil.disk_io_counters() else {},
                "network_io": psutil.net_io_counters()._asdict() if psutil.net_io_counters() else {},
                "boot_time": psutil.boot_time(),
                "load_average": os.getloadavg() if hasattr(os, 'getloadavg') else "Not available"
            }
            system_info["performance"] = performance_info

        return system_info

    except Exception as e:
        return f"Error getting system information: {str(e)}"