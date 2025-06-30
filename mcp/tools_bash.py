from croe import mcp
import subprocess


@mcp.tool()
async def bash(
    command: str, cwd: str = None, env: dict = None, timeout: int = None
) -> str:
    """

    :param command:
    :param cwd:
    :param env:
    :param timeout:
    :return:
    """
    return subprocess.check_output(
        command, shell=True, cwd=cwd, env=env, timeout=timeout
    ).decode("utf-8")