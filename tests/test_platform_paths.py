#!/usr/bin/env python3
"""测试跨平台路径生成"""

import platform
import sys

# 保存原始平台信息
original_system = platform.system

def test_platform_paths():
    """测试不同平台的路径生成"""
    
    # 测试函数
    def get_platform_specific_path(extension_id: str, system: str) -> str:
        """根据操作系统返回正确的VS Code扩展配置路径"""
        if system == "Darwin":  # macOS
            return f"~/Library/Application Support/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
        elif system == "Windows":
            return f"~/AppData/Roaming/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
        elif system == "Linux":
            return f"~/.config/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
        else:
            # 默认返回 Linux 路径
            return f"~/.config/Code/User/globalStorage/{extension_id}/settings/custom_modes.yaml"
    
    extensions = [
        "rooveterinaryinc.roo-cline",
        "rooveterinaryinc.roo-code-nightly",
        "kilocode.kilo-code"
    ]
    
    platforms = ["Darwin", "Windows", "Linux"]
    
    print("=" * 80)
    print("跨平台路径测试结果")
    print("=" * 80)
    
    for plat in platforms:
        print(f"\n{plat} 平台路径:")
        print("-" * 40)
        for ext in extensions:
            path = get_platform_specific_path(ext, plat)
            print(f"  {ext}:")
            print(f"    {path}")
    
    print("\n" + "=" * 80)
    print("当前系统检测:")
    current_system = platform.system()
    print(f"  操作系统: {current_system}")
    print(f"  平台信息: {platform.platform()}")
    print("=" * 80)

if __name__ == "__main__":
    test_platform_paths()