"""
回收站自动清理调度器
Recycle Bin Automatic Cleanup Scheduler

定期清理过期的回收站项目
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional
from contextlib import asynccontextmanager

from app.core.recycle_bin_service import get_recycle_bin_service
from app.core.file_security_service import get_file_security_service
from app.core.secure_logging import sanitize_for_log
from app.core.logging import setup_logging

logger = setup_logging("INFO")

class RecycleBinScheduler:
    """回收站清理调度器"""
    
    def __init__(self, cleanup_interval_hours: int = 6):
        """
        初始化调度器
        
        Args:
            cleanup_interval_hours: 清理间隔（小时），默认6小时
        """
        self.cleanup_interval_hours = cleanup_interval_hours
        self.cleanup_interval_seconds = cleanup_interval_hours * 3600
        self.running = False
        self.task: Optional[asyncio.Task] = None
        
        logger.info(f"RecycleBinScheduler initialized with {cleanup_interval_hours}h interval")
    
    def _get_current_config(self) -> dict:
        """获取当前回收站配置"""
        try:
            security_service = get_file_security_service()
            
            # 获取回收站相关配置
            enabled_config = security_service.get_limit_config("recycle_bin_enabled")
            cleanup_hours_config = security_service.get_limit_config("recycle_bin_auto_cleanup_hours")
            retention_days_config = security_service.get_limit_config("recycle_bin_retention_days")
            
            return {
                "enabled": enabled_config.get("value", True) if enabled_config else True,
                "cleanup_hours": cleanup_hours_config.get("value", 6) if cleanup_hours_config else 6,
                "retention_days": retention_days_config.get("value", 3) if retention_days_config else 3
            }
        except Exception as e:
            logger.error(f"Failed to get recycle bin config: {sanitize_for_log(str(e))}")
            # 返回默认配置
            return {"enabled": True, "cleanup_hours": 6, "retention_days": 3}
    
    def _should_run_cleanup(self) -> bool:
        """检查是否应该运行清理"""
        config = self._get_current_config()
        return config["enabled"] and config["cleanup_hours"] > 0
    
    async def cleanup_expired_items(self) -> int:
        """清理过期项目"""
        try:
            recycle_service = get_recycle_bin_service()
            cleaned_count = recycle_service.cleanup_expired_items()
            
            if cleaned_count > 0:
                logger.info(f"Scheduled cleanup: removed {cleaned_count} expired items")
            else:
                logger.debug("Scheduled cleanup: no expired items to clean")
                
            return cleaned_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired items: {sanitize_for_log(str(e))}")
            return 0
    
    async def _cleanup_loop(self):
        """清理循环任务"""
        logger.info("Started recycle bin cleanup scheduler loop")
        
        while self.running:
            try:
                # 检查是否应该运行清理
                if self._should_run_cleanup():
                    # 执行清理
                    await self.cleanup_expired_items()
                    
                    # 获取当前配置的清理间隔
                    config = self._get_current_config()
                    wait_seconds = config["cleanup_hours"] * 3600
                    
                    logger.debug(f"Next cleanup in {config['cleanup_hours']} hours")
                else:
                    # 如果回收站功能被禁用或自动清理关闭，等待1小时后重新检查
                    wait_seconds = 3600
                    logger.debug("Recycle bin disabled or auto-cleanup off, checking again in 1 hour")
                
                # 等待下次清理时间
                await asyncio.sleep(wait_seconds)
                
            except asyncio.CancelledError:
                logger.info("Recycle bin cleanup scheduler loop cancelled")
                break
            except Exception as e:
                logger.error(f"Error in cleanup loop: {sanitize_for_log(str(e))}")
                # 出错后等待较短时间再重试
                await asyncio.sleep(300)  # 5分钟
    
    async def start(self):
        """启动调度器"""
        if self.running:
            logger.warning("Recycle bin scheduler is already running")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._cleanup_loop())
        logger.info(f"Recycle bin scheduler started (cleanup every {self.cleanup_interval_hours}h)")
        
        # 启动时执行一次清理
        await self.cleanup_expired_items()
    
    async def stop(self):
        """停止调度器"""
        if not self.running:
            logger.warning("Recycle bin scheduler is not running")
            return
        
        self.running = False
        
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
            self.task = None
        
        logger.info("Recycle bin scheduler stopped")
    
    def is_running(self) -> bool:
        """检查调度器是否运行中"""
        return self.running and self.task is not None and not self.task.done()
    
    def get_status(self) -> dict:
        """获取调度器状态"""
        config = self._get_current_config()
        return {
            "running": self.running,
            "cleanup_interval_hours": config["cleanup_hours"],
            "recycle_bin_enabled": config["enabled"],
            "retention_days": config["retention_days"],
            "task_status": "running" if self.is_running() else "stopped",
            "auto_cleanup_enabled": config["enabled"] and config["cleanup_hours"] > 0,
            "next_cleanup_in_seconds": config["cleanup_hours"] * 3600 if (self.running and config["enabled"] and config["cleanup_hours"] > 0) else None
        }

# 全局调度器实例
_scheduler: Optional[RecycleBinScheduler] = None

def get_recycle_bin_scheduler(cleanup_interval_hours: int = 6) -> RecycleBinScheduler:
    """获取回收站调度器实例"""
    global _scheduler
    if _scheduler is None:
        _scheduler = RecycleBinScheduler(cleanup_interval_hours=cleanup_interval_hours)
    return _scheduler

@asynccontextmanager
async def recycle_bin_scheduler_lifespan():
    """回收站调度器生命周期管理器"""
    scheduler = get_recycle_bin_scheduler()
    
    try:
        # 启动调度器
        await scheduler.start()
        yield scheduler
    finally:
        # 停止调度器
        await scheduler.stop()

# FastAPI 生命周期事件处理
async def startup_recycle_bin_scheduler():
    """应用启动时启动回收站调度器"""
    try:
        scheduler = get_recycle_bin_scheduler()
        await scheduler.start()
        logger.info("Recycle bin scheduler startup completed")
    except Exception as e:
        logger.error(f"Failed to start recycle bin scheduler: {sanitize_for_log(str(e))}")

async def shutdown_recycle_bin_scheduler():
    """应用关闭时停止回收站调度器"""
    try:
        scheduler = get_recycle_bin_scheduler()
        await scheduler.stop()
        logger.info("Recycle bin scheduler shutdown completed")
    except Exception as e:
        logger.error(f"Failed to stop recycle bin scheduler: {sanitize_for_log(str(e))}")

# 手动触发清理的便捷函数
async def manual_cleanup_expired_items() -> dict:
    """手动触发过期项目清理"""
    try:
        start_time = datetime.now()
        
        recycle_service = get_recycle_bin_service()
        cleaned_count = recycle_service.cleanup_expired_items()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        result = {
            "status": "success",
            "cleaned_count": cleaned_count,
            "duration_seconds": round(duration, 2),
            "timestamp": end_time.isoformat()
        }
        
        logger.info(f"Manual cleanup completed: {result}")
        return result
        
    except Exception as e:
        error_msg = f"Manual cleanup failed: {str(e)}"
        logger.error(f"Manual cleanup error: {sanitize_for_log(str(e))}")
        return {
            "status": "error",
            "error": error_msg,
            "cleaned_count": 0,
            "timestamp": datetime.now().isoformat()
        }

# 获取清理统计信息
def get_cleanup_statistics() -> dict:
    """获取清理统计信息"""
    try:
        recycle_service = get_recycle_bin_service()
        stats = recycle_service.get_statistics()
        scheduler = get_recycle_bin_scheduler()
        
        return {
            "recycle_bin_stats": stats,
            "scheduler_status": scheduler.get_status(),
            "last_check": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get cleanup statistics: {sanitize_for_log(str(e))}")
        return {
            "error": str(e),
            "last_check": datetime.now().isoformat()
        }