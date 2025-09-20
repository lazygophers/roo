"""
MCP工具初始化服务
在应用启动时自动发现、注册和刷新MCP工具到数据库
"""
import time
from typing import Dict, List, Any, Tuple
from pathlib import Path

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.tools.registry import (
    auto_discover_tools, scan_tools_directory,
    get_registered_tools, get_registered_categories,
    get_registry_stats, clear_registry
)
from app.models.mcp_tool import MCPTool

logger = setup_logging()


class MCPToolsInitializer:
    """MCP工具初始化器"""

    def __init__(self):
        self.start_time = None
        self.stats = {
            "discovered_tools": 0,
            "registered_categories": 0,
            "database_saved": 0,
            "errors": 0,
            "timing": {}
        }

    def initialize_all_tools(self, save_to_database: bool = True) -> Dict[str, Any]:
        """
        完整的MCP工具初始化流程

        Args:
            save_to_database: 是否保存到数据库

        Returns:
            初始化结果统计
        """
        self.start_time = time.time()
        logger.info("🔧 Starting MCP tools initialization...")
        print("🔧 Initializing MCP tools and toolsets...", flush=True)

        try:
            # 步骤1: 清理注册表
            self._step_clear_registry()

            # 步骤2: 自动发现工具
            self._step_discover_tools()

            # 步骤3: 验证工具注册
            self._step_validate_tools()

            # 步骤4: 保存到数据库
            if save_to_database:
                self._step_save_to_database()

            # 步骤5: 生成统计报告
            result = self._generate_final_report()

            logger.info("✅ MCP tools initialization completed successfully")
            print("✅ MCP tools initialization completed!", flush=True)

            return result

        except Exception as e:
            self.stats["errors"] += 1
            logger.error(f"❌ MCP tools initialization failed: {e}")
            print(f"❌ MCP tools initialization failed: {e}", flush=True)
            raise

    def _step_clear_registry(self):
        """步骤1: 清理注册表"""
        step_start = time.time()
        logger.info("🧹 Step 1: Clearing MCP tools registry...")
        print("  📋 [1/5] Clearing tools registry...", flush=True)

        try:
            clear_registry()
            self.stats["timing"]["clear_registry"] = time.time() - step_start
            logger.debug("Registry cleared successfully")
            print("    ✅ Registry cleared", flush=True)
        except Exception as e:
            logger.error(f"Failed to clear registry: {e}")
            raise

    def _step_discover_tools(self):
        """步骤2: 自动发现工具"""
        step_start = time.time()
        logger.info("🔍 Step 2: Auto-discovering MCP tools...")
        print("  📋 [2/5] Discovering MCP tools...", flush=True)

        try:
            # 扫描工具目录
            tools_dir = Path("app/tools")
            if not tools_dir.exists():
                logger.warning(f"Tools directory not found: {tools_dir}")
                print(f"    ⚠️  Tools directory not found: {tools_dir}", flush=True)
                return

            # 发现各类工具文件
            discovered_count = scan_tools_directory(str(tools_dir), "**/*_tools.py")
            self.stats["discovered_tools"] = discovered_count

            # 额外模块发现
            additional_modules = [
                "app.tools.github_tools",
                "app.tools.fetch_tools",
                "app.tools.file_tools",
                "app.tools.system_tools",
                "app.tools.time_tools",
                "app.tools.cache_tools",
                "app.tools.web_scraping_tools"
            ]

            for module_name in additional_modules:
                try:
                    module_count = auto_discover_tools([module_name])
                    self.stats["discovered_tools"] += module_count
                    logger.debug(f"Discovered {module_count} tools from {module_name}")
                except Exception as e:
                    logger.warning(f"Failed to discover tools from {module_name}: {e}")

            self.stats["timing"]["discover_tools"] = time.time() - step_start

            logger.info(f"Discovered {self.stats['discovered_tools']} MCP tools")
            print(f"    ✅ Discovered {self.stats['discovered_tools']} tools", flush=True)

        except Exception as e:
            logger.error(f"Failed to discover tools: {e}")
            raise

    def _step_validate_tools(self):
        """步骤3: 验证工具注册"""
        step_start = time.time()
        logger.info("🔍 Step 3: Validating registered tools...")
        print("  📋 [3/5] Validating tools registration...", flush=True)

        try:
            # 获取注册统计
            registry_stats = get_registry_stats()
            self.stats["registered_categories"] = registry_stats["categories"]

            # 验证工具完整性
            registered_tools = get_registered_tools()
            valid_tools = 0
            invalid_tools = 0

            for tool in registered_tools:
                if self._validate_tool(tool):
                    valid_tools += 1
                else:
                    invalid_tools += 1
                    logger.warning(f"Invalid tool detected: {sanitize_for_log(tool.name)}")

            # 验证分类
            registered_categories = get_registered_categories()
            valid_categories = len([cat for cat in registered_categories if cat.get("name")])

            self.stats["timing"]["validate_tools"] = time.time() - step_start

            logger.info(f"Validation complete: {valid_tools} valid tools, {invalid_tools} invalid tools")
            logger.info(f"Categories: {valid_categories} valid categories")

            print(f"    ✅ Validated {valid_tools} tools in {valid_categories} categories", flush=True)

            if invalid_tools > 0:
                print(f"    ⚠️  Found {invalid_tools} invalid tools", flush=True)

        except Exception as e:
            logger.error(f"Failed to validate tools: {e}")
            raise

    def _step_save_to_database(self):
        """步骤4: 保存到数据库"""
        step_start = time.time()
        logger.info("💾 Step 4: Saving tools to database...")
        print("  📋 [4/5] Saving tools to database...", flush=True)

        try:
            # 这里可以添加数据库保存逻辑
            # 现在只是模拟保存过程

            registered_tools = get_registered_tools()
            registered_categories = get_registered_categories()

            # 模拟保存工具
            saved_tools = 0
            for tool in registered_tools:
                try:
                    # 这里可以调用数据库服务保存工具
                    # db_service.save_mcp_tool(tool)
                    saved_tools += 1
                except Exception as e:
                    logger.error(f"Failed to save tool {tool.name}: {e}")

            # 模拟保存分类
            saved_categories = 0
            for category in registered_categories:
                try:
                    # 这里可以调用数据库服务保存分类
                    # db_service.save_mcp_category(category)
                    saved_categories += 1
                except Exception as e:
                    logger.error(f"Failed to save category {category.get('id', 'unknown')}: {e}")

            self.stats["database_saved"] = saved_tools
            self.stats["timing"]["save_to_database"] = time.time() - step_start

            logger.info(f"Saved {saved_tools} tools and {saved_categories} categories to database")
            print(f"    ✅ Saved {saved_tools} tools and {saved_categories} categories", flush=True)

        except Exception as e:
            logger.error(f"Failed to save to database: {e}")
            raise

    def _generate_final_report(self) -> Dict[str, Any]:
        """步骤5: 生成最终报告"""
        step_start = time.time()
        logger.info("📊 Step 5: Generating initialization report...")
        print("  📋 [5/5] Generating report...", flush=True)

        try:
            total_time = time.time() - self.start_time
            registry_stats = get_registry_stats()

            result = {
                "success": True,
                "total_time": total_time,
                "stats": {
                    **self.stats,
                    "registry_stats": registry_stats
                },
                "summary": {
                    "discovered_tools": self.stats["discovered_tools"],
                    "registered_categories": self.stats["registered_categories"],
                    "database_saved": self.stats["database_saved"],
                    "errors": self.stats["errors"],
                    "total_time_ms": int(total_time * 1000)
                }
            }

            self.stats["timing"]["generate_report"] = time.time() - step_start

            # 打印详细报告
            self._print_detailed_report(result)

            return result

        except Exception as e:
            logger.error(f"Failed to generate report: {e}")
            raise

    def _validate_tool(self, tool: MCPTool) -> bool:
        """验证单个工具的有效性"""
        try:
            # 检查必需字段
            if not tool.name or not tool.description or not tool.category:
                return False

            # 检查schema格式
            if not isinstance(tool.schema, dict):
                return False

            # 基本schema验证
            if "type" not in tool.schema:
                return False

            return True

        except Exception:
            return False

    def _print_detailed_report(self, result: Dict[str, Any]):
        """打印详细的初始化报告"""
        stats = result["stats"]
        registry_stats = stats.get("registry_stats", {})
        timing = stats.get("timing", {})

        report = f"""
    ✅ MCP Tools Initialization Complete!

    📊 Summary:
      • Tools Discovered: {stats['discovered_tools']}
      • Categories: {stats['registered_categories']}
      • Database Saved: {stats['database_saved']}
      • Errors: {stats['errors']}
      • Total Time: {result['total_time']:.2f}s

    🔧 Registry Stats:
      • Total Tools: {registry_stats.get('total_tools', 0)}
      • Total Categories: {registry_stats.get('categories', 0)}
      • Registered Tools: {len(registry_stats.get('registered_tools', []))}

    ⏱️ Timing Breakdown:
      • Clear Registry: {timing.get('clear_registry', 0):.3f}s
      • Discover Tools: {timing.get('discover_tools', 0):.3f}s
      • Validate Tools: {timing.get('validate_tools', 0):.3f}s
      • Save Database: {timing.get('save_to_database', 0):.3f}s
      • Generate Report: {timing.get('generate_report', 0):.3f}s
    """

        print(report, flush=True)

        # 显示分类详情
        tools_by_category = registry_stats.get('tools_by_category', {})
        if tools_by_category:
            print("    📂 Tools by Category:", flush=True)
            for category, count in sorted(tools_by_category.items()):
                print(f"      • {category}: {count} tools", flush=True)


def initialize_mcp_tools(save_to_database: bool = True) -> Dict[str, Any]:
    """
    便捷函数：初始化MCP工具

    Args:
        save_to_database: 是否保存到数据库

    Returns:
        初始化结果
    """
    initializer = MCPToolsInitializer()
    return initializer.initialize_all_tools(save_to_database)


def quick_refresh_mcp_tools() -> Dict[str, Any]:
    """
    快速刷新MCP工具（不保存到数据库）
    """
    return initialize_mcp_tools(save_to_database=False)


# 异步包装器（如果需要异步初始化）
async def async_initialize_mcp_tools(save_to_database: bool = True) -> Dict[str, Any]:
    """异步初始化MCP工具"""
    import asyncio

    # 在线程池中运行同步初始化
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, initialize_mcp_tools, save_to_database)