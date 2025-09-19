import os
import time
import psutil
import json
import asyncio
from datetime import datetime
from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from typing import Dict, Any

router = APIRouter()

# 记录应用启动时间
start_time = time.time()

@router.get(
    "/system/monitor",
    summary="获取系统性能监控信息",
    description="获取应用的CPU使用率、内存使用量、运行时间等性能指标"
)
async def get_system_monitor() -> Dict[str, Any]:
    """获取系统性能监控信息"""
    try:
        # 获取当前进程
        process = psutil.Process(os.getpid())
        
        # 计算运行时间
        uptime_seconds = time.time() - start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_seconds = int(uptime_seconds % 60)
        
        # 获取CPU使用率（过去1秒的平均值）
        cpu_percent = process.cpu_percent(interval=0.1)
        
        # 获取内存使用信息
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB
        
        # 获取系统总内存
        system_memory = psutil.virtual_memory()
        memory_percent = (memory_info.rss / system_memory.total) * 100
        
        # 计算响应时间（简单的处理时间）
        response_start = time.time()
        
        return {
            "success": True,
            "data": {
                "uptime": {
                    "seconds": uptime_seconds,
                    "formatted": f"{uptime_hours:02d}:{uptime_minutes:02d}:{uptime_seconds:02d}",
                    "total_seconds": int(time.time() - start_time)
                },
                "cpu": {
                    "percent": round(cpu_percent, 1),
                    "usage": f"{cpu_percent:.1f}%"
                },
                "memory": {
                    "used_mb": round(memory_mb, 1),
                    "used_bytes": memory_info.rss,
                    "percent": round(memory_percent, 2),
                    "formatted": f"{memory_mb:.1f} MB ({memory_percent:.1f}%)"
                },
                "response_time": {
                    "ms": round((time.time() - response_start) * 1000, 2)
                },
                "process": {
                    "pid": os.getpid(),
                    "name": process.name(),
                    "status": process.status(),
                    "create_time": process.create_time(),
                    "num_threads": process.num_threads()
                },
                "timestamp": datetime.now().isoformat(),
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "uptime": {"formatted": "00:00:00"},
                "cpu": {"usage": "0.0%"},
                "memory": {"formatted": "0.0 MB"},
                "response_time": {"ms": 0}
            }
        }


@router.get(
    "/system/health",
    summary="获取系统健康状况",
    description="获取详细的系统健康检查信息"
)
async def get_system_health() -> Dict[str, Any]:
    """获取系统健康状况"""
    try:
        process = psutil.Process(os.getpid())
        
        # 检查各种健康指标
        health_checks = {
            "process_running": True,
            "memory_usage_ok": process.memory_percent() < 80,  # 内存使用率小于80%
            "cpu_usage_ok": process.cpu_percent(interval=0.1) < 90,  # CPU使用率小于90%
            "uptime_ok": (time.time() - start_time) > 10  # 运行时间大于10秒
        }
        
        overall_health = all(health_checks.values())
        
        return {
            "success": True,
            "healthy": overall_health,
            "checks": health_checks,
            "status": "healthy" if overall_health else "warning",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        return {
            "success": False,
            "healthy": False,
            "error": str(e),
            "status": "error",
            "timestamp": datetime.now().isoformat()
        }


@router.get(
    "/system/stats",
    summary="获取性能统计信息",
    description="获取CPU、内存、磁盘等详细统计信息"
)
async def get_system_stats() -> Dict[str, Any]:
    """获取详细的系统统计信息"""
    try:
        # 获取系统整体信息
        cpu_count = psutil.cpu_count()
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # 获取当前进程信息
        process = psutil.Process(os.getpid())
        
        return {
            "success": True,
            "data": {
                "system": {
                    "cpu_count": cpu_count,
                    "cpu_usage": psutil.cpu_percent(interval=0.1),
                    "memory_total": memory.total,
                    "memory_available": memory.available,
                    "memory_percent": memory.percent,
                    "disk_total": disk.total,
                    "disk_free": disk.free,
                    "disk_percent": (disk.used / disk.total) * 100
                },
                "process": {
                    "cpu_percent": process.cpu_percent(interval=0.1),
                    "memory_info": process.memory_info()._asdict(),
                    "memory_percent": process.memory_percent(),
                    "num_threads": process.num_threads(),
                    "num_fds": process.num_fds() if hasattr(process, 'num_fds') else 0,
                    "status": process.status()
                },
                "timestamp": datetime.now().isoformat()
            }
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


def get_system_monitor_data() -> Dict[str, Any]:
    """获取系统监控数据（内部函数）"""
    try:
        # 获取当前进程
        process = psutil.Process(os.getpid())

        # 计算运行时间
        uptime_seconds = time.time() - start_time
        uptime_hours = int(uptime_seconds // 3600)
        uptime_minutes = int((uptime_seconds % 3600) // 60)
        uptime_seconds = int(uptime_seconds % 60)

        # 获取CPU使用率（过去1秒的平均值）
        cpu_percent = process.cpu_percent(interval=0.1)

        # 获取内存使用信息
        memory_info = process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024  # 转换为MB

        # 获取系统总内存
        system_memory = psutil.virtual_memory()
        memory_percent = (memory_info.rss / system_memory.total) * 100

        # 计算响应时间（简单的处理时间）
        response_start = time.time()

        return {
            "success": True,
            "data": {
                "uptime": {
                    "seconds": uptime_seconds,
                    "formatted": f"{uptime_hours:02d}:{uptime_minutes:02d}:{uptime_seconds:02d}",
                    "total_seconds": int(time.time() - start_time)
                },
                "cpu": {
                    "percent": round(cpu_percent, 1),
                    "usage": f"{cpu_percent:.1f}%"
                },
                "memory": {
                    "used_mb": round(memory_mb, 1),
                    "used_bytes": memory_info.rss,
                    "percent": round(memory_percent, 2),
                    "formatted": f"{memory_mb:.1f} MB ({memory_percent:.1f}%)"
                },
                "response_time": {
                    "ms": round((time.time() - response_start) * 1000, 2)
                },
                "process": {
                    "pid": os.getpid(),
                    "name": process.name(),
                    "status": process.status(),
                    "create_time": process.create_time(),
                    "num_threads": process.num_threads()
                },
                "timestamp": datetime.now().isoformat(),
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        }

    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "data": {
                "uptime": {"formatted": "00:00:00"},
                "cpu": {"usage": "0.0%"},
                "memory": {"formatted": "0.0 MB"},
                "response_time": {"ms": 0}
            }
        }


async def generate_monitor_events():
    """SSE事件生成器"""
    while True:
        try:
            # 获取监控数据
            data = get_system_monitor_data()

            # 格式化为SSE事件
            json_data = json.dumps(data)
            yield f"data: {json_data}\n\n"

            # 等待2秒再发送下一组数据
            await asyncio.sleep(2)

        except Exception as e:
            # 发送错误事件
            error_data = {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            yield f"data: {json.dumps(error_data)}\n\n"
            await asyncio.sleep(5)  # 错误时等待更长时间


@router.get(
    "/system/monitor/stream",
    summary="获取实时系统监控数据流",
    description="通过Server-Sent Events (SSE)获取实时系统性能监控数据"
)
async def stream_system_monitor():
    """SSE方式获取实时系统监控数据"""
    return StreamingResponse(
        generate_monitor_events(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
        }
    )