"""
超高性能命令API路由
Ultra Performance Commands API Router
"""

import time
import asyncio
from typing import List, Dict, Any
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import ORJSONResponse

from app.models.schemas import CommandsResponse
from app.core.ultra_performance_service import get_ultra_commands_service, get_ultra_cache
from app.core.logging import setup_logging

logger = setup_logging("INFO")
router = APIRouter(default_response_class=ORJSONResponse)

# 获取服务实例
commands_service = get_ultra_commands_service()
cache = get_ultra_cache()


@router.post(
    "/commands",
    response_model=CommandsResponse,
    summary="获取所有命令 - 超高性能版本",
    response_class=ORJSONResponse
)
async def get_commands_ultra() -> CommandsResponse:
    """超高性能获取所有命令"""
    start_time = time.perf_counter()
    
    try:
        cache_key = "ultra_commands_response"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Ultra-fast commands response: {processing_time:.2f}ms (cached)")
            return cached_response
        
        commands = commands_service.get_all_commands()
        
        response = CommandsResponse(
            success=True,
            data=commands,
            count=len(commands),
            total=len(commands),
            message=f"Successfully retrieved {len(commands)} commands",
            processing_time_ms=(time.perf_counter() - start_time) * 1000
        )
        
        cache.set(cache_key, response, ttl=600)  # 10分钟缓存
        
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Commands retrieved: {len(commands)} items in {processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Ultra commands API error: {e}")
        
        return CommandsResponse(
            success=False,
            data=[],
            count=0,
            total=0,
            message=f"Failed to retrieve commands: {str(e)}",
            processing_time_ms=processing_time
        )


@router.get(
    "/commands/health",
    summary="命令服务健康检查",
    response_class=ORJSONResponse
)
async def commands_health_check() -> Dict[str, Any]:
    """命令服务健康检查"""
    start_time = time.perf_counter()
    
    try:
        test_commands = cache.get("ultra_commands_response")
        is_warmed = test_commands is not None
        
        processing_time = (time.perf_counter() - start_time) * 1000
        
        return {
            "success": True,
            "status": "healthy",
            "cache_warmed": is_warmed,
            "response_time_ms": processing_time,
            "timestamp": time.time()
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        return {
            "success": False,
            "status": "unhealthy",
            "error": str(e),
            "response_time_ms": processing_time,
            "timestamp": time.time()
        }