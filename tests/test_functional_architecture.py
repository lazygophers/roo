"""
函数式架构测试

测试重构后的函数式架构是否正常工作
"""

import pytest
import asyncio
from pathlib import Path
import tempfile
import json

from app.core.functional_base import Result, pipe, compose, safe, memoize
from app.core.database_functional import (
    create_database_service, create_scan_config,
    process_file, batch_process_files
)
from app.core.config_functional import (
    create_mcp_config_manager, get_config_from_manager,
    update_config_in_manager
)
from app.core.tools_functional import (
    create_tool_registry, register_tool, ToolDefinition,
    execute_tool, get_all_tools
)
from app.tools.functional_tools import (
    get_current_time, hash_text, parse_json, stringify_json
)

# =============================================================================
# 函数式基础工具测试
# =============================================================================

class TestFunctionalBase:
    """测试函数式基础工具"""

    def test_result_success(self):
        """测试Result成功情况"""
        result = Result(value="test")
        assert result.is_success
        assert not result.is_error
        assert result.value == "test"
        assert result.unwrap() == "test"

    def test_result_error(self):
        """测试Result错误情况"""
        error = ValueError("test error")
        result = Result(error=error)
        assert not result.is_success
        assert result.is_error
        assert result.error == error

        with pytest.raises(ValueError):
            result.unwrap()

    def test_result_map(self):
        """测试Result映射"""
        result = Result(value=5)
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_success
        assert mapped.value == 10

    def test_result_map_error(self):
        """测试Result映射错误"""
        result = Result(error=ValueError("test"))
        mapped = result.map(lambda x: x * 2)
        assert mapped.is_error

    def test_pipe(self):
        """测试管道函数"""
        add_one = lambda x: x + 1
        multiply_two = lambda x: x * 2

        pipeline = pipe(add_one, multiply_two)
        result = pipeline(5)
        assert result == 12  # (5 + 1) * 2

    def test_compose(self):
        """测试组合函数"""
        add_one = lambda x: x + 1
        multiply_two = lambda x: x * 2

        composition = compose(multiply_two, add_one)
        result = composition(5)
        assert result == 12  # (5 + 1) * 2

    def test_safe_wrapper(self):
        """测试安全包装器"""
        def divide(a, b):
            return a / b

        safe_divide = safe(divide)

        # 成功情况
        result = safe_divide(10, 2)
        assert result.is_success
        assert result.value == 5.0

        # 错误情况
        result = safe_divide(10, 0)
        assert result.is_error
        assert isinstance(result.error, ZeroDivisionError)

    def test_memoize(self):
        """测试记忆化装饰器"""
        call_count = 0

        @memoize
        def expensive_func(x):
            nonlocal call_count
            call_count += 1
            return x * x

        # 第一次调用
        result1 = expensive_func(5)
        assert result1 == 25
        assert call_count == 1

        # 第二次调用（应该使用缓存）
        result2 = expensive_func(5)
        assert result2 == 25
        assert call_count == 1  # 没有增加

        # 不同参数的调用
        result3 = expensive_func(10)
        assert result3 == 100
        assert call_count == 2

# =============================================================================
# 数据库功能测试
# =============================================================================

class TestDatabaseFunctional:
    """测试函数式数据库功能"""

    def test_create_database_service(self):
        """测试创建数据库服务"""
        service = create_database_service(use_unified=False)
        assert 'db' in service
        assert 'scan_configs' in service
        assert 'observers' in service
        assert 'logger' in service

    def test_scan_config_creation(self):
        """测试扫描配置创建"""
        config = create_scan_config(
            name="test_scan",
            path="/tmp",
            patterns=["*.txt", "*.yaml"],
            watch=True
        )

        assert config['name'] == "test_scan"
        assert config['path'] == Path("/tmp")
        assert config['patterns'] == ["*.txt", "*.yaml"]
        assert config['watch'] is True
        assert 'created_at' in config

    def test_process_file_yaml(self):
        """测试YAML文件处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = """
name: test
value: 123
items:
  - a
  - b
"""
            f.write(yaml_content)
            f.flush()

            result = process_file(Path(f.name))
            assert result.is_success

            file_info = result.value
            assert file_info['name'] == Path(f.name).name
            assert file_info['data']['name'] == 'test'
            assert file_info['data']['value'] == 123
            assert file_info['parse_error'] is None

        # 清理
        Path(f.name).unlink()

    def test_process_file_invalid(self):
        """测试无效文件处理"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            # 无效的YAML
            f.write("invalid: yaml: content: [")
            f.flush()

            result = process_file(Path(f.name))
            assert result.is_success

            file_info = result.value
            assert file_info['data'] is None
            assert file_info['parse_error'] is not None

        # 清理
        Path(f.name).unlink()

# =============================================================================
# 配置管理测试
# =============================================================================

