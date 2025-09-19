"""
安全日志单元测试
Secure Logging Unit Tests
"""

import pytest
from app.core.secure_logging import (
    sanitize_for_log,
    secure_log_format,
    secure_log_key_value
)


class TestSanitizeForLog:
    """测试日志输入净化函数"""

    def test_sanitize_none_value(self):
        """测试None值处理"""
        result = sanitize_for_log(None)
        assert result == "None"

    def test_sanitize_normal_string(self):
        """测试正常字符串"""
        normal_strings = [
            "hello world",
            "user123",
            "simple text",
            "file.txt",
            "normal-value_123"
        ]

        for text in normal_strings:
            result = sanitize_for_log(text)
            assert result == text

    def test_sanitize_newlines_and_carriage_returns(self):
        """测试换行符和回车符处理"""
        test_cases = [
            ("line1\nline2", "line1 line2"),
            ("line1\r\nline2", "line1 line2"),
            ("line1\rline2", "line1 line2"),
            ("multiple\n\r\nlines\nhere", "multiple  lines here"),
            ("\n\r\n", "  ")
        ]

        for input_text, expected in test_cases:
            result = sanitize_for_log(input_text)
            assert result == expected

    def test_sanitize_control_characters(self):
        """测试控制字符处理"""
        # 测试各种控制字符
        control_chars = [
            "\x00",  # NULL
            "\x01",  # SOH
            "\x08",  # Backspace
            "\x0B",  # Vertical Tab
            "\x0C",  # Form Feed
            "\x0E",  # Shift Out
            "\x1F",  # Unit Separator
            "\x7F"   # DEL
        ]

        for char in control_chars:
            text_with_control = f"before{char}after"
            result = sanitize_for_log(text_with_control)
            assert char not in result
            assert result == "beforeafter"

    def test_sanitize_keep_safe_characters(self):
        """测试保留安全字符"""
        safe_text = "Hello\tWorld 123!@#$%^&*(){}[]"
        result = sanitize_for_log(safe_text)
        assert result == safe_text

    def test_sanitize_long_string(self):
        """测试长字符串截断"""
        long_string = "x" * 300
        result = sanitize_for_log(long_string)

        assert len(result) == 200
        assert result.endswith("...")
        assert result == "x" * 197 + "..."

    def test_sanitize_exactly_max_length(self):
        """测试正好最大长度的字符串"""
        max_length_string = "x" * 200
        result = sanitize_for_log(max_length_string)
        assert result == max_length_string
        assert not result.endswith("...")

    def test_sanitize_different_types(self):
        """测试不同数据类型"""
        test_cases = [
            (123, "123"),
            (45.67, "45.67"),
            (True, "True"),
            (False, "False"),
            ([], "[]"),
            ({}, "{}"),
            ({"key": "value"}, "{'key': 'value'}"),
            ([1, 2, 3], "[1, 2, 3]")
        ]

        for input_value, expected in test_cases:
            result = sanitize_for_log(input_value)
            assert result == expected

    def test_sanitize_complex_injection_attempt(self):
        """测试复杂的日志注入攻击尝试"""
        injection_attempts = [
            "normal\n2023-01-01 FAKE LOG ENTRY\nreal",
            "user\r\nERROR: Fake error message",
            "data\x00\x01INJECTED\x7F",
            f"flood{'A' * 500}attack"
        ]

        for attempt in injection_attempts:
            result = sanitize_for_log(attempt)

            # 不应包含换行符
            assert "\n" not in result
            assert "\r" not in result

            # 不应包含控制字符
            for i in range(32):
                if i not in [9, 10, 13]:  # 除了tab, LF, CR
                    assert chr(i) not in result

            # 长度应该被限制
            assert len(result) <= 200

    def test_sanitize_unicode_characters(self):
        """测试Unicode字符处理"""
        unicode_text = "用户名123 🚀 émojis"
        result = sanitize_for_log(unicode_text)
        assert result == unicode_text

    def test_sanitize_empty_string(self):
        """测试空字符串"""
        result = sanitize_for_log("")
        assert result == ""

    def test_sanitize_whitespace_only(self):
        """测试只包含空白字符的字符串"""
        whitespace_strings = [
            "   ",
            "\t\t",
            "   \t   ",
        ]

        for text in whitespace_strings:
            result = sanitize_for_log(text)
            assert result == text


