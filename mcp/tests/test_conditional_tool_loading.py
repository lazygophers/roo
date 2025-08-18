# -*- coding: utf-8 -*-
"""
此模块专用于测试 MCP 服务器中工具的条件化加载逻辑。

核心测试目标：
1.  验证在非 Docker 环境下，文件操作工具能够被正确加载。
2.  验证在 Docker 环境下，文件操作工具会被禁用，以确保系统的安全性和隔离性。

通过 `unittest.mock.patch`，我们可以在不依赖真实 Docker 环境的情况下，
精确模拟这两种场景，从而实现高效、可靠的单元测试。
"""

import unittest
from unittest.mock import patch

# 假设的未来模块路径，我们将在后续步骤中实现它
from src.server import get_tools
from src.tools.file_operations import file_operation_tools

class TestConditionalToolLoading(unittest.TestCase):
    """测试 MCP 服务器根据环境动态加载工具集的行为。"""

    @patch('src.server.is_running_in_docker', return_value=False)
    def test_load_file_tools_in_local_env(self, mock_is_docker):
        """
        测试场景：在本地环境（非 Docker）中。
        预期行为：文件操作工具集应该被成功加载。
        """
        loaded_tools = get_tools()
        
        # 断言：确认模拟函数被调用
        mock_is_docker.assert_called_once()
        
        # 断言：检查 file_operation_tools 中的所有工具是否都已加载
        file_tool_names = file_operation_tools.keys()
        for tool_name in file_tool_names:
            self.assertIn(tool_name, loaded_tools,
                          f"工具 '{tool_name}' 未能在本地环境中加载。")
        
        # 验证 memory 工具也已加载
        self.assertIn("save_core_memory", loaded_tools)
        
        print("\n[PASS] 本地环境测试：文件操作工具已成功加载。")

    @patch('src.server.is_running_in_docker', return_value=True)
    def test_disable_file_tools_in_docker_env(self, mock_is_docker):
        """
        测试场景：在模拟的 Docker 环境中。
        预期行为：文件操作工具集不应该被加载。
        """
        loaded_tools = get_tools()
        
        # 断言：确认模拟函数被调用
        mock_is_docker.assert_called_once()
        
        # 断言：检查 file_operation_tools 中的任何工具都不应存在于加载的工具中
        file_tool_names = file_operation_tools.keys()
        for tool_name in file_tool_names:
            self.assertNotIn(tool_name, loaded_tools,
                             f"工具 '{tool_name}' 在 Docker 环境中被错误地加载了。")
            
        print("\n[PASS] Docker 环境测试：文件操作工具已按预期被禁用。")

if __name__ == '__main__':
    unittest.main()