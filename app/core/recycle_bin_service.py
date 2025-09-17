"""
回收站服务
Recycle Bin Service

实现软删除功能，删除的数据会被移动到回收站，保留3天后自动永久删除
"""

import json
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from tinydb import TinyDB, Query
from enum import Enum

from app.core.config import PROJECT_ROOT
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging
from app.core.unified_database import get_unified_database, TableNames

logger = setup_logging("INFO")

class RecycleBinItemType(str, Enum):
    """回收站项目类型"""
    MODEL = "model"
    COMMAND = "command" 
    RULE = "rule"
    HOOK = "hook"
    ROLE = "role"
    CONFIGURATION = "configuration"
    SECURITY_PATH = "security_path"
    SECURITY_LIMIT = "security_limit"
    MCP_TOOL = "mcp_tool"
    MCP_CATEGORY = "mcp_category"
    CACHE_FILE = "cache_file"
    CACHE_METADATA = "cache_metadata"

class RecycleBinItem:
    """回收站项目数据模型"""
    
    def __init__(
        self,
        original_id: str,
        item_type: RecycleBinItemType,
        original_table: str,
        original_data: Dict[str, Any],
        deleted_by: str = "system",
        deleted_reason: str = "manual_delete",
        **kwargs
    ):
        self.id = kwargs.get('id', str(uuid.uuid4()))
        self.original_id = original_id
        self.item_type = item_type
        self.original_table = original_table
        self.original_data = original_data
        self.deleted_by = deleted_by
        self.deleted_reason = deleted_reason
        self.deleted_at = kwargs.get('deleted_at', datetime.now().isoformat())
        self.expires_at = kwargs.get('expires_at', 
            (datetime.now() + timedelta(days=3)).isoformat())
        self.metadata = kwargs.get('metadata', {})
        
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            'id': self.id,
            'original_id': self.original_id,
            'item_type': self.item_type.value,
            'original_table': self.original_table,
            'original_data': self.original_data,
            'deleted_by': self.deleted_by,
            'deleted_reason': self.deleted_reason,
            'deleted_at': self.deleted_at,
            'expires_at': self.expires_at,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecycleBinItem':
        """从字典创建实例"""
        return cls(
            original_id=data['original_id'],
            item_type=RecycleBinItemType(data['item_type']),
            original_table=data['original_table'],
            original_data=data['original_data'],
            deleted_by=data.get('deleted_by', 'system'),
            deleted_reason=data.get('deleted_reason', 'manual_delete'),
            **{k: v for k, v in data.items() if k not in [
                'original_id', 'item_type', 'original_table', 'original_data',
                'deleted_by', 'deleted_reason'
            ]}
        )
    
    def is_expired(self) -> bool:
        """检查是否已过期"""
        expires_dt = datetime.fromisoformat(self.expires_at)
        return datetime.now() >= expires_dt
    
    def get_remaining_days(self) -> int:
        """获取剩余保留天数"""
        expires_dt = datetime.fromisoformat(self.expires_at)
        remaining = expires_dt - datetime.now()
        return max(0, remaining.days)

