"""Comprehensive test suite for the timestamp tool.

This module provides exhaustive testing for the get_timestamp function,
ensuring complete code coverage and robust validation of all functionality.

Test Categories:
    - Default behavior (seconds precision)
    - Milliseconds precision
    - Type validation
    - Temporal consistency
    - Edge cases and boundaries
"""

import time
from datetime import UTC, datetime
from typing import Any
from unittest.mock import MagicMock, patch

import pytest

from src.tools.timestamp import get_timestamp


class TestGetTimestamp:
    """Test suite for the get_timestamp function."""

    # ========== Default Behavior Tests ==========

    def test_default_returns_seconds(self) -> None:
        """Test that default behavior returns Unix timestamp in seconds.

        Validates:
            - Function can be called without arguments
            - Returns a valid timestamp in seconds
            - Result is an integer
        """
        result = get_timestamp()

        # Verify the result is an integer
        assert isinstance(result, int), "Result must be an integer"

        # Verify it's a reasonable Unix timestamp (after year 2020)
        assert result > 1577836800, "Timestamp should be after 2020-01-01"

        # Verify it's not in milliseconds (should be smaller)
        current_time_ms = int(time.time() * 1000)
        assert result < current_time_ms, "Default should return seconds, not milliseconds"

    def test_explicit_false_returns_seconds(self) -> None:
        """Test that explicitly passing False returns seconds.

        Ensures that get_timestamp(milliseconds=False) behaves
        identically to get_timestamp().
        """
        result = get_timestamp(milliseconds=False)

        assert isinstance(result, int), "Result must be an integer"

        # Compare with current time to ensure it's in seconds
        current_time_s = int(time.time())
        assert abs(result - current_time_s) <= 1, "Should be within 1 second of current time"

    # ========== Milliseconds Precision Tests ==========

    def test_milliseconds_returns_milliseconds(self) -> None:
        """Test that milliseconds=True returns timestamp in milliseconds.

        Validates:
            - Returns milliseconds when requested
            - Result is still an integer
            - Value is appropriately scaled
        """
        result = get_timestamp(milliseconds=True)

        assert isinstance(result, int), "Result must be an integer"

        # Verify it's in milliseconds range
        current_time_ms = int(time.time() * 1000)
        assert abs(result - current_time_ms) <= 1000, "Should be within 1 second of current time"

        # Verify it's larger than seconds would be
        current_time_s = int(time.time())
        assert result > current_time_s, "Milliseconds should be larger than seconds"

    def test_milliseconds_precision_difference(self) -> None:
        """Test that milliseconds provides higher precision than seconds.

        Verifies that the milliseconds timestamp has more significant
        digits than the seconds timestamp.
        """
        seconds_ts = get_timestamp(milliseconds=False)
        milliseconds_ts = get_timestamp(milliseconds=True)

        # Milliseconds should be approximately 1000x larger
        ratio = milliseconds_ts / seconds_ts
        assert 990 < ratio < 1010, f"Ratio should be ~1000, got {ratio}"

    # ========== Type Validation Tests ==========

    def test_return_type_always_int(self) -> None:
        """Test that the function always returns an integer.

        Ensures type consistency across all valid inputs.
        """
        # Test various inputs
        test_cases = [
            {},  # No arguments
            {"milliseconds": False},
            {"milliseconds": True},
        ]

        for kwargs in test_cases:
            result = get_timestamp(**kwargs)
            assert isinstance(
                result, int
            ), f"Failed for kwargs={kwargs}: expected int, got {type(result)}"

    def test_no_float_leakage(self) -> None:
        """Test that internal float calculations don't leak to output.

        The function uses time.time() which returns float,
        but should always convert to int before returning.
        """
        with patch("src.tools.timestamp.time") as mock_time:
            # Mock time.time() to return a float with decimals
            mock_time.time.return_value = 1234567890.987654

            # Test seconds
            result_s = get_timestamp(milliseconds=False)
            assert result_s == 1234567890, "Should truncate to integer seconds"
            assert isinstance(result_s, int), "Must be integer, not float"

            # Test milliseconds
            result_ms = get_timestamp(milliseconds=True)
            assert result_ms == 1234567890987, "Should truncate to integer milliseconds"
            assert isinstance(result_ms, int), "Must be integer, not float"

    # ========== Temporal Consistency Tests ==========

    def test_timestamp_increases_over_time(self) -> None:
        """Test that consecutive calls return increasing timestamps.

        Validates temporal consistency and monotonic behavior.
        """
        first = get_timestamp()
        time.sleep(0.01)  # Small delay to ensure time passes
        second = get_timestamp()

        assert second >= first, "Later timestamp should be greater or equal"

        # Test with milliseconds for finer granularity
        first_ms = get_timestamp(milliseconds=True)
        time.sleep(0.001)  # 1ms delay
        second_ms = get_timestamp(milliseconds=True)

        assert second_ms > first_ms, "Later millisecond timestamp should be greater"

    def test_reasonable_time_range(self) -> None:
        """Test that timestamps are within reasonable bounds.

        Ensures the timestamp represents a time between:
        - Not before year 2020 (past boundary)
        - Not after year 2100 (future boundary)
        """
        result = get_timestamp()

        # Define reasonable bounds
        min_timestamp = 1577836800  # 2020-01-01 00:00:00 UTC
        max_timestamp = 4102444800  # 2100-01-01 00:00:00 UTC

        assert (
            min_timestamp < result < max_timestamp
        ), f"Timestamp {result} outside reasonable range [{min_timestamp}, {max_timestamp}]"

    # ========== Edge Cases and Mock Tests ==========

    @patch("src.tools.timestamp.time")
    def test_mock_specific_time(self, mock_time: MagicMock) -> None:
        """Test with mocked specific time for deterministic testing.

        Uses mock to test exact values and conversions.
        """
        # Mock a specific time: 2024-01-15 12:30:45.123456 UTC
        mock_time.time.return_value = 1705323045.123456

        # Test seconds
        result_s = get_timestamp(milliseconds=False)
        assert result_s == 1705323045, "Should return exact second timestamp"

        # Test milliseconds
        result_ms = get_timestamp(milliseconds=True)
        assert result_ms == 1705323045123, "Should return exact millisecond timestamp"

    @patch("src.tools.timestamp.time")
    def test_epoch_time(self, mock_time: MagicMock) -> None:
        """Test behavior at Unix epoch (1970-01-01 00:00:00 UTC).

        Edge case: ensures correct handling of epoch time.
        """
        mock_time.time.return_value = 0.0

        assert get_timestamp(milliseconds=False) == 0, "Epoch in seconds should be 0"
        assert get_timestamp(milliseconds=True) == 0, "Epoch in milliseconds should be 0"

    @patch("src.tools.timestamp.time")
    def test_negative_timestamp(self, mock_time: MagicMock) -> None:
        """Test behavior with pre-epoch times (negative timestamps).

        Edge case: times before 1970-01-01 should work correctly.
        """
        # Mock a time before epoch: 1969-12-31 23:59:59 UTC
        mock_time.time.return_value = -1.0

        assert get_timestamp(milliseconds=False) == -1, "Should handle negative timestamps"
        assert get_timestamp(milliseconds=True) == -1000, "Should handle negative milliseconds"

    @patch("src.tools.timestamp.time")
    def test_large_future_timestamp(self, mock_time: MagicMock) -> None:
        """Test behavior with very large future timestamps.

        Edge case: ensures no overflow or precision issues.
        Note: int() rounds towards zero, so 253402300799.999999 becomes 253402300799
        """
        # Mock a far future time: year 9999
        # Use a value that won't cause rounding issues
        mock_time.time.return_value = 253402300799.0

        result_s = get_timestamp(milliseconds=False)
        result_ms = get_timestamp(milliseconds=True)

        assert result_s == 253402300799, "Should handle large timestamps"
        assert result_ms == 253402300799000, "Should handle large millisecond timestamps"

    # ========== Performance and Stress Tests ==========

    def test_performance_multiple_calls(self) -> None:
        """Test that multiple rapid calls work correctly.

        Stress test to ensure the function handles rapid successive calls.
        """
        results = []
        for _ in range(100):
            results.append(get_timestamp(milliseconds=True))

        # All results should be integers
        assert all(isinstance(r, int) for r in results), "All results must be integers"

        # Results should be non-decreasing (allowing for same timestamps)
        for i in range(1, len(results)):
            assert results[i] >= results[i - 1], "Timestamps should not decrease"

    def test_concurrent_behavior(self) -> None:
        """Test that the function behaves correctly when called concurrently.

        Note: This is a basic test. Full concurrency testing would require
        threading or multiprocessing.
        """
        import concurrent.futures

        def get_both_formats() -> tuple[int, int]:
            """Helper to get both timestamp formats."""
            return get_timestamp(False), get_timestamp(True)

        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(get_both_formats) for _ in range(10)]
            results = [f.result() for f in concurrent.futures.as_completed(futures)]

        # Verify all results are valid
        for seconds, milliseconds in results:
            assert isinstance(seconds, int), "Seconds must be int"
            assert isinstance(milliseconds, int), "Milliseconds must be int"
            # Rough validation of the relationship
            assert milliseconds // 1000 <= seconds + 1, "Milliseconds and seconds should be related"

    # ========== Documentation and API Tests ==========

    def test_function_signature(self) -> None:
        """Test that the function signature matches expectations.

        Validates that the function accepts the expected parameters.
        """
        import inspect

        sig = inspect.signature(get_timestamp)
        params = sig.parameters

        # Check parameter exists and has correct default
        assert "milliseconds" in params, "Function should have 'milliseconds' parameter"
        assert params["milliseconds"].default is False, "Default should be False"

        # Check return annotation
        assert sig.return_annotation == int, "Return type should be annotated as int"

    def test_docstring_present(self) -> None:
        """Test that the function has proper documentation.

        Ensures the function is properly documented for users.
        """
        assert get_timestamp.__doc__ is not None, "Function should have a docstring"
        assert len(get_timestamp.__doc__) > 50, "Docstring should be comprehensive"

        # Check for key documentation elements
        doc_lower = get_timestamp.__doc__.lower()
        assert "unix" in doc_lower, "Should mention Unix timestamp"
        assert "milliseconds" in doc_lower, "Should document milliseconds parameter"
        assert "int" in doc_lower, "Should mention return type"


