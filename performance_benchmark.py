#!/usr/bin/env python3
"""
性能基准测试脚本
比较优化前后的性能差异
"""

import time
import psutil
import asyncio
from pathlib import Path
from typing import Dict, List, Any
import statistics

# 导入原始服务
from app.core.database_service import DatabaseService, init_database_service
from app.core.yaml_service import YAMLService

# 导入优化服务
from app.core.database_service_lite import LiteDatabaseService, init_lite_database_service
from app.core.yaml_service_optimized import OptimizedYAMLService

class PerformanceBenchmark:
    """性能基准测试"""
    
    def __init__(self):
        self.results = {}
        self.process = psutil.Process()
    
    def measure_memory_usage(self) -> float:
        """测量内存使用量（MB）"""
        memory_info = self.process.memory_info()
        return memory_info.rss / 1024 / 1024
    
    def measure_cpu_usage(self) -> float:
        """测量CPU使用率"""
        return self.process.cpu_percent(interval=0.1)
    
    def benchmark_function(self, name: str, func, *args, **kwargs) -> Dict[str, Any]:
        """基准测试函数"""
        print(f"\n🔍 测试 {name}...")
        
        # 测量前状态
        start_memory = self.measure_memory_usage()
        start_time = time.time()
        
        # 执行函数
        try:
            result = func(*args, **kwargs)
            success = True
            error = None
        except Exception as e:
            result = None
            success = False
            error = str(e)
        
        # 测量后状态
        end_time = time.time()
        end_memory = self.measure_memory_usage()
        cpu_usage = self.measure_cpu_usage()
        
        execution_time = end_time - start_time
        memory_usage = end_memory - start_memory
        
        benchmark_result = {
            'name': name,
            'success': success,
            'error': error,
            'execution_time': execution_time,
            'memory_usage': memory_usage,
            'cpu_usage': cpu_usage,
            'start_memory': start_memory,
            'end_memory': end_memory
        }
        
        print(f"  ⏱️  执行时间: {execution_time:.3f}s")
        print(f"  🧠 内存使用: {memory_usage:+.2f}MB")
        print(f"  💻 CPU使用: {cpu_usage:.1f}%")
        print(f"  ✅ 状态: {'成功' if success else '失败'}")
        
        if error:
            print(f"  ❌ 错误: {error}")
        
        return benchmark_result
    
    def test_original_services(self) -> Dict[str, Any]:
        """测试原始服务性能"""
        print("\n" + "="*60)
        print("🚀 测试原始服务性能")
        print("="*60)
        
        results = {}
        
        # 测试原始数据库服务初始化
        def init_original_db():
            db_service = DatabaseService()
            # 添加扫描配置
            db_service.add_scan_config(
                name="models",
                path="resources/models",
                patterns=['*.yaml', '*.yml'],
                watch=True
            )
            # 执行同步
            db_service.sync_all()
            return db_service
        
        results['db_init'] = self.benchmark_function(
            "原始数据库服务初始化", 
            init_original_db
        )
        
        # 测试原始YAML服务
        def load_original_models():
            return YAMLService.load_all_models()
        
        results['yaml_load'] = self.benchmark_function(
            "原始YAML服务加载所有模型",
            load_original_models
        )
        
        return results
    
    def test_optimized_services(self) -> Dict[str, Any]:
        """测试优化服务性能"""
        print("\n" + "="*60)
        print("⚡ 测试优化服务性能")
        print("="*60)
        
        results = {}
        
        # 测试优化数据库服务初始化
        def init_optimized_db():
            return init_lite_database_service()
        
        results['db_init'] = self.benchmark_function(
            "优化数据库服务初始化",
            init_optimized_db
        )
        
        # 测试优化YAML服务
        def load_optimized_models():
            yaml_service = OptimizedYAMLService()
            return yaml_service.load_all_models()
        
        results['yaml_load'] = self.benchmark_function(
            "优化YAML服务加载所有模型",
            load_optimized_models
        )
        
        # 测试缓存性能
        def test_cache_performance():
            db_service = init_lite_database_service()
            # 第一次加载
            first_load = db_service.get_models_data()
            # 第二次加载（应该使用缓存）
            second_load = db_service.get_models_data()
            return len(first_load), len(second_load)
        
        results['cache_test'] = self.benchmark_function(
            "缓存性能测试",
            test_cache_performance
        )
        
        return results
    
    def multiple_runs_test(self, func, name: str, runs: int = 5) -> Dict[str, Any]:
        """多次运行测试以获得更准确的结果"""
        print(f"\n📊 多次运行测试: {name} ({runs}次)")
        
        execution_times = []
        memory_usages = []
        
        for i in range(runs):
            print(f"  运行 {i+1}/{runs}...")
            result = self.benchmark_function(f"{name}_run_{i+1}", func)
            if result['success']:
                execution_times.append(result['execution_time'])
                memory_usages.append(result['memory_usage'])
        
        if execution_times:
            return {
                'avg_execution_time': statistics.mean(execution_times),
                'min_execution_time': min(execution_times),
                'max_execution_time': max(execution_times),
                'avg_memory_usage': statistics.mean(memory_usages),
                'execution_times': execution_times,
                'memory_usages': memory_usages,
                'runs': len(execution_times)
            }
        else:
            return {'error': 'All runs failed'}
    
    def generate_comparison_report(self, original_results: Dict, optimized_results: Dict):
        """生成对比报告"""
        print("\n" + "="*60)
        print("📊 性能对比报告")
        print("="*60)
        
        comparisons = []
        
        for key in original_results:
            if key in optimized_results:
                orig = original_results[key]
                opt = optimized_results[key]
                
                if orig['success'] and opt['success']:
                    time_improvement = (orig['execution_time'] - opt['execution_time']) / orig['execution_time'] * 100
                    memory_improvement = (orig['memory_usage'] - opt['memory_usage']) / abs(orig['memory_usage']) * 100 if orig['memory_usage'] != 0 else 0
                    
                    comparison = {
                        'test': key,
                        'original_time': orig['execution_time'],
                        'optimized_time': opt['execution_time'],
                        'time_improvement': time_improvement,
                        'original_memory': orig['memory_usage'],
                        'optimized_memory': opt['memory_usage'],
                        'memory_improvement': memory_improvement
                    }
                    
                    comparisons.append(comparison)
                    
                    print(f"\n🔍 {key}:")
                    print(f"  ⏱️  执行时间: {orig['execution_time']:.3f}s → {opt['execution_time']:.3f}s ({time_improvement:+.1f}%)")
                    print(f"  🧠 内存使用: {orig['memory_usage']:+.2f}MB → {opt['memory_usage']:+.2f}MB ({memory_improvement:+.1f}%)")
        
        # 总体性能提升
        if comparisons:
            avg_time_improvement = statistics.mean([c['time_improvement'] for c in comparisons])
            avg_memory_improvement = statistics.mean([c['memory_improvement'] for c in comparisons])
            
            print(f"\n🎉 总体性能提升:")
            print(f"  ⚡ 平均执行时间提升: {avg_time_improvement:+.1f}%")
            print(f"  💾 平均内存使用改善: {avg_memory_improvement:+.1f}%")
        
        return comparisons
    
    def run_full_benchmark(self):
        """运行完整基准测试"""
        print("🚀 LazyAI Studio 性能基准测试")
        print("="*60)
        print("测试原始服务 vs 优化服务的性能差异")
        
        # 测试原始服务
        original_results = self.test_original_services()
        
        # 测试优化服务
        optimized_results = self.test_optimized_services()
        
        # 生成对比报告
        comparisons = self.generate_comparison_report(original_results, optimized_results)
        
        # 保存结果到文件
        import json
        report = {
            'timestamp': time.time(),
            'original_results': original_results,
            'optimized_results': optimized_results,
            'comparisons': comparisons
        }
        
        with open('performance_report.json', 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, default=str)
        
        print(f"\n📄 详细报告已保存到: performance_report.json")
        
        return report


def main():
    """主函数"""
    benchmark = PerformanceBenchmark()
    benchmark.run_full_benchmark()


if __name__ == "__main__":
    main()