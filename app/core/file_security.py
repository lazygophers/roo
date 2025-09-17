"""
文件工具安全管理模块
负责文件操作权限检查和安全控制
"""

import os
from pathlib import Path
from typing import List, Tuple, Optional
from app.core.file_security_service import get_file_security_service
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging("INFO")

class FileSecurityManager:
    """文件安全管理器"""
    
    def __init__(self):
        """初始化文件安全管理器"""
        self.security_service = get_file_security_service()
        self._load_security_config()
        
        logger.info(f"FileSecurityManager initialized with {len(self.readable_dirs)} readable dirs, "
                   f"{len(self.writable_dirs)} writable dirs, {len(self.deletable_dirs)} deletable dirs")
    
    def _load_security_config(self):
        """从数据库加载安全配置"""
        # 加载路径配置
        readable_config = self.security_service.get_path_config("readable")
        writable_config = self.security_service.get_path_config("writable")
        deletable_config = self.security_service.get_path_config("deletable")
        forbidden_config = self.security_service.get_path_config("forbidden")
        
        self.readable_dirs = [Path(d).resolve() for d in (readable_config["paths"] if readable_config else [])]
        self.writable_dirs = [Path(d).resolve() for d in (writable_config["paths"] if writable_config else [])]
        self.deletable_dirs = [Path(d).resolve() for d in (deletable_config["paths"] if deletable_config else [])]
        self.forbidden_dirs = [Path(d).resolve() for d in (forbidden_config["paths"] if forbidden_config else [])]
        
        # 加载限制配置
        max_file_size_config = self.security_service.get_limit_config("max_file_size")
        max_read_lines_config = self.security_service.get_limit_config("max_read_lines")
        strict_mode_config = self.security_service.get_limit_config("strict_mode")
        
        self.max_file_size = max_file_size_config["value"] if max_file_size_config else 100 * 1024 * 1024
        self.max_read_lines = max_read_lines_config["value"] if max_read_lines_config else 10000
        self.strict_mode = strict_mode_config["value"] if strict_mode_config else False
    
    def _normalize_path(self, file_path: str) -> Path:
        """标准化路径"""
        try:
            path = Path(file_path).resolve()
            return path
        except Exception:
            # 如果路径无法解析，返回原始路径
            return Path(file_path)
    
    def _is_path_allowed(self, path: Path, allowed_dirs: List[Path]) -> Tuple[bool, Optional[str]]:
        """检查路径是否在允许的目录列表中"""
        try:
            # 首先检查是否在禁止目录中
            for forbidden_dir in self.forbidden_dirs:
                try:
                    if path == forbidden_dir or forbidden_dir in path.parents:
                        return False, f"访问被禁止的目录: {forbidden_dir}"
                except Exception:
                    continue
            
            # 如果不是严格模式，默认允许
            if not self.strict_mode and not allowed_dirs:
                return True, None
            
            # 检查是否在允许的目录中
            for allowed_dir in allowed_dirs:
                try:
                    if path == allowed_dir or allowed_dir in path.parents:
                        return True, None
                except Exception:
                    continue
            
            return False, f"路径不在允许的目录列表中"
            
        except Exception as e:
            logger.error(f"Path permission check failed: {sanitize_for_log(str(e))}")
            return False, f"路径权限检查失败: {str(e)}"
    
    def check_read_permission(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """检查读取权限"""
        path = self._normalize_path(file_path)
        return self._is_path_allowed(path, self.readable_dirs)
    
    def check_write_permission(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """检查写入权限"""
        path = self._normalize_path(file_path)
        return self._is_path_allowed(path, self.writable_dirs)
    
    def check_delete_permission(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """检查删除权限"""
        path = self._normalize_path(file_path)
        return self._is_path_allowed(path, self.deletable_dirs)
    
    def check_file_size_limit(self, file_path: str) -> Tuple[bool, Optional[str]]:
        """检查文件大小限制"""
        try:
            path = Path(file_path)
            if path.exists() and path.is_file():
                file_size = path.stat().st_size
                if file_size > self.max_file_size:
                    return False, f"文件大小 {file_size} bytes 超过限制 {self.max_file_size} bytes"
            return True, None
        except Exception as e:
            return False, f"文件大小检查失败: {str(e)}"
    
    def get_limited_read_lines(self, requested_lines: int) -> int:
        """获取限制后的读取行数"""
        if requested_lines == 0:
            return self.max_read_lines
        return min(requested_lines, self.max_read_lines)
    
    def reload_config(self):
        """重新加载安全配置"""
        self._load_security_config()
        logger.info("File security configuration reloaded from database")
    
    def get_security_info(self) -> dict:
        """获取安全配置信息"""
        return {
            "readable_directories": [str(d) for d in self.readable_dirs],
            "writable_directories": [str(d) for d in self.writable_dirs], 
            "deletable_directories": [str(d) for d in self.deletable_dirs],
            "forbidden_directories": [str(d) for d in self.forbidden_dirs],
            "max_file_size_mb": self.max_file_size / (1024 * 1024),
            "max_read_lines": self.max_read_lines,
            "strict_mode": self.strict_mode,
            "database_summary": self.security_service.get_security_summary()
        }
    
    def validate_operation(self, operation: str, file_path: str) -> Tuple[bool, Optional[str]]:
        """验证文件操作"""
        if operation == "read":
            allowed, msg = self.check_read_permission(file_path)
            if not allowed:
                return False, f"读取权限检查失败: {msg}"
            
            size_ok, size_msg = self.check_file_size_limit(file_path)
            if not size_ok:
                return False, f"文件大小检查失败: {size_msg}"
                
        elif operation == "write":
            allowed, msg = self.check_write_permission(file_path)
            if not allowed:
                return False, f"写入权限检查失败: {msg}"
                
        elif operation == "delete":
            allowed, msg = self.check_delete_permission(file_path)
            if not allowed:
                return False, f"删除权限检查失败: {msg}"
                
        elif operation == "list":
            allowed, msg = self.check_read_permission(file_path)
            if not allowed:
                return False, f"列表权限检查失败: {msg}"
        
        else:
            return False, f"未知操作类型: {operation}"
        
        return True, None


# 全局文件安全管理器实例
_file_security_manager = None

def get_file_security_manager() -> FileSecurityManager:
    """获取文件安全管理器实例"""
    global _file_security_manager
    if _file_security_manager is None:
        _file_security_manager = FileSecurityManager()
    return _file_security_manager