class TestEdgeCasesAndValidation:
    """Additional edge case and validation tests."""

    def test_invalid_parameter_types(self) -> None:
        """Test behavior with invalid parameter types.

        The function should handle type errors gracefully.
        """
        # These should raise TypeErrors due to type hints
        invalid_values: list[Any] = [
            1,  # Integer instead of bool
            "true",  # String instead of bool
            None,  # None instead of bool
            1.0,  # Float instead of bool
            [],  # List instead of bool
        ]

        for invalid in invalid_values:
            # The function might accept truthy/falsy values
            # Let's test the actual behavior
            try:
                result = get_timestamp(milliseconds=invalid)
                # If it doesn't raise, verify it still returns int
                assert isinstance(result, int), f"Should return int even with invalid={invalid}"
            except TypeError:
                # This is also acceptable behavior
                pass

    def test_keyword_only_argument(self) -> None:
        """Test that milliseconds can be passed as keyword argument.

        Ensures proper keyword argument handling.
        """
        # Should work with keyword
        result_kw = get_timestamp(milliseconds=True)
        assert isinstance(result_kw, int)

        # Should also work with positional (though not recommended)
        result_pos = get_timestamp(True)
        assert isinstance(result_pos, int)

    @patch("src.tools.timestamp.time")
    def test_float_precision_edge_cases(self, mock_time: MagicMock) -> None:
        """Test edge cases related to float precision.

        Ensures proper handling of float precision issues.
        """
        test_cases = [
            (1234567890.999999, 1234567890, 1234567890999),  # Round down
            (1234567890.500000, 1234567890, 1234567890500),  # Exact half
            (1234567890.000001, 1234567890, 1234567890000),  # Very small fraction
            (0.999999, 0, 999),  # Less than 1 second
            (0.001, 0, 1),  # 1 millisecond
        ]

        for timestamp_float, expected_s, expected_ms in test_cases:
            mock_time.time.return_value = timestamp_float

            assert get_timestamp(False) == expected_s, f"Failed for {timestamp_float} seconds"
            assert get_timestamp(True) == expected_ms, f"Failed for {timestamp_float} milliseconds"


if __name__ == "__main__":
    """Allow running tests directly with python -m pytest."""
    pytest.main([__file__, "-v", "--color=yes"])
