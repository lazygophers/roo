"""
系统工具和时间工具模块全面测试
目标：将system_tools.py和time_tools.py的测试覆盖率大幅提升
涵盖系统监控和时间处理的所有功能
"""
import pytest
import time
import datetime
import platform
from unittest.mock import Mock, patch, MagicMock

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.tools.system_tools import get_info
    SYSTEM_TOOLS_AVAILABLE = True
except ImportError as e:
    SYSTEM_TOOLS_AVAILABLE = False
    print(f"System tools import failed: {e}")

try:
    from app.tools.time_tools import (
        get_ts, format, convert_tz, parse, calc_diff, get_tz_info
    )
    TIME_TOOLS_AVAILABLE = True
except ImportError as e:
    TIME_TOOLS_AVAILABLE = False
    print(f"Time tools import failed: {e}")


@pytest.mark.skipif(not SYSTEM_TOOLS_AVAILABLE, reason="System tools module not available")
class TestSystemTools:
    """系统工具测试套件"""

    @pytest.fixture
    def mock_psutil(self):
        """模拟psutil模块"""
        mock_psutil = Mock()

        # CPU相关mock
        mock_psutil.cpu_count.side_effect = lambda logical=True: 8 if logical else 4
        mock_cpu_freq = Mock()
        mock_cpu_freq.max = 3500.0
        mock_cpu_freq.current = 2800.0
        mock_psutil.cpu_freq.return_value = mock_cpu_freq
        mock_psutil.cpu_percent.return_value = 45.2

        # 内存相关mock
        mock_memory = Mock()
        mock_memory.total = 16 * 1024**3  # 16GB
        mock_memory.available = 8 * 1024**3  # 8GB
        mock_memory.used = 8 * 1024**3  # 8GB
        mock_memory.percent = 50.0
        mock_psutil.virtual_memory.return_value = mock_memory

        # 磁盘相关mock
        mock_disk = Mock()
        mock_disk.total = 500 * 1024**3  # 500GB
        mock_disk.used = 250 * 1024**3  # 250GB
        mock_disk.free = 250 * 1024**3  # 250GB
        mock_psutil.disk_usage.return_value = mock_disk

        # IO相关mock
        mock_disk_io = Mock()
        mock_disk_io._asdict.return_value = {
            "read_count": 1000,
            "write_count": 800,
            "read_bytes": 1024000,
            "write_bytes": 512000
        }
        mock_psutil.disk_io_counters.return_value = mock_disk_io

        mock_net_io = Mock()
        mock_net_io._asdict.return_value = {
            "bytes_sent": 2048000,
            "bytes_recv": 4096000,
            "packets_sent": 1500,
            "packets_recv": 2000
        }
        mock_psutil.net_io_counters.return_value = mock_net_io

        # 启动时间mock
        mock_psutil.boot_time.return_value = time.time() - 86400  # 1天前启动

        return mock_psutil

    @pytest.fixture
    def mock_platform(self):
        """模拟platform模块"""
        mock_platform = Mock()
        mock_platform.system.return_value = "Darwin"
        mock_platform.release.return_value = "22.1.0"
        mock_platform.version.return_value = "Darwin Kernel Version 22.1.0"
        mock_platform.machine.return_value = "x86_64"
        mock_platform.processor.return_value = "i386"
        mock_platform.python_version.return_value = "3.12.9"
        mock_platform.node.return_value = "test-machine"
        return mock_platform

    def test_get_info_detailed_without_performance(self, mock_psutil, mock_platform):
        """测试获取详细系统信息但不包含性能指标"""
        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform), \
             patch('app.tools.system_tools.time.time', return_value=1640995200):

            result = get_info(detailed=True, include_performance=False)

            assert isinstance(result, dict)
            assert result["application"] == "LazyAI Studio - LazyGophers Organization"
            assert result["timestamp"] == 1640995200

            # 验证平台信息
            platform_info = result["platform"]
            assert platform_info["system"] == "Darwin"
            assert platform_info["release"] == "22.1.0"
            assert platform_info["machine"] == "x86_64"

            # 验证详细信息存在
            assert "cpu" in result
            assert "memory" in result
            assert "disk" in result
            assert "python_version" in result
            assert "hostname" in result

            # 验证性能信息不存在
            assert "performance" not in result

    def test_get_info_detailed_with_performance(self, mock_psutil, mock_platform):
        """测试获取详细系统信息包含性能指标"""
        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform), \
             patch('app.tools.system_tools.os.getloadavg', return_value=(1.5, 1.2, 1.0)):

            result = get_info(detailed=True, include_performance=True)

            assert "performance" in result
            performance = result["performance"]

            assert "cpu_usage" in performance
            assert "memory_usage" in performance
            assert "disk_io" in performance
            assert "network_io" in performance
            assert "boot_time" in performance
            assert "load_average" in performance

            # 验证CPU使用率
            mock_psutil.cpu_percent.assert_called_with(interval=1)

    def test_get_info_simple_mode(self, mock_psutil, mock_platform):
        """测试简单模式（detailed=False）"""
        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform):

            result = get_info(detailed=False, include_performance=False)

            assert "application" in result
            assert "timestamp" in result
            assert "platform" in result

            # 详细信息不应该存在
            assert "cpu" not in result
            assert "memory" not in result
            assert "disk" not in result

    def test_get_info_cpu_freq_none(self, mock_psutil, mock_platform):
        """测试CPU频率信息为None的情况"""
        mock_psutil.cpu_freq.return_value = None

        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform):

            result = get_info(detailed=True)

            cpu_info = result["cpu"]
            assert cpu_info["max_frequency"] == "Unknown"
            assert cpu_info["current_frequency"] == "Unknown"

    def test_get_info_io_counters_none(self, mock_psutil, mock_platform):
        """测试IO计数器为None的情况"""
        mock_psutil.disk_io_counters.return_value = None
        mock_psutil.net_io_counters.return_value = None

        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform):

            result = get_info(detailed=True, include_performance=True)

            performance = result["performance"]
            assert performance["disk_io"] == {}
            assert performance["network_io"] == {}

    def test_get_info_no_getloadavg(self, mock_psutil, mock_platform):
        """测试没有getloadavg函数的情况"""
        with patch('app.tools.system_tools.psutil', mock_psutil), \
             patch('app.tools.system_tools.platform', mock_platform), \
             patch('app.tools.system_tools.os', spec=[]):  # os没有getloadavg属性

            result = get_info(detailed=True, include_performance=True)

            performance = result["performance"]
            assert performance["load_average"] == "Not available"

    def test_get_info_exception_handling(self):
        """测试异常处理"""
        with patch('app.tools.system_tools.platform.system', side_effect=Exception("Platform error")):
            result = get_info()

            assert isinstance(result, str)
            assert "Error getting system information" in result
            assert "Platform error" in result