class RecycleBinService:
    """回收站服务"""
    
    # 回收站表名
    RECYCLE_BIN_TABLE = TableNames.RECYCLE_BIN
    
    # 默认保留天数
    DEFAULT_RETENTION_DAYS = 3
    
    def __init__(self, use_unified_db: bool = True):
        """初始化回收站服务"""
        self.use_unified_db = use_unified_db
        
        if use_unified_db:
            self.unified_db = get_unified_database()
            self.db = self.unified_db.db
            self.db_path = self.unified_db.db_path
        else:
            # 兼容模式：使用独立数据库文件
            db_dir = PROJECT_ROOT / "data"
            db_dir.mkdir(exist_ok=True)
            db_path = str(db_dir / "recycle_bin.db")
            self.db_path = db_path
            self.db = TinyDB(db_path)
            self.unified_db = None
        
        # 获取回收站表
        self.recycle_table = self.db.table(self.RECYCLE_BIN_TABLE)
        
        logger.info(f"RecycleBinService initialized with unified db: {use_unified_db}")
    
    def soft_delete(
        self,
        table_name: str,
        item_id: str,
        item_type: RecycleBinItemType,
        deleted_by: str = "system",
        deleted_reason: str = "manual_delete",
        retention_days: int = None
    ) -> bool:
        """
        软删除：将项目移动到回收站
        
        Args:
            table_name: 原始表名
            item_id: 项目ID
            item_type: 项目类型
            deleted_by: 删除者
            deleted_reason: 删除原因
            retention_days: 保留天数，默认3天
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取原始表和数据
            source_table = self.db.table(table_name)
            Query_obj = Query()
            
            # 查找原始数据
            original_item = source_table.get(Query_obj.id == item_id)
            if not original_item:
                logger.warning(f"Item not found for soft delete: {sanitize_for_log(item_id)}")
                return False
            
            # 计算过期时间
            retention_days = retention_days or self.DEFAULT_RETENTION_DAYS
            expires_at = (datetime.now() + timedelta(days=retention_days)).isoformat()
            
            # 创建回收站项目
            recycle_item = RecycleBinItem(
                original_id=item_id,
                item_type=item_type,
                original_table=table_name,
                original_data=original_item,
                deleted_by=deleted_by,
                deleted_reason=deleted_reason,
                expires_at=expires_at
            )
            
            # 插入到回收站
            self.recycle_table.insert(recycle_item.to_dict())
            
            # 从原始表中删除
            source_table.remove(Query_obj.id == item_id)
            
            logger.info(f"Item moved to recycle bin: {sanitize_for_log(item_id)}, expires: {expires_at}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to soft delete item {sanitize_for_log(item_id)}: {sanitize_for_log(str(e))}")
            return False
    
    def restore(self, recycle_bin_id: str) -> bool:
        """
        从回收站恢复项目
        
        Args:
            recycle_bin_id: 回收站项目ID
            
        Returns:
            bool: 是否成功恢复
        """
        try:
            Query_obj = Query()
            
            # 查找回收站项目
            recycle_data = self.recycle_table.get(Query_obj.id == recycle_bin_id)
            if not recycle_data:
                logger.warning(f"Recycle bin item not found: {sanitize_for_log(recycle_bin_id)}")
                return False
            
            recycle_item = RecycleBinItem.from_dict(recycle_data)
            
            # 检查是否已过期
            if recycle_item.is_expired():
                logger.warning(f"Cannot restore expired item: {sanitize_for_log(recycle_bin_id)}")
                return False
            
            # 获取目标表
            target_table = self.db.table(recycle_item.original_table)
            
            # 检查原始ID是否已被占用
            existing_item = target_table.get(Query_obj.id == recycle_item.original_id)
            if existing_item:
                logger.warning(f"Original ID already exists, cannot restore: {sanitize_for_log(recycle_item.original_id)}")
                return False
            
            # 恢复到原始表
            target_table.insert(recycle_item.original_data)
            
            # 从回收站删除
            self.recycle_table.remove(Query_obj.id == recycle_bin_id)
            
            logger.info(f"Item restored from recycle bin: {sanitize_for_log(recycle_item.original_id)}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restore item {sanitize_for_log(recycle_bin_id)}: {sanitize_for_log(str(e))}")
            return False
    
    def permanent_delete(self, recycle_bin_id: str) -> bool:
        """
        永久删除回收站项目
        
        Args:
            recycle_bin_id: 回收站项目ID
            
        Returns:
            bool: 是否成功删除
        """
        try:
            Query_obj = Query()
            result = self.recycle_table.remove(Query_obj.id == recycle_bin_id)
            
            if result:
                logger.info(f"Item permanently deleted from recycle bin: {sanitize_for_log(recycle_bin_id)}")
                return True
            else:
                logger.warning(f"Recycle bin item not found for permanent delete: {sanitize_for_log(recycle_bin_id)}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to permanently delete item {sanitize_for_log(recycle_bin_id)}: {sanitize_for_log(str(e))}")
            return False
    
    def get_all_items(
        self,
        item_type: Optional[RecycleBinItemType] = None,
        include_expired: bool = True,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取回收站所有项目
        
        Args:
            item_type: 过滤项目类型
            include_expired: 是否包含已过期项目
            limit: 限制返回数量
            
        Returns:
            List[Dict]: 回收站项目列表
        """
        try:
            items = self.recycle_table.all()
            
            # 按类型过滤
            if item_type:
                items = [item for item in items if item['item_type'] == item_type.value]
            
            # 过滤过期项目
            if not include_expired:
                current_time = datetime.now()
                items = [
                    item for item in items 
                    if datetime.fromisoformat(item['expires_at']) > current_time
                ]
            
            # 按删除时间倒序排序
            items.sort(key=lambda x: x['deleted_at'], reverse=True)
            
            # 限制数量
            if limit:
                items = items[:limit]
            
            # 添加额外信息
            for item in items:
                recycle_item = RecycleBinItem.from_dict(item)
                item['is_expired'] = recycle_item.is_expired()
                item['remaining_days'] = recycle_item.get_remaining_days()
            
            return items
            
        except Exception as e:
            logger.error(f"Failed to get recycle bin items: {sanitize_for_log(str(e))}")
            return []
    
    def cleanup_expired_items(self) -> int:
        """
        清理过期的回收站项目
        
        Returns:
            int: 清理的项目数量
        """
        try:
            Query_obj = Query()
            current_time = datetime.now().isoformat()
            
            # 查找过期项目
            expired_items = self.recycle_table.search(Query_obj.expires_at < current_time)
            expired_count = len(expired_items)
            
            if expired_count > 0:
                # 删除过期项目
                self.recycle_table.remove(Query_obj.expires_at < current_time)
                logger.info(f"Cleaned up {expired_count} expired recycle bin items")
            
            return expired_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {sanitize_for_log(str(e))}")
            return 0
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        获取回收站统计信息
        
        Returns:
            Dict: 统计信息
        """
        try:
            all_items = self.recycle_table.all()
            current_time = datetime.now()
            
            stats = {
                'total_items': len(all_items),
                'by_type': {},
                'expired_items': 0,
                'expiring_soon': 0,  # 24小时内过期
                'oldest_item': None,
                'newest_item': None
            }
            
            if not all_items:
                return stats
            
            # 按类型统计
            for item in all_items:
                item_type = item['item_type']
                stats['by_type'][item_type] = stats['by_type'].get(item_type, 0) + 1
                
                # 检查过期状态
                expires_at = datetime.fromisoformat(item['expires_at'])
                if expires_at <= current_time:
                    stats['expired_items'] += 1
                elif expires_at <= current_time + timedelta(hours=24):
                    stats['expiring_soon'] += 1
            
            # 最新和最旧项目
            sorted_items = sorted(all_items, key=lambda x: x['deleted_at'])
            stats['oldest_item'] = sorted_items[0]['deleted_at']
            stats['newest_item'] = sorted_items[-1]['deleted_at']
            
            return stats
            
        except Exception as e:
            logger.error(f"Failed to get recycle bin statistics: {sanitize_for_log(str(e))}")
            return {'total_items': 0, 'by_type': {}, 'expired_items': 0, 'expiring_soon': 0}
    
    def empty_recycle_bin(self, force: bool = False) -> Tuple[int, int]:
        """
        清空回收站
        
        Args:
            force: 是否强制删除未过期项目
            
        Returns:
            Tuple[int, int]: (删除的项目数, 跳过的项目数)
        """
        try:
            all_items = self.recycle_table.all()
            deleted_count = 0
            skipped_count = 0
            
            current_time = datetime.now()
            
            for item in all_items:
                expires_at = datetime.fromisoformat(item['expires_at'])
                
                # 如果强制删除或已过期，则删除
                if force or expires_at <= current_time:
                    Query_obj = Query()
                    self.recycle_table.remove(Query_obj.id == item['id'])
                    deleted_count += 1
                else:
                    skipped_count += 1
            
            logger.info(f"Emptied recycle bin: deleted {deleted_count}, skipped {skipped_count}")
            return deleted_count, skipped_count
            
        except Exception as e:
            logger.error(f"Failed to empty recycle bin: {sanitize_for_log(str(e))}")
            return 0, 0
    
    def close(self):
        """关闭数据库连接"""
        if not self.use_unified_db:
            # 只有非统一数据库模式才需要手动关闭
            self.db.close()
        logger.info("RecycleBinService closed")


# 全局回收站服务实例
_recycle_bin_service = None

def get_recycle_bin_service(use_unified_db: bool = True) -> RecycleBinService:
    """获取回收站服务实例"""
    global _recycle_bin_service
    if _recycle_bin_service is None:
        _recycle_bin_service = RecycleBinService(use_unified_db=use_unified_db)
    return _recycle_bin_service