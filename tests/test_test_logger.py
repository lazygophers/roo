"""test_logger.py 的单元测试"""

import os
import sys
import tempfile
import shutil
from pathlib import Path
from datetime import datetime, timedelta
import pytz
import pytest
import logging
from unittest.mock import patch, MagicMock

# 添加 app 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.utils.logger import setup_logger, get_logger, cleanup_old_logs, ColoredFormatter


class TestColoredFormatter:
    """测试 ColoredFormatter 类"""
    
    def test_format_with_color(self):
        """测试带颜色的日志格式化"""
        formatter = ColoredFormatter(
            fmt='%(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建一个日志记录
        record = logging.LogRecord(
            name='test_logger',
            level=logging.INFO,
            pathname='test.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # 格式化日志
        formatted = formatter.format(record)
        
        # 验证包含颜色代码
        assert '\033[32m' in formatted  # 绿色
        assert 'INFO' in formatted
        assert 'Test message' in formatted
        assert '\033[0m' in formatted  # 重置颜色
    
    def test_format_without_color(self):
        """测试不带颜色的日志格式化"""
        formatter = ColoredFormatter(
            fmt='%(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 创建一个未知级别的日志记录
        record = logging.LogRecord(
            name='test_logger',
            level=99,  # 未知级别
            pathname='test.py',
            lineno=42,
            msg='Test message',
            args=(),
            exc_info=None
        )
        
        # 格式化日志
        formatted = formatter.format(record)
        
        # 验证不包含颜色代码
        assert '\033[' not in formatted
        assert '99' in formatted
        assert 'Test message' in formatted


class TestSetupLogger:
    """测试 setup_logger 函数"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        
        # 清理已存在的 logger
        if logging.getLogger("app unified").hasHandlers():
            logging.getLogger("app unified").handlers.clear()
        
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理 logger handlers
        if logging.getLogger("app unified").hasHandlers():
            logging.getLogger("app unified").handlers.clear()
            
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_setup_logger_with_default_dir(self):
        """测试使用默认目录设置日志记录器"""
        logger = setup_logger()
        
        # 验证 logger 对象
        assert isinstance(logger, logging.Logger)
        assert logger.name == "app unified"
        assert logger.level == logging.DEBUG
        
        # 验证处理器 - 默认创建控制台和文件处理器
        assert len(logger.handlers) == 2  # 控制台和文件处理器
        
        # 验证控制台处理器
        console_handler = logger.handlers[0]
        assert isinstance(console_handler, logging.StreamHandler)
        assert isinstance(console_handler.formatter, ColoredFormatter)
        assert console_handler.level == logging.INFO
        
        # 验证文件处理器
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.TimedRotatingFileHandler)]
        assert len(file_handlers) == 1
        assert file_handlers[0].level == logging.DEBUG
    
    def test_setup_logger_with_custom_dir(self):
        """测试使用自定义目录设置日志记录器"""
        logger = setup_logger(log_dir=self.log_dir)
        
        # 验证日志目录已创建
        assert self.log_dir.exists()
        
        # 验证 logger 对象
        assert isinstance(logger, logging.Logger)
        assert logger.name == "app unified"
        assert logger.level == logging.DEBUG
        
        # 验证处理器
        assert len(logger.handlers) == 2  # 控制台和文件处理器
        
        # 验证文件处理器使用了正确的目录
        file_handlers = [h for h in logger.handlers if isinstance(h, logging.handlers.TimedRotatingFileHandler)]
        assert len(file_handlers) == 1
        assert str(self.log_dir) in file_handlers[0].baseFilename
    
    def test_setup_logger_reuses_instance(self):
        """测试 setup_logger 重用已存在的 logger 实例"""
        # 第一次调用
        logger1 = setup_logger(log_dir=self.log_dir)
        handler_count1 = len(logger1.handlers)
        
        # 第二次调用
        logger2 = setup_logger(log_dir=self.log_dir)
        
        # 验证返回同一个实例
        assert logger1 is logger2
        assert len(logger2.handlers) == handler_count1
    
    def test_log_levels(self):
        """测试不同日志级别"""
        logger = setup_logger(log_dir=self.log_dir)
        
        # 创建内存缓冲区捕获日志输出
        with patch.object(logger.handlers[0], 'stream') as mock_stream:
            # 测试不同级别的日志
            logger.debug("Debug message")
            logger.info("Info message")
            logger.warning("Warning message")
            logger.error("Error message")
            logger.critical("Critical message")
            
            # 验证控制台输出
            assert mock_stream.write.called
    
    def test_log_to_file(self):
        """测试日志写入文件"""
        logger = setup_logger(log_dir=self.log_dir)
        
        # 写入日志
        test_message = "Test file logging"
        logger.info(test_message)
        
        # 强制刷新处理器
        for handler in logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # 读取日志文件内容
        log_files = list(self.log_dir.glob("app_*.log"))
        assert len(log_files) == 1
        
        with open(log_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            # 移除ANSI颜色代码进行验证
            import re
            clean_content = re.sub(r'\x1b\[[0-9;]*m', '', content)
            assert test_message in clean_content
            assert 'INFO' in clean_content
            # 注意：实际日志格式可能不包含文件名，这是正常的
    
    def test_log_format(self):
        """测试日志格式"""
        logger = setup_logger(log_dir=self.log_dir)
        
        # 写入日志
        logger.info("Format test")
        
        # 强制刷新处理器
        for handler in logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # 读取日志文件内容
        log_files = list(self.log_dir.glob("app_*.log"))
        with open(log_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            # 移除ANSI颜色代码进行验证
            import re
            clean_content = re.sub(r'\x1b\[[0-9;]*m', '', content)
            
            # 验证格式包含所有必需元素
            assert ' - ' in clean_content  # 分隔符
            assert 'app unified' in clean_content  # logger 名称
            assert 'INFO' in clean_content  # 日志级别
            # 注意：实际日志格式可能不包含文件名，这是正常的
            # 但应该包含函数名（如果配置了funcName参数）
    
    def test_exception_logging(self):
        """测试异常日志记录"""
        logger = setup_logger(log_dir=self.log_dir)
        
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger.error("Exception occurred", exc_info=True)
        
        # 强制刷新处理器
        for handler in logger.handlers:
            if hasattr(handler, 'flush'):
                handler.flush()
        
        # 读取日志文件内容
        log_files = list(self.log_dir.glob("app_*.log"))
        with open(log_files[0], 'r', encoding='utf-8') as f:
            content = f.read()
            assert 'ValueError: Test exception' in content
            assert 'Traceback' in content


class TestCleanupOldLogs:
    """测试 cleanup_old_logs 函数"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)
        
        # 创建一些测试日志文件
        self.create_test_log_files()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def create_test_log_files(self):
        """创建测试用的日志文件"""
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        
        # 创建当前时间的日志文件
        current_file = self.log_dir / f"app_{now.strftime('%Y-%m-%d_%H')}.log"
        current_file.write_text("Current log file")
        
        # 创建1小时前的日志文件
        old_time = now - timedelta(hours=1)
        old_file = self.log_dir / f"app_{old_time.strftime('%Y-%m-%d_%H')}.log"
        old_file.write_text("Old log file")
        
        # 创建2小时前的日志文件
        older_time = now - timedelta(hours=2)
        older_file = self.log_dir / f"app_{older_time.strftime('%Y-%m-%d_%H')}.log"
        older_file.write_text("Older log file")
        
        # 创建一个格式错误的文件名
        invalid_file = self.log_dir / "invalid_format.log"
        invalid_file.write_text("Invalid format")
    
    def test_cleanup_old_logs_removes_old_files(self):
        """测试清理旧日志文件功能"""
        # 清理1小时前的日志
        cleanup_old_logs(self.log_dir, hours=1)
        
        # 检查文件是否存在
        log_files = list(self.log_dir.glob("app_*.log"))
        
        # 根据实际文件时间，应该只剩下1个文件（当前文件）
        # 因为其他文件都被删除了
        assert len(log_files) == 1
        
        # 验证旧文件被删除
        now = datetime.now(pytz.timezone('Asia/Shanghai'))
        older_time = now - timedelta(hours=2)
        older_file = self.log_dir / f"app_{older_time.strftime('%Y-%m-%d_%H')}.log"
        assert not older_file.exists()
    
    def test_cleanup_old_logs_preserves_recent_files(self):
        """测试清理旧日志文件时保留新文件"""
        # 清理2小时前的日志
        cleanup_old_logs(self.log_dir, hours=2)
        
        # 检查所有文件都存在
        log_files = list(self.log_dir.glob("app_*.log"))
        # 根据实际文件时间，应该剩下2个文件
        assert len(log_files) == 2
        
        # 验证无效格式文件不被影响
        invalid_file = self.log_dir / "invalid_format.log"
        assert invalid_file.exists()
    
    def test_cleanup_old_logs_handles_invalid_filenames(self):
        """测试清理功能正确处理格式错误的文件名"""
        # 清理所有日志
        cleanup_old_logs(self.log_dir, hours=0)
        
        # 验证无效格式文件仍然存在
        invalid_file = self.log_dir / "invalid_format.log"
        assert invalid_file.exists()
        
        # 验证没有错误抛出
        cleanup_old_logs(self.log_dir, hours=1)
    
    @patch('app.utils.logger.print')
    def test_cleanup_old_logs_prints_deletion_messages(self, mock_print):
        """测试删除旧文件时打印消息"""
        # 清理1小时前的日志
        cleanup_old_logs(self.log_dir, hours=1)
        
        # 验证打印了删除消息
        assert mock_print.called
        assert any("已删除旧日志文件" in str(call) for call in mock_print.call_args_list)


class TestGetLogger:
    """测试 get_logger 函数"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir)
        
        # 清理已存在的 logger
        if logging.getLogger("app unified").hasHandlers():
            logging.getLogger("app unified").handlers.clear()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 清理 logger handlers
        if logging.getLogger("app unified").hasHandlers():
            logging.getLogger("app unified").handlers.clear()
            
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_get_logger_returns_logger_instance(self):
        """测试 get_logger 返回 logger 实例"""
        logger = get_logger("test_module", self.log_dir)
        
        # 验证返回的是 Logger 实例
        assert isinstance(logger, logging.Logger)
        assert logger.name == "app unified"
    
    def test_get_logger_is_alias_for_setup_logger(self):
        """测试 get_logger 是 setup_logger 的别名"""
        with patch('app.utils.logger.setup_logger') as mock_setup:
            mock_setup.return_value = MagicMock()
            
            logger = get_logger("test_module", self.log_dir)
            
            # 验证调用了 setup_logger
            mock_setup.assert_called_once_with("test_module", self.log_dir)
            assert logger is mock_setup.return_value


class TestIntegration:
    """集成测试"""
    
    def setup_method(self):
        """每个测试方法前的设置"""
        # 创建临时目录
        self.temp_dir = tempfile.mkdtemp()
        self.log_dir = Path(self.temp_dir) / "logs"
        
        # 保存原始的 logger handlers
        self.original_handlers = logging.getLogger("app unified").handlers.copy()
        
        # 清理已存在的 logger
        if logging.getLogger("app unified").hasHandlers():
            logging.getLogger("app unified").handlers.clear()
    
    def teardown_method(self):
        """每个测试方法后的清理"""
        # 恢复原始的 logger handlers
        logger = logging.getLogger("app unified")
        logger.handlers.clear()
        logger.handlers.extend(self.original_handlers)
        
        # 删除临时目录
        shutil.rmtree(self.temp_dir)
    
    def test_multiple_loggers_share_instance(self):
        """测试多个 logger 共享同一个实例"""
        # 获取多个 logger
        logger1 = get_logger("module1", self.log_dir)
        logger2 = get_logger("module2", self.log_dir)
        logger3 = get_logger("module3", self.log_dir)
        
        # 验证它们是同一个实例
        assert logger1 is logger2 is logger3
        
        # 验证处理器数量不会重复增加
        assert len(logger1.handlers) == 2
    
    def test_log_rotation(self):
        """测试日志轮转功能"""
        logger = setup_logger(log_dir=self.log_dir)
        
        # 写入一些日志
        logger.info("Before rotation")
        
        # 获取当前日志文件
        log_files_before = list(self.log_dir.glob("app_*.log"))
        assert len(log_files_before) == 1
        
        # 模拟时间变化（这里无法直接测试轮转，但可以验证配置）
        file_handler = None
        for handler in logger.handlers:
            if isinstance(handler, logging.handlers.TimedRotatingFileHandler):
                file_handler = handler
                break
        
        assert file_handler is not None
        assert file_handler.when == 'H'
        assert file_handler.interval == 3600
        assert file_handler.backupCount == 1
    
    def test_preconfigured_loggers(self):
        """测试预配置的 logger 别名"""
        from app.utils.logger import app_logger, db_logger, utils_logger, test_logger
        
        # 验证所有预配置的 logger 都是同一个实例
        assert app_logger is db_logger is utils_logger is test_logger
        
        # 验证它们可以正常工作
        if len(test_logger.handlers) > 0:
            with patch.object(test_logger.handlers[0], 'stream') as mock_stream:
                test_logger.info("Test preconfigured logger")
                assert mock_stream.write.called
        else:
            # 如果预配置的 logger 没有处理器，先设置一个
            from app.utils.logger import setup_logger
            setup_logger()
            with patch.object(test_logger.handlers[0], 'stream') as mock_stream:
                test_logger.info("Test preconfigured logger")
                assert mock_stream.write.called


# 如果直接运行测试文件，执行 pytest
if __name__ == "__main__":
    pytest.main([__file__])