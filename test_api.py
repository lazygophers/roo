#!/usr/bin/env python3
"""测试数据库API功能的脚本"""

import requests
import json
import sys
import time

BASE_URL = "http://127.0.0.1:8001/api"

def test_api_endpoint(endpoint, method='GET', data=None):
    """测试API端点"""
    try:
        if method == 'GET':
            response = requests.get(f"{BASE_URL}{endpoint}")
        elif method == 'POST':
            response = requests.post(f"{BASE_URL}{endpoint}", json=data)
        
        print(f"\n--- {method} {endpoint} ---")
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Success: {result.get('success', 'Unknown')}")
            print(f"Message: {result.get('message', 'No message')}")
            
            if 'data' in result:
                data = result['data']
                if isinstance(data, list):
                    print(f"Data count: {len(data)}")
                    if data:
                        print(f"First item keys: {list(data[0].keys()) if isinstance(data[0], dict) else 'Not a dict'}")
                elif isinstance(data, dict):
                    print(f"Data keys: {list(data.keys())}")
                else:
                    print(f"Data type: {type(data)}")
        else:
            print(f"Error: {response.text}")
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

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