class TestSecureLogFormat:
    """测试安全日志格式化函数"""

    def test_secure_log_format_basic(self):
        """测试基本日志格式化"""
        template = "User '{user}' performed action '{action}'"
        result = secure_log_format(template, user="john", action="login")
        assert result == "User 'john' performed action 'login'"

    def test_secure_log_format_with_injection(self):
        """测试包含注入攻击的格式化"""
        template = "User '{user}' accessed file '{file}'"
        malicious_user = "admin\n2023-01-01 FAKE: Unauthorized access"
        malicious_file = "secret.txt\rDELETED: All files"

        result = secure_log_format(
            template,
            user=malicious_user,
            file=malicious_file
        )

        # 验证恶意内容被净化
        assert "\n" not in result
        assert "\r" not in result
        assert "User 'admin 2023-01-01 FAKE: Unauthorized access' accessed file 'secret.txt DELETED: All files'" == result

    def test_secure_log_format_multiple_placeholders(self):
        """测试多个占位符"""
        template = "Event: {event}, User: {user}, IP: {ip}, Time: {time}"
        result = secure_log_format(
            template,
            event="login",
            user="testuser",
            ip="192.168.1.1",
            time="2023-01-01T12:00:00"
        )

        expected = "Event: login, User: testuser, IP: 192.168.1.1, Time: 2023-01-01T12:00:00"
        assert result == expected

    def test_secure_log_format_no_placeholders(self):
        """测试没有占位符的模板"""
        template = "Static log message"
        result = secure_log_format(template)
        assert result == template

    def test_secure_log_format_with_none_values(self):
        """测试包含None值的格式化"""
        template = "User: {user}, Session: {session}"
        result = secure_log_format(template, user="john", session=None)
        assert result == "User: john, Session: None"

    def test_secure_log_format_with_complex_objects(self):
        """测试复杂对象的格式化"""
        template = "Request data: {data}, Config: {config}"
        data = {"key": "value\ninjection", "list": [1, 2, 3]}
        config = {"setting": "value\rattack"}

        result = secure_log_format(template, data=data, config=config)

        assert "\n" not in result
        assert "\r" not in result
        assert "Request data:" in result
        assert "Config:" in result

    def test_secure_log_format_long_values(self):
        """测试长值的格式化"""
        template = "Long data: {data}"
        long_data = "x" * 300

        result = secure_log_format(template, data=long_data)

        assert len(result) < len(template) + 300  # 应该被截断
        assert "..." in result


class TestSecureLogKeyValue:
    """测试安全键值日志函数"""

    def test_secure_log_key_value_key_only(self):
        """测试仅键的日志"""
        result = secure_log_key_value("cache_key")
        assert result == "key='cache_key'"

    def test_secure_log_key_value_key_and_value(self):
        """测试键值对日志"""
        result = secure_log_key_value("user_id", "12345")
        assert result == "key='user_id', value='12345'"

    def test_secure_log_key_value_with_injection(self):
        """测试包含注入攻击的键值"""
        malicious_key = "key\nfake_log_entry"
        malicious_value = "value\rmalicious_content"

        result = secure_log_key_value(malicious_key, malicious_value)

        assert "\n" not in result
        assert "\r" not in result
        assert result == "key='key fake_log_entry', value='value malicious_content'"

    def test_secure_log_key_value_none_value(self):
        """测试None值"""
        result = secure_log_key_value("test_key", None)
        assert result == "key='test_key'"

    def test_secure_log_key_value_complex_types(self):
        """测试复杂类型"""
        complex_key = {"nested": "key"}
        complex_value = [1, 2, {"inner": "value"}]

        result = secure_log_key_value(complex_key, complex_value)

        assert "key=" in result
        assert "value=" in result
        assert "nested" in result
        assert "inner" in result

    def test_secure_log_key_value_empty_strings(self):
        """测试空字符串"""
        result = secure_log_key_value("", "")
        assert result == "key='', value=''"

    def test_secure_log_key_value_long_inputs(self):
        """测试长输入"""
        long_key = "k" * 300
        long_value = "v" * 300

        result = secure_log_key_value(long_key, long_value)

        # 都应该被截断
        assert "..." in result
        assert len(result) < 600  # 应该比原始长度短很多


