import datetime
import time
from croe import mcp
from zoneinfo import ZoneInfo


@mcp.tool(
	name="time_now",
	title="Get Current Time",
	description="Get the current time",
)
async def time_now() -> int:
	return int(time.time())

@mcp.tool(
	name="time_ts_to_str",
	title="Convert Time Stamp to String",
	description="Convert a time stamp to a string",
)
async def time_ts_to_str(timestamp: int, format: str = "%Y-%m-%d %H:%M:%S", timezone: str = "") -> str:
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