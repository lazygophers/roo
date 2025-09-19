"""
MCP工具注册系统单元测试
MCP Tools Registry System Unit Tests
"""

import pytest
import tempfile
import inspect
from pathlib import Path
from unittest.mock import patch, MagicMock

from app.tools.registry import (
    mcp_category,
    mcp_tool,
    get_registered_tools,
    get_tools_by_category,
    get_tool_by_name,
    clear_registry,
    auto_discover_tools,
    scan_tools_directory,
    get_registry_stats,
    get_registered_categories,
    get_category_definition,
    github_tool,
    time_tool,
    file_tool,
    system_tool,
    cache_tool,
    fetch_tool,
    _scan_module_for_tools,
    _TOOL_REGISTRY,
    _CATEGORY_REGISTRY,
    _CATEGORY_DEFINITIONS
)
from app.models.mcp_tool import MCPTool


class TestMCPCategoryDecorator:
    """测试MCP分类装饰器"""

    def setup_method(self):
        """每个测试前清空注册表"""
        clear_registry()

    def test_mcp_category_basic(self):
        """测试基本分类注册"""
        @mcp_category(
            category_id="test_cat",
            name="测试分类",
            description="这是一个测试分类"
        )
        def test_category():
            return "test"

        # 验证分类定义已注册
        category_def = get_category_definition("test_cat")
        assert category_def is not None
        assert category_def["id"] == "test_cat"
        assert category_def["name"] == "测试分类"
        assert category_def["description"] == "这是一个测试分类"
        assert category_def["icon"] == "📦"  # 默认图标
        assert category_def["enabled"] is True
        assert category_def["sort_order"] == 999

        # 验证装饰器正常工作
        result = test_category()
        assert result == "test"

    def test_mcp_category_with_all_params(self):
        """测试带全部参数的分类注册"""
        config = {"setting1": "value1", "setting2": True}

        @mcp_category(
            category_id="full_cat",
            name="完整分类",
            description="包含所有参数的分类",
            icon="🔧",
            enabled=False,
            sort_order=10,
            config=config
        )
        def full_category():
            pass

        category_def = get_category_definition("full_cat")
        assert category_def["icon"] == "🔧"
        assert category_def["enabled"] is False
        assert category_def["sort_order"] == 10
        assert category_def["config"] == config

    def test_multiple_category_registration(self):
        """测试多个分类注册"""
        @mcp_category("cat1", "分类1", "描述1")
        def category1():
            pass

        @mcp_category("cat2", "分类2", "描述2")
        def category2():
            pass

        categories = get_registered_categories()
        assert len(categories) == 2

        cat_ids = [cat["id"] for cat in categories]
        assert "cat1" in cat_ids
        assert "cat2" in cat_ids


class TestMCPToolDecorator:
    """测试MCP工具装饰器"""

    def setup_method(self):
        """每个测试前清空注册表"""
        clear_registry()

    def test_mcp_tool_basic(self):
        """测试基本工具注册"""
        schema = {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        }

        @mcp_tool(
            name="test_tool",
            description="测试工具",
            category="test",
            schema=schema
        )
        def test_function():
            return "test_result"

        # 验证工具已注册
        tools = get_registered_tools()
        assert len(tools) == 1

        tool = get_tool_by_name("test_test_tool")  # 带分类前缀
        assert tool is not None
        assert tool.name == "test_test_tool"
        assert tool.description == "测试工具"
        assert tool.category == "test"
        assert tool.schema == schema
        assert tool.enabled is True
        assert tool.implementation_type == "builtin"

        # 验证函数正常工作
        result = test_function()
        assert result == "test_result"

        # 验证工具元数据附加到函数
        assert hasattr(test_function, '_mcp_tool')
        assert test_function._mcp_tool == tool

    def test_mcp_tool_with_prefix(self):
        """测试工具名称已有前缀的情况"""
        schema = {"type": "object"}

        @mcp_tool(
            name="test_existing_tool",  # 已有前缀
            description="现有前缀工具",
            category="test",
            schema=schema
        )
        def existing_prefix_tool():
            pass

        tool = get_tool_by_name("test_existing_tool")
        assert tool is not None
        assert tool.name == "test_existing_tool"

    def test_mcp_tool_with_returns_and_metadata(self):
        """测试带返回值定义和元数据的工具"""
        schema = {"type": "object"}
        returns = {
            "type": "object",
            "properties": {
                "result": {"type": "string"}
            }
        }
        metadata = {"tags": ["test", "example"], "version": "1.0"}

        @mcp_tool(
            name="full_tool",
            description="完整工具",
            category="test",
            schema=schema,
            returns=returns,
            metadata=metadata,
            enabled=False
        )
        def full_tool():
            pass

        tool = get_tool_by_name("test_full_tool")
        assert tool.returns == returns
        assert tool.metadata == metadata
        assert tool.enabled is False

    def test_tools_by_category(self):
        """测试按分类获取工具"""
        schema = {"type": "object"}

        @mcp_tool("tool1", "工具1", "cat1", schema)
        def tool1():
            pass

        @mcp_tool("tool2", "工具2", "cat1", schema)
        def tool2():
            pass

        @mcp_tool("tool3", "工具3", "cat2", schema)
        def tool3():
            pass

        cat1_tools = get_tools_by_category("cat1")
        assert len(cat1_tools) == 2
        tool_names = [tool.name for tool in cat1_tools]
        assert "cat1_tool1" in tool_names
        assert "cat1_tool2" in tool_names

        cat2_tools = get_tools_by_category("cat2")
        assert len(cat2_tools) == 1
        assert cat2_tools[0].name == "cat2_tool3"

        # 不存在的分类
        empty_tools = get_tools_by_category("nonexistent")
        assert len(empty_tools) == 0


