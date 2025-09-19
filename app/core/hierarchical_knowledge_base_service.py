"""
分层知识库服务
支持知识库 > 文件夹 > 文件的层级结构管理
"""
import os
import json
import hashlib
import asyncio
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Tuple
from datetime import datetime
import aiofiles
import pandas as pd
from sentence_transformers import SentenceTransformer
import requests
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

from app.core.config import PROJECT_ROOT
from app.core.logging import setup_logging
from app.models.knowledge_base_models import (
    KnowledgeBase, KnowledgeFolder, KnowledgeFile, DocumentChunk,
    FolderType, FileType, ProcessStatus, VectorDatabaseConfig,
    CreateKnowledgeBaseRequest, CreateFolderRequest, AddFileRequest,
    SearchRequest, SearchResult, KnowledgeBaseStats, FolderStats
)
from app.core.knowledge_base_service import DocumentProcessor, TextChunker
from app.core.vector_database_interface import VectorDatabaseFactory, VectorDatabaseInterface

logger = setup_logging()


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
            # 使用Web抓取MCP工具
            from app.tools.web_scraping_tools import web_scraping_webpage

            try:
                # 使用智能网页抓取工具
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
                    # 回退到基础抓取
                    files = await DataSourceProcessor._fallback_basic_scraping(url)

            except Exception as mcp_error:
                logger.warning(f"Web scraping MCP tool failed: {mcp_error}, falling back to basic scraping")
                # 回退到基础抓取
                files = await DataSourceProcessor._fallback_basic_scraping(url)

        except Exception as e:
            logger.error(f"Error processing website {url}: {e}")

        return files

    @staticmethod
    async def _fallback_basic_scraping(url: str) -> List[Dict[str, Any]]:
        """回退到基础网页抓取"""
        files = []
        try:
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

            # 使用GitHub MCP工具获取仓库内容
            from app.tools.github_tools import github_get_file_contents

            try:
                # 获取根目录内容
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
                # 回退到直接API调用
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


