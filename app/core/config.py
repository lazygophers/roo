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

# 环境配置
ENVIRONMENT = os.getenv("ENVIRONMENT", "local")  # local 或 remote

# 基于环境的服务器配置
if ENVIRONMENT == "remote":
    # 远端环境配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # 远端环境 CORS 配置 - 默认允许所有域名
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*").split(",") if os.getenv("CORS_ORIGINS", "*") != "*" else ["*"]
    CORS_ALLOW_CREDENTIALS = os.getenv("CORS_ALLOW_CREDENTIALS", "false").lower() == "true"
else:  # local 默认配置
    # 本地环境配置
    HOST = os.getenv("HOST", "0.0.0.0")
    PORT = int(os.getenv("PORT", "8000"))
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    # 本地环境 CORS 配置
    CORS_ORIGINS = ["*"]  # 本地开发允许所有来源
    CORS_ALLOW_CREDENTIALS = True

# 数据库配置
DATABASE_PATH = os.getenv("DATABASE_PATH", str(PROJECT_ROOT / "data" / "lazyai.db"))
CACHE_TTL = int(os.getenv("CACHE_TTL", "3600"))  # 缓存过期时间（秒）

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