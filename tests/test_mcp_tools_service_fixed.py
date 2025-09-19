"""
MCP工具服务测试
修复版本 - 专门测试 mcp_tools_service.py 模块
"""
import pytest
import json
import os
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, mock_open, MagicMock


class TestMCPToolsServiceFixed:
    """MCP工具服务修复测试"""

    @pytest.fixture
    def temp_config_file(self):
        """临时配置文件"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump({"test": "config"}, f)
            temp_file = f.name
        yield temp_file
        try:
            os.unlink(temp_file)
        except:
            pass

    @pytest.fixture
    def mock_mcp_config(self):
        """模拟MCP配置对象"""
        config = Mock()
        config.to_dict.return_value = {"test": "config"}
        config.proxy = Mock()
        config.proxy.to_dict.return_value = {"enabled": False}
        config.network = Mock()
        config.network.to_dict.return_value = {"timeout": 30}
        config.security = Mock()
        config.security.to_dict.return_value = {"verify_ssl": True}
        config.security.allowed_hosts = []
        config.security.blocked_hosts = []
        config.environment_variables = {"TEST_VAR": "test_value"}
        config.tool_categories = {}
        config.get_proxy_dict.return_value = None
        config.update_category_config = Mock()
        return config

    def test_mcp_config_service_init(self, temp_config_file, mock_mcp_config):
        """测试MCPConfigService初始化"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            assert service.config_file == Path(temp_config_file)
            assert service._config == mock_mcp_config

    def test_load_config_with_existing_file(self, temp_config_file, mock_mcp_config):
        """测试加载现有配置文件"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            service._load_config()

            MockConfig.from_dict.assert_called()

    def test_load_config_without_file(self, mock_mcp_config):
        """测试加载不存在的配置文件"""
        non_existent_file = "/tmp/non_existent_config.json"

        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config'):
                service = MCPConfigService(non_existent_file)
                assert service._config == mock_mcp_config

    def test_save_config(self, temp_config_file, mock_mcp_config):
        """测试保存配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"test": "config"}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_reload_tool_clients'):
                service = MCPConfigService(temp_config_file)
                service._save_config()

                # 验证文件被保存
                assert os.path.exists(temp_config_file)

    def test_get_config(self, temp_config_file, mock_mcp_config):
        """测试获取配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            result = service.get_config()
            assert result == mock_mcp_config

    def test_update_config(self, temp_config_file, mock_mcp_config):
        """测试更新配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"test": "config"}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)

                updates = {"new_key": "new_value"}
                result = service.update_config(updates)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_proxy_config(self, temp_config_file, mock_mcp_config):
        """测试更新代理配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"proxy": {"enabled": False}}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)

                proxy_config = {"enabled": True}
                result = service.update_proxy_config(proxy_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_network_config(self, temp_config_file, mock_mcp_config):
        """测试更新网络配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"network": {"timeout": 30}}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)

                network_config = {"timeout": 60}
                result = service.update_network_config(network_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_security_config(self, temp_config_file, mock_mcp_config):
        """测试更新安全配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"security": {"verify_ssl": True}}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)

                security_config = {"verify_ssl": False}
                result = service.update_security_config(security_config)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_update_environment_variables(self, temp_config_file, mock_mcp_config):
        """测试更新环境变量"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"environment_variables": {}}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                with patch.dict('os.environ', {}, clear=False):
                    service = MCPConfigService(temp_config_file)

                    env_vars = {"NEW_VAR": "new_value"}
                    result = service.update_environment_variables(env_vars)

                    assert result == mock_mcp_config
                    mock_save.assert_called_once()
                    assert os.environ.get("NEW_VAR") == "new_value"

    def test_get_proxy_config(self, temp_config_file, mock_mcp_config):
        """测试获取代理配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            result = service.get_proxy_config()

            mock_mcp_config.proxy.to_dict.assert_called_once()
            assert result == {"enabled": False}

    def test_get_requests_proxy_config(self, temp_config_file, mock_mcp_config):
        """测试获取requests代理配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            result = service.get_requests_proxy_config()

            mock_mcp_config.get_proxy_dict.assert_called_once()
            assert result is None

    def test_is_category_enabled(self, temp_config_file, mock_mcp_config):
        """测试检查分类是否启用"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            # 测试存在的分类
            mock_category = Mock()
            mock_category.enabled = True
            mock_mcp_config.tool_categories = {"github": mock_category}

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)

            # 测试存在的分类
            assert service.is_category_enabled("github") is True

            # 测试不存在的分类（默认启用）
            assert service.is_category_enabled("nonexistent") is True

    def test_is_host_allowed(self, temp_config_file, mock_mcp_config):
        """测试检查主机是否被允许"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)

            # 测试空允许列表（默认允许）
            mock_mcp_config.security.allowed_hosts = []
            assert service.is_host_allowed("example.com") is True

            # 测试有允许列表
            mock_mcp_config.security.allowed_hosts = ["example.com"]
            assert service.is_host_allowed("example.com") is True
            assert service.is_host_allowed("blocked.com") is False

    def test_is_host_blocked(self, temp_config_file, mock_mcp_config):
        """测试检查主机是否被阻止"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)

            mock_mcp_config.security.blocked_hosts = ["blocked.com"]
            assert service.is_host_blocked("blocked.com") is True
            assert service.is_host_blocked("allowed.com") is False

    def test_reset_to_defaults(self, temp_config_file, mock_mcp_config):
        """测试重置为默认配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)
                result = service.reset_to_defaults()

                assert result is not None
                mock_save.assert_called_once()

    def test_export_config(self, temp_config_file, mock_mcp_config):
        """测试导出配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)
            result = service.export_config()

            mock_mcp_config.to_dict.assert_called()
            assert result == {"test": "config"}

    def test_import_config(self, temp_config_file, mock_mcp_config):
        """测试导入配置"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config') as mock_save:
                service = MCPConfigService(temp_config_file)

                config_data = {"imported": "config"}
                result = service.import_config(config_data)

                assert result == mock_mcp_config
                mock_save.assert_called_once()

    def test_reload_tool_clients(self, temp_config_file, mock_mcp_config):
        """测试重新加载工具客户端"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            from app.core.mcp_tools_service import MCPConfigService

            service = MCPConfigService(temp_config_file)

            # 测试重新加载（不应该抛出异常）
            with patch('app.tools.github_tools.reload_github_client_config') as mock_github:
                with patch('app.tools.web_scraping_tools.reload_web_scraping_config') as mock_web:
                    service._reload_tool_clients()
                    mock_github.assert_called_once()
                    mock_web.assert_called_once()

    def test_global_functions(self, temp_config_file, mock_mcp_config):
        """测试全局函数"""
        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config

            import app.core.mcp_tools_service as mcp_module

            # 重置全局变量
            original_service = mcp_module._mcp_config_service
            mcp_module._mcp_config_service = None

            try:
                # 测试初始化全局服务
                result1 = mcp_module.init_mcp_config_service(temp_config_file)
                assert isinstance(result1, mcp_module.MCPConfigService)

                # 测试获取全局服务
                result2 = mcp_module.get_mcp_config_service()
                assert result2 is result1

                # 测试获取配置
                config = mcp_module.get_mcp_config()
                assert config == mock_mcp_config

                # 测试获取代理配置
                proxy_config = mcp_module.get_proxy_for_requests()
                assert proxy_config is None

            finally:
                mcp_module._mcp_config_service = original_service

    def test_thread_safety(self, temp_config_file, mock_mcp_config):
        """测试线程安全性"""
        import threading
        import time

        with patch('app.models.mcp_config.MCPGlobalConfig') as MockConfig:
            MockConfig.from_dict.return_value = mock_mcp_config
            MockConfig.return_value = mock_mcp_config
            mock_mcp_config.to_dict.return_value = {"test": "config"}

            from app.core.mcp_tools_service import MCPConfigService

            with patch.object(MCPConfigService, '_save_config'):
                service = MCPConfigService(temp_config_file)

                results = []
                errors = []

                def thread_worker():
                    try:
                        # 模拟并发操作
                        config = service.get_config()
                        service.update_config({"thread_test": "value"})
                        results.append(config)
                    except Exception as e:
                        errors.append(e)

                # 创建多个线程
                threads = []
                for i in range(5):
                    thread = threading.Thread(target=thread_worker)
                    threads.append(thread)
                    thread.start()

                # 等待所有线程完成
                for thread in threads:
                    thread.join()

                # 验证结果
                assert len(errors) == 0
                assert len(results) == 5
                assert all(result == mock_mcp_config for result in results)