class HierarchicalKnowledgeBaseService:
    """分层知识库服务"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or os.path.join(PROJECT_ROOT, "data", "hierarchical_kb")
        self.vector_db = None  # 改用向量数据库接口
        self.model = None
        self.chunker = TextChunker()
        self.doc_processor = DocumentProcessor()
        self.data_source_processor = DataSourceProcessor()

        # 确保数据库目录存在
        os.makedirs(self.db_path, exist_ok=True)

    async def initialize(self, vector_db_config: VectorDatabaseConfig = None):
        """初始化分层知识库服务"""
        try:
            # 使用传入的配置或默认配置初始化向量数据库
            if vector_db_config is None:
                vector_db_config = VectorDatabaseConfig()

            # 创建向量数据库实例
            config = vector_db_config.config.copy()
            config["type"] = vector_db_config.type
            if vector_db_config.type == "lancedb":
                config["path"] = config.get("path", self.db_path)

            self.vector_db = VectorDatabaseFactory.create_database(config)
            await self.vector_db.initialize()

            # 初始化嵌入模型
            logger.info(f"Loading sentence transformer model: {vector_db_config.embedding_model}")
            self.model = SentenceTransformer(vector_db_config.embedding_model)

            # 创建所有必要的表
            await self._ensure_tables_exist()

            logger.info(f"Hierarchical knowledge base service initialized successfully with {vector_db_config.type}")
        except Exception as e:
            logger.error(f"Failed to initialize hierarchical knowledge base service: {e}")
            raise

    async def _ensure_tables_exist(self):
        """确保所有必要的表存在（延迟创建）"""
        # 创建所有必要的集合/表schema
        schemas = {
            "knowledge_bases": self._get_knowledge_base_schema(),
            "knowledge_folders": self._get_folder_schema(),
            "knowledge_files": self._get_file_schema(),
            "document_chunks": self._get_chunk_schema()
        }

        for table_name, schema in schemas.items():
            if not await self.vector_db.collection_exists(table_name):
                await self.vector_db.create_collection(table_name, schema)

    def _get_knowledge_base_schema(self):
        """获取知识库表的schema"""
        return {
            "id": "string",
            "name": "string",
            "description": "string",
            "icon": "string",
            "color": "string",
            "tags": "string",  # JSON字符串
            "vector_db_config": "string",  # JSON字符串
            "created_at": "string",
            "updated_at": "string",
            "folder_count": "int",
            "file_count": "int",
            "total_size": "int"
        }

    def _get_folder_schema(self):
        """获取文件夹表的schema"""
        return {
            "id": "string",
            "knowledge_base_id": "string",
            "parent_folder_id": "string",
            "name": "string",
            "description": "string",
            "folder_type": "string",
            "path": "string",
            "config": "string",  # JSON字符串
            "tags": "string",  # JSON字符串
            "icon": "string",
            "color": "string",
            "created_at": "string",
            "updated_at": "string",
            "sub_folder_count": "int",
            "file_count": "int",
            "total_size": "int",
            "status": "string"
        }

    def _get_file_schema(self):
        """获取文件表的schema"""
        return {
            "id": "string",
            "knowledge_base_id": "string",
            "folder_id": "string",
            "name": "string",
            "original_name": "string",
            "file_type": "string",
            "file_extension": "string",
            "file_path": "string",
            "url": "string",
            "file_size": "int",
            "file_hash": "string",
            "content_preview": "string",
            "tags": "string",  # JSON字符串
            "metadata": "string",  # JSON字符串
            "created_at": "string",
            "updated_at": "string",
            "processed_at": "string",
            "chunks_count": "int",
            "status": "string"
        }

    def _get_chunk_schema(self):
        """获取文档块表的schema"""
        return {
            "id": "string",
            "file_id": "string",
            "knowledge_base_id": "string",
            "chunk_index": "int",
            "content": "string",
            "embedding": "vector(384)",  # all-MiniLM-L6-v2的维度
            "metadata": "string",  # JSON字符串
            "created_at": "string"
        }

    # 知识库管理方法
    async def create_knowledge_base(self, request: CreateKnowledgeBaseRequest) -> KnowledgeBase:
        """创建知识库"""
        try:
            # 确保数据库和表都存在
            if not self.vector_db:
                await self.initialize(request.vector_db_config)

            kb_id = str(uuid.uuid4())
            now = datetime.now()

            kb_data = {
                "id": kb_id,
                "name": request.name,
                "description": request.description or "",
                "icon": request.icon or "",
                "color": request.color or "",
                "tags": json.dumps(request.tags),
                "vector_db_config": json.dumps(request.vector_db_config.dict() if request.vector_db_config else VectorDatabaseConfig().dict()),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "folder_count": 0,
                "file_count": 0,
                "total_size": 0
            }

            # 插入数据到向量数据库
            await self.vector_db.insert_data("knowledge_bases", [kb_data])

            logger.info(f"Created knowledge base: {request.name}")

            return KnowledgeBase(
                id=kb_id,
                name=request.name,
                description=request.description,
                icon=request.icon,
                color=request.color,
                tags=request.tags,
                vector_db_config=request.vector_db_config or VectorDatabaseConfig(),
                created_at=now,
                updated_at=now,
                folder_count=0,
                file_count=0,
                total_size=0
            )

        except Exception as e:
            logger.error(f"Error creating knowledge base: {e}")
            raise

    async def list_knowledge_bases(self) -> List[KnowledgeBase]:
        """列出所有知识库"""
        try:
            if not self.vector_db:
                await self.initialize()

            results = await self.vector_db.query("knowledge_bases", limit=1000)

            knowledge_bases = []
            for result in results:
                vector_db_config_data = json.loads(result.get("vector_db_config", "{}"))
                vector_db_config = VectorDatabaseConfig(**vector_db_config_data) if vector_db_config_data else VectorDatabaseConfig()

                kb = KnowledgeBase(
                    id=result["id"],
                    name=result["name"],
                    description=result["description"],
                    icon=result["icon"],
                    color=result["color"],
                    tags=json.loads(result["tags"]) if result["tags"] else [],
                    vector_db_config=vector_db_config,
                    created_at=datetime.fromisoformat(result["created_at"]),
                    updated_at=datetime.fromisoformat(result["updated_at"]),
                    folder_count=result["folder_count"],
                    file_count=result["file_count"],
                    total_size=result["total_size"]
                )
                knowledge_bases.append(kb)

            return knowledge_bases

        except Exception as e:
            logger.error(f"Error listing knowledge bases: {e}")
            return []

    async def create_folder(self, request: CreateFolderRequest) -> KnowledgeFolder:
        """创建文件夹"""
        try:
            folder_id = str(uuid.uuid4())
            now = datetime.now()

            folder_data = {
                "id": folder_id,
                "knowledge_base_id": request.knowledge_base_id,
                "parent_folder_id": request.parent_folder_id or "",
                "name": request.name,
                "description": request.description or "",
                "folder_type": request.folder_type.value,
                "path": request.path or "",
                "config": json.dumps(request.config),
                "tags": json.dumps(request.tags),
                "icon": request.icon or "",
                "color": request.color or "",
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "sub_folder_count": 0,
                "file_count": 0,
                "total_size": 0,
                "status": ProcessStatus.PENDING.value
            }

            # 插入数据到向量数据库
            await self.vector_db.insert_data("knowledge_folders", [folder_data])

            # 异步处理文件夹内容
            asyncio.create_task(self._process_folder_content(folder_id, request))

            logger.info(f"Created folder: {request.name}")

            return KnowledgeFolder(
                id=folder_id,
                knowledge_base_id=request.knowledge_base_id,
                parent_folder_id=request.parent_folder_id,
                name=request.name,
                description=request.description,
                folder_type=request.folder_type,
                path=request.path,
                config=request.config,
                tags=request.tags,
                icon=request.icon,
                color=request.color,
                created_at=now,
                updated_at=now,
                sub_folder_count=0,
                file_count=0,
                total_size=0,
                status=ProcessStatus.PENDING
            )

        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            raise

    async def _process_folder_content(self, folder_id: str, request: CreateFolderRequest):
        """异步处理文件夹内容"""
        try:
            # 更新状态为处理中
            await self._update_folder_status(folder_id, ProcessStatus.PROCESSING)

            # 根据文件夹类型处理内容
            files = []
            if request.folder_type == FolderType.LOCAL:
                files = await self.data_source_processor.process_local_folder(request.path, request.config)
            elif request.folder_type == FolderType.WEBSITE:
                files = await self.data_source_processor.process_website(request.path, request.config)
            elif request.folder_type == FolderType.GITHUB:
                files = await self.data_source_processor.process_github_repo(request.path, request.config)

            # 批量添加文件
            for file_info in files:
                file_request = AddFileRequest(
                    knowledge_base_id=request.knowledge_base_id,
                    folder_id=folder_id,
                    name=file_info["name"],
                    file_type=self._determine_file_type(file_info),
                    file_path=file_info.get("path"),
                    url=file_info.get("url"),
                    metadata=file_info
                )
                await self.add_file(file_request)

            # 更新状态为完成
            await self._update_folder_status(folder_id, ProcessStatus.COMPLETED)

        except Exception as e:
            logger.error(f"Error processing folder content for {folder_id}: {e}")
            await self._update_folder_status(folder_id, ProcessStatus.FAILED)

    def _determine_file_type(self, file_info: Dict[str, Any]) -> FileType:
        """根据文件信息确定文件类型"""
        if "url" in file_info and "github" in file_info.get("url", ""):
            return FileType.REPOSITORY
        elif "url" in file_info:
            return FileType.WEBPAGE
        else:
            return FileType.DOCUMENT

    async def _update_folder_status(self, folder_id: str, status: ProcessStatus):
        """更新文件夹状态"""
        try:
            update_data = {
                "status": status.value,
                "updated_at": datetime.now().isoformat()
            }
            conditions = {"id": folder_id}
            await self.vector_db.update_data("knowledge_folders", [update_data], conditions)
        except Exception as e:
            logger.error(f"Error updating folder status: {e}")

    async def add_file(self, request: AddFileRequest) -> KnowledgeFile:
        """添加文件"""
        try:
            file_id = str(uuid.uuid4())
            now = datetime.now()

            # 处理文件内容
            content = ""
            file_hash = ""
            file_size = 0

            if request.file_path:
                # 处理本地文件
                content = await self.doc_processor.extract_text_from_file(request.file_path)
                file_hash = self._calculate_file_hash(request.file_path)
                file_size = Path(request.file_path).stat().st_size
            elif request.url:
                # 处理网络文件
                content = await self._download_and_process_url(request.url)
                file_hash = hashlib.md5(content.encode()).hexdigest()
                file_size = len(content.encode())

            file_data = {
                "id": file_id,
                "knowledge_base_id": request.knowledge_base_id,
                "folder_id": request.folder_id or "",
                "name": request.name or Path(request.file_path or request.url or "").name,
                "original_name": Path(request.file_path or request.url or "").name,
                "file_type": request.file_type.value,
                "file_extension": Path(request.file_path or request.url or "").suffix,
                "file_path": request.file_path or "",
                "url": request.url or "",
                "file_size": file_size,
                "file_hash": file_hash,
                "content_preview": content[:200] if content else "",
                "tags": json.dumps(request.tags),
                "metadata": json.dumps(request.metadata),
                "created_at": now.isoformat(),
                "updated_at": now.isoformat(),
                "processed_at": now.isoformat() if content else "",
                "chunks_count": 0,
                "status": ProcessStatus.PENDING.value if content else ProcessStatus.FAILED.value
            }

            # 插入数据到向量数据库
            await self.vector_db.insert_data("knowledge_files", [file_data])

            # 异步处理文档分块和向量化
            if content:
                asyncio.create_task(self._process_file_content(file_id, content))

            logger.info(f"Added file: {file_data['name']}")

            return KnowledgeFile(
                id=file_id,
                knowledge_base_id=request.knowledge_base_id,
                folder_id=request.folder_id,
                name=file_data['name'],
                original_name=file_data['original_name'],
                file_type=request.file_type,
                file_extension=file_data['file_extension'],
                file_path=request.file_path,
                url=request.url,
                file_size=file_size,
                file_hash=file_hash,
                content_preview=file_data['content_preview'],
                tags=request.tags,
                metadata=request.metadata,
                created_at=now,
                updated_at=now,
                processed_at=now if content else None,
                chunks_count=0,
                status=ProcessStatus.PENDING if content else ProcessStatus.FAILED
            )

        except Exception as e:
            logger.error(f"Error adding file: {e}")
            raise

    async def _download_and_process_url(self, url: str) -> str:
        """下载并处理URL内容"""
        try:
            response = requests.get(url, timeout=30)
            response.raise_for_status()

            if url.endswith('.html') or 'text/html' in response.headers.get('content-type', ''):
                # 处理HTML内容
                soup = BeautifulSoup(response.content, 'html.parser')
                return soup.get_text()
            else:
                return response.text

        except Exception as e:
            logger.error(f"Error downloading URL {url}: {e}")
            return ""

    async def _process_file_content(self, file_id: str, content: str):
        """异步处理文件内容，分块和向量化"""
        try:
            if not content.strip():
                return

            # 文本分块
            chunks = self.chunker.chunk_text(content, {"file_id": file_id})

            # 生成向量并保存
            chunk_data = []
            for chunk in chunks:
                chunk_id = str(uuid.uuid4())
                embedding = self.model.encode(chunk['text'])

                chunk_record = {
                    "id": chunk_id,
                    "file_id": file_id,
                    "knowledge_base_id": "",  # 需要从文件表中获取
                    "chunk_index": chunk['metadata']['chunk_index'],
                    "content": chunk['text'],
                    "embedding": embedding.tolist(),
                    "metadata": json.dumps(chunk['metadata']),
                    "created_at": datetime.now().isoformat()
                }
                chunk_data.append(chunk_record)

            if chunk_data:
                # 插入数据到向量数据库
                await self.vector_db.insert_data("document_chunks", chunk_data)

                logger.info(f"Processed {len(chunk_data)} chunks for file {file_id}")

        except Exception as e:
            logger.error(f"Error processing file content for {file_id}: {e}")

    def _calculate_file_hash(self, file_path: str) -> str:
        """计算文件哈希"""
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()

    async def search_documents(self, request: SearchRequest) -> List[SearchResult]:
        """搜索文档"""
        try:
            # 生成查询向量
            query_embedding = self.model.encode(request.query)

            # 在向量数据库中搜索
            results = await self.vector_db.search(
                "document_chunks",
                query_embedding.tolist(),
                limit=request.limit
            )

            # 处理搜索结果
            search_results = []
            for result in results:
                score = float(result.get('_distance', 0))
                if score >= request.threshold:
                    # 这里需要连接查询获取更多信息
                    search_result = SearchResult(
                        content=result['content'],
                        score=score,
                        file_id=result['file_id'],
                        file_name="",  # 需要从文件表获取
                        knowledge_base_id=result['knowledge_base_id'],
                        knowledge_base_name="",  # 需要从知识库表获取
                        folder_id="",  # 需要从文件表获取
                        folder_name="",  # 需要从文件夹表获取
                        chunk_index=result['chunk_index'],
                        metadata=json.loads(result['metadata'])
                    )
                    search_results.append(search_result)

            return search_results

        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []


# 全局服务实例
_hierarchical_knowledge_base_service = None

def init_hierarchical_knowledge_base_service() -> HierarchicalKnowledgeBaseService:
    """初始化分层知识库服务"""
    global _hierarchical_knowledge_base_service
    if _hierarchical_knowledge_base_service is None:
        _hierarchical_knowledge_base_service = HierarchicalKnowledgeBaseService()
    return _hierarchical_knowledge_base_service

def get_hierarchical_knowledge_base_service() -> HierarchicalKnowledgeBaseService:
    """获取分层知识库服务实例"""
    if _hierarchical_knowledge_base_service is None:
        return init_hierarchical_knowledge_base_service()
    return _hierarchical_knowledge_base_service