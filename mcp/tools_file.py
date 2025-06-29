import os
import shutil
from pydantic import BaseModel, Field
from croe import mcp


class FileInfo(BaseModel):
    """文件元数据模型，包含路径、大小、权限等信息.

    Attributes:
        path (str): 文件路径
        size (int): 文件大小（字节）
        is_dir (bool): 是否为目录类型
        mode (int): Unix权限模式（十进制）
        created_at (int): 创建时间戳（秒）
        modified_at (int): 最后修改时间戳（秒）
    """
    path: str = Field(..., description="文件路径")
    size: int = Field(..., description="文件大小（字节）")
    is_dir: bool = Field(..., description="是否为目录类型")
    mode: int = Field(..., description="Unix文件权限模式（十进制表示）")
    created_at: int = Field(..., description="文件创建时间的时间戳（以秒为单位）")
    modified_at: int = Field(..., description="文件最后修改时间的时间戳（以秒为单位）")


@mcp.tool()
async def read_file(file_path: str) -> str:
    """异步读取文件内容.

    Args:
        file_path (str): 需要读取的文件路径

    Returns:
        str: 文件内容字符串（失败时抛出异常）

    Raises:
        FileNotFoundError: 文件不存在时触发
    """
    with open(file_path, "r") as f:
        return f.read()


@mcp.tool()
async def write_file(file_path: str, content: str) -> bool:
    """异步写入文件内容.

    Args:
        file_path (str): 需要写入的文件路径
        content (str): 要写入的文件内容

    Returns:
        bool: 写入是否成功

    Raises:
        IOError: 文件写入异常时触发
    """
    with open(file_path, "w") as f:
        f.write(content)
    return True


@mcp.tool()
async def delete_file(file_path: str) -> bool:
    """异步删除文件.

    Args:
        file_path (str): 需要删除的文件路径

    Returns:
        bool: 删除是否成功

    Raises:
        FileNotFoundError: 文件不存在时触发
        PermissionError: 权限不足时触发
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False
    return True


@mcp.tool()
async def mkdir(dir_path: str) -> bool:
    """创建指定路径的目录.

    Args:
        dir_path (str): 需要创建的目录路径

    Returns:
        bool: 目录创建是否成功

    Raises:
        FileExistsError: 当目录已存在时触发
        PermissionError: 当权限不足时触发
    """
    os.mkdir(dir_path)
    return True


@mcp.tool()
async def rmdir(dir_path: str) -> bool:
    """删除指定路径的空目录.

    Args:
        dir_path (str): 需要删除的目录路径

    Returns:
        bool: 目录删除是否成功

    Raises:
        FileNotFoundError: 当目录不存在时触发
        OSError: 当目录非空或权限不足时触发
    """
    os.rmdir(dir_path)
    return True


@mcp.tool()
async def file_exists(path: str) -> bool:
    """检查指定路径是否存在.

    Args:
        path (str): 需要检查的文件/目录路径

    Returns:
        bool: 路径存在时返回True，否则返回False
    """
    return os.path.exists(path)


@mcp.tool()
async def file_is_dir(path: str) -> bool:
    """检查指定路径是否为目录.

    Args:
        path (str): 需要检查的路径

    Returns:
        bool: 路径存在且为目录时返回True
    """
    return os.path.isdir(path)


@mcp.tool()
async def file_is_file(path: str) -> bool:
    """检查指定路径是否为文件.

    Args:
        path (str): 需要检查的路径

    Returns:
        bool: 路径存在且为文件时返回True
    """
    return os.path.isfile(path)


@mcp.tool()
async def ln(src: str, dest: str) -> bool:
    """创建符号链接.

    Args:
        src (str): 源文件路径
        dest (str): 目标链接路径

    Returns:
        bool: 符号链接创建是否成功

    Raises:
        OSError: 当操作失败时触发
    """
    os.symlink(src, dest)
    return True


@mcp.tool()
async def mv(src: str, dest: str) -> bool:
    """移动/重命名文件或目录.

    Args:
        src (str): 源路径
        dest (str): 目标路径

    Returns:
        bool: 移动操作是否成功

    Raises:
        FileNotFoundError: 当源路径不存在时触发
        FileExistsError: 当目标路径已存在时触发
    """
    try:
        os.rename(src, dest)
        return True
    except Exception as e:
        print(e)
        return False


@mcp.tool()
async def cp(src: str, dest: str) -> bool:
    """复制文件或目录.

    Args:
        src (str): 源路径
        dest (str): 目标路径

    Returns:
        bool: 复制操作是否成功

    Raises:
        FileNotFoundError: 当源路径不存在时触发
        FileExistsError: 当目标路径已存在时触发
    """
    try:
        shutil.copytree(src, dest)
    except FileNotFoundError:
        shutil.copy(src, dest)
    return True


@mcp.tool()
async def edit_file(path: str, line_range: str = None) -> bool:
    """编辑文件内容（可指定行范围）.

    Args:
        path (str): 文件路径
        line_range (str, optional): 行范围字符串（如"1-3"），默认保留全部内容

    Returns:
        bool: 文件编辑是否成功

    Raises:
        FileNotFoundError: 当文件不存在时触发
    """
    with open(path, "r") as f:
        lines = f.readlines()
    if line_range:
        start, end = line_range.split("-")
        lines = lines[int(start):int(end)]
    with open(path, "w") as f:
        f.writelines(lines)
    return True


@mcp.tool()
async def append_file(path: str, content: str) -> bool:
    """异步追加内容到文件末尾.

    Args:
        path (str): 文件路径
        content (str): 要追加的内容字符串

    Returns:
        bool: 追加操作是否成功

    Raises:
        IOError: 文件写入异常时触发
    """
    with open(path, 'a', encoding='utf8') as f:
        f.write(content)
        return True


@mcp.tool()
async def list_files(path: str, recursive: bool = False) -> list[FileInfo]:
    """递归列出目录内容（含子目录）.

    Args:
        path (str): 需要遍历的目录路径
        recursive (bool, optional): 是否递归子目录，默认False

    Returns:
        list[FileInfo]: 包含所有文件信息的列表对象
    """
    files = []

    for file in os.listdir(path):
        files.append(await file_info(os.path.join(path, file)))

        if os.path.isfile(os.path.join(path, file)):
            continue
        if not recursive:
            continue

        files.extend(await list_files(os.path.join(path, file), True))

    return files


@mcp.tool()
async def file_info(path: str) -> FileInfo:
    """获取指定路径的文件元数据信息.

    Args:
        path (str): 需要分析的文件/目录路径

    Returns:
        path (str): 文件路径
        size (int): 文件大小（字节）
        is_dir (bool): 是否为目录类型
        mode (int): Unix权限模式（十进制）
        created_at (int): 创建时间戳（秒）
        modified_at (int): 最后修改时间戳（秒）

    Raises:
        FileNotFoundError: 当指定路径不存在时触发
        PermissionError: 当没有访问权限时触发
    """
    return FileInfo(
        path=path,
        size=os.path.getsize(path),
        is_dir=os.path.isdir(path),
        mode=os.stat(path).st_mode,
        created_at=int(os.path.getctime(path)),
        modified_at=int(os.path.getmtime(path)),
    )