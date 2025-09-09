from typing import List, Dict, Any, Optional
from pydantic import BaseModel


class ModelInfo(BaseModel):
    """模型信息数据结构"""
    slug: str
    name: str
    roleDefinition: str
    whenToUse: str
    description: str
    groups: List[Any]
    file_path: str


class ModelsResponse(BaseModel):
    """API 响应数据结构"""
    success: bool
    message: str
    data: List[ModelInfo]
    total: int


class ErrorResponse(BaseModel):
    """错误响应数据结构"""
    success: bool
    message: str
    error_detail: Optional[str] = None


class HookInfo(BaseModel):
    """Hook 文件信息数据结构"""
    name: str
    title: str
    description: str
    category: str
    priority: str
    tags: List[str]
    examples: Optional[List[str]] = None
    content: str
    file_path: str


class HookResponse(BaseModel):
    """Hook API 响应数据结构"""
    success: bool
    message: str
    data: HookInfo


class FileMetadata(BaseModel):
    """文件 metadata 信息数据结构"""
    name: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    language: Optional[str] = None
    priority: Optional[str] = None
    tags: Optional[List[str]] = None
    sections: Optional[List[str]] = None
    references: Optional[List[str]] = None
    file_path: str
    source_directory: str
    file_size: int
    last_modified: str


class RulesResponse(BaseModel):
    """Rules API 响应数据结构"""
    success: bool
    message: str
    slug: str
    searched_directories: List[str]
    found_directories: List[str]
    data: List[FileMetadata]
    total: int