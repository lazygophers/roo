"""
超级缓存系统全面功能测试
目标：将ultra_cache_system.py的测试覆盖率从0%提升到90%+
涵盖多级缓存、内存池、预计算引擎的全面测试
"""
import pytest
import asyncio
import time
import threading
import tempfile
import shutil
import pickle
import json
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import ThreadPoolExecutor, Future
from collections import OrderedDict, defaultdict

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.core.ultra_cache_system import (
        CacheStats, MemoryPool, SmartCache, PrecomputeEngine,
        UltraCacheSystem, get_ultra_cache, cached
    )
    ULTRA_CACHE_AVAILABLE = True
except ImportError as e:
    ULTRA_CACHE_AVAILABLE = False
    print(f"Ultra cache system import failed: {e}")


@pytest.mark.skipif(not ULTRA_CACHE_AVAILABLE, reason="Ultra cache system module not available")
class TestUltraCacheSystemComprehensive:
    """超级缓存系统全面测试套件"""

    @pytest.fixture
    def temp_cache_dir(self):
        """创建临时缓存目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    # ==== CacheStats 测试 ====

    def test_cache_stats_init(self):
        """测试缓存统计初始化"""
        stats = CacheStats()

        assert stats.hits == 0
        assert stats.misses == 0
        assert stats.evictions == 0
        assert stats.size_bytes == 0
        assert stats.items_count == 0
        assert isinstance(stats.last_hit_time, float)
        assert isinstance(stats.last_miss_time, float)

    def test_cache_stats_hit_rate_zero(self):
        """测试零命中率计算"""
        stats = CacheStats()
        assert stats.hit_rate == 0.0

    def test_cache_stats_hit_rate_calculation(self):
        """测试命中率计算"""
        stats = CacheStats()
        stats.hits = 80
        stats.misses = 20

        assert stats.hit_rate == 0.8

    def test_cache_stats_hit_rate_all_hits(self):
        """测试全命中率"""
        stats = CacheStats()
        stats.hits = 100
        stats.misses = 0

        assert stats.hit_rate == 1.0

    def test_cache_stats_hit_rate_all_misses(self):
        """测试全未命中率"""
        stats = CacheStats()
        stats.hits = 0
        stats.misses = 100

        assert stats.hit_rate == 0.0

    # ==== MemoryPool 测试 ====

    def test_memory_pool_init(self):
        """测试内存池初始化"""
        pool = MemoryPool(max_size=1024)

        assert pool.max_size == 1024
        assert pool.current_size == 0
        assert isinstance(pool._pools, defaultdict)
        assert isinstance(pool._lock, threading.RLock)

    def test_memory_pool_get_buffer_new(self):
        """测试获取新缓冲区"""
        pool = MemoryPool()
        buffer = pool.get_buffer(1024)

        assert isinstance(buffer, bytearray)
        assert len(buffer) == 1024

    def test_memory_pool_get_buffer_from_pool(self):
        """测试从池中获取缓冲区"""
        pool = MemoryPool()

        # 先归还一个缓冲区
        original_buffer = bytearray(512)
        pool.return_buffer(original_buffer)

        # 再获取相同大小的缓冲区
        buffer = pool.get_buffer(512)

        assert buffer is original_buffer

    def test_memory_pool_return_buffer_success(self):
        """测试归还缓冲区成功"""
        pool = MemoryPool(max_size=2048)
        buffer = bytearray(1024)

        pool.return_buffer(buffer)

        assert pool.current_size == 1024
        key = "buffer_1024"
        assert key in pool._pools
        assert buffer in pool._pools[key]

    def test_memory_pool_return_buffer_too_large(self):
        """测试归还过大的缓冲区"""
        pool = MemoryPool()
        large_buffer = bytearray(2 * 1024 * 1024)  # 2MB

        pool.return_buffer(large_buffer)

        # 不应该被缓存
        assert pool.current_size == 0

    def test_memory_pool_return_buffer_exceeds_max_size(self):
        """测试归还缓冲区超过最大容量"""
        pool = MemoryPool(max_size=100)
        buffer = bytearray(200)

        pool.return_buffer(buffer)

        # 不应该被缓存
        assert pool.current_size == 0

    def test_memory_pool_thread_safety(self):
        """测试内存池线程安全"""
        pool = MemoryPool()
        results = []

        def worker():
            buffer = pool.get_buffer(1024)
            results.append(len(buffer))
            pool.return_buffer(buffer)

        threads = []
        for _ in range(10):
            t = threading.Thread(target=worker)
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        assert len(results) == 10
        assert all(size == 1024 for size in results)

    # ==== SmartCache 测试 ====

    def test_smart_cache_init(self):
        """测试智能缓存初始化"""
        cache = SmartCache(max_size=100, default_ttl=1800)

        assert cache.max_size == 100
        assert cache.default_ttl == 1800
        assert isinstance(cache._data, OrderedDict)
        assert isinstance(cache._access_count, defaultdict)
        assert isinstance(cache._lock, threading.RLock)
        assert isinstance(cache.stats, CacheStats)

    def test_smart_cache_set_and_get_success(self):
        """测试设置和获取缓存成功"""
        cache = SmartCache[str](max_size=10)

        cache.set("key1", "value1")
        result = cache.get("key1")

        assert result == "value1"
        assert cache.stats.hits == 1
        assert cache.stats.misses == 0
        assert cache.stats.items_count == 1

    def test_smart_cache_get_miss(self):
        """测试缓存未命中"""
        cache = SmartCache[str]()

        result = cache.get("nonexistent_key")

        assert result is None
        assert cache.stats.hits == 0
        assert cache.stats.misses == 1

    def test_smart_cache_get_expired(self):
        """测试获取过期缓存"""
        cache = SmartCache[str](default_ttl=0.1)

        cache.set("key1", "value1")
        time.sleep(0.2)  # 等待过期

        result = cache.get("key1")

        assert result is None
        assert cache.stats.misses == 1
        assert "key1" not in cache._data

    def test_smart_cache_set_with_custom_ttl(self):
        """测试设置自定义TTL"""
        cache = SmartCache[str](default_ttl=3600)

        cache.set("key1", "value1", ttl=1800)

        # 验证TTL被正确设置
        item = cache._data["key1"]
        expected_expires = time.time() + 1800
        assert abs(item['expires_at'] - expected_expires) < 1

    def test_smart_cache_update_existing_key(self):
        """测试更新已存在的键"""
        cache = SmartCache[str]()

        cache.set("key1", "value1")
        cache.set("key1", "value2")

        result = cache.get("key1")
        assert result == "value2"
        assert len(cache._data) == 1

    def test_smart_cache_lru_eviction(self):
        """测试LRU驱逐机制"""
        cache = SmartCache[str](max_size=2)

        # 添加三个项
        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")  # 应该驱逐key1

        assert cache.get("key1") is None
        assert cache.get("key2") == "value2"
        assert cache.get("key3") == "value3"
        assert cache.stats.evictions == 1

    def test_smart_cache_lru_with_access_count(self):
        """测试基于访问次数的LRU驱逐"""
        cache = SmartCache[str](max_size=2)

        cache.set("key1", "value1")
        cache.set("key2", "value2")

        # 多次访问key1，增加其访问计数
        cache.get("key1")
        cache.get("key1")
        cache.get("key1")

        # 添加新项，应该驱逐访问次数较少的key2
        cache.set("key3", "value3")

        assert cache.get("key1") == "value1"
        assert cache.get("key2") is None
        assert cache.get("key3") == "value3"

    def test_smart_cache_clear(self):
        """测试清空缓存"""
        cache = SmartCache[str]()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.get("key1")  # 生成一些统计

        cache.clear()

        assert len(cache._data) == 0
        assert len(cache._access_count) == 0
        assert cache.stats.hits == 0
        assert cache.stats.misses == 0

    def test_smart_cache_move_to_end_on_access(self):
        """测试访问时移动到末尾"""
        cache = SmartCache[str]()

        cache.set("key1", "value1")
        cache.set("key2", "value2")
        cache.set("key3", "value3")

        # 访问key1，应该移动到末尾
        cache.get("key1")

        keys = list(cache._data.keys())
        assert keys[-1] == "key1"  # key1应该在最后

    def test_smart_cache_thread_safety(self):
        """测试智能缓存线程安全"""
        cache = SmartCache[int]()
        results = []

        def worker(thread_id):
            for i in range(100):
                key = f"thread_{thread_id}_key_{i}"
                cache.set(key, thread_id * 100 + i)
                value = cache.get(key)
                if value is not None:
                    results.append(value)

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 应该有很多成功的操作
        assert len(results) > 400

    # ==== PrecomputeEngine 测试 ====

    def test_precompute_engine_init(self):
        """测试预计算引擎初始化"""
        engine = PrecomputeEngine(max_workers=2)

        assert isinstance(engine.executor, ThreadPoolExecutor)
        assert isinstance(engine._tasks, set)
        assert isinstance(engine._results, dict)
        assert isinstance(engine._lock, threading.Lock)

    def test_precompute_engine_submit_task_success(self):
        """测试提交预计算任务成功"""
        engine = PrecomputeEngine()

        def test_func(x, y):
            return x + y

        engine.submit_task("add_task", test_func, 10, 20)

        # 等待任务完成
        time.sleep(0.1)

        assert "add_task" in engine._tasks or engine.has_result("add_task")

    def test_precompute_engine_submit_duplicate_task(self):
        """测试提交重复任务"""
        engine = PrecomputeEngine()

        def test_func():
            time.sleep(0.5)
            return "result"

        engine.submit_task("duplicate", test_func)
        initial_task_count = len(engine._tasks)

        # 提交相同ID的任务
        engine.submit_task("duplicate", test_func)

        # 任务数量不应该增加
        assert len(engine._tasks) <= initial_task_count

    def test_precompute_engine_get_result_success(self):
        """测试获取预计算结果成功"""
        engine = PrecomputeEngine()

        def test_func():
            return "computed_result"

        engine.submit_task("test_task", test_func)

        # 等待任务完成
        time.sleep(0.1)
        result = engine.get_result("test_task")

        assert result == "computed_result"

    def test_precompute_engine_get_result_not_found(self):
        """测试获取不存在的结果"""
        engine = PrecomputeEngine()

        result = engine.get_result("nonexistent_task")

        assert result is None

    def test_precompute_engine_has_result(self):
        """测试检查结果是否存在"""
        engine = PrecomputeEngine()

        def test_func():
            return "result"

        assert engine.has_result("test_task") is False

        engine.submit_task("test_task", test_func)
        time.sleep(0.1)

        assert engine.has_result("test_task") is True

    def test_precompute_engine_task_exception(self):
        """测试任务执行异常"""
        engine = PrecomputeEngine()

        def failing_func():
            raise ValueError("Task failed")

        engine.submit_task("failing_task", failing_func)

        # 等待任务完成
        time.sleep(0.1)

        # 任务应该从活动任务中移除
        assert "failing_task" not in engine._tasks
        # 不应该有结果
        assert engine.get_result("failing_task") is None

    def test_precompute_engine_on_task_complete_success(self):
        """测试任务完成回调成功"""
        engine = PrecomputeEngine()

        # 模拟Future对象
        mock_future = Mock()
        mock_future.result.return_value = "success_result"

        engine._on_task_complete("test_task", mock_future)

        assert engine._results["test_task"] == "success_result"
        assert "test_task" not in engine._tasks

    def test_precompute_engine_on_task_complete_exception(self):
        """测试任务完成回调异常"""
        engine = PrecomputeEngine()

        # 模拟失败的Future对象
        mock_future = Mock()
        mock_future.result.side_effect = Exception("Task error")

        # 添加任务ID到任务集合
        engine._tasks.add("failed_task")

        engine._on_task_complete("failed_task", mock_future)

        assert "failed_task" not in engine._results
        assert "failed_task" not in engine._tasks

    # ==== UltraCacheSystem 集成测试 ====

    def test_ultra_cache_system_init_default(self):
        """测试超级缓存系统默认初始化"""
        cache_system = UltraCacheSystem()

        assert isinstance(cache_system.l1_cache, SmartCache)
        assert isinstance(cache_system.l2_cache, SmartCache)
        assert cache_system.l1_cache.max_size == 1000
        assert cache_system.l2_cache.max_size == 5000

    def test_ultra_cache_system_init_custom_config(self):
        """测试自定义配置初始化"""
        config = {
            'l1_size': 500,
            'l2_size': 2000,
            'default_ttl': 1800,
            'enable_disk_cache': False,
            'enable_precompute': False
        }

        cache_system = UltraCacheSystem(config)

        assert cache_system.l1_cache.max_size == 500
        assert cache_system.l2_cache.max_size == 2000
        assert cache_system.l1_cache.default_ttl == 1800

    def test_ultra_cache_system_get_l1_hit(self):
        """测试L1缓存命中"""
        cache_system = UltraCacheSystem()

        cache_system.set("key1", "value1")
        result = cache_system.get("key1")

        assert result == "value1"
        assert cache_system.l1_cache.stats.hits == 2  # set时也会get检查

    def test_ultra_cache_system_get_l2_hit(self):
        """测试L2缓存命中"""
        cache_system = UltraCacheSystem()

        # 直接设置到L2
        cache_system.l2_cache.set("key1", "value1")

        result = cache_system.get("key1")

        assert result == "value1"
        # 应该提升到L1
        assert cache_system.l1_cache.get("key1") == "value1"

    def test_ultra_cache_system_get_miss(self):
        """测试缓存完全未命中"""
        cache_system = UltraCacheSystem()

        result = cache_system.get("nonexistent_key")

        assert result is None

    def test_ultra_cache_system_set_basic(self):
        """测试基本设置操作"""
        cache_system = UltraCacheSystem()

        cache_system.set("key1", "value1", ttl=3600)

        # 应该在L1中找到
        assert cache_system.l1_cache.get("key1") == "value1"

    def test_ultra_cache_system_set_large_value_to_l2(self):
        """测试大值设置到L2"""
        cache_system = UltraCacheSystem()

        # 创建大值（模拟）
        large_value = "x" * 10000

        with patch.object(cache_system, '_estimate_size', return_value=5000):
            cache_system.set("large_key", large_value)

        # 应该直接设置到L2
        assert cache_system.l2_cache.get("large_key") == large_value
        assert cache_system.l1_cache.get("large_key") is None

    def test_ultra_cache_system_delete(self):
        """测试删除缓存项"""
        cache_system = UltraCacheSystem()

        cache_system.set("key1", "value1")
        assert cache_system.get("key1") == "value1"

        result = cache_system.delete("key1")

        assert result is True
        assert cache_system.get("key1") is None

    def test_ultra_cache_system_delete_nonexistent(self):
        """测试删除不存在的缓存项"""
        cache_system = UltraCacheSystem()

        result = cache_system.delete("nonexistent_key")

        assert result is False

    def test_ultra_cache_system_clear(self):
        """测试清空缓存"""
        cache_system = UltraCacheSystem()

        cache_system.set("key1", "value1")
        cache_system.set("key2", "value2")

        cache_system.clear()

        assert cache_system.get("key1") is None
        assert cache_system.get("key2") is None

    def test_ultra_cache_system_get_stats(self):
        """测试获取缓存统计"""
        cache_system = UltraCacheSystem()

        cache_system.set("key1", "value1")
        cache_system.get("key1")
        cache_system.get("nonexistent")

        stats = cache_system.get_stats()

        assert "l1_cache" in stats
        assert "l2_cache" in stats
        assert "system" in stats
        assert stats["l1_cache"]["hits"] > 0

    def test_ultra_cache_system_estimate_size(self):
        """测试值大小估算"""
        cache_system = UltraCacheSystem()

        # 测试不同类型的大小估算
        sizes = [
            cache_system._estimate_size("string"),
            cache_system._estimate_size({"key": "value"}),
            cache_system._estimate_size([1, 2, 3, 4, 5]),
            cache_system._estimate_size(42)
        ]

        assert all(size > 0 for size in sizes)

    # ==== 磁盘缓存测试 ====

    def test_ultra_cache_system_disk_cache_enabled(self, temp_cache_dir):
        """测试启用磁盘缓存"""
        config = {
            'enable_disk_cache': True,
            'disk_cache_dir': str(temp_cache_dir)
        }

        with patch('app.core.ultra_cache_system.PROJECT_ROOT', temp_cache_dir):
            cache_system = UltraCacheSystem(config)

            # 验证磁盘缓存目录被创建
            assert cache_system.disk_cache_dir.exists()

    def test_ultra_cache_system_disk_cache_disabled(self):
        """测试禁用磁盘缓存"""
        config = {'enable_disk_cache': False}

        cache_system = UltraCacheSystem(config)

        assert cache_system.disk_cache_dir is None

    # ==== 预计算功能测试 ====

    def test_ultra_cache_system_precompute_enabled(self):
        """测试启用预计算"""
        config = {'enable_precompute': True}

        cache_system = UltraCacheSystem(config)

        assert cache_system.precompute_engine is not None

    def test_ultra_cache_system_precompute_disabled(self):
        """测试禁用预计算"""
        config = {'enable_precompute': False}

        cache_system = UltraCacheSystem(config)

        assert cache_system.precompute_engine is None

    # ==== 全局函数测试 ====

    def test_get_ultra_cache_singleton(self):
        """测试全局缓存单例"""
        with patch('app.core.ultra_cache_system._ultra_cache', None):
            cache1 = get_ultra_cache()
            cache2 = get_ultra_cache()

            assert cache1 is cache2

    def test_cached_decorator_basic(self):
        """测试缓存装饰器基本功能"""
        call_count = 0

        @cached(ttl=3600)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = expensive_function(1, 2)
        result2 = expensive_function(1, 2)

        assert result1 == 3
        assert result2 == 3
        assert call_count == 1  # 第二次调用应该使用缓存

    def test_cached_decorator_different_args(self):
        """测试装饰器不同参数"""
        call_count = 0

        @cached(ttl=3600)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x * y

        result1 = expensive_function(2, 3)
        result2 = expensive_function(2, 4)

        assert result1 == 6
        assert result2 == 8
        assert call_count == 2  # 不同参数应该调用两次

    def test_cached_decorator_custom_key_func(self):
        """测试自定义键函数"""
        call_count = 0

        def custom_key_func(*args, **kwargs):
            return f"custom_{args[0]}"

        @cached(ttl=3600, key_func=custom_key_func)
        def expensive_function(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = expensive_function(1, 2)
        result2 = expensive_function(1, 3)  # 不同的y，但key相同

        assert result1 == 3
        assert result2 == 3  # 应该返回缓存的结果
        assert call_count == 1

    def test_cached_decorator_ttl_expiration(self):
        """测试装饰器TTL过期"""
        call_count = 0

        @cached(ttl=0.1)  # 很短的TTL
        def expensive_function(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        result1 = expensive_function(5)
        time.sleep(0.2)  # 等待过期
        result2 = expensive_function(5)

        assert result1 == 10
        assert result2 == 10
        assert call_count == 2  # 过期后应该重新调用

    # ==== 边界条件和错误处理测试 ====

    def test_smart_cache_evict_lru_empty(self):
        """测试空缓存驱逐"""
        cache = SmartCache[str]()

        # 不应该抛出异常
        cache._evict_lru()

        assert len(cache._data) == 0

    def test_ultra_cache_system_invalid_config(self):
        """测试无效配置处理"""
        config = {
            'l1_size': -1,  # 无效值
            'l2_size': 0,   # 无效值
        }

        # 应该使用默认值
        cache_system = UltraCacheSystem(config)

        assert cache_system.l1_cache.max_size > 0
        assert cache_system.l2_cache.max_size > 0

    def test_ultra_cache_system_memory_pressure(self):
        """测试内存压力处理"""
        cache_system = UltraCacheSystem()

        # 模拟内存压力
        with patch('app.core.ultra_cache_system.psutil.virtual_memory') as mock_memory:
            mock_memory.return_value.percent = 95  # 高内存使用率

            # 这种情况下系统应该正常工作
            cache_system.set("key1", "value1")
            assert cache_system.get("key1") == "value1"

    def test_precompute_engine_cleanup(self):
        """测试预计算引擎清理"""
        engine = PrecomputeEngine()

        def test_func():
            time.sleep(0.1)
            return "result"

        engine.submit_task("cleanup_test", test_func)

        # 等待任务完成
        time.sleep(0.2)

        # 任务完成后应该从_tasks中移除
        assert "cleanup_test" not in engine._tasks

    def test_ultra_cache_system_concurrent_access(self):
        """测试并发访问"""
        cache_system = UltraCacheSystem()
        results = []

        def worker(thread_id):
            for i in range(50):
                key = f"thread_{thread_id}_key_{i}"
                value = f"thread_{thread_id}_value_{i}"
                cache_system.set(key, value)
                retrieved = cache_system.get(key)
                if retrieved == value:
                    results.append(True)

        threads = []
        for i in range(5):
            t = threading.Thread(target=worker, args=(i,))
            threads.append(t)
            t.start()

        for t in threads:
            t.join()

        # 应该有很多成功的操作
        assert len(results) > 200

    def test_ultra_cache_system_large_dataset(self):
        """测试大数据集处理"""
        cache_system = UltraCacheSystem({'l1_size': 10, 'l2_size': 50})

        # 添加大量数据，测试驱逐机制
        for i in range(100):
            cache_system.set(f"key_{i}", f"value_{i}")

        # 验证缓存仍然工作
        stats = cache_system.get_stats()
        assert stats['l1_cache']['items_count'] <= 10
        assert stats['l2_cache']['items_count'] <= 50

    def test_cache_system_serialization_error_handling(self):
        """测试序列化错误处理"""
        cache_system = UltraCacheSystem({'enable_disk_cache': True})

        # 创建不可序列化的对象
        class UnserializableClass:
            def __reduce__(self):
                raise TypeError("Cannot serialize")

        unserializable_obj = UnserializableClass()

        # 应该优雅处理错误
        cache_system.set("unserializable", unserializable_obj)
        result = cache_system.get("unserializable")

        # 应该仍然能从内存缓存获取
        assert result is unserializable_obj

if __name__ == "__main__":
    pytest.main([__file__, "-v"])