"""
数据库配置和 TinyDB 初始化
"""
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

# 导入日志配置
from .utils.logger import db_logger

# 记录数据库模块初始化
db_logger.info("正在初始化数据库模块...")

# 基础路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "configurations.json"

# 确保数据目录存在
try:
    DATA_DIR.mkdir(exist_ok=True)
    db_logger.info(f"数据目录已创建或已存在: {DATA_DIR}")
except Exception as e:
    db_logger.error(f"创建数据目录失败: {e}")
    raise

# 数据库实例
try:
    db = TinyDB(DB_PATH, storage=JSONStorage)
    db_logger.info(f"数据库连接成功: {DB_PATH}")
except Exception as e:
    db_logger.error(f"数据库连接失败: {e}")
    raise

# 查询对象
Q = Query()
db_logger.debug("数据库查询对象已创建")

class ConfigDatabase:
    """配置数据库操作类"""
    
    @staticmethod
    def init_db():
        """初始化数据库表结构"""
        try:
            # 创建配置表（TinyDB 默认只有一个表）
            db_logger.info("数据库表结构初始化完成")
        except Exception as e:
            db_logger.error(f"初始化数据库表结构失败: {e}")
            raise
    
    @staticmethod
    def create_config(
        name: str,
        config_data: Dict[str, Any],
        description: str = "",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建新配置"""
        db_logger.debug(f"开始创建配置: {name}, 用户: {user_id or 'anonymous'}")
        try:
            config_id = str(uuid.uuid4())
            now = datetime.now().isoformat()
            
            config = {
                "id": config_id,
                "name": name,
                "description": description,
                "config": config_data,
                "user_id": user_id or "anonymous",
                "created_at": now,
                "updated_at": now,
                "version": "1.0"
            }
            
            db.insert(config)
            db_logger.info(f"配置创建成功: {config_id}, 名称: {name}")
            return config
        except Exception as e:
            db_logger.error(f"创建配置失败: {e}")
            raise
    
    @staticmethod
    def get_all_configs(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有配置"""
        db_logger.debug(f"获取配置列表, 用户ID: {user_id}")
        try:
            if user_id:
                configs = db.search(Q.user_id == user_id)
                db_logger.info(f"获取到用户 {user_id} 的 {len(configs)} 个配置")
            else:
                configs = db.all()
                db_logger.info(f"获取到所有配置，共 {len(configs)} 个")
            return configs
        except Exception as e:
            db_logger.error(f"获取配置列表失败: {e}")
            raise
    
    @staticmethod
    def get_config(config_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取单个配置"""
        db_logger.debug(f"获取单个配置, ID: {config_id}, 用户ID: {user_id}")
        try:
            query = Q.id == config_id
            if user_id:
                query = query & (Q.user_id == user_id)
            config = db.get(query)
            if config:
                db_logger.info(f"成功获取配置: {config_id}")
            else:
                db_logger.warning(f"未找到配置: {config_id}")
            return config
        except Exception as e:
            db_logger.error(f"获取配置失败: {e}")
            raise
    
    @staticmethod
    def update_config(
        config_id: str,
        config_data: Dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """更新配置"""
        db_logger.debug(f"更新配置, ID: {config_id}, 用户ID: {user_id}")
        try:
            updates = {
                "config": config_data,
                "updated_at": datetime.now().isoformat()
            }
            
            if name is not None:
                updates["name"] = name
            if description is not None:
                updates["description"] = description
            
            query = Q.id == config_id
            if user_id:
                query = query & (Q.user_id == user_id)
            
            result = db.update(updates, query)
            if result:
                db_logger.info(f"配置更新成功: {config_id}")
            else:
                db_logger.warning(f"未找到要更新的配置: {config_id}")
            return result
        except Exception as e:
            db_logger.error(f"更新配置失败: {e}")
            raise
    
    @staticmethod
    def delete_config(config_id: str, user_id: Optional[str] = None) -> bool:
        """删除配置"""
        db_logger.debug(f"删除配置, ID: {config_id}, 用户ID: {user_id}")
        try:
            query = Q.id == config_id
            if user_id:
                query = query & (Q.user_id == user_id)
            
            result = db.remove(query)
            if result:
                db_logger.info(f"配置删除成功: {config_id}")
            else:
                db_logger.warning(f"未找到要删除的配置: {config_id}")
            return result
        except Exception as e:
            db_logger.error(f"删除配置失败: {e}")
            raise
    
    @staticmethod
    def rename_config(config_id: str, new_name: str, user_id: Optional[str] = None) -> bool:
        """重命名配置"""
        db_logger.debug(f"重命名配置, ID: {config_id}, 新名称: {new_name}, 用户ID: {user_id}")
        try:
            updates = {
                "name": new_name,
                "updated_at": datetime.now().isoformat()
            }
            
            query = Q.id == config_id
            if user_id:
                query = query & (Q.user_id == user_id)
            
            result = db.update(updates, query)
            if result:
                db_logger.info(f"配置重命名成功: {config_id} -> {new_name}")
            else:
                db_logger.warning(f"未找到要重命名的配置: {config_id}")
            return result
        except Exception as e:
            db_logger.error(f"重命名配置失败: {e}")
            raise
    
    @staticmethod
    def duplicate_config(config_id: str, new_name: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """复制配置"""
        db_logger.debug(f"复制配置, 原ID: {config_id}, 新名称: {new_name}, 用户ID: {user_id}")
        try:
            original = ConfigDatabase.get_config(config_id, user_id)
            if not original:
                db_logger.warning(f"未找到要复制的原始配置: {config_id}")
                return None
            
            # 移除原始ID，让系统生成新的
            original.pop("id", None)
            original["name"] = new_name
            original["description"] = f"复制自: {original.get('description', '原始配置')}"
            
            new_config = ConfigDatabase.create_config(
                name=original["name"],
                config_data=original["config"],
                description=original["description"],
                user_id=user_id
            )
            db_logger.info(f"配置复制成功: {config_id} -> {new_config.get('id')}")
            return new_config
        except Exception as e:
            db_logger.error(f"复制配置失败: {e}")
            raise
    
    @staticmethod
    def get_configs_stats(user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取配置统计信息"""
        db_logger.debug(f"获取配置统计信息, 用户ID: {user_id}")
        try:
            configs = ConfigDatabase.get_all_configs(user_id)
            
            total = len(configs)
            if total == 0:
                db_logger.info("没有找到任何配置，返回空统计")
                return {"total": 0, "average_size": 0, "latest": None}
            
            # 计算平均大小
            total_size = sum(len(str(c.get("config", {}))) for c in configs)
            average_size = total_size / total
            
            # 获取最新创建的配置
            latest = max(configs, key=lambda x: x.get("created_at", ""))
            
            stats = {
                "total": total,
                "average_size": average_size,
                "latest": latest.get("created_at")
            }
            db_logger.info(f"配置统计信息计算完成: {stats}")
            return stats
        except Exception as e:
            db_logger.error(f"获取配置统计信息失败: {e}")
            raise

# 初始化数据库
try:
    ConfigDatabase.init_db()
    db_logger.info("数据库模块初始化完成")
except Exception as e:
    db_logger.critical(f"数据库模块初始化失败: {e}")
    raise