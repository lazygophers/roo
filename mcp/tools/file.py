import os
import shutil
from pydantic import BaseModel, Field
from core.croe import mcp


class FileInfo(BaseModel):
    """文件元数据模型，包含绝对路径、大小、权限等信息.

    Attributes:
        path: str - 文件绝对路径
        size: int - 文件大小（字节）
        is_dir: bool - 是否为目录类型
        mode: int - Unix权限模式（十进制）
        created_at: int - 创建时间戳（秒）
        modified_at: int - 最后修改时间戳（秒）
    """

    path: str = Field(description="文件绝对路径")
    size: int = Field(description="文件大小（字节）")
    is_dir: bool = Field(description="是否为目录类型")
    mode: int = Field(description="Unix文件权限模式（十进制表示）")
    created_at: int = Field(description="文件创建时间的时间戳（以秒为单位）")
    modified_at: int = Field(description="文件最后修改时间的时间戳（以秒为单位）")


@mcp.tool()
async def read_file(
    file_path: str = Field(description="需要读取的文件绝对路径"),
) -> str:
    """异步读取文件内容
    Returns:
        str: 文件内容字符串（失败时抛出异常）
    """
    with open(file_path, "r") as f:
        return f.read()


@mcp.tool()
async def write_file(
    file_path: str = Field(description="需要写入的文件绝对路径"),
    content: str = Field(description="要写入的内容"),
) -> bool:
    """写入文件内容
    Returns:
        bool: 写入是否成功
    """
    with open(file_path, "w") as f:
        f.write(content)
    return True


@mcp.tool()
async def delete_file(
    file_path: str = Field(description="需要删除的文件绝对路径"),
) -> bool:
    """删除文件
    Returns:
        bool: 删除是否成功
    """
    try:
        os.remove(file_path)
    except FileNotFoundError:
        return False
    return True


@mcp.tool()
async def mkdir(dir_path: str = Field(description="需要创建的目录绝对路径")) -> bool:
    """创建指定绝对路径的目录
    Returns:
        bool: 目录创建是否成功
    """
    os.mkdir(dir_path)
    return True


@mcp.tool()
async def rmdir(dir_path: str = Field(description="需要删除的目录绝对路径")) -> bool:
    """删除指定绝对路径的空目录
    Returns:
        bool: 目录删除是否成功
    """
    os.rmdir(dir_path)
    return True


@mcp.tool()
async def file_exists(path: str = Field(description="需要检查的绝对路径")) -> bool:
    """检查指定绝对路径是否存在
    Returns:
        bool: 绝对路径存在时返回True，否则返回False
    """
    return os.path.exists(path)


@mcp.tool()
async def file_is_dir(path: str = Field(description="需要检查的绝对路径")) -> bool:
    """检查指定绝对路径是否为目录.
    Returns:
        bool: 绝对路径存在且为目录时返回True
    """
    return os.path.isdir(path)


@mcp.tool()
async def file_is_file(path: str = Field(description="需要检查的绝对路径")) -> bool:
    """检查指定绝对路径是否为文件
    Returns:
        bool: 绝对路径存在且为文件时返回True
    """
    return os.path.isfile(path)


@mcp.tool()
async def ln(
    src: str = Field(description="源文件绝对路径"),
    dest: str = Field(description="目标文件绝对路径"),
) -> bool:
    """创建符号链接
    Returns:
        bool: 符号链接创建是否成功
    """
    os.symlink(src, dest)
    return True


@mcp.tool()
async def mv(
    src: str = Field(description="源绝对路径"),
    dest: str = Field(description="目标绝对路径"),
) -> bool:
    """移动/重命名文件或目录
    Returns:
        bool: 移动操作是否成功
    """
    try:
        os.rename(src, dest)
        return True
    except Exception as e:
        print(e)
        return False


@mcp.tool()
async def cp(
    src: str = Field(description="源绝对路径"),
    dest: str = Field(description="目标绝对路径"),
) -> bool:
    """复制文件或目录
    Returns:
        bool: 复制操作是否成功
    """
    try:
        shutil.copytree(src, dest)
    except FileNotFoundError:
        shutil.copy(src, dest)
    return True


@mcp.tool()
async def edit_file(
    path: str = Field(description="文件绝对路径"),
    line_range: str = Field(description="行范围", examples=["1-10"]),
) -> bool:
    """编辑文件内容（可指定行范围）
    Returns:
        bool: 文件编辑是否成功
    """
    with open(path, "r") as f:
        lines = f.readlines()
    if line_range:
        start, end = line_range.split("-")
        lines = lines[int(start) : int(end)]
    with open(path, "w") as f:
        f.writelines(lines)
    return True


@mcp.tool()
async def append_file(
    path: str = Field(description="文件绝对路径"),
    content: str = Field(description="追加的内容"),
) -> bool:
    """异步追加内容到文件末尾
    Returns:
        bool: 追加操作是否成功
    """
    with open(path, "a", encoding="utf8") as f:
        f.write(content)
        return True


@mcp.tool()
async def list_files(
    path: str = Field(description="目录绝对路径"),
    recursive: bool = Field(description="是否递归列出子目录", default=False),
) -> list[str]:
    """递归列出目录内容
    Returns:
        list[str]: 包含所有文件信息的列表对象
    """
    files = []

    for file in os.listdir(path):
        files.append(os.path.join(path, file))

        if os.path.isfile(os.path.join(path, file)):
            continue
        if not recursive:
            continue

        files.extend(await list_files(os.path.join(path, file), True))

    return files


@mcp.tool()
async def file_info(path: str = Field(description="文件绝对路径")) -> FileInfo:
    """获取指定绝对路径的文件元数据信息
    Returns:
        path (str): 文件绝对路径
        size (int): 文件大小（字节）
        is_dir (bool): 是否为目录类型
        mode (int): Unix权限模式（十进制）
        created_at (int): 创建时间戳（秒）
        modified_at (int): 最后修改时间戳（秒）
    """
    return FileInfo(
        path=path,
        size=os.path.getsize(path),
        is_dir=os.path.isdir(path),
        mode=os.stat(path).st_mode,
        created_at=int(os.path.getctime(path)),
        modified_at=int(os.path.getmtime(path)),
    )
