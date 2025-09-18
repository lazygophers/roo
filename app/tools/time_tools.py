"""
时间工具集
使用装饰器自动注册时间相关的MCP工具
"""
from app.core.mcp_tool_registry import time_tool


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
    pass


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
def format():
    """Format time output with support for multiple formats and timezones"""
    pass


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
def convert_tz():
    """Timezone conversion tool to convert time from one timezone to another"""
    pass


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
def parse():
    """Parse and normalize time strings with support for multiple format recognition"""
    pass


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
def calc_diff():
    """Calculate time difference between two timestamps"""
    pass


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
def get_tz_info():
    """Get timezone information including current time, UTC offset, etc."""
    pass