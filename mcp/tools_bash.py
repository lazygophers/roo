from croe import mcp
import subprocess


@mcp.tool()
async def bash(
    command: str, cwd: str = None, env: dict = None, timeout: int = None
) -> str:
    """
    执行 bash 命令

    Args:
        command (str): 脚本
        cwd(str): 工作目录
        env(dict): 环境变量
        timeout(int): 超时时间

    Returns:
        str: 命令执行结果输出
    """
    return subprocess.check_output(
        command, shell=True, cwd=cwd, env=env, timeout=timeout
    ).decode("utf-8")
