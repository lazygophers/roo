"""
GitHub API 工具集
提供完整的 GitHub REST API v3 接口支持
基于 GitHub 官方 OpenAPI 规范实现
"""

import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Union
import requests
from urllib.parse import urljoin

from app.core.logging import setup_logging
from app.core.secure_logging import sanitize_for_log

logger = setup_logging("INFO")

class GitHubAPIService:
    """GitHub API 服务类"""

    def __init__(self, token: Optional[str] = None, base_url: str = "https://api.github.com"):
        """
        初始化 GitHub API 服务

        Args:
            token: GitHub Personal Access Token or App Token
            base_url: GitHub API 基础 URL，默认为公共 GitHub
        """
        self.token = token
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()

        # 设置默认请求头
        self.session.headers.update({
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'LazyAI-Studio-GitHub-Tools/1.0'
        })

        # 如果提供了 token，设置认证头
        if self.token:
            self.session.headers['Authorization'] = f'token {self.token}'

        logger.info("GitHub API Service initialized")

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict[str, Any]:
        """
        发起 API 请求的通用方法

        Args:
            method: HTTP 方法 (GET, POST, PUT, DELETE 等)
            endpoint: API 端点
            **kwargs: 其他请求参数

        Returns:
            API 响应数据

        Raises:
            Exception: 当 API 请求失败时
        """
        url = urljoin(self.base_url + '/', endpoint.lstrip('/'))

        try:
            response = self.session.request(method, url, **kwargs)

            # 处理速率限制
            if response.status_code == 429:
                reset_time = int(response.headers.get('X-RateLimit-Reset', time.time() + 60))
                sleep_time = max(reset_time - int(time.time()), 60)
                logger.warning(f"Rate limit exceeded, sleeping for {sleep_time} seconds")
                time.sleep(sleep_time)
                # 重试请求
                response = self.session.request(method, url, **kwargs)

            response.raise_for_status()

            # 尝试解析 JSON 响应
            try:
                return response.json()
            except json.JSONDecodeError:
                return {"message": "Success", "status_code": response.status_code}

        except requests.exceptions.RequestException as e:
            logger.error(f"GitHub API request failed: {sanitize_for_log(str(e))}")
            raise Exception(f"GitHub API 请求失败: {str(e)}")

    # ============ 仓库相关操作 ============

    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库信息"""
        return self._make_request('GET', f'/repos/{owner}/{repo}')

    def list_repositories(self, type: str = "owner", sort: str = "updated",
                         per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """
        列出仓库

        Args:
            type: 仓库类型 (all, owner, public, private, member)
            sort: 排序方式 (created, updated, pushed, full_name)
            per_page: 每页数量 (1-100)
            page: 页码
        """
        params = {
            'type': type,
            'sort': sort,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', '/user/repos', params=params)

    def create_repository(self, name: str, description: str = "", private: bool = False,
                         has_issues: bool = True, has_projects: bool = True,
                         has_wiki: bool = True, auto_init: bool = False) -> Dict[str, Any]:
        """创建仓库"""
        data = {
            'name': name,
            'description': description,
            'private': private,
            'has_issues': has_issues,
            'has_projects': has_projects,
            'has_wiki': has_wiki,
            'auto_init': auto_init
        }
        return self._make_request('POST', '/user/repos', json=data)

    def update_repository(self, owner: str, repo: str, **kwargs) -> Dict[str, Any]:
        """更新仓库信息"""
        return self._make_request('PATCH', f'/repos/{owner}/{repo}', json=kwargs)

    def delete_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """删除仓库"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}')

    # ============ 问题 (Issues) 相关操作 ============

    def list_issues(self, owner: str, repo: str, state: str = "open",
                   labels: str = "", sort: str = "created", direction: str = "desc",
                   per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """列出问题"""
        params = {
            'state': state,
            'labels': labels,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues', params=params)

    def get_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """获取特定问题"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}')

    def create_issue(self, owner: str, repo: str, title: str, body: str = "",
                    assignees: List[str] = None, milestone: int = None,
                    labels: List[str] = None) -> Dict[str, Any]:
        """创建问题"""
        data = {
            'title': title,
            'body': body
        }
        if assignees:
            data['assignees'] = assignees
        if milestone:
            data['milestone'] = milestone
        if labels:
            data['labels'] = labels

        return self._make_request('POST', f'/repos/{owner}/{repo}/issues', json=data)

    def update_issue(self, owner: str, repo: str, issue_number: int, **kwargs) -> Dict[str, Any]:
        """更新问题"""
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/issues/{issue_number}', json=kwargs)

    def close_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """关闭问题"""
        return self.update_issue(owner, repo, issue_number, state='closed')

    # ============ Issues 评论管理 ============

    def list_issue_comments(self, owner: str, repo: str, issue_number: int,
                           since: str = "", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        列出问题评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            since: ISO 8601 格式的时间，只返回此时间之后更新的评论
            per_page: 每页数量
            page: 页码

        Returns:
            问题评论列表
        """
        params = {
            'per_page': per_page,
            'page': page
        }
        if since:
            params['since'] = since

        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', params=params)

    def get_issue_comment(self, owner: str, repo: str, comment_id: int) -> Dict[str, Any]:
        """
        获取问题评论详情

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            comment_id: 评论 ID

        Returns:
            评论详情
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/comments/{comment_id}')

    def create_issue_comment(self, owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
        """
        创建问题评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            body: 评论内容

        Returns:
            创建的评论信息
        """
        data = {'body': body}
        return self._make_request('POST', f'/repos/{owner}/{repo}/issues/{issue_number}/comments', json=data)

    def update_issue_comment(self, owner: str, repo: str, comment_id: int, body: str) -> Dict[str, Any]:
        """
        更新问题评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            comment_id: 评论 ID
            body: 新的评论内容

        Returns:
            更新后的评论信息
        """
        data = {'body': body}
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/issues/comments/{comment_id}', json=data)

    def delete_issue_comment(self, owner: str, repo: str, comment_id: int) -> Dict[str, Any]:
        """
        删除问题评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            comment_id: 评论 ID

        Returns:
            删除操作结果
        """
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/comments/{comment_id}')

    # ============ Issues 标签管理 ============

    def list_issue_labels(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        列出问题的标签

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号

        Returns:
            问题标签列表
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}/labels')

    def add_issue_labels(self, owner: str, repo: str, issue_number: int, labels: List[str]) -> Dict[str, Any]:
        """
        为问题添加标签

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            labels: 要添加的标签列表

        Returns:
            添加后的标签列表
        """
        data = {'labels': labels}
        return self._make_request('POST', f'/repos/{owner}/{repo}/issues/{issue_number}/labels', json=data)

    def remove_issue_label(self, owner: str, repo: str, issue_number: int, label: str) -> Dict[str, Any]:
        """
        移除问题的指定标签

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            label: 要移除的标签名称

        Returns:
            移除操作结果
        """
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/{issue_number}/labels/{label}')

    def replace_issue_labels(self, owner: str, repo: str, issue_number: int, labels: List[str]) -> Dict[str, Any]:
        """
        替换问题的所有标签

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            labels: 新的标签列表

        Returns:
            替换后的标签列表
        """
        data = {'labels': labels}
        return self._make_request('PUT', f'/repos/{owner}/{repo}/issues/{issue_number}/labels', json=data)

    def remove_all_issue_labels(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        移除问题的所有标签

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号

        Returns:
            移除操作结果
        """
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/{issue_number}/labels')

    # ============ Issues 高级管理 ============

    def lock_issue(self, owner: str, repo: str, issue_number: int, lock_reason: str = "") -> Dict[str, Any]:
        """
        锁定问题

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            lock_reason: 锁定原因 (off-topic, too heated, resolved, spam)

        Returns:
            锁定操作结果
        """
        data = {}
        if lock_reason:
            data['lock_reason'] = lock_reason

        return self._make_request('PUT', f'/repos/{owner}/{repo}/issues/{issue_number}/lock', json=data)

    def unlock_issue(self, owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
        """
        解锁问题

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号

        Returns:
            解锁操作结果
        """
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/issues/{issue_number}/lock')

    def list_issue_events(self, owner: str, repo: str, issue_number: int,
                         per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        列出问题事件

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            issue_number: 问题编号
            per_page: 每页数量
            page: 页码

        Returns:
            问题事件列表
        """
        params = {
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/issues/{issue_number}/events', params=params)

    # ============ 拉取请求 (Pull Requests) 相关操作 ============

    def list_pull_requests(self, owner: str, repo: str, state: str = "open",
                          head: str = "", base: str = "", sort: str = "created",
                          direction: str = "desc", per_page: int = 30,
                          page: int = 1) -> List[Dict[str, Any]]:
        """列出拉取请求"""
        params = {
            'state': state,
            'head': head,
            'base': base,
            'sort': sort,
            'direction': direction,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls', params=params)

    def get_pull_request(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """获取特定拉取请求"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}')

    def create_pull_request(self, owner: str, repo: str, title: str, head: str,
                           base: str, body: str = "", maintainer_can_modify: bool = True,
                           draft: bool = False) -> Dict[str, Any]:
        """创建拉取请求"""
        data = {
            'title': title,
            'head': head,
            'base': base,
            'body': body,
            'maintainer_can_modify': maintainer_can_modify,
            'draft': draft
        }
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls', json=data)

    def update_pull_request(self, owner: str, repo: str, pull_number: int, **kwargs) -> Dict[str, Any]:
        """更新拉取请求"""
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/pulls/{pull_number}', json=kwargs)

    def merge_pull_request(self, owner: str, repo: str, pull_number: int,
                          commit_title: str = "", commit_message: str = "",
                          merge_method: str = "merge") -> Dict[str, Any]:
        """合并拉取请求"""
        data = {
            'commit_title': commit_title,
            'commit_message': commit_message,
            'merge_method': merge_method  # merge, squash, rebase
        }
        return self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pull_number}/merge', json=data)

    # ============ 分支相关操作 ============

    def list_branches(self, owner: str, repo: str, protected: bool = None,
                     per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """列出分支"""
        params = {'per_page': per_page, 'page': page}
        if protected is not None:
            params['protected'] = protected
        return self._make_request('GET', f'/repos/{owner}/{repo}/branches', params=params)

    def get_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """获取分支信息"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/branches/{branch}')

    def create_branch(self, owner: str, repo: str, branch_name: str, sha: str) -> Dict[str, Any]:
        """创建分支"""
        data = {
            'ref': f'refs/heads/{branch_name}',
            'sha': sha
        }
        return self._make_request('POST', f'/repos/{owner}/{repo}/git/refs', json=data)

    def delete_branch(self, owner: str, repo: str, branch: str) -> Dict[str, Any]:
        """删除分支"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/git/refs/heads/{branch}')

    # ============ 提交相关操作 ============

    def list_commits(self, owner: str, repo: str, sha: str = "", path: str = "",
                    author: str = "", since: str = "", until: str = "",
                    per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """列出提交"""
        params = {'per_page': per_page, 'page': page}
        if sha:
            params['sha'] = sha
        if path:
            params['path'] = path
        if author:
            params['author'] = author
        if since:
            params['since'] = since
        if until:
            params['until'] = until
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits', params=params)

    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """获取特定提交"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits/{sha}')

    # ============ 用户相关操作 ============

    def get_authenticated_user(self) -> Dict[str, Any]:
        """获取认证用户信息"""
        return self._make_request('GET', '/user')

    def get_user(self, username: str) -> Dict[str, Any]:
        """获取用户信息"""
        return self._make_request('GET', f'/users/{username}')

    def list_user_repos(self, username: str, type: str = "owner",
                       sort: str = "updated", per_page: int = 30,
                       page: int = 1) -> List[Dict[str, Any]]:
        """列出用户仓库"""
        params = {
            'type': type,
            'sort': sort,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/users/{username}/repos', params=params)

    # ============ 组织相关操作 ============

    def get_organization(self, org: str) -> Dict[str, Any]:
        """获取组织信息"""
        return self._make_request('GET', f'/orgs/{org}')

    def list_organization_repos(self, org: str, type: str = "all",
                               sort: str = "updated", per_page: int = 30,
                               page: int = 1) -> List[Dict[str, Any]]:
        """列出组织仓库"""
        params = {
            'type': type,
            'sort': sort,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/orgs/{org}/repos', params=params)

    def list_organization_members(self, org: str, filter: str = "all",
                                 role: str = "all", per_page: int = 30,
                                 page: int = 1) -> List[Dict[str, Any]]:
        """列出组织成员"""
        params = {
            'filter': filter,
            'role': role,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/orgs/{org}/members', params=params)

    # ============ 仓库内容相关操作 ============

    def get_repository_contents(self, owner: str, repo: str, path: str = "",
                               ref: str = "") -> Union[Dict[str, Any], List[Dict[str, Any]]]:
        """
        获取仓库内容（文件或目录）

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件或目录路径，空字符串表示根目录
            ref: Git 引用（分支名、标签或提交 SHA），默认为默认分支

        Returns:
            如果是文件，返回文件信息字典；如果是目录，返回文件/目录列表
        """
        params = {}
        if ref:
            params['ref'] = ref

        endpoint = f'/repos/{owner}/{repo}/contents'
        if path:
            endpoint += f'/{path}'

        return self._make_request('GET', endpoint, params=params)

    def get_file_content(self, owner: str, repo: str, path: str, ref: str = "") -> Dict[str, Any]:
        """
        获取单个文件的内容和元数据

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
            ref: Git 引用（分支名、标签或提交 SHA），默认为默认分支

        Returns:
            包含文件内容（base64编码）和元数据的字典
        """
        params = {}
        if ref:
            params['ref'] = ref

        return self._make_request('GET', f'/repos/{owner}/{repo}/contents/{path}', params=params)

    def create_file(self, owner: str, repo: str, path: str, message: str,
                   content: str, branch: str = "", committer: Dict[str, str] = None,
                   author: Dict[str, str] = None) -> Dict[str, Any]:
        """
        创建新文件

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
            message: 提交信息
            content: 文件内容（base64编码）
            branch: 目标分支，默认为仓库默认分支
            committer: 提交者信息 {"name": "名称", "email": "邮箱"}
            author: 作者信息 {"name": "名称", "email": "邮箱"}

        Returns:
            创建操作的结果，包含提交信息
        """
        import base64

        # 如果内容不是 base64 编码，进行编码
        try:
            base64.b64decode(content)
            encoded_content = content
        except:
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        data = {
            'message': message,
            'content': encoded_content
        }

        if branch:
            data['branch'] = branch
        if committer:
            data['committer'] = committer
        if author:
            data['author'] = author

        return self._make_request('PUT', f'/repos/{owner}/{repo}/contents/{path}', json=data)

    def update_file(self, owner: str, repo: str, path: str, message: str,
                   content: str, sha: str, branch: str = "",
                   committer: Dict[str, str] = None, author: Dict[str, str] = None) -> Dict[str, Any]:
        """
        更新现有文件

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
            message: 提交信息
            content: 新的文件内容（base64编码）
            sha: 要更新的文件的当前 SHA
            branch: 目标分支，默认为仓库默认分支
            committer: 提交者信息
            author: 作者信息

        Returns:
            更新操作的结果
        """
        import base64

        # 如果内容不是 base64 编码，进行编码
        try:
            base64.b64decode(content)
            encoded_content = content
        except:
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')

        data = {
            'message': message,
            'content': encoded_content,
            'sha': sha
        }

        if branch:
            data['branch'] = branch
        if committer:
            data['committer'] = committer
        if author:
            data['author'] = author

        return self._make_request('PUT', f'/repos/{owner}/{repo}/contents/{path}', json=data)

    def delete_file(self, owner: str, repo: str, path: str, message: str,
                   sha: str, branch: str = "", committer: Dict[str, str] = None,
                   author: Dict[str, str] = None) -> Dict[str, Any]:
        """
        删除文件

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            path: 文件路径
            message: 提交信息
            sha: 要删除的文件的当前 SHA
            branch: 目标分支
            committer: 提交者信息
            author: 作者信息

        Returns:
            删除操作的结果
        """
        data = {
            'message': message,
            'sha': sha
        }

        if branch:
            data['branch'] = branch
        if committer:
            data['committer'] = committer
        if author:
            data['author'] = author

        return self._make_request('DELETE', f'/repos/{owner}/{repo}/contents/{path}', json=data)

    def get_repository_tree(self, owner: str, repo: str, tree_sha: str,
                           recursive: bool = False) -> Dict[str, Any]:
        """
        获取仓库目录树

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            tree_sha: 树的 SHA 值或分支名
            recursive: 是否递归获取所有子目录

        Returns:
            目录树信息
        """
        params = {}
        if recursive:
            params['recursive'] = 1

        return self._make_request('GET', f'/repos/{owner}/{repo}/git/trees/{tree_sha}', params=params)

    def get_blob(self, owner: str, repo: str, file_sha: str) -> Dict[str, Any]:
        """
        获取 blob 对象（文件内容）

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            file_sha: 文件的 SHA 值

        Returns:
            blob 对象信息，包含文件内容
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/git/blobs/{file_sha}')

    def create_blob(self, owner: str, repo: str, content: str, encoding: str = "utf-8") -> Dict[str, Any]:
        """
        创建 blob 对象

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            content: 文件内容（字符串或base64编码）
            encoding: 内容编码方式 ("utf-8" 或 "base64")

        Returns:
            创建的 blob 对象信息，包含 SHA
        """
        import base64

        if encoding == "utf-8":
            # 将 UTF-8 字符串编码为 base64
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')
            encoding = "base64"
        else:
            encoded_content = content

        data = {
            "content": encoded_content,
            "encoding": encoding
        }

        return self._make_request('POST', f'/repos/{owner}/{repo}/git/blobs', json=data)

    def create_tree(self, owner: str, repo: str, tree: List[Dict[str, Any]],
                   base_tree: str = "") -> Dict[str, Any]:
        """
        创建目录树对象

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            tree: 树对象列表，每个对象包含 path, mode, type, sha/content
            base_tree: 基础树的 SHA（可选）

        Returns:
            创建的树对象信息
        """
        data = {"tree": tree}
        if base_tree:
            data["base_tree"] = base_tree

        return self._make_request('POST', f'/repos/{owner}/{repo}/git/trees', json=data)

    def create_commit(self, owner: str, repo: str, message: str, tree: str,
                     parents: List[str] = None, author: Dict[str, str] = None,
                     committer: Dict[str, str] = None) -> Dict[str, Any]:
        """
        创建提交对象

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            message: 提交信息
            tree: 树对象的 SHA
            parents: 父提交的 SHA 列表
            author: 作者信息 {"name": "名称", "email": "邮箱", "date": "ISO时间"}
            committer: 提交者信息

        Returns:
            创建的提交对象信息
        """
        data = {
            "message": message,
            "tree": tree
        }

        if parents:
            data["parents"] = parents
        if author:
            data["author"] = author
        if committer:
            data["committer"] = committer

        return self._make_request('POST', f'/repos/{owner}/{repo}/git/commits', json=data)

    def create_reference(self, owner: str, repo: str, ref: str, sha: str) -> Dict[str, Any]:
        """
        创建引用（分支/标签）

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: 引用名称（如 "refs/heads/feature-branch"）
            sha: 指向的提交 SHA

        Returns:
            创建的引用信息
        """
        data = {
            "ref": ref,
            "sha": sha
        }

        return self._make_request('POST', f'/repos/{owner}/{repo}/git/refs', json=data)

    def update_reference(self, owner: str, repo: str, ref: str, sha: str,
                        force: bool = False) -> Dict[str, Any]:
        """
        更新引用

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: 引用名称（如 "heads/main"）
            sha: 新的提交 SHA
            force: 是否强制更新

        Returns:
            更新后的引用信息
        """
        data = {
            "sha": sha,
            "force": force
        }

        return self._make_request('PATCH', f'/repos/{owner}/{repo}/git/refs/{ref}', json=data)

    def get_reference(self, owner: str, repo: str, ref: str) -> Dict[str, Any]:
        """
        获取引用信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: 引用名称（如 "heads/main"）

        Returns:
            引用信息
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/git/refs/{ref}')

    def list_references(self, owner: str, repo: str, namespace: str = "") -> List[Dict[str, Any]]:
        """
        列出引用

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            namespace: 命名空间过滤（如 "heads", "tags"）

        Returns:
            引用列表
        """
        endpoint = f'/repos/{owner}/{repo}/git/refs'
        if namespace:
            endpoint += f'/{namespace}'

        return self._make_request('GET', endpoint)

    def delete_reference(self, owner: str, repo: str, ref: str) -> Dict[str, Any]:
        """
        删除引用

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: 引用名称（如 "heads/feature-branch"）

        Returns:
            删除操作结果
        """
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/git/refs/{ref}')

    def create_tag(self, owner: str, repo: str, tag: str, message: str,
                  object_sha: str, object_type: str = "commit",
                  tagger: Dict[str, str] = None) -> Dict[str, Any]:
        """
        创建标签对象

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            tag: 标签名称
            message: 标签信息
            object_sha: 标签指向的对象 SHA
            object_type: 对象类型（commit, tree, blob）
            tagger: 标签创建者信息

        Returns:
            创建的标签对象信息
        """
        data = {
            "tag": tag,
            "message": message,
            "object": object_sha,
            "type": object_type
        }

        if tagger:
            data["tagger"] = tagger

        return self._make_request('POST', f'/repos/{owner}/{repo}/git/tags', json=data)

    def get_tag(self, owner: str, repo: str, tag_sha: str) -> Dict[str, Any]:
        """
        获取标签对象

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            tag_sha: 标签对象的 SHA

        Returns:
            标签对象信息
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/git/tags/{tag_sha}')

    def compare_commits(self, owner: str, repo: str, base: str, head: str) -> Dict[str, Any]:
        """
        比较提交

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            base: 基础提交
            head: 目标提交

        Returns:
            提交比较结果，包含差异信息
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/compare/{base}...{head}')

    # ============ Git Commits API ============

    def list_commits(self, owner: str, repo: str, sha: str = "", path: str = "",
                    author: str = "", committer: str = "", since: str = "",
                    until: str = "", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        列出仓库提交

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: SHA 或分支名称，默认为默认分支
            path: 只返回影响此路径的提交
            author: GitHub 用户名或邮箱
            committer: GitHub 用户名或邮箱
            since: ISO 8601 日期时间字符串，只返回此日期之后的提交
            until: ISO 8601 日期时间字符串，只返回此日期之前的提交
            per_page: 每页数量
            page: 页码

        Returns:
            提交列表
        """
        params = {
            'per_page': per_page,
            'page': page
        }
        if sha:
            params['sha'] = sha
        if path:
            params['path'] = path
        if author:
            params['author'] = author
        if committer:
            params['committer'] = committer
        if since:
            params['since'] = since
        if until:
            params['until'] = until

        return self._make_request('GET', f'/repos/{owner}/{repo}/commits', params=params)

    def get_commit(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """
        获取单个提交

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA

        Returns:
            提交详细信息
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits/{sha}')

    def list_commit_comments(self, owner: str, repo: str, sha: str,
                           per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        列出提交评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA
            per_page: 每页数量
            page: 页码

        Returns:
            提交评论列表
        """
        params = {
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits/{sha}/comments', params=params)

    def create_commit_comment(self, owner: str, repo: str, sha: str, body: str,
                            path: str = "", line: int = None, position: int = None) -> Dict[str, Any]:
        """
        创建提交评论

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA
            body: 评论内容
            path: 文件路径（用于行级评论）
            line: 文件行号（用于行级评论）
            position: 差异位置（用于行级评论）

        Returns:
            创建的评论信息
        """
        data = {'body': body}
        if path:
            data['path'] = path
        if line is not None:
            data['line'] = line
        if position is not None:
            data['position'] = position

        return self._make_request('POST', f'/repos/{owner}/{repo}/commits/{sha}/comments', json=data)

    def get_commit_status(self, owner: str, repo: str, sha: str) -> Dict[str, Any]:
        """
        获取提交状态

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA

        Returns:
            提交状态信息
        """
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits/{sha}/status')

    def list_commit_statuses(self, owner: str, repo: str, sha: str,
                           per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """
        列出提交状态

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA
            per_page: 每页数量
            page: 页码

        Returns:
            提交状态列表
        """
        params = {
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/commits/{sha}/statuses', params=params)

    def create_commit_status(self, owner: str, repo: str, sha: str, state: str,
                           target_url: str = "", description: str = "", context: str = "default") -> Dict[str, Any]:
        """
        创建提交状态

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            sha: 提交 SHA
            state: 状态（error, failure, pending, success）
            target_url: 目标 URL
            description: 状态描述
            context: 状态上下文

        Returns:
            创建的状态信息
        """
        data = {
            'state': state,
            'context': context
        }
        if target_url:
            data['target_url'] = target_url
        if description:
            data['description'] = description

        return self._make_request('POST', f'/repos/{owner}/{repo}/statuses/{sha}', json=data)

    def get_repository_readme(self, owner: str, repo: str, ref: str = "") -> Dict[str, Any]:
        """
        获取仓库的 README 文件

        Args:
            owner: 仓库所有者
            repo: 仓库名称
            ref: Git 引用，默认为默认分支

        Returns:
            README 文件信息
        """
        params = {}
        if ref:
            params['ref'] = ref

        return self._make_request('GET', f'/repos/{owner}/{repo}/readme', params=params)

    # ============ 搜索相关操作 ============

    def search_repositories(self, q: str, sort: str = "updated", order: str = "desc",
                           per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """搜索仓库"""
        params = {
            'q': q,
            'sort': sort,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', '/search/repositories', params=params)

    def search_issues(self, q: str, sort: str = "created", order: str = "desc",
                     per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """搜索问题"""
        params = {
            'q': q,
            'sort': sort,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', '/search/issues', params=params)

    def search_code(self, q: str, sort: str = "indexed", order: str = "desc",
                   per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """搜索代码"""
        params = {
            'q': q,
            'sort': sort,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', '/search/code', params=params)

    def search_users(self, q: str, sort: str = "joined", order: str = "desc",
                    per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """搜索用户"""
        params = {
            'q': q,
            'sort': sort,
            'order': order,
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', '/search/users', params=params)

    # ============ GitHub Actions 管理 ============

    def list_workflows(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出仓库的工作流"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/workflows', params=params)

    def get_workflow(self, owner: str, repo: str, workflow_id: Union[int, str]) -> Dict[str, Any]:
        """获取指定工作流详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}')

    def enable_workflow(self, owner: str, repo: str, workflow_id: Union[int, str]) -> Dict[str, Any]:
        """启用工作流"""
        return self._make_request('PUT', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/enable')

    def disable_workflow(self, owner: str, repo: str, workflow_id: Union[int, str]) -> Dict[str, Any]:
        """禁用工作流"""
        return self._make_request('PUT', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/disable')

    def trigger_workflow(self, owner: str, repo: str, workflow_id: Union[int, str],
                        ref: str, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """触发工作流运行"""
        data = {'ref': ref}
        if inputs:
            data['inputs'] = inputs
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/dispatches', json=data)

    def list_workflow_runs(self, owner: str, repo: str, workflow_id: Optional[Union[int, str]] = None,
                          actor: str = "", branch: str = "", event: str = "", status: str = "",
                          per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出工作流运行"""
        if workflow_id:
            endpoint = f'/repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs'
        else:
            endpoint = f'/repos/{owner}/{repo}/actions/runs'

        params = {'per_page': per_page, 'page': page}
        if actor:
            params['actor'] = actor
        if branch:
            params['branch'] = branch
        if event:
            params['event'] = event
        if status:
            params['status'] = status

        return self._make_request('GET', endpoint, params=params)

    def get_workflow_run(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """获取指定工作流运行详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}')

    def cancel_workflow_run(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """取消工作流运行"""
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/runs/{run_id}/cancel')

    def rerun_workflow_run(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """重新运行工作流"""
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/runs/{run_id}/rerun')

    def rerun_failed_jobs(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """重新运行失败的作业"""
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/runs/{run_id}/rerun-failed-jobs')

    def list_workflow_run_jobs(self, owner: str, repo: str, run_id: int,
                              filter_status: str = "latest", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出工作流运行的作业"""
        params = {'filter': filter_status, 'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}/jobs', params=params)

    def get_job(self, owner: str, repo: str, job_id: int) -> Dict[str, Any]:
        """获取指定作业详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/jobs/{job_id}')

    def download_job_logs(self, owner: str, repo: str, job_id: int) -> Dict[str, Any]:
        """下载作业日志"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/jobs/{job_id}/logs')

    def download_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """下载工作流运行日志"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}/logs')

    def delete_workflow_run_logs(self, owner: str, repo: str, run_id: int) -> Dict[str, Any]:
        """删除工作流运行日志"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/runs/{run_id}/logs')

    def list_workflow_run_artifacts(self, owner: str, repo: str, run_id: int,
                                   per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出工作流运行的构件"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runs/{run_id}/artifacts', params=params)

    def list_repository_artifacts(self, owner: str, repo: str, name: str = "",
                                 per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出仓库的构件"""
        params = {'per_page': per_page, 'page': page}
        if name:
            params['name'] = name
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/artifacts', params=params)

    def get_artifact(self, owner: str, repo: str, artifact_id: int) -> Dict[str, Any]:
        """获取指定构件详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/artifacts/{artifact_id}')

    def download_artifact(self, owner: str, repo: str, artifact_id: int, archive_format: str = "zip") -> Dict[str, Any]:
        """下载构件"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/artifacts/{artifact_id}/{archive_format}')

    def delete_artifact(self, owner: str, repo: str, artifact_id: int) -> Dict[str, Any]:
        """删除构件"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/artifacts/{artifact_id}')

    # ============ Actions Secrets 管理 ============

    def list_repository_secrets(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出仓库密钥"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/secrets', params=params)

    def get_repository_secret(self, owner: str, repo: str, secret_name: str) -> Dict[str, Any]:
        """获取仓库密钥"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}')

    def create_or_update_repository_secret(self, owner: str, repo: str, secret_name: str,
                                         encrypted_value: str, key_id: str) -> Dict[str, Any]:
        """创建或更新仓库密钥"""
        data = {
            'encrypted_value': encrypted_value,
            'key_id': key_id
        }
        return self._make_request('PUT', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}', json=data)

    def delete_repository_secret(self, owner: str, repo: str, secret_name: str) -> Dict[str, Any]:
        """删除仓库密钥"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/secrets/{secret_name}')

    def get_repository_public_key(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库公钥（用于加密密钥）"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/secrets/public-key')

    # ============ Actions Variables 管理 ============

    def list_repository_variables(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出仓库变量"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/variables', params=params)

    def get_repository_variable(self, owner: str, repo: str, name: str) -> Dict[str, Any]:
        """获取仓库变量"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/variables/{name}')

    def create_repository_variable(self, owner: str, repo: str, name: str, value: str) -> Dict[str, Any]:
        """创建仓库变量"""
        data = {'name': name, 'value': value}
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/variables', json=data)

    def update_repository_variable(self, owner: str, repo: str, name: str, value: str) -> Dict[str, Any]:
        """更新仓库变量"""
        data = {'name': name, 'value': value}
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/actions/variables/{name}', json=data)

    def delete_repository_variable(self, owner: str, repo: str, name: str) -> Dict[str, Any]:
        """删除仓库变量"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/variables/{name}')

    # ============ Actions Runners 管理 ============

    def list_self_hosted_runners(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出自托管运行器"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runners', params=params)

    def get_self_hosted_runner(self, owner: str, repo: str, runner_id: int) -> Dict[str, Any]:
        """获取自托管运行器详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/runners/{runner_id}')

    def delete_self_hosted_runner(self, owner: str, repo: str, runner_id: int) -> Dict[str, Any]:
        """删除自托管运行器"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/runners/{runner_id}')

    def create_registration_token(self, owner: str, repo: str) -> Dict[str, Any]:
        """创建运行器注册令牌"""
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/runners/registration-token')

    def create_remove_token(self, owner: str, repo: str) -> Dict[str, Any]:
        """创建运行器移除令牌"""
        return self._make_request('POST', f'/repos/{owner}/{repo}/actions/runners/remove-token')

    # ============ Actions Cache 管理 ============

    def get_actions_cache_usage(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取 Actions 缓存使用情况"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/cache/usage')

    def list_actions_caches(self, owner: str, repo: str, ref: str = "", key: str = "",
                           sort: str = "last_accessed_at", direction: str = "desc",
                           per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出 Actions 缓存"""
        params = {'per_page': per_page, 'page': page, 'sort': sort, 'direction': direction}
        if ref:
            params['ref'] = ref
        if key:
            params['key'] = key
        return self._make_request('GET', f'/repos/{owner}/{repo}/actions/caches', params=params)

    def delete_actions_cache_by_key(self, owner: str, repo: str, key: str, ref: str = "") -> Dict[str, Any]:
        """按键删除 Actions 缓存"""
        params = {'key': key}
        if ref:
            params['ref'] = ref
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/caches', params=params)

    def delete_actions_cache_by_id(self, owner: str, repo: str, cache_id: int) -> Dict[str, Any]:
        """按 ID 删除 Actions 缓存"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/actions/caches/{cache_id}')

    # ============ Pull Requests 详细管理 ============

    def list_pull_request_reviews(self, owner: str, repo: str, pull_number: int,
                                 per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出拉取请求的审查"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews', params=params)

    def get_pull_request_review(self, owner: str, repo: str, pull_number: int, review_id: int) -> Dict[str, Any]:
        """获取拉取请求审查详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}')

    def create_pull_request_review(self, owner: str, repo: str, pull_number: int,
                                  commit_id: str = "", body: str = "", event: str = "COMMENT",
                                  comments: Optional[List[Dict[str, Any]]] = None) -> Dict[str, Any]:
        """创建拉取请求审查"""
        data = {'event': event}
        if commit_id:
            data['commit_id'] = commit_id
        if body:
            data['body'] = body
        if comments:
            data['comments'] = comments
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews', json=data)

    def submit_pull_request_review(self, owner: str, repo: str, pull_number: int, review_id: int,
                                  body: str = "", event: str = "COMMENT") -> Dict[str, Any]:
        """提交拉取请求审查"""
        data = {'event': event}
        if body:
            data['body'] = body
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/events', json=data)

    def dismiss_pull_request_review(self, owner: str, repo: str, pull_number: int, review_id: int,
                                   message: str) -> Dict[str, Any]:
        """驳回拉取请求审查"""
        data = {'message': message}
        return self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/dismissals', json=data)

    def list_pull_request_review_comments(self, owner: str, repo: str, pull_number: int, review_id: int,
                                         per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出拉取请求审查评论"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/reviews/{review_id}/comments', params=params)

    def list_pull_request_comments(self, owner: str, repo: str, pull_number: int,
                                  sort: str = "created", direction: str = "asc",
                                  per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出拉取请求评论"""
        params = {'sort': sort, 'direction': direction, 'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/comments', params=params)

    def create_pull_request_review_comment(self, owner: str, repo: str, pull_number: int,
                                          body: str, commit_id: str, path: str, line: int,
                                          side: str = "RIGHT") -> Dict[str, Any]:
        """创建拉取请求审查评论"""
        data = {
            'body': body,
            'commit_id': commit_id,
            'path': path,
            'line': line,
            'side': side
        }
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/comments', json=data)

    def merge_pull_request(self, owner: str, repo: str, pull_number: int,
                          commit_title: str = "", commit_message: str = "",
                          sha: str = "", merge_method: str = "merge") -> Dict[str, Any]:
        """合并拉取请求"""
        data = {'merge_method': merge_method}
        if commit_title:
            data['commit_title'] = commit_title
        if commit_message:
            data['commit_message'] = commit_message
        if sha:
            data['sha'] = sha
        return self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pull_number}/merge', json=data)

    def request_pull_request_reviewers(self, owner: str, repo: str, pull_number: int,
                                      reviewers: Optional[List[str]] = None,
                                      team_reviewers: Optional[List[str]] = None) -> Dict[str, Any]:
        """请求拉取请求审查者"""
        data = {}
        if reviewers:
            data['reviewers'] = reviewers
        if team_reviewers:
            data['team_reviewers'] = team_reviewers
        return self._make_request('POST', f'/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers', json=data)

    def remove_pull_request_reviewers(self, owner: str, repo: str, pull_number: int,
                                     reviewers: Optional[List[str]] = None,
                                     team_reviewers: Optional[List[str]] = None) -> Dict[str, Any]:
        """移除拉取请求审查者"""
        data = {}
        if reviewers:
            data['reviewers'] = reviewers
        if team_reviewers:
            data['team_reviewers'] = team_reviewers
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/pulls/{pull_number}/requested_reviewers', json=data)

    def list_pull_request_commits(self, owner: str, repo: str, pull_number: int,
                                 per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出拉取请求的提交"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/commits', params=params)

    def list_pull_request_files(self, owner: str, repo: str, pull_number: int,
                               per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出拉取请求的文件"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/files', params=params)

    def check_pull_request_merge_status(self, owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
        """检查拉取请求是否可以合并"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/pulls/{pull_number}/merge')

    def update_pull_request_branch(self, owner: str, repo: str, pull_number: int,
                                  expected_head_sha: str = "") -> Dict[str, Any]:
        """更新拉取请求分支"""
        data = {}
        if expected_head_sha:
            data['expected_head_sha'] = expected_head_sha
        return self._make_request('PUT', f'/repos/{owner}/{repo}/pulls/{pull_number}/update-branch', json=data)

    # ============ Releases 管理 ============

    def list_releases(self, owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出仓库的 releases"""
        params = {
            'per_page': per_page,
            'page': page
        }
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases', params=params)

    def get_release(self, owner: str, repo: str, release_id: int) -> Dict[str, Any]:
        """获取特定 release 的详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases/{release_id}')

    def get_latest_release(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取最新的 release"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases/latest')

    def get_release_by_tag(self, owner: str, repo: str, tag: str) -> Dict[str, Any]:
        """根据标签获取 release"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases/tags/{tag}')

    def create_release(self, owner: str, repo: str, tag_name: str,
                      target_commitish: str = "", name: str = "", body: str = "",
                      draft: bool = False, prerelease: bool = False,
                      discussion_category_name: str = "",
                      generate_release_notes: bool = False,
                      make_latest: str = "true") -> Dict[str, Any]:
        """创建新的 release"""
        data = {
            'tag_name': tag_name,
            'draft': draft,
            'prerelease': prerelease,
            'generate_release_notes': generate_release_notes
        }

        if target_commitish:
            data['target_commitish'] = target_commitish
        if name:
            data['name'] = name
        if body:
            data['body'] = body
        if discussion_category_name:
            data['discussion_category_name'] = discussion_category_name
        if make_latest in ['true', 'false', 'legacy']:
            data['make_latest'] = make_latest

        return self._make_request('POST', f'/repos/{owner}/{repo}/releases', json=data)

    def update_release(self, owner: str, repo: str, release_id: int,
                      tag_name: str = "", target_commitish: str = "", name: str = "",
                      body: str = "", draft: Optional[bool] = None,
                      prerelease: Optional[bool] = None,
                      discussion_category_name: str = "",
                      make_latest: str = "") -> Dict[str, Any]:
        """更新 release"""
        data = {}

        if tag_name:
            data['tag_name'] = tag_name
        if target_commitish:
            data['target_commitish'] = target_commitish
        if name:
            data['name'] = name
        if body:
            data['body'] = body
        if draft is not None:
            data['draft'] = draft
        if prerelease is not None:
            data['prerelease'] = prerelease
        if discussion_category_name:
            data['discussion_category_name'] = discussion_category_name
        if make_latest in ['true', 'false', 'legacy']:
            data['make_latest'] = make_latest

        return self._make_request('PATCH', f'/repos/{owner}/{repo}/releases/{release_id}', json=data)

    def delete_release(self, owner: str, repo: str, release_id: int) -> Dict[str, Any]:
        """删除 release"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/releases/{release_id}')

    def list_release_assets(self, owner: str, repo: str, release_id: int,
                           per_page: int = 30, page: int = 1) -> Dict[str, Any]:
        """列出 release 的资产"""
        params = {'per_page': per_page, 'page': page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases/{release_id}/assets', params=params)

    def get_release_asset(self, owner: str, repo: str, asset_id: int) -> Dict[str, Any]:
        """获取 release 资产详情"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/releases/assets/{asset_id}')

    def update_release_asset(self, owner: str, repo: str, asset_id: int,
                            name: str = "", label: str = "") -> Dict[str, Any]:
        """更新 release 资产"""
        data = {}
        if name:
            data['name'] = name
        if label:
            data['label'] = label
        return self._make_request('PATCH', f'/repos/{owner}/{repo}/releases/assets/{asset_id}', json=data)

    def delete_release_asset(self, owner: str, repo: str, asset_id: int) -> Dict[str, Any]:
        """删除 release 资产"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/releases/assets/{asset_id}')

    def generate_release_notes(self, owner: str, repo: str, tag_name: str,
                              target_commitish: str = "", previous_tag_name: str = "",
                              configuration_file_path: str = ".github/release.yml") -> Dict[str, Any]:
        """生成 release 说明"""
        data = {
            'tag_name': tag_name,
            'configuration_file_path': configuration_file_path
        }

        if target_commitish:
            data['target_commitish'] = target_commitish
        if previous_tag_name:
            data['previous_tag_name'] = previous_tag_name

        return self._make_request('POST', f'/repos/{owner}/{repo}/releases/generate-notes', json=data)

    # ============ Security 安全相关 ============

    # Code Scanning 代码扫描
    def list_code_scanning_alerts(self, owner: str, repo: str, tool_name: str = "",
                                 tool_guid: str = "", page: int = 1, per_page: int = 30,
                                 ref: str = "", state: str = "", severity: str = "") -> Dict[str, Any]:
        """列出代码扫描警报"""
        params = {'page': page, 'per_page': per_page}

        if tool_name:
            params['tool_name'] = tool_name
        if tool_guid:
            params['tool_guid'] = tool_guid
        if ref:
            params['ref'] = ref
        if state in ['open', 'closed', 'dismissed', 'fixed']:
            params['state'] = state
        if severity in ['critical', 'high', 'medium', 'low', 'warning', 'note', 'error']:
            params['severity'] = severity

        return self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/alerts', params=params)

    def get_code_scanning_alert(self, owner: str, repo: str, alert_number: int) -> Dict[str, Any]:
        """获取特定代码扫描警报"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}')

    def update_code_scanning_alert(self, owner: str, repo: str, alert_number: int,
                                  state: str, dismissed_reason: str = "",
                                  dismissed_comment: str = "") -> Dict[str, Any]:
        """更新代码扫描警报状态"""
        data = {'state': state}

        if dismissed_reason:
            data['dismissed_reason'] = dismissed_reason
        if dismissed_comment:
            data['dismissed_comment'] = dismissed_comment

        return self._make_request('PATCH', f'/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}', json=data)

    def list_code_scanning_alert_instances(self, owner: str, repo: str, alert_number: int,
                                          page: int = 1, per_page: int = 30, ref: str = "") -> Dict[str, Any]:
        """列出代码扫描警报实例"""
        params = {'page': page, 'per_page': per_page}
        if ref:
            params['ref'] = ref

        return self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/alerts/{alert_number}/instances', params=params)

    def list_code_scanning_analyses(self, owner: str, repo: str, tool_name: str = "",
                                   tool_guid: str = "", page: int = 1, per_page: int = 30,
                                   ref: str = "", sarif_id: str = "") -> Dict[str, Any]:
        """列出代码扫描分析"""
        params = {'page': page, 'per_page': per_page}

        if tool_name:
            params['tool_name'] = tool_name
        if tool_guid:
            params['tool_guid'] = tool_guid
        if ref:
            params['ref'] = ref
        if sarif_id:
            params['sarif_id'] = sarif_id

        return self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/analyses', params=params)

    def get_code_scanning_analysis(self, owner: str, repo: str, analysis_id: int) -> Dict[str, Any]:
        """获取特定代码扫描分析"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}')

    def delete_code_scanning_analysis(self, owner: str, repo: str, analysis_id: int,
                                     confirm_delete: str = "") -> Dict[str, Any]:
        """删除代码扫描分析"""
        params = {}
        if confirm_delete:
            params['confirm_delete'] = confirm_delete

        return self._make_request('DELETE', f'/repos/{owner}/{repo}/code-scanning/analyses/{analysis_id}', params=params)

    # Secret Scanning 密钥扫描
    def list_secret_scanning_alerts(self, owner: str, repo: str, state: str = "",
                                   secret_type: str = "", resolution: str = "",
                                   sort: str = "created", direction: str = "desc",
                                   page: int = 1, per_page: int = 30) -> Dict[str, Any]:
        """列出密钥扫描警报"""
        params = {'page': page, 'per_page': per_page, 'sort': sort, 'direction': direction}

        if state in ['open', 'resolved']:
            params['state'] = state
        if secret_type:
            params['secret_type'] = secret_type
        if resolution in ['false_positive', 'wont_fix', 'revoked', 'pattern_edited', 'pattern_deleted', 'used_in_tests']:
            params['resolution'] = resolution

        return self._make_request('GET', f'/repos/{owner}/{repo}/secret-scanning/alerts', params=params)

    def get_secret_scanning_alert(self, owner: str, repo: str, alert_number: int) -> Dict[str, Any]:
        """获取特定密钥扫描警报"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}')

    def update_secret_scanning_alert(self, owner: str, repo: str, alert_number: int,
                                    state: str, resolution: str = "",
                                    resolution_comment: str = "") -> Dict[str, Any]:
        """更新密钥扫描警报"""
        data = {'state': state}

        if resolution:
            data['resolution'] = resolution
        if resolution_comment:
            data['resolution_comment'] = resolution_comment

        return self._make_request('PATCH', f'/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}', json=data)

    def list_secret_scanning_alert_locations(self, owner: str, repo: str, alert_number: int,
                                            page: int = 1, per_page: int = 30) -> Dict[str, Any]:
        """列出密钥扫描警报位置"""
        params = {'page': page, 'per_page': per_page}
        return self._make_request('GET', f'/repos/{owner}/{repo}/secret-scanning/alerts/{alert_number}/locations', params=params)

    # Dependabot 依赖项安全
    def list_dependabot_alerts(self, owner: str, repo: str, state: str = "",
                              severity: str = "", ecosystem: str = "", package: str = "",
                              manifest: str = "", scope: str = "", sort: str = "created",
                              direction: str = "desc", page: int = 1, per_page: int = 30) -> Dict[str, Any]:
        """列出 Dependabot 警报"""
        params = {'page': page, 'per_page': per_page, 'sort': sort, 'direction': direction}

        if state in ['auto_dismissed', 'dismissed', 'fixed', 'open']:
            params['state'] = state
        if severity in ['low', 'medium', 'high', 'critical']:
            params['severity'] = severity
        if ecosystem:
            params['ecosystem'] = ecosystem
        if package:
            params['package'] = package
        if manifest:
            params['manifest'] = manifest
        if scope in ['development', 'runtime']:
            params['scope'] = scope

        return self._make_request('GET', f'/repos/{owner}/{repo}/dependabot/alerts', params=params)

    def get_dependabot_alert(self, owner: str, repo: str, alert_number: int) -> Dict[str, Any]:
        """获取特定 Dependabot 警报"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/dependabot/alerts/{alert_number}')

    def update_dependabot_alert(self, owner: str, repo: str, alert_number: int,
                               state: str, dismissed_reason: str = "",
                               dismissed_comment: str = "") -> Dict[str, Any]:
        """更新 Dependabot 警报"""
        data = {'state': state}

        if dismissed_reason:
            data['dismissed_reason'] = dismissed_reason
        if dismissed_comment:
            data['dismissed_comment'] = dismissed_comment

        return self._make_request('PATCH', f'/repos/{owner}/{repo}/dependabot/alerts/{alert_number}', json=data)

    # Security Configuration 安全配置
    def get_security_configuration(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取仓库安全配置"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/code-security-configuration')

    def enable_automated_security_fixes(self, owner: str, repo: str) -> Dict[str, Any]:
        """启用自动安全修复"""
        return self._make_request('PUT', f'/repos/{owner}/{repo}/automated-security-fixes')

    def disable_automated_security_fixes(self, owner: str, repo: str) -> Dict[str, Any]:
        """禁用自动安全修复"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/automated-security-fixes')

    def get_vulnerability_alerts_status(self, owner: str, repo: str) -> Dict[str, Any]:
        """获取漏洞警报状态"""
        return self._make_request('GET', f'/repos/{owner}/{repo}/vulnerability-alerts')

    def enable_vulnerability_alerts(self, owner: str, repo: str) -> Dict[str, Any]:
        """启用漏洞警报"""
        return self._make_request('PUT', f'/repos/{owner}/{repo}/vulnerability-alerts')

    def disable_vulnerability_alerts(self, owner: str, repo: str) -> Dict[str, Any]:
        """禁用漏洞警报"""
        return self._make_request('DELETE', f'/repos/{owner}/{repo}/vulnerability-alerts')

    # ============ 通用工具方法 ============

    def get_rate_limit(self) -> Dict[str, Any]:
        """获取速率限制信息"""
        return self._make_request('GET', '/rate_limit')

    def get_api_root(self) -> Dict[str, Any]:
        """获取 API 根信息"""
        return self._make_request('GET', '/')


# 创建默认实例
github_api_service = GitHubAPIService()