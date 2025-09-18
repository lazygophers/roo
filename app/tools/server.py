"""
MCP (Model Context Protocol) server implementation
使用 FastMCP 提供 SSE 和 Streamable HTTP 传输
集成数据库工具管理系统
"""

import asyncio
import time
import platform
import psutil
import os
import hashlib
import shutil
from pathlib import Path
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from fastmcp import FastMCP
from mcp import types

from app.tools.service import get_mcp_tools_service
from app.core.database_service import get_database_service
from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log
from app.core.file_security import get_file_security_manager

logger = setup_logging("INFO")


class LazyAIMCPServer:
    """LazyAI Studio MCP 服务器实现"""
    
    def __init__(self, use_unified_db: bool = True):
        self.mcp = FastMCP("LazyAI Studio")
        self.tools_service = get_mcp_tools_service(use_unified_db=use_unified_db)
        self.db_service = get_database_service(use_unified_db=use_unified_db)
        self.file_security = get_file_security_manager()
        self._setup_tools_from_database()
        
    def _setup_tools_from_database(self):
        """从数据库动态设置 MCP 工具"""
        enabled_tools = self.tools_service.get_tools(enabled_only=True)
        logger.info(f"Setting up {len(enabled_tools)} MCP tools from database")
        
        for tool_data in enabled_tools:
            tool_name = tool_data['name']
            self._register_tool(tool_data)
            logger.info(f"Registered MCP tool: {sanitize_for_log(tool_name)}")
    
    def _register_tool(self, tool_data: Dict[str, Any]):
        """注册单个工具到FastMCP"""
        tool_name = tool_data['name']
        tool_description = tool_data['description']
        tool_schema = tool_data['schema']
        
        # 创建工具实现函数
        if tool_name == "time_get_ts":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_current_timestamp_impl() -> str:
                """获取当前Unix时间戳（纯数字）"""
                try:
                    now = datetime.now()
                    return str(int(now.timestamp()))
                except Exception as e:
                    logger.error(f"Error in get_current_timestamp: {str(e)}")
                    return str(int(datetime.now().timestamp()))
                    
        elif tool_name == "time_format":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def format_time_impl(timestamp: Optional[Union[int, float, str]] = None, 
                                format: str = 'formatted',
                                custom_format: str = '%Y-%m-%d %H:%M:%S',
                                timezone: Optional[str] = None,
                                include_timezone_info: Optional[bool] = None) -> str:
                """格式化时间输出实现"""
                from app.core.time_tools_service import get_time_tools_service
                import pytz
                
                try:
                    time_service = get_time_tools_service()
                    
                    # 确定时间对象
                    if timestamp is None:
                        dt = datetime.now()
                    else:
                        if isinstance(timestamp, str):
                            # 尝试解析字符串时间戳
                            try:
                                timestamp = float(timestamp)
                            except ValueError:
                                # 可能是ISO格式
                                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                                timestamp = None
                        
                        if timestamp is not None:
                            dt = datetime.fromtimestamp(timestamp)
                    
                    # 确定时区
                    if timezone is None:
                        tz_obj = time_service.get_timezone_object()
                        timezone_name = time_service.get_default_timezone()
                    else:
                        if timezone.lower() == "local":
                            tz_obj = None
                            timezone_name = "local"
                        elif timezone.upper() == "UTC":
                            tz_obj = pytz.UTC
                            timezone_name = "UTC"
                        else:
                            tz_obj = pytz.timezone(timezone)
                            timezone_name = timezone
                    
                    # 应用时区
                    if tz_obj:
                        if dt.tzinfo is None:
                            dt = tz_obj.localize(dt)
                        else:
                            dt = dt.astimezone(tz_obj)
                    else:
                        # 本地时区
                        if dt.tzinfo is None:
                            dt = dt.astimezone()
                    
                    # 确定是否显示时区信息
                    if include_timezone_info is None:
                        show_tz_info = time_service.should_display_timezone_info()
                    else:
                        show_tz_info = include_timezone_info
                    
                    # 格式化输出
                    if format == 'iso':
                        return dt.isoformat()
                    elif format == 'custom':
                        formatted_time = dt.strftime(custom_format)
                        if show_tz_info:
                            return f"{formatted_time} ({str(dt.tzinfo)})"
                        return formatted_time
                    else:  # formatted
                        formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                        if show_tz_info:
                            return f"格式化时间: {formatted_time} ({str(dt.tzinfo)})\n\n完整时间信息:\n- ISO 格式: {dt.isoformat()}\n- Unix 时间戳: {int(dt.timestamp())}\n- 格式化时间: {formatted_time}\n- 配置时区: {timezone_name}\n- 实际时区: {str(dt.tzinfo)}"
                        return formatted_time
                        
                except Exception as e:
                    logger.error(f"Error in format_time: {str(e)}")
                    return f"格式化时间失败: {str(e)}"
                    
        elif tool_name == "time_convert_tz":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def convert_timezone_impl(time_input: str, to_timezone: str, 
                                    from_timezone: str = "local", 
                                    output_format: str = "formatted") -> str:
                """时区转换工具实现"""
                import pytz
                from dateutil.parser import parse
                
                try:
                    # 解析输入时间
                    try:
                        # 尝试作为Unix时间戳
                        timestamp = float(time_input)
                        dt = datetime.fromtimestamp(timestamp)
                    except ValueError:
                        # 作为时间字符串解析
                        dt = parse(time_input)
                    
                    # 设置源时区
                    if from_timezone.lower() == "local":
                        if dt.tzinfo is None:
                            dt = dt.astimezone()
                    elif from_timezone.upper() == "UTC":
                        if dt.tzinfo is None:
                            dt = pytz.UTC.localize(dt)
                    else:
                        from_tz = pytz.timezone(from_timezone)
                        if dt.tzinfo is None:
                            dt = from_tz.localize(dt)
                        else:
                            dt = dt.astimezone(from_tz)
                    
                    # 转换到目标时区
                    if to_timezone.upper() == "UTC":
                        to_tz = pytz.UTC
                    else:
                        to_tz = pytz.timezone(to_timezone)
                    
                    converted_dt = dt.astimezone(to_tz)
                    
                    # 格式化输出
                    if output_format == "iso":
                        return converted_dt.isoformat()
                    elif output_format == "unix":
                        return str(int(converted_dt.timestamp()))
                    else:  # formatted
                        result = f"时区转换结果:\n\n"
                        result += f"输入时间: {dt.strftime('%Y-%m-%d %H:%M:%S')} ({str(dt.tzinfo)})\n"
                        result += f"转换后: {converted_dt.strftime('%Y-%m-%d %H:%M:%S')} ({str(converted_dt.tzinfo)})\n"
                        result += f"时差: {(converted_dt.utcoffset() - dt.utcoffset()).total_seconds() / 3600} 小时"
                        return result
                        
                except Exception as e:
                    logger.error(f"Error in convert_timezone: {str(e)}")
                    return f"时区转换失败: {str(e)}"
                    
        elif tool_name == "time_parse":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def parse_time_impl(time_string: str, 
                              input_format: Optional[str] = None,
                              timezone: str = "local",
                              output_timezone: Optional[str] = None) -> str:
                """时间解析工具实现"""
                from dateutil.parser import parse
                import pytz
                
                try:
                    # 解析时间字符串
                    if input_format:
                        dt = datetime.strptime(time_string, input_format)
                    else:
                        dt = parse(time_string)
                    
                    # 应用输入时区
                    if timezone.lower() == "local":
                        if dt.tzinfo is None:
                            dt = dt.astimezone()
                    elif timezone.upper() == "UTC":
                        if dt.tzinfo is None:
                            dt = pytz.UTC.localize(dt)
                    else:
                        input_tz = pytz.timezone(timezone)
                        if dt.tzinfo is None:
                            dt = input_tz.localize(dt)
                    
                    # 转换输出时区
                    if output_timezone:
                        if output_timezone.upper() == "UTC":
                            dt = dt.astimezone(pytz.UTC)
                        else:
                            output_tz = pytz.timezone(output_timezone)
                            dt = dt.astimezone(output_tz)
                    
                    result = f"时间解析结果:\n\n"
                    result += f"原始输入: {time_string}\n"
                    result += f"解析结果: {dt.strftime('%Y-%m-%d %H:%M:%S')} ({str(dt.tzinfo)})\n"
                    result += f"ISO 格式: {dt.isoformat()}\n"
                    result += f"Unix 时间戳: {int(dt.timestamp())}\n"
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in parse_time: {str(e)}")
                    return f"时间解析失败: {str(e)}"
                    
        elif tool_name == "time_calc_diff":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def calculate_time_diff_impl(start_time: str, 
                                       end_time: Optional[str] = None,
                                       unit: str = "auto",
                                       precision: int = 2,
                                       human_readable: bool = True) -> str:
                """时间差值计算工具实现"""
                from dateutil.parser import parse
                
                try:
                    # 解析开始时间
                    try:
                        start_timestamp = float(start_time)
                        start_dt = datetime.fromtimestamp(start_timestamp)
                    except ValueError:
                        start_dt = parse(start_time)
                    
                    # 解析结束时间
                    if end_time is None:
                        end_dt = datetime.now()
                    else:
                        try:
                            end_timestamp = float(end_time)
                            end_dt = datetime.fromtimestamp(end_timestamp)
                        except ValueError:
                            end_dt = parse(end_time)
                    
                    # 计算时间差
                    diff = end_dt - start_dt
                    total_seconds = abs(diff.total_seconds())
                    
                    # 单位转换
                    if unit == "seconds":
                        value = total_seconds
                        unit_name = "秒"
                    elif unit == "minutes":
                        value = total_seconds / 60
                        unit_name = "分钟"
                    elif unit == "hours":
                        value = total_seconds / 3600
                        unit_name = "小时"
                    elif unit == "days":
                        value = total_seconds / 86400
                        unit_name = "天"
                    elif unit == "weeks":
                        value = total_seconds / (86400 * 7)
                        unit_name = "周"
                    elif unit == "months":
                        value = total_seconds / (86400 * 30.44)  # 平均月长度
                        unit_name = "月"
                    elif unit == "years":
                        value = total_seconds / (86400 * 365.25)  # 平均年长度
                        unit_name = "年"
                    else:  # auto
                        if total_seconds < 60:
                            value = total_seconds
                            unit_name = "秒"
                        elif total_seconds < 3600:
                            value = total_seconds / 60
                            unit_name = "分钟"
                        elif total_seconds < 86400:
                            value = total_seconds / 3600
                            unit_name = "小时"
                        else:
                            value = total_seconds / 86400
                            unit_name = "天"
                    
                    result = f"时间差值计算结果:\n\n"
                    result += f"开始时间: {start_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"结束时间: {end_dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"时间差: {round(value, precision)} {unit_name}\n"
                    
                    if human_readable and total_seconds >= 60:
                        days = int(total_seconds // 86400)
                        hours = int((total_seconds % 86400) // 3600)
                        minutes = int((total_seconds % 3600) // 60)
                        seconds = int(total_seconds % 60)
                        
                        human_parts = []
                        if days > 0:
                            human_parts.append(f"{days}天")
                        if hours > 0:
                            human_parts.append(f"{hours}小时")
                        if minutes > 0:
                            human_parts.append(f"{minutes}分钟")
                        if seconds > 0 or not human_parts:
                            human_parts.append(f"{seconds}秒")
                        
                        result += f"人类可读: {' '.join(human_parts)}"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in calculate_time_diff: {str(e)}")
                    return f"时间差值计算失败: {str(e)}"
                    
        elif tool_name == "time_get_tz":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_timezone_info_impl(timezone: str = "local", include_dst_info: bool = True) -> str:
                """获取时区信息实现"""
                import pytz
                
                try:
                    # 获取时区对象
                    if timezone.lower() == "local":
                        dt = datetime.now()
                        tz_obj = dt.astimezone().tzinfo
                        tz_name = "本地时区"
                    elif timezone.upper() == "UTC":
                        dt = datetime.now(pytz.UTC)
                        tz_obj = pytz.UTC
                        tz_name = "UTC (协调世界时)"
                    else:
                        tz_obj = pytz.timezone(timezone)
                        dt = datetime.now(tz_obj)
                        tz_name = timezone
                    
                    result = f"时区信息:\n\n"
                    result += f"时区名称: {tz_name}\n"
                    result += f"当前时间: {dt.strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"UTC 偏移: {dt.strftime('%z')} ({dt.utcoffset()})\n"
                    result += f"时区简写: {dt.strftime('%Z')}\n"
                    
                    if include_dst_info and hasattr(tz_obj, 'localize'):
                        # 检查夏令时信息
                        try:
                            dst_offset = dt.dst()
                            if dst_offset and dst_offset.total_seconds() != 0:
                                result += f"夏令时: 是 (偏移 {dst_offset})\n"
                            else:
                                result += f"夏令时: 否\n"
                        except:
                            result += f"夏令时: 信息不可用\n"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Error in get_timezone_info: {str(e)}")
                    return f"获取时区信息失败: {str(e)}"
                    
        elif tool_name == "sys_get_info":
            @self.mcp.tool(name=tool_name, description=tool_description) 
            def get_system_info_impl(detailed: bool = False, include_performance: bool = True) -> str:
                """获取系统信息实现"""
                memory = psutil.virtual_memory()
                cpu_percent = psutil.cpu_percent(interval=1) if include_performance else 0
                
                result = f"""LazyAI Studio 系统信息:
- Python 版本: {platform.python_version()}
- 操作系统: {platform.system()} {platform.release()}
- CPU 使用率: {cpu_percent}%
- 内存使用: {memory.percent}% ({memory.used // 1024 // 1024}MB / {memory.total // 1024 // 1024}MB)
- 可用内存: {memory.available // 1024 // 1024}MB
- LazyGophers 出品 - 让 AI 替你思考！"""
                
                if detailed:
                    disk = psutil.disk_usage('/')
                    result += f"""
                    
详细信息:
- 磁盘使用: {disk.percent}% ({disk.used // 1024 // 1024 // 1024}GB / {disk.total // 1024 // 1024 // 1024}GB)
- CPU 核心数: {psutil.cpu_count()}
- 启动时间: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M:%S')}"""
                
                return result
                
        elif tool_name == "list_available_modes":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def list_available_modes_impl(category: str = 'all', include_description: bool = True) -> str:
                """列出可用AI模式实现"""
                
                try:
                    models_data = self.db_service.get_models_data()
                    if category != 'all':
                        models_data = [m for m in models_data if category in m.get('groups', [])]
                    
                    result = "LazyAI Studio 可用模式:\n\n"
                    
                    for model in models_data[:10]:  # 限制数量
                        emoji_map = {
                            'orchestrator': '🧠', 'architect': '🏗️', 'ask': '📚',
                            'code': '🪄', 'code-python': '🐍', 'debug': '🔬',
                            'doc-writer': '✍️', 'giter': '⚙️', 'memory': '🧠',
                            'project-research': '🔍'
                        }
                        emoji = emoji_map.get(model.get('slug', ''), '🔧')
                        name = model.get('name', 'Unknown')
                        slug = model.get('slug', '')
                        
                        result += f"{emoji} {slug} - {name}\n"
                        
                        if include_description and model.get('description'):
                            result += f"   {model['description'][:100]}...\n"
                    
                    result += "\nLazyGophers - 让你做个聪明的懒人！ 🛋️"
                    return result
                    
                except Exception as e:
                    logger.error(f"Failed to list modes: {sanitize_for_log(str(e))}")
                    return "获取AI模式列表失败，请稍后重试"
        
        elif tool_name == "get_project_stats":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_project_stats_impl(include_models: bool = True, include_files: bool = True) -> str:
                """获取项目统计信息实现"""
                
                try:
                    result = "LazyAI Studio 项目统计:\n\n"
                    
                    if include_models:
                        models_data = self.db_service.get_models_data()
                        result += f"📊 模型统计:\n"
                        result += f"  - 总模型数量: {len(models_data)}\n"
                        
                        # 按分组统计
                        groups = {}
                        for model in models_data:
                            for group in model.get('groups', []):
                                groups[group] = groups.get(group, 0) + 1
                        
                        result += f"  - 分组分布: {dict(list(groups.items())[:5])}\n\n"
                    
                    if include_files:
                        tools_stats = self.tools_service.get_statistics()
                        result += f"🔧 工具统计:\n"
                        result += f"  - 可用工具: {tools_stats['enabled_tools']}\n"
                        result += f"  - 工具分类: {tools_stats['total_categories']}\n\n"
                    
                    result += f"📈 系统状态: 正常运行\n"
                    result += f"⏰ 统计时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += "\nLazyGophers - 数据驱动的智能工作室！ 📊"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Failed to get project stats: {sanitize_for_log(str(e))}")
                    return "获取项目统计失败，请稍后重试"
        
        elif tool_name == "health_check":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def health_check_impl(check_database: bool = True, check_cache: bool = True) -> str:
                """系统健康检查实现"""
                
                try:
                    result = "LazyAI Studio 系统健康检查:\n\n"
                    overall_status = "✅ 健康"
                    
                    if check_database:
                        try:
                            models_count = len(self.db_service.get_models_data())
                            result += f"📊 数据库: ✅ 正常 ({models_count} 模型)\n"
                        except Exception as e:
                            result += f"📊 数据库: ❌ 异常\n"
                            overall_status = "⚠️ 部分异常"
                    
                    if check_cache:
                        try:
                            tools_count = len(self.tools_service.get_tools())
                            result += f"🔧 工具系统: ✅ 正常 ({tools_count} 工具)\n"
                        except Exception as e:
                            result += f"🔧 工具系统: ❌ 异常\n"
                            overall_status = "⚠️ 部分异常"
                    
                    # 系统资源检查
                    memory = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent(interval=0.1)
                    
                    if memory.percent > 90:
                        result += f"💾 内存: ⚠️ 使用率过高 ({memory.percent}%)\n"
                        overall_status = "⚠️ 部分异常"
                    else:
                        result += f"💾 内存: ✅ 正常 ({memory.percent}%)\n"
                    
                    if cpu_percent > 80:
                        result += f"🖥️ CPU: ⚠️ 使用率过高 ({cpu_percent}%)\n"
                    else:
                        result += f"🖥️ CPU: ✅ 正常 ({cpu_percent}%)\n"
                    
                    result += f"\n🏥 整体状态: {overall_status}\n"
                    result += f"⏰ 检查时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += "\nLazyGophers - 让系统健康运行！ 🏥"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Health check failed: {sanitize_for_log(str(e))}")
                    return "健康检查执行失败，请稍后重试"
        
        # 文件操作工具实现
        elif tool_name == "file_read":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def read_file_impl(file_path: str, encoding: str = 'utf-8', max_lines: int = 0) -> str:
                """读取文件内容实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("read", file_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(file_path)
                    
                    # 文件存在性检查
                    if not path.exists():
                        return f"❌ 文件不存在: {file_path}"
                    
                    if not path.is_file():
                        return f"❌ 路径不是文件: {file_path}"
                    
                    # 应用行数限制
                    limited_lines = self.file_security.get_limited_read_lines(max_lines)
                    
                    # 读取文件
                    with open(path, 'r', encoding=encoding) as f:
                        if max_lines == 0:
                            lines = []
                            for i, line in enumerate(f):
                                if i >= limited_lines:
                                    break
                                lines.append(line.rstrip('\n'))
                            content = '\n'.join(lines)
                            line_count = len(lines)
                            if limited_lines < len(content.splitlines()) and limited_lines > 0:
                                content += f"\n... (显示前 {limited_lines} 行，文件可能有更多内容)"
                        else:
                            lines = []
                            for i, line in enumerate(f):
                                if i >= limited_lines:
                                    break
                                lines.append(line.rstrip('\n'))
                            content = '\n'.join(lines)
                            line_count = len(lines)
                    
                    file_size = path.stat().st_size
                    return f"📄 文件读取成功: {file_path}\n📊 大小: {file_size} bytes | 行数: {line_count}\n📝 内容:\n{'-'*50}\n{content}"
                    
                except UnicodeDecodeError:
                    return f"❌ 编码错误: 无法使用 {encoding} 编码读取文件 {file_path}"
                except Exception as e:
                    logger.error(f"Read file failed: {sanitize_for_log(str(e))}")
                    return f"❌ 读取文件失败: {str(e)}"
        
        elif tool_name == "file_write":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def write_file_impl(file_path: str, content: str, encoding: str = 'utf-8', mode: str = 'write') -> str:
                """写入文件内容实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("write", file_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(file_path)
                    
                    # 确保父目录存在
                    path.parent.mkdir(parents=True, exist_ok=True)
                    
                    # 选择写入模式
                    write_mode = 'w' if mode == 'write' else 'a'
                    
                    with open(path, write_mode, encoding=encoding) as f:
                        f.write(content)
                    
                    file_size = path.stat().st_size
                    action = "写入" if mode == 'write' else "追加"
                    return f"✅ 文件{action}成功: {file_path}\n📊 文件大小: {file_size} bytes\n📝 {action}内容长度: {len(content)} 字符"
                    
                except Exception as e:
                    logger.error(f"Write file failed: {sanitize_for_log(str(e))}")
                    return f"❌ 写入文件失败: {str(e)}"
        
        elif tool_name == "file_ls_dir":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def list_directory_impl(directory_path: str = '.', show_hidden: bool = False, recursive: bool = False, file_info: bool = True) -> str:
                """列出目录内容实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("list", directory_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(directory_path)
                    
                    if not path.exists():
                        return f"❌ 目录不存在: {directory_path}"
                    
                    if not path.is_dir():
                        return f"❌ 路径不是目录: {directory_path}"
                    
                    result = f"📁 目录列表: {path.resolve()}\n{'='*50}\n"
                    
                    def format_size(size_bytes):
                        """格式化文件大小"""
                        for unit in ['B', 'KB', 'MB', 'GB']:
                            if size_bytes < 1024.0:
                                return f"{size_bytes:.1f} {unit}"
                            size_bytes /= 1024.0
                        return f"{size_bytes:.1f} TB"
                    
                    def list_items(current_path, prefix=""):
                        items = []
                        for item in current_path.iterdir():
                            if not show_hidden and item.name.startswith('.'):
                                continue
                            
                            try:
                                stat = item.stat()
                                if item.is_dir():
                                    icon = "📁"
                                    size_info = f"({len(list(item.iterdir()))} items)" if file_info else ""
                                elif item.suffix.lower() in ['.txt', '.md', '.py', '.js', '.json']:
                                    icon = "📄"
                                    size_info = format_size(stat.st_size) if file_info else ""
                                elif item.suffix.lower() in ['.jpg', '.png', '.gif', '.bmp']:
                                    icon = "🖼️"
                                    size_info = format_size(stat.st_size) if file_info else ""
                                else:
                                    icon = "📋"
                                    size_info = format_size(stat.st_size) if file_info else ""
                                
                                mod_time = datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M') if file_info else ""
                                info_part = f" [{size_info}] {mod_time}" if file_info else ""
                                
                                items.append(f"{prefix}{icon} {item.name}{info_part}")
                                
                                if recursive and item.is_dir():
                                    items.extend(list_items(item, prefix + "  "))
                                    
                            except (PermissionError, OSError):
                                items.append(f"{prefix}❌ {item.name} (无法访问)")
                        
                        return sorted(items)
                    
                    items = list_items(path)
                    if items:
                        result += '\n'.join(items)
                        result += f"\n\n📊 总计: {len(items)} 项"
                    else:
                        result += "📭 目录为空"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"List directory failed: {sanitize_for_log(str(e))}")
                    return f"❌ 列出目录失败: {str(e)}"
        
        elif tool_name == "file_new_dir":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def create_directory_impl(directory_path: str, parents: bool = True) -> str:
                """创建目录实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("write", directory_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(directory_path)
                    
                    if path.exists():
                        if path.is_dir():
                            return f"ℹ️ 目录已存在: {directory_path}"
                        else:
                            return f"❌ 路径已存在但不是目录: {directory_path}"
                    
                    path.mkdir(parents=parents, exist_ok=False)
                    return f"✅ 目录创建成功: {path.resolve()}"
                    
                except Exception as e:
                    logger.error(f"Create directory failed: {sanitize_for_log(str(e))}")
                    return f"❌ 创建目录失败: {str(e)}"
        
        elif tool_name == "github_del_file":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def delete_file_impl(file_path: str, force: bool = False) -> str:
                """删除文件或目录实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("delete", file_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(file_path)
                    
                    if not path.exists():
                        return f"ℹ️ 文件或目录不存在: {file_path}"
                    
                    if path.is_file():
                        path.unlink()
                        return f"✅ 文件删除成功: {file_path}"
                    elif path.is_dir():
                        if force:
                            shutil.rmtree(path)
                            return f"✅ 目录删除成功: {file_path}"
                        else:
                            try:
                                path.rmdir()  # 只删除空目录
                                return f"✅ 空目录删除成功: {file_path}"
                            except OSError:
                                return f"❌ 目录不为空，需要使用 force=True 强制删除: {file_path}"
                    else:
                        return f"❌ 未知文件类型: {file_path}"
                    
                except Exception as e:
                    logger.error(f"Delete file failed: {sanitize_for_log(str(e))}")
                    return f"❌ 删除失败: {str(e)}"
        
        elif tool_name == "file_get_info":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def file_info_impl(file_path: str, checksum: bool = False) -> str:
                """获取文件信息实现"""
                try:
                    # 安全权限检查
                    allowed, error_msg = self.file_security.validate_operation("read", file_path)
                    if not allowed:
                        return f"🚫 {error_msg}"
                    
                    path = Path(file_path)
                    
                    if not path.exists():
                        return f"❌ 文件或目录不存在: {file_path}"
                    
                    stat = path.stat()
                    result = f"📋 文件信息: {path.resolve()}\n{'='*50}\n"
                    
                    # 基本信息
                    if path.is_file():
                        result += f"📄 类型: 文件\n"
                        result += f"📊 大小: {stat.st_size} bytes ({stat.st_size/1024:.1f} KB)\n"
                        
                        # 计算校验和
                        if checksum and stat.st_size < 100 * 1024 * 1024:  # 只对小于100MB的文件计算
                            with open(path, 'rb') as f:
                                content = f.read()
                                md5_hash = hashlib.md5(content).hexdigest()
                                sha1_hash = hashlib.sha1(content).hexdigest()
                                result += f"🔍 MD5: {md5_hash}\n"
                                result += f"🔍 SHA1: {sha1_hash}\n"
                        elif checksum:
                            result += "⚠️ 文件过大，跳过校验和计算\n"
                    
                    elif path.is_dir():
                        result += f"📁 类型: 目录\n"
                        try:
                            item_count = len(list(path.iterdir()))
                            result += f"📊 包含项目: {item_count} 个\n"
                        except PermissionError:
                            result += "❌ 无法访问目录内容\n"
                    
                    # 时间信息
                    result += f"📅 创建时间: {datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"📅 修改时间: {datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    result += f"📅 访问时间: {datetime.fromtimestamp(stat.st_atime).strftime('%Y-%m-%d %H:%M:%S')}\n"
                    
                    # 权限信息
                    mode = stat.st_mode
                    permissions = []
                    if os.access(path, os.R_OK): permissions.append('读')
                    if os.access(path, os.W_OK): permissions.append('写')
                    if os.access(path, os.X_OK): permissions.append('执行')
                    
                    result += f"🔐 权限: {' | '.join(permissions) if permissions else '无权限'}\n"
                    result += f"🔢 权限模式: {oct(mode)[-3:]}"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"File info failed: {sanitize_for_log(str(e))}")
                    return f"❌ 获取文件信息失败: {str(e)}"
        
        elif tool_name == "sys_get_security":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def get_file_security_info_impl() -> str:
                """获取文件安全配置信息实现"""
                try:
                    security_info = self.file_security.get_security_info()
                    
                    result = "🔒 文件工具安全配置信息\n"
                    result += "=" * 50 + "\n\n"
                    
                    result += f"🛡️ 安全模式: {'严格模式' if security_info['strict_mode'] else '宽松模式'}\n\n"
                    
                    result += f"📖 可读取目录 ({len(security_info['readable_directories'])} 个):\n"
                    for dir_path in security_info['readable_directories']:
                        result += f"  📁 {dir_path}\n"
                    result += "\n"
                    
                    result += f"✏️ 可写入目录 ({len(security_info['writable_directories'])} 个):\n"
                    for dir_path in security_info['writable_directories']:
                        result += f"  📝 {dir_path}\n"
                    result += "\n"
                    
                    result += f"🗑️ 可删除目录 ({len(security_info['deletable_directories'])} 个):\n"
                    for dir_path in security_info['deletable_directories']:
                        result += f"  🗂️ {dir_path}\n"
                    result += "\n"
                    
                    result += f"🚫 禁止访问目录 ({len(security_info['forbidden_directories'])} 个):\n"
                    for dir_path in security_info['forbidden_directories']:
                        result += f"  ⛔ {dir_path}\n"
                    result += "\n"
                    
                    result += "📊 限制设置:\n"
                    result += f"  📏 最大文件大小: {security_info['max_file_size_mb']:.1f} MB\n"
                    result += f"  📄 最大读取行数: {security_info['max_read_lines']} 行\n\n"
                    
                    result += "ℹ️ 说明:\n"
                    result += "- 严格模式下，只能访问明确允许的目录\n"
                    result += "- 宽松模式下，除了禁止目录外都可以访问\n"
                    result += "- 所有文件操作都会进行安全检查\n"
                    result += "- 配置存储在数据库中，可通过 update_file_security_* 工具修改"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Get file security info failed: {sanitize_for_log(str(e))}")
                    return f"❌ 获取安全配置信息失败: {str(e)}"

        elif tool_name == "sys_set_security_paths":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def update_file_security_paths_impl(config_type: str, paths: List[str]) -> str:
                """更新文件安全路径配置实现"""
                try:
                    # 验证配置类型
                    valid_types = ["readable", "writable", "deletable", "forbidden"]
                    if config_type not in valid_types:
                        return f"❌ 无效的配置类型: {config_type}，有效类型: {', '.join(valid_types)}"
                    
                    # 更新数据库配置
                    success = self.file_security.security_service.update_path_config(config_type, paths)
                    if not success:
                        return f"❌ 更新{config_type}路径配置失败"
                    
                    # 重新加载配置到内存
                    self.file_security.reload_config()
                    
                    result = f"✅ 成功更新{config_type}路径配置\n"
                    result += f"📁 已配置 {len(paths)} 个路径:\n"
                    for path in paths:
                        result += f"  • {path}\n"
                    result += "\n💾 配置已保存到数据库并刷新到内存"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Update file security paths failed: {sanitize_for_log(str(e))}")
                    return f"❌ 更新路径配置失败: {str(e)}"

        elif tool_name == "sys_set_security_limits":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def update_file_security_limits_impl(limit_type: str, value) -> str:
                """更新文件安全限制配置实现"""
                try:
                    # 验证限制类型
                    valid_types = ["max_file_size", "max_read_lines", "strict_mode"]
                    if limit_type not in valid_types:
                        return f"❌ 无效的限制类型: {limit_type}，有效类型: {', '.join(valid_types)}"
                    
                    # 验证值类型
                    if limit_type == "max_file_size" and not isinstance(value, (int, float)):
                        return f"❌ max_file_size 必须是数字类型（字节数）"
                    elif limit_type == "max_read_lines" and not isinstance(value, int):
                        return f"❌ max_read_lines 必须是整数类型"
                    elif limit_type == "strict_mode" and not isinstance(value, bool):
                        return f"❌ strict_mode 必须是布尔类型"
                    
                    # 更新数据库配置
                    success = self.file_security.security_service.update_limit_config(limit_type, value)
                    if not success:
                        return f"❌ 更新{limit_type}限制配置失败"
                    
                    # 重新加载配置到内存
                    self.file_security.reload_config()
                    
                    # 格式化显示值
                    display_value = value
                    if limit_type == "max_file_size":
                        display_value = f"{value / (1024 * 1024):.1f} MB"
                    elif limit_type == "strict_mode":
                        display_value = "启用" if value else "禁用"
                    
                    result = f"✅ 成功更新{limit_type}限制配置\n"
                    result += f"📊 新值: {display_value}\n"
                    result += "💾 配置已保存到数据库并刷新到内存"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Update file security limits failed: {sanitize_for_log(str(e))}")
                    return f"❌ 更新限制配置失败: {str(e)}"

        elif tool_name == "sys_reload_security":
            @self.mcp.tool(name=tool_name, description=tool_description)
            def reload_file_security_config_impl() -> str:
                """重新加载文件安全配置实现"""
                try:
                    # 重新加载配置
                    self.file_security.reload_config()
                    
                    # 获取更新后的配置信息
                    security_info = self.file_security.get_security_info()
                    
                    result = "🔄 文件安全配置已重新加载\n"
                    result += "=" * 30 + "\n\n"
                    result += f"🛡️ 安全模式: {'严格模式' if security_info['strict_mode'] else '宽松模式'}\n"
                    result += f"📖 可读取目录: {len(security_info['readable_directories'])} 个\n"
                    result += f"✏️ 可写入目录: {len(security_info['writable_directories'])} 个\n"
                    result += f"🗑️ 可删除目录: {len(security_info['deletable_directories'])} 个\n"
                    result += f"🚫 禁止访问目录: {len(security_info['forbidden_directories'])} 个\n"
                    result += f"📏 最大文件大小: {security_info['max_file_size_mb']:.1f} MB\n"
                    result += f"📄 最大读取行数: {security_info['max_read_lines']} 行\n\n"
                    result += "✅ 所有配置已从数据库刷新到内存"
                    
                    return result
                    
                except Exception as e:
                    logger.error(f"Reload file security config failed: {sanitize_for_log(str(e))}")
                    return f"❌ 重新加载安全配置失败: {str(e)}"
    
    def get_available_tools(self) -> List[Dict[str, Any]]:
        """获取可用工具列表"""
        return self.tools_service.get_tools(enabled_only=True)
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> str:
        """调用MCP工具"""
        try:
            # 获取工具信息
            available_tools = self.get_available_tools()
            tool_info = next((tool for tool in available_tools if tool['name'] == tool_name), None)
            
            if not tool_info:
                raise ValueError(f"Tool '{tool_name}' not found")
            
            # 调用FastMCP服务器的工具
            # 需要通过MCP协议调用已注册的工具
            # 这里我们需要直接调用对应的实现函数
            
            if tool_name == "time_get_ts":
                now = datetime.now()
                return str(int(now.timestamp()))
                
            elif tool_name == "time_format":
                from app.core.time_tools_service import get_time_tools_service
                import pytz
                
                timestamp = arguments.get('timestamp')
                format_type = arguments.get('format', 'formatted')
                custom_format = arguments.get('custom_format', '%Y-%m-%d %H:%M:%S')
                timezone = arguments.get('timezone')
                include_timezone_info = arguments.get('include_timezone_info')
                
                time_service = get_time_tools_service()
                
                # 确定时间对象
                if timestamp is None:
                    dt = datetime.now()
                else:
                    if isinstance(timestamp, str):
                        try:
                            timestamp = float(timestamp)
                        except ValueError:
                            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                            timestamp = None
                    
                    if timestamp is not None:
                        dt = datetime.fromtimestamp(timestamp)
                
                # 确定时区
                if timezone is None:
                    tz_obj = time_service.get_timezone_object()
                    timezone_name = time_service.get_default_timezone()
                else:
                    if timezone.lower() == "local":
                        tz_obj = None
                        timezone_name = "local"
                    elif timezone.upper() == "UTC":
                        tz_obj = pytz.UTC
                        timezone_name = "UTC"
                    else:
                        tz_obj = pytz.timezone(timezone)
                        timezone_name = timezone
                
                # 应用时区
                if tz_obj:
                    if dt.tzinfo is None:
                        dt = tz_obj.localize(dt)
                    else:
                        dt = dt.astimezone(tz_obj)
                else:
                    if dt.tzinfo is None:
                        dt = dt.astimezone()
                
                # 确定是否显示时区信息
                if include_timezone_info is None:
                    show_tz_info = time_service.should_display_timezone_info()
                else:
                    show_tz_info = include_timezone_info
                
                # 格式化输出
                if format_type == 'iso':
                    return dt.isoformat()
                elif format_type == 'custom':
                    formatted_time = dt.strftime(custom_format)
                    if show_tz_info:
                        return f"{formatted_time} ({str(dt.tzinfo)})"
                    return formatted_time
                else:  # formatted
                    formatted_time = dt.strftime('%Y-%m-%d %H:%M:%S')
                    if show_tz_info:
                        return f"格式化时间: {formatted_time} ({str(dt.tzinfo)})\n\n完整时间信息:\n- ISO 格式: {dt.isoformat()}\n- Unix 时间戳: {int(dt.timestamp())}\n- 格式化时间: {formatted_time}\n- 配置时区: {timezone_name}\n- 实际时区: {str(dt.tzinfo)}"
                    return formatted_time
            
            # 对于其他工具，可以添加类似的实现
            # 这是一个简化的实现，实际中可能需要更完善的工具调用机制
            else:
                return f"Tool '{tool_name}' is registered but not implemented in call_tool method"
                
        except Exception as e:
            logger.error(f"Error calling tool '{tool_name}': {str(e)}")
            raise
    
    def get_tools_by_category(self) -> Dict[str, Any]:
        """按分类获取工具"""
        return self.tools_service.get_tools_by_category()
    
    def refresh_tools(self) -> Dict[str, int]:
        """刷新工具配置"""
        logger.info("Refreshing MCP tools from database")
        
        # 重新注册内置工具
        result = self.tools_service.register_builtin_tools()
        
        # 重新设置FastMCP工具
        # 注意: FastMCP可能不支持动态重新注册，这里只是记录
        logger.info(f"Tools refreshed: {result}")
        return result
    
    def get_fastapi_app(self):
        """获取 FastAPI 应用实例用于集成"""
        return self.mcp


# 全局 MCP 服务器实例
_mcp_server = None

def get_mcp_server(use_unified_db: bool = True) -> LazyAIMCPServer:
    """获取 MCP 服务器实例"""
    global _mcp_server
    if _mcp_server is None:
        _mcp_server = LazyAIMCPServer(use_unified_db=use_unified_db)
    return _mcp_server

def init_mcp_server(use_unified_db: bool = True) -> LazyAIMCPServer:
    """初始化 MCP 服务器"""
    logger.info("Initializing MCP server...")
    
    mcp_server = get_mcp_server(use_unified_db=use_unified_db)
    tools_count = len(mcp_server.get_available_tools())
    
    logger.info(f"MCP server initialized with {tools_count} tools (unified_db: {use_unified_db})")
    return mcp_server