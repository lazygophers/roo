"""
数据库服务专项深度测试
目标：将database_service.py的测试覆盖率从15%提升到85%+
涵盖文件扫描、监听、缓存、数据库操作的全面测试
"""
import pytest
import os
import tempfile
import shutil
import time
import threading
import yaml
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, mock_open
from datetime import datetime

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.core.database_service import (
        DatabaseService, get_database_service, init_database_service
    )
    from app.core.unified_database import TableNames
    DATABASE_SERVICE_AVAILABLE = True
except ImportError as e:
    DATABASE_SERVICE_AVAILABLE = False
    print(f"Database service import failed: {e}")


@pytest.mark.skipif(not DATABASE_SERVICE_AVAILABLE, reason="Database service module not available")
class TestDatabaseServiceMegaCoverage:
    """数据库服务深度测试套件"""

    @pytest.fixture
    def temp_project_root(self):
        """创建临时项目根目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def mock_unified_db(self):
        """模拟统一数据库"""
        mock_db = Mock()
        mock_unified_db = Mock()
        mock_unified_db.db = mock_db

        mock_table = Mock()
        mock_table.all.return_value = []
        mock_table.search.return_value = []
        mock_table.insert.return_value = None
        mock_table.update.return_value = None
        mock_table.remove.return_value = None
        mock_table.upsert.return_value = None

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
        mock_table.remove.return_value = None
        mock_table.upsert.return_value = None

        mock_db.table.return_value = mock_table
        mock_db.close.return_value = None

        return mock_db

    @pytest.fixture
    def sample_yaml_files(self, temp_project_root):
        """创建示例YAML文件"""
        models_dir = temp_project_root / "resources" / "models"
        models_dir.mkdir(parents=True)

        # 创建模型文件
        model1_content = {
            "name": "test-model-1",
            "version": "1.0.0",
            "description": "Test model 1"
        }
        model1_path = models_dir / "model1.yaml"
        with open(model1_path, 'w') as f:
            yaml.dump(model1_content, f)

        model2_content = {
            "name": "test-model-2",
            "version": "2.0.0",
            "description": "Test model 2"
        }
        model2_path = models_dir / "model2.yml"
        with open(model2_path, 'w') as f:
            yaml.dump(model2_content, f)

        hooks_dir = temp_project_root / "resources" / "hooks"
        hooks_dir.mkdir(parents=True)

        # 创建hooks文件
        hook_content = "# Test hook\nThis is a test hook file"
        hook_path = hooks_dir / "test_hook.md"
        with open(hook_path, 'w') as f:
            f.write(hook_content)

        return {
            'models_dir': models_dir,
            'hooks_dir': hooks_dir,
            'model1': model1_path,
            'model2': model2_path,
            'hook': hook_path
        }

    # ==== DatabaseService 初始化测试 ====

    def test_database_service_init_unified_db(self, mock_unified_db):
        """测试使用统一数据库初始化"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService(use_unified_db=True)

            assert service.use_unified_db is True
            assert service.unified_db == mock_unified_db
            assert service.db == mock_unified_db.db
            assert service.file_monitor is None
            assert service.observer is None
            assert service._scan_configs == {}
            assert service._running is False

    def test_database_service_init_standalone_db(self, mock_tinydb, temp_project_root):
        """测试使用独立数据库初始化"""
        with patch('app.core.database_service.PROJECT_ROOT', temp_project_root), \
             patch('app.core.database_service.TinyDB', return_value=mock_tinydb):

            service = DatabaseService(use_unified_db=False)

            assert service.use_unified_db is False
            assert service.unified_db is None
            assert service.db == mock_tinydb

            # 验证数据库目录被创建
            db_dir = temp_project_root / "data"
            assert db_dir.exists()

    # ==== 扫描配置管理测试 ====

    def test_add_scan_config_basic(self, mock_unified_db):
        """测试添加基本扫描配置"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            service.add_scan_config(
                name="test_config",
                path="/test/path",
                patterns=["*.yaml"],
                watch=True
            )

            assert "test_config" in service._scan_configs
            config = service._scan_configs["test_config"]
            assert config['path'] == Path("/test/path")
            assert config['patterns'] == ["*.yaml"]
            assert config['watch'] is True
            assert config['table_name'] == "test_config_cache"

    def test_add_scan_config_predefined_names(self, mock_unified_db):
        """测试添加预定义名称的扫描配置"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            # 测试models配置
            service.add_scan_config(name="models", path="/models/path")
            assert service._scan_configs["models"]['table_name'] == TableNames.MODELS_CACHE

            # 测试hooks配置
            service.add_scan_config(name="hooks", path="/hooks/path")
            assert service._scan_configs["hooks"]['table_name'] == TableNames.HOOKS_CACHE

            # 测试rules配置
            service.add_scan_config(name="rules", path="/rules/path")
            assert service._scan_configs["rules"]['table_name'] == TableNames.RULES_CACHE

    def test_add_scan_config_default_patterns(self, mock_unified_db):
        """测试默认文件匹配模式"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            service.add_scan_config(name="test", path="/test", patterns=None)

            config = service._scan_configs["test"]
            assert config['patterns'] == ['*.yaml', '*.yml']

    def test_add_scan_config_custom_parser(self, mock_unified_db):
        """测试自定义解析器"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            def custom_parser(file_path):
                return {"custom": "data"}

            service.add_scan_config(
                name="test",
                path="/test",
                parser_func=custom_parser
            )

            config = service._scan_configs["test"]
            assert config['parser_func'] == custom_parser

    # ==== 文件解析和哈希测试 ====

    def test_default_yaml_parser_success(self, mock_unified_db, temp_project_root):
        """测试YAML文件解析成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            yaml_file = temp_project_root / "test.yaml"
            test_data = {"key": "value", "number": 42}

            with open(yaml_file, 'w') as f:
                yaml.dump(test_data, f)

            result = service._default_yaml_parser(yaml_file)
            assert result == test_data

    def test_default_yaml_parser_empty_file(self, mock_unified_db, temp_project_root):
        """测试解析空YAML文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            yaml_file = temp_project_root / "empty.yaml"
            yaml_file.touch()

            result = service._default_yaml_parser(yaml_file)
            assert result == {}

    def test_default_yaml_parser_invalid_file(self, mock_unified_db, temp_project_root):
        """测试解析无效YAML文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            yaml_file = temp_project_root / "invalid.yaml"
            with open(yaml_file, 'w') as f:
                f.write("invalid: yaml: content: [")

            result = service._default_yaml_parser(yaml_file)
            assert result == {}

    def test_default_yaml_parser_nonexistent_file(self, mock_unified_db):
        """测试解析不存在的文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            result = service._default_yaml_parser(Path("/nonexistent/file.yaml"))
            assert result == {}

    def test_get_file_hash_success(self, mock_unified_db, temp_project_root):
        """测试文件哈希计算成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            test_file = temp_project_root / "test.txt"
            test_content = "test content"
            with open(test_file, 'w') as f:
                f.write(test_content)

            hash_result = service._get_file_hash(test_file)
            assert len(hash_result) == 32  # MD5 hash length
            assert hash_result != ""

    def test_get_file_hash_nonexistent_file(self, mock_unified_db):
        """测试不存在文件的哈希计算"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            hash_result = service._get_file_hash(Path("/nonexistent/file.txt"))
            assert hash_result == ""

    # ==== 目录扫描测试 ====

    def test_scan_directory_success(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试目录扫描成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml", "*.yml"]
            )

            results = service._scan_directory("models")

            assert len(results) == 2  # 两个模型文件

            # 验证第一个文件
            file1 = next(r for r in results if r['file_name'] == 'model1.yaml')
            assert file1['config_name'] == "models"
            assert 'file_hash' in file1
            assert 'file_size' in file1
            assert 'last_modified' in file1
            assert 'scan_time' in file1
            assert file1['content']['name'] == "test-model-1"

    def test_scan_directory_nonexistent_path(self, mock_unified_db):
        """测试扫描不存在的目录"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(
                name="test",
                path="/nonexistent/path"
            )

            results = service._scan_directory("test")
            assert results == []

    def test_scan_directory_file_processing_error(self, mock_unified_db, temp_project_root):
        """测试文件处理错误"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            # 创建一个无法访问的文件（模拟权限错误）
            test_dir = temp_project_root / "test"
            test_dir.mkdir()
            test_file = test_dir / "test.yaml"
            test_file.touch()

            service.add_scan_config(name="test", path=str(test_dir))

            # 模拟文件读取错误
            with patch.object(service, '_default_yaml_parser', side_effect=Exception("Read error")):
                results = service._scan_directory("test")
                assert results == []

    # ==== 同步操作测试 ====

    def test_sync_config_success(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试配置同步成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml", "*.yml"]
            )

            # 模拟空的现有记录
            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = []

            stats = service.sync_config("models")

            assert stats['added'] == 2
            assert stats['updated'] == 0
            assert stats['deleted'] == 0
            assert stats['unchanged'] == 0

            # 验证插入调用
            assert mock_table.insert.call_count == 2

    def test_sync_config_update_existing(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试更新现有文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml", "*.yml"]
            )

            # 模拟现有记录（文件哈希不同）
            existing_record = {
                'file_path': 'resources/models/model1.yaml',
                'file_hash': 'old_hash',
                'file_size': 100,
                'last_modified': 1234567890
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = [existing_record]

            stats = service.sync_config("models")

            assert stats['added'] == 1  # model2.yml
            assert stats['updated'] == 1  # model1.yaml updated
            assert stats['deleted'] == 0
            assert stats['unchanged'] == 0

    def test_sync_config_delete_removed_files(self, mock_unified_db, temp_project_root):
        """测试删除已移除的文件记录"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()

            # 创建空目录
            test_dir = temp_project_root / "test"
            test_dir.mkdir()

            service.add_scan_config(name="test", path=str(test_dir))

            # 模拟现有记录但文件不存在
            existing_record = {
                'file_path': 'test/removed_file.yaml',
                'file_hash': 'hash',
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = [existing_record]

            stats = service.sync_config("test")

            assert stats['deleted'] == 1
            assert mock_table.remove.call_count == 1

    def test_sync_config_unchanged_files(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试未变化的文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml"]
            )

            # 计算实际文件哈希
            actual_hash = service._get_file_hash(sample_yaml_files['model1'])

            # 模拟相同哈希的现有记录
            existing_record = {
                'file_path': 'resources/models/model1.yaml',
                'file_hash': actual_hash,
                'file_size': 100,
                'last_modified': 1234567890
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = [existing_record]

            stats = service.sync_config("models")

            assert stats['unchanged'] == 1

    def test_sync_config_invalid_config(self, mock_unified_db):
        """测试同步无效配置"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            with pytest.raises(ValueError, match="Config 'nonexistent' not found"):
                service.sync_config("nonexistent")

    def test_sync_all_configs(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试同步所有配置"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml", "*.yml"]
            )
            service.add_scan_config(
                name="hooks",
                path=str(sample_yaml_files['hooks_dir']),
                patterns=["*.md"]
            )

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = []

            results = service.sync_all()

            assert "models" in results
            assert "hooks" in results
            assert results["models"]["added"] == 2
            assert results["hooks"]["added"] == 1

    # ==== 数据查询测试 ====

    def test_get_cached_data_no_filters(self, mock_unified_db):
        """测试无筛选条件获取缓存数据"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            mock_data = [{"name": "item1"}, {"name": "item2"}]
            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = mock_data

            result = service.get_cached_data("test")

            assert result == mock_data
            mock_table.all.assert_called_once()

    def test_get_cached_data_with_string_filter(self, mock_unified_db):
        """测试字符串筛选条件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            filters = {"name": "test_value"}
            mock_data = [{"name": "test_value"}]

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = mock_data

            result = service.get_cached_data("test", filters)

            assert result == mock_data
            mock_table.search.assert_called_once()

    def test_get_cached_data_with_list_filter(self, mock_unified_db):
        """测试列表筛选条件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            filters = {"category": ["type1", "type2"]}
            mock_data = [{"category": "type1"}]

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = mock_data

            result = service.get_cached_data("test", filters)

            assert result == mock_data

    def test_get_cached_data_with_contains_filter(self, mock_unified_db):
        """测试包含筛选条件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            filters = {"description": {"contains": "test"}}
            mock_data = [{"description": "contains test"}]

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = mock_data

            result = service.get_cached_data("test", filters)

            assert result == mock_data

    def test_get_cached_data_multiple_filters(self, mock_unified_db):
        """测试多个筛选条件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            filters = {
                "name": "test",
                "category": ["type1", "type2"],
                "description": {"contains": "keyword"}
            }
            mock_data = [{"name": "test", "category": "type1"}]

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = mock_data

            result = service.get_cached_data("test", filters)

            assert result == mock_data

    def test_get_cached_data_invalid_config(self, mock_unified_db):
        """测试无效配置名称"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            with pytest.raises(ValueError, match="Config 'invalid' not found"):
                service.get_cached_data("invalid")

    def test_get_file_by_path_success(self, mock_unified_db):
        """测试根据路径获取文件成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            mock_data = [{"file_path": "test/file.yaml", "content": {}}]
            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = mock_data

            result = service.get_file_by_path("test", "test/file.yaml")

            assert result == mock_data[0]

    def test_get_file_by_path_not_found(self, mock_unified_db):
        """测试根据路径获取文件未找到"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = []

            result = service.get_file_by_path("test", "nonexistent.yaml")

            assert result is None

    def test_get_file_by_path_invalid_config(self, mock_unified_db):
        """测试无效配置名称"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            result = service.get_file_by_path("invalid", "file.yaml")

            assert result is None

    # ==== FileChangeHandler 测试 ====

    def test_file_change_handler_init(self, mock_unified_db):
        """测试文件变化监听器初始化"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            handler = service.FileChangeHandler(service, "test")

            assert handler.db_service == service
            assert handler.config_name == "test"
            assert handler.config == service._scan_configs["test"]

    def test_file_change_handler_should_process_file(self, mock_unified_db):
        """测试文件处理判断"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", patterns=["*.yaml", "*.yml"])

            handler = service.FileChangeHandler(service, "test")

            assert handler._should_process_file(Path("test.yaml")) is True
            assert handler._should_process_file(Path("test.yml")) is True
            assert handler._should_process_file(Path("test.txt")) is False

    def test_file_change_handler_on_modified(self, mock_unified_db):
        """测试文件修改事件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", patterns=["*.yaml"])

            handler = service.FileChangeHandler(service, "test")

            # 模拟文件修改事件
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = "/test/file.yaml"

            with patch.object(handler, '_sync_file') as mock_sync:
                handler.on_modified(mock_event)
                mock_sync.assert_called_once_with(Path("/test/file.yaml"))

    def test_file_change_handler_on_created(self, mock_unified_db):
        """测试文件创建事件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", patterns=["*.yaml"])

            handler = service.FileChangeHandler(service, "test")

            # 模拟文件创建事件
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = "/test/new_file.yaml"

            with patch.object(handler, '_sync_file') as mock_sync:
                handler.on_created(mock_event)
                mock_sync.assert_called_once_with(Path("/test/new_file.yaml"))

    def test_file_change_handler_on_deleted(self, mock_unified_db):
        """测试文件删除事件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", patterns=["*.yaml"])

            handler = service.FileChangeHandler(service, "test")

            # 模拟文件删除事件
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = "/test/deleted_file.yaml"

            with patch.object(handler, '_remove_file') as mock_remove:
                handler.on_deleted(mock_event)
                mock_remove.assert_called_once_with(Path("/test/deleted_file.yaml"))

    def test_file_change_handler_ignore_directory_events(self, mock_unified_db):
        """测试忽略目录事件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            handler = service.FileChangeHandler(service, "test")

            # 模拟目录事件
            mock_event = Mock()
            mock_event.is_directory = True
            mock_event.src_path = "/test/directory"

            with patch.object(handler, '_sync_file') as mock_sync, \
                 patch.object(handler, '_remove_file') as mock_remove:

                handler.on_modified(mock_event)
                handler.on_created(mock_event)
                handler.on_deleted(mock_event)

                mock_sync.assert_not_called()
                mock_remove.assert_not_called()

    def test_file_change_handler_ignore_non_matching_files(self, mock_unified_db):
        """测试忽略不匹配的文件"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", patterns=["*.yaml"])

            handler = service.FileChangeHandler(service, "test")

            # 模拟不匹配的文件事件
            mock_event = Mock()
            mock_event.is_directory = False
            mock_event.src_path = "/test/file.txt"

            with patch.object(handler, '_sync_file') as mock_sync:
                handler.on_modified(mock_event)
                mock_sync.assert_not_called()

    # ==== 文件监听管理测试 ====

    def test_start_watching_success(self, mock_unified_db):
        """测试启动文件监听成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", watch=True)

            mock_observer = Mock()

            with patch('app.core.database_service.Observer', return_value=mock_observer):
                service.start_watching()

                assert service._running is True
                assert service.observer == mock_observer
                mock_observer.start.assert_called_once()

    def test_start_watching_no_watch_configs(self, mock_unified_db):
        """测试没有监听配置时启动监听"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test", watch=False)

            service.start_watching()

            assert service._running is False
            assert service.observer is None

    def test_start_watching_already_running(self, mock_unified_db):
        """测试已经在运行时启动监听"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service._running = True

            result = service.start_watching()

            assert result is False

    def test_stop_watching_success(self, mock_unified_db):
        """测试停止文件监听成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_observer = Mock()
            service.observer = mock_observer
            service._running = True

            service.stop_watching()

            assert service._running is False
            mock_observer.stop.assert_called_once()
            mock_observer.join.assert_called_once()

    def test_stop_watching_not_running(self, mock_unified_db):
        """测试未运行时停止监听"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service._running = False

            result = service.stop_watching()

            assert result is False

    # ==== 高级操作测试 ====

    def test_cache_data_to_table_success(self, mock_unified_db):
        """测试缓存数据到表成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            test_data = {"name": "test", "value": 123}
            mock_table = mock_unified_db.db.table.return_value

            result = service.cache_data_to_table("test_table", "test_key", test_data)

            assert result is True
            mock_table.upsert.assert_called_once()

    def test_cache_data_to_table_exception(self, mock_unified_db):
        """测试缓存数据异常"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_table = mock_unified_db.db.table.return_value
            mock_table.upsert.side_effect = Exception("Database error")

            result = service.cache_data_to_table("test_table", "test_key", {})

            assert result is False

    def test_remove_data_from_table_success(self, mock_unified_db):
        """测试从表删除数据成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_table = mock_unified_db.db.table.return_value

            result = service.remove_data_from_table("test_table", "test_key")

            assert result is True
            mock_table.remove.assert_called_once()

    def test_remove_data_from_table_exception(self, mock_unified_db):
        """测试删除数据异常"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_table = mock_unified_db.db.table.return_value
            mock_table.remove.side_effect = Exception("Database error")

            result = service.remove_data_from_table("test_table", "test_key")

            assert result is False

    def test_get_cached_data_by_table_success(self, mock_unified_db):
        """测试按表获取数据成功"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_data = [{"name": "item1"}, {"name": "item2"}]
            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = mock_data

            result = service.get_cached_data_by_table("test_table")

            assert result == mock_data

    def test_get_cached_data_by_table_exception(self, mock_unified_db):
        """测试按表获取数据异常"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.side_effect = Exception("Database error")

            result = service.get_cached_data_by_table("test_table")

            assert result == []

    # ==== 数据库关闭测试 ====

    def test_close_unified_db(self, mock_unified_db):
        """测试关闭统一数据库"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService(use_unified_db=True)

            with patch.object(service, 'stop_watching') as mock_stop:
                service.close()
                mock_stop.assert_called_once()
                # 统一数据库不应该调用close
                mock_unified_db.db.close.assert_not_called()

    def test_close_standalone_db(self, mock_tinydb, temp_project_root):
        """测试关闭独立数据库"""
        with patch('app.core.database_service.PROJECT_ROOT', temp_project_root), \
             patch('app.core.database_service.TinyDB', return_value=mock_tinydb):

            service = DatabaseService(use_unified_db=False)

            with patch.object(service, 'stop_watching') as mock_stop:
                service.close()
                mock_stop.assert_called_once()
                mock_tinydb.close.assert_called_once()

    # ==== 全局函数测试 ====

    def test_get_database_service_singleton(self, mock_unified_db):
        """测试数据库服务单例"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service._db_service', None):

            # 第一次调用创建实例
            service1 = get_database_service()

            # 第二次调用返回同一实例
            service2 = get_database_service()

            assert service1 is service2

    def test_get_database_service_with_default_configs(self, mock_unified_db, temp_project_root):
        """测试带默认配置的数据库服务"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root), \
             patch('app.core.database_service._db_service', None):

            # 创建资源目录
            models_dir = temp_project_root / "resources" / "models"
            models_dir.mkdir(parents=True)

            hooks_dir = temp_project_root / "resources" / "hooks"
            hooks_dir.mkdir(parents=True)

            rules_dir = temp_project_root / "resources"

            service = get_database_service()

            # 验证默认配置被添加
            assert "models" in service._scan_configs
            assert "hooks" in service._scan_configs
            assert "rules" in service._scan_configs

    def test_init_database_service(self, mock_unified_db):
        """测试初始化数据库服务"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service._db_service', None):

            mock_service = Mock()
            mock_service.sync_all.return_value = {"test": {"added": 1}}
            mock_service.start_watching.return_value = None

            with patch('app.core.database_service.get_database_service', return_value=mock_service):
                result = init_database_service()

                assert result == mock_service
                mock_service.sync_all.assert_called_once()
                mock_service.start_watching.assert_called_once()

    # ==== 边界条件和错误处理测试 ====

    def test_sync_config_missing_metadata_fields(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试缺少元数据字段的同步"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml"]
            )

            # 模拟缺少字段的现有记录
            existing_record = {
                'file_path': 'resources/models/model1.yaml',
                'file_hash': 'different_hash',
                # 缺少 file_size 字段
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = [existing_record]

            stats = service.sync_config("models")

            # 应该更新缺少字段的记录
            assert stats['updated'] == 1

    def test_sync_config_string_timestamp_conversion(self, mock_unified_db, sample_yaml_files, temp_project_root):
        """测试字符串时间戳转换"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db), \
             patch('app.core.database_service.PROJECT_ROOT', temp_project_root):

            service = DatabaseService()
            service.add_scan_config(
                name="models",
                path=str(sample_yaml_files['models_dir']),
                patterns=["*.yaml"]
            )

            # 模拟字符串类型的时间戳
            existing_record = {
                'file_path': 'resources/models/model1.yaml',
                'file_hash': 'hash',
                'file_size': 100,
                'last_modified': "1234567890"  # 字符串类型
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.all.return_value = [existing_record]

            stats = service.sync_config("models")

            # 应该更新字符串时间戳的记录
            assert stats['updated'] == 1

    def test_file_change_handler_sync_file_exception(self, mock_unified_db):
        """测试文件同步异常处理"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            handler = service.FileChangeHandler(service, "test")

            # 模拟线程创建失败
            with patch('app.core.database_service.threading.Thread', side_effect=Exception("Thread error")):
                # 不应该抛出异常
                handler._sync_file(Path("/test/file.yaml"))

    def test_complex_filters_query_building(self, mock_unified_db):
        """测试复杂筛选条件查询构建"""
        with patch('app.core.database_service.get_unified_database', return_value=mock_unified_db):
            service = DatabaseService()
            service.add_scan_config(name="test", path="/test")

            # 复杂的筛选条件组合
            filters = {
                "name": "test_name",
                "tags": ["tag1", "tag2"],
                "description": {"contains": "keyword"},
                "version": "1.0.0"
            }

            mock_table = mock_unified_db.db.table.return_value
            mock_table.search.return_value = []

            service.get_cached_data("test", filters)

            # 验证search被调用
            mock_table.search.assert_called_once()

if __name__ == "__main__":
    pytest.main([__file__, "-v"])