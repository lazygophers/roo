"""
GitHub工具模块专项深度测试
目标：将github_tools.py的测试覆盖率从20%提升到80%+
涵盖34个GitHub API函数的全面测试
"""
import pytest
import json
import base64
from unittest.mock import Mock, patch, MagicMock
from requests.adapters import HTTPAdapter
from requests import Session

# 尝试导入需要测试的模块，如果导入失败则跳过测试
try:
    from app.tools.github_tools import (
        GitHubAPIClient, github_client, reload_github_client_config,
        github_get_repository, github_list_repositories, github_create_repository,
        github_get_user, github_list_issues, github_create_issue,
        github_list_pull_requests, github_create_pull_request, github_list_branches,
        github_get_branch, github_list_commits, github_get_commit,
        github_list_releases, github_get_latest_release, github_search_repositories,
        github_search_issues, github_get_file_contents, github_create_or_update_file,
        github_delete_file, github_get_pull_request, github_get_pull_request_files,
        github_merge_pull_request, github_get_issue, github_update_issue,
        github_add_issue_comment, github_list_workflows, github_list_workflow_runs,
        github_get_workflow_run, github_list_tags, github_create_release,
        github_fork_repository, github_create_branch, github_search_code,
        github_search_users
    )
    GITHUB_TOOLS_AVAILABLE = True
except ImportError as e:
    GITHUB_TOOLS_AVAILABLE = False
    print(f"GitHub tools import failed: {e}")


