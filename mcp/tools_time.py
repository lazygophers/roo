import datetime
import time
from croe import mcp
from zoneinfo import ZoneInfo


@mcp.tool()
async def time_now() -> int:
	"""
	获取当前Unix时间戳（秒级）

	返回:
		int: 当前时间的Unix时间戳

	异常:
		OSError: 当系统时间不可用时抛出
	"""
	return int(time.time())


@mcp.tool()
async def time_ts_to_str(timestamp: int, format: str = "%Y-%m-%d %H:%M:%S", timezone: str = "") -> str:
	"""
	将时间戳转换为指定格式的字符串

	参数:
		timestamp (int): 要转换的Unix时间戳
		format (str): 输出字符串的格式（默认：'%Y-%m-%d %H:%M:%S'）
		timezone (str): 目标时区名称（如'Asia/Shanghai'），留空则使用系统本地时区

	返回:
		str: 格式化后的时间字符串

	异常:
		ValueError: 当时区名称无效时抛出
		TypeError: 当时间戳类型不正确时抛出
	"""
	# 将时间戳转换为 UTC 时间
	dt_utc = datetime.datetime.utcfromtimestamp(timestamp).replace(tzinfo=datetime.timezone.utc)

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