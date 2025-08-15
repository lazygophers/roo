#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
高性能 Searx 实例可用性检测器

这个脚本会检测所有配置的 Searx 实例的可用性，并自动更新 config.yaml 文件。
支持并发检测、进度显示、配置备份等高级功能。

使用方法:
    python scripts/check_searx.py
    python scripts/check_searx.py --concurrent 20 --timeout 5
    python scripts/check_searx.py --dry-run --verbose
"""

import argparse
import json
import logging
import os
import shutil
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import requests
import yaml
from requests.adapters import HTTPAdapter
from tqdm import tqdm
from urllib3.util.retry import Retry

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.tools.searx import search

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 默认 Searx 实例列表
DEFAULT_HOST_LIST = [
    "https://so.ddns-ip.net",
    "https://seek.nuer.cc",
    "https://sousuo.emoe.top",
    "https://searxng.ctbot.tech",
    "https://searxng.jethrowang.cn",
    "https://aimonitor.xiaocg.xyz",
    "https://search.fatgpt.cn",
    "https://searxng.narasaka.dev",
    "https://search.songai.icu",
    "https://searxng.ddaodan.cc",
    "https://sg.goyor.com",
    "https://search.infinityf4p.com",
    "https://s.yyy.earth",
    "https://ss.helper5210.top",
    "https://search.no-code.gdn",
    "https://search.corrently.cloud",
    "https://search.jakespeed.org",
    "https://searxng.fly2me.cc",
    "https://searxng.stardream.online",
    "https://search.lucathomas.de",
    "https://negativenull.com",
    "https://searx.yorgis.net",
    "https://search.mixel.cloud",
    "https://xng.huidaolasa.xyz",
    "https://searxng-pilot.jitera.app",
    "https://searxng.vyro.ai",
    "https://martechia.online",
    "https://search.chgr.cc",
    "https://websearch.nwt.de",
    "https://s.arson.pw",
    "https://s.gottsnack.net",
    "https://srx.zebralab.io",
    "https://search.the8.dev",
    "https://search.nicolasallemand.com",
    "https://search.aidoing.de",
    "https://search.f-ws.net",
    "https://searxng.ai.flagbit.de",
    "https://searxng.asudox.dev",
    "https://searxng.k3s.koski.co",
    "https://mfood3.hongquantrader.com",
    "https://searx.privhub.space",
    "https://search.muellers-software.org",
    "https://searxng.lmdr.io",
    "https://uwg8swww0o0cw4osg4okc4gs.phytertek.com",
    "https://searxng.sbbz-ilvesheim.de",
    "https://search.soulrend.net",
    "https://searxng.core.sciling.com",
    "https://searxng.springbokagency.com",
    "https://seachx.lunarfire.home64.de",
    "https://cari.aeenquran.id",
    "https://searx.work",
]


@dataclass
class CheckResult:
    """Searx 实例检测结果"""
    host: str
    is_alive: bool
    response_time: Optional[float] = None
    error: Optional[str] = None
    timestamp: datetime = None

    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()


class SearxChecker:
    """Searx 实例可用性检测器"""
    
    def __init__(
        self,
        timeout: int = 10,
        max_workers: int = 10,
        test_query: str = "test",
        verbose: bool = False
    ):
        """
        初始化检测器
        
        Args:
            timeout: 请求超时时间（秒）
            max_workers: 最大并发数
            test_query: 测试查询字符串
            verbose: 是否输出详细日志
        """
        self.timeout = timeout
        self.max_workers = max_workers
        self.test_query = test_query
        self.verbose = verbose
        
        # 配置日志级别
        if verbose:
            logger.setLevel(logging.DEBUG)
            logging.getLogger().setLevel(logging.DEBUG)
        
        # 创建 HTTP 会话
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """创建配置好的 HTTP 会话"""
        session = requests.Session()
        
        # 配置重试策略
        retry_strategy = Retry(
            total=2,
            backoff_factor=0.3,
            status_forcelist=[408, 429, 500, 502, 503, 504],
        )
        
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)
        
        # 设置请求头
        session.headers.update({
            "User-Agent": "Searx-Checker/1.0",
            "Accept": "application/json",
        })
        
        return session
    
    def check_host_direct(self, host: str) -> CheckResult:
        """
        直接检测单个 Searx 实例（使用 HTTP 请求）
        
        Args:
            host: Searx 实例 URL
            
        Returns:
            检测结果
        """
        logger.debug(f"直接检测 {host}")
        start_time = time.time()
        
        try:
            # 构建搜索 URL
            search_url = f"{host.rstrip('/')}/search"
            params = {
                "q": self.test_query,
                "format": "json",
                "categories": "general",
                "pageno": 1
            }
            
            # 发送请求
            response = self.session.get(
                search_url,
                params=params,
                timeout=self.timeout
            )
            
            # 检查响应
            response.raise_for_status()
            data = response.json()
            
            # 验证响应格式
            if isinstance(data, dict) and "results" in data:
                response_time = time.time() - start_time
                logger.debug(f"✅ {host} 可用 (响应时间: {response_time:.2f}s)")
                return CheckResult(
                    host=host,
                    is_alive=True,
                    response_time=response_time
                )
            else:
                logger.debug(f"❌ {host} 响应格式无效")
                return CheckResult(
                    host=host,
                    is_alive=False,
                    error="Invalid response format"
                )
                
        except requests.exceptions.Timeout:
            logger.debug(f"⏱️ {host} 超时")
            return CheckResult(
                host=host,
                is_alive=False,
                error=f"Timeout after {self.timeout}s"
            )
        except requests.exceptions.ConnectionError as e:
            logger.debug(f"🔌 {host} 连接失败: {e}")
            return CheckResult(
                host=host,
                is_alive=False,
                error=f"Connection error: {str(e)[:50]}"
            )
        except Exception as e:
            logger.debug(f"❌ {host} 检测失败: {e}")
            return CheckResult(
                host=host,
                is_alive=False,
                error=f"Error: {str(e)[:50]}"
            )
    
    def check_host_via_tool(self, host: str) -> CheckResult:
        """
        通过项目的 searx 工具检测单个实例
        
        Args:
            host: Searx 实例 URL
            
        Returns:
            检测结果
        """
        logger.debug(f"通过工具检测 {host}")
        start_time = time.time()
        
        # 临时修改配置以测试特定 host
        import src.config as config_module
        original_hosts = config_module._config.searx.searx_hosts if config_module._config else []
        
        try:
            # 设置单个 host 进行测试
            if config_module._config:
                config_module._config.searx.searx_hosts = [host]
            
            # 使用 search 函数进行测试
            results = search(
                query=self.test_query,
                categories="general",
                page=1
            )
            
            # 检查结果
            if results and isinstance(results, dict) and "results" in results:
                response_time = time.time() - start_time
                logger.debug(f"✅ {host} 可用 (响应时间: {response_time:.2f}s)")
                return CheckResult(
                    host=host,
                    is_alive=True,
                    response_time=response_time
                )
            else:
                logger.debug(f"❌ {host} 无有效结果")
                return CheckResult(
                    host=host,
                    is_alive=False,
                    error="No valid results"
                )
                
        except Exception as e:
            logger.debug(f"❌ {host} 检测失败: {e}")
            return CheckResult(
                host=host,
                is_alive=False,
                error=f"Error: {str(e)[:50]}"
            )
        finally:
            # 恢复原始配置
            if config_module._config:
                config_module._config.searx.searx_hosts = original_hosts
    
    def check_hosts_concurrent(
        self,
        hosts: List[str],
        use_tool: bool = False
    ) -> List[CheckResult]:
        """
        并发检测多个 Searx 实例
        
        Args:
            hosts: Searx 实例 URL 列表
            use_tool: 是否使用项目工具进行检测
            
        Returns:
            检测结果列表
        """
        results = []
        check_func = self.check_host_via_tool if use_tool else self.check_host_direct
        
        # 使用线程池并发检测
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # 提交所有任务
            future_to_host = {
                executor.submit(check_func, host): host
                for host in hosts
            }
            
            # 使用 tqdm 显示进度
            with tqdm(
                total=len(hosts),
                desc="检测 Searx 实例",
                unit="host",
                ncols=100,
                bar_format='{l_bar}{bar}| {n_fmt}/{total_fmt} [{elapsed}<{remaining}]'
            ) as pbar:
                for future in as_completed(future_to_host):
                    result = future.result()
                    results.append(result)
                    
                    # 更新进度条
                    status = "✅" if result.is_alive else "❌"
                    pbar.set_postfix_str(f"{status} {result.host[:30]}")
                    pbar.update(1)
        
        return results
    
    def print_summary(self, results: List[CheckResult]):
        """
        打印检测结果摘要
        
        Args:
            results: 检测结果列表
        """
        alive_results = [r for r in results if r.is_alive]
        dead_results = [r for r in results if not r.is_alive]
        
        print("\n" + "="*60)
        print("📊 检测结果统计")
        print("="*60)
        
        print(f"\n✅ 可用实例 ({len(alive_results)}/{len(results)}):")
        if alive_results:
            # 按响应时间排序
            alive_results.sort(key=lambda x: x.response_time or float('inf'))
            for i, result in enumerate(alive_results[:10], 1):
                time_str = f"{result.response_time:.2f}s" if result.response_time else "N/A"
                print(f"  {i:2d}. {result.host:40} [{time_str}]")
            if len(alive_results) > 10:
                print(f"  ... 还有 {len(alive_results) - 10} 个可用实例")
        else:
            print("  （无可用实例）")
        
        print(f"\n❌ 不可用实例 ({len(dead_results)}/{len(results)}):")
        if dead_results:
            for i, result in enumerate(dead_results[:5], 1):
                error = result.error or "Unknown error"
                print(f"  {i:2d}. {result.host:40} - {error}")
            if len(dead_results) > 5:
                print(f"  ... 还有 {len(dead_results) - 5} 个不可用实例")
        else:
            print("  （所有实例都可用）")
        
        # 性能统计
        if alive_results:
            avg_time = sum(r.response_time for r in alive_results if r.response_time) / len(alive_results)
            min_time = min(r.response_time for r in alive_results if r.response_time)
            max_time = max(r.response_time for r in alive_results if r.response_time)
            
            print(f"\n⚡ 性能统计:")
            print(f"  平均响应时间: {avg_time:.2f}s")
            print(f"  最快响应时间: {min_time:.2f}s")
            print(f"  最慢响应时间: {max_time:.2f}s")
        
        print("\n" + "="*60)


class ConfigManager:
    """配置文件管理器"""
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = Path(config_path)
        self.backup_dir = Path("backups")
    
    def backup_config(self) -> Optional[Path]:
        """
        备份当前配置文件
        
        Returns:
            备份文件路径，如果备份失败则返回 None
        """
        if not self.config_path.exists():
            logger.warning(f"配置文件 {self.config_path} 不存在，跳过备份")
            return None
        
        # 创建备份目录
        self.backup_dir.mkdir(exist_ok=True)
        
        # 生成备份文件名
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = self.backup_dir / f"config_{timestamp}.yaml"
        
        try:
            shutil.copy2(self.config_path, backup_path)
            logger.info(f"✅ 配置文件已备份到: {backup_path}")
            return backup_path
        except Exception as e:
            logger.error(f"❌ 备份配置文件失败: {e}")
            return None
    
    def load_config(self) -> Dict:
        """
        加载配置文件
        
        Returns:
            配置字典
        """
        if not self.config_path.exists():
            logger.warning(f"配置文件 {self.config_path} 不存在，将创建新文件")
            return {}
        
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f) or {}
                logger.debug(f"成功加载配置文件: {self.config_path}")
                return config
        except Exception as e:
            logger.error(f"加载配置文件失败: {e}")
            raise
    
    def update_searx_hosts(
        self,
        hosts: List[str],
        dry_run: bool = False
    ) -> bool:
        """
        更新配置文件中的 searx_hosts 字段
        
        Args:
            hosts: 新的 Searx 实例列表
            dry_run: 是否为模拟运行（不实际写入文件）
            
        Returns:
            是否更新成功
        """
        try:
            # 加载现有配置
            config = self.load_config()
            
            # 更新 searx_hosts 字段
            old_hosts = config.get('searx_hosts', [])
            config['searx_hosts'] = hosts
            
            # 显示变更
            logger.info(f"📝 配置更新:")
            logger.info(f"  原有 {len(old_hosts)} 个实例")
            logger.info(f"  更新为 {len(hosts)} 个可用实例")
            
            if dry_run:
                logger.info("🔍 模拟运行模式，不会实际更新配置文件")
                print("\n将要写入的配置:")
                print(yaml.dump({'searx_hosts': hosts}, allow_unicode=True, default_flow_style=False)[:500])
                return True
            
            # 备份原配置
            backup_path = self.backup_config()
            
            # 写入新配置（原子操作）
            temp_path = self.config_path.with_suffix('.tmp')
            try:
                with open(temp_path, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        config,
                        f,
                        allow_unicode=True,
                        default_flow_style=False,
                        sort_keys=False
                    )
                
                # 原子替换
                temp_path.replace(self.config_path)
                logger.info(f"✅ 配置文件已更新: {self.config_path}")
                return True
                
            except Exception as e:
                # 清理临时文件
                if temp_path.exists():
                    temp_path.unlink()
                raise e
                
        except Exception as e:
            logger.error(f"❌ 更新配置文件失败: {e}")
            return False


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="检测 Searx 实例可用性并更新配置",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s                           # 使用默认参数检测
  %(prog)s --concurrent 20           # 使用 20 个并发连接
  %(prog)s --timeout 5               # 设置 5 秒超时
  %(prog)s --dry-run                 # 模拟运行，不更新配置
  %(prog)s --use-tool                # 使用项目 searx 工具检测
  %(prog)s --host-file hosts.txt     # 从文件读取主机列表
  %(prog)s --verbose                 # 显示详细日志
        """
    )
    
    parser.add_argument(
        '-c', '--concurrent',
        type=int,
        default=10,
        help='最大并发数 (默认: 10)'
    )
    
    parser.add_argument(
        '-t', '--timeout',
        type=int,
        default=10,
        help='请求超时时间(秒) (默认: 10)'
    )
    
    parser.add_argument(
        '-q', '--query',
        type=str,
        default='test',
        help='测试查询字符串 (默认: test)'
    )
    
    parser.add_argument(
        '--config',
        type=str,
        default='config.yaml',
        help='配置文件路径 (默认: config.yaml)'
    )
    
    parser.add_argument(
        '--host-file',
        type=str,
        help='从文件读取主机列表（每行一个 URL）'
    )
    
    parser.add_argument(
        '--use-tool',
        action='store_true',
        help='使用项目的 searx 工具进行检测'
    )
    
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='模拟运行，不实际更新配置文件'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='显示详细日志'
    )
    
    parser.add_argument(
        '--no-update',
        action='store_true',
        help='只检测，不更新配置文件'
    )
    
    return parser.parse_args()


