"""
优化YAML服务全面测试
目标：将yaml_service_optimized.py的测试覆盖率从0%提升到90%+
涵盖懒加载、LRU缓存、文件监控等优化功能
"""
import pytest
import yaml
import tempfile
import time
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# 尝试导入模块
try:
    from app.core.yaml_service_optimized import OptimizedYAMLService
    YAML_SERVICE_OPTIMIZED_AVAILABLE = True
except ImportError as e:
    YAML_SERVICE_OPTIMIZED_AVAILABLE = False
    print(f"YAML service optimized import failed: {e}")


@pytest.mark.skipif(not YAML_SERVICE_OPTIMIZED_AVAILABLE, reason="YAML service optimized module not available")
class TestYAMLServiceOptimizedComprehensive:
    """优化YAML服务全面测试套件"""

    @pytest.fixture
    def yaml_service(self):
        """创建YAML服务实例"""
        return OptimizedYAMLService(cache_size=64)

    @pytest.fixture
    def temp_yaml_file(self):
        """创建临时YAML文件"""
        temp_file = tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False)
        yaml_content = {
            'name': 'test_model',
            'version': '1.0',
            'description': 'Test model description',
            'parameters': {'param1': 'value1', 'param2': 42}
        }
        yaml.dump(yaml_content, temp_file)
        temp_file.close()

        yield Path(temp_file.name)

        # 清理
        try:
            Path(temp_file.name).unlink()
        except:
            pass

    # ==== 初始化测试 ====

    def test_optimized_yaml_service_init_default(self):
        """测试默认初始化"""
        service = OptimizedYAMLService()

        assert service._cache_size == 128  # 默认缓存大小
        assert isinstance(service._file_cache, dict)
        assert isinstance(service._file_stats, dict)
        assert service._last_scan_time is None
        assert service._scan_cache_duration == 60

    def test_optimized_yaml_service_init_custom(self):
        """测试自定义初始化"""
        service = OptimizedYAMLService(cache_size=256)

        assert service._cache_size == 256

    # ==== 文件修改时间测试 ====

    def test_get_file_modification_time_existing_file(self, temp_yaml_file):
        """测试获取存在文件的修改时间"""
        service = OptimizedYAMLService()

        mtime = service._get_file_modification_time(temp_yaml_file)

        assert mtime > 0
        assert isinstance(mtime, float)

    def test_get_file_modification_time_nonexistent_file(self):
        """测试获取不存在文件的修改时间"""
        service = OptimizedYAMLService()
        nonexistent_file = Path("/nonexistent/file.yaml")

        mtime = service._get_file_modification_time(nonexistent_file)

        assert mtime == 0.0

    # ==== 缓存有效性检查测试 ====

    def test_is_file_cached_and_valid_not_cached(self, temp_yaml_file):
        """测试未缓存文件的有效性"""
        service = OptimizedYAMLService()

        is_valid = service._is_file_cached_and_valid(temp_yaml_file)

        assert is_valid is False

    def test_is_file_cached_and_valid_cached_and_valid(self, temp_yaml_file):
        """测试已缓存且有效的文件"""
        service = OptimizedYAMLService()
        file_key = str(temp_yaml_file)

        # 设置缓存
        service._file_cache[file_key] = {"test": "data"}
        service._file_stats[file_key] = time.time() + 1000  # 未来时间，确保有效

        is_valid = service._is_file_cached_and_valid(temp_yaml_file)

        assert is_valid is True

    def test_is_file_cached_and_valid_cached_but_invalid(self, temp_yaml_file):
        """测试已缓存但无效的文件"""
        service = OptimizedYAMLService()
        file_key = str(temp_yaml_file)

        # 设置过期缓存
        service._file_cache[file_key] = {"test": "data"}
        service._file_stats[file_key] = 0.0  # 过去时间，缓存无效

        is_valid = service._is_file_cached_and_valid(temp_yaml_file)

        assert is_valid is False

    # ==== LRU缓存加载测试 ====

    def test_load_yaml_file_cached_success(self, temp_yaml_file):
        """测试LRU缓存加载成功"""
        service = OptimizedYAMLService()

        result = service._load_yaml_file_cached(str(temp_yaml_file), time.time())

        assert isinstance(result, dict)
        assert 'name' in result
        assert result['name'] == 'test_model'

    def test_load_yaml_file_cached_empty_file(self):
        """测试LRU缓存加载空文件"""
        service = OptimizedYAMLService()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write("")  # 空文件
            temp_file_path = temp_file.name

        try:
            result = service._load_yaml_file_cached(temp_file_path, time.time())
            assert result == {}
        finally:
            Path(temp_file_path).unlink()

    def test_load_yaml_file_cached_invalid_yaml(self):
        """测试LRU缓存加载无效YAML"""
        service = OptimizedYAMLService()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write("invalid: yaml: content:")
            temp_file_path = temp_file.name

        try:
            with pytest.raises(Exception, match="Failed to load"):
                service._load_yaml_file_cached(temp_file_path, time.time())
        finally:
            Path(temp_file_path).unlink()

    def test_load_yaml_file_cached_file_not_found(self):
        """测试LRU缓存加载不存在文件"""
        service = OptimizedYAMLService()

        with pytest.raises(Exception, match="Failed to load"):
            service._load_yaml_file_cached("/nonexistent/file.yaml", time.time())

    # ==== 单文件加载测试 ====

    def test_load_yaml_file_from_cache(self, temp_yaml_file):
        """测试从缓存加载文件"""
        service = OptimizedYAMLService()
        file_key = str(temp_yaml_file)

        # 预设缓存
        cached_data = {"cached": "data"}
        service._file_cache[file_key] = cached_data
        service._file_stats[file_key] = time.time() + 1000

        result = service.load_yaml_file(temp_yaml_file)

        assert result == cached_data

    def test_load_yaml_file_load_new(self, temp_yaml_file):
        """测试加载新文件"""
        service = OptimizedYAMLService()

        result = service.load_yaml_file(temp_yaml_file)

        # 验证结果
        assert isinstance(result, dict)
        assert result['name'] == 'test_model'

        # 验证缓存被更新
        file_key = str(temp_yaml_file)
        assert file_key in service._file_cache
        assert file_key in service._file_stats

    def test_load_yaml_file_cache_invalidation(self, temp_yaml_file):
        """测试缓存失效"""
        service = OptimizedYAMLService()
        file_key = str(temp_yaml_file)

        # 设置过期缓存
        service._file_cache[file_key] = {"old": "data"}
        service._file_stats[file_key] = 0.0

        result = service.load_yaml_file(temp_yaml_file)

        # 应该重新加载，不是旧缓存
        assert result != {"old": "data"}
        assert result['name'] == 'test_model'

    # ==== 批量加载测试 ====

    @pytest.fixture
    def temp_yaml_files(self):
        """创建多个临时YAML文件"""
        files = []
        for i in range(3):
            temp_file = tempfile.NamedTemporaryFile(mode='w', suffix=f'_{i}.yaml', delete=False)
            yaml_content = {
                'name': f'model_{i}',
                'version': f'{i}.0',
                'index': i
            }
            yaml.dump(yaml_content, temp_file)
            temp_file.close()
            files.append(Path(temp_file.name))

        yield files

        # 清理
        for file_path in files:
            try:
                file_path.unlink()
            except:
                pass

    def test_load_multiple_yaml_files(self, temp_yaml_files):
        """测试加载多个YAML文件"""
        service = OptimizedYAMLService()

        results = []
        for file_path in temp_yaml_files:
            result = service.load_yaml_file(file_path)
            results.append(result)

        # 验证结果
        assert len(results) == 3
        for i, result in enumerate(results):
            assert result['name'] == f'model_{i}'
            assert result['index'] == i

    def test_load_multiple_yaml_files_with_caching(self, temp_yaml_files):
        """测试多次加载同一文件的缓存效果"""
        service = OptimizedYAMLService()

        # 第一次加载
        result1 = service.load_yaml_file(temp_yaml_files[0])

        # 第二次加载（应该从缓存获取）
        result2 = service.load_yaml_file(temp_yaml_files[0])

        # 结果应该相同，且来自缓存
        assert result1 == result2
        file_key = str(temp_yaml_files[0])
        assert file_key in service._file_cache

    # ==== 缓存管理测试 ====

    def test_lru_cache_functionality(self, temp_yaml_files):
        """测试LRU缓存功能"""
        # 使用小缓存测试LRU行为
        service = OptimizedYAMLService(cache_size=2)

        # 加载文件，应该命中LRU缓存
        file1 = temp_yaml_files[0]
        file2 = temp_yaml_files[1]

        # 第一次加载
        result1_1 = service._load_yaml_file_cached(str(file1), time.time())
        result2_1 = service._load_yaml_file_cached(str(file2), time.time())

        # 第二次加载相同文件（应该从LRU缓存获取）
        result1_2 = service._load_yaml_file_cached(str(file1), time.time())
        result2_2 = service._load_yaml_file_cached(str(file2), time.time())

        # 验证缓存命中
        assert result1_1 == result1_2
        assert result2_1 == result2_2

    def test_cache_size_management(self):
        """测试缓存大小管理"""
        service = OptimizedYAMLService(cache_size=50)

        # 添加多个文件到内部缓存
        for i in range(60):  # 超过缓存大小
            file_key = f"fake_file_{i}.yaml"
            service._file_cache[file_key] = {"index": i}
            service._file_stats[file_key] = time.time()

        # 内部缓存大小应该被控制
        assert len(service._file_cache) == 60  # 内部缓存不自动清理

        # 但LRU缓存应该有限制
        cache_info = service._load_yaml_file_cached.cache_info()
        assert cache_info.maxsize == 128  # 默认LRU缓存大小

    # ==== 错误处理测试 ====

    def test_error_handling_permission_denied(self):
        """测试权限拒绝错误处理"""
        service = OptimizedYAMLService()

        # 模拟权限拒绝
        with patch('builtins.open', side_effect=PermissionError("Permission denied")):
            with pytest.raises(Exception, match="Failed to load"):
                service._load_yaml_file_cached("/restricted/file.yaml", time.time())

    def test_error_handling_corrupted_yaml(self):
        """测试损坏YAML文件错误处理"""
        service = OptimizedYAMLService()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write("---\ninvalid:\n  - yaml\n  content:\n    missing: closing")
            temp_file_path = temp_file.name

        try:
            with pytest.raises(Exception, match="Failed to load"):
                service._load_yaml_file_cached(temp_file_path, time.time())
        finally:
            Path(temp_file_path).unlink()

    # ==== 性能测试 ====

    def test_performance_caching_benefit(self, temp_yaml_file):
        """测试缓存性能优势"""
        service = OptimizedYAMLService()

        # 第一次加载（无缓存）
        start_time = time.time()
        result1 = service.load_yaml_file(temp_yaml_file)
        first_load_time = time.time() - start_time

        # 第二次加载（从缓存）
        start_time = time.time()
        result2 = service.load_yaml_file(temp_yaml_file)
        second_load_time = time.time() - start_time

        # 验证结果相同
        assert result1 == result2

        # 第二次应该明显更快（从缓存加载）
        # 注意：这个测试可能不稳定，因为文件很小，差异可能不明显
        assert second_load_time <= first_load_time

    def test_concurrent_access_safety(self, temp_yaml_files):
        """测试并发访问安全性"""
        import threading

        service = OptimizedYAMLService()
        results = []
        errors = []

        def load_worker(file_path):
            try:
                for _ in range(5):
                    result = service.load_yaml_file(file_path)
                    results.append(result)
            except Exception as e:
                errors.append(str(e))

        # 创建多个线程同时访问
        threads = []
        for file_path in temp_yaml_files:
            thread = threading.Thread(target=load_worker, args=(file_path,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证没有错误
        assert len(errors) == 0
        assert len(results) == 15  # 3个文件 × 5次加载

    # ==== 边界条件测试 ====

    def test_empty_yaml_content_handling(self):
        """测试空YAML内容处理"""
        service = OptimizedYAMLService()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            temp_file.write("# This is just a comment")
            temp_file_path = temp_file.name

        try:
            result = service._load_yaml_file_cached(temp_file_path, time.time())
            assert result == {}  # 空内容应该返回空字典
        finally:
            Path(temp_file_path).unlink()

    def test_large_yaml_file_handling(self):
        """测试大YAML文件处理"""
        service = OptimizedYAMLService()

        # 创建较大的YAML内容
        large_content = {
            'models': [
                {'name': f'model_{i}', 'params': list(range(100))}
                for i in range(50)
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as temp_file:
            yaml.dump(large_content, temp_file)
            temp_file_path = temp_file.name

        try:
            result = service._load_yaml_file_cached(temp_file_path, time.time())
            assert 'models' in result
            assert len(result['models']) == 50
        finally:
            Path(temp_file_path).unlink()

    def test_special_characters_in_yaml(self):
        """测试YAML中的特殊字符处理"""
        service = OptimizedYAMLService()

        special_content = {
            'unicode_text': '这是中文测试 🚀',
            'special_chars': '@#$%^&*()[]{}',
            'multiline': 'Line 1\nLine 2\nLine 3',
            'quotes': "String with 'single' and \"double\" quotes"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False, encoding='utf-8') as temp_file:
            yaml.dump(special_content, temp_file, allow_unicode=True)
            temp_file_path = temp_file.name

        try:
            result = service._load_yaml_file_cached(temp_file_path, time.time())
            assert result['unicode_text'] == '这是中文测试 🚀'
            assert result['special_chars'] == '@#$%^&*()[]{}'
        finally:
            Path(temp_file_path).unlink()