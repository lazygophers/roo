"""
时间工具集配置服务
Time Tools Configuration Service

提供时间工具的全局配置管理，包括默认时区设置等。
类似于文件安全配置系统的架构。
"""

from typing import Dict, Any, Optional, List
from dataclasses import dataclass
from datetime import datetime
import pytz

from app.core.unified_database import get_unified_database, TableNames
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging
from tinydb import Query

logger = setup_logging()

@dataclass
class TimeToolsConfig:
    """时间工具配置数据模型"""
    config_type: str
    name: str
    value: Any
    description: str
    created_at: str = ""
    updated_at: str = ""

class TimeToolsService:
    """时间工具集配置服务"""
    
    def __init__(self, use_unified_db: bool = True):
        """初始化时间工具配置服务"""
        self.use_unified_db = use_unified_db
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.config_table = self.unified_db.get_table(TableNames.TIME_TOOLS_CONFIG)
        
        logger.info(f"TimeToolsService initialized with unified db: {use_unified_db}")
        
        # 初始化默认配置
        self._initialize_default_config()
    
    def _initialize_default_config(self):
        """初始化默认时间工具配置"""
        try:
            default_configs = [
                TimeToolsConfig(
                    config_type="default_timezone",
                    name="默认时区",
                    value="local",
                    description="时间工具的默认时区设置。local表示系统本地时区，也可设置为UTC或具体时区如Asia/Shanghai"
                ),
                TimeToolsConfig(
                    config_type="display_timezone_info",
                    name="显示时区信息",
                    value=True,
                    description="是否在时间输出中显示时区信息"
                ),
                TimeToolsConfig(
                    config_type="auto_detect_timezone",
                    name="自动检测时区",
                    value=True,
                    description="是否自动检测并使用系统时区"
                )
            ]
            
            created_count = 0
            updated_count = 0
            
            for config in default_configs:
                if self._create_or_update_config(config):
                    created_count += 1
                else:
                    updated_count += 1
            
            logger.info(f"Time tools default config initialized: {created_count} created, {updated_count} updated")
            
        except Exception as e:
            logger.error(f"Failed to initialize time tools config: {sanitize_for_log(str(e))}")
    
    def _create_or_update_config(self, config: TimeToolsConfig) -> bool:
        """创建或更新配置项"""
        try:
            Query_obj = Query()
            existing = self.config_table.get(Query_obj.config_type == config.config_type)
            
            config_data = {
                'config_type': config.config_type,
                'name': config.name,
                'value': config.value,
                'description': config.description,
                'updated_at': datetime.now().isoformat()
            }
            
            if existing:
                # 更新现有配置
                self.config_table.update(config_data, Query_obj.config_type == config.config_type)
                return False  # 表示更新
            else:
                # 创建新配置
                config_data['created_at'] = datetime.now().isoformat()
                self.config_table.insert(config_data)
                return True  # 表示创建
                
        except Exception as e:
            logger.error(f"Failed to create/update time config '{config.config_type}': {sanitize_for_log(str(e))}")
            return False
    
    def get_config(self, config_type: str) -> Optional[Dict[str, Any]]:
        """获取指定类型的配置"""
        try:
            Query_obj = Query()
            return self.config_table.get(Query_obj.config_type == config_type)
        except Exception as e:
            logger.error(f"Failed to get time config '{config_type}': {sanitize_for_log(str(e))}")
            return None
    
    def get_all_configs(self) -> List[Dict[str, Any]]:
        """获取所有时间工具配置"""
        try:
            return self.config_table.all()
        except Exception as e:
            logger.error(f"Failed to get all time configs: {sanitize_for_log(str(e))}")
            return []
    
    def update_config(self, config_type: str, value: Any) -> bool:
        """更新配置值"""
        try:
            Query_obj = Query()
            existing = self.config_table.get(Query_obj.config_type == config_type)
            
            if not existing:
                logger.warning(f"Time config '{config_type}' not found for update")
                return False
            
            # 验证配置值
            if not self._validate_config_value(config_type, value):
                logger.warning(f"Invalid value for time config '{config_type}': {sanitize_for_log(str(value))}")
                return False
            
            # 更新配置
            update_data = {
                'value': value,
                'updated_at': datetime.now().isoformat()
            }
            
            self.config_table.update(update_data, Query_obj.config_type == config_type)
            logger.info(f"Updated time config: {config_type} = {sanitize_for_log(str(value))}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to update time config '{config_type}': {sanitize_for_log(str(e))}")
            return False
    
    def _validate_config_value(self, config_type: str, value: Any) -> bool:
        """验证配置值的有效性"""
        try:
            if config_type == "default_timezone":
                if isinstance(value, str):
                    if value.lower() == "local" or value.upper() == "UTC":
                        return True
                    try:
                        pytz.timezone(value)
                        return True
                    except pytz.exceptions.UnknownTimeZoneError:
                        return False
                return False
            
            elif config_type == "display_timezone_info":
                return isinstance(value, bool)
            
            elif config_type == "auto_detect_timezone":
                return isinstance(value, bool)
            
            return True  # 默认允许
            
        except Exception as e:
            logger.error(f"Failed to validate config value: {sanitize_for_log(str(e))}")
            return False
    
    def get_default_timezone(self) -> str:
        """获取默认时区设置"""
        try:
            config = self.get_config("default_timezone")
            return config.get("value", "local") if config else "local"
        except Exception as e:
            logger.error(f"Failed to get default timezone: {sanitize_for_log(str(e))}")
            return "local"
    
    def get_timezone_object(self, timezone_str: Optional[str] = None):
        """获取时区对象"""
        try:
            if timezone_str is None:
                timezone_str = self.get_default_timezone()
            
            if timezone_str.lower() == "local":
                return None  # 使用系统本地时区
            elif timezone_str.upper() == "UTC":
                return pytz.UTC
            else:
                return pytz.timezone(timezone_str)
                
        except pytz.exceptions.UnknownTimeZoneError:
            logger.warning(f"Unknown timezone '{timezone_str}', falling back to local")
            return None
        except Exception as e:
            logger.error(f"Failed to get timezone object: {sanitize_for_log(str(e))}")
            return None
    
    def should_display_timezone_info(self) -> bool:
        """是否应该显示时区信息"""
        try:
            config = self.get_config("display_timezone_info")
            return config.get("value", True) if config else True
        except Exception as e:
            logger.error(f"Failed to get display timezone config: {sanitize_for_log(str(e))}")
            return True
    
    def should_auto_detect_timezone(self) -> bool:
        """是否应该自动检测时区"""
        try:
            config = self.get_config("auto_detect_timezone")
            return config.get("value", True) if config else True
        except Exception as e:
            logger.error(f"Failed to get auto detect timezone config: {sanitize_for_log(str(e))}")
            return True
    
    def get_available_timezones(self) -> List[str]:
        """获取可用的时区列表"""
        try:
            # 返回常用时区列表
            common_timezones = [
                "local",
                "UTC",
                "Asia/Shanghai",
                "Asia/Tokyo", 
                "Asia/Seoul",
                "Asia/Hong_Kong",
                "Asia/Singapore",
                "Europe/London",
                "Europe/Paris",
                "Europe/Berlin",
                "America/New_York",
                "America/Los_Angeles",
                "America/Chicago",
                "America/Denver",
                "Australia/Sydney",
                "Australia/Melbourne"
            ]
            return common_timezones
        except Exception as e:
            logger.error(f"Failed to get available timezones: {sanitize_for_log(str(e))}")
            return ["local", "UTC"]
    
    def get_status_info(self) -> Dict[str, Any]:
        """获取时间工具配置状态信息"""
        try:
            configs = self.get_all_configs()
            
            # 获取当前配置值
            current_values = {}
            for config in configs:
                current_values[config['config_type']] = config['value']
            
            # 获取时区信息
            default_tz = self.get_default_timezone()
            tz_obj = self.get_timezone_object()
            
            if tz_obj:
                current_time = datetime.now(tz_obj)
                tz_name = str(tz_obj)
            else:
                current_time = datetime.now()
                tz_name = str(current_time.astimezone().tzinfo)
            
            return {
                "status": "active",
                "configs": current_values,
                "current_timezone": default_tz,
                "timezone_display_name": tz_name,
                "current_time": current_time.isoformat(),
                "auto_detect": self.should_auto_detect_timezone(),
                "show_timezone_info": self.should_display_timezone_info(),
                "available_timezones": self.get_available_timezones(),
                "total_configs": len(configs),
                "last_updated": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get time tools status: {sanitize_for_log(str(e))}")
            return {
                "status": "error",
                "error": str(e),
                "last_updated": datetime.now().isoformat()
            }

# 全局服务实例
_time_tools_service: Optional[TimeToolsService] = None

def get_time_tools_service(use_unified_db: bool = True) -> TimeToolsService:
    """获取时间工具配置服务实例"""
    global _time_tools_service
    if _time_tools_service is None:
        _time_tools_service = TimeToolsService(use_unified_db=use_unified_db)
    return _time_tools_service

def init_time_tools_service(use_unified_db: bool = True) -> TimeToolsService:
    """初始化时间工具配置服务"""
    global _time_tools_service
    _time_tools_service = TimeToolsService(use_unified_db=use_unified_db)
    return _time_tools_service