def load_hosts_from_file(file_path: str) -> List[str]:
    """
    从文件加载主机列表
    
    Args:
        file_path: 文件路径
        
    Returns:
        主机 URL 列表
    """
    hosts = []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    hosts.append(line)
        logger.info(f"从 {file_path} 加载了 {len(hosts)} 个主机")
        return hosts
    except Exception as e:
        logger.error(f"加载主机文件失败: {e}")
        return []


def main():
    """主函数"""
    # 解析参数
    args = parse_arguments()
    
    # 打印启动信息
    print("🚀 Searx 实例可用性检测器")
    print("="*60)
    print(f"配置: 并发={args.concurrent}, 超时={args.timeout}s, 查询='{args.query}'")
    print(f"模式: {'项目工具' if args.use_tool else '直接HTTP'}")
    if args.dry_run:
        print("⚠️  模拟运行模式 - 不会修改配置文件")
    print("="*60)
    
    # 加载主机列表
    if args.host_file:
        hosts = load_hosts_from_file(args.host_file)
        if not hosts:
            logger.error("无法从文件加载主机列表")
            return 1
    else:
        hosts = DEFAULT_HOST_LIST
    
    print(f"\n📋 准备检测 {len(hosts)} 个 Searx 实例...")
    
    # 创建检测器
    checker = SearxChecker(
        timeout=args.timeout,
        max_workers=args.concurrent,
        test_query=args.query,
        verbose=args.verbose
    )
    
    # 执行检测
    start_time = time.time()
    results = checker.check_hosts_concurrent(hosts, use_tool=args.use_tool)
    elapsed_time = time.time() - start_time
    
    # 打印统计
    checker.print_summary(results)
    print(f"⏱️  总耗时: {elapsed_time:.2f} 秒")
    
    # 获取可用的主机
    alive_hosts = [r.host for r in results if r.is_alive]
    
    if not alive_hosts:
        logger.error("❌ 没有找到可用的 Searx 实例")
        return 1
    
    # 更新配置文件
    if not args.no_update:
        config_manager = ConfigManager(args.config)
        success = config_manager.update_searx_hosts(alive_hosts, dry_run=args.dry_run)
        
        if not success and not args.dry_run:
            logger.error("❌ 更新配置文件失败")
            return 1
    else:
        print("\n跳过配置文件更新（--no-update）")
    
    print(f"\n✨ 检测完成！找到 {len(alive_hosts)} 个可用实例")
    return 0


if __name__ == "__main__":
    sys.exit(main())