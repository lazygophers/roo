#!/usr/bin/env python3
"""测试数据库API功能的脚本"""

import requests
import json
import sys
import time
import pytest

BASE_URL = "http://127.0.0.1:8001/api"

def test_api_endpoint():
    """测试API端点 - 需要运行中的数据库服务器在端口 8001"""
    pytest.skip("This test requires a running database server on port 8001")

def main():
    """运行所有测试"""
    
    # 等待服务启动
    print("Waiting for service to start...")
    time.sleep(3)
    print("Testing database API functionality...")
    
    # 测试基础端点
    test_api_endpoint("/")
    test_api_endpoint("/health")
    
    # 测试数据库状态
    test_api_endpoint("/database/status")
    
    # 测试缓存数据获取
    test_api_endpoint("/database/data/models")
    
    # 测试快速API端点
    test_api_endpoint("/database/models/fast")

if __name__ == "__main__":
    main()
