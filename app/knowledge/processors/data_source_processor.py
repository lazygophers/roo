"""
数据源处理器，支持多种数据源类型
"""
import os
import requests
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime
from urllib.parse import urlparse
import logging

logger = logging.getLogger(__name__)


class DataSourceProcessor:
    """数据源处理器，支持多种数据源类型"""

    @staticmethod
    async def process_local_folder(folder_path: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """处理本地文件夹"""
        files = []
        try:
            folder_path = Path(folder_path)
            if not folder_path.exists() or not folder_path.is_dir():
                raise ValueError(f"Invalid local folder path: {folder_path}")

            # 递归扫描文件夹
            for file_path in folder_path.rglob("*"):
                if file_path.is_file():
                    file_info = {
                        "name": file_path.name,
                        "path": str(file_path),
                        "size": file_path.stat().st_size,
                        "extension": file_path.suffix.lower(),
                        "modified_at": datetime.fromtimestamp(file_path.stat().st_mtime)
                    }
                    files.append(file_info)
        except Exception as e:
            logger.error(f"Error processing local folder {folder_path}: {e}")

        return files

    @staticmethod
    async def process_website(url: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """处理网站链接，使用Web抓取MCP工具"""
        files = []
        try:
            # 优先使用Web抓取MCP工具
            try:
                from app.tools.web_scraping_tools import web_scraping_webpage

                scraping_result = await web_scraping_webpage(
                    url=url,
                    options={
                        "extract_content": True,
                        "extract_metadata": True,
                        "convert_to_markdown": True,
                        "timeout": config.get("timeout", 30) if config else 30
                    }
                )

                if scraping_result.get("success") and scraping_result.get("data"):
                    data = scraping_result["data"]

                    file_info = {
                        "name": data.get("title", urlparse(url).path.split("/")[-1] or "webpage"),
                        "url": url,
                        "size": len(data.get("content", "")),
                        "extension": ".md",  # 转换为Markdown格式
                        "modified_at": datetime.now(),
                        "content": data.get("content", ""),
                        "metadata": {
                            "title": data.get("title", ""),
                            "description": data.get("description", ""),
                            "keywords": data.get("keywords", []),
                            "author": data.get("author", ""),
                            "lang": data.get("lang", ""),
                            "links": data.get("links", []),
                            "images": data.get("images", [])
                        }
                    }
                    files.append(file_info)
                else:
                    logger.warning(f"Web scraping MCP tool failed for {url}, falling back to basic scraping")
                    files = await DataSourceProcessor._fallback_basic_scraping(url)

            except Exception as mcp_error:
                logger.warning(f"Web scraping MCP tool failed: {mcp_error}, falling back to basic scraping")
                files = await DataSourceProcessor._fallback_basic_scraping(url)

        except Exception as e:
            logger.error(f"Error processing website {url}: {e}")

        return files

    @staticmethod
    async def _fallback_basic_scraping(url: str) -> List[Dict[str, Any]]:
        """回退到基础网页抓取"""
        files = []
        try:
            from bs4 import BeautifulSoup

            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')
            title = soup.find('title')

            file_info = {
                "name": title.text.strip() if title else urlparse(url).path,
                "url": url,
                "size": len(response.content),
                "extension": ".html",
                "modified_at": datetime.now(),
                "content": response.text
            }
            files.append(file_info)
        except Exception as e:
            logger.error(f"Basic scraping also failed for {url}: {e}")

        return files

    @staticmethod
    async def process_github_repo(repo_url: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """处理GitHub仓库，使用GitHub MCP工具"""
        files = []
        try:
            # 解析GitHub仓库URL
            parsed_url = urlparse(repo_url)
            if "github.com" not in parsed_url.netloc:
                raise ValueError("Invalid GitHub repository URL")

            # 提取owner和repo名称
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) < 2:
                raise ValueError("Invalid GitHub repository URL format")

            owner, repo = path_parts[0], path_parts[1]

            # 优先使用GitHub MCP工具
            try:
                from app.tools.github_tools import github_get_file_contents

                contents_result = await github_get_file_contents(owner=owner, repo=repo, path="/")

                if contents_result.get("success") and contents_result.get("data"):
                    contents = contents_result["data"]

                    # 处理文件列表
                    for item in contents:
                        if item.get("type") == "file":
                            file_info = {
                                "name": item["name"],
                                "url": item.get("download_url", ""),
                                "size": item.get("size", 0),
                                "extension": Path(item["name"]).suffix.lower(),
                                "modified_at": datetime.now(),
                                "github_path": item.get("path", ""),
                                "sha": item.get("sha", ""),
                                "github_url": item.get("html_url", "")
                            }
                            files.append(file_info)
                        elif item.get("type") == "dir":
                            # 递归处理子目录
                            sub_files = await DataSourceProcessor._process_github_directory(
                                owner, repo, item.get("path", ""), max_depth=3
                            )
                            files.extend(sub_files)
                else:
                    logger.warning(f"Failed to get GitHub contents for {owner}/{repo}")

            except Exception as mcp_error:
                logger.warning(f"GitHub MCP tool failed, falling back to direct API: {mcp_error}")
                files = await DataSourceProcessor._fallback_github_api(owner, repo, config)

        except Exception as e:
            logger.error(f"Error processing GitHub repo {repo_url}: {e}")

        return files

    @staticmethod
    async def _process_github_directory(owner: str, repo: str, path: str, max_depth: int = 3) -> List[Dict[str, Any]]:
        """递归处理GitHub目录"""
        files = []
        if max_depth <= 0:
            return files

        try:
            from app.tools.github_tools import github_get_file_contents

            contents_result = await github_get_file_contents(owner=owner, repo=repo, path=path)

            if contents_result.get("success") and contents_result.get("data"):
                contents = contents_result["data"]

                for item in contents:
                    if item.get("type") == "file":
                        file_info = {
                            "name": item["name"],
                            "url": item.get("download_url", ""),
                            "size": item.get("size", 0),
                            "extension": Path(item["name"]).suffix.lower(),
                            "modified_at": datetime.now(),
                            "github_path": item.get("path", ""),
                            "sha": item.get("sha", ""),
                            "github_url": item.get("html_url", "")
                        }
                        files.append(file_info)
                    elif item.get("type") == "dir":
                        # 递归处理子目录
                        sub_files = await DataSourceProcessor._process_github_directory(
                            owner, repo, item.get("path", ""), max_depth - 1
                        )
                        files.extend(sub_files)
        except Exception as e:
            logger.error(f"Error processing GitHub directory {path}: {e}")

        return files

    @staticmethod
    async def _fallback_github_api(owner: str, repo: str, config: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """回退到直接GitHub API调用"""
        files = []
        try:
            api_url = f"https://api.github.com/repos/{owner}/{repo}/contents"
            headers = {}
            if config and config.get("github_token"):
                headers["Authorization"] = f"token {config['github_token']}"

            response = requests.get(api_url, headers=headers, timeout=10)
            response.raise_for_status()

            contents = response.json()

            for item in contents:
                if item["type"] == "file":
                    file_info = {
                        "name": item["name"],
                        "url": item["download_url"],
                        "size": item["size"],
                        "extension": Path(item["name"]).suffix.lower(),
                        "modified_at": datetime.now(),
                        "github_path": item["path"]
                    }
                    files.append(file_info)
        except Exception as e:
            logger.error(f"Fallback GitHub API also failed: {e}")

        return files