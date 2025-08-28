#!/usr/bin/env python3
"""
测试日志配置的简单脚本
"""

import os
import sys
import time
from datetime import datetime

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from utils.logger import setup_logger

def test_logger():
    """测试日志功能"""
    print("开始测试日志配置...")
    
    # 创建日志目录
    log_dir = "logs"
    os.makedirs(log_dir, exist_ok=True)
    
    # 设置日志系统
    setup_logger(log_dir=log_dir)
    # 获取日志记录器实例
    from app.utils.logger import get_app_logger
    logger = get_app_logger()
    
    # 测试不同级别的日志
    print("\n=== 测试不同级别的日志输出 ===")
    logger.debug("这是一条调试信息")
    logger.info("这是一条普通信息")
    logger.warning("这是一条警告信息")
    logger.error("这是一条错误信息")
    
    # 测试带参数的日志
    print("\n=== 测试带参数的日志 ===")
    user_id = 12345
    action = "login"
    logger.info(f"用户 {user_id} 执行了 {action} 操作")
    
    # 测试异常日志
    print("\n=== 测试异常日志 ===")
    try:
        1 / 0
    except Exception as e:
        logger.error(f"发生异常: {e}", exc_info=True)
    
    print("\n=== 检查日志文件 ===")
    
    # 检查是否生成了日志文件
    log_files = [f for f in os.listdir(log_dir) if f.startswith('test_logger')]
    if log_files:
        print(f"✓ 成功生成日志文件: {log_files}")
        # 显示最新的日志文件内容
        latest_log = os.path.join(log_dir, sorted(log_files)[-1])
        print(f"\n最新的日志文件内容 ({latest_log}):")
        print("-" * 50)
        with open(latest_log, 'r', encoding='utf-8') as f:
            print(f.read())
        print("-" * 50)
    else:
        print("✗ 未找到日志文件")
    
    print("\n测试完成！")

if __name__ == "__main__":
    test_logger()