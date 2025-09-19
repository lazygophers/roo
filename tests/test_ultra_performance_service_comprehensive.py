"""
超高性能服务全面测试
目标：将ultra_performance_service.py的测试覆盖率从0%提升到90%+
涵盖资源池、批量处理、性能指标、超高性能YAML服务等核心功能
"""
import pytest
import asyncio
import time
import threading
import tempfile
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from concurrent.futures import Future
import weakref
from collections import deque

# 尝试导入模块
try:
    from app.core.ultra_performance_service import (
        PerformanceMetrics, ResourcePool, BatchProcessor, UltraYAMLService
    )
    ULTRA_PERFORMANCE_SERVICE_AVAILABLE = True
except ImportError as e:
    ULTRA_PERFORMANCE_SERVICE_AVAILABLE = False
    print(f"Ultra performance service import failed: {e}")


@pytest.mark.skipif(not ULTRA_PERFORMANCE_SERVICE_AVAILABLE, reason="Ultra performance service module not available")
class TestUltraPerformanceServiceComprehensive:
    """超高性能服务全面测试套件"""

    # ==== PerformanceMetrics 测试 ====

    def test_performance_metrics_creation_default(self):
        """测试性能指标默认创建"""
        metrics = PerformanceMetrics()

        assert metrics.request_count == 0
        assert metrics.total_processing_time == 0.0
        assert metrics.cache_hits == 0
        assert metrics.cache_misses == 0
        assert metrics.memory_usage_mb == 0.0
        assert metrics.cpu_usage_percent == 0.0

    def test_performance_metrics_creation_with_values(self):
        """测试性能指标自定义值创建"""
        metrics = PerformanceMetrics(
            request_count=100,
            total_processing_time=50.0,
            cache_hits=80,
            cache_misses=20,
            memory_usage_mb=256.5,
            cpu_usage_percent=75.2
        )

        assert metrics.request_count == 100
        assert metrics.total_processing_time == 50.0
        assert metrics.cache_hits == 80
        assert metrics.cache_misses == 20
        assert metrics.memory_usage_mb == 256.5
        assert metrics.cpu_usage_percent == 75.2

    def test_performance_metrics_avg_response_time_zero_requests(self):
        """测试零请求时的平均响应时间"""
        metrics = PerformanceMetrics()
        assert metrics.avg_response_time == 0.0

    def test_performance_metrics_avg_response_time_with_requests(self):
        """测试有请求时的平均响应时间"""
        metrics = PerformanceMetrics(
            request_count=10,
            total_processing_time=5.0
        )
        assert metrics.avg_response_time == 0.5

    def test_performance_metrics_cache_hit_rate_zero_requests(self):
        """测试零缓存请求时的命中率"""
        metrics = PerformanceMetrics()
        assert metrics.cache_hit_rate == 0.0

    def test_performance_metrics_cache_hit_rate_with_requests(self):
        """测试有缓存请求时的命中率"""
        metrics = PerformanceMetrics(
            cache_hits=80,
            cache_misses=20
        )
        assert metrics.cache_hit_rate == 0.8

    def test_performance_metrics_cache_hit_rate_all_hits(self):
        """测试全命中的缓存率"""
        metrics = PerformanceMetrics(
            cache_hits=100,
            cache_misses=0
        )
        assert metrics.cache_hit_rate == 1.0

    def test_performance_metrics_cache_hit_rate_all_misses(self):
        """测试全丢失的缓存率"""
        metrics = PerformanceMetrics(
            cache_hits=0,
            cache_misses=100
        )
        assert metrics.cache_hit_rate == 0.0

    # ==== ResourcePool 测试 ====

    def test_resource_pool_creation(self):
        """测试资源池创建"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=50)

        assert pool.create_func == create_func
        assert pool.max_size == 50
        assert isinstance(pool._pool, deque)
        assert hasattr(pool, '_lock')
        assert pool._created_count == 10  # 预分配的资源数量

        # 验证预分配调用
        assert create_func.call_count == 10

    def test_resource_pool_creation_small_max_size(self):
        """测试小容量资源池创建"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=5)

        assert pool.max_size == 5
        assert pool._created_count == 5  # 预分配数量等于最大容量
        assert create_func.call_count == 5

    def test_resource_pool_get_from_pool(self):
        """测试从池中获取资源"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=20)

        # 获取资源
        resource = pool.get()

        assert resource is not None
        assert len(pool._pool) == 9  # 从10减少到9
        assert create_func.call_count == 10  # 只是预分配调用

    def test_resource_pool_get_create_new(self):
        """测试创建新资源"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=20)

        # 清空池
        pool._pool.clear()

        # 获取资源
        resource = pool.get()

        assert resource is not None
        assert pool._created_count == 11  # 增加计数
        assert create_func.call_count == 11  # 新增一次调用

    def test_resource_pool_get_exceeds_max_size(self):
        """测试超过最大容量时获取资源"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=5)

        # 清空池并设置计数为最大值
        pool._pool.clear()
        pool._created_count = 5

        # 获取资源
        resource = pool.get()

        assert resource is not None
        assert pool._created_count == 5  # 计数不变
        assert create_func.call_count == 6  # 临时创建一个

    def test_resource_pool_put_within_capacity(self):
        """测试在容量内归还资源"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=20)

        # 获取一个资源
        resource = pool.get()
        original_pool_size = len(pool._pool)

        # 归还资源
        pool.put(resource)

        assert len(pool._pool) == original_pool_size + 1

    def test_resource_pool_put_exceeds_capacity(self):
        """测试超过容量时归还资源"""
        create_func = Mock(side_effect=lambda: "resource")
        pool = ResourcePool(create_func=create_func, max_size=10)

        # 添加额外资源直到满容量
        while len(pool._pool) < pool.max_size:
            pool._pool.append("extra_resource")

        original_pool_size = len(pool._pool)

        # 尝试归还资源
        pool.put("overflow_resource")

        # 池大小不应该增加
        assert len(pool._pool) == original_pool_size

    def test_resource_pool_thread_safety(self):
        """测试资源池线程安全性"""
        create_func = Mock(side_effect=lambda: f"resource_{time.time()}")
        pool = ResourcePool(create_func=create_func, max_size=50)

        results = []
        errors = []

        def worker_get_put(worker_id):
            try:
                for i in range(10):
                    # 获取资源
                    resource = pool.get()
                    time.sleep(0.001)  # 模拟使用
                    # 归还资源
                    pool.put(resource)
                    results.append((worker_id, i, "success"))
            except Exception as e:
                errors.append((worker_id, str(e)))

        # 创建多个线程
        threads = []
        for worker_id in range(5):
            thread = threading.Thread(target=worker_get_put, args=(worker_id,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(errors) == 0
        assert len(results) == 50  # 5个工作线程 × 10次操作

    # ==== BatchProcessor 测试 ====

    def test_batch_processor_creation(self):
        """测试批量处理器创建"""
        process_func = Mock(return_value=["result1", "result2"])
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=5,
            max_wait=0.1
        )

        assert processor.process_func == process_func
        assert processor.batch_size == 5
        assert processor.max_wait == 0.1
        assert processor._batch == []
        assert processor._futures == []
        assert hasattr(processor, '_lock')
        assert hasattr(processor, '_timer_thread')
        assert processor._timer_thread.daemon is True

    def test_batch_processor_submit_single_item(self):
        """测试提交单个项目"""
        process_func = Mock(return_value=["result"])
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=5,
            max_wait=0.1
        )

        # 提交项目
        future = processor.submit("item1")

        assert isinstance(future, Future)
        assert len(processor._batch) == 1
        assert len(processor._futures) == 1
        assert processor._batch[0] == "item1"

    def test_batch_processor_submit_batch_size_trigger(self):
        """测试批次大小触发处理"""
        process_func = Mock(return_value=["r1", "r2", "r3"])
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=3,
            max_wait=0.1
        )

        # 提交3个项目触发批次处理
        futures = []
        for i in range(3):
            future = processor.submit(f"item{i}")
            futures.append(future)

        # 等待处理完成
        time.sleep(0.05)

        # 验证批次被清空
        assert len(processor._batch) == 0
        assert len(processor._futures) == 0

    def test_batch_processor_process_batch_empty(self):
        """测试处理空批次"""
        process_func = Mock()
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=5,
            max_wait=0.1
        )

        # 处理空批次
        processor._process_batch()

        # 应该没有调用处理函数
        process_func.assert_not_called()

    def test_batch_processor_execute_batch_success(self):
        """测试批次执行成功"""
        process_func = Mock(return_value=["result1", "result2"])
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=5,
            max_wait=0.1
        )

        # 创建模拟futures
        futures = [Future(), Future()]
        batch = ["item1", "item2"]

        # 执行批次
        processor._execute_batch(batch, futures)

        # 验证结果
        process_func.assert_called_once_with(batch)
        assert futures[0].result() == "result1"
        assert futures[1].result() == "result2"

    def test_batch_processor_execute_batch_exception(self):
        """测试批次执行异常"""
        process_func = Mock(side_effect=Exception("Processing error"))
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=5,
            max_wait=0.1
        )

        # 创建模拟futures
        futures = [Future(), Future()]
        batch = ["item1", "item2"]

        # 执行批次
        processor._execute_batch(batch, futures)

        # 验证异常设置
        assert futures[0].exception() is not None
        assert futures[1].exception() is not None
        assert "Processing error" in str(futures[0].exception())

    def test_batch_processor_timer_processor_integration(self):
        """测试定时器处理器集成"""
        process_func = Mock(return_value=["result"])
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=10,  # 大批次大小，确保定时器触发
            max_wait=0.05   # 短等待时间
        )

        # 提交单个项目
        future = processor.submit("item1")

        # 等待定时器触发
        time.sleep(0.1)

        # 验证批次被处理
        assert len(processor._batch) == 0
        time.sleep(0.05)  # 等待异步处理完成

    # ==== UltraYAMLService 测试 ====

    @pytest.fixture
    def temp_yaml_dir(self):
        """创建临时YAML目录"""
        import tempfile
        import shutil
        temp_dir = tempfile.mkdtemp()
        temp_path = Path(temp_dir)

        # 创建测试YAML文件
        yaml_content1 = {"name": "test1", "version": "1.0"}
        yaml_content2 = {"name": "test2", "version": "2.0"}

        (temp_path / "test1.yaml").write_text(yaml.dump(yaml_content1))
        (temp_path / "test2.yml").write_text(yaml.dump(yaml_content2))
        (temp_path / "subdir").mkdir()
        (temp_path / "subdir" / "test3.yaml").write_text(yaml.dump({"name": "test3"}))

        yield temp_path
        shutil.rmtree(temp_dir, ignore_errors=True)

    def test_ultra_yaml_service_creation(self):
        """测试超高性能YAML服务创建"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            assert service.cache == mock_cache.return_value
            assert isinstance(service.metrics, PerformanceMetrics)
            assert hasattr(service, '_lock')
            assert hasattr(service, 'batch_processor')
            assert hasattr(service, 'yaml_loader_pool')

    def test_ultra_yaml_service_find_yaml_files(self, temp_yaml_dir):
        """测试查找YAML文件"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            # 查找YAML文件
            yaml_files = service.find_yaml_files(temp_yaml_dir)

            # 验证找到的文件
            file_names = [f.name for f in yaml_files]
            assert "test1.yaml" in file_names
            assert "test2.yml" in file_names
            assert "test3.yaml" in file_names
            assert len(yaml_files) == 3

    def test_ultra_yaml_service_find_yaml_files_nonexistent_dir(self):
        """测试查找不存在目录的YAML文件"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            # 查找不存在目录的YAML文件
            yaml_files = service.find_yaml_files(Path("/nonexistent/directory"))

            # 应该返回空列表
            assert yaml_files == []

    def test_ultra_yaml_service_load_yaml_file_cache_hit(self, temp_yaml_dir):
        """测试YAML文件加载缓存命中"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            cached_content = {"cached": "data"}
            mock_cache_instance = Mock()
            mock_cache_instance.get.return_value = cached_content
            mock_cache.return_value = mock_cache_instance

            service = UltraYAMLService()

            yaml_file = temp_yaml_dir / "test1.yaml"
            result = service.load_yaml_file(yaml_file)

            # 验证缓存命中
            assert result == cached_content
            assert service.metrics.cache_hits == 1
            assert service.metrics.cache_misses == 0

    def test_ultra_yaml_service_load_yaml_file_cache_miss(self, temp_yaml_dir):
        """测试YAML文件加载缓存未命中"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache_instance = Mock()
            mock_cache_instance.get.return_value = None  # 缓存未命中
            mock_cache.return_value = mock_cache_instance

            service = UltraYAMLService()

            yaml_file = temp_yaml_dir / "test1.yaml"

            # 模拟批量处理器
            future = Future()
            future.set_result({"name": "test1", "version": "1.0"})
            service.batch_processor.submit = Mock(return_value=future)

            result = service.load_yaml_file(yaml_file)

            # 验证缓存未命中和结果
            assert result == {"name": "test1", "version": "1.0"}
            service.batch_processor.submit.assert_called_once()

    def test_ultra_yaml_service_update_metrics(self):
        """测试更新性能指标"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            with patch('app.core.ultra_performance_service.psutil') as mock_psutil:
                mock_cache.return_value = Mock()
                mock_psutil.Process.return_value.memory_info.return_value.rss = 256 * 1024 * 1024  # 256MB
                mock_psutil.cpu_percent.return_value = 75.5

                service = UltraYAMLService()

                # 更新指标
                service._update_metrics(0.5)

                # 验证指标更新
                assert service.metrics.request_count == 1
                assert service.metrics.total_processing_time == 0.5
                assert service.metrics.memory_usage_mb == 256.0
                assert service.metrics.cpu_usage_percent == 75.5

    def test_ultra_yaml_service_batch_load_yaml_files(self, temp_yaml_dir):
        """测试批量加载YAML文件"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            # 准备文件路径列表
            yaml_files = [
                temp_yaml_dir / "test1.yaml",
                temp_yaml_dir / "test2.yml"
            ]

            # 批量加载
            results = service._batch_load_yaml_files(yaml_files)

            # 验证结果
            assert len(results) == 2
            assert results[0]["name"] == "test1"
            assert results[1]["name"] == "test2"

    def test_ultra_yaml_service_batch_load_yaml_files_with_errors(self, temp_yaml_dir):
        """测试批量加载YAML文件包含错误"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            # 创建无效YAML文件
            invalid_file = temp_yaml_dir / "invalid.yaml"
            invalid_file.write_text("invalid: yaml: content:")

            yaml_files = [
                temp_yaml_dir / "test1.yaml",  # 有效文件
                invalid_file,                  # 无效文件
                temp_yaml_dir / "nonexistent.yaml"  # 不存在的文件
            ]

            # 批量加载
            results = service._batch_load_yaml_files(yaml_files)

            # 验证结果（错误文件返回空字典）
            assert len(results) == 3
            assert results[0]["name"] == "test1"  # 有效文件
            assert results[1] == {}  # 无效文件
            assert results[2] == {}  # 不存在文件

    # ==== 性能和集成测试 ====

    def test_performance_integration_end_to_end(self, temp_yaml_dir):
        """测试端到端性能集成"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache_instance = Mock()
            mock_cache_instance.get.return_value = None  # 模拟缓存未命中
            mock_cache.return_value = mock_cache_instance

            service = UltraYAMLService()

            # 查找文件
            yaml_files = service.find_yaml_files(temp_yaml_dir)

            # 加载每个文件
            results = []
            for yaml_file in yaml_files:
                # 模拟批量处理器返回
                future = Future()
                with open(yaml_file, 'r') as f:
                    content = yaml.safe_load(f)
                future.set_result(content)
                service.batch_processor.submit = Mock(return_value=future)

                result = service.load_yaml_file(yaml_file)
                results.append(result)

            # 验证结果
            assert len(results) == 3
            assert service.metrics.request_count > 0

    def test_concurrent_yaml_service_operations(self, temp_yaml_dir):
        """测试并发YAML服务操作"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            results = []
            errors = []

            def worker_load_files(worker_id):
                try:
                    yaml_files = service.find_yaml_files(temp_yaml_dir)
                    for yaml_file in yaml_files:
                        # 模拟加载
                        future = Future()
                        future.set_result({"worker": worker_id, "file": yaml_file.name})
                        service.batch_processor.submit = Mock(return_value=future)
                        result = service.load_yaml_file(yaml_file)
                        results.append((worker_id, result))
                except Exception as e:
                    errors.append((worker_id, str(e)))

            # 创建多个线程
            threads = []
            for worker_id in range(3):
                thread = threading.Thread(target=worker_load_files, args=(worker_id,))
                threads.append(thread)
                thread.start()

            # 等待所有线程完成
            for thread in threads:
                thread.join()

            # 验证结果
            assert len(errors) == 0
            assert len(results) == 9  # 3个工作线程 × 3个文件

    # ==== 边界条件和错误处理测试 ====

    def test_resource_pool_edge_cases(self):
        """测试资源池边界条件"""
        # 测试最小容量
        create_func = Mock(side_effect=lambda: "resource")
        pool = ResourcePool(create_func=create_func, max_size=1)

        assert pool.max_size == 1
        assert pool._created_count == 1

        # 测试零容量（理论上不应该发生，但要处理）
        pool_zero = ResourcePool(create_func=create_func, max_size=0)
        resource = pool_zero.get()
        assert resource is not None  # 应该创建临时资源

    def test_batch_processor_edge_cases(self):
        """测试批量处理器边界条件"""
        process_func = Mock(return_value=[])

        # 测试最小批次大小
        processor = BatchProcessor(
            process_func=process_func,
            batch_size=1,
            max_wait=0.01
        )

        future = processor.submit("item")
        time.sleep(0.02)  # 等待处理

        # 测试零等待时间
        processor_zero_wait = BatchProcessor(
            process_func=process_func,
            batch_size=10,
            max_wait=0.0
        )

        assert processor_zero_wait.max_wait == 0.0

    def test_ultra_yaml_service_error_handling(self):
        """测试超高性能YAML服务错误处理"""
        with patch('app.core.ultra_performance_service.get_ultra_cache') as mock_cache:
            mock_cache.return_value = Mock()
            service = UltraYAMLService()

            # 测试不存在的文件
            nonexistent_file = Path("/nonexistent/file.yaml")

            future = Future()
            future.set_result({})
            service.batch_processor.submit = Mock(return_value=future)

            result = service.load_yaml_file(nonexistent_file)
            assert result == {}

    def test_performance_metrics_extreme_values(self):
        """测试性能指标极值"""
        # 测试极大值
        metrics = PerformanceMetrics(
            request_count=10**9,
            total_processing_time=10**6,
            cache_hits=10**8,
            cache_misses=10**7
        )

        assert metrics.avg_response_time == 0.001
        assert abs(metrics.cache_hit_rate - 0.909) < 0.01  # 约90.9%

        # 测试极小值
        metrics_small = PerformanceMetrics(
            request_count=1,
            total_processing_time=0.0001
        )

        assert metrics_small.avg_response_time == 0.0001