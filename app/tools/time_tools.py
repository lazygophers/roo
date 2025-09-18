"""
时间工具集
使用装饰器自动注册时间相关的MCP工具
"""
import time
import datetime
from typing import Optional, Union
from dateutil import tz, parser
from app.tools.registry import time_tool


@time_tool(
    name="get_ts",
    description="Get current Unix timestamp (pure number)",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["timestamp", "Unix", "number"],
        "examples": [{}]
    }
)
def get_ts():
    """Get current Unix timestamp (pure number)"""
    return int(time.time())


@time_tool(
    name="format",
    description="Format time output with support for multiple formats and timezones",
    schema={
        "type": "object",
        "properties": {
            "timestamp": {
                "type": ["number", "string"],
                "description": "Unix timestamp or ISO format time string. Uses current time if not provided",
                "default": None
            },
            "format": {
                "type": "string",
                "description": "Output format",
                "enum": ["iso", "formatted", "custom"],
                "default": "formatted"
            },
            "custom_format": {
                "type": "string",
                "description": "Custom time format (e.g.: %Y-%m-%d %H:%M:%S)",
                "default": "%Y-%m-%d %H:%M:%S"
            },
            "timezone": {
                "type": "string",
                "description": "Target timezone (e.g.: UTC, Asia/Shanghai, local). Uses global config if not specified",
                "default": None
            },
            "include_timezone_info": {
                "type": "boolean",
                "description": "Include timezone information",
                "default": None
            }
        },
        "required": []
    },
    metadata={
        "tags": ["time_format", "timezone", "date"],
        "examples": [
            {},
            {"format": "iso"},
            {"format": "custom", "custom_format": "%Y年%m月%d日 %H时%M分"},
            {"timestamp": 1234567890, "timezone": "UTC"}
        ]
    }
)
def format(timestamp: Optional[Union[int, float, str]] = None,
           format: str = "formatted",
           custom_format: str = "%Y-%m-%d %H:%M:%S",
           timezone: Optional[str] = None,
           include_timezone_info: Optional[bool] = None):
    """Format time output with support for multiple formats and timezones"""
    try:
        # Use current time if timestamp not provided
        if timestamp is None:
            dt = datetime.datetime.now()
        else:
            # Parse timestamp
            if isinstance(timestamp, str):
                # Try to parse as ISO format first
                try:
                    dt = datetime.datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                except:
                    # Try to parse as timestamp string
                    dt = datetime.datetime.fromtimestamp(float(timestamp))
            else:
                dt = datetime.datetime.fromtimestamp(float(timestamp))

        # Handle timezone
        if timezone:
            if timezone.lower() == "local":
                dt = dt.replace(tzinfo=tz.tzlocal())
            elif timezone.upper() == "UTC":
                dt = dt.replace(tzinfo=tz.tzutc())
            else:
                target_tz = tz.gettz(timezone)
                if target_tz:
                    dt = dt.replace(tzinfo=tz.tzutc()).astimezone(target_tz)

        # Format output
        if format == "iso":
            result = dt.isoformat()
        elif format == "custom":
            result = dt.strftime(custom_format)
        else:  # formatted
            result = dt.strftime("%Y-%m-%d %H:%M:%S")

        # Add timezone info if requested
        if include_timezone_info and timezone:
            tz_name = dt.tzname() if dt.tzinfo else "Local"
            result += f" ({tz_name})"

        return result

    except Exception as e:
        return f"Error formatting time: {str(e)}"


