"""
@author: lancelrq
@description: Roo-Code 记忆系统核心数据模型
"""

import uuid
from datetime import datetime
from typing import Any, Literal

from lancedb.pydantic import LanceModel, Vector
from pydantic import Field


class BaseMemory(LanceModel):
    """
    记忆模型的抽象基类，定义了跨层级的通用字段。

    所有具体的记忆模型都应继承自此类，以确保数据结构的一致性。
    """

    id: str = Field(
        default_factory=lambda: str(uuid.uuid4()),
        description="唯一标识符，采用 UUIDv4 格式。",
    )
    embedding: Vector(768) = Field(
        description="内容的文本嵌入向量，维度为 768，用于向量相似度搜索。"
    )
    source: str = Field(
        default="manual",
        description="记忆来源的标识，例如 'user_input', 'api_call'。",
    )
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="记录创建的 UTC 时间。",
    )
    usage_count: int = Field(
        default=0,
        description="记录被引用或检索的次数，用于评估记忆的重要性。",
    )
    last_accessed_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="记录最后一次被访问的 UTC 时间，用于实现 LRU 淘汰策略。",
    )
    manual_promote_flag: bool = Field(
        default=False,
        description="手动标记，用于强制提升记忆层级或防止其被自动降级。",
    )
    confidence: int = Field(
        default=100,
        description="记忆的可信度 (0-100)。值越高表示系统对该记忆的准确性越有信心。",
    )

    class Config:
        """Pydantic 模型配置"""

        frozen = True  # 设为不可变对象，增强数据一致性


class CoreMemory(BaseMemory):
    """
    L0: 核心记忆模型。

    代表最高层级的记忆单元，定义了一个工作的总体范围和上下文。
    """

    name: str = Field(description="项目的正式名称。")
    description: str = Field(description="项目的详细描述，用于生成嵌入向量。")
    content_type: Literal["project"] = Field(
        default="project",
        description="内容类型标识，固定为 'project'。",
    )
    ttl: int = Field(
        default=-1,
        description="生命周期（天）。-1 表示永不过期。",
    )
    level: Literal[0] = Field(
        default=0,
        description="层级标识，固定为 0。",
    )


class KnowledgeMemory(BaseMemory):
    """
    L1: 知识记忆模型。

    隶属于一个核心记忆，代表一个具体、独立的核心任务目标。
    """

    core_id: str = Field(description="所属 CoreMemory 的 id。")
    objective: str = Field(description="根任务的核心目标描述。")
    content_type: Literal["root_task"] = Field(
        default="root_task",
        description="内容类型标识，固定为 'root_task'。",
    )
    ttl: int = Field(default=90, description="生命周期（天）。")
    level: Literal[1] = Field(default=1, description="层级标识，固定为 1。")


class WorkingMemory(BaseMemory):
    """
    L2: 工作记忆模型。

    由知识记忆分解而来，是最细粒度的记忆单元，用于记录具体的实现步骤、
    代码片段或关键思考。
    """

    knowledge_id: str = Field(description="所属 KnowledgeMemory 的 id。")
    details: str = Field(description="子任务的详细内容、代码或思考。")
    metadata: dict[str, Any] = Field(
        default_factory=dict,
        description="可扩展的元数据字段，用于存储结构化信息，如代码语言、关联文件等。",
    )
    content_type: Literal["sub_task"] = Field(
        default="sub_task",
        description="内容类型标识，固定为 'sub_task'。",
    )
    ttl: int = Field(
        default=30,
        description="生命周期（天）。",
    )
    level: Literal[2] = Field(
        default=2,
        description="层级标识，固定为 2。",
    )
