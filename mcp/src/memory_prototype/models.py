import lancedb
from lancedb.pydantic import LanceModel, Vector
from pydantic import Field
from datetime import datetime
import uuid
from typing import Dict, Any

class BaseMemory(LanceModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="唯一标识符")
    embedding: Vector(768)
    source: str = Field(description="记忆来源")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    usage_count: int = Field(default=0, description="被引用或检索的次数")
    last_accessed_at: datetime = Field(default_factory=datetime.utcnow, description="最后访问时间")
    manual_promote_flag: bool = Field(default=False, description="用户手动标记晋升")
    confidence: int = Field(default=100, description="记忆的可信度 (0-100)")

class ProjectMemory(BaseMemory):
    name: str = Field(description="项目名称")
    description: str = Field(description="项目的详细描述")
    content_type: str = "project"
    ttl: int = Field(default=-1, description="生命周期（天），-1 表示永不过期")
    level: int = 0

class RootTaskMemory(BaseMemory):
    project_id: str = Field(description="关联的项目 ID")
    objective: str = Field(description="根任务的核心目标")
    content_type: str = "root_task"
    ttl: int = Field(default=90, description="生命周期（天）")
    level: int = 1

class SubTaskMemory(BaseMemory):
    root_task_id: str = Field(description="关联的根任务 ID")
    details: str = Field(description="子任务的详细内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="可扩展的元数据")
    content_type: str = "sub_task"
    ttl: int = Field(default=30, description="生命周期（天）")
    level: int = 2