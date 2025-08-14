"""A tool to get the current timestamp as a Unix timestamp."""

from datetime import datetime, timezone


def get_timestamp(milliseconds: bool = False) -> int:
    """Returns the current UTC time as an integer Unix timestamp.

    A Unix timestamp represents the number of seconds that have elapsed since
    the epoch. This function allows for configurable precision.

    Args:
        milliseconds (bool): If True, returns the timestamp in milliseconds.
                             Defaults to False, returning seconds.

    Returns:
        int: The current UTC time as a Unix timestamp, either in seconds or
             milliseconds based on the `milliseconds` parameter.
    """
    timestamp = datetime.now(timezone.utc).timestamp()
    if milliseconds:
        return int(timestamp * 1000)
    return int(timestamp)