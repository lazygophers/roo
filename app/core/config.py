import os
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent.parent

# 模型文件目录
MODELS_DIR = PROJECT_ROOT / "resources" / "models"

# Hooks 文件目录
HOOKS_DIR = PROJECT_ROOT / "resources" / "hooks"

# API 配置
API_PREFIX = "/api"
API_VERSION = "v1"

# 服务器配置
HOST = "0.0.0.0"
PORT = 8000
DEBUG = os.getenv("DEBUG", "false").lower() == "true"

# 日志配置
LOG_LEVEL = "INFO" if not DEBUG else "DEBUG"

# 文件工具安全配置
FILE_TOOLS_CONFIG = {
    # 可读取的目录列表 - 默认允许项目根目录及其子目录
    "readable_directories": [
        str(PROJECT_ROOT),  # 项目根目录
        str(Path.home()),   # 用户主目录
        "/tmp",             # 临时目录
        # 可以添加其他允许读取的目录
    ],
    
    # 可编辑的目录列表 - 默认允许项目根目录及其子目录和临时目录
    "writable_directories": [
        str(PROJECT_ROOT),  # 项目根目录
        str(Path.home() / "Documents"),  # 用户文档目录
        "/tmp",             # 临时目录
        # 可以添加其他允许编辑的目录
    ],
    
    # 可删除的目录列表 - 默认只允许项目目录和临时目录
    "deletable_directories": [
        str(PROJECT_ROOT / "temp"),      # 项目临时目录
        str(PROJECT_ROOT / "data" / "temp"),  # 数据临时目录
        "/tmp",                         # 系统临时目录
        str(Path.home() / "Downloads"),  # 用户下载目录
        # 可以添加其他允许删除的目录
    ],
    
    # 禁止访问的目录列表 - 系统重要目录
    "forbidden_directories": [
        "/etc",
        "/bin", 
        "/sbin",
        "/usr/bin",
        "/usr/sbin",
        "/System",  # macOS系统目录
        "/private/etc",  # macOS系统配置
        str(Path.home() / ".ssh"),  # SSH密钥目录
        # 可以添加其他需要保护的目录
    ],
    
    # 最大文件大小限制（字节）
    "max_file_size": 100 * 1024 * 1024,  # 100MB
    
    # 最大读取行数限制
    "max_read_lines": 10000,
    
    # 是否启用严格模式（严格模式下只能访问明确允许的目录）
    "strict_mode": False,
}