class TestRegistryOperations:
    """测试注册表操作"""

    def setup_method(self):
        clear_registry()

    def test_clear_registry(self):
        """测试清空注册表"""
        schema = {"type": "object"}

        @mcp_category("test_cat", "测试", "描述")
        def test_cat():
            pass

        @mcp_tool("test_tool", "测试", "test_cat", schema)
        def test_tool():
            pass

        # 验证有数据
        assert len(get_registered_tools()) > 0
        assert len(get_registered_categories()) > 0

        # 清空注册表
        clear_registry()

        # 验证已清空
        assert len(get_registered_tools()) == 0
        assert len(get_registered_categories()) == 0
        assert get_tool_by_name("test_cat_test_tool") is None
        assert get_category_definition("test_cat") is None

    def test_get_tool_by_name_nonexistent(self):
        """测试获取不存在的工具"""
        tool = get_tool_by_name("nonexistent_tool")
        assert tool is None

    def test_registry_stats(self):
        """测试注册表统计信息"""
        schema = {"type": "object"}

        @mcp_category("cat1", "分类1", "描述1")
        def cat1():
            pass

        @mcp_category("cat2", "分类2", "描述2")
        def cat2():
            pass

        @mcp_tool("tool1", "工具1", "cat1", schema)
        def tool1():
            pass

        @mcp_tool("tool2", "工具2", "cat1", schema)
        def tool2():
            pass

        @mcp_tool("tool3", "工具3", "cat2", schema)
        def tool3():
            pass

        stats = get_registry_stats()
        assert stats["total_tools"] == 3
        assert stats["categories"] == 2
        assert stats["category_definitions"] == 2
        assert stats["tools_by_category"]["cat1"] == 2
        assert stats["tools_by_category"]["cat2"] == 1
        assert len(stats["registered_tools"]) == 3
        assert len(stats["registered_categories"]) == 2


class TestAutoDiscovery:
    """测试自动发现功能"""

    def setup_method(self):
        clear_registry()

    def test_scan_module_for_tools(self):
        """测试扫描模块中的工具"""
        # 创建一个模拟模块
        class MockModule:
            pass

        # 创建带工具装饰器的函数
        schema = {"type": "object"}

        @mcp_tool("scan_tool", "扫描工具", "test", schema)
        def decorated_tool():
            pass

        def normal_function():
            pass

        # 将函数添加到模块
        MockModule.decorated_tool = decorated_tool
        MockModule.normal_function = normal_function

        count = _scan_module_for_tools(MockModule)
        assert count == 1

    @patch('app.tools.registry.importlib.util.spec_from_file_location')
    @patch('app.tools.registry.importlib.util.module_from_spec')
    def test_auto_discover_tools_file_path(self, mock_module_from_spec, mock_spec_from_file):
        """测试从文件路径自动发现工具"""
        # 模拟模块加载
        mock_spec = MagicMock()
        mock_spec.loader = MagicMock()
        mock_spec_from_file.return_value = mock_spec

        mock_module = MagicMock()
        mock_module_from_spec.return_value = mock_module

        # 模拟模块中有一个装饰器函数
        def mock_tool():
            pass
        mock_tool._mcp_tool = MCPTool(
            name="mock_tool",
            description="Mock tool",
            category="test",
            schema={"type": "object"}
        )

        # 设置模拟模块的成员
        with patch('inspect.getmembers') as mock_getmembers:
            mock_getmembers.return_value = [
                ("mock_tool", mock_tool),
                ("other_func", lambda: None)
            ]

            count = auto_discover_tools(["/path/to/tools.py"])

        assert count == 1
        mock_spec_from_file.assert_called_once()

    @patch('app.tools.registry.importlib.import_module')
    def test_auto_discover_tools_module_name(self, mock_import_module):
        """测试从模块名自动发现工具"""
        mock_module = MagicMock()
        mock_import_module.return_value = mock_module

        def mock_tool():
            pass
        mock_tool._mcp_tool = MCPTool(
            name="mock_tool",
            description="Mock tool",
            category="test",
            schema={"type": "object"}
        )

        with patch('inspect.getmembers') as mock_getmembers:
            mock_getmembers.return_value = [("mock_tool", mock_tool)]

            count = auto_discover_tools(["test.module"])

        assert count == 1
        mock_import_module.assert_called_once_with("test.module")

    def test_auto_discover_tools_import_error(self):
        """测试模块导入错误处理"""
        with patch('app.tools.registry.logger') as mock_logger:
            count = auto_discover_tools(["nonexistent.module"])

        assert count == 0
        # 应该记录警告日志

    def test_scan_tools_directory(self):
        """测试扫描工具目录"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 创建测试工具文件
            tool_file = Path(temp_dir) / "test_tools.py"
            tool_file.write_text("""
