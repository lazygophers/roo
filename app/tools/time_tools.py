"""
时间工具集
使用装饰器自动注册时间相关的MCP工具
"""
from app.core.mcp_tool_registry import time_tool


@time_tool(
    name="get_ts",
    description="获取当前Unix时间戳（纯数字）",
    schema={
        "type": "object",
        "properties": {},
        "required": []
    },
    metadata={
        "tags": ["时间戳", "Unix", "数字"],
        "examples": [{}]
    }
)
def get_ts():
    """获取当前Unix时间戳（纯数字）"""
    pass


@time_tool(
    name="format",
    description="格式化时间输出，支持多种格式和时区",
    schema={
        "type": "object",
        "properties": {
            "timestamp": {
                "type": ["number", "string"],
                "description": "Unix时间戳或ISO格式时间字符串。如不提供则使用当前时间",
                "default": None
            },
            "format": {
                "type": "string",
                "description": "输出格式",
                "enum": ["iso", "formatted", "custom"],
                "default": "formatted"
            },
            "custom_format": {
                "type": "string",
                "description": "自定义时间格式（如：%Y-%m-%d %H:%M:%S）",
                "default": "%Y-%m-%d %H:%M:%S"
            },
            "timezone": {
                "type": "string",
                "description": "目标时区（如：UTC, Asia/Shanghai, local）。如不指定则使用全局配置",
                "default": None
            },
            "include_timezone_info": {
                "type": "boolean",
                "description": "是否包含时区信息",
                "default": None
            }
        },
        "required": []
    },
    metadata={
        "tags": ["时间格式化", "时区", "日期"],
        "examples": [
            {},
            {"format": "iso"},
            {"format": "custom", "custom_format": "%Y年%m月%d日 %H时%M分"},
            {"timestamp": 1234567890, "timezone": "UTC"}
        ]
    }
)
def format():
    """格式化时间输出，支持多种格式和时区"""
    pass


@time_tool(
    name="convert_tz",
    description="时区转换工具，将时间从一个时区转换到另一个时区",
    schema={
        "type": "object",
        "properties": {
            "time_input": {
                "type": "string",
                "description": "输入的时间（支持ISO格式或Unix时间戳）",
            },
            "from_timezone": {
                "type": "string",
                "description": "源时区（如：UTC, Asia/Shanghai）",
                "default": "local"
            },
            "to_timezone": {
                "type": "string",
                "description": "目标时区（如：UTC, Asia/Tokyo）",
            },
            "output_format": {
                "type": "string",
                "description": "输出格式",
                "enum": ["iso", "formatted", "unix"],
                "default": "formatted"
            }
        },
        "required": ["time_input", "to_timezone"]
    },
    metadata={
        "tags": ["时区转换", "国际化", "时间"],
        "examples": [
            {"time_input": "2023-12-25 15:30:00", "from_timezone": "Asia/Shanghai", "to_timezone": "UTC"},
            {"time_input": "1703574600", "from_timezone": "UTC", "to_timezone": "America/New_York"}
        ]
    }
)
def convert_tz():
    """时区转换工具，将时间从一个时区转换到另一个时区"""
    pass


@time_tool(
    name="parse",
    description="解析和标准化时间字符串，支持多种格式识别",
    schema={
        "type": "object",
        "properties": {
            "time_string": {
                "type": "string",
                "description": "要解析的时间字符串"
            },
            "input_format": {
                "type": "string",
                "description": "输入格式提示（如：%Y-%m-%d %H:%M:%S）。留空自动识别",
                "default": None
            },
            "timezone": {
                "type": "string",
                "description": "输入时间的时区（如未指定则假设为本地时区）",
                "default": "local"
            },
            "output_timezone": {
                "type": "string",
                "description": "输出时区（转换后的时区）",
                "default": None
            }
        },
        "required": ["time_string"]
    },
    metadata={
        "tags": ["时间解析", "格式识别", "标准化"],
        "examples": [
            {"time_string": "2023-12-25 15:30:00"},
            {"time_string": "Dec 25, 2023 3:30 PM"},
            {"time_string": "25/12/2023 15:30", "input_format": "%d/%m/%Y %H:%M"}
        ]
    }
)
def parse():
    """解析和标准化时间字符串，支持多种格式识别"""
    pass


@time_tool(
    name="calc_diff",
    description="计算两个时间之间的差值",
    schema={
        "type": "object",
        "properties": {
            "start_time": {
                "type": "string",
                "description": "开始时间（Unix时间戳或ISO格式）"
            },
            "end_time": {
                "type": "string",
                "description": "结束时间（Unix时间戳或ISO格式）。如不提供则使用当前时间",
                "default": None
            },
            "unit": {
                "type": "string",
                "description": "输出单位",
                "enum": ["seconds", "minutes", "hours", "days", "weeks", "months", "years", "auto"],
                "default": "auto"
            },
            "precision": {
                "type": "integer",
                "description": "小数点精度",
                "default": 2,
                "minimum": 0,
                "maximum": 6
            },
            "human_readable": {
                "type": "boolean",
                "description": "是否输出人类可读的格式（如：2天3小时30分钟）",
                "default": True
            }
        },
        "required": ["start_time"]
    },
    metadata={
        "tags": ["时间差", "持续时间", "计算"],
        "examples": [
            {"start_time": "2023-12-25 10:00:00"},
            {"start_time": "1703573400", "end_time": "1703659800", "unit": "hours"},
            {"start_time": "2023-01-01", "end_time": "2023-12-31", "unit": "days"}
        ]
    }
)
def calc_diff():
    """计算两个时间之间的差值"""
    pass


@time_tool(
    name="get_tz_info",
    description="获取时区信息，包括当前时间、UTC偏移等",
    schema={
        "type": "object",
        "properties": {
            "timezone": {
                "type": "string",
                "description": "时区名称（如：Asia/Shanghai, UTC）",
                "default": "local"
            },
            "include_dst_info": {
                "type": "boolean",
                "description": "是否包含夏令时信息",
                "default": True
            }
        },
        "required": []
    },
    metadata={
        "tags": ["时区信息", "UTC偏移", "夏令时"],
        "examples": [
            {},
            {"timezone": "Asia/Shanghai"},
            {"timezone": "America/New_York", "include_dst_info": True}
        ]
    }
)
def get_tz_info():
    """获取时区信息，包括当前时间、UTC偏移等"""
    pass