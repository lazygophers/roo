from croe import mcp
import subprocess


@mcp.tool()
async def bash(
    command: str, cwd: str = None, env: dict = None, timeout: int = None
) -> str:
    """
    执行shell命令并返回UTF-8解码后的标准输出
    
    :param command: 需要执行的shell命令字符串
    :param cwd: 可选的工作目录路径
    :param env: 可选的环境变量字典
    :param timeout: 可选的命令超时时间（秒）
    :return: 命令执行结果的UTF-8字符串输出
    :raises subprocess.CalledProcessError: 当命令返回非零退出状态时抛出
    :raises subprocess.TimeoutExpired: 当命令执行超时时抛出
    """
    return subprocess.check_output(
        command, shell=True, cwd=cwd, env=env, timeout=timeout
    ).decode("utf-8")