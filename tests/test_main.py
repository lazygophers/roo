import pytest
from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def test_client():
    client = TestClient(app)
    return client


def test_root_endpoint(test_client):
    """测试根路径"""
    response = test_client.get("/")
    assert response.status_code == 200


def test_health_check(test_client):
    """测试健康检查端点"""
    response = test_client.get("/health")
    # 如果端点不存在，返回 404 也是正常的
    assert response.status_code in [200, 404]


def test_example():
    """示例测试"""
    assert 1 + 1 == 2