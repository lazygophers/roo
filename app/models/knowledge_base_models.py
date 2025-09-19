"""
分层知识库数据模型
支持知识库 > 文件夹 > 文件的层级结构
"""
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import BaseModel
from enum import Enum


class FolderType(str, Enum):
    """文件夹类型枚举"""
    LOCAL = "local"          # 本地文件夹
    WEBSITE = "website"      # 网站链接
    GITHUB = "github"        # GitHub仓库
    CLOUD = "cloud"          # 云存储
    VIRTUAL = "virtual"      # 虚拟文件夹（用于组织）


class FileType(str, Enum):
    """文件类型枚举"""
    DOCUMENT = "document"    # 文档文件
    WEBPAGE = "webpage"      # 网页
    REPOSITORY = "repository"  # 代码仓库
    NOTE = "note"           # 笔记
    BOOKMARK = "bookmark"    # 书签


class ProcessStatus(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"      # 待处理
    PROCESSING = "processing"  # 处理中
    COMPLETED = "completed"  # 已完成
    FAILED = "failed"        # 处理失败


class VectorDatabaseConfig(BaseModel):
    """向量数据库配置模型"""
    type: str = "lancedb"  # 数据库类型：lancedb, chroma, qdrant等
    config: Dict[str, Any] = {}  # 具体配置参数
    embedding_model: str = "all-MiniLM-L6-v2"  # 嵌入模型


class KnowledgeBase(BaseModel):
    """知识库模型"""
    id: str
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: List[str] = []
    vector_db_config: VectorDatabaseConfig = VectorDatabaseConfig()  # 向量数据库配置
    created_at: datetime
    updated_at: datetime
    folder_count: int = 0
    file_count: int = 0
    total_size: int = 0  # 总大小（字节）


class KnowledgeFolder(BaseModel):
    """知识库文件夹模型"""
    id: str
    knowledge_base_id: str
    parent_folder_id: Optional[str] = None  # 父文件夹ID，为空表示根级文件夹
    name: str
    description: Optional[str] = None
    folder_type: FolderType
    path: Optional[str] = None  # 本地路径或URL
    config: Dict[str, Any] = {}  # 配置信息（如GitHub token、网站抓取配置等）
    tags: List[str] = []
    icon: Optional[str] = None
    color: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    sub_folder_count: int = 0
    file_count: int = 0
    total_size: int = 0
    status: ProcessStatus = ProcessStatus.PENDING


class KnowledgeFile(BaseModel):
    """知识库文件模型"""
    id: str
    knowledge_base_id: str
    folder_id: Optional[str] = None  # 所属文件夹ID，为空表示在根目录
    name: str
    original_name: str  # 原始文件名
    file_type: FileType
    file_extension: Optional[str] = None
    file_path: Optional[str] = None  # 本地文件路径
    url: Optional[str] = None  # 网络资源URL
    file_size: int = 0
    file_hash: Optional[str] = None
    content_preview: Optional[str] = None  # 内容预览
    tags: List[str] = []
    metadata: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime
    processed_at: Optional[datetime] = None
    chunks_count: int = 0
    status: ProcessStatus = ProcessStatus.PENDING


class DocumentChunk(BaseModel):
    """文档块模型"""
    id: str
    file_id: str
    knowledge_base_id: str
    chunk_index: int
    content: str
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = {}
    created_at: datetime


# API请求/响应模型
class CreateKnowledgeBaseRequest(BaseModel):
    """创建知识库请求"""
    name: str
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: List[str] = []
    vector_db_config: Optional[VectorDatabaseConfig] = None


class UpdateKnowledgeBaseRequest(BaseModel):
    """更新知识库请求"""
    name: Optional[str] = None
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    tags: Optional[List[str]] = None


class CreateFolderRequest(BaseModel):
    """创建文件夹请求"""
    knowledge_base_id: str
    parent_folder_id: Optional[str] = None
    name: str
    description: Optional[str] = None
    folder_type: FolderType
    path: Optional[str] = None
    config: Dict[str, Any] = {}
    tags: List[str] = []
    icon: Optional[str] = None
    color: Optional[str] = None


class AddFileRequest(BaseModel):
    """添加文件请求"""
    knowledge_base_id: str
    folder_id: Optional[str] = None
    name: Optional[str] = None
    file_type: FileType
    file_path: Optional[str] = None
    url: Optional[str] = None
    tags: List[str] = []
    metadata: Dict[str, Any] = {}


class SearchRequest(BaseModel):
    """搜索请求"""
    query: str
    knowledge_base_ids: Optional[List[str]] = None
    folder_ids: Optional[List[str]] = None
    file_types: Optional[List[FileType]] = None
    tags: Optional[List[str]] = None
    limit: int = 10
    threshold: float = 0.3


class SearchResult(BaseModel):
    """搜索结果"""
    content: str
    score: float
    file_id: str
    file_name: str
    knowledge_base_id: str
    knowledge_base_name: str
    folder_id: Optional[str] = None
    folder_name: Optional[str] = None
    chunk_index: int
    metadata: Dict[str, Any] = {}


# 统计信息模型
class KnowledgeBaseStats(BaseModel):
    """知识库统计信息"""
    total_knowledge_bases: int
    total_folders: int
    total_files: int
    total_chunks: int
    total_size_bytes: int
    total_size_mb: float
    folder_type_stats: Dict[FolderType, int]
    file_type_stats: Dict[FileType, int]
    processing_stats: Dict[ProcessStatus, int]


class FolderStats(BaseModel):
    """文件夹统计信息"""
    folder_id: str
    folder_name: str
    sub_folder_count: int
    file_count: int
    total_size: int
    file_type_stats: Dict[FileType, int]
    processing_stats: Dict[ProcessStatus, int]