@time_tool(
    name="convert_tz",
    description="Timezone conversion tool to convert time from one timezone to another",
    schema={
        "type": "object",
        "properties": {
            "time_input": {
                "type": "string",
                "description": "Input time (supports ISO format or Unix timestamp)",
            },
            "from_timezone": {
                "type": "string",
                "description": "Source timezone (e.g.: UTC, Asia/Shanghai)",
                "default": "local"
            },
            "to_timezone": {
                "type": "string",
                "description": "Target timezone (e.g.: UTC, Asia/Tokyo)",
            },
            "output_format": {
                "type": "string",
                "description": "Output format",
                "enum": ["iso", "formatted", "unix"],
                "default": "formatted"
            }
        },
        "required": ["time_input", "to_timezone"]
    },
    metadata={
        "tags": ["timezone_conversion", "i18n", "time"],
        "examples": [
            {"time_input": "2023-12-25 15:30:00", "from_timezone": "Asia/Shanghai", "to_timezone": "UTC"},
            {"time_input": "1703574600", "from_timezone": "UTC", "to_timezone": "America/New_York"}
        ]
    }
)
def convert_tz(time_input: str,
               to_timezone: str,
               from_timezone: str = "local",
               output_format: str = "formatted"):
    """Timezone conversion tool to convert time from one timezone to another"""
    try:
        # Parse input time
        if time_input.isdigit():
            # Unix timestamp
            dt = datetime.datetime.fromtimestamp(int(time_input))
        else:
            # Parse as datetime string
            dt = parser.parse(time_input)

        # Set source timezone
        if from_timezone.lower() == "local":
            dt = dt.replace(tzinfo=tz.tzlocal())
        elif from_timezone.upper() == "UTC":
            dt = dt.replace(tzinfo=tz.tzutc())
        else:
            source_tz = tz.gettz(from_timezone)
            if source_tz:
                dt = dt.replace(tzinfo=source_tz)

        # Convert to target timezone
        if to_timezone.upper() == "UTC":
            dt_converted = dt.astimezone(tz.tzutc())
        else:
            target_tz = tz.gettz(to_timezone)
            if target_tz:
                dt_converted = dt.astimezone(target_tz)
            else:
                return f"Error: Unknown timezone '{to_timezone}'"

        # Format output
        if output_format == "iso":
            return dt_converted.isoformat()
        elif output_format == "unix":
            return str(int(dt_converted.timestamp()))
        else:  # formatted
            return dt_converted.strftime("%Y-%m-%d %H:%M:%S %Z")

    except Exception as e:
        return f"Error converting timezone: {str(e)}"


@time_tool(
    name="parse",
    description="Parse and normalize time strings with support for multiple format recognition",
    schema={
        "type": "object",
        "properties": {
            "time_string": {
                "type": "string",
                "description": "Time string to parse"
            },
            "input_format": {
                "type": "string",
                "description": "Input format hint (e.g.: %Y-%m-%d %H:%M:%S). Leave empty for auto-recognition",
                "default": None
            },
            "timezone": {
                "type": "string",
                "description": "Input time timezone (assumes local timezone if not specified)",
                "default": "local"
            },
            "output_timezone": {
                "type": "string",
                "description": "Output timezone (converted timezone)",
                "default": None
            }
        },
        "required": ["time_string"]
    },
    metadata={
        "tags": ["time_parsing", "format_recognition", "normalization"],
        "examples": [
            {"time_string": "2023-12-25 15:30:00"},
            {"time_string": "Dec 25, 2023 3:30 PM"},
            {"time_string": "25/12/2023 15:30", "input_format": "%d/%m/%Y %H:%M"}
        ]
    }
)
def parse(time_string: str,
         input_format: Optional[str] = None,
         timezone: str = "local",
         output_timezone: Optional[str] = None):
    """Parse and normalize time strings with support for multiple format recognition"""
    try:
        if input_format:
            dt = datetime.datetime.strptime(time_string, input_format)
        else:
            dt = parser.parse(time_string)

        # Set input timezone
        if timezone.lower() == "local":
            dt = dt.replace(tzinfo=tz.tzlocal())
        elif timezone.upper() == "UTC":
            dt = dt.replace(tzinfo=tz.tzutc())
        else:
            tz_info = tz.gettz(timezone)
            if tz_info:
                dt = dt.replace(tzinfo=tz_info)

        # Convert to output timezone if specified
        if output_timezone:
            if output_timezone.upper() == "UTC":
                dt = dt.astimezone(tz.tzutc())
            else:
                target_tz = tz.gettz(output_timezone)
                if target_tz:
                    dt = dt.astimezone(target_tz)

        return {
            "parsed_time": dt.isoformat(),
            "unix_timestamp": int(dt.timestamp()),
            "formatted": dt.strftime("%Y-%m-%d %H:%M:%S %Z")
        }
    except Exception as e:
        return f"Error parsing time: {str(e)}"


