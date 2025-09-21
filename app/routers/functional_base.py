"""
函数式API路由基础框架

提供标准化的API响应格式、错误处理、请求验证等功能
"""

from typing import Any, Dict, List, Optional, Callable, Union
from fastapi import HTTPException, Request, Response
from fastapi.responses import JSONResponse
import asyncio
import time
from datetime import datetime

from app.core.functional_base import Result, create_logger

# =============================================================================
# 响应格式标准化
# =============================================================================

def create_success_response(data: Any = None, message: str = "Success",
                          metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建成功响应"""
    response = {
        "success": True,
        "message": message,
        "data": data,
        "timestamp": datetime.now().isoformat()
    }

    if metadata:
        response["metadata"] = metadata

    return response

def create_error_response(error: Union[str, Exception], code: str = "UNKNOWN_ERROR",
                         status_code: int = 500, details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建错误响应"""
    error_message = str(error)

    response = {
        "success": False,
        "error": {
            "code": code,
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        }
    }

    if details:
        response["error"]["details"] = details

    return response

def create_validation_error_response(validation_errors: List[Dict[str, Any]]) -> Dict[str, Any]:
    """创建验证错误响应"""
    return create_error_response(
        error="Validation failed",
        code="VALIDATION_ERROR",
        status_code=422,
        details={"validation_errors": validation_errors}
    )

def create_not_found_response(resource: str, identifier: str = None) -> Dict[str, Any]:
    """创建资源未找到响应"""
    message = f"{resource} not found"
    if identifier:
        message += f": {identifier}"

    return create_error_response(
        error=message,
        code="NOT_FOUND",
        status_code=404
    )

def create_paginated_response(items: List[Any], total: int, page: int = 1,
                            per_page: int = 20, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """创建分页响应"""
    total_pages = (total + per_page - 1) // per_page

    pagination_metadata = {
        "pagination": {
            "page": page,
            "per_page": per_page,
            "total": total,
            "total_pages": total_pages,
            "has_next": page < total_pages,
            "has_prev": page > 1
        }
    }

    if metadata:
        pagination_metadata.update(metadata)

    return create_success_response(
        data=items,
        message=f"Retrieved {len(items)} items",
        metadata=pagination_metadata
    )

# =============================================================================
# 错误处理装饰器
# =============================================================================

def handle_api_errors(logger: Optional[Any] = None):
    """API错误处理装饰器"""
    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            try:
                result = await func(*args, **kwargs)

                # 如果返回Result对象，处理它
                if isinstance(result, Result):
                    if result.is_success:
                        return create_success_response(result.value)
                    else:
                        if logger:
                            logger.error(f"API error in {func.__name__}: {result.error}")
                        return JSONResponse(
                            content=create_error_response(result.error),
                            status_code=500
                        )

                return result

            except HTTPException:
                # 重新抛出FastAPI异常
                raise
            except Exception as e:
                if logger:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                return JSONResponse(
                    content=create_error_response(e),
                    status_code=500
                )

        def sync_wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)

                # 如果返回Result对象，处理它
                if isinstance(result, Result):
                    if result.is_success:
                        return create_success_response(result.value)
                    else:
                        if logger:
                            logger.error(f"API error in {func.__name__}: {result.error}")
                        return JSONResponse(
                            content=create_error_response(result.error),
                            status_code=500
                        )

                return result

            except HTTPException:
                # 重新抛出FastAPI异常
                raise
            except Exception as e:
                if logger:
                    logger.error(f"Unexpected error in {func.__name__}: {e}")
                return JSONResponse(
                    content=create_error_response(e),
                    status_code=500
                )

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# =============================================================================
# 请求验证工具
# =============================================================================

def validate_pagination_params(page: int = 1, per_page: int = 20,
                              max_per_page: int = 100) -> Dict[str, int]:
    """验证分页参数"""
    if page < 1:
        raise HTTPException(status_code=422, detail="Page must be >= 1")

    if per_page < 1:
        raise HTTPException(status_code=422, detail="Per page must be >= 1")

    if per_page > max_per_page:
        raise HTTPException(status_code=422, detail=f"Per page must be <= {max_per_page}")

    return {"page": page, "per_page": per_page}

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> None:
    """验证必需字段"""
    missing_fields = [field for field in required_fields if field not in data or data[field] is None]

    if missing_fields:
        raise HTTPException(
            status_code=422,
            detail=f"Missing required fields: {', '.join(missing_fields)}"
        )

def validate_field_types(data: Dict[str, Any], field_types: Dict[str, type]) -> None:
    """验证字段类型"""
    type_errors = []

    for field, expected_type in field_types.items():
        if field in data and data[field] is not None:
            if not isinstance(data[field], expected_type):
                type_errors.append(f"{field} must be of type {expected_type.__name__}")

    if type_errors:
        raise HTTPException(status_code=422, detail="; ".join(type_errors))

# =============================================================================
# 性能监控装饰器
# =============================================================================

def monitor_performance(log_slow_requests: bool = True, slow_threshold: float = 1.0):
    """API性能监控装饰器"""
    def decorator(func: Callable):
        logger = create_logger(f"performance.{func.__name__}")

        async def async_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = await func(*args, **kwargs)
            finally:
                duration = time.time() - start_time

                if log_slow_requests and duration > slow_threshold:
                    logger.warning(f"Slow request: {func.__name__} took {duration:.2f}s")
                else:
                    logger.debug(f"Request: {func.__name__} took {duration:.2f}s")

            return result

        def sync_wrapper(*args, **kwargs):
            start_time = time.time()

            try:
                result = func(*args, **kwargs)
            finally:
                duration = time.time() - start_time

                if log_slow_requests and duration > slow_threshold:
                    logger.warning(f"Slow request: {func.__name__} took {duration:.2f}s")
                else:
                    logger.debug(f"Request: {func.__name__} took {duration:.2f}s")

            return result

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# =============================================================================
# 缓存装饰器
# =============================================================================

def cache_response(ttl: int = 300, key_generator: Optional[Callable] = None):
    """API响应缓存装饰器"""
    cache = {}

    def decorator(func: Callable):
        async def async_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 检查缓存
            now = time.time()
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if now - timestamp < ttl:
                    return cached_data

            # 执行函数
            result = await func(*args, **kwargs)

            # 缓存结果
            cache[cache_key] = (result, now)

            # 清理过期缓存
            expired_keys = [k for k, (_, ts) in cache.items() if now - ts >= ttl]
            for k in expired_keys:
                del cache[k]

            return result

        def sync_wrapper(*args, **kwargs):
            # 生成缓存键
            if key_generator:
                cache_key = key_generator(*args, **kwargs)
            else:
                cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # 检查缓存
            now = time.time()
            if cache_key in cache:
                cached_data, timestamp = cache[cache_key]
                if now - timestamp < ttl:
                    return cached_data

            # 执行函数
            result = func(*args, **kwargs)

            # 缓存结果
            cache[cache_key] = (result, now)

            # 清理过期缓存
            expired_keys = [k for k, (_, ts) in cache.items() if now - ts >= ttl]
            for k in expired_keys:
                del cache[k]

            return result

        # 根据函数类型返回相应的包装器
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        else:
            return sync_wrapper

    return decorator

# =============================================================================
# 路由工厂函数
# =============================================================================

def create_crud_endpoints(name: str, service_func: Callable,
                         create_schema: Optional[type] = None,
                         update_schema: Optional[type] = None):
    """创建标准CRUD端点"""
    logger = create_logger(f"api.{name}")

    @handle_api_errors(logger)
    @monitor_performance()
    async def get_all(page: int = 1, per_page: int = 20):
        """获取所有项目"""
        pagination = validate_pagination_params(page, per_page)
        result = await service_func('get_all', **pagination)

        if isinstance(result, Result):
            if result.is_success:
                items, total = result.value
                return create_paginated_response(items, total, page, per_page)
            else:
                return JSONResponse(
                    content=create_error_response(result.error),
                    status_code=500
                )

        return result

    @handle_api_errors(logger)
    @monitor_performance()
    async def get_by_id(item_id: str):
        """根据ID获取项目"""
        result = await service_func('get_by_id', item_id)

        if isinstance(result, Result):
            if result.is_success:
                if result.value:
                    return create_success_response(result.value)
                else:
                    return JSONResponse(
                        content=create_not_found_response(name, item_id),
                        status_code=404
                    )
            else:
                return JSONResponse(
                    content=create_error_response(result.error),
                    status_code=500
                )

        return result

    @handle_api_errors(logger)
    @monitor_performance()
    async def create_item(item_data: Dict[str, Any]):
        """创建新项目"""
        if create_schema:
            # 验证数据
            try:
                validated_data = create_schema(**item_data)
                item_data = validated_data.dict()
            except Exception as e:
                return JSONResponse(
                    content=create_validation_error_response([{"field": "data", "error": str(e)}]),
                    status_code=422
                )

        result = await service_func('create', item_data)

        if isinstance(result, Result):
            if result.is_success:
                return create_success_response(result.value, f"{name} created successfully")
            else:
                return JSONResponse(
                    content=create_error_response(result.error),
                    status_code=500
                )

        return result

    @handle_api_errors(logger)
    @monitor_performance()
    async def update_item(item_id: str, item_data: Dict[str, Any]):
        """更新项目"""
        if update_schema:
            # 验证数据
            try:
                validated_data = update_schema(**item_data)
                item_data = validated_data.dict(exclude_unset=True)
            except Exception as e:
                return JSONResponse(
                    content=create_validation_error_response([{"field": "data", "error": str(e)}]),
                    status_code=422
                )

        result = await service_func('update', item_id, item_data)

        if isinstance(result, Result):
            if result.is_success:
                return create_success_response(result.value, f"{name} updated successfully")
            else:
                return JSONResponse(
                    content=create_error_response(result.error),
                    status_code=500
                )

        return result

    @handle_api_errors(logger)
    @monitor_performance()
    async def delete_item(item_id: str):
        """删除项目"""
        result = await service_func('delete', item_id)

        if isinstance(result, Result):
            if result.is_success:
                return create_success_response(None, f"{name} deleted successfully")
            else:
                return JSONResponse(
                    content=create_error_response(result.error),
                    status_code=500
                )

        return result

    return {
        'get_all': get_all,
        'get_by_id': get_by_id,
        'create': create_item,
        'update': update_item,
        'delete': delete_item
    }

# =============================================================================
# 中间件工具
# =============================================================================

def add_cors_headers(response: Response) -> Response:
    """添加CORS头"""
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
    return response

def add_security_headers(response: Response) -> Response:
    """添加安全头"""
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    return response

# =============================================================================
# 健康检查端点
# =============================================================================

def create_health_check_endpoint(dependencies: Optional[List[Callable]] = None):
    """创建健康检查端点"""
    @handle_api_errors()
    @monitor_performance()
    async def health_check():
        """健康检查"""
        health_status = {
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "version": "1.0.0"
        }

        # 检查依赖项
        if dependencies:
            dependency_status = {}
            for dep in dependencies:
                try:
                    if asyncio.iscoroutinefunction(dep):
                        await dep()
                    else:
                        dep()
                    dependency_status[dep.__name__] = "healthy"
                except Exception as e:
                    dependency_status[dep.__name__] = f"unhealthy: {str(e)}"
                    health_status["status"] = "unhealthy"

            health_status["dependencies"] = dependency_status

        return create_success_response(health_status)

    return health_check