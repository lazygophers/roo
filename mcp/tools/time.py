import datetime
import time
from core.croe import mcp
from zoneinfo import ZoneInfo
from pydantic import Field


@mcp.tool()
async def time_now() -> int:
    """
    获取当前Unix时间戳（秒级）
    Returns:
        int: 当前时间的Unix时间戳
    """
    return int(time.time())


@mcp.tool()
async def time_ts_to_str(
    timestamp: int = Field(description="时间戳"),
    format: str = Field(description="时间格式", default="%Y-%m-%d %H:%M:%S"),
    timezone: str = Field(description="时区", default="Asia/Shanghai"),
) -> str:
    """
    将时间戳转换为指定格式的字符串
    Returns:
        str: 格式化后的时间字符串
    """
    # 将时间戳转换为 UTC 时间
    dt_utc = datetime.datetime.utcfromtimestamp(timestamp).replace(
        tzinfo=datetime.timezone.utc
    )

    # 处理目标时区
    if timezone:
        target_tz = ZoneInfo(timezone)
    else:
        # 获取当前系统的本地时区
        local_tz = datetime.datetime.now().astimezone().tzinfo
        target_tz = local_tz

    # 转换为指定时区并格式化输出
    dt_target = dt_utc.astimezone(target_tz)
    return dt_target.strftime(format)
