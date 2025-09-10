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