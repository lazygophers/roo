from rich.logging import RichHandler
import logging

# 配置日志
# 修改日志格式配置，添加完整日期时间和每行时间显示
logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s %(message)s",  # 添加asctime字段
    datefmt="%Y-%m-%d %H:%M:%S",  # 完整日期时间格式
    handlers=[RichHandler(rich_tracebacks=True)],
    encoding="utf-8",
)

# 创建日志记录器
log = logging.getLogger("lazygophers")