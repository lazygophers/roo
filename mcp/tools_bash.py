from croe import mcp
import subprocess
from pydantic import Field


@mcp.tool()
async def bash(
    command: str = Field(description="需要执行的shell命令字符串"),
    cwd: str = Field(description="可选的工作目录路径", default=None),
    env: dict = Field(description="可选的环境变量字典", default=None),
    timeout: int = Field(description="可选的超时时间（秒）", default=None),
) -> str:
    """
    执行shell命令并返回UTF-8解码后的标准输出
    """
    return subprocess.check_output(
        command, shell=True, cwd=cwd, env=env, timeout=timeout
    ).decode("utf-8")