class TestConfigFunctional:
    """测试函数式配置管理"""

    def test_mcp_config_manager(self):
        """测试MCP配置管理器"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_mcp_config.json"

            manager = create_mcp_config_manager(str(config_file))

            # 获取默认配置
            result = get_config_from_manager(manager)
            assert result.is_success

            config = result.value
            assert isinstance(config, dict)
            assert 'environment' in config

    def test_config_update(self):
        """测试配置更新"""
        with tempfile.TemporaryDirectory() as temp_dir:
            config_file = Path(temp_dir) / "test_config.json"

            manager = create_mcp_config_manager(str(config_file))

            # 更新配置
            updates = {'debug': True, 'custom_setting': 'test_value'}
            result = update_config_in_manager(manager, updates)
            assert result.is_success

            # 验证更新
            result = get_config_from_manager(manager)
            assert result.is_success
            assert result.value['debug'] is True
            assert result.value['custom_setting'] == 'test_value'

# =============================================================================
# 工具系统测试
# =============================================================================

class TestToolsFunctional:
    """测试函数式工具系统"""

    def test_tool_registry_creation(self):
        """测试工具注册表创建"""
        registry = create_tool_registry()
        assert 'tools' in registry
        assert 'categories' in registry
        assert 'logger' in registry

    def test_tool_registration(self):
        """测试工具注册"""
        registry = create_tool_registry()

        def test_tool(x: int) -> int:
            return x * 2

        tool_def = ToolDefinition(
            name="test_tool",
            description="Test tool",
            func=test_tool,
            category="test"
        )

        result = register_tool(registry, tool_def)
        assert result.is_success
        assert "test_tool" in registry['tools']

    def test_tool_execution(self):
        """测试工具执行"""
        registry = create_tool_registry()

        def multiply(x: int, y: int) -> int:
            return x * y

        tool_def = ToolDefinition(
            name="multiply",
            description="Multiply two numbers",
            func=multiply,
            category="math"
        )

        register_tool(registry, tool_def)

        result = execute_tool(registry, "multiply", [5, 3])
        assert result.is_success
        assert result.value == 15

    def test_builtin_tools(self):
        """测试内置工具"""
        # 测试时间工具
        time_result = get_current_time()
        assert isinstance(time_result, str)
        assert 'T' in time_result  # ISO格式包含T

        # 测试哈希工具
        hash_result = hash_text("hello")
        assert isinstance(hash_result, str)
        assert len(hash_result) == 32  # MD5长度

        # 测试JSON解析
        json_result = parse_json('{"key": "value"}')
        assert json_result.is_success
        assert json_result.value == {"key": "value"}

        # 测试JSON字符串化
        stringify_result = stringify_json({"key": "value"})
        assert stringify_result.is_success
        assert '"key"' in stringify_result.value

# =============================================================================
# 异步工具测试
# =============================================================================

class TestAsyncFunctional:
    """测试异步函数功能"""

    @pytest.mark.asyncio
    async def test_async_file_operations(self):
        """测试异步文件操作"""
        from app.tools.functional_tools import write_file, read_file

        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "test.txt"
            test_content = "Hello, functional world!"

            # 写入文件
            write_result = await write_file(str(test_file), test_content)
            assert write_result.is_success
            assert write_result.value is True

            # 读取文件
            read_result = await read_file(str(test_file))
            assert read_result.is_success
            assert read_result.value == test_content

# =============================================================================
# 集成测试
# =============================================================================

class TestIntegration:
    """集成测试"""

    def test_functional_pipeline(self):
        """测试函数式管道"""
        # 创建一个数据处理管道
        def extract_data(file_info):
            return file_info.get('data', {})

        def transform_data(data):
            if isinstance(data, dict) and 'name' in data:
                return {'processed_name': data['name'].upper()}
            return data

        def validate_data(data):
            if isinstance(data, dict) and 'processed_name' in data:
                return Result(value=data)
            return Result(error=ValueError("Invalid data"))

        pipeline = pipe(extract_data, transform_data, validate_data)

        # 测试数据
        test_file_info = {
            'path': '/test/file.yaml',
            'data': {'name': 'test_item'}
        }

        result = pipeline(test_file_info)
        assert result.is_success
        assert result.value['processed_name'] == 'TEST_ITEM'

    def test_error_handling_pipeline(self):
        """测试错误处理管道"""
        def step1(x):
            if x < 0:
                raise ValueError("Negative value")
            return x * 2

        def step2(x):
            return x + 10

        safe_step1 = safe(step1)
        pipeline = lambda x: safe_step1(x).map(step2)

        # 正常情况
        result = pipeline(5)
        assert result.is_success
        assert result.value == 20

        # 错误情况
        result = pipeline(-1)
        assert result.is_error
        assert isinstance(result.error, ValueError)

# =============================================================================
# 性能测试
# =============================================================================

class TestPerformance:
    """性能测试"""

    def test_memoization_performance(self):
        """测试记忆化性能"""
        import time

        @memoize
        def slow_function(n):
            time.sleep(0.01)  # 模拟慢操作
            return n * n

        # 第一次调用 - 慢
        start = time.time()
        result1 = slow_function(5)
        first_duration = time.time() - start

        # 第二次调用 - 快（缓存）
        start = time.time()
        result2 = slow_function(5)
        second_duration = time.time() - start

        assert result1 == result2 == 25
        assert second_duration < first_duration / 2  # 应该快很多

    def test_batch_processing(self):
        """测试批量处理性能"""
        # 创建测试文件
        test_files = []
        with tempfile.TemporaryDirectory() as temp_dir:
            for i in range(5):
                test_file = Path(temp_dir) / f"test_{i}.yaml"
                test_file.write_text(f"name: test_{i}\nvalue: {i}")
                test_files.append(test_file)

            # 批量处理
            result = batch_process_files(test_files)

            assert result['success_count'] == 5
            assert result['error_count'] == 0
            assert len(result['results']) == 5

if __name__ == "__main__":
    pytest.main([__file__, "-v"])