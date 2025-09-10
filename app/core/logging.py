import logging
import sys
import os
from pathlib import Path
from logging.handlers import TimedRotatingFileHandler
from typing import Dict, Any

def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """配置日志系统 - 控制台 + 按小时切割的文件日志"""
    
    # 创建日志器
    logger = logging.getLogger("roo_api")
    logger.setLevel(getattr(logging, log_level.upper()))
    
    # 清除现有处理器
    logger.handlers.clear()
    
    # 创建格式器
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # 1. 创建控制台处理器
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, log_level.upper()))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # 2. 创建文件处理器（按小时切割）
    try:
        # 确保日志目录存在
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # 创建按小时切割的文件处理器
        file_handler = TimedRotatingFileHandler(
            filename=log_dir / "roo_api.log",
            when="H",  # 按小时切割
            interval=1,  # 每1小时切割一次
            backupCount=3,  # 保留最多3个备份文件（即3个小时的日志）
            encoding="utf-8"
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))
        file_handler.setFormatter(formatter)
        
        # 设置文件名后缀格式
        file_handler.suffix = "%Y%m%d-%H.log"
        
        logger.addHandler(file_handler)
        
        # 记录日志配置成功
        logger.info("日志系统初始化成功 - 控制台 + 文件(按小时切割，保留3小时)")
        
    except Exception as e:
        # 如果文件处理器创建失败，只使用控制台处理器
        logger.warning(f"文件日志处理器创建失败，仅使用控制台日志: {str(e)}")
    
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