class TestSecureLoggingIntegration:
    """测试安全日志集成功能"""

    def test_real_world_scenarios(self):
        """测试真实世界场景"""
        scenarios = [
            {
                "desc": "SQL注入尝试",
                "input": "'; DROP TABLE users; --",
                "expected_safe": True
            },
            {
                "desc": "XSS尝试",
                "input": "<script>alert('xss')</script>",
                "expected_safe": True
            },
            {
                "desc": "日志伪造尝试",
                "input": "user\n2023-01-01 [ERROR] Fake error message",
                "expected_safe": True
            },
            {
                "desc": "路径遍历尝试",
                "input": "../../../etc/passwd",
                "expected_safe": True
            },
            {
                "desc": "正常用户输入",
                "input": "normal_user_123",
                "expected_safe": True
            }
        ]

        for scenario in scenarios:
            result = sanitize_for_log(scenario["input"])

            # 基本安全检查
            assert "\n" not in result
            assert "\r" not in result
            assert len(result) <= 200

            # 应该不为空（除非输入为空）
            if scenario["input"]:
                assert result

    def test_performance_with_large_inputs(self):
        """测试大输入的性能"""
        large_input = "x" * 10000

        # 应该能快速处理大输入
        result = sanitize_for_log(large_input)

        assert len(result) == 200
        assert result.endswith("...")

    def test_thread_safety(self):
        """测试线程安全性"""
        import threading
        import time

        results = []

        def sanitize_worker(value):
            result = sanitize_for_log(f"thread_{value}\ninjection")
            results.append(result)

        # 创建多个线程
        threads = []
        for i in range(10):
            thread = threading.Thread(target=sanitize_worker, args=(i,))
            threads.append(thread)
            thread.start()

        # 等待所有线程完成
        for thread in threads:
            thread.join()

        # 验证结果
        assert len(results) == 10
        for result in results:
            assert "\n" not in result
            assert "thread_" in result
            assert " injection" in result  # 换行符应该变成空格

    def test_encoding_handling(self):
        """测试编码处理"""
        test_cases = [
            "简体中文",
            "繁體中文",
            "日本語",
            "한국어",
            "العربية",
            "Русский",
            "🎉🚀🎯💫",
            "Mixed 中文 English 🌟"
        ]

        for text in test_cases:
            result = sanitize_for_log(text)
            assert result == text  # Unicode字符应该保持不变

    def test_edge_case_combinations(self):
        """测试边缘情况组合"""
        edge_cases = [
            "\x00\n\r\x1F" + "normal" + "\x7F" * 100,
            "\n" * 50 + "content" + "\r" * 50,
            "a" * 150 + "\n\r" + "b" * 150,
            "\t\n\r\x01\x02\x03normal\x04\x05\x06\t"
        ]

        for case in edge_cases:
            result = sanitize_for_log(case)

            # 基本安全检查
            assert "\n" not in result
            assert "\r" not in result
            assert len(result) <= 200

            # 应该包含"normal"或"content"部分（除了第三个测试用例，它太长被截断了）
            if "a" * 150 not in case:  # 不是第三个测试用例
                assert "normal" in result or "content" in result