@time_tool(
    name="calc_diff",
    description="Calculate time difference between two timestamps",
    schema={
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "description": "Start time (Unix timestamp or ISO format)"
            },
            "end_time": {
                "type": "string",
                "description": "End time (Unix timestamp or ISO format). Uses current time if not provided",
                "default": None
            },
            "unit": {
                "type": "string",
                "description": "Output unit",
                "enum": ["seconds", "minutes", "hours", "days", "weeks", "months", "years", "auto"],
                "default": "auto"
            },
            "precision": {
                "type": "integer",
                "description": "Decimal precision",
                "default": 2,
                "minimum": 0,
                "maximum": 6
            },
            "human_readable": {
                "type": "boolean",
                "description": "Output human-readable format (e.g.: 2 days 3 hours 30 minutes)",
                "default": True
            }
        },
        "required": ["start_time"]
    },
    metadata={
        "tags": ["time_diff", "duration", "calculation"],
        "examples": [
            {"start_time": "2023-12-25 10:00:00"},
            {"start_time": "1703573400", "end_time": "1703659800", "unit": "hours"},
            {"start_time": "2023-01-01", "end_time": "2023-12-31", "unit": "days"}
        ]
    }
)
def calc_diff(start_time: str,
              end_time: Optional[str] = None,
              unit: str = "auto",
              precision: int = 2,
              human_readable: bool = True):
    """Calculate time difference between two timestamps"""
    try:
        # Parse start time
        if start_time.isdigit():
            start_dt = datetime.datetime.fromtimestamp(int(start_time))
        else:
            start_dt = parser.parse(start_time)

        # Parse end time or use current time
        if end_time:
            if end_time.isdigit():
                end_dt = datetime.datetime.fromtimestamp(int(end_time))
            else:
                end_dt = parser.parse(end_time)
        else:
            end_dt = datetime.datetime.now()

        # Calculate difference
        diff = end_dt - start_dt
        total_seconds = diff.total_seconds()

        if human_readable:
            days = diff.days
            hours, remainder = divmod(diff.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)

            parts = []
            if days:
                parts.append(f"{days} day{'s' if days != 1 else ''}")
            if hours:
                parts.append(f"{hours} hour{'s' if hours != 1 else ''}")
            if minutes:
                parts.append(f"{minutes} minute{'s' if minutes != 1 else ''}")
            if seconds or not parts:
                parts.append(f"{seconds} second{'s' if seconds != 1 else ''}")

            return " ".join(parts)

        # Unit conversion
        if unit == "seconds" or unit == "auto":
            return round(total_seconds, precision)
        elif unit == "minutes":
            return round(total_seconds / 60, precision)
        elif unit == "hours":
            return round(total_seconds / 3600, precision)
        elif unit == "days":
            return round(total_seconds / 86400, precision)
        elif unit == "weeks":
            return round(total_seconds / 604800, precision)
        elif unit == "months":
            return round(total_seconds / 2629746, precision)  # Average month
        elif unit == "years":
            return round(total_seconds / 31556952, precision)  # Average year

    except Exception as e:
        return f"Error calculating difference: {str(e)}"


@time_tool(
    name="get_tz_info",
    description="Get timezone information including current time, UTC offset, etc.",
    schema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "Timezone name (e.g.: Asia/Shanghai, UTC)",
                "default": "local"
            },
            "include_dst_info": {
                "type": "boolean",
                "description": "Include daylight saving time information",
                "default": True
            }
        },
        "required": []
    },
    metadata={
        "tags": ["timezone_info", "UTC_offset", "DST"],
        "examples": [
            {},
            {"timezone": "Asia/Shanghai"},
            {"timezone": "America/New_York", "include_dst_info": True}
        ]
    }
)
def get_tz_info(timezone: str = "local", include_dst_info: bool = True):
    """Get timezone information including current time, UTC offset, etc."""
    try:
        if timezone.lower() == "local":
            tz_info = tz.tzlocal()
            tz_name = "Local"
        elif timezone.upper() == "UTC":
            tz_info = tz.tzutc()
            tz_name = "UTC"
        else:
            tz_info = tz.gettz(timezone)
            tz_name = timezone

        if not tz_info:
            return f"Error: Unknown timezone '{timezone}'"

        now = datetime.datetime.now(tz_info)

        result = {
            "timezone_name": tz_name,
            "current_time": now.strftime("%Y-%m-%d %H:%M:%S %Z"),
            "current_time_iso": now.isoformat(),
            "utc_offset": now.strftime("%z"),
            "unix_timestamp": int(now.timestamp())
        }

        if include_dst_info:
            result["is_dst"] = now.dst() is not None and now.dst().total_seconds() > 0
            result["timezone_abbreviation"] = now.tzname()

        return result

    except Exception as e:
        return f"Error getting timezone info: {str(e)}"