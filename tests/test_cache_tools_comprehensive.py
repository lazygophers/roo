"""
缓存工具模块全面功能测试
目标：将cache_tools.py的测试覆盖率从38%提升到90%+
涵盖SimpleCache类和所有缓存工具函数的全面测试
"""
import pytest
import time
import threading
from unittest.mock import Mock, patch

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.tools.cache_tools import (
        SimpleCache, _cache,
        cache_set, cache_get, cache_delete, cache_exists,
        cache_ttl, cache_expire, cache_keys, cache_mset,
        cache_mget, cache_incr, cache_info, cache_flushall
    )
    CACHE_TOOLS_AVAILABLE = True
except ImportError as e:
    CACHE_TOOLS_AVAILABLE = False
    print(f"Cache tools import failed: {e}")


@pytest.mark.skipif(not CACHE_TOOLS_AVAILABLE, reason="Cache tools module not available")
class TestCacheToolsComprehensive:
    """缓存工具模块全面测试套件"""

    @pytest.fixture
    def fresh_cache(self):
        """为每个测试创建新的缓存实例"""
        cache = SimpleCache()
        return cache

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """测试前后清理全局缓存"""
        _cache.clear()
        yield
        _cache.clear()

    # ==== SimpleCache 类基础功能测试 ====

    def test_simple_cache_init(self, fresh_cache):
        """测试SimpleCache初始化"""
        assert fresh_cache._cache == {}
        # 检查锁是否是锁类型的实例（兼容不同的锁实现）
        assert hasattr(fresh_cache._lock, 'acquire') and hasattr(fresh_cache._lock, 'release')

    def test_simple_cache_set_without_ttl(self, fresh_cache):
        """测试设置缓存无过期时间"""
        fresh_cache.set("test_key", "test_value")

        assert "test_key" in fresh_cache._cache
        assert fresh_cache._cache["test_key"]["value"] == "test_value"
        assert fresh_cache._cache["test_key"]["expire_time"] is None

    def test_simple_cache_set_with_ttl(self, fresh_cache):
        """测试设置缓存带过期时间"""
        start_time = time.time()
        fresh_cache.set("test_key", "test_value", ttl=10)

        assert "test_key" in fresh_cache._cache
        assert fresh_cache._cache["test_key"]["value"] == "test_value"
        expire_time = fresh_cache._cache["test_key"]["expire_time"]
        assert expire_time is not None
        assert expire_time > start_time + 9  # 允许一些时间误差

    def test_simple_cache_get_existing_key(self, fresh_cache):
        """测试获取存在的键"""
        fresh_cache.set("test_key", "test_value")
        value = fresh_cache.get("test_key")
        assert value == "test_value"

    def test_simple_cache_get_nonexistent_key(self, fresh_cache):
        """测试获取不存在的键"""
        value = fresh_cache.get("nonexistent_key")
        assert value is None

    def test_simple_cache_get_expired_key(self, fresh_cache):
        """测试获取过期的键"""
        fresh_cache.set("test_key", "test_value", ttl=1)

        # 立即获取应该成功
        value = fresh_cache.get("test_key")
        assert value == "test_value"

        # 等待过期
        time.sleep(1.1)
        value = fresh_cache.get("test_key")
        assert value is None
        assert "test_key" not in fresh_cache._cache  # 过期键被删除

    def test_simple_cache_delete_existing_key(self, fresh_cache):
        """测试删除存在的键"""
        fresh_cache.set("test_key", "test_value")
        result = fresh_cache.delete("test_key")

        assert result is True
        assert "test_key" not in fresh_cache._cache

    def test_simple_cache_delete_nonexistent_key(self, fresh_cache):
        """测试删除不存在的键"""
        result = fresh_cache.delete("nonexistent_key")
        assert result is False

    def test_simple_cache_exists_existing_key(self, fresh_cache):
        """测试检查存在的键"""
        fresh_cache.set("test_key", "test_value")
        assert fresh_cache.exists("test_key") is True

    def test_simple_cache_exists_nonexistent_key(self, fresh_cache):
        """测试检查不存在的键"""
        assert fresh_cache.exists("nonexistent_key") is False

    def test_simple_cache_exists_expired_key(self, fresh_cache):
        """测试检查过期的键"""
        fresh_cache.set("test_key", "test_value", ttl=1)
        time.sleep(1.1)
        assert fresh_cache.exists("test_key") is False

    def test_simple_cache_keys_all_pattern(self, fresh_cache):
        """测试获取所有键"""
        fresh_cache.set("key1", "value1")
        fresh_cache.set("key2", "value2")
        fresh_cache.set("test_key", "test_value")

        keys = fresh_cache.keys("*")
        assert set(keys) == {"key1", "key2", "test_key"}

    def test_simple_cache_keys_with_pattern(self, fresh_cache):
        """测试使用模式匹配获取键"""
        fresh_cache.set("user:1", "Alice")
        fresh_cache.set("user:2", "Bob")
        fresh_cache.set("session:1", "session_data")

        keys = fresh_cache.keys("user")
        assert set(keys) == {"user:1", "user:2"}

    def test_simple_cache_keys_expired_filtering(self, fresh_cache):
        """测试键列表自动过滤过期键"""
        fresh_cache.set("permanent", "value")
        fresh_cache.set("temporary", "value", ttl=1)

        time.sleep(1.1)
        keys = fresh_cache.keys("*")
        assert keys == ["permanent"]

    def test_simple_cache_clear(self, fresh_cache):
        """测试清空缓存"""
        fresh_cache.set("key1", "value1")
        fresh_cache.set("key2", "value2")

        fresh_cache.clear()
        assert fresh_cache._cache == {}

    def test_simple_cache_match_pattern(self, fresh_cache):
        """测试模式匹配逻辑"""
        assert fresh_cache._match_pattern("user:123", "user") is True
        assert fresh_cache._match_pattern("session:abc", "user") is False
        assert fresh_cache._match_pattern("prefix_suffix", "prefix") is True

    def test_simple_cache_is_valid(self, fresh_cache):
        """测试键有效性检查"""
        # 不存在的键
        assert fresh_cache._is_valid("nonexistent") is False

        # 永久键
        fresh_cache.set("permanent", "value")
        assert fresh_cache._is_valid("permanent") is True

        # 过期键
        fresh_cache.set("temporary", "value", ttl=1)
        time.sleep(1.1)
        assert fresh_cache._is_valid("temporary") is False
        assert "temporary" not in fresh_cache._cache  # 过期键被清理

    # ==== 缓存工具函数测试 ====

    def test_cache_set_success(self):
        """测试cache_set成功"""
        result = cache_set("test_key", "test_value")

        assert result["success"] is True
        assert result["key"] == "test_key"
        assert "Value set successfully" in result["message"]

        # 验证实际设置成功
        assert _cache.get("test_key") == "test_value"

    def test_cache_set_with_ttl(self):
        """测试cache_set带TTL"""
        result = cache_set("test_key", "test_value", ttl=10)

        assert result["success"] is True
        assert _cache.get("test_key") == "test_value"

    def test_cache_set_complex_value(self):
        """测试cache_set复杂值类型"""
        complex_value = {
            "user_id": 123,
            "data": [1, 2, 3],
            "nested": {"key": "value"}
        }
        result = cache_set("complex_key", complex_value)

        assert result["success"] is True
        assert _cache.get("complex_key") == complex_value

    def test_cache_set_exception_handling(self):
        """测试cache_set异常处理"""
        with patch.object(_cache, 'set', side_effect=Exception("Cache error")):
            result = cache_set("test_key", "test_value")

            assert result["success"] is False
            assert "Cache error" in result["error"]

    def test_cache_get_existing_key(self):
        """测试cache_get获取存在的键"""
        _cache.set("test_key", "test_value")
        result = cache_get("test_key")

        assert result["success"] is True
        assert result["key"] == "test_key"
        assert result["value"] == "test_value"
        assert result["exists"] is True

    def test_cache_get_nonexistent_key(self):
        """测试cache_get获取不存在的键"""
        result = cache_get("nonexistent_key")

        assert result["success"] is True
        assert result["key"] == "nonexistent_key"
        assert result["value"] is None
        assert result["exists"] is False

    def test_cache_get_exception_handling(self):
        """测试cache_get异常处理"""
        with patch.object(_cache, 'get', side_effect=Exception("Cache error")):
            result = cache_get("test_key")

            assert result["success"] is False
            assert result["key"] == "test_key"
            assert result["exists"] is False
            assert "Cache error" in result["error"]

    def test_cache_delete_existing_key(self):
        """测试cache_delete删除存在的键"""
        _cache.set("test_key", "test_value")
        result = cache_delete("test_key")

        assert result["success"] is True
        assert result["key"] == "test_key"
        assert result["deleted"] is True

        # 验证键被删除
        assert _cache.get("test_key") is None

    def test_cache_delete_nonexistent_key(self):
        """测试cache_delete删除不存在的键"""
        result = cache_delete("nonexistent_key")

        assert result["success"] is True
        assert result["key"] == "nonexistent_key"
        assert result["deleted"] is False

    def test_cache_delete_exception_handling(self):
        """测试cache_delete异常处理"""
        with patch.object(_cache, 'delete', side_effect=Exception("Cache error")):
            result = cache_delete("test_key")

            assert result["success"] is False
            assert result["key"] == "test_key"
            assert "Cache error" in result["error"]

    def test_cache_exists_existing_key(self):
        """测试cache_exists检查存在的键"""
        _cache.set("test_key", "test_value")
        result = cache_exists("test_key")

        assert result["success"] is True
        assert result["key"] == "test_key"
        assert result["exists"] is True

    def test_cache_exists_nonexistent_key(self):
        """测试cache_exists检查不存在的键"""
        result = cache_exists("nonexistent_key")

        assert result["success"] is True
        assert result["key"] == "nonexistent_key"
        assert result["exists"] is False

    def test_cache_exists_exception_handling(self):
        """测试cache_exists异常处理"""
        with patch.object(_cache, 'exists', side_effect=Exception("Cache error")):
            result = cache_exists("test_key")

            assert result["success"] is False
            assert result["key"] == "test_key"
            assert "Cache error" in result["error"]

    def test_cache_keys_all_pattern(self):
        """测试cache_keys获取所有键"""
        _cache.set("key1", "value1")
        _cache.set("key2", "value2")
        _cache.set("test_key", "test_value")

        result = cache_keys("*")

        assert result["success"] is True
        assert result["pattern"] == "*"
        assert set(result["keys"]) == {"key1", "key2", "test_key"}

    def test_cache_keys_with_pattern(self):
        """测试cache_keys使用模式"""
        _cache.set("user:1", "Alice")
        _cache.set("user:2", "Bob")
        _cache.set("session:1", "session_data")

        result = cache_keys("user")

        assert result["success"] is True
        assert result["pattern"] == "user"
        assert set(result["keys"]) == {"user:1", "user:2"}

    def test_cache_keys_default_pattern(self):
        """测试cache_keys默认模式"""
        _cache.set("test_key", "test_value")

        result = cache_keys()  # 不传参数，使用默认的"*"

        assert result["success"] is True
        assert result["pattern"] == "*"
        assert "test_key" in result["keys"]

    def test_cache_keys_exception_handling(self):
        """测试cache_keys异常处理"""
        with patch.object(_cache, 'keys', side_effect=Exception("Cache error")):
            result = cache_keys("*")

            assert result["success"] is False
            assert result["pattern"] == "*"
            assert "Cache error" in result["error"]

    def test_cache_flushall_success(self):
        """测试cache_flushall清空所有缓存"""
        _cache.set("key1", "value1")
        _cache.set("key2", "value2")

        result = cache_flushall()

        assert result["success"] is True
        assert "All cache data cleared" in result["message"]

        # 验证缓存被清空
        assert _cache.get("key1") is None
        assert _cache.get("key2") is None

    def test_cache_flushall_exception_handling(self):
        """测试cache_flushall异常处理"""
        with patch.object(_cache, 'clear', side_effect=Exception("Cache error")):
            result = cache_flushall()

            assert result["success"] is False
            assert "Cache error" in result["error"]

    # ==== 未实现函数测试（占位符函数）====

    def test_cache_ttl_placeholder(self):
        """测试cache_ttl占位符函数"""
        result = cache_ttl()
        assert result is None  # 未实现，返回None

    def test_cache_expire_placeholder(self):
        """测试cache_expire占位符函数"""
        result = cache_expire()
        assert result is None  # 未实现，返回None

    def test_cache_mset_placeholder(self):
        """测试cache_mset占位符函数"""
        result = cache_mset()
        assert result is None  # 未实现，返回None

    def test_cache_mget_placeholder(self):
        """测试cache_mget占位符函数"""
        result = cache_mget()
        assert result is None  # 未实现，返回None

    def test_cache_incr_placeholder(self):
        """测试cache_incr占位符函数"""
        result = cache_incr()
        assert result is None  # 未实现，返回None

    def test_cache_info_placeholder(self):
        """测试cache_info占位符函数"""
        result = cache_info()
        assert result is None  # 未实现，返回None

    # ==== 线程安全测试 ====

    def test_simple_cache_thread_safety(self, fresh_cache):
        """测试SimpleCache线程安全性"""
        results = {}

        def set_values(thread_id):
            for i in range(100):
                fresh_cache.set(f"thread_{thread_id}_key_{i}", f"value_{i}")

        def get_values(thread_id):
            retrieved = []
            for i in range(100):
                value = fresh_cache.get(f"thread_{thread_id}_key_{i}")
                if value:
                    retrieved.append(value)
            results[thread_id] = len(retrieved)

        # 创建多个线程同时设置数据
        threads = []
        for i in range(3):
            t = threading.Thread(target=set_values, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有设置线程完成
        for t in threads:
            t.join()

        # 创建多个线程同时读取数据
        threads = []
        for i in range(3):
            t = threading.Thread(target=get_values, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有读取线程完成
        for t in threads:
            t.join()

        # 验证线程安全性：每个线程都应该能读取到自己设置的所有数据
        for thread_id in range(3):
            assert results[thread_id] == 100, f"Thread {thread_id} only retrieved {results[thread_id]} values"

    # ==== 边界条件和特殊情况测试 ====

    def test_cache_complex_data_types(self):
        """测试缓存复杂数据类型"""
        test_cases = [
            ("string", "hello world"),
            ("integer", 42),
            ("float", 3.14159),
            ("boolean", True),
            ("list", [1, 2, 3, "four", 5.0]),
            ("dict", {"key": "value", "nested": {"inner": "data"}}),
            ("tuple", (1, 2, "three")),
            ("none", None),
        ]

        for key, value in test_cases:
            result = cache_set(key, value)
            assert result["success"] is True

            get_result = cache_get(key)
            assert get_result["success"] is True
            assert get_result["value"] == value

    def test_cache_zero_ttl_behavior(self):
        """测试TTL为0的行为"""
        result = cache_set("permanent_key", "permanent_value", ttl=0)
        assert result["success"] is True

        # 等待一段时间，应该仍然存在
        time.sleep(0.1)
        get_result = cache_get("permanent_key")
        assert get_result["exists"] is True
        assert get_result["value"] == "permanent_value"

    def test_cache_very_short_ttl(self):
        """测试非常短的TTL"""
        result = cache_set("short_lived_key", "short_lived_value", ttl=1)
        assert result["success"] is True

        # 立即检查应该存在
        get_result = cache_get("short_lived_key")
        assert get_result["exists"] is True

        # 等待过期
        time.sleep(1.1)
        get_result = cache_get("short_lived_key")
        assert get_result["exists"] is False

    def test_cache_key_overwrite(self):
        """测试键覆盖行为"""
        # 设置原始值
        cache_set("overwrite_key", "original_value")

        # 覆盖值
        cache_set("overwrite_key", "new_value")

        # 验证被覆盖
        get_result = cache_get("overwrite_key")
        assert get_result["value"] == "new_value"

    def test_cache_large_data(self):
        """测试大数据缓存"""
        large_string = "x" * 10000  # 10KB字符串
        large_list = list(range(1000))  # 1000个元素的列表

        # 测试大字符串
        result = cache_set("large_string", large_string)
        assert result["success"] is True

        get_result = cache_get("large_string")
        assert get_result["value"] == large_string

        # 测试大列表
        result = cache_set("large_list", large_list)
        assert result["success"] is True

        get_result = cache_get("large_list")
        assert get_result["value"] == large_list

    def test_cache_special_characters_in_keys(self):
        """测试键中的特殊字符"""
        special_keys = [
            "key:with:colons",
            "key-with-dashes",
            "key_with_underscores",
            "key.with.dots",
            "key with spaces",
            "key/with/slashes",
            "key\\with\\backslashes",
            "键中文字符",
            "key@#$%^&*()",
        ]

        for key in special_keys:
            result = cache_set(key, f"value_for_{key}")
            assert result["success"] is True

            get_result = cache_get(key)
            assert get_result["exists"] is True
            assert get_result["value"] == f"value_for_{key}"

    def test_cache_empty_values(self):
        """测试空值缓存"""
        empty_values = [
            ("empty_string", ""),
            ("empty_list", []),
            ("empty_dict", {}),
            ("zero", 0),
            ("false", False),
        ]

        for key, value in empty_values:
            result = cache_set(key, value)
            assert result["success"] is True

            get_result = cache_get(key)
            assert get_result["exists"] is True
            assert get_result["value"] == value

    # ==== 集成测试 ====

    def test_cache_workflow_integration(self):
        """测试完整的缓存工作流程"""
        # 1. 设置多个键
        cache_set("user:1", {"name": "Alice", "age": 30})
        cache_set("user:2", {"name": "Bob", "age": 25})
        cache_set("session:abc", "session_data", ttl=5)

        # 2. 检查键是否存在
        assert cache_exists("user:1")["exists"] is True
        assert cache_exists("user:2")["exists"] is True
        assert cache_exists("session:abc")["exists"] is True

        # 3. 获取所有用户键
        user_keys = cache_keys("user")
        assert set(user_keys["keys"]) == {"user:1", "user:2"}

        # 4. 删除一个键
        delete_result = cache_delete("user:2")
        assert delete_result["deleted"] is True

        # 5. 验证删除
        assert cache_exists("user:2")["exists"] is False

        # 6. 获取剩余键
        remaining_keys = cache_keys("*")
        assert "user:1" in remaining_keys["keys"]
        assert "user:2" not in remaining_keys["keys"]
        assert "session:abc" in remaining_keys["keys"]

        # 7. 清空所有缓存
        flush_result = cache_flushall()
        assert flush_result["success"] is True

        # 8. 验证清空
        all_keys = cache_keys("*")
        assert all_keys["keys"] == []

    def test_cache_concurrent_operations(self):
        """测试并发操作"""
        def worker(worker_id):
            for i in range(50):
                # 设置键
                cache_set(f"worker_{worker_id}_key_{i}", f"value_{i}")

                # 立即获取
                result = cache_get(f"worker_{worker_id}_key_{i}")
                assert result["exists"] is True

                # 检查存在性
                exists_result = cache_exists(f"worker_{worker_id}_key_{i}")
                assert exists_result["exists"] is True

        # 启动多个工作线程
        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        # 等待所有线程完成
        for t in threads:
            t.join()

        # 验证最终结果
        all_keys = cache_keys("*")
        assert len(all_keys["keys"]) == 250  # 5个工作线程 × 50个键

if __name__ == "__main__":
    pytest.main([__file__, "-v"])