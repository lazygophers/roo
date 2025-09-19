import logging
import sys
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """配置日志系统 - 仅控制台输出"""

    # 创建日志器
    logger = logging.getLogger("roo_api")
    logger.setLevel(getattr(logging, log_level.upper()))

    # 清除现有处理器
    logger.handlers.clear()

    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # 记录日志配置成功
    logger.info("日志系统初始化成功 - 仅控制台输出")

    return logger


def log_request_info(method: str, path: str, params: Dict[str, Any] = None):
    """记录请求信息"""
    logger = logging.getLogger("roo_api")
    params_str = f", params: {params}" if params else ""
    logger.info(f"Request: {method} {path}{params_str}")


def log_error(error: Exception, context: str = ""):
    """记录错误信息"""
    logger = logging.getLogger("roo_api")
    context_str = f" ({context})" if context else ""
    logger.error(f"Error{context_str}: {str(error)}", exc_info=True)