from app.tools.registry import mcp_tool

@mcp_tool("scan_test", "扫描测试", "test", {"type": "object"})
def scan_test_tool():
    pass
""")

            with patch('app.tools.registry.auto_discover_tools') as mock_auto_discover:
                mock_auto_discover.return_value = 1
                count = scan_tools_directory(temp_dir)

            assert count == 1
            mock_auto_discover.assert_called_once()

    def test_scan_tools_directory_not_exists(self):
        """测试扫描不存在的目录"""
        with patch('app.tools.registry.logger') as mock_logger:
            count = scan_tools_directory("/nonexistent/directory")

        assert count == 0
        # 应该记录警告日志


class TestConvenienceDecorators:
    """测试便捷装饰器"""

    def setup_method(self):
        clear_registry()

    def test_github_tool_decorator(self):
        """测试GitHub工具装饰器"""
        schema = {"type": "object"}

        @github_tool("get_repo", "获取仓库", schema)
        def github_get_repo():
            pass

        tool = get_tool_by_name("github_get_repo")
        assert tool is not None
        assert tool.category == "github"

    def test_time_tool_decorator(self):
        """测试时间工具装饰器"""
        schema = {"type": "object"}

        @time_tool("get_time", "获取时间", schema)
        def time_get_time():
            pass

        tool = get_tool_by_name("time_get_time")
        assert tool is not None
        assert tool.category == "time"

    def test_file_tool_decorator(self):
        """测试文件工具装饰器"""
        schema = {"type": "object"}

        @file_tool("read_file", "读取文件", schema)
        def file_read_file():
            pass

        tool = get_tool_by_name("file_read_file")
        assert tool is not None
        assert tool.category == "file"

    def test_system_tool_decorator(self):
        """测试系统工具装饰器"""
        schema = {"type": "object"}

        @system_tool("get_info", "获取信息", schema)
        def system_get_info():
            pass

        tool = get_tool_by_name("system_get_info")
        assert tool is not None
        assert tool.category == "system"

    def test_cache_tool_decorator(self):
        """测试缓存工具装饰器"""
        schema = {"type": "object"}

        @cache_tool("get_cache", "获取缓存", schema)
        def cache_get_cache():
            pass

        tool = get_tool_by_name("cache_get_cache")
        assert tool is not None
        assert tool.category == "cache"

    def test_fetch_tool_decorator(self):
        """测试网络抓取工具装饰器"""
        schema = {"type": "object"}

        @fetch_tool("fetch_url", "抓取URL", schema)
        def fetch_fetch_url():
            pass

        tool = get_tool_by_name("web-scraping_fetch_url")
        assert tool is not None
        assert tool.category == "web-scraping"


class TestRegistryIntegration:
    """测试注册表集成功能"""

    def setup_method(self):
        clear_registry()

    def test_category_and_tools_integration(self):
        """测试分类和工具的集成"""
        # 注册分类
        @mcp_category("integration", "集成测试", "集成测试分类")
        def integration_category():
            pass

        # 注册工具
        schema = {"type": "object"}

        @mcp_tool("tool1", "工具1", "integration", schema)
        def tool1():
            pass

        @mcp_tool("tool2", "工具2", "integration", schema)
        def tool2():
            pass

        # 验证分类存在
        category = get_category_definition("integration")
        assert category is not None

        # 验证工具正确分类
        tools = get_tools_by_category("integration")
        assert len(tools) == 2

        # 验证统计信息
        stats = get_registry_stats()
        assert stats["total_tools"] == 2
        assert stats["categories"] == 1
        assert stats["tools_by_category"]["integration"] == 2

    def test_tool_metadata_preservation(self):
        """测试工具元数据保持"""
        schema = {"type": "object", "properties": {"param": {"type": "string"}}}
        returns = {"type": "string"}
        metadata = {"author": "test", "version": "1.0"}

        @mcp_tool(
            name="metadata_tool",
            description="元数据工具",
            category="test",
            schema=schema,
            returns=returns,
            metadata=metadata
        )
        def metadata_tool():
            return "result"

        tool = get_tool_by_name("test_metadata_tool")
        assert tool.schema == schema
        assert tool.returns == returns
        assert tool.metadata == metadata

        # 验证函数仍然可调用
        result = metadata_tool()
        assert result == "result"

    @patch('app.tools.registry.logger')
    def test_logging_integration(self, mock_logger):
        """测试日志集成"""
        schema = {"type": "object"}

        @mcp_category("log_test", "日志测试", "测试日志")
        def log_category():
            pass

        @mcp_tool("log_tool", "日志工具", "log_test", schema)
        def log_tool():
            pass

        # 验证记录了调试日志
        assert mock_logger.debug.called