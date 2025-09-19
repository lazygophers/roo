"""
数据库服务精简版全面测试
目标：将database_service_lite.py的测试覆盖率从0%提升到90%+
涵盖轻量级数据库服务、缓存系统、YAML解析等核心功能
"""
import pytest
import json
import yaml
import tempfile
import shutil
import hashlib
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock
from datetime import datetime
import time
import os

# 尝试导入模块
try:
    from app.core.database_service_lite import (
        LiteDatabaseService, get_lite_database_service,
        init_lite_database_service
    )
    LITE_DB_SERVICE_AVAILABLE = True
except ImportError as e:
    LITE_DB_SERVICE_AVAILABLE = False
    print(f"Database service lite import failed: {e}")


@pytest.mark.skipif(not LITE_DB_SERVICE_AVAILABLE, reason="Database service lite module not available")
class TestLiteDatabaseServiceComprehensive:
    """数据库服务精简版全面测试套件"""

    @pytest.fixture
    def temp_project_dir(self):
        """创建临时项目目录"""
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        # 创建项目结构
        (temp_path / "data").mkdir(exist_ok=True)
        (temp_path / "resources" / "models").mkdir(parents=True, exist_ok=True)
        (temp_path / "resources" / "hooks").mkdir(parents=True, exist_ok=True)

        yield temp_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_yaml_content(self):
        """示例YAML模型内容"""
        return {
            'slug': 'test-model',
            'name': 'Test Model',
            'roleDefinition': 'A test model for testing purposes' * 10,  # 长文本测试截断
            'whenToUse': 'Use when testing' * 5,  # 测试截断
            'description': 'Test description' * 5,  # 测试截断
            'groups': ['ai', 'test', 'dev', 'more', 'groups', 'extra'],  # 测试数组限制
            'extra_field': 'This should be ignored'
        }

    @pytest.fixture
    def mock_unified_db(self):
        """模拟统一数据库"""
        mock_db = Mock()
        mock_unified_db = Mock()
        mock_unified_db.db = mock_db
        mock_unified_db.db_path = "/tmp/unified.db"

        # 模拟table方法
        mock_table = Mock()
        mock_table.all.return_value = []
        mock_table.search.return_value = []
        mock_table.insert.return_value = None
        mock_table.update.return_value = None
        mock_db.table.return_value = mock_table

        return mock_unified_db

    @pytest.fixture
    def mock_tinydb(self):
        """模拟TinyDB"""
        mock_db = Mock()
        mock_table = Mock()
        mock_table.all.return_value = []
        mock_table.search.return_value = []
        mock_table.insert.return_value = None
        mock_table.update.return_value = None
        mock_db.table.return_value = mock_table
        mock_db.close.return_value = None
        return mock_db

    # ==== 初始化测试 ====

    def test_lite_database_service_init_unified_db(self, mock_unified_db):
        """测试使用统一数据库初始化"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService(use_unified_db=True)

            assert service.use_unified_db is True
            assert service.unified_db == mock_unified_db
            assert service.db == mock_unified_db.db
            assert service.db_path == mock_unified_db.db_path
            assert isinstance(service._memory_cache, dict)
            assert isinstance(service._cache_timestamps, dict)
            assert service._cache_ttl == 300

    def test_lite_database_service_init_independent_db(self, temp_project_dir, mock_tinydb):
        """测试使用独立数据库初始化"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.TinyDB', return_value=mock_tinydb):
                service = LiteDatabaseService(use_unified_db=False)

                assert service.use_unified_db is False
                assert service.unified_db is None
                assert service.db == mock_tinydb
                assert str(temp_project_dir / "data" / "lite_cache.db") in service.db_path

    # ==== 缓存功能测试 ====

    def test_memory_cache_operations(self, mock_unified_db):
        """测试内存缓存操作"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 测试设置缓存
            test_data = {"test": "data"}
            service._set_cache("test_key", test_data)

            assert "test_key" in service._memory_cache
            assert "test_key" in service._cache_timestamps
            assert service._memory_cache["test_key"] == test_data

            # 测试获取缓存
            result = service._get_cache("test_key")
            assert result == test_data

            # 测试缓存有效性检查
            assert service._is_cache_valid("test_key") is True
            assert service._is_cache_valid("nonexistent_key") is False

    def test_cache_ttl_expiration(self, mock_unified_db):
        """测试缓存TTL过期"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()
            service._cache_ttl = 0.1  # 0.1秒TTL

            # 设置缓存
            service._set_cache("test_key", "test_data")
            assert service._is_cache_valid("test_key") is True

            # 等待过期
            time.sleep(0.2)
            assert service._is_cache_valid("test_key") is False

            # 过期后获取缓存返回None
            result = service._get_cache("test_key")
            assert result is None

    def test_cache_size_limit(self, mock_unified_db):
        """测试缓存大小限制"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 添加101个缓存项（超过100的限制）
            for i in range(101):
                service._set_cache(f"key_{i}", f"data_{i}")

            # 验证最老的缓存被清除
            assert len(service._memory_cache) <= 100
            assert "key_0" not in service._memory_cache  # 最老的应该被清除

    # ==== 文件操作测试 ====

    def test_get_file_hash(self, temp_project_dir, mock_unified_db):
        """测试文件哈希计算"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 创建测试文件
            test_file = temp_project_dir / "test.txt"
            test_content = "test content" * 100  # 超过1KB的内容
            with open(test_file, 'w') as f:
                f.write(test_content)

            # 计算哈希
            file_hash = service._get_file_hash(test_file)

            # 验证哈希长度为16（截断后）
            assert len(file_hash) == 16
            assert isinstance(file_hash, str)

            # 测试不存在的文件
            nonexistent_file = temp_project_dir / "nonexistent.txt"
            empty_hash = service._get_file_hash(nonexistent_file)
            assert empty_hash == ""

    def test_parse_yaml_file_success(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试YAML文件解析成功"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 创建YAML文件
            yaml_file = temp_project_dir / "test.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(sample_yaml_content, f)

            file_stats = yaml_file.stat()

            # 解析文件
            result = service._parse_yaml_file(str(yaml_file), file_stats.st_mtime)

            # 验证核心字段被提取
            assert result['slug'] == 'test-model'
            assert result['name'] == 'Test Model'
            assert len(result['roleDefinition']) <= 200  # 测试截断
            assert len(result['whenToUse']) <= 100
            assert len(result['description']) <= 100
            assert len(result['groups']) <= 5  # 测试数组限制
            assert 'extra_field' not in result  # 不包含的字段被过滤

    def test_parse_yaml_file_invalid(self, temp_project_dir, mock_unified_db):
        """测试解析无效YAML文件"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 创建无效YAML文件
            yaml_file = temp_project_dir / "invalid.yaml"
            with open(yaml_file, 'w') as f:
                f.write("invalid: yaml: content:")

            file_stats = yaml_file.stat()

            # 解析文件应该返回空字典
            result = service._parse_yaml_file(str(yaml_file), file_stats.st_mtime)
            assert result == {}

    def test_parse_yaml_file_nonexistent(self, mock_unified_db):
        """测试解析不存在的YAML文件"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 解析不存在的文件
            result = service._parse_yaml_file("/nonexistent/file.yaml", 0)
            assert result == {}

    # ==== 模型数据操作测试 ====

    def test_get_models_data_no_directory(self, temp_project_dir, mock_unified_db):
        """测试获取模型数据 - 无模型目录"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 删除模型目录
                models_dir = temp_project_dir / "resources" / "models"
                shutil.rmtree(models_dir, ignore_errors=True)

                result = service.get_models_data()
                assert result == []

    def test_get_models_data_with_models(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试获取模型数据 - 有模型文件"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建模型文件
                models_dir = temp_project_dir / "resources" / "models"
                model_file = models_dir / "test-model.yaml"
                with open(model_file, 'w') as f:
                    yaml.dump(sample_yaml_content, f)

                # 创建第二个模型文件（用于测试排序）
                sample_yaml_content2 = sample_yaml_content.copy()
                sample_yaml_content2['slug'] = 'another-model'
                model_file2 = models_dir / "another-model.yaml"
                with open(model_file2, 'w') as f:
                    yaml.dump(sample_yaml_content2, f)

                result = service.get_models_data()

                # 验证结果
                assert len(result) == 2
                assert result[0]['slug'] == 'another-model'  # 按slug排序
                assert result[1]['slug'] == 'test-model'

                # 验证文件信息被添加
                assert 'file_path' in result[0]
                assert 'file_size' in result[0]
                assert 'last_modified' in result[0]

    def test_get_models_data_cached(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试获取模型数据 - 缓存机制"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 第一次调用
                result1 = service.get_models_data()

                # 第二次调用应该从缓存获取
                with patch.object(service, '_parse_yaml_file') as mock_parse:
                    result2 = service.get_models_data()
                    # 没有调用解析方法，说明使用了缓存
                    mock_parse.assert_not_called()
                    assert result1 == result2

    def test_get_models_data_force_refresh(self, temp_project_dir, mock_unified_db):
        """测试强制刷新模型数据"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 设置缓存
                service._set_cache("all_models", [{"cached": "data"}])

                # 强制刷新
                result = service.get_models_data(force_refresh=True)

                # 应该忽略缓存，重新加载
                assert result != [{"cached": "data"}]

    def test_get_model_by_slug_found(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试根据slug获取模型 - 找到"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建模型文件
                models_dir = temp_project_dir / "resources" / "models"
                model_file = models_dir / "test-model.yaml"
                with open(model_file, 'w') as f:
                    yaml.dump(sample_yaml_content, f)

                result = service.get_model_by_slug('test-model')

                assert result is not None
                assert result['slug'] == 'test-model'
                assert result['name'] == 'Test Model'

    def test_get_model_by_slug_not_found(self, temp_project_dir, mock_unified_db):
        """测试根据slug获取模型 - 未找到"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                result = service.get_model_by_slug('nonexistent-model')
                assert result is None

    def test_get_model_by_slug_cached(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试根据slug获取模型 - 缓存"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 设置模型缓存
                test_model = {"slug": "test-model", "name": "Test Model"}
                service._set_cache("model_test-model", test_model)

                result = service.get_model_by_slug('test-model')
                assert result == test_model

    def test_get_models_by_group(self, temp_project_dir, sample_yaml_content, mock_unified_db):
        """测试根据组获取模型"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建模型文件
                models_dir = temp_project_dir / "resources" / "models"
                model_file = models_dir / "test-model.yaml"
                with open(model_file, 'w') as f:
                    yaml.dump(sample_yaml_content, f)

                result = service.get_models_by_group('ai')

                assert len(result) == 1
                assert result[0]['slug'] == 'test-model'
                assert 'ai' in result[0]['groups']

    def test_get_models_by_group_cached(self, mock_unified_db):
        """测试根据组获取模型 - 缓存"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 设置组缓存
            test_models = [{"slug": "test-model", "groups": ["ai"]}]
            service._set_cache("group_ai", test_models)

            result = service.get_models_by_group('ai')
            assert result == test_models

    def test_get_models_by_group_no_match(self, temp_project_dir, mock_unified_db):
        """测试根据组获取模型 - 无匹配"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                result = service.get_models_by_group('nonexistent-group')
                assert result == []

    # ==== 缓存刷新测试 ====

    def test_refresh_models_cache(self, mock_unified_db):
        """测试刷新模型缓存"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 设置一些缓存
            service._set_cache("all_models", [])
            service._set_cache("model_test", {})
            service._set_cache("group_ai", [])
            service._set_cache("other_cache", {})

            # 刷新缓存
            with patch.object(service, 'get_models_data', return_value=[{"test": "model"}]) as mock_get:
                result = service.refresh_models_cache()

                # 验证相关缓存被清除
                assert "all_models" not in service._memory_cache
                assert "model_test" not in service._memory_cache
                assert "group_ai" not in service._memory_cache
                assert "other_cache" in service._memory_cache  # 无关缓存保留

                # 验证返回结果
                assert result['total_models'] == 1
                assert result['cache_cleared'] == 3

                # 验证get_models_data被调用
                mock_get.assert_called_once_with(force_refresh=True)

    # ==== Hooks数据测试 ====

    def test_get_hooks_data_no_directory(self, temp_project_dir, mock_unified_db):
        """测试获取hooks数据 - 无hooks目录"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 删除hooks目录
                hooks_dir = temp_project_dir / "resources" / "hooks"
                shutil.rmtree(hooks_dir, ignore_errors=True)

                result = service.get_hooks_data()
                assert result == {}

    def test_get_hooks_data_with_hooks(self, temp_project_dir, mock_unified_db):
        """测试获取hooks数据 - 有hooks文件"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建hooks文件
                hooks_dir = temp_project_dir / "resources" / "hooks"
                hook_file = hooks_dir / "test-hook.md"
                hook_content = "# Test Hook\n" + "Content " * 200  # 长内容测试截断
                with open(hook_file, 'w') as f:
                    f.write(hook_content)

                result = service.get_hooks_data()

                assert "test-hook" in result
                assert len(result["test-hook"]) <= 1000  # 测试内容截断

    def test_get_hooks_data_cached(self, temp_project_dir, mock_unified_db):
        """测试获取hooks数据 - 缓存"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 设置缓存
            cached_hooks = {"cached": "hook"}
            service._set_cache("hooks_data", cached_hooks)

            result = service.get_hooks_data()
            assert result == cached_hooks

    def test_get_hooks_data_file_error(self, temp_project_dir, mock_unified_db):
        """测试获取hooks数据 - 文件读取错误"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建hooks文件但无读取权限
                hooks_dir = temp_project_dir / "resources" / "hooks"
                hook_file = hooks_dir / "error-hook.md"
                with open(hook_file, 'w') as f:
                    f.write("test content")

                # 模拟读取错误
                with patch('builtins.open', mock_open()) as mock_file:
                    mock_file.side_effect = PermissionError("Access denied")

                    result = service.get_hooks_data()
                    # 错误的文件应该被跳过
                    assert result == {}

    # ==== 状态和管理功能测试 ====

    def test_get_status(self, mock_unified_db):
        """测试获取服务状态"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 添加一些缓存和数据
            service._set_cache("test", "data")

            result = service.get_status()

            assert result['service_type'] == 'LiteDatabaseService'
            assert result['db_path'] == mock_unified_db.db_path
            assert result['memory_cache_size'] == 1
            assert 'lru_cache_hits' in result
            assert 'lru_cache_misses' in result
            assert 'lru_cache_size' in result
            assert result['uptime'] == 'running'

    def test_clear_all_cache(self, mock_unified_db):
        """测试清除所有缓存"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 添加缓存数据
            service._set_cache("test1", "data1")
            service._set_cache("test2", "data2")

            # 添加LRU缓存数据
            service._parse_yaml_file("test", 123)

            # 清除缓存
            service.clear_all_cache()

            # 验证缓存被清除
            assert len(service._memory_cache) == 0
            assert len(service._cache_timestamps) == 0

            # 验证LRU缓存被清除
            cache_info = service._parse_yaml_file.cache_info()
            assert cache_info.currsize == 0

    def test_close_unified_db(self, mock_unified_db):
        """测试关闭服务 - 统一数据库模式"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService(use_unified_db=True)

            # 添加一些缓存
            service._set_cache("test", "data")

            service.close()

            # 验证缓存被清除
            assert len(service._memory_cache) == 0
            # 统一数据库模式下不应该调用db.close()
            mock_unified_db.db.close.assert_not_called()

    def test_close_independent_db(self, temp_project_dir, mock_tinydb):
        """测试关闭服务 - 独立数据库模式"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.TinyDB', return_value=mock_tinydb):
                service = LiteDatabaseService(use_unified_db=False)

                # 添加一些缓存
                service._set_cache("test", "data")

                service.close()

                # 验证缓存被清除
                assert len(service._memory_cache) == 0
                # 独立数据库模式下应该调用db.close()
                mock_tinydb.close.assert_called_once()

    # ==== 全局函数测试 ====

    def test_get_lite_database_service_singleton(self, mock_unified_db):
        """测试获取轻量级数据库服务单例"""
        import app.core.database_service_lite as lite_module

        # 重置全局变量
        original_service = lite_module._lite_db_service
        lite_module._lite_db_service = None

        try:
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                # 第一次调用
                service1 = lite_module.get_lite_database_service()

                # 第二次调用应该返回同一实例
                service2 = lite_module.get_lite_database_service()

                assert service1 is service2
                assert isinstance(service1, LiteDatabaseService)
        finally:
            lite_module._lite_db_service = original_service

    def test_init_lite_database_service(self, mock_unified_db):
        """测试初始化轻量级数据库服务"""
        import app.core.database_service_lite as lite_module

        # 重置全局变量
        original_service = lite_module._lite_db_service
        lite_module._lite_db_service = None

        try:
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = lite_module.init_lite_database_service(use_unified_db=True)

                assert isinstance(service, LiteDatabaseService)
                assert service.use_unified_db is True
        finally:
            lite_module._lite_db_service = original_service

    def test_init_lite_database_service_independent(self, temp_project_dir, mock_tinydb):
        """测试初始化轻量级数据库服务 - 独立模式"""
        import app.core.database_service_lite as lite_module

        # 重置全局变量
        original_service = lite_module._lite_db_service
        lite_module._lite_db_service = None

        try:
            with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
                with patch('app.core.database_service_lite.TinyDB', return_value=mock_tinydb):
                    service = lite_module.init_lite_database_service(use_unified_db=False)

                    assert isinstance(service, LiteDatabaseService)
                    assert service.use_unified_db is False
        finally:
            lite_module._lite_db_service = original_service

    # ==== 边界条件和错误处理测试 ====

    def test_yaml_parsing_with_non_dict_data(self, temp_project_dir, mock_unified_db):
        """测试YAML解析 - 非字典数据"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 创建包含列表的YAML文件
            yaml_file = temp_project_dir / "list.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump(['item1', 'item2', 'item3'], f)

            file_stats = yaml_file.stat()
            result = service._parse_yaml_file(str(yaml_file), file_stats.st_mtime)

            # 非字典数据应该返回空字典
            assert result == {}

    def test_models_data_with_invalid_yaml(self, temp_project_dir, mock_unified_db):
        """测试获取模型数据 - 包含无效YAML文件"""
        with patch('app.core.database_service_lite.PROJECT_ROOT', temp_project_dir):
            with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
                service = LiteDatabaseService()

                # 创建有效和无效的YAML文件
                models_dir = temp_project_dir / "resources" / "models"

                # 有效文件
                valid_file = models_dir / "valid.yaml"
                with open(valid_file, 'w') as f:
                    yaml.dump({'slug': 'valid-model', 'name': 'Valid Model'}, f)

                # 无效文件
                invalid_file = models_dir / "invalid.yaml"
                with open(invalid_file, 'w') as f:
                    f.write("invalid: yaml: content:")

                # 无slug的文件
                no_slug_file = models_dir / "no-slug.yaml"
                with open(no_slug_file, 'w') as f:
                    yaml.dump({'name': 'No Slug Model'}, f)

                result = service.get_models_data()

                # 只有有效的文件应该被包含
                assert len(result) == 1
                assert result[0]['slug'] == 'valid-model'

    def test_lru_cache_functionality(self, temp_project_dir, mock_unified_db):
        """测试LRU缓存功能"""
        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            # 创建测试文件
            yaml_file = temp_project_dir / "test.yaml"
            with open(yaml_file, 'w') as f:
                yaml.dump({'slug': 'test', 'name': 'Test'}, f)

            file_stats = yaml_file.stat()

            # 第一次调用
            result1 = service._parse_yaml_file(str(yaml_file), file_stats.st_mtime)
            cache_info1 = service._parse_yaml_file.cache_info()

            # 第二次调用相同参数
            result2 = service._parse_yaml_file(str(yaml_file), file_stats.st_mtime)
            cache_info2 = service._parse_yaml_file.cache_info()

            # 验证结果相同
            assert result1 == result2
            # 验证缓存命中增加
            assert cache_info2.hits > cache_info1.hits

    def test_concurrent_cache_operations(self, mock_unified_db):
        """测试并发缓存操作"""
        import threading
        import time

        with patch('app.core.database_service_lite.get_unified_database', return_value=mock_unified_db):
            service = LiteDatabaseService()

            results = []
            errors = []

            def cache_worker(worker_id):
                try:
                    for i in range(10):
                        key = f"worker_{worker_id}_item_{i}"
                        data = f"data_{worker_id}_{i}"

                        # 设置缓存
                        service._set_cache(key, data)

                        # 获取缓存
                        result = service._get_cache(key)
                        if result == data:
                            results.append((worker_id, i, "success"))
                        else:
                            results.append((worker_id, i, "fail"))

                        time.sleep(0.001)  # 短暂休眠
                except Exception as e:
                    errors.append((worker_id, str(e)))

            # 创建多个线程
            threads = []
            for worker_id in range(3):
                thread = threading.Thread(target=cache_worker, args=(worker_id,))
                threads.append(thread)
                thread.start()

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            # 验证结果
            assert len(errors) == 0
            assert len(results) == 30  # 3个工作线程 × 10次操作
            assert all(result[2] == "success" for result in results)