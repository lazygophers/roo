"""
GitHub工具集
使用装饰器自动注册GitHub相关的MCP工具，所有工具名称以github_开头
"""
from app.core.mcp_tool_registry import github_tool


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
def github_get_repository():
    """获取GitHub仓库详细信息"""
    pass


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
def github_list_repositories():
    """列出用户或组织的仓库列表"""
    pass


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
def github_create_repository():
    """创建新的GitHub仓库"""
    pass


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
def github_get_user():
    """获取GitHub用户信息"""
    pass


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
def github_list_issues():
    """列出仓库的Issues"""
    pass


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
def github_create_issue():
    """创建新的Issue"""
    pass


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
def github_list_pull_requests():
    """列出仓库的Pull Requests"""
    pass


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
def github_create_pull_request():
    """创建新的Pull Request"""
    pass


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
def github_list_branches():
    """列出仓库的分支"""
    pass


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
def github_get_branch():
    """获取特定分支信息"""
    pass


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
def github_list_commits():
    """列出仓库的提交历史"""
    pass


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
def github_get_commit():
    """获取特定提交的详细信息"""
    pass


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
def github_list_releases():
    """列出仓库的发布版本"""
    pass


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
def github_get_latest_release():
    """获取仓库的最新发布版本"""
    pass


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
def github_search_repositories():
    """搜索GitHub仓库"""
    pass


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
def github_search_issues():
    """搜索GitHub Issues"""
    pass


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
def github_get_file_contents():
    """获取GitHub仓库中文件或目录的内容"""
    pass


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
def github_create_or_update_file():
    """在GitHub仓库中创建或更新文件"""
    pass


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
def github_delete_file():
    """删除GitHub仓库中的文件"""
    pass


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
def github_get_pull_request():
    """获取Pull Request详细信息"""
    pass


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
def github_get_pull_request_files():
    """获取Pull Request中变更的文件列表"""
    pass


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
def github_merge_pull_request():
    """合并Pull Request"""
    pass


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
def github_get_issue():
    """获取Issue详细信息"""
    pass


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
def github_update_issue():
    """更新Issue信息"""
    pass


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
def github_add_issue_comment():
    """为Issue添加评论"""
    pass


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
def github_list_workflows():
    """列出仓库的GitHub Actions工作流"""
    pass


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
def github_list_workflow_runs():
    """列出工作流的运行记录"""
    pass


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
def github_get_workflow_run():
    """获取工作流运行详情"""
    pass


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
def github_list_tags():
    """列出仓库的Git标签"""
    pass


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
def github_create_release():
    """创建新的GitHub Release"""
    pass


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
def github_fork_repository():
    """Fork GitHub仓库到个人账户或组织"""
    pass


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
def github_create_branch():
    """创建新分支"""
    pass


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
def github_search_code():
    """搜索GitHub代码"""
    pass


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
def github_search_users():
    """搜索GitHub用户"""
    pass