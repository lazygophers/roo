"""
FastAPI + Vue3 示例应用的主应用包。

该包作为整个应用的核心模块，采用 Clean Architecture 架构模式，将应用清晰地分为多个层次：
- 领域层：包含核心业务逻辑
- 接口层：处理 HTTP 请求和响应
- 基础设施层：处理数据库、日志等外部依赖

包结构：
    app/
    ├── __init__.py          # 包初始化文件
    ├── main.py              # FastAPI 应用入口点
    ├── database.py          # 数据库连接和操作
    ├── api/
    │   └── routes.py       # API 路由定义
    └── utils/
        ├── frontmatter_parser.py  # Frontmatter 解析工具
        └── logger.py            # 日志配置工具

技术栈：
- FastAPI: 现代、高性能的 Web 框架
- Vue3: 前端渐进式框架
- TinyDB: 轻量级文档数据库
- Structured Logging: 结构化日志记录

作者: FastAPI + Vue3 Example Team
版本: 1.0.0
"""
# 导入日志配置
from .utils.logger import app_logger

# 记录应用包初始化
app_logger.info("正在初始化 app 包...")

# 导入应用模块，使包可以被正确导入
app_logger.debug("导入应用模块")
try:
    from . import main
    from . import database
    from . import api
    app_logger.info("应用模块导入成功")
except ImportError as e:
    app_logger.error(f"导入应用模块失败: {e}")
    raise