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
    file_size: Optional[int] = None
    last_modified: Optional[int] = None


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
    last_modified: int


class RulesResponse(BaseModel):
    """Rules API 响应数据结构"""
    success: bool
    message: str
    slug: str
    searched_directories: List[str]
    found_directories: List[str]
    data: List[FileMetadata]
    total: int


# POST 请求数据模型
class ModelsRequest(BaseModel):
    """Models API POST 请求数据结构"""
    slug: Optional[str] = None
    category: Optional[str] = None
    search: Optional[str] = None


class ModelBySlugRequest(BaseModel):
    """根据 slug 获取单个模型的请求数据结构"""
    slug: str


class RulesRequest(BaseModel):
    """Rules API POST 请求数据结构"""
    slug: str


class CommandsResponse(BaseModel):
    """Commands API 响应数据结构"""
    success: bool
    message: str
    data: List[FileMetadata]
    total: int


class SelectedItem(BaseModel):
    """选中项数据结构"""
    id: str
    type: str  # 'model', 'command', 'rule'
    name: str
    data: Dict[str, Any]


class ModelRuleBinding(BaseModel):
    """模型-规则绑定关系数据结构"""
    modelId: str
    selectedRuleIds: List[str]


class ConfigurationData(BaseModel):
    """配置数据结构"""
    name: str
    description: Optional[str] = None
    selectedItems: List[SelectedItem]
    modelRuleBindings: List[ModelRuleBinding]
    modelRules: Dict[str, List[Dict[str, Any]]]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class SaveConfigurationRequest(BaseModel):
    """保存配置请求数据结构"""
    name: str
    description: Optional[str] = None
    selectedItems: List[SelectedItem]
    modelRuleBindings: List[ModelRuleBinding]
    modelRules: Dict[str, List[Dict[str, Any]]]
    overwrite: bool = False


class ConfigurationResponse(BaseModel):
    """配置响应数据结构"""
    success: bool
    message: str
    data: Optional[ConfigurationData] = None


class ConfigurationListResponse(BaseModel):
    """配置列表响应数据结构"""
    success: bool
    message: str
    data: List[ConfigurationData]
    total: int


class GetConfigurationRequest(BaseModel):
    """获取单个配置请求数据结构"""
    name: str


class DeleteConfigurationRequest(BaseModel):
    """删除配置请求数据结构"""
    name: str


class RoleInfo(BaseModel):
    """角色信息数据结构"""
    name: str
    title: str
    description: str
    category: str
    traits: List[str]
    features: List[str]
    restrictions: Optional[List[str]] = None
    file_path: str


class RoleResponse(BaseModel):
    """角色 API 响应数据结构"""
    success: bool
    message: str
    data: List[RoleInfo]
    total: int