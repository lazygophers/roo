"""
MCP工具权限控制系统
根据环境模式（local/remote）控制MCP工具的访问权限
"""
import os
from typing import Dict, List, Set
from app.core.logging import setup_logging

logger = setup_logging()


class MCPPermissionLevel:
    """权限级别定义"""
    READ_ONLY = "read_only"
    WRITE = "write"
    ADMIN = "admin"


class MCPPermissionManager:
    """MCP工具权限管理器"""

    def __init__(self, environment: str = None):
        self.environment = (environment or os.getenv("ENVIRONMENT", "local")).lower()
        self._init_tool_permissions()

    def _init_tool_permissions(self):
        """初始化工具权限分类"""
        # 只读工具 - 在remote模式下允许
        self.read_only_tools: Set[str] = {
            # GitHub 只读操作
            "github_get_repository",
            "github_list_repositories",
            "github_get_user",
            "github_list_issues",
            "github_list_pull_requests",
            "github_list_branches",
            "github_get_branch",
            "github_list_commits",
            "github_get_commit",
            "github_list_releases",
            "github_get_latest_release",
            "github_search_repositories",
            "github_search_issues",
            "github_search_code",
            "github_search_users",
            "github_get_file_contents",
            "github_get_pull_request",
            "github_get_pull_request_files",
            "github_get_issue",
            "github_list_workflows",
            "github_list_workflow_runs",
            "github_get_workflow_run",
            "github_list_tags",

            # 时间工具（纯计算，无副作用）
            "time_get_ts",
            "time_format",
            "time_convert_tz",
            "time_parse",
            "time_calc_diff",
            "time_get_tz_info",

            # 系统信息获取（只读）
            "system_get_info",

            # 文件只读操作
            "file_read",
            "file_ls_dir",
            "file_info",
            "file_get_sec_info",

            # 缓存只读操作
            "cache_get",
            "cache_exists",
            "cache_ttl",
            "cache_keys",
            "cache_mget",
            "cache_info",

            # Web抓取（只读外部数据）
            "web-scraping_http_request",
            "web-scraping_webpage",
            "web-scraping_parse_html",
            "web-scraping_parse_json",
            "web-scraping_parse_markdown",
            "web-scraping_parse_rss",
            "web-scraping_parse_xml",
            "web-scraping_extract_css_selector",
            "web-scraping_smart_extract_and_parse"
        }

        # 写入工具 - 在remote模式下禁用
        self.write_tools: Set[str] = {
            # GitHub 写入操作
            "github_create_repository",
            "github_create_issue",
            "github_create_pull_request",
            "github_create_branch",
            "github_create_release",
            "github_create_or_update_file",
            "github_delete_file",
            "github_fork_repository",
            "github_merge_pull_request",
            "github_update_issue",
            "github_add_issue_comment",

            # 文件写入操作
            "file_write",
            "file_new_dir",
            "file_del_file",
            "file_update_sec_limits",
            "file_reload_sec_config",

            # 缓存写入操作
            "cache_set",
            "cache_del",
            "cache_expire",
            "cache_incr",
            "cache_mset",
            "cache_flushall",

            # Web抓取写入操作
            "web-scraping_download_file",
            "web-scraping_api_call",
            "web-scraping_batch_requests"
        }

        logger.info(f"MCP权限管理器初始化完成 - 环境: {self.environment}")
        logger.info(f"只读工具: {len(self.read_only_tools)}个, 写入工具: {len(self.write_tools)}个")

    def is_tool_allowed(self, tool_name: str) -> bool:
        """检查工具是否允许在当前环境下使用"""
        if self.environment == "local":
            # local模式下允许所有工具
            return True
        elif self.environment == "remote":
            # remote模式下只允许只读工具
            return tool_name in self.read_only_tools
        else:
            # 未知环境，默认只允许只读
            logger.warning(f"未知环境: {self.environment}, 默认只允许只读工具")
            return tool_name in self.read_only_tools

    def get_permission_level(self, tool_name: str) -> str:
        """获取工具的权限级别"""
        if tool_name in self.read_only_tools:
            return MCPPermissionLevel.READ_ONLY
        elif tool_name in self.write_tools:
            return MCPPermissionLevel.WRITE
        else:
            # 未分类的工具默认为admin级别（最高权限）
            return MCPPermissionLevel.ADMIN

    def get_blocked_tools(self) -> List[str]:
        """获取在当前环境下被阻止的工具列表"""
        if self.environment == "local":
            return []
        else:
            return list(self.write_tools)

    def get_allowed_tools(self) -> List[str]:
        """获取在当前环境下允许的工具列表"""
        if self.environment == "local":
            return list(self.read_only_tools | self.write_tools)
        else:
            return list(self.read_only_tools)

    def get_permission_info(self) -> Dict[str, any]:
        """获取权限系统信息"""
        return {
            "environment": self.environment,
            "total_tools": len(self.read_only_tools) + len(self.write_tools),
            "read_only_tools": len(self.read_only_tools),
            "write_tools": len(self.write_tools),
            "allowed_tools": len(self.get_allowed_tools()),
            "blocked_tools": len(self.get_blocked_tools()),
            "restrictions_active": self.environment != "local"
        }


# 全局权限管理器实例
_permission_manager = None

def get_permission_manager() -> MCPPermissionManager:
    """获取权限管理器单例"""
    global _permission_manager
    if _permission_manager is None:
        _permission_manager = MCPPermissionManager()
    return _permission_manager


def refresh_permission_manager(environment: str = None) -> MCPPermissionManager:
    """刷新权限管理器（重新读取环境变量）"""
    global _permission_manager
    _permission_manager = MCPPermissionManager(environment)
    logger.info(f"权限管理器已刷新 - 当前环境: {_permission_manager.environment}")
    return _permission_manager


def check_tool_permission(tool_name: str) -> bool:
    """检查工具权限的便捷函数"""
    return get_permission_manager().is_tool_allowed(tool_name)


def get_tool_permission_level(tool_name: str) -> str:
    """获取工具权限级别的便捷函数"""
    return get_permission_manager().get_permission_level(tool_name)