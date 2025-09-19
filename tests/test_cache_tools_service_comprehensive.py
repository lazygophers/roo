"""
缓存工具服务全面测试
目标：将cache_tools_service.py的测试覆盖率从0%提升到90%+
涵盖Redis风格缓存、数据类型操作、TTL管理等核心功能
"""
import pytest
import json
import time
import threading
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# 尝试导入模块
try:
    from app.core.cache_tools_service import (
        CacheToolsService, CacheItem, CacheDataType, CacheToolsConfig
    )
    CACHE_TOOLS_SERVICE_AVAILABLE = True
except ImportError as e:
    CACHE_TOOLS_SERVICE_AVAILABLE = False
    print(f"Cache tools service import failed: {e}")


@pytest.mark.skipif(not CACHE_TOOLS_SERVICE_AVAILABLE, reason="Cache tools service module not available")
class TestCacheToolsServiceComprehensive:
    """缓存工具服务全面测试套件"""

    @pytest.fixture
    def mock_unified_db(self):
        """模拟统一数据库"""
        mock_db = Mock()
        mock_unified_db = Mock()
        mock_unified_db.get_table.return_value = mock_db

        # 模拟表操作
        mock_db.get.return_value = None
        mock_db.insert.return_value = None
        mock_db.update.return_value = None
        mock_db.all.return_value = []
        mock_db.search.return_value = []
        mock_db.remove.return_value = None

        return mock_unified_db

    @pytest.fixture
    def cache_service(self, mock_unified_db):
        """创建缓存服务实例"""
        with patch('app.core.cache_tools_service.get_unified_database', return_value=mock_unified_db):
            with patch.object(CacheToolsService, '_start_background_tasks'):
                with patch.object(CacheToolsService, '_initialize_default_config'):
                    service = CacheToolsService(use_unified_db=True)
                    return service

    # ==== CacheItem 数据模型测试 ====

    def test_cache_item_creation_default_values(self):
        """测试CacheItem创建时的默认值"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING
        )

        assert item.key == "test_key"
        assert item.value == "test_value"
        assert item.data_type == CacheDataType.STRING
        assert item.ttl is None
        assert item.created_at > 0
        assert item.last_accessed > 0
        assert item.access_count == 0
        assert item.tags == []

    def test_cache_item_creation_with_values(self):
        """测试CacheItem创建时设置自定义值"""
        created_time = time.time()
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            ttl=3600,
            created_at=created_time,
            last_accessed=created_time,
            access_count=5,
            tags=["tag1", "tag2"]
        )

        assert item.ttl == 3600
        assert item.created_at == created_time
        assert item.access_count == 5
        assert item.tags == ["tag1", "tag2"]

    def test_cache_item_is_expired_no_ttl(self):
        """测试无TTL的缓存项不会过期"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING
        )

        assert item.is_expired() is False

    def test_cache_item_is_expired_with_ttl(self):
        """测试有TTL的缓存项过期检查"""
        past_time = time.time() - 10
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            ttl=5,  # 5秒TTL
            created_at=past_time
        )

        assert item.is_expired() is True

    def test_cache_item_not_expired_with_ttl(self):
        """测试有TTL的缓存项未过期"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            ttl=3600  # 1小时TTL
        )

        assert item.is_expired() is False

    def test_cache_item_get_remaining_ttl_no_ttl(self):
        """测试无TTL的剩余时间"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING
        )

        assert item.get_remaining_ttl() == -1

    def test_cache_item_get_remaining_ttl_with_ttl(self):
        """测试有TTL的剩余时间"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            ttl=3600
        )

        remaining = item.get_remaining_ttl()
        assert 3595 <= remaining <= 3600  # 允许小的时间误差

    def test_cache_item_get_remaining_ttl_expired(self):
        """测试已过期项的剩余时间"""
        past_time = time.time() - 10
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            ttl=5,
            created_at=past_time
        )

        assert item.get_remaining_ttl() == 0

    def test_cache_item_update_access(self):
        """测试更新访问信息"""
        item = CacheItem(
            key="test_key",
            value="test_value",
            data_type=CacheDataType.STRING,
            access_count=0
        )

        old_access_time = item.last_accessed
        old_count = item.access_count

        time.sleep(0.001)  # 确保时间差异
        item.update_access()

        assert item.last_accessed > old_access_time
        assert item.access_count == old_count + 1

    # ==== CacheToolsConfig 数据模型测试 ====

    def test_cache_tools_config_creation(self):
        """测试CacheToolsConfig创建"""
        config = CacheToolsConfig(
            config_type="test_type",
            name="Test Config",
            value=123,
            description="Test description"
        )

        assert config.config_type == "test_type"
        assert config.name == "Test Config"
        assert config.value == 123
        assert config.description == "Test description"
        assert config.created_at == ""
        assert config.updated_at == ""

    # ==== CacheToolsService 初始化测试 ====

    def test_cache_tools_service_init_unified_db(self, mock_unified_db):
        """测试使用统一数据库初始化"""
        with patch('app.core.cache_tools_service.get_unified_database', return_value=mock_unified_db):
            with patch.object(CacheToolsService, '_start_background_tasks'):
                service = CacheToolsService(use_unified_db=True)

                assert service.use_unified_db is True
                assert service.unified_db == mock_unified_db
                assert isinstance(service._memory_cache, dict)
                assert hasattr(service, '_cache_lock')

    def test_cache_tools_service_init_without_unified_db(self):
        """测试不使用统一数据库初始化"""
        with patch.object(CacheToolsService, '_start_background_tasks'):
            service = CacheToolsService(use_unified_db=False)

            assert service.use_unified_db is False
            assert not hasattr(service, 'unified_db')

    # ==== 配置管理测试 ====

    def test_initialize_default_config(self, cache_service):
        """测试初始化默认配置"""
        with patch.object(cache_service, '_create_or_update_config') as mock_create:
            cache_service._initialize_default_config()

            # 验证默认配置被创建
            assert mock_create.call_count == 4  # 4个默认配置项

            # 验证配置类型
            config_types = [call[0][0].config_type for call in mock_create.call_args_list]
            expected_types = ["default_ttl", "persistence_enabled", "compression_enabled", "stats_enabled"]
            assert all(config_type in config_types for config_type in expected_types)

    def test_create_or_update_config_new(self, cache_service):
        """测试创建新配置"""
        config = CacheToolsConfig(
            config_type="new_config",
            name="New Config",
            value=100,
            description="New config description"
        )

        # 模拟数据库中不存在该配置
        cache_service.config_table.get.return_value = None

        result = cache_service._create_or_update_config(config)

        assert result is True  # 新建配置返回True
        cache_service.config_table.insert.assert_called_once()

    def test_create_or_update_config_existing(self, cache_service):
        """测试更新已存在配置"""
        config = CacheToolsConfig(
            config_type="existing_config",
            name="Existing Config",
            value=200,
            description="Existing config description"
        )

        # 模拟数据库中存在该配置
        cache_service.config_table.get.return_value = {"config_type": "existing_config"}

        result = cache_service._create_or_update_config(config)

        assert result is False  # 更新配置返回False
        cache_service.config_table.update.assert_called_once()

    def test_create_or_update_config_exception(self, cache_service):
        """测试配置创建/更新异常处理"""
        config = CacheToolsConfig(
            config_type="error_config",
            name="Error Config",
            value=300,
            description="Error config description"
        )

        # 模拟数据库操作异常
        cache_service.config_table.get.side_effect = Exception("Database error")

        result = cache_service._create_or_update_config(config)

        assert result is False

    def test_get_config_value_existing(self, cache_service):
        """测试获取存在的配置值"""
        # 模拟返回存在的配置
        cache_service.config_table.get.return_value = {"value": 1800}

        result = cache_service._get_config_value("default_ttl", 3600)

        assert result == 1800

    def test_get_config_value_not_existing(self, cache_service):
        """测试获取不存在的配置值"""
        # 模拟返回不存在的配置
        cache_service.config_table.get.return_value = None

        result = cache_service._get_config_value("nonexistent_config", 9999)

        assert result == 9999  # 返回默认值

    def test_get_config_value_exception(self, cache_service):
        """测试获取配置值时的异常处理"""
        # 模拟数据库异常
        cache_service.config_table.get.side_effect = Exception("Database error")

        result = cache_service._get_config_value("error_config", 5555)

        assert result == 5555  # 异常时返回默认值

    # ==== 后台任务测试 ====

    def test_start_background_tasks(self, mock_unified_db):
        """测试启动后台任务"""
        with patch('app.core.cache_tools_service.get_unified_database', return_value=mock_unified_db):
            with patch('threading.Timer') as mock_timer:
                mock_timer_instance = Mock()
                mock_timer.return_value = mock_timer_instance

                service = CacheToolsService(use_unified_db=True)

                # 验证定时器被创建和启动
                mock_timer.assert_called_once_with(300, service._cleanup_expired_items)
                mock_timer_instance.start.assert_called_once()

    def test_start_background_tasks_exception(self, cache_service):
        """测试启动后台任务异常处理"""
        with patch('threading.Timer', side_effect=Exception("Timer error")):
            # 不应该抛出异常
            cache_service._start_background_tasks()

    # ==== 过期清理测试 ====

    def test_cleanup_expired_items_success(self, cache_service):
        """测试清理过期项成功"""
        # 添加已过期和未过期的缓存项
        expired_item = CacheItem(
            key="expired_key",
            value="expired_value",
            data_type=CacheDataType.STRING,
            ttl=1,
            created_at=time.time() - 10
        )

        valid_item = CacheItem(
            key="valid_key",
            value="valid_value",
            data_type=CacheDataType.STRING,
            ttl=3600
        )

        cache_service._memory_cache = {
            "expired_key": expired_item,
            "valid_key": valid_item
        }

        cache_service._cleanup_expired_items()

        # 验证过期项被删除，有效项保留
        assert "expired_key" not in cache_service._memory_cache
        assert "valid_key" in cache_service._memory_cache

    def test_cleanup_expired_items_with_background_task(self, cache_service):
        """测试后台任务中的过期清理"""
        # 添加过期项
        expired_item = CacheItem(
            key="expired_key",
            value="expired_value",
            data_type=CacheDataType.STRING,
            ttl=1,
            created_at=time.time() - 10
        )

        cache_service._memory_cache = {"expired_key": expired_item}

        with patch('threading.Timer') as mock_timer:
            mock_timer_instance = Mock()
            mock_timer.return_value = mock_timer_instance

            cache_service._cleanup_expired_items()

            # 验证清理后启动新的定时器
            mock_timer.assert_called_once_with(300, cache_service._cleanup_expired_items)
            mock_timer_instance.start.assert_called_once()

    def test_cleanup_expired_items_exception(self, cache_service):
        """测试清理过期项异常处理"""
        # 模拟异常情况 - 使用all()方法抛出异常
        with patch.object(cache_service.cache_table, 'all', side_effect=Exception("Database error")):
            # 不应该抛出异常，应该被捕获并记录日志
            cache_service._cleanup_expired_items()

    # ==== 数据类型枚举测试 ====

    def test_cache_data_type_enum_values(self):
        """测试缓存数据类型枚举值"""
        assert CacheDataType.STRING.value == "string"
        assert CacheDataType.HASH.value == "hash"
        assert CacheDataType.LIST.value == "list"
        assert CacheDataType.SET.value == "set"
        assert CacheDataType.ZSET.value == "zset"
        assert CacheDataType.JSON.value == "json"

    # ==== 线程安全测试 ====

    def test_thread_safety_memory_cache_operations(self, cache_service):
        """测试内存缓存操作的线程安全性"""
        results = []
        errors = []

        def cache_worker(worker_id):
            try:
                for i in range(10):
                    # 添加缓存项
                    item = CacheItem(
                        key=f"worker_{worker_id}_item_{i}",
                        value=f"value_{worker_id}_{i}",
                        data_type=CacheDataType.STRING
                    )

                    with cache_service._cache_lock:
                        cache_service._memory_cache[item.key] = item

                    # 读取缓存项
                    with cache_service._cache_lock:
                        retrieved = cache_service._memory_cache.get(item.key)
                        if retrieved and retrieved.value == item.value:
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

    def test_concurrent_cleanup_operations(self, cache_service):
        """测试并发清理操作"""
        # 添加一些缓存项
        for i in range(10):
            item = CacheItem(
                key=f"test_key_{i}",
                value=f"test_value_{i}",
                data_type=CacheDataType.STRING,
                ttl=1 if i % 2 == 0 else 3600  # 一半过期，一半有效
            )
            if i % 2 == 0:  # 设置一半为过期
                item.created_at = time.time() - 10
            cache_service._memory_cache[item.key] = item

        # 并发执行清理操作
        threads = []
        for _ in range(3):
            thread = threading.Thread(target=cache_service._cleanup_expired_items)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        # 验证只有有效项保留
        remaining_keys = list(cache_service._memory_cache.keys())
        assert len(remaining_keys) == 5  # 只有5个有效项

    # ==== 边界条件和错误处理测试 ====

    def test_cache_item_zero_ttl(self):
        """测试TTL为0的缓存项"""
        item = CacheItem(
            key="zero_ttl_key",
            value="zero_ttl_value",
            data_type=CacheDataType.STRING,
            ttl=0
        )

        # TTL为0应该立即过期
        assert item.is_expired() is True
        assert item.get_remaining_ttl() == 0

    def test_cache_item_negative_ttl(self):
        """测试负数TTL的缓存项"""
        item = CacheItem(
            key="negative_ttl_key",
            value="negative_ttl_value",
            data_type=CacheDataType.STRING,
            ttl=-100
        )

        # 负数TTL应该立即过期
        assert item.is_expired() is True
        assert item.get_remaining_ttl() == 0

    def test_large_memory_cache_operations(self, cache_service):
        """测试大量内存缓存操作"""
        # 添加大量缓存项
        for i in range(1000):
            item = CacheItem(
                key=f"large_test_key_{i}",
                value=f"large_test_value_{i}" * 100,  # 较大的值
                data_type=CacheDataType.STRING,
                ttl=3600
            )
            cache_service._memory_cache[item.key] = item

        # 验证所有项都被添加
        assert len(cache_service._memory_cache) == 1000

        # 测试清理操作性能
        start_time = time.time()
        cache_service._cleanup_expired_items()
        end_time = time.time()

        # 清理操作应该在合理时间内完成（1秒内）
        assert end_time - start_time < 1.0

    def test_service_initialization_with_missing_dependencies(self):
        """测试缺少依赖时的服务初始化"""
        with patch('app.core.cache_tools_service.get_unified_database', side_effect=ImportError("Missing module")):
            with patch.object(CacheToolsService, '_start_background_tasks'):
                # 即使缺少依赖也应该能够初始化基本功能
                try:
                    service = CacheToolsService(use_unified_db=False)
                    assert service.use_unified_db is False
                except Exception:
                    pytest.fail("Service initialization should not fail when dependencies are missing")