@pytest.mark.skipif(not TIME_TOOLS_AVAILABLE, reason="Time tools module not available")
class TestTimeTools:
    """时间工具测试套件"""

    def test_get_ts_basic(self):
        """测试获取基本时间戳"""
        with patch('app.tools.time_tools.time.time', return_value=1640995200.5):
            result = get_ts()
            assert result == 1640995200

    def test_format_default_current_time(self):
        """测试格式化当前时间（默认参数）"""
        with patch('app.tools.time_tools.datetime.datetime') as mock_datetime:
            mock_now = Mock()
            mock_now.strftime.return_value = "2023-12-31 23:59:59"
            mock_datetime.now.return_value = mock_now

            result = format()

            assert result == "2023-12-31 23:59:59"
            mock_datetime.now.assert_called_once()

    def test_format_with_timestamp_unix(self):
        """测试格式化Unix时间戳"""
        result = format(timestamp=1640995200, format="formatted")

        assert isinstance(result, str)
        assert "2022" in result  # 验证年份正确

    def test_format_with_timestamp_string(self):
        """测试格式化时间戳字符串"""
        result = format(timestamp="1640995200", format="formatted")

        assert isinstance(result, str)
        assert "2022" in result

    def test_format_iso_string_input(self):
        """测试格式化ISO格式字符串输入"""
        result = format(timestamp="2022-01-01T00:00:00Z", format="iso")

        assert isinstance(result, str)
        # ISO格式应该包含日期和时间
        assert "2022" in result
        assert "T" in result or ":" in result

    def test_format_custom_format(self):
        """测试自定义格式"""
        result = format(
            timestamp=1640995200,
            format="custom",
            custom_format="%Y年%m月%d日 %H时%M分"
        )

        assert isinstance(result, str)
        assert "年" in result
        assert "月" in result
        assert "日" in result

    def test_format_with_timezone_local(self):
        """测试带本地时区"""
        result = format(
            timestamp=1640995200,
            timezone="local",
            include_timezone_info=True
        )

        assert isinstance(result, str)

    def test_format_with_timezone_utc(self):
        """测试UTC时区"""
        result = format(
            timestamp=1640995200,
            timezone="UTC",
            include_timezone_info=True
        )

        assert isinstance(result, str)
        if "(UTC)" not in result:
            # 有些情况下可能显示为GMT或其他形式
            assert "UTC" in result or "GMT" in result or "+" in result or "-" in result

    def test_format_with_specific_timezone(self):
        """测试特定时区"""
        result = format(
            timestamp=1640995200,
            timezone="Asia/Shanghai",
            include_timezone_info=True
        )

        assert isinstance(result, str)

    def test_format_error_handling(self):
        """测试格式化错误处理"""
        result = format(timestamp="invalid_timestamp")

        assert isinstance(result, str)
        assert "Error formatting time" in result

    def test_convert_tz_timestamp_input(self):
        """测试时区转换Unix时间戳输入"""
        result = convert_tz(
            time_input="1640995200",
            from_timezone="UTC",
            to_timezone="Asia/Shanghai",
            output_format="formatted"
        )

        assert isinstance(result, str)
        # 应该包含时区信息
        assert any(tz in result for tz in ["CST", "GMT", "+", "-"])

    def test_convert_tz_datetime_string_input(self):
        """测试时区转换日期时间字符串输入"""
        result = convert_tz(
            time_input="2022-01-01 00:00:00",
            from_timezone="UTC",
            to_timezone="America/New_York",
            output_format="iso"
        )

        assert isinstance(result, str)
        assert "2021-12-31" in result or "2022-01-01" in result  # 可能是前一天由于时区差异

    def test_convert_tz_unix_output(self):
        """测试时区转换Unix输出格式"""
        result = convert_tz(
            time_input="2022-01-01 00:00:00",
            from_timezone="UTC",
            to_timezone="UTC",
            output_format="unix"
        )

        # Unix时间戳应该是数字字符串
        assert result.isdigit()

    def test_convert_tz_unknown_timezone(self):
        """测试转换到未知时区"""
        result = convert_tz(
            time_input="1640995200",
            from_timezone="UTC",
            to_timezone="Invalid/Timezone"
        )

        assert isinstance(result, str)
        assert "Error" in result and "Unknown timezone" in result

    def test_convert_tz_error_handling(self):
        """测试时区转换错误处理"""
        result = convert_tz(
            time_input="invalid_time",
            to_timezone="UTC"
        )

        assert isinstance(result, str)
        assert "Error converting timezone" in result

    def test_parse_simple_string(self):
        """测试解析简单时间字符串"""
        result = parse("2023-12-25 15:30:00")

        assert isinstance(result, dict)
        assert "parsed_time" in result
        assert "unix_timestamp" in result
        assert "formatted" in result

    def test_parse_with_input_format(self):
        """测试带输入格式解析"""
        result = parse(
            time_string="25/12/2023 15:30",
            input_format="%d/%m/%Y %H:%M"
        )

        assert isinstance(result, dict)
        assert "parsed_time" in result

    def test_parse_with_timezone(self):
        """测试带时区解析"""
        result = parse(
            time_string="2023-12-25 15:30:00",
            timezone="Asia/Shanghai"
        )

        assert isinstance(result, dict)
        assert "parsed_time" in result

    def test_parse_with_output_timezone(self):
        """测试带输出时区解析"""
        result = parse(
            time_string="2023-12-25 15:30:00",
            timezone="local",
            output_timezone="UTC"
        )

        assert isinstance(result, dict)
        assert "parsed_time" in result

    def test_parse_error_handling(self):
        """测试解析错误处理"""
        result = parse("invalid_time_string")

        assert isinstance(result, str)
        assert "Error parsing time" in result

    def test_calc_diff_with_end_time(self):
        """测试计算时间差带结束时间"""
        result = calc_diff(
            start_time="2023-01-01 00:00:00",
            end_time="2023-01-01 01:30:00"
        )

        assert isinstance(result, str)
        assert "hour" in result or "minute" in result

    def test_calc_diff_without_end_time(self):
        """测试计算时间差不带结束时间（使用当前时间）"""
        with patch('app.tools.time_tools.datetime.datetime') as mock_datetime:
            mock_now = datetime.datetime(2023, 1, 1, 12, 0, 0)
            mock_datetime.now.return_value = mock_now
            mock_datetime.fromtimestamp = datetime.datetime.fromtimestamp

            # 需要模拟strptime的行为
            def mock_strptime(date_string, format_string):
                return datetime.datetime(2023, 1, 1, 10, 0, 0)

            with patch('app.tools.time_tools.parser.parse', return_value=datetime.datetime(2023, 1, 1, 10, 0, 0)):
                result = calc_diff(start_time="2023-01-01 10:00:00")

                assert isinstance(result, str)
                assert "hour" in result or "minute" in result

    def test_calc_diff_unix_timestamps(self):
        """测试Unix时间戳计算时间差"""
        result = calc_diff(
            start_time="1640995200",  # 2022-01-01 00:00:00 UTC
            end_time="1640998800",    # 2022-01-01 01:00:00 UTC
            unit="hours"
        )

        assert isinstance(result, (int, float))
        assert result == 1.0

    def test_calc_diff_different_units(self):
        """测试不同时间单位"""
        units = ["seconds", "minutes", "hours", "days", "weeks", "months", "years"]

        for unit in units:
            result = calc_diff(
                start_time="1640995200",
                end_time="1640998800",
                unit=unit,
                human_readable=False
            )

            assert isinstance(result, (int, float))

    def test_calc_diff_human_readable_false(self):
        """测试非人类可读格式"""
        result = calc_diff(
            start_time="1640995200",
            end_time="1640998800",
            human_readable=False
        )

        assert isinstance(result, (int, float))

    def test_calc_diff_error_handling(self):
        """测试时间差计算错误处理"""
        result = calc_diff(start_time="invalid_time")

        assert isinstance(result, str)
        assert "Error calculating difference" in result

    def test_get_tz_info_local(self):
        """测试获取本地时区信息"""
        result = get_tz_info(timezone="local")

        assert isinstance(result, dict)
        assert "timezone_name" in result
        assert "current_time" in result
        assert "current_time_iso" in result
        assert "utc_offset" in result
        assert "unix_timestamp" in result

    def test_get_tz_info_utc(self):
        """测试获取UTC时区信息"""
        result = get_tz_info(timezone="UTC")

        assert isinstance(result, dict)
        assert result["timezone_name"] == "UTC"

    def test_get_tz_info_specific_timezone(self):
        """测试获取特定时区信息"""
        result = get_tz_info(timezone="Asia/Shanghai", include_dst_info=True)

        assert isinstance(result, dict)
        assert result["timezone_name"] == "Asia/Shanghai"
        assert "is_dst" in result
        assert "timezone_abbreviation" in result

    def test_get_tz_info_without_dst(self):
        """测试不包含DST信息"""
        result = get_tz_info(timezone="UTC", include_dst_info=False)

        assert isinstance(result, dict)
        assert "is_dst" not in result
        assert "timezone_abbreviation" not in result

    def test_get_tz_info_unknown_timezone(self):
        """测试未知时区"""
        result = get_tz_info(timezone="Invalid/Timezone")

        assert isinstance(result, str)
        assert "Error" in result and "Unknown timezone" in result

    def test_get_tz_info_error_handling(self):
        """测试时区信息获取错误处理"""
        with patch('app.tools.time_tools.datetime.datetime.now', side_effect=Exception("Time error")):
            result = get_tz_info()

            assert isinstance(result, str)
            assert "Error getting timezone info" in result

    # ==== 边界条件和特殊情况测试 ====

    def test_time_tools_edge_cases(self):
        """测试时间工具边界条件"""
        # 测试0时间戳
        result = format(timestamp=0)
        assert isinstance(result, str)
        assert "1970" in result  # Unix纪元

        # 测试负时间戳
        result = format(timestamp=-86400)  # 1970-01-01前一天
        assert isinstance(result, str)
        assert "1969" in result

        # 测试很大的时间戳
        result = format(timestamp=2147483647)  # 2038年问题
        assert isinstance(result, str)

    def test_time_tools_precision(self):
        """测试时间工具精度"""
        result = calc_diff(
            start_time="1640995200",
            end_time="1640995200.5",
            unit="seconds",
            precision=3,
            human_readable=False
        )

        assert isinstance(result, float)
        assert result == 0.5

    def test_time_tools_complex_scenarios(self):
        """测试复杂时间场景"""
        # 跨年时间差计算
        result = calc_diff(
            start_time="2023-12-31 23:00:00",
            end_time="2024-01-01 01:00:00"
        )

        assert isinstance(result, str)
        assert "hour" in result

        # 闰年处理
        result = format(
            timestamp=datetime.datetime(2024, 2, 29, 12, 0, 0).timestamp(),
            format="custom",
            custom_format="%Y-%m-%d"
        )

        assert "2024-02-29" in result

if __name__ == "__main__":
    pytest.main([__file__, "-v"])