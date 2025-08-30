"""
日志配置工具模块

该模块提供了统一的日志配置功能，支持：
- 同时输出到控制台和文件
- 按小时自动分割日志文件
- 只保留1小时内的日志文件
- 使用文本格式而非JSON格式
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime, timedelta
import pytz


class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    # ANSI颜色代码
    COLORS = {
        'DEBUG': '\033[36m',    # 青色
        'INFO': '\033[32m',     # 绿色
        'WARNING': '\033[33m',  # 黄色
        'ERROR': '\033[31m',    # 红色
        'CRITICAL': '\033[35m', # 紫色
        'RESET': '\033[0m'      # 重置
    }
    
    def format(self, record):
        # 添加颜色
        if record.levelname in self.COLORS:
            record.levelname = f"{self.COLORS[record.levelname]}{record.levelname}{self.COLORS['RESET']}"
        return super().format(record)


def setup_logger(name: str = None, log_dir: Path = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称（现在仅用于标识模块，不影响文件名）
        log_dir: 日志目录，默认为项目根目录下的logs文件夹
        
    Returns:
        配置好的日志记录器
    """
    # 设置日志目录
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / "logs"
    log_dir.mkdir(exist_ok=True)
    
    # 创建日志记录器
    # 使用统一的名称，确保所有模块共享同一个logger实例
    logger_name = "app unified"
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 创建格式化器
    file_formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    console_formatter = ColoredFormatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # 文件处理器 - 按小时分割，使用统一的文件名
    current_time = datetime.now(pytz.timezone('Asia/Shanghai'))
    log_file = log_dir / f"app_{current_time.strftime('%Y-%m-%d_%H')}.log"
    
    file_handler = logging.handlers.TimedRotatingFileHandler(
        filename=log_file,
        when='H',  # 按小时分割
        interval=1,
        backupCount=1,  # 保留1个小时的日志
        encoding='utf-8'
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # 清理旧日志文件（保留1小时内的）
    cleanup_old_logs(log_dir, hours=1)
    
    return logger


def cleanup_old_logs(log_dir: Path, hours: int = 1):
    """
    清理指定小时数之前的日志文件
    
    Args:
        log_dir: 日志目录
        hours: 要保留的小时数
    """
    try:
        cutoff_time = datetime.now(pytz.timezone('Asia/Shanghai')) - timedelta(hours=hours)
        
        for log_file in log_dir.glob("app_*.log"):
            # 从文件名提取时间
            try:
                # 文件名格式: app_YYYY-MM-DD_HH.log
                time_str = log_file.stem.split('_', 1)[1]
                file_time = datetime.strptime(time_str, '%Y-%m-%d_%H')
                file_time = pytz.timezone('Asia/Shanghai').localize(file_time)
                
                if file_time < cutoff_time:
                    log_file.unlink()
                    print(f"已删除旧日志文件: {log_file}")
            except (ValueError, IndexError):
                # 如果文件名格式不正确，跳过
                continue
    except Exception as e:
        print(f"清理日志文件时出错: {e}")


def get_logger(name: str, log_dir: Path = None) -> logging.Logger:
    """
    获取日志记录器的便捷函数
    
    该函数是 setup_logger 的包装器，提供更简洁的接口。
    主要用于保持向后兼容性。
    
    Args:
        name: 日志记录器名称，通常使用 __name__
        log_dir: 日志目录，默认为 None（使用项目根目录下的 logs 文件夹）
        
    Returns:
        配置好的日志记录器实例
        
    Example:
        >>> from app.utils.logger import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("这是一条日志消息")
    """
    return setup_logger(name, log_dir)


# 预配置的统一日志记录器
logger = setup_logger('app unified')

# 为了向后兼容，保留原有名称的别名
app_logger = logger
db_logger = logger
utils_logger = logger
test_logger = logger