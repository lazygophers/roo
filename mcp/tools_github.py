import os.path
import time

from git import Repo, BadName, GitCommandError

from cache import Cache
from croe import mcp
from tools_file import read_file

cache = Cache(
    os.path.join("cache", "github", "cache")
)  # 初始化缓存实例，用于存储仓库更新时间等信息


async def get_github_repo(origin_name: str, repo_name: str) -> Repo:
    """
    获取或克隆GitHub仓库

    Args:
        origin_name: GitHub用户名/组织名
        repo_name: 仓库名称

    Returns:
        Repo: 本地仓库实例，用于后续git操作
    Raises:
        GitCommandError: 当克隆或初始化仓库失败时抛出
    """
    cache_path = os.path.join("cache", "github", origin_name, repo_name)
    if not os.path.exists(cache_path):
        Repo.clone_from(
            url="https://github.com/{}/{}.git".format(origin_name, repo_name),
            to_path=cache_path,
            mkdir=True,
        )

    repo = Repo.init(cache_path)
    return repo


@mcp.tool()
async def library_github_refresh(
    origin_name: str, repo_name: str, branch: str = "master", force: bool = True
):
    """
    刷新GitHub仓库代码

    Args:
        origin_name: GitHub用户名/组织名
        repo_name: 仓库名称
        branch: 分支名称（默认master）
        force: 是否强制刷新（默认True）

    功能：
        1. 检查分支是否存在
        2. 非强制模式下每5分钟更新一次
        3. 强制模式下强制拉取最新代码
    Raises:
        Exception: 当指定分支在远程不存在时抛出
        GitCommandError: 当git pull操作失败时抛出
    """
    repo = await get_github_repo(origin_name, repo_name)

    # 如果指定分支在远端不存在，则抛出异常
    if branch not in repo.remote().refs:
        raise Exception("分支不存在")

    if not force:
        updated_at = cache.get(
            "updated_at/{}/{}/{}".format(origin_name, repo_name, branch)
        )

        # 如果 5 分钟内更新过,则跳过更新
        if updated_at and time.time() - int(updated_at) < 5 * 60:
            return

    # 如果存在，则强制pull指定分支的代码
    repo.git.pull("origin", branch, "--force")

    cache.set(
        "updated_at/{}/{}/{}".format(origin_name, repo_name, branch),
        time.time(),
        ttl=5 * 60,
    )


@mcp.tool()
async def library_github_branches(origin_name: str, repo_name: str) -> list:
    """
    获取仓库所有分支列表

    Args:
        origin_name: GitHub用户名/组织名
        repo_name: 仓库名称

    Returns:
        List[str]: 包含所有分支名称的字符串列表
    Raises:
        GitCommandError: 当仓库初始化失败时抛出
    """
    await library_github_refresh(origin_name, repo_name, force=False)
    repo = await get_github_repo(origin_name, repo_name)

    return [head.name for head in repo.branches]


@mcp.tool()
async def library_github_list_files(
    origin_name: str, repo_name: str, path: str = ".", branch: str = "master"
) -> list:
    """
    列取仓库指定路径下的文件列表

    Args:
        origin_name: GitHub用户名/组织名
        repo_name: 仓库名称
        path: 需要列出的文件路径（默认根目录)
        branch: 分支名称（默认master）

    Returns:
        List[Dict]: 包含文件名、路径、类型、大小的字典列表
    Raises:
        ValueError: 当分支不存在或没有提交记录时抛出
        GitCommandError: 当git ls-tree命令执行失败时抛出
    """
    await library_github_refresh(origin_name, repo_name, force=False)
    repo = await get_github_repo(origin_name, repo_name)

    try:
        # 2. 获取目标分支的提交对象
        try:
            commit = repo.commit(branch)
        except BadName:
            raise ValueError(f"Branch {branch} not found in {origin_name}")

        # 3. 规范化路径（确保以/结尾并处理相对路径）
        normalized_path = path.rstrip("/") + "/"

        # 4. 使用git ls-tree命令获取指定路径的文件列表
        # -l 显示文件大小, -r 递归查找, -- 避免模式匹配
        ls_tree_output = repo.git.ls_tree(
            "-l",  # 显示文件大小
            "-r",  # 递归查找
            "--",  # 避免模式匹配
            commit.hexsha,
            normalized_path,
        )

        files = []
        for line in ls_tree_output.splitlines():
            parts = line.split()
            if len(parts) < 6:
                continue

            mode, typ, obj_id, size, name = (
                parts[0],
                parts[1],
                parts[2],
                parts[3],
                parts[4],
            )

            # 过滤非文件条目（目录/子模块等）
            if typ != "blob":
                continue

            # 构造完整路径（处理多级目录）
            full_path = os.path.join(normalized_path, name)

            files.append(
                {
                    "name": name,
                    "path": full_path,
                    "type": "file",
                    "size": int(size),
                }
            )

        return files

    except GitCommandError as e:
        if "does not have a commit" in str(e):
            raise ValueError(f"Branch {branch} has no commits") from e
        raise


@mcp.tool()
async def library_github_read_file(
    origin_name: str, repo_name: str, file_path: str, branch: str = "master"
):
    """
    读取仓库指定文件内容

    Args:
        origin_name: GitHub用户名/组织名
        repo_name: 仓库名称
        file_path: 文件路径
        branch: 分支名称（默认master）

    Returns:
        bytes: 文件内容的原始字节流
    Raises:
        GitCommandError: 当git checkout失败时抛出
        FileNotFoundError: 当指定文件路径不存在时抛出
    """
    await library_github_refresh(origin_name, repo_name, force=False)
    repo = await get_github_repo(origin_name, repo_name)
    repo.git.checkout(branch, force=True)
    return await read_file(repo.working_dir.join(file_path))