@pytest.mark.skipif(not GITHUB_TOOLS_AVAILABLE, reason="GitHub tools module not available")
class TestGitHubToolsMegaCoverage:
    """GitHub工具模块深度测试套件"""

    @pytest.fixture
    def mock_mcp_config(self):
        """模拟MCP配置"""
        config = Mock()
        config.environment_variables = {"GITHUB_TOKEN": "test_token_from_mcp"}
        config.network = Mock()
        config.network.retry_times = 3
        config.network.user_agent = "LazyAI-Test"
        config.network.timeout = 30
        config.security = Mock()
        config.security.verify_ssl = True
        return config

    @pytest.fixture
    def mock_requests_session(self):
        """模拟requests会话"""
        session = Mock(spec=Session)
        session.headers = {}
        session.proxies = {}
        session.timeout = 30
        session.verify = True

        # 模拟成功响应
        response = Mock()
        response.status_code = 200
        response.json.return_value = {"test": "data"}
        response.text = "success"

        session.get.return_value = response
        session.post.return_value = response
        session.patch.return_value = response
        session.delete.return_value = response
        session.mount = Mock()

        return session

    def test_github_api_client_init_with_token(self, mock_mcp_config):
        """测试带token的GitHubAPIClient初始化"""
        with patch('app.tools.github_tools.get_mcp_config', return_value=mock_mcp_config), \
             patch('app.tools.github_tools.get_proxy_for_requests', return_value=None), \
             patch('app.tools.github_tools.requests.Session') as mock_session_class:

            mock_session = Mock()
            mock_session.headers = {}
            mock_session.proxies = {}
            mock_session_class.return_value = mock_session

            client = GitHubAPIClient(token="test_token")

            assert client.token == "test_token"
            assert client.base_url == "https://api.github.com"
            assert mock_session.headers.get("Authorization") is not None

    def test_github_api_client_init_without_config(self):
        """测试无配置的GitHubAPIClient初始化"""
        with patch('app.tools.github_tools.get_mcp_config', side_effect=Exception("Config not found")), \
             patch('app.tools.github_tools.requests.Session') as mock_session_class, \
             patch.dict('os.environ', {'GITHUB_TOKEN': 'env_token'}):

            mock_session = Mock()
            mock_session.headers = {}
            mock_session_class.return_value = mock_session

            client = GitHubAPIClient()

            assert client.token == "env_token"
            assert client.mcp_config is None

    def test_github_api_client_reload_config(self, mock_mcp_config):
        """测试重新加载配置"""
        with patch('app.tools.github_tools.get_mcp_config', return_value=mock_mcp_config), \
             patch('app.tools.github_tools.get_proxy_for_requests', return_value={"http": "proxy"}), \
             patch('app.tools.github_tools.requests.Session') as mock_session_class:

            mock_session = Mock()
            mock_session.headers = {}
            mock_session.proxies = {}
            mock_session_class.return_value = mock_session

            client = GitHubAPIClient()
            client.reload_config()

            # 验证代理配置被更新
            mock_session.proxies.clear.assert_called()
            mock_session.proxies.update.assert_called_with({"http": "proxy"})

    def test_github_api_client_get_success(self, mock_requests_session):
        """测试GET请求成功"""
        with patch('app.tools.github_tools.requests.Session', return_value=mock_requests_session):
            client = GitHubAPIClient()
            result = client.get("repos/test/repo")

            assert result["success"] is True
            assert "data" in result
            mock_requests_session.get.assert_called_once()

    def test_github_api_client_get_error(self, mock_requests_session):
        """测试GET请求错误"""
        mock_requests_session.get.return_value.status_code = 404
        mock_requests_session.get.return_value.text = "Not Found"

        with patch('app.tools.github_tools.requests.Session', return_value=mock_requests_session):
            client = GitHubAPIClient()
            result = client.get("repos/invalid/repo")

            assert result["success"] is False
            assert "HTTP 404" in result["error"]

    def test_github_api_client_post_created(self, mock_requests_session):
        """测试POST请求创建成功"""
        mock_requests_session.post.return_value.status_code = 201

        with patch('app.tools.github_tools.requests.Session', return_value=mock_requests_session):
            client = GitHubAPIClient()
            result = client.post("repos/test/repo", {"name": "test"})

            assert result["success"] is True
            mock_requests_session.post.assert_called_once()

    def test_github_api_client_patch_success(self, mock_requests_session):
        """测试PATCH请求成功"""
        with patch('app.tools.github_tools.requests.Session', return_value=mock_requests_session):
            client = GitHubAPIClient()
            result = client.patch("repos/test/repo", {"description": "updated"})

            assert result["success"] is True
            mock_requests_session.patch.assert_called_once()

    def test_github_api_client_delete_success(self, mock_requests_session):
        """测试DELETE请求成功"""
        mock_requests_session.delete.return_value.status_code = 204
        mock_requests_session.delete.return_value.text = ""

        with patch('app.tools.github_tools.requests.Session', return_value=mock_requests_session):
            client = GitHubAPIClient()
            result = client.delete("repos/test/repo")

            assert result["success"] is True
            assert "Deleted successfully" in result["data"]

    def test_github_api_client_exception_handling(self):
        """测试异常处理"""
        with patch('app.tools.github_tools.requests.Session') as mock_session_class:
            mock_session = Mock()
            mock_session.get.side_effect = Exception("Network error")
            mock_session_class.return_value = mock_session

            client = GitHubAPIClient()
            result = client.get("test")

            assert result["success"] is False
            assert "Network error" in result["error"]

    def test_reload_github_client_config(self):
        """测试重新加载全局GitHub客户端配置"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            reload_github_client_config()
            mock_client.reload_config.assert_called_once()

    # ==== Repository 相关测试 ====

    def test_github_get_repository_success(self):
        """测试获取仓库信息成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"name": "test-repo"}}

            result = github_get_repository("owner", "repo")

            assert result["success"] is True
            assert result["data"]["name"] == "test-repo"
            mock_client.get.assert_called_with("repos/owner/repo")

    def test_github_get_repository_empty_params(self):
        """测试获取仓库信息参数为空"""
        result = github_get_repository("", "repo")
        assert result["success"] is False
        assert "owner和repo参数不能为空" in result["error"]

        result = github_get_repository("owner", "")
        assert result["success"] is False
        assert "owner和repo参数不能为空" in result["error"]

    def test_github_list_repositories_success(self):
        """测试列出仓库成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": [{"name": "repo1"}]}

            result = github_list_repositories("owner", type="public", sort="created", per_page=50)

            assert result["success"] is True
            mock_client.get.assert_called_with("users/owner/repos", {
                "type": "public",
                "sort": "created",
                "direction": "desc",
                "per_page": 50
            })

    def test_github_list_repositories_max_per_page(self):
        """测试列出仓库最大页数限制"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            github_list_repositories("owner", per_page=150)  # 超过最大值100

            # 验证per_page被限制为100
            args, kwargs = mock_client.get.call_args
            assert kwargs["per_page"] == 100

    def test_github_create_repository_success(self):
        """测试创建仓库成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"name": "new-repo"}}

            result = github_create_repository(
                name="new-repo",
                description="Test repo",
                private=True,
                auto_init=True,
                gitignore_template="Python",
                license_template="MIT"
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    def test_github_create_repository_empty_name(self):
        """测试创建仓库名称为空"""
        result = github_create_repository(name="")
        assert result["success"] is False
        assert "name参数不能为空" in result["error"]

    # ==== User 相关测试 ====

    def test_github_get_user_with_username(self):
        """测试获取指定用户信息"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"login": "testuser"}}

            result = github_get_user("testuser")

            assert result["success"] is True
            mock_client.get.assert_called_with("users/testuser")

    def test_github_get_user_current_user(self):
        """测试获取当前用户信息"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"login": "currentuser"}}

            result = github_get_user("")

            assert result["success"] is True
            mock_client.get.assert_called_with("user")

    # ==== Issues 相关测试 ====

    def test_github_list_issues_with_filters(self):
        """测试带筛选条件列出Issues"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_issues(
                owner="owner",
                repo="repo",
                state="closed",
                assignee="user1",
                creator="user2",
                mentioned="user3",
                labels="bug,enhancement",
                milestone="v1.0",
                since="2023-01-01T00:00:00Z",
                sort="updated",
                per_page=50
            )

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["state"] == "closed"
            assert kwargs["assignee"] == "user1"
            assert kwargs["labels"] == "bug,enhancement"

    def test_github_create_issue_with_all_params(self):
        """测试创建Issue包含所有参数"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"number": 123}}

            result = github_create_issue(
                owner="owner",
                repo="repo",
                title="Test Issue",
                body="Issue description",
                assignees=["user1", "user2"],
                milestone=5,
                labels=["bug", "high-priority"]
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    def test_github_create_issue_missing_required_params(self):
        """测试创建Issue缺少必需参数"""
        result = github_create_issue("", "repo", "title")
        assert result["success"] is False
        assert "owner、repo和title参数不能为空" in result["error"]

    def test_github_get_issue_success(self):
        """测试获取Issue详情成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"number": 123}}

            result = github_get_issue("owner", "repo", 123)

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/issues/123")

    def test_github_update_issue_all_fields(self):
        """测试更新Issue所有字段"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.patch.return_value = {"success": True, "data": {"number": 123}}

            result = github_update_issue(
                owner="owner",
                repo="repo",
                issue_number=123,
                title="Updated title",
                body="Updated body",
                state="closed",
                assignees=["user1"],
                labels=["resolved"]
            )

            assert result["success"] is True
            mock_client.patch.assert_called_once()

    def test_github_update_issue_no_fields(self):
        """测试更新Issue无更新字段"""
        result = github_update_issue("owner", "repo", 123)
        assert result["success"] is False
        assert "至少需要提供一个更新字段" in result["error"]

    def test_github_add_issue_comment_success(self):
        """测试添加Issue评论成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"id": 456}}

            result = github_add_issue_comment("owner", "repo", 123, "Great issue!")

            assert result["success"] is True
            mock_client.post.assert_called_with("repos/owner/repo/issues/123/comments", {"body": "Great issue!"})

    # ==== Pull Requests 相关测试 ====

    def test_github_list_pull_requests_with_filters(self):
        """测试带筛选条件列出PR"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_pull_requests(
                owner="owner",
                repo="repo",
                state="closed",
                head="feature-branch",
                base="main",
                sort="updated"
            )

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["state"] == "closed"
            assert kwargs["head"] == "feature-branch"
            assert kwargs["base"] == "main"

    def test_github_create_pull_request_success(self):
        """测试创建PR成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"number": 456}}

            result = github_create_pull_request(
                owner="owner",
                repo="repo",
                title="Feature PR",
                head="feature-branch",
                base="main",
                body="PR description",
                draft=True
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    def test_github_get_pull_request_success(self):
        """测试获取PR详情成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"number": 456}}

            result = github_get_pull_request("owner", "repo", 456)

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/pulls/456")

    def test_github_get_pull_request_files_success(self):
        """测试获取PR文件列表成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": [{"filename": "test.py"}]}

            result = github_get_pull_request_files("owner", "repo", 456, per_page=50)

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/pulls/456/files", {"per_page": 50, "page": 1})

    def test_github_merge_pull_request_success(self):
        """测试合并PR成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"merged": True}}

            result = github_merge_pull_request(
                owner="owner",
                repo="repo",
                pull_number=456,
                commit_title="Merge feature",
                commit_message="Feature implementation",
                merge_method="squash"
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    # ==== Branches 相关测试 ====

    def test_github_list_branches_protected_only(self):
        """测试只列出受保护分支"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_branches("owner", "repo", protected=True)

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["protected"] == "true"

    def test_github_get_branch_success(self):
        """测试获取分支信息成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"name": "main"}}

            result = github_get_branch("owner", "repo", "main")

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/branches/main")

    def test_github_create_branch_success(self):
        """测试创建分支成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            # 模拟获取源分支SHA
            mock_client.get.return_value = {
                "success": True,
                "data": {"object": {"sha": "abc123"}}
            }
            mock_client.post.return_value = {"success": True, "data": {"ref": "refs/heads/new-branch"}}

            result = github_create_branch("owner", "repo", "new-branch", "develop")

            assert result["success"] is True
            # 验证调用了get和post
            assert mock_client.get.call_count == 1
            assert mock_client.post.call_count == 1

    def test_github_create_branch_source_not_found(self):
        """测试创建分支源分支不存在"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": False, "error": "Branch not found"}

            result = github_create_branch("owner", "repo", "new-branch", "nonexistent")

            assert result["success"] is False
            assert "无法获取源分支" in result["error"]

    # ==== Commits 相关测试 ====

    def test_github_list_commits_with_filters(self):
        """测试带筛选条件列出提交"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_commits(
                owner="owner",
                repo="repo",
                sha="main",
                path="src/",
                author="developer",
                since="2023-01-01T00:00:00Z",
                until="2023-12-31T23:59:59Z"
            )

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["sha"] == "main"
            assert kwargs["path"] == "src/"
            assert kwargs["author"] == "developer"

    def test_github_get_commit_success(self):
        """测试获取提交详情成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"sha": "abc123"}}

            result = github_get_commit("owner", "repo", "abc123")

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/commits/abc123")

    # ==== Releases 相关测试 ====

    def test_github_list_releases_success(self):
        """测试列出发布版本成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_releases("owner", "repo", per_page=50)

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/releases", {"per_page": 50, "page": 1})

    def test_github_get_latest_release_success(self):
        """测试获取最新发布版本成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"tag_name": "v1.0.0"}}

            result = github_get_latest_release("owner", "repo")

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/releases/latest")

    def test_github_create_release_success(self):
        """测试创建发布版本成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"tag_name": "v2.0.0"}}

            result = github_create_release(
                owner="owner",
                repo="repo",
                tag_name="v2.0.0",
                target_commitish="develop",
                name="Version 2.0.0",
                body="Major release",
                draft=True,
                prerelease=True
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    def test_github_list_tags_success(self):
        """测试列出标签成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": []}

            result = github_list_tags("owner", "repo")

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/tags", {"per_page": 30, "page": 1})

    # ==== Search 相关测试 ====

    def test_github_search_repositories_with_sort(self):
        """测试搜索仓库带排序"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"items": []}}

            result = github_search_repositories(
                q="javascript framework",
                sort="stars",
                order="asc",
                per_page=50
            )

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["q"] == "javascript framework"
            assert kwargs["sort"] == "stars"
            assert kwargs["order"] == "asc"

    def test_github_search_issues_success(self):
        """测试搜索Issues成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"items": []}}

            result = github_search_issues("bug label:bug", sort="comments")

            assert result["success"] is True
            mock_client.get.assert_called_with("search/issues", {
                "q": "bug label:bug",
                "order": "desc",
                "per_page": 30,
                "page": 1,
                "sort": "comments"
            })

    def test_github_search_code_success(self):
        """测试搜索代码成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"items": []}}

            result = github_search_code("function language:javascript")

            assert result["success"] is True
            mock_client.get.assert_called_with("search/code", {
                "q": "function language:javascript",
                "order": "desc",
                "per_page": 30,
                "page": 1
            })

    def test_github_search_users_success(self):
        """测试搜索用户成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"items": []}}

            result = github_search_users("tom", sort="followers")

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["sort"] == "followers"

    # ==== File Operations 相关测试 ====

    def test_github_get_file_contents_success(self):
        """测试获取文件内容成功"""
        file_content = base64.b64encode("Hello World".encode('utf-8')).decode('ascii')

        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {
                "success": True,
                "data": {"content": file_content, "type": "file"}
            }

            result = github_get_file_contents("owner", "repo", "README.md", "main")

            assert result["success"] is True
            assert result["data"]["decoded_content"] == "Hello World"

    def test_github_get_file_contents_directory(self):
        """测试获取目录内容"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {
                "success": True,
                "data": [{"name": "file1.txt", "type": "file"}]
            }

            result = github_get_file_contents("owner", "repo", "src/")

            assert result["success"] is True
            # 目录内容不会有decoded_content
            assert "decoded_content" not in str(result["data"])

    def test_github_create_or_update_file_create(self):
        """测试创建文件"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"content": {"sha": "abc123"}}}

            result = github_create_or_update_file(
                owner="owner",
                repo="repo",
                path="new-file.txt",
                content="Hello World",  # 非Base64格式，会自动编码
                message="Add new file",
                branch="main"
            )

            assert result["success"] is True
            mock_client.post.assert_called_once()

    def test_github_create_or_update_file_update_with_sha(self):
        """测试更新文件（提供SHA）"""
        encoded_content = base64.b64encode("Updated content".encode('utf-8')).decode('ascii')

        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"content": {"sha": "def456"}}}

            result = github_create_or_update_file(
                owner="owner",
                repo="repo",
                path="existing-file.txt",
                content=encoded_content,  # 已经是Base64格式
                message="Update file",
                sha="abc123"
            )

            assert result["success"] is True

    def test_github_delete_file_success(self):
        """测试删除文件成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.delete.return_value = {"success": True, "data": "Deleted"}

            result = github_delete_file(
                owner="owner",
                repo="repo",
                path="old-file.txt",
                message="Remove old file",
                sha="abc123",
                branch="main"
            )

            assert result["success"] is True

    # ==== GitHub Actions 相关测试 ====

    def test_github_list_workflows_success(self):
        """测试列出工作流成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"workflows": []}}

            result = github_list_workflows("owner", "repo")

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/actions/workflows", {"per_page": 30, "page": 1})

    def test_github_list_workflow_runs_with_filters(self):
        """测试带筛选条件列出工作流运行"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"workflow_runs": []}}

            result = github_list_workflow_runs(
                owner="owner",
                repo="repo",
                workflow_id="ci.yml",
                actor="developer",
                branch="main",
                event="push",
                status="completed"
            )

            assert result["success"] is True
            args, kwargs = mock_client.get.call_args
            assert kwargs["actor"] == "developer"
            assert kwargs["branch"] == "main"
            assert kwargs["event"] == "push"
            assert kwargs["status"] == "completed"

    def test_github_get_workflow_run_success(self):
        """测试获取工作流运行详情成功"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {"success": True, "data": {"id": 123456}}

            result = github_get_workflow_run("owner", "repo", 123456)

            assert result["success"] is True
            mock_client.get.assert_called_with("repos/owner/repo/actions/runs/123456")

    # ==== Fork 相关测试 ====

    def test_github_fork_repository_to_personal(self):
        """测试Fork仓库到个人账户"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"full_name": "user/repo"}}

            result = github_fork_repository("original-owner", "repo")

            assert result["success"] is True
            mock_client.post.assert_called_with("repos/original-owner/repo/forks", {})

    def test_github_fork_repository_to_organization(self):
        """测试Fork仓库到组织"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.post.return_value = {"success": True, "data": {"full_name": "org/repo"}}

            result = github_fork_repository("original-owner", "repo", "myorg")

            assert result["success"] is True
            mock_client.post.assert_called_with("repos/original-owner/repo/forks", {"organization": "myorg"})

    # ==== 异常处理测试 ====

    def test_function_exception_handling(self):
        """测试各函数的异常处理"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.side_effect = Exception("API Error")

            # 测试多个函数的异常处理
            functions_to_test = [
                (github_get_repository, ("owner", "repo")),
                (github_list_repositories, ("owner",)),
                (github_get_user, ("user",)),
                (github_list_issues, ("owner", "repo")),
                (github_list_pull_requests, ("owner", "repo")),
                (github_list_branches, ("owner", "repo")),
                (github_list_commits, ("owner", "repo")),
                (github_list_releases, ("owner", "repo")),
                (github_get_latest_release, ("owner", "repo")),
                (github_search_repositories, ("test query",)),
                (github_search_issues, ("test query",)),
                (github_get_file_contents, ("owner", "repo")),
                (github_list_workflows, ("owner", "repo")),
                (github_list_tags, ("owner", "repo")),
                (github_search_code, ("test query",)),
                (github_search_users, ("test query",))
            ]

            for func, args in functions_to_test:
                result = func(*args)
                assert result["success"] is False
                assert "API Error" in result["error"]

    def test_search_functions_empty_query(self):
        """测试搜索函数空查询参数"""
        search_functions = [
            github_search_repositories,
            github_search_issues,
            github_search_code,
            github_search_users
        ]

        for func in search_functions:
            result = func("")
            assert result["success"] is False
            assert "q参数不能为空" in result["error"]

    def test_edge_cases_and_boundary_conditions(self):
        """测试边界条件和特殊情况"""
        # 测试Base64解码失败的情况
        with patch('app.tools.github_tools.github_client') as mock_client:
            mock_client.get.return_value = {
                "success": True,
                "data": {"content": "invalid-base64", "type": "file"}
            }

            result = github_get_file_contents("owner", "repo", "file.txt")
            # 解码失败时应该保持原样
            assert result["success"] is True
            assert "decoded_content" not in result["data"]

    def test_comprehensive_parameter_validation(self):
        """测试全面的参数验证"""
        # 测试各种必需参数为空的情况
        test_cases = [
            (github_get_repository, {"owner": "", "repo": "test"}),
            (github_get_repository, {"owner": "test", "repo": ""}),
            (github_list_repositories, {"owner": ""}),
            (github_create_repository, {"name": ""}),
            (github_list_issues, {"owner": "", "repo": "test"}),
            (github_create_issue, {"owner": "", "repo": "test", "title": "test"}),
            (github_create_issue, {"owner": "test", "repo": "", "title": "test"}),
            (github_create_issue, {"owner": "test", "repo": "test", "title": ""}),
            (github_list_pull_requests, {"owner": "", "repo": "test"}),
            (github_create_pull_request, {"owner": "", "repo": "test", "title": "test", "head": "feature", "base": "main"}),
            (github_list_branches, {"owner": "", "repo": "test"}),
            (github_get_branch, {"owner": "", "repo": "test", "branch": "main"}),
            (github_list_commits, {"owner": "", "repo": "test"}),
            (github_get_commit, {"owner": "", "repo": "test", "ref": "abc123"}),
            (github_list_releases, {"owner": "", "repo": "test"}),
            (github_get_latest_release, {"owner": "", "repo": "test"}),
            (github_get_file_contents, {"owner": "", "repo": "test"}),
            (github_create_or_update_file, {"owner": "", "repo": "test", "path": "file.txt", "content": "test", "message": "test"}),
            (github_delete_file, {"owner": "", "repo": "test", "path": "file.txt", "message": "test", "sha": "abc123"}),
            (github_get_pull_request, {"owner": "", "repo": "test", "pull_number": 123}),
            (github_get_pull_request_files, {"owner": "", "repo": "test", "pull_number": 123}),
            (github_merge_pull_request, {"owner": "", "repo": "test", "pull_number": 123}),
            (github_get_issue, {"owner": "", "repo": "test", "issue_number": 123}),
            (github_update_issue, {"owner": "", "repo": "test", "issue_number": 123}),
            (github_add_issue_comment, {"owner": "", "repo": "test", "issue_number": 123, "body": "test"}),
            (github_list_workflows, {"owner": "", "repo": "test"}),
            (github_list_workflow_runs, {"owner": "", "repo": "test", "workflow_id": "ci.yml"}),
            (github_get_workflow_run, {"owner": "", "repo": "test", "run_id": 123}),
            (github_list_tags, {"owner": "", "repo": "test"}),
            (github_create_release, {"owner": "", "repo": "test", "tag_name": "v1.0.0"}),
            (github_fork_repository, {"owner": "", "repo": "test"}),
            (github_create_branch, {"owner": "", "repo": "test", "branch": "feature"})
        ]

        for func, kwargs in test_cases:
            result = func(**kwargs)
            assert result["success"] is False
            assert "不能为空" in result["error"]

    def test_complex_workflow_scenarios(self):
        """测试复杂的工作流场景"""
        with patch('app.tools.github_tools.github_client') as mock_client:
            # 模拟完整的开发工作流

            # 1. 创建仓库
            mock_client.post.return_value = {"success": True, "data": {"name": "test-repo"}}
            repo_result = github_create_repository("test-repo", description="Test repository", auto_init=True)
            assert repo_result["success"] is True

            # 2. 创建分支
            mock_client.get.return_value = {"success": True, "data": {"object": {"sha": "abc123"}}}
            branch_result = github_create_branch("owner", "test-repo", "feature-branch")
            assert branch_result["success"] is True

            # 3. 创建文件
            file_result = github_create_or_update_file(
                "owner", "test-repo", "feature.py", "print('Hello')", "Add feature"
            )
            assert file_result["success"] is True

            # 4. 创建PR
            pr_result = github_create_pull_request(
                "owner", "test-repo", "Add feature", "feature-branch", "main"
            )
            assert pr_result["success"] is True

            # 5. 创建Issue
            issue_result = github_create_issue(
                "owner", "test-repo", "Bug report", "Found a bug"
            )
            assert issue_result["success"] is True

if __name__ == "__main__":
    pytest.main([__file__, "-v"])