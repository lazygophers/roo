"""
数据库配置和 TinyDB 初始化
"""
from pathlib import Path
from tinydb import TinyDB, Query
from tinydb.storages import JSONStorage
from datetime import datetime
import uuid
from typing import List, Dict, Any, Optional

# 基础路径配置
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "configurations.json"

# 确保数据目录存在
DATA_DIR.mkdir(exist_ok=True)

# 数据库实例
db = TinyDB(DB_PATH, storage=JSONStorage)

# 查询对象
Q = Query()

class ConfigDatabase:
    """配置数据库操作类"""
    
    @staticmethod
    def init_db():
        """初始化数据库表结构"""
        # 创建配置表（TinyDB 默认只有一个表）
        pass
    
    @staticmethod
    def create_config(
        name: str,
        config_data: Dict[str, Any],
        description: str = "",
        user_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """创建新配置"""
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
        return config
    
    @staticmethod
    def get_all_configs(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取所有配置"""
        if user_id:
            return db.search(Q.user_id == user_id)
        return db.all()
    
    @staticmethod
    def get_config(config_id: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """获取单个配置"""
        query = Q.id == config_id
        if user_id:
            query = query & (Q.user_id == user_id)
        return db.get(query)
    
    @staticmethod
    def update_config(
        config_id: str,
        config_data: Dict[str, Any],
        name: Optional[str] = None,
        description: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> bool:
        """更新配置"""
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
        
        return db.update(updates, query)
    
    @staticmethod
    def delete_config(config_id: str, user_id: Optional[str] = None) -> bool:
        """删除配置"""
        query = Q.id == config_id
        if user_id:
            query = query & (Q.user_id == user_id)
        
        return db.remove(query)
    
    @staticmethod
    def rename_config(config_id: str, new_name: str, user_id: Optional[str] = None) -> bool:
        """重命名配置"""
        updates = {
            "name": new_name,
            "updated_at": datetime.now().isoformat()
        }
        
        query = Q.id == config_id
        if user_id:
            query = query & (Q.user_id == user_id)
        
        return db.update(updates, query)
    
    @staticmethod
    def duplicate_config(config_id: str, new_name: str, user_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """复制配置"""
        original = ConfigDatabase.get_config(config_id, user_id)
        if not original:
            return None
        
        # 移除原始ID，让系统生成新的
        original.pop("id", None)
        original["name"] = new_name
        original["description"] = f"复制自: {original.get('description', '原始配置')}"
        
        return ConfigDatabase.create_config(
            name=original["name"],
            config_data=original["config"],
            description=original["description"],
            user_id=user_id
        )
    
    @staticmethod
    def get_configs_stats(user_id: Optional[str] = None) -> Dict[str, Any]:
        """获取配置统计信息"""
        configs = ConfigDatabase.get_all_configs(user_id)
        
        total = len(configs)
        if total == 0:
            return {"total": 0, "average_size": 0, "latest": None}
        
        # 计算平均大小
        total_size = sum(len(str(c.get("config", {}))) for c in configs)
        average_size = total_size / total
        
        # 获取最新创建的配置
        latest = max(configs, key=lambda x: x.get("created_at", ""))
        
        return {
            "total": total,
            "average_size": average_size,
            "latest": latest.get("created_at")
        }

# 初始化数据库
ConfigDatabase.init_db()