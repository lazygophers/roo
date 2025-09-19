"""
MCP全局配置模型定义
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class EnvironmentType(str, Enum):
    """环境类型枚举"""
    LOCAL = "local"  # 本地环境：所有功能可用
    REMOTE = "remote"  # 远程环境：仅可查看，不可编辑和调用


@dataclass
class ProxyConfig:
    """代理配置模型"""
    enabled: bool = False
    proxy: str = ""  # 统一的代理地址，同时用于HTTP和HTTPS
    no_proxy: str = ""  # 不使用代理的地址列表，逗号分隔
    username: str = ""
    password: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "enabled": self.enabled,
            "proxy": self.proxy,
            "no_proxy": self.no_proxy,
            "username": self.username,
            "password": self.password
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ProxyConfig':
        """从字典创建实例"""
        # 支持向后兼容：如果存在旧格式的http_proxy或https_proxy，优先使用https_proxy
        proxy = data.get("proxy", "")
        if not proxy:
            proxy = data.get("https_proxy", data.get("http_proxy", ""))

        return cls(
            enabled=data.get("enabled", False),
            proxy=proxy,
            no_proxy=data.get("no_proxy", ""),
            username=data.get("username", ""),
            password=data.get("password", "")
        )


@dataclass
class NetworkConfig:
    """网络配置模型"""
    timeout: int = 30  # 请求超时时间（秒）
    retry_times: int = 3  # 重试次数
    retry_delay: float = 1.0  # 重试延迟（秒）
    user_agent: str = "LazyAI-Studio-MCP/1.0"
    max_connections: int = 100  # 最大连接数

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "timeout": self.timeout,
            "retry_times": self.retry_times,
            "retry_delay": self.retry_delay,
            "user_agent": self.user_agent,
            "max_connections": self.max_connections
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'NetworkConfig':
        """从字典创建实例"""
        return cls(
            timeout=data.get("timeout", 30),
            retry_times=data.get("retry_times", 3),
            retry_delay=data.get("retry_delay", 1.0),
            user_agent=data.get("user_agent", "LazyAI-Studio-MCP/1.0"),
            max_connections=data.get("max_connections", 100)
        )


@dataclass
class SecurityConfig:
    """安全配置模型"""
    verify_ssl: bool = True  # 验证SSL证书
    allowed_hosts: list = field(default_factory=list)  # 允许访问的主机列表
    blocked_hosts: list = field(default_factory=list)  # 禁止访问的主机列表
    enable_rate_limit: bool = True  # 启用速率限制
    rate_limit_per_minute: int = 60  # 每分钟请求限制

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "verify_ssl": self.verify_ssl,
            "allowed_hosts": self.allowed_hosts,
            "blocked_hosts": self.blocked_hosts,
            "enable_rate_limit": self.enable_rate_limit,
            "rate_limit_per_minute": self.rate_limit_per_minute
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'SecurityConfig':
        """从字典创建实例"""
        return cls(
            verify_ssl=data.get("verify_ssl", True),
            allowed_hosts=data.get("allowed_hosts", []),
            blocked_hosts=data.get("blocked_hosts", []),
            enable_rate_limit=data.get("enable_rate_limit", True),
            rate_limit_per_minute=data.get("rate_limit_per_minute", 60)
        )


@dataclass
class ToolCategoryConfig:
    """工具分类配置模型"""
    category: str
    enabled: bool = True
    custom_config: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "category": self.category,
            "enabled": self.enabled,
            "custom_config": self.custom_config
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ToolCategoryConfig':
        """从字典创建实例"""
        return cls(
            category=data["category"],
            enabled=data.get("enabled", True),
            custom_config=data.get("custom_config", {})
        )


@dataclass
class MCPGlobalConfig:
    """MCP全局配置模型"""
    # 基本配置
    enabled: bool = True
    debug_mode: bool = False
    log_level: str = "INFO"

    # 环境配置
    environment: EnvironmentType = EnvironmentType.LOCAL

    # 网络配置
    proxy: ProxyConfig = field(default_factory=ProxyConfig)
    network: NetworkConfig = field(default_factory=NetworkConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)

    # 工具配置
    tool_categories: Dict[str, ToolCategoryConfig] = field(default_factory=dict)

    # 环境变量配置
    environment_variables: Dict[str, str] = field(default_factory=dict)

    # 元数据
    version: str = "1.0"
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def __post_init__(self):
        """初始化后处理"""
        if not self.created_at:
            self.created_at = datetime.now().isoformat()
        self.updated_at = datetime.now().isoformat()

    def is_remote_environment(self) -> bool:
        """检查是否为远程环境"""
        return self.environment == EnvironmentType.REMOTE

    def is_local_environment(self) -> bool:
        """检查是否为本地环境"""
        return self.environment == EnvironmentType.LOCAL

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "enabled": self.enabled,
            "debug_mode": self.debug_mode,
            "log_level": self.log_level,
            "environment": self.environment.value,
            "proxy": self.proxy.to_dict(),
            "network": self.network.to_dict(),
            "security": self.security.to_dict(),
            "tool_categories": {
                cat: config.to_dict()
                for cat, config in self.tool_categories.items()
            },
            "environment_variables": self.environment_variables,
            "version": self.version,
            "created_at": self.created_at,
            "updated_at": self.updated_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'MCPGlobalConfig':
        """从字典创建实例"""
        # 解析环境类型
        environment_str = data.get("environment", "local")
        environment = EnvironmentType.LOCAL if environment_str == "local" else EnvironmentType.REMOTE

        config = cls(
            enabled=data.get("enabled", True),
            debug_mode=data.get("debug_mode", False),
            log_level=data.get("log_level", "INFO"),
            environment=environment,
            environment_variables=data.get("environment_variables", {}),
            version=data.get("version", "1.0"),
            created_at=data.get("created_at"),
            updated_at=data.get("updated_at")
        )

        # 解析嵌套配置
        if "proxy" in data:
            config.proxy = ProxyConfig.from_dict(data["proxy"])
        if "network" in data:
            config.network = NetworkConfig.from_dict(data["network"])
        if "security" in data:
            config.security = SecurityConfig.from_dict(data["security"])
        if "tool_categories" in data:
            config.tool_categories = {
                cat: ToolCategoryConfig.from_dict(cat_data)
                for cat, cat_data in data["tool_categories"].items()
            }

        return config

    def get_proxy_dict(self) -> Optional[Dict[str, str]]:
        """获取代理配置字典，适用于requests库"""
        if not self.proxy.enabled or not self.proxy.proxy:
            return None

        # 构建代理URL
        if self.proxy.username and self.proxy.password:
            # 包含认证信息的代理URL
            proxy_base = self.proxy.proxy.replace('http://', '').replace('https://', '')
            proxy_url = f"http://{self.proxy.username}:{self.proxy.password}@{proxy_base}"
        else:
            proxy_url = self.proxy.proxy

        # 统一的代理配置，同时用于HTTP和HTTPS
        return {
            "http": proxy_url,
            "https": proxy_url
        }

    def get_no_proxy_list(self) -> list:
        """获取不使用代理的地址列表"""
        if not self.proxy.no_proxy:
            return []
        return [host.strip() for host in self.proxy.no_proxy.split(",") if host.strip()]

    def update_category_config(self, category: str, enabled: bool = None, custom_config: Dict[str, Any] = None):
        """更新工具分类配置"""
        if category not in self.tool_categories:
            self.tool_categories[category] = ToolCategoryConfig(category=category)

        if enabled is not None:
            self.tool_categories[category].enabled = enabled

        if custom_config is not None:
            self.tool_categories[category].custom_config.update(custom_config)

        self.updated_at = datetime.now().isoformat()