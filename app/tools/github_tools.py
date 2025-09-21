"""
GitHub工具集
使用装饰器自动注册GitHub相关的MCP工具，所有工具名称以github_开头
"""
import os
import json
import base64
from typing import Dict, Any, List, Optional, Union
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.tools.registry import github_tool, mcp_category
from app.core.mcp_tools_service import get_proxy_for_requests, get_mcp_config


# 注册GitHub工具分类
@mcp_category(
    category_id="github",
    name="GitHub API 工具",
    description="GitHub 仓库管理、Issues、Pull Requests、Releases 等完整 API 工具集",
    icon="🐙",
    enabled=True,
    sort_order=1
)
def register_github_category():
    """注册GitHub工具分类"""
    pass


class GitHubAPIClient:
    """GitHub API客户端"""

    def __init__(self, token: Optional[str] = None):
        # 获取全局配置
        try:
            mcp_config = get_mcp_config()
            self.mcp_config = mcp_config
        except Exception:
            # 如果获取配置失败，使用默认值
            self.mcp_config = None

        # 获取GitHub工具的文件配置
        try:
            from app.core.tool_config_service import get_tool_config_service
            tool_config_service = get_tool_config_service()
            self.github_config = tool_config_service.get_config("github")
        except Exception:
            # 如果获取文件配置失败，使用默认值
            self.github_config = None

        # Token配置：优先使用参数，其次文件配置，再次环境变量，最后从MCP配置中获取
        self.token = (
            token or
            (self.github_config.get('github_token') if self.github_config else None) or
            os.getenv('GITHUB_TOKEN') or
            (self.mcp_config.environment_variables.get('GITHUB_TOKEN') if self.mcp_config else None)
        ) or ''

        # 基础URL配置：优先使用文件配置，否则使用默认值
        self.base_url = (
            self.github_config.get('api_base_url', 'https://api.github.com') if self.github_config
            else "https://api.github.com"
        )

        self.session = requests.Session()

        # 配置GitHub工具特定设置
        if self.github_config:
            # 配置重试策略（使用GitHub配置）
            retry_count = self.github_config.get('retry_count', 3)
            retry_strategy = Retry(
                total=retry_count,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )

            # 设置请求头
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "LazyAI-Studio-GitHub-Tools/1.0"
            })

            # 配置超时（使用GitHub配置）
            self.session.timeout = self.github_config.get('timeout', 30)

            # 配置SSL验证（使用GitHub配置）
            self.session.verify = self.github_config.get('security', {}).get('verify_ssl', True)

            # 如果有MCP配置，仍然使用代理设置
            if self.mcp_config:
                proxy_config = get_proxy_for_requests()
                if proxy_config:
                    self.session.proxies.update(proxy_config)

        # 从MCP配置获取网络设置（如果没有GitHub特定配置）
        elif self.mcp_config:
            network_config = self.mcp_config.network
            # 配置重试策略
            retry_strategy = Retry(
                total=network_config.retry_times,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )

            # 设置请求头
            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": network_config.user_agent
            })

            # 配置代理
            proxy_config = get_proxy_for_requests()
            if proxy_config:
                self.session.proxies.update(proxy_config)

            # 配置SSL验证
            self.session.verify = self.mcp_config.security.verify_ssl

            # 配置超时
            self.session.timeout = network_config.timeout
        else:
            # 默认配置
            retry_strategy = Retry(
                total=3,
                status_forcelist=[429, 500, 502, 503, 504],
                allowed_methods=["HEAD", "GET", "OPTIONS"]
            )

            self.session.headers.update({
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "LazyAI-Studio-GitHub-Tools/1.0"
            })

            self.session.timeout = 30

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)

        if self.token:
            self.session.headers.update({
                "Authorization": f"token {self.token}"
            })

    def reload_config(self):
        """重新加载配置"""
        try:
            self.mcp_config = get_mcp_config()
            # 重新配置session
            if self.mcp_config:
                # 更新代理配置
                proxy_config = get_proxy_for_requests()
                if proxy_config:
                    self.session.proxies.clear()
                    self.session.proxies.update(proxy_config)
                else:
                    self.session.proxies.clear()

                # 更新SSL验证
                self.session.verify = self.mcp_config.security.verify_ssl

                # 更新超时
                self.session.timeout = self.mcp_config.network.timeout

                # 更新User-Agent
                self.session.headers.update({
                    "User-Agent": self.mcp_config.network.user_agent
                })
        except Exception:
            pass  # 配置加载失败时不影响现有功能

    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """GET请求"""
        try:
            response = self.session.get(f"{self.base_url}/{endpoint}", params=params)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """POST请求"""
        try:
            response = self.session.post(f"{self.base_url}/{endpoint}", json=data)
            if response.status_code in [200, 201]:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def patch(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """PATCH请求"""
        try:
            response = self.session.patch(f"{self.base_url}/{endpoint}", json=data)
            if response.status_code == 200:
                return {"success": True, "data": response.json()}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"success": False, "error": str(e)}

    def delete(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """DELETE请求"""
        try:
            response = self.session.delete(f"{self.base_url}/{endpoint}", json=data)
            if response.status_code in [200, 204]:
                return {"success": True, "data": response.text if response.text else "Deleted successfully"}
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}",
                    "status_code": response.status_code
                }
        except Exception as e:
            return {"success": False, "error": str(e)}


# 创建全局GitHub客户端实例
github_client = GitHubAPIClient()


def reload_github_client_config():
    """重新加载GitHub客户端配置"""
    global github_client
    github_client.reload_config()


@github_tool(
    name="get_repository",
    description="获取GitHub仓库详细信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者用户名或组织名"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "repository", "info"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react"}
        ]
    }
)
def github_get_repository(owner: str, repo: str) -> Dict[str, Any]:
    """获取GitHub仓库详细信息"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_repositories",
    description="列出用户或组织的仓库列表",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "用户名或组织名"
            },
            "type": {
                "type": "string",
                "description": "仓库类型",
                "enum": ["all", "public", "private", "forks", "sources", "member"],
                "default": "all"
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["created", "updated", "pushed", "full_name"],
                "default": "updated"
            },
            "direction": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner"]
    },
    metadata={
        "tags": ["github", "repository", "list"],
        "examples": [
            {"owner": "microsoft"},
            {"owner": "google", "type": "public", "sort": "created"},
            {"owner": "facebook", "per_page": 50}
        ]
    }
)
def github_list_repositories(owner: str, type: str = "all", sort: str = "updated", direction: str = "desc", per_page: int = 30) -> Dict[str, Any]:
    """列出用户或组织的仓库列表"""
    try:
        if not owner:
            return {"success": False, "error": "owner参数不能为空"}

        params = {
            "type": type,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100)  # GitHub API限制最大100
        }

        result = github_client.get(f"users/{owner}/repos", params=params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_repository",
    description="创建新的GitHub仓库",
    schema={
        "type": "object",
        "properties": {
            "name": {
                "type": "string",
                "description": "仓库名称"
            },
            "description": {
                "type": "string",
                "description": "仓库描述",
                "default": ""
            },
            "homepage": {
                "type": "string",
                "description": "项目主页URL",
                "default": ""
            },
            "private": {
                "type": "boolean",
                "description": "是否创建私有仓库",
                "default": False
            },
            "has_issues": {
                "type": "boolean",
                "description": "启用Issues功能",
                "default": True
            },
            "has_projects": {
                "type": "boolean",
                "description": "启用Projects功能",
                "default": True
            },
            "has_wiki": {
                "type": "boolean",
                "description": "启用Wiki功能",
                "default": True
            },
            "auto_init": {
                "type": "boolean",
                "description": "自动创建README文件",
                "default": False
            },
            "gitignore_template": {
                "type": "string",
                "description": ".gitignore模板",
                "default": ""
            },
            "license_template": {
                "type": "string",
                "description": "许可证模板",
                "default": ""
            }
        },
        "required": ["name"]
    },
    metadata={
        "tags": ["github", "repository", "create"],
        "examples": [
            {"name": "my-new-project", "description": "A new project"},
            {"name": "private-repo", "private": True, "auto_init": True}
        ]
    }
)
def github_create_repository(name: str, description: str = "", homepage: str = "", private: bool = False,
                            has_issues: bool = True, has_projects: bool = True, has_wiki: bool = True,
                            auto_init: bool = False, gitignore_template: str = "", license_template: str = "") -> Dict[str, Any]:
    """创建新的GitHub仓库"""
    try:
        if not name:
            return {"success": False, "error": "name参数不能为空"}

        data = {
            "name": name,
            "description": description,
            "homepage": homepage,
            "private": private,
            "has_issues": has_issues,
            "has_projects": has_projects,
            "has_wiki": has_wiki,
            "auto_init": auto_init
        }

        if gitignore_template:
            data["gitignore_template"] = gitignore_template
        if license_template:
            data["license_template"] = license_template

        result = github_client.post("user/repos", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_user",
    description="获取GitHub用户信息",
    schema={
        "type": "object",
        "properties": {
            "username": {
                "type": "string",
                "description": "用户名（为空时获取当前认证用户信息）",
                "default": ""
            }
        }
    },
    metadata={
        "tags": ["github", "user", "profile"],
        "examples": [
            {},
            {"username": "octocat"},
            {"username": "torvalds"}
        ]
    }
)
def github_get_user(username: str = "") -> Dict[str, Any]:
    """获取GitHub用户信息"""
    try:
        if username:
            endpoint = f"users/{username}"
        else:
            endpoint = "user"

        result = github_client.get(endpoint)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_issues",
    description="列出仓库的Issues",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "milestone": {
                "type": "string",
                "description": "里程碑筛选",
                "default": ""
            },
            "state": {
                "type": "string",
                "description": "Issue状态",
                "enum": ["open", "closed", "all"],
                "default": "open"
            },
            "assignee": {
                "type": "string",
                "description": "指派人筛选",
                "default": ""
            },
            "creator": {
                "type": "string",
                "description": "创建者筛选",
                "default": ""
            },
            "mentioned": {
                "type": "string",
                "description": "提及用户筛选",
                "default": ""
            },
            "labels": {
                "type": "string",
                "description": "标签筛选（逗号分隔）",
                "default": ""
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["created", "updated", "comments"],
                "default": "created"
            },
            "direction": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "since": {
                "type": "string",
                "description": "筛选时间（ISO 8601格式）",
                "default": ""
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "issues", "list"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react", "state": "closed", "labels": "bug"}
        ]
    }
)
def github_list_issues(owner: str, repo: str, milestone: str = "", state: str = "open", assignee: str = "",
                      creator: str = "", mentioned: str = "", labels: str = "", sort: str = "created",
                      direction: str = "desc", since: str = "", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的Issues"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": page
        }

        if milestone:
            params["milestone"] = milestone
        if assignee:
            params["assignee"] = assignee
        if creator:
            params["creator"] = creator
        if mentioned:
            params["mentioned"] = mentioned
        if labels:
            params["labels"] = labels
        if since:
            params["since"] = since

        result = github_client.get(f"repos/{owner}/{repo}/issues", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_issue",
    description="创建新的Issue",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "title": {
                "type": "string",
                "description": "Issue标题"
            },
            "body": {
                "type": "string",
                "description": "Issue内容",
                "default": ""
            },
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "指派人列表",
                "default": []
            },
            "milestone": {
                "type": "integer",
                "description": "里程碑编号",
                "default": None
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表",
                "default": []
            }
        },
        "required": ["owner", "repo", "title"]
    },
    metadata={
        "tags": ["github", "issues", "create"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "title": "Bug report",
                "body": "Something is not working",
                "labels": ["bug", "high-priority"]
            }
        ]
    }
)
def github_create_issue(owner: str, repo: str, title: str, body: str = "", assignees: List[str] = [],
                       milestone: Optional[int] = None, labels: List[str] = []) -> Dict[str, Any]:
    """创建新的Issue"""
    try:
        if not owner or not repo or not title:
            return {"success": False, "error": "owner、repo和title参数不能为空"}

        data = {
            "title": title,
            "body": body
        }

        if assignees:
            data["assignees"] = assignees
        if milestone is not None:
            data["milestone"] = milestone
        if labels:
            data["labels"] = labels

        result = github_client.post(f"repos/{owner}/{repo}/issues", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_pull_requests",
    description="列出仓库的Pull Requests",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "state": {
                "type": "string",
                "description": "PR状态",
                "enum": ["open", "closed", "all"],
                "default": "open"
            },
            "head": {
                "type": "string",
                "description": "分支筛选",
                "default": ""
            },
            "base": {
                "type": "string",
                "description": "基础分支筛选",
                "default": ""
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["created", "updated", "popularity", "long-running"],
                "default": "created"
            },
            "direction": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "pull-requests", "list"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react", "state": "closed"}
        ]
    }
)
def github_list_pull_requests(owner: str, repo: str, state: str = "open", head: str = "", base: str = "",
                             sort: str = "created", direction: str = "desc", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的Pull Requests"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "state": state,
            "sort": sort,
            "direction": direction,
            "per_page": min(per_page, 100),
            "page": page
        }

        if head:
            params["head"] = head
        if base:
            params["base"] = base

        result = github_client.get(f"repos/{owner}/{repo}/pulls", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_pull_request",
    description="创建新的Pull Request",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "title": {
                "type": "string",
                "description": "PR标题"
            },
            "head": {
                "type": "string",
                "description": "源分支"
            },
            "base": {
                "type": "string",
                "description": "目标分支"
            },
            "body": {
                "type": "string",
                "description": "PR描述",
                "default": ""
            },
            "maintainer_can_modify": {
                "type": "boolean",
                "description": "允许维护者修改",
                "default": True
            },
            "draft": {
                "type": "boolean",
                "description": "创建草稿PR",
                "default": False
            }
        },
        "required": ["owner", "repo", "title", "head", "base"]
    },
    metadata={
        "tags": ["github", "pull-requests", "create"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "title": "Feature implementation",
                "head": "feature-branch",
                "base": "main",
                "body": "This PR implements a new feature"
            }
        ]
    }
)
def github_create_pull_request(owner: str, repo: str, title: str, head: str, base: str, body: str = "",
                              maintainer_can_modify: bool = True, draft: bool = False) -> Dict[str, Any]:
    """创建新的Pull Request"""
    try:
        if not owner or not repo or not title or not head or not base:
            return {"success": False, "error": "owner、repo、title、head和base参数不能为空"}

        data = {
            "title": title,
            "head": head,
            "base": base,
            "body": body,
            "maintainer_can_modify": maintainer_can_modify,
            "draft": draft
        }

        result = github_client.post(f"repos/{owner}/{repo}/pulls", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_branches",
    description="列出仓库的分支",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "protected": {
                "type": "boolean",
                "description": "只显示受保护的分支",
                "default": False
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "branches", "list"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react", "protected": True}
        ]
    }
)
def github_list_branches(owner: str, repo: str, protected: bool = False, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的分支"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if protected:
            params["protected"] = "true"

        result = github_client.get(f"repos/{owner}/{repo}/branches", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_branch",
    description="获取特定分支信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "branch": {
                "type": "string",
                "description": "分支名称"
            }
        },
        "required": ["owner", "repo", "branch"]
    },
    metadata={
        "tags": ["github", "branch", "info"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "branch": "main"},
            {"owner": "facebook", "repo": "react", "branch": "develop"}
        ]
    }
)
def github_get_branch(owner: str, repo: str, branch: str) -> Dict[str, Any]:
    """获取特定分支信息"""
    try:
        if not owner or not repo or not branch:
            return {"success": False, "error": "owner、repo和branch参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/branches/{branch}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_commits",
    description="列出仓库的提交历史",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "sha": {
                "type": "string",
                "description": "分支或提交SHA",
                "default": ""
            },
            "path": {
                "type": "string",
                "description": "文件路径筛选",
                "default": ""
            },
            "author": {
                "type": "string",
                "description": "作者筛选",
                "default": ""
            },
            "since": {
                "type": "string",
                "description": "开始时间（ISO 8601格式）",
                "default": ""
            },
            "until": {
                "type": "string",
                "description": "结束时间（ISO 8601格式）",
                "default": ""
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "commits", "history"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react", "author": "gaearon"}
        ]
    }
)
def github_list_commits(owner: str, repo: str, sha: str = "", path: str = "", author: str = "",
                       since: str = "", until: str = "", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的提交历史"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if sha:
            params["sha"] = sha
        if path:
            params["path"] = path
        if author:
            params["author"] = author
        if since:
            params["since"] = since
        if until:
            params["until"] = until

        result = github_client.get(f"repos/{owner}/{repo}/commits", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_commit",
    description="获取特定提交的详细信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "ref": {
                "type": "string",
                "description": "提交SHA"
            }
        },
        "required": ["owner", "repo", "ref"]
    },
    metadata={
        "tags": ["github", "commit", "info"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "ref": "abc123"},
            {"owner": "facebook", "repo": "react", "ref": "def456"}
        ]
    }
)
def github_get_commit(owner: str, repo: str, ref: str) -> Dict[str, Any]:
    """获取特定提交的详细信息"""
    try:
        if not owner or not repo or not ref:
            return {"success": False, "error": "owner、repo和ref参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/commits/{ref}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_releases",
    description="列出仓库的发布版本",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "releases", "list"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react"}
        ]
    }
)
def github_list_releases(owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的发布版本"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        result = github_client.get(f"repos/{owner}/{repo}/releases", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_latest_release",
    description="获取仓库的最新发布版本",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "release", "latest"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react"}
        ]
    }
)
def github_get_latest_release(owner: str, repo: str) -> Dict[str, Any]:
    """获取仓库的最新发布版本"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/releases/latest")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="search_repositories",
    description="搜索GitHub仓库",
    schema={
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": "搜索查询字符串"
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["stars", "forks", "help-wanted-issues", "updated"],
                "default": "best-match"
            },
            "order": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["q"]
    },
    metadata={
        "tags": ["github", "search", "repositories"],
        "examples": [
            {"q": "javascript framework"},
            {"q": "language:python", "sort": "stars"},
            {"q": "user:microsoft language:typescript"}
        ]
    }
)
def github_search_repositories(q: str, sort: str = "", order: str = "desc", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """搜索GitHub仓库"""
    try:
        if not q:
            return {"success": False, "error": "q参数不能为空"}

        params = {
            "q": q,
            "order": order,
            "per_page": min(per_page, 100),
            "page": page
        }

        if sort:
            params["sort"] = sort

        result = github_client.get("search/repositories", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="search_issues",
    description="搜索GitHub Issues",
    schema={
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": "搜索查询字符串"
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["comments", "reactions", "reactions-+1", "reactions--1", "reactions-smile", "reactions-thinking_face", "reactions-heart", "reactions-tada", "interactions", "created", "updated"],
                "default": "best-match"
            },
            "order": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["q"]
    },
    metadata={
        "tags": ["github", "search", "issues"],
        "examples": [
            {"q": "bug label:bug"},
            {"q": "is:open is:issue repo:microsoft/vscode"},
            {"q": "author:octocat"}
        ]
    }
)
def github_search_issues(q: str, sort: str = "", order: str = "desc", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """搜索GitHub Issues"""
    try:
        if not q:
            return {"success": False, "error": "q参数不能为空"}

        params = {
            "q": q,
            "order": order,
            "per_page": min(per_page, 100),
            "page": page
        }

        if sort:
            params["sort"] = sort

        result = github_client.get("search/issues", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== 文件操作工具 ====

@github_tool(
    name="get_file_contents",
    description="获取GitHub仓库中文件或目录的内容",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "path": {
                "type": "string",
                "description": "文件或目录路径",
                "default": ""
            },
            "ref": {
                "type": "string",
                "description": "分支、标签或提交SHA",
                "default": ""
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "file", "content"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "path": "README.md"},
            {"owner": "facebook", "repo": "react", "path": "src", "ref": "main"}
        ]
    }
)
def github_get_file_contents(owner: str, repo: str, path: str = "", ref: str = "") -> Dict[str, Any]:
    """获取GitHub仓库中文件或目录的内容"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        endpoint = f"repos/{owner}/{repo}/contents"
        if path:
            endpoint += f"/{path}"

        params = {}
        if ref:
            params["ref"] = ref

        result = github_client.get(endpoint, params)

        # 如果是文件内容，解码Base64
        if result.get("success") and "data" in result:
            if isinstance(result["data"], dict) and "content" in result["data"]:
                try:
                    content = result["data"]["content"]
                    decoded_content = base64.b64decode(content).decode('utf-8')
                    result["data"]["decoded_content"] = decoded_content
                except Exception:
                    pass  # 如果解码失败，保持原样

        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_or_update_file",
    description="在GitHub仓库中创建或更新文件",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "content": {
                "type": "string",
                "description": "文件内容（Base64编码）"
            },
            "message": {
                "type": "string",
                "description": "提交信息"
            },
            "branch": {
                "type": "string",
                "description": "分支名称",
                "default": "main"
            },
            "sha": {
                "type": "string",
                "description": "文件SHA（更新时必需）",
                "default": ""
            }
        },
        "required": ["owner", "repo", "path", "content", "message"]
    },
    metadata={
        "tags": ["github", "file", "create", "update"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "path": "docs/README.md",
                "content": "IyBSZWFkbWU=",
                "message": "Add README file"
            }
        ]
    }
)
def github_create_or_update_file(owner: str, repo: str, path: str, content: str, message: str,
                                 branch: str = "main", sha: str = "") -> Dict[str, Any]:
    """在GitHub仓库中创建或更新文件"""
    try:
        if not owner or not repo or not path or not content or not message:
            return {"success": False, "error": "owner、repo、path、content和message参数不能为空"}

        # 如果内容不是Base64格式，先编码
        try:
            base64.b64decode(content).decode('utf-8')
            encoded_content = content
        except Exception:
            encoded_content = base64.b64encode(content.encode('utf-8')).decode('ascii')

        data = {
            "message": message,
            "content": encoded_content,
            "branch": branch
        }

        if sha:
            data["sha"] = sha

        result = github_client.post(f"repos/{owner}/{repo}/contents/{path}", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="delete_file",
    description="删除GitHub仓库中的文件",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "path": {
                "type": "string",
                "description": "文件路径"
            },
            "message": {
                "type": "string",
                "description": "提交信息"
            },
            "sha": {
                "type": "string",
                "description": "文件SHA"
            },
            "branch": {
                "type": "string",
                "description": "分支名称",
                "default": "main"
            }
        },
        "required": ["owner", "repo", "path", "message", "sha"]
    },
    metadata={
        "tags": ["github", "file", "delete"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "path": "old-file.txt",
                "message": "Remove old file",
                "sha": "abc123def456"
            }
        ]
    }
)
def github_delete_file(owner: str, repo: str, path: str, message: str, sha: str, branch: str = "main") -> Dict[str, Any]:
    """删除GitHub仓库中的文件"""
    try:
        if not owner or not repo or not path or not message or not sha:
            return {"success": False, "error": "owner、repo、path、message和sha参数不能为空"}

        data = {
            "message": message,
            "sha": sha,
            "branch": branch
        }

        result = github_client.delete(f"repos/{owner}/{repo}/contents/{path}", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== Pull Request 高级操作 ====

@github_tool(
    name="get_pull_request",
    description="获取Pull Request详细信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "pull_number": {
                "type": "integer",
                "description": "Pull Request编号"
            }
        },
        "required": ["owner", "repo", "pull_number"]
    },
    metadata={
        "tags": ["github", "pull-request", "detail"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "pull_number": 123}
        ]
    }
)
def github_get_pull_request(owner: str, repo: str, pull_number: int) -> Dict[str, Any]:
    """获取Pull Request详细信息"""
    try:
        if not owner or not repo or not pull_number:
            return {"success": False, "error": "owner、repo和pull_number参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/pulls/{pull_number}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_pull_request_files",
    description="获取Pull Request中变更的文件列表",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "pull_number": {
                "type": "integer",
                "description": "Pull Request编号"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo", "pull_number"]
    },
    metadata={
        "tags": ["github", "pull-request", "files"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "pull_number": 123}
        ]
    }
)
def github_get_pull_request_files(owner: str, repo: str, pull_number: int, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """获取Pull Request中变更的文件列表"""
    try:
        if not owner or not repo or not pull_number:
            return {"success": False, "error": "owner、repo和pull_number参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        result = github_client.get(f"repos/{owner}/{repo}/pulls/{pull_number}/files", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="merge_pull_request",
    description="合并Pull Request",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "pull_number": {
                "type": "integer",
                "description": "Pull Request编号"
            },
            "commit_title": {
                "type": "string",
                "description": "合并提交标题",
                "default": ""
            },
            "commit_message": {
                "type": "string",
                "description": "合并提交信息",
                "default": ""
            },
            "merge_method": {
                "type": "string",
                "description": "合并方式",
                "enum": ["merge", "squash", "rebase"],
                "default": "merge"
            }
        },
        "required": ["owner", "repo", "pull_number"]
    },
    metadata={
        "tags": ["github", "pull-request", "merge"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "pull_number": 123,
                "merge_method": "squash"
            }
        ]
    }
)
def github_merge_pull_request(owner: str, repo: str, pull_number: int, commit_title: str = "",
                             commit_message: str = "", merge_method: str = "merge") -> Dict[str, Any]:
    """合并Pull Request"""
    try:
        if not owner or not repo or not pull_number:
            return {"success": False, "error": "owner、repo和pull_number参数不能为空"}

        data = {
            "merge_method": merge_method
        }

        if commit_title:
            data["commit_title"] = commit_title
        if commit_message:
            data["commit_message"] = commit_message

        result = github_client.post(f"repos/{owner}/{repo}/pulls/{pull_number}/merge", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== Issue 操作扩展 ====

@github_tool(
    name="get_issue",
    description="获取Issue详细信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "issue_number": {
                "type": "integer",
                "description": "Issue编号"
            }
        },
        "required": ["owner", "repo", "issue_number"]
    },
    metadata={
        "tags": ["github", "issue", "detail"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "issue_number": 456}
        ]
    }
)
def github_get_issue(owner: str, repo: str, issue_number: int) -> Dict[str, Any]:
    """获取Issue详细信息"""
    try:
        if not owner or not repo or not issue_number:
            return {"success": False, "error": "owner、repo和issue_number参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/issues/{issue_number}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="update_issue",
    description="更新Issue信息",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "issue_number": {
                "type": "integer",
                "description": "Issue编号"
            },
            "title": {
                "type": "string",
                "description": "Issue标题",
                "default": ""
            },
            "body": {
                "type": "string",
                "description": "Issue内容",
                "default": ""
            },
            "state": {
                "type": "string",
                "description": "Issue状态",
                "enum": ["open", "closed"],
                "default": ""
            },
            "assignees": {
                "type": "array",
                "items": {"type": "string"},
                "description": "指派人列表",
                "default": []
            },
            "labels": {
                "type": "array",
                "items": {"type": "string"},
                "description": "标签列表",
                "default": []
            }
        },
        "required": ["owner", "repo", "issue_number"]
    },
    metadata={
        "tags": ["github", "issue", "update"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "issue_number": 456,
                "state": "closed",
                "labels": ["resolved"]
            }
        ]
    }
)
def github_update_issue(owner: str, repo: str, issue_number: int, title: str = "", body: str = "",
                       state: str = "", assignees: List[str] = [], labels: List[str] = []) -> Dict[str, Any]:
    """更新Issue信息"""
    try:
        if not owner or not repo or not issue_number:
            return {"success": False, "error": "owner、repo和issue_number参数不能为空"}

        data = {}

        if title:
            data["title"] = title
        if body:
            data["body"] = body
        if state:
            data["state"] = state
        if assignees:
            data["assignees"] = assignees
        if labels:
            data["labels"] = labels

        if not data:
            return {"success": False, "error": "至少需要提供一个更新字段"}

        result = github_client.patch(f"repos/{owner}/{repo}/issues/{issue_number}", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="add_issue_comment",
    description="为Issue添加评论",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "issue_number": {
                "type": "integer",
                "description": "Issue编号"
            },
            "body": {
                "type": "string",
                "description": "评论内容"
            }
        },
        "required": ["owner", "repo", "issue_number", "body"]
    },
    metadata={
        "tags": ["github", "issue", "comment"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "issue_number": 456,
                "body": "Thanks for reporting this issue!"
            }
        ]
    }
)
def github_add_issue_comment(owner: str, repo: str, issue_number: int, body: str) -> Dict[str, Any]:
    """为Issue添加评论"""
    try:
        if not owner or not repo or not issue_number or not body:
            return {"success": False, "error": "owner、repo、issue_number和body参数不能为空"}

        data = {
            "body": body
        }

        result = github_client.post(f"repos/{owner}/{repo}/issues/{issue_number}/comments", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== GitHub Actions 工具 ====

@github_tool(
    name="list_workflows",
    description="列出仓库的GitHub Actions工作流",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "actions", "workflows"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"}
        ]
    }
)
def github_list_workflows(owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的GitHub Actions工作流"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        result = github_client.get(f"repos/{owner}/{repo}/actions/workflows", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="list_workflow_runs",
    description="列出工作流的运行记录",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "workflow_id": {
                "type": "string",
                "description": "工作流ID或文件名"
            },
            "actor": {
                "type": "string",
                "description": "触发用户",
                "default": ""
            },
            "branch": {
                "type": "string",
                "description": "分支名",
                "default": ""
            },
            "event": {
                "type": "string",
                "description": "触发事件",
                "default": ""
            },
            "status": {
                "type": "string",
                "description": "运行状态",
                "enum": ["queued", "in_progress", "completed"],
                "default": ""
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo", "workflow_id"]
    },
    metadata={
        "tags": ["github", "actions", "runs"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "workflow_id": "ci.yml"}
        ]
    }
)
def github_list_workflow_runs(owner: str, repo: str, workflow_id: str, actor: str = "", branch: str = "",
                              event: str = "", status: str = "", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出工作流的运行记录"""
    try:
        if not owner or not repo or not workflow_id:
            return {"success": False, "error": "owner、repo和workflow_id参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        if actor:
            params["actor"] = actor
        if branch:
            params["branch"] = branch
        if event:
            params["event"] = event
        if status:
            params["status"] = status

        result = github_client.get(f"repos/{owner}/{repo}/actions/workflows/{workflow_id}/runs", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="get_workflow_run",
    description="获取工作流运行详情",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "run_id": {
                "type": "integer",
                "description": "运行ID"
            }
        },
        "required": ["owner", "repo", "run_id"]
    },
    metadata={
        "tags": ["github", "actions", "run", "detail"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode", "run_id": 123456}
        ]
    }
)
def github_get_workflow_run(owner: str, repo: str, run_id: int) -> Dict[str, Any]:
    """获取工作流运行详情"""
    try:
        if not owner or not repo or not run_id:
            return {"success": False, "error": "owner、repo和run_id参数不能为空"}

        result = github_client.get(f"repos/{owner}/{repo}/actions/runs/{run_id}")
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== 标签和里程碑 ====

