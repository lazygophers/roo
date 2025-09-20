"""
MCP全局配置服务
管理MCP工具的全局配置，包括代理、网络、安全等设置
"""
import os
import json
import threading
from typing import Dict, Any, Optional
from pathlib import Path

from app.models.mcp_config import MCPGlobalConfig, EnvironmentType
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.config import ENVIRONMENT

logger = setup_logging()


class MCPConfigService:
    """MCP配置服务"""

    def __init__(self, config_file: str = "data/mcp_config.json"):
        self.config_file = Path(config_file)
        self.config_file.parent.mkdir(parents=True, exist_ok=True)
        self._config: Optional[MCPGlobalConfig] = None
        self._lock = threading.RLock()
        self._load_config()

    def _load_config(self):
        """加载配置文件"""
        with self._lock:
            try:
                if self.config_file.exists():
                    with open(self.config_file, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    self._config = MCPGlobalConfig.from_dict(data)
                    logger.info(f"Loaded MCP config from {self.config_file}")
                else:
                    # 创建默认配置
                    self._config = MCPGlobalConfig()
                    self._save_config()
                    logger.info("Created default MCP config")
            except Exception as e:
                logger.error(f"Failed to load MCP config: {e}")
                # 使用默认配置
                self._config = MCPGlobalConfig()

    def _save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self._config.to_dict(), f, indent=2, ensure_ascii=False)
            logger.debug("Saved MCP config")
            # 触发工具客户端重新加载配置
            self._reload_tool_clients()
        except Exception as e:
            logger.error(f"Failed to save MCP config: {e}")
            raise

    def get_config(self) -> MCPGlobalConfig:
        """获取当前配置"""
        with self._lock:
            return self._config

    def update_config(self, updates: Dict[str, Any]) -> MCPGlobalConfig:
        """更新配置"""
        with self._lock:
            try:
                # 创建新的配置对象
                current_dict = self._config.to_dict()
                current_dict.update(updates)
                new_config = MCPGlobalConfig.from_dict(current_dict)

                # 保存配置
                self._config = new_config
                self._save_config()

                logger.info(f"Updated MCP config: {sanitize_for_log(list(updates.keys()))}")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update MCP config: {e}")
                raise

    def update_proxy_config(self, proxy_config: Dict[str, Any]) -> MCPGlobalConfig:
        """更新代理配置"""
        with self._lock:
            try:
                current_dict = self._config.to_dict()
                current_dict["proxy"].update(proxy_config)
                new_config = MCPGlobalConfig.from_dict(current_dict)

                self._config = new_config
                self._save_config()

                logger.info("Updated MCP proxy config")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update proxy config: {e}")
                raise

    def update_network_config(self, network_config: Dict[str, Any]) -> MCPGlobalConfig:
        """更新网络配置"""
        with self._lock:
            try:
                current_dict = self._config.to_dict()
                current_dict["network"].update(network_config)
                new_config = MCPGlobalConfig.from_dict(current_dict)

                self._config = new_config
                self._save_config()

                logger.info("Updated MCP network config")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update network config: {e}")
                raise

    def update_security_config(self, security_config: Dict[str, Any]) -> MCPGlobalConfig:
        """更新安全配置"""
        with self._lock:
            try:
                current_dict = self._config.to_dict()
                current_dict["security"].update(security_config)
                new_config = MCPGlobalConfig.from_dict(current_dict)

                self._config = new_config
                self._save_config()

                logger.info("Updated MCP security config")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update security config: {e}")
                raise

    def update_tool_category_config(self, category: str, config: Dict[str, Any]) -> MCPGlobalConfig:
        """更新工具分类配置"""
        with self._lock:
            try:
                self._config.update_category_config(
                    category=category,
                    enabled=config.get("enabled"),
                    custom_config=config.get("custom_config")
                )
                self._save_config()

                logger.info(f"Updated tool category config for {sanitize_for_log(category)}")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update tool category config: {e}")
                raise

    def update_environment_variables(self, env_vars: Dict[str, str]) -> MCPGlobalConfig:
        """更新环境变量配置"""
        with self._lock:
            try:
                current_dict = self._config.to_dict()
                current_dict["environment_variables"].update(env_vars)
                new_config = MCPGlobalConfig.from_dict(current_dict)

                self._config = new_config
                self._save_config()

                # 同时更新系统环境变量
                for key, value in env_vars.items():
                    if value:
                        os.environ[key] = value
                    elif key in os.environ:
                        del os.environ[key]

                logger.info(f"Updated environment variables: {sanitize_for_log(list(env_vars.keys()))}")
                return self._config
            except Exception as e:
                logger.error(f"Failed to update environment variables: {e}")
                raise

    def get_proxy_config(self) -> Dict[str, Any]:
        """获取代理配置"""
        return self._config.proxy.to_dict()

    def get_requests_proxy_config(self) -> Optional[Dict[str, str]]:
        """获取适用于requests库的代理配置"""
        return self._config.get_proxy_dict()

    def get_network_config(self) -> Dict[str, Any]:
        """获取网络配置"""
        return self._config.network.to_dict()

    def get_security_config(self) -> Dict[str, Any]:
        """获取安全配置"""
        return self._config.security.to_dict()

    def get_tool_category_config(self, category: str) -> Dict[str, Any]:
        """获取工具分类配置"""
        if category in self._config.tool_categories:
            return self._config.tool_categories[category].to_dict()
        else:
            # 返回默认配置
            return {"category": category, "enabled": True, "custom_config": {}}

    def get_environment_variables(self) -> Dict[str, str]:
        """获取环境变量配置"""
        return self._config.environment_variables.copy()

    def is_category_enabled(self, category: str) -> bool:
        """检查工具分类是否启用"""
        if category in self._config.tool_categories:
            return self._config.tool_categories[category].enabled
        return True  # 默认启用

    def is_host_allowed(self, host: str) -> bool:
        """检查主机是否被允许访问"""
        # 如果没有配置允许列表，则默认允许
        if not self._config.security.allowed_hosts:
            return True

        # 检查是否在允许列表中
        return host in self._config.security.allowed_hosts

    def is_host_blocked(self, host: str) -> bool:
        """检查主机是否被阻止访问"""
        return host in self._config.security.blocked_hosts

    def is_tool_call_allowed(self) -> bool:
        """检查是否允许调用MCP工具"""
        # 如果是远程环境，不允许调用工具
        if self._config.is_remote_environment():
            return False
        # 也可以从环境变量检查
        if ENVIRONMENT == "remote":
            return False
        return True

    def is_tool_edit_allowed(self) -> bool:
        """检查是否允许编辑MCP工具配置"""
        # 使用权限管理器检查当前环境
        try:
            from app.core.mcp_permissions import get_permission_manager
            permission_manager = get_permission_manager()
            # 在remote模式下，禁用所有编辑功能
            return permission_manager.environment == "local"
        except ImportError:
            # 如果权限管理器不可用，回退到原有逻辑
            if self._config.is_remote_environment():
                return False
            if ENVIRONMENT == "remote":
                return False
            return True

    def get_environment_type(self) -> str:
        """获取当前环境类型"""
        return self._config.environment.value

    def reset_to_defaults(self) -> MCPGlobalConfig:
        """重置为默认配置"""
        with self._lock:
            try:
                self._config = MCPGlobalConfig()
                self._save_config()
                logger.info("Reset MCP config to defaults")
                return self._config
            except Exception as e:
                logger.error(f"Failed to reset MCP config: {e}")
                raise

    def export_config(self) -> Dict[str, Any]:
        """导出配置"""
        return self._config.to_dict()

    def import_config(self, config_data: Dict[str, Any]) -> MCPGlobalConfig:
        """导入配置"""
        with self._lock:
            try:
                self._config = MCPGlobalConfig.from_dict(config_data)
                self._save_config()
                logger.info("Imported MCP config")
                return self._config
            except Exception as e:
                logger.error(f"Failed to import MCP config: {e}")
                raise

    def _reload_tool_clients(self):
        """重新加载工具客户端配置"""
        try:
            # 重新加载GitHub工具客户端配置
            from app.tools.github_tools import reload_github_client_config
            reload_github_client_config()
            logger.debug("Reloaded GitHub tools configuration")
        except ImportError:
            logger.debug("GitHub tools module not available, skipping client reload")
        except Exception as e:
            logger.error(f"Failed to reload GitHub tools: {e}")

        try:
            # 重新加载网络抓取工具配置
            from app.tools.web_scraping_tools import reload_web_scraping_config
            reload_web_scraping_config()
            logger.debug("Reloaded web scraping tools configuration")
        except ImportError:
            logger.debug("Web scraping tools module not available, skipping reload")
        except Exception as e:
            logger.error(f"Failed to reload web scraping tools: {e}")

        logger.debug("Reloaded all available tool clients configuration")


# 全局配置服务实例
_mcp_config_service: Optional[MCPConfigService] = None


def init_mcp_config_service(config_file: str = "data/mcp_config.json") -> MCPConfigService:
    """初始化MCP配置服务"""
    global _mcp_config_service
    if _mcp_config_service is None:
        _mcp_config_service = MCPConfigService(config_file)
    return _mcp_config_service


def get_mcp_config_service() -> MCPConfigService:
    """获取MCP配置服务单例"""
    global _mcp_config_service
    if _mcp_config_service is None:
        _mcp_config_service = MCPConfigService()
    return _mcp_config_service


def get_mcp_config() -> MCPGlobalConfig:
    """获取MCP全局配置的便捷函数"""
    return get_mcp_config_service().get_config()


def get_proxy_for_requests() -> Optional[Dict[str, str]]:
    """获取适用于requests库的代理配置的便捷函数"""
    return get_mcp_config_service().get_requests_proxy_config()