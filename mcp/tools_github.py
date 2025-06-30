import os.path
import time

from git import Repo, BadName, GitCommandError
from pydantic import Field

from cache import Cache
from croe import mcp
from tools_file import read_file

cache = Cache(
    os.path.join("cache", "github", "cache")
)  # 初始化缓存实例，用于存储仓库更新时间等信息


async def get_github_repo(
    origin_name: str = Field(
        description="GitHub用户名/组织名", examples=["lazygophers", "google"]
    ),
    repo_name: str = Field(
        description="仓库名", examples=["tensorflow", "pytorch", "roo"]
    ),
) -> Repo:
    """
    获取或克隆GitHub仓库
    Returns:
        Repo: 本地仓库实例，用于后续git操作
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
    origin_name: str = Field(
        description="GitHub用户名/组织名", examples=["lazygophers", "google"]
    ),
    repo_name: str = Field(
        description="仓库名", examples=["tensorflow", "pytorch", "roo"]
    ),
    branch: str = Field(
        description="分支名", default="master", examples=["master", "main", "dev"]
    ),
    force: bool = Field(description="是否强制刷新", default=True),
):
    """
    刷新GitHub仓库代码
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
async def library_github_branches(
    origin_name: str = Field(
        description="GitHub用户名/组织名", examples=["lazygophers", "google"]
    ),
    repo_name: str = Field(
        description="仓库名", examples=["tensorflow", "pytorch", "roo"]
    ),
) -> list:
    """
    获取仓库所有分支列表
    Returns:
        List[str]: 包含所有分支名称的字符串列表
    """
    await library_github_refresh(origin_name, repo_name, force=False)
    repo = await get_github_repo(origin_name, repo_name)

    return [head.name for head in repo.branches]


@mcp.tool()
async def library_github_list_files(
    origin_name: str = Field(
        description="GitHub用户名/组织名", examples=["lazygophers", "google"]
    ),
    repo_name: str = Field(
        description="仓库名", examples=["tensorflow", "pytorch", "roo"]
    ),
    path: str = Field(description="文件路径", examples=["src"]),
    branch: str = Field(
        description="分支名", default="master", examples=["master", "main", "dev"]
    ),
) -> list:
    """
    列取仓库指定路径下的文件列表
    Returns:
        List[Dict]: 包含文件名、路径、类型、大小的字典列表
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
    origin_name: str = Field(
        description="GitHub用户名/组织名", examples=["lazygophers", "google"]
    ),
    repo_name: str = Field(
        description="仓库名", examples=["tensorflow", "pytorch", "roo"]
    ),
    file_path: str = Field(description="文件路径", examples=["README.md"]),
    branch: str = Field(
        description="分支名", default="master", examples=["master", "main", "dev"]
    ),
):
    """
    读取仓库指定文件内容
    Returns:
        bytes: 文件内容的原始字节流
    """
    await library_github_refresh(origin_name, repo_name, force=False)
    repo = await get_github_repo(origin_name, repo_name)
    repo.git.checkout(branch, force=True)
    return await read_file(repo.working_dir.join(file_path))