@github_tool(
    name="list_tags",
    description="列出仓库的Git标签",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "tags", "git"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"}
        ]
    }
)
def github_list_tags(owner: str, repo: str, per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """列出仓库的Git标签"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        params = {
            "per_page": min(per_page, 100),
            "page": page
        }

        result = github_client.get(f"repos/{owner}/{repo}/tags", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_release",
    description="创建新的GitHub Release",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "tag_name": {
                "type": "string",
                "description": "标签名称"
            },
            "target_commitish": {
                "type": "string",
                "description": "目标分支或提交SHA",
                "default": "main"
            },
            "name": {
                "type": "string",
                "description": "Release标题",
                "default": ""
            },
            "body": {
                "type": "string",
                "description": "Release描述",
                "default": ""
            },
            "draft": {
                "type": "boolean",
                "description": "是否为草稿",
                "default": False
            },
            "prerelease": {
                "type": "boolean",
                "description": "是否为预发布版本",
                "default": False
            }
        },
        "required": ["owner", "repo", "tag_name"]
    },
    metadata={
        "tags": ["github", "release", "create"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "tag_name": "v1.0.0",
                "name": "Version 1.0.0",
                "body": "First stable release"
            }
        ]
    }
)
def github_create_release(owner: str, repo: str, tag_name: str, target_commitish: str = "main",
                         name: str = "", body: str = "", draft: bool = False, prerelease: bool = False) -> Dict[str, Any]:
    """创建新的GitHub Release"""
    try:
        if not owner or not repo or not tag_name:
            return {"success": False, "error": "owner、repo和tag_name参数不能为空"}

        data = {
            "tag_name": tag_name,
            "target_commitish": target_commitish,
            "name": name if name else tag_name,
            "body": body,
            "draft": draft,
            "prerelease": prerelease
        }

        result = github_client.post(f"repos/{owner}/{repo}/releases", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== Fork 和 分支操作 ====

@github_tool(
    name="fork_repository",
    description="Fork GitHub仓库到个人账户或组织",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "原仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "原仓库名称"
            },
            "organization": {
                "type": "string",
                "description": "目标组织（留空则Fork到个人账户）",
                "default": ""
            }
        },
        "required": ["owner", "repo"]
    },
    metadata={
        "tags": ["github", "fork", "repository"],
        "examples": [
            {"owner": "microsoft", "repo": "vscode"},
            {"owner": "facebook", "repo": "react", "organization": "myorg"}
        ]
    }
)
def github_fork_repository(owner: str, repo: str, organization: str = "") -> Dict[str, Any]:
    """Fork GitHub仓库到个人账户或组织"""
    try:
        if not owner or not repo:
            return {"success": False, "error": "owner和repo参数不能为空"}

        data = {}
        if organization:
            data["organization"] = organization

        result = github_client.post(f"repos/{owner}/{repo}/forks", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="create_branch",
    description="创建新分支",
    schema={
        "type": "object",
        "properties": {
            "owner": {
                "type": "string",
                "description": "仓库所有者"
            },
            "repo": {
                "type": "string",
                "description": "仓库名称"
            },
            "branch": {
                "type": "string",
                "description": "新分支名称"
            },
            "from_branch": {
                "type": "string",
                "description": "源分支名称",
                "default": "main"
            }
        },
        "required": ["owner", "repo", "branch"]
    },
    metadata={
        "tags": ["github", "branch", "create"],
        "examples": [
            {
                "owner": "myorg",
                "repo": "myrepo",
                "branch": "feature-new-ui",
                "from_branch": "develop"
            }
        ]
    }
)
def github_create_branch(owner: str, repo: str, branch: str, from_branch: str = "main") -> Dict[str, Any]:
    """创建新分支"""
    try:
        if not owner or not repo or not branch:
            return {"success": False, "error": "owner、repo和branch参数不能为空"}

        # 首先获取源分支的SHA
        ref_result = github_client.get(f"repos/{owner}/{repo}/git/ref/heads/{from_branch}")
        if not ref_result.get("success"):
            return {"success": False, "error": f"无法获取源分支 {from_branch} 的信息"}

        sha = ref_result["data"]["object"]["sha"]

        # 创建新分支
        data = {
            "ref": f"refs/heads/{branch}",
            "sha": sha
        }

        result = github_client.post(f"repos/{owner}/{repo}/git/refs", data)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# ==== 搜索工具扩展 ====

@github_tool(
    name="search_code",
    description="搜索GitHub代码",
    schema={
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": "搜索查询字符串"
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["indexed"],
                "default": ""
            },
            "order": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["q"]
    },
    metadata={
        "tags": ["github", "search", "code"],
        "examples": [
            {"q": "function language:javascript"},
            {"q": "console.log repo:microsoft/vscode"},
            {"q": "import React language:typescript"}
        ]
    }
)
def github_search_code(q: str, sort: str = "", order: str = "desc", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """搜索GitHub代码"""
    try:
        if not q:
            return {"success": False, "error": "q参数不能为空"}

        params = {
            "q": q,
            "order": order,
            "per_page": min(per_page, 100),
            "page": page
        }

        if sort:
            params["sort"] = sort

        result = github_client.get("search/code", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


@github_tool(
    name="search_users",
    description="搜索GitHub用户",
    schema={
        "type": "object",
        "properties": {
            "q": {
                "type": "string",
                "description": "搜索查询字符串"
            },
            "sort": {
                "type": "string",
                "description": "排序方式",
                "enum": ["followers", "repositories", "joined"],
                "default": ""
            },
            "order": {
                "type": "string",
                "description": "排序方向",
                "enum": ["asc", "desc"],
                "default": "desc"
            },
            "per_page": {
                "type": "integer",
                "description": "每页数量",
                "minimum": 1,
                "maximum": 100,
                "default": 30
            },
            "page": {
                "type": "integer",
                "description": "页码",
                "minimum": 1,
                "default": 1
            }
        },
        "required": ["q"]
    },
    metadata={
        "tags": ["github", "search", "users"],
        "examples": [
            {"q": "tom"},
            {"q": "location:seattle language:python"},
            {"q": "followers:>100"}
        ]
    }
)
def github_search_users(q: str, sort: str = "", order: str = "desc", per_page: int = 30, page: int = 1) -> Dict[str, Any]:
    """搜索GitHub用户"""
    try:
        if not q:
            return {"success": False, "error": "q参数不能为空"}

        params = {
            "q": q,
            "order": order,
            "per_page": min(per_page, 100),
            "page": page
        }

        if sort:
            params["sort"] = sort

        result = github_client.get("search/users", params)
        return result
    except Exception as e:
        return {"success": False, "error": str(e)}


# 全局GitHub客户端重新加载函数
def reload_github_client_config():
    """重新加载GitHub客户端配置"""
    try:
        global github_client
        # 重新创建GitHub客户端实例以加载新配置
        github_client = GitHubAPIClient()
        return True
    except Exception as e:
        logger.error(f"Failed to reload GitHub client config: {e}")
        return False