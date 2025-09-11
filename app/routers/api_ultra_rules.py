"""
超高性能规则API路由
Ultra Performance Rules API Router
"""

import time
import asyncio
from typing import List, Dict, Any, Optional
from fastapi import APIRouter, BackgroundTasks
from fastapi.responses import ORJSONResponse

from app.models.schemas import RulesResponse, RuleBySlugRequest
from app.core.ultra_performance_service import get_ultra_rules_service, get_ultra_cache
from app.core.logging import setup_logging

logger = setup_logging("INFO")
router = APIRouter(default_response_class=ORJSONResponse)

# 获取服务实例
rules_service = get_ultra_rules_service()
cache = get_ultra_cache()


@router.post(
    "/rules",
    response_model=RulesResponse,
    summary="获取所有规则 - 超高性能版本",
    response_class=ORJSONResponse
)
async def get_rules_ultra() -> RulesResponse:
    """超高性能获取所有规则"""
    start_time = time.perf_counter()
    
    try:
        cache_key = "ultra_rules_response"
        cached_response = cache.get(cache_key)
        
        if cached_response:
            processing_time = (time.perf_counter() - start_time) * 1000
            logger.debug(f"Ultra-fast rules response: {processing_time:.2f}ms (cached)")
            return cached_response
        
        rules = rules_service.get_all_rules()
        
        response = RulesResponse(
            success=True,
            data=rules,
            count=len(rules),
            total=len(rules),
            message=f"Successfully retrieved {len(rules)} rules",
            processing_time_ms=(time.perf_counter() - start_time) * 1000
        )
        
        cache.set(cache_key, response, ttl=600)  # 10分钟缓存
        
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.info(f"Rules retrieved: {len(rules)} items in {processing_time:.2f}ms")
        
        return response
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Ultra rules API error: {e} (took {processing_time:.2f}ms)")
        
        return RulesResponse(
            success=False,
            data=[],
            count=0,
            total=0,
            message=f"Failed to retrieve rules: {str(e)}",
            processing_time_ms=processing_time
        )


@router.post(
    "/rules/by-slug",
    summary="根据slug获取规则 - 超高性能版本",
    response_class=ORJSONResponse
)
async def get_rule_by_slug_ultra(request: RuleBySlugRequest) -> Dict[str, Any]:
    """超高性能根据slug获取规则"""
    start_time = time.perf_counter()
    
    try:
        cache_key = f"ultra_rule_slug_{request.slug}"
        cached_rule = cache.get(cache_key)
        
        if cached_rule:
            processing_time = (time.perf_counter() - start_time) * 1000
            return {
                "success": True,
                "data": cached_rule,
                "message": f"Rule '{request.slug}' found",
                "processing_time_ms": processing_time
            }
        
        rules = rules_service.get_all_rules()
        target_rule = next((rule for rule in rules if rule['slug'] == request.slug), None)
        
        if not target_rule:
            return {
                "success": False,
                "data": None,
                "message": f"Rule with slug '{request.slug}' not found",
                "processing_time_ms": (time.perf_counter() - start_time) * 1000
            }
        
        cache.set(cache_key, target_rule, ttl=1800)
        
        processing_time = (time.perf_counter() - start_time) * 1000
        return {
            "success": True,
            "data": target_rule,
            "message": f"Rule '{request.slug}' found",
            "processing_time_ms": processing_time
        }
        
    except Exception as e:
        processing_time = (time.perf_counter() - start_time) * 1000
        logger.error(f"Rule by slug error: {e}")
        
        return {
            "success": False,
            "data": None,
            "message": f"Error retrieving rule: {str(e)}",
            "processing_time_ms": processing_time
        }


@router.get(
    "/rules/health",
    summary="规则服务健康检查",
    response_class=ORJSONResponse
)
async def rules_health_check() -> Dict[str, Any]:
    """规则服务健康检查"""
    start_time = time.perf_counter()
    
    try:
        test_rules = cache.get("ultra_rules_response")
        is_warmed = test_rules is not None
        
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