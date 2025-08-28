"""
FastAPI 应用程序测试模块

本模块提供了 FastAPI 应用程序的基础测试用例，包括：
- 根路径端点测试
- 健康检查端点测试
- 基础功能测试示例

测试框架：
- pytest: Python 测试框架
- TestClient: FastAPI 测试客户端
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.utils.logger import test_logger


@pytest.fixture
def test_client() -> TestClient:
    """创建 FastAPI 测试客户端 fixture

    Returns:
        TestClient: 配置好的 FastAPI 测试客户端实例
        
    Usage:
        def test_something(test_client):
            response = test_client.get("/some-path")
            assert response.status_code == 200
    """
    test_logger.info("创建 FastAPI 测试客户端")
    try:
        # 创建测试客户端，用于模拟 HTTP 请求
        client = TestClient(app)
        test_logger.debug("测试客户端创建成功")
        return client
    except Exception as e:
        test_logger.error(f"创建测试客户端失败: {e}")
        raise


def test_root_endpoint(test_client: TestClient) -> None:
    """测试根路径 (/) 端点

    验证应用程序的根路径是否正常响应。
    这是一个基础的冒烟测试，确保应用程序能够正常启动。

    Args:
        test_client: FastAPI 测试客户端

    Asserts:
        - 响应状态码为 200 OK

    Note:
        此测试不验证响应内容，仅验证端点是否可达。
    """
    test_logger.info("开始测试根路径端点 (/)")
    try:
        # 发送 GET 请求到根路径
        response = test_client.get("/")
        
        # 验证响应状态码
        if response.status_code == 200:
            test_logger.info("根路径端点测试通过 - 状态码: 200")
        else:
            test_logger.warning(f"根路径端点测试失败 - 状态码: {response.status_code}")
        assert response.status_code == 200
    except Exception as e:
        test_logger.error(f"根路径端点测试异常: {e}")
        raise


def test_health_check(test_client: TestClient) -> None:
    """测试健康检查 (/health) 端点

    验证健康检查端点的响应状态。
    健康检查端点通常用于监控应用程序的运行状态。

    Args:
        test_client: FastAPI 测试客户端

    Asserts:
        - 响应状态码为 200 或 404

    Note:
        - 200: 健康检查端点存在且正常响应
        - 404: 健康检查端点不存在（也是正常情况）
    """
    test_logger.info("开始测试健康检查端点 (/health)")
    try:
        # 发送 GET 请求到健康检查端点
        response = test_client.get("/health")
        
        # 验证响应状态码
        # 如果端点不存在，返回 404 也是正常的
        if response.status_code == 200:
            test_logger.info("健康检查端点测试通过 - 端点存在且正常响应")
        elif response.status_code == 404:
            test_logger.info("健康检查端点测试通过 - 端点不存在（正常情况）")
        else:
            test_logger.warning(f"健康检查端点返回意外状态码: {response.status_code}")
        assert response.status_code in [200, 404]
    except Exception as e:
        test_logger.error(f"健康检查端点测试异常: {e}")
        raise


def test_example() -> None:
    """示例测试函数

    这是一个简单的示例测试，展示了 pytest 的基本用法。
    可以作为编写其他测试的参考模板。

    Asserts:
        - 基础数学运算 1 + 1 等于 2

    Example:
        >>> test_example()
        # 测试通过，无输出
    """
    test_logger.debug("执行示例测试函数")
    try:
        # 基础断言示例
        result = 1 + 1
        assert result == 2
        test_logger.debug(f"示例测试通过: 1 + 1 = {result}")
    except AssertionError:
        test_logger.error("示例测试失败: 1 + 1 不等于 2")
        raise
    except Exception as e:
        test_logger.error(f"示例测试异常: {e}")
        raise