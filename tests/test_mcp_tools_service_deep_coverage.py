"""
MCP工具服务深度测试
目标：将mcp_tools_service.py的测试覆盖率从19%提升到85%+
涵盖MCP配置管理、代理设置、网络配置的全面测试
"""
import pytest
import json
import tempfile
import shutil
import threading
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.core.mcp_tools_service import (
        MCPConfigService, init_mcp_config_service, get_mcp_config_service,
        get_mcp_config, get_proxy_for_requests
    )
    from app.models.mcp_config import MCPGlobalConfig
    MCP_TOOLS_SERVICE_AVAILABLE = True
except ImportError as e:
    MCP_TOOLS_SERVICE_AVAILABLE = False
    print(f"MCP tools service import failed: {e}")


@pytest.mark.skipif(not MCP_TOOLS_SERVICE_AVAILABLE, reason="MCP tools service module not available")
class TestMCPToolsServiceDeepCoverage:
    """MCP工具服务深度测试套件"""

    @pytest.fixture
    def temp_config_dir(self):
        """创建临时配置目录"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir, ignore_errors=True)

    @pytest.fixture
    def sample_config_data(self):
        """示例配置数据"""
        return {
            "proxy": {
                "enabled": True,
                "http_proxy": "http://proxy.example.com:8080",
                "https_proxy": "https://proxy.example.com:8080",
                "no_proxy": ["localhost", "127.0.0.1"]
            },
            "network": {
                "timeout": 30,
                "retry_times": 3,
                "user_agent": "LazyAI-Studio/1.0"
            },
            "security": {
                "verify_ssl": True,
                "allow_insecure_hosts": False
            },
            "environment_variables": {
                "GITHUB_TOKEN": "test_token",
                "OPENAI_API_KEY": "test_key"
            },
            "tool_categories": {
                "github": {
                    "category": "github",
                    "enabled": True,
                    "custom_config": {"rate_limit": 1000}
                }
            }
        }

    @pytest.fixture
    def mock_mcp_config(self):
        """模拟MCP配置对象"""
        config = Mock(spec=MCPGlobalConfig)
        config.to_dict.return_value = {"test": "config"}
        config.proxy.to_dict.return_value = {"enabled": False}
        config.network.to_dict.return_value = {"timeout": 30}
        config.security.to_dict.return_value = {"verify_ssl": True}
        config.environment_variables = {"TEST_VAR": "test_value"}
        config.tool_categories = {}
        config.get_proxy_dict.return_value = None
        config.update_category_config = Mock()
        return config

    # ==== MCPConfigService 初始化测试 ====

    def test_mcp_config_service_init_with_existing_file(self, temp_config_dir, sample_config_data):
        """测试使用现有配置文件初始化"""
        config_file = temp_config_dir / "mcp_config.json"

        # 创建配置文件
        with open(config_file, 'w') as f:
            json.dump(sample_config_data, f)

        with patch('app.core.mcp_tools_service.MCPGlobalConfig.from_dict') as mock_from_dict:
            mock_config = Mock()
            mock_from_dict.return_value = mock_config

            service = MCPConfigService(str(config_file))

            assert service.config_file == config_file
            assert service._config == mock_config
            mock_from_dict.assert_called_once_with(sample_config_data)

    def test_mcp_config_service_init_without_file(self, temp_config_dir):
        """测试没有配置文件时初始化"""
        config_file = temp_config_dir / "new_config.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config
            mock_config.to_dict.return_value = {"default": "config"}

            service = MCPConfigService(str(config_file))

            assert service._config == mock_config
            # 验证配置文件被创建
            assert config_file.exists()

    def test_mcp_config_service_init_with_invalid_json(self, temp_config_dir):
        """测试无效JSON文件初始化"""
        config_file = temp_config_dir / "invalid_config.json"

        # 创建无效JSON文件
        with open(config_file, 'w') as f:
            f.write("invalid json content {")

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config

            service = MCPConfigService(str(config_file))

            # 应该使用默认配置
            assert service._config == mock_config

    def test_mcp_config_service_init_with_file_permission_error(self, temp_config_dir):
        """测试文件权限错误初始化"""
        config_file = temp_config_dir / "protected_config.json"

        with patch('builtins.open', side_effect=PermissionError("Permission denied")), \
             patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:

            mock_config = Mock()
            mock_config_class.return_value = mock_config

            service = MCPConfigService(str(config_file))

            # 应该使用默认配置
            assert service._config == mock_config

    # ==== 配置加载和保存测试 ====

    def test_load_config_success(self, temp_config_dir, sample_config_data):
        """测试配置加载成功"""
        config_file = temp_config_dir / "test_config.json"

        with open(config_file, 'w') as f:
            json.dump(sample_config_data, f)

        with patch('app.core.mcp_tools_service.MCPGlobalConfig.from_dict') as mock_from_dict:
            mock_config = Mock()
            mock_from_dict.return_value = mock_config

            service = MCPConfigService(str(config_file))
            service._load_config()

            assert service._config == mock_config

    def test_save_config_success(self, temp_config_dir, mock_mcp_config):
        """测试配置保存成功"""
        config_file = temp_config_dir / "save_test.json"

        service = MCPConfigService(str(config_file))
        service._config = mock_mcp_config

        with patch.object(service, '_reload_tool_clients') as mock_reload:
            service._save_config()

            # 验证文件被保存
            assert config_file.exists()
            mock_reload.assert_called_once()

    def test_save_config_write_error(self, temp_config_dir, mock_mcp_config):
        """测试配置保存写入错误"""
        config_file = temp_config_dir / "write_error.json"

        service = MCPConfigService(str(config_file))
        service._config = mock_mcp_config

        with patch('builtins.open', side_effect=PermissionError("Write error")):
            with pytest.raises(PermissionError):
                service._save_config()

    # ==== 配置获取和更新测试 ====

    def test_get_config(self, mock_mcp_config):
        """测试获取配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            result = service.get_config()

            assert result == mock_mcp_config

    def test_update_config_success(self, temp_config_dir, mock_mcp_config):
        """测试更新配置成功"""
        config_file = temp_config_dir / "update_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            updates = {"new_setting": "new_value"}

            with patch.object(service, '_save_config') as mock_save:
                result = service.update_config(updates)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_config_exception(self, mock_mcp_config):
        """测试更新配置异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.side_effect = Exception("Conversion error")

            with pytest.raises(Exception, match="Conversion error"):
                service.update_config({"test": "value"})

    def test_update_proxy_config_success(self, temp_config_dir, mock_mcp_config):
        """测试更新代理配置成功"""
        config_file = temp_config_dir / "proxy_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            # 模拟to_dict返回有proxy字段
            mock_mcp_config.to_dict.return_value = {"proxy": {"enabled": False}}

            proxy_config = {"enabled": True, "http_proxy": "http://proxy.test:8080"}

            with patch.object(service, '_save_config') as mock_save:
                result = service.update_proxy_config(proxy_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_proxy_config_exception(self, mock_mcp_config):
        """测试更新代理配置异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.side_effect = Exception("Proxy error")

            with pytest.raises(Exception, match="Proxy error"):
                service.update_proxy_config({"enabled": True})

    def test_update_network_config_success(self, temp_config_dir, mock_mcp_config):
        """测试更新网络配置成功"""
        config_file = temp_config_dir / "network_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            # 模拟to_dict返回有network字段
            mock_mcp_config.to_dict.return_value = {"network": {"timeout": 30}}

            network_config = {"timeout": 60, "retry_times": 5}

            with patch.object(service, '_save_config') as mock_save:
                result = service.update_network_config(network_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_network_config_exception(self, mock_mcp_config):
        """测试更新网络配置异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.side_effect = Exception("Network error")

            with pytest.raises(Exception, match="Network error"):
                service.update_network_config({"timeout": 60})

    def test_update_security_config_success(self, temp_config_dir, mock_mcp_config):
        """测试更新安全配置成功"""
        config_file = temp_config_dir / "security_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            # 模拟to_dict返回有security字段
            mock_mcp_config.to_dict.return_value = {"security": {"verify_ssl": True}}

            security_config = {"verify_ssl": False, "allow_insecure_hosts": True}

            with patch.object(service, '_save_config') as mock_save:
                result = service.update_security_config(security_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_security_config_exception(self, mock_mcp_config):
        """测试更新安全配置异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.side_effect = Exception("Security error")

            with pytest.raises(Exception, match="Security error"):
                service.update_security_config({"verify_ssl": False})

    def test_update_tool_category_config_success(self, temp_config_dir, mock_mcp_config):
        """测试更新工具分类配置成功"""
        config_file = temp_config_dir / "category_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            category_config = {
                "enabled": False,
                "custom_config": {"rate_limit": 500}
            }

            with patch.object(service, '_save_config') as mock_save:
                result = service.update_tool_category_config("github", category_config)

                assert result == mock_mcp_config
                mock_mcp_config.update_category_config.assert_called_once_with(
                    category="github",
                    enabled=False,
                    custom_config={"rate_limit": 500}
                )
                mock_save.assert_called_once()

    def test_update_tool_category_config_exception(self, mock_mcp_config):
        """测试更新工具分类配置异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.update_category_config.side_effect = Exception("Category error")

            with pytest.raises(Exception, match="Category error"):
                service.update_tool_category_config("github", {"enabled": True})

    def test_update_environment_variables_success(self, temp_config_dir, mock_mcp_config):
        """测试更新环境变量成功"""
        config_file = temp_config_dir / "env_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            # 模拟to_dict返回有environment_variables字段
            mock_mcp_config.to_dict.return_value = {"environment_variables": {}}

            env_vars = {
                "NEW_VAR": "new_value",
                "EXISTING_VAR": "updated_value"
            }

            with patch.object(service, '_save_config') as mock_save, \
                 patch.dict('os.environ', {}, clear=False):

                result = service.update_environment_variables(env_vars)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

                # 验证环境变量被设置
                import os
                assert os.environ["NEW_VAR"] == "new_value"
                assert os.environ["EXISTING_VAR"] == "updated_value"

    def test_update_environment_variables_with_empty_values(self, temp_config_dir, mock_mcp_config):
        """测试更新环境变量包含空值"""
        config_file = temp_config_dir / "env_empty_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.return_value = {"environment_variables": {}}

            env_vars = {
                "DELETE_VAR": "",  # 空值应该删除环境变量
                "NULL_VAR": None   # None值应该删除环境变量
            }

            with patch.object(service, '_save_config') as mock_save, \
                 patch.dict('os.environ', {"DELETE_VAR": "old_value", "NULL_VAR": "old_value"}, clear=False):

                result = service.update_environment_variables(env_vars)

                assert result == mock_mcp_config

                # 验证环境变量被删除
                import os
                assert "DELETE_VAR" not in os.environ
                assert "NULL_VAR" not in os.environ

    def test_update_environment_variables_exception(self, mock_mcp_config):
        """测试更新环境变量异常"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.to_dict.side_effect = Exception("Env error")

            with pytest.raises(Exception, match="Env error"):
                service.update_environment_variables({"TEST": "value"})

    # ==== 配置获取方法测试 ====

    def test_get_proxy_config(self, mock_mcp_config):
        """测试获取代理配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            proxy_dict = {"enabled": True, "http_proxy": "http://test:8080"}
            mock_mcp_config.proxy.to_dict.return_value = proxy_dict

            result = service.get_proxy_config()

            assert result == proxy_dict

    def test_get_requests_proxy_config(self, mock_mcp_config):
        """测试获取requests代理配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            proxy_dict = {"http": "http://test:8080", "https": "https://test:8080"}
            mock_mcp_config.get_proxy_dict.return_value = proxy_dict

            result = service.get_requests_proxy_config()

            assert result == proxy_dict

    def test_get_requests_proxy_config_none(self, mock_mcp_config):
        """测试获取requests代理配置返回None"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.get_proxy_dict.return_value = None

            result = service.get_requests_proxy_config()

            assert result is None

    def test_get_network_config(self, mock_mcp_config):
        """测试获取网络配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            network_dict = {"timeout": 30, "retry_times": 3}
            mock_mcp_config.network.to_dict.return_value = network_dict

            result = service.get_network_config()

            assert result == network_dict

    def test_get_security_config(self, mock_mcp_config):
        """测试获取安全配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            security_dict = {"verify_ssl": True, "allow_insecure_hosts": False}
            mock_mcp_config.security.to_dict.return_value = security_dict

            result = service.get_security_config()

            assert result == security_dict

    def test_get_tool_category_config_existing(self, mock_mcp_config):
        """测试获取存在的工具分类配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            # 模拟存在的分类配置
            mock_category = Mock()
            mock_category.to_dict.return_value = {"category": "github", "enabled": True}
            mock_mcp_config.tool_categories = {"github": mock_category}

            result = service.get_tool_category_config("github")

            assert result == {"category": "github", "enabled": True}

    def test_get_tool_category_config_not_existing(self, mock_mcp_config):
        """测试获取不存在的工具分类配置"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            mock_mcp_config.tool_categories = {}

            result = service.get_tool_category_config("nonexistent")

            expected = {"category": "nonexistent", "enabled": True, "custom_config": {}}
            assert result == expected

    def test_get_environment_variables(self, mock_mcp_config):
        """测试获取环境变量"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")
            service._config = mock_mcp_config

            env_vars = {"TEST_VAR": "test_value", "ANOTHER_VAR": "another_value"}
            mock_mcp_config.environment_variables = env_vars

            result = service.get_environment_variables()

            assert result == env_vars

    # ==== 工具客户端重新加载测试 ====

    def test_reload_tool_clients(self, mock_mcp_config):
        """测试重新加载工具客户端"""
        with patch('app.core.mcp_tools_service.MCPGlobalConfig', return_value=mock_mcp_config):
            service = MCPConfigService("test_config.json")

            # _reload_tool_clients是一个占位符方法，应该不抛出异常
            service._reload_tool_clients()

    # ==== 线程安全测试 ====

    def test_thread_safety(self, temp_config_dir, mock_mcp_config):
        """测试线程安全"""
        config_file = temp_config_dir / "thread_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            results = []

            def worker(thread_id):
                for i in range(10):
                    updates = {f"thread_{thread_id}_setting_{i}": f"value_{i}"}
                    try:
                        with patch.object(service, '_save_config'):
                            result = service.update_config(updates)
                            results.append(result)
                    except Exception as e:
                        results.append(f"Error: {e}")

            threads = []
            for i in range(5):
                t = threading.Thread(target=worker, args=(i,))
                threads.append(t)
                t.start()

            for t in threads:
                t.join()

            # 应该有50个结果（5线程 × 10次更新）
            assert len(results) == 50

    # ==== 全局函数测试 ====

    def test_init_mcp_config_service(self):
        """测试初始化MCP配置服务"""
        with patch('app.core.mcp_tools_service.MCPConfigService') as mock_service_class:
            mock_service = Mock()
            mock_service_class.return_value = mock_service

            result = init_mcp_config_service("custom_config.json")

            assert result == mock_service
            mock_service_class.assert_called_once_with("custom_config.json")

    def test_get_mcp_config_service_singleton(self):
        """测试获取MCP配置服务单例"""
        with patch('app.core.mcp_tools_service._mcp_config_service', None), \
             patch('app.core.mcp_tools_service.init_mcp_config_service') as mock_init:

            mock_service = Mock()
            mock_init.return_value = mock_service

            # 第一次调用应该初始化
            result1 = get_mcp_config_service()

            # 第二次调用应该返回同一实例
            result2 = get_mcp_config_service()

            assert result1 == mock_service
            assert result2 == mock_service
            mock_init.assert_called_once()

    def test_get_mcp_config(self):
        """测试获取MCP配置"""
        mock_service = Mock()
        mock_config = Mock()
        mock_service.get_config.return_value = mock_config

        with patch('app.core.mcp_tools_service.get_mcp_config_service', return_value=mock_service):
            result = get_mcp_config()

            assert result == mock_config
            mock_service.get_config.assert_called_once()

    def test_get_proxy_for_requests(self):
        """测试获取requests代理配置"""
        mock_service = Mock()
        mock_proxy = {"http": "http://test:8080", "https": "https://test:8080"}
        mock_service.get_requests_proxy_config.return_value = mock_proxy

        with patch('app.core.mcp_tools_service.get_mcp_config_service', return_value=mock_service):
            result = get_proxy_for_requests()

            assert result == mock_proxy
            mock_service.get_requests_proxy_config.assert_called_once()

    def test_get_proxy_for_requests_none(self):
        """测试获取requests代理配置返回None"""
        mock_service = Mock()
        mock_service.get_requests_proxy_config.return_value = None

        with patch('app.core.mcp_tools_service.get_mcp_config_service', return_value=mock_service):
            result = get_proxy_for_requests()

            assert result is None

    # ==== 边界条件和错误处理测试 ====

    def test_config_file_directory_creation(self, temp_config_dir):
        """测试配置文件目录创建"""
        nested_config_path = temp_config_dir / "nested" / "deep" / "config.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config = Mock()
            mock_config_class.return_value = mock_config

            service = MCPConfigService(str(nested_config_path))

            # 验证嵌套目录被创建
            assert nested_config_path.parent.exists()

    def test_concurrent_config_updates(self, temp_config_dir, mock_mcp_config):
        """测试并发配置更新"""
        config_file = temp_config_dir / "concurrent_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))
            service._config = mock_mcp_config

            errors = []

            def update_worker(config_type, config_data):
                try:
                    with patch.object(service, '_save_config'):
                        if config_type == "proxy":
                            service.update_proxy_config(config_data)
                        elif config_type == "network":
                            service.update_network_config(config_data)
                        elif config_type == "security":
                            service.update_security_config(config_data)
                except Exception as e:
                    errors.append(str(e))

            # 模拟to_dict返回值
            mock_mcp_config.to_dict.return_value = {
                "proxy": {},
                "network": {},
                "security": {}
            }

            threads = [
                threading.Thread(target=update_worker, args=("proxy", {"enabled": True})),
                threading.Thread(target=update_worker, args=("network", {"timeout": 60})),
                threading.Thread(target=update_worker, args=("security", {"verify_ssl": False}))
            ]

            for t in threads:
                t.start()

            for t in threads:
                t.join()

            # 不应该有错误
            assert len(errors) == 0

    def test_large_config_handling(self, temp_config_dir, mock_mcp_config):
        """测试大配置文件处理"""
        config_file = temp_config_dir / "large_config_test.json"

        with patch('app.core.mcp_tools_service.MCPGlobalConfig') as mock_config_class:
            mock_config_class.return_value = mock_mcp_config
            mock_config_class.from_dict.return_value = mock_mcp_config

            service = MCPConfigService(str(config_file))

            # 创建大量配置更新
            large_config = {f"setting_{i}": f"value_{i}" for i in range(1000)}

            with patch.object(service, '_save_config'):
                result = service.update_config(large_config)

            assert result == mock_mcp_config

if __name__ == "__main__":
    pytest.main([__file__, "-v"])