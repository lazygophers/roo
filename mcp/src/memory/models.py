# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/17 10:50
@Author  : roo
@File    : models.py
@Software: PyCharm
@Desc    : 定义了记忆库系统的核心数据模型，包括不同类型的记忆及其属性。
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, conint, confloat


class MemoryType(str, Enum):
    """记忆类型的枚举。

    定义了AI可以拥有的三种基本记忆类型。

    Attributes:
        CORE: 核心记忆，定义AI的身份、原则和行为边界。
        KNOWLEDGE: 知识库，存储跨会话的、可复用的知识和经验。
        WORKING: 工作记忆，存储与当前任务相关的临时上下文信息。
    """

    CORE = "CORE"
    KNOWLEDGE = "KNOWLEDGE"
    WORKING = "WORKING"


class KnowledgeType(str, Enum):
    """知识类型的枚举。

    对知识库中的知识进行分类，便于管理和检索。

    Attributes:
        SOLUTION: 经过验证的、用于解决特定问题的方案。
        PATTERN: 可复用的架构模式、设计模式或代码模式。
        FACT: 确定的技术事实、数据或行业规范。
        SKILL: 具体的操作技能、工具使用方法或编程技巧。
        EXPERIENCE: 从过去的项目或任务中总结出的实践经验。
        PRINCIPLE: 在特定领域内应当遵循的指导原则或最佳实践。
    """

    SOLUTION = "solution"
    PATTERN = "pattern"
    FACT = "fact"
    SKILL = "skill"
    EXPERIENCE = "experience"
    PRINCIPLE = "principle"


class Relation(BaseModel):
    """定义知识点之间的关联关系。

    用于构建知识图谱，表达知识之间的联系。

    Attributes:
        target_id: 关联的目标知识的唯一ID。
        type: 关联关系的类型，例如 'extends' (扩展), 'conflicts_with' (冲突),
              'depends_on' (依赖于)。
    """

    target_id: str = Field(..., description="关联的目标知识ID")
    type: str = Field(..., description="关联类型 (e.g., 'extends', 'conflicts_with')")


class BaseMemory(BaseModel):
    """所有记忆类型的基类模型。

    包含了所有记忆共有的基础字段，为不同类型的记忆提供了统一的结构。

    Attributes:
        id: 记忆的唯一标识符，自动生成。
        content: 记忆的具体内容，可以是简单的字符串，也可以是复杂的结构化数据。
        type: 记忆的类型，使用 `MemoryType` 枚举。
        created_at: 记忆创建的时间戳 (UTC)。
        updated_at: 记忆最后更新的时间戳 (UTC)。
        ttl: 存活时间（秒）。如果为 None，表示记忆永久有效。
        confidence: AI对该记忆准确性的置信度，范围在 0.0 到 1.0 之间。
        priority: 记忆的重要性等级，范围在 1 到 10 之间，用于冲突解决和遗忘机制。
        tags: 用于分类和检索的标签列表。
        relations: 与其他知识点的关联关系列表。
    """

    id: str = Field(default_factory=lambda: f"mem_{uuid.uuid4()}", description="记忆的唯一标识符")
    content: Union[str, Dict[str, Any]] = Field(..., description="记忆内容，可以是文本或结构化数据")
    type: MemoryType = Field(..., description="记忆类型")
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="创建时间 (UTC)"
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc), description="最后更新时间 (UTC)"
    )
    ttl: Optional[int] = Field(None, description="存活时间 (秒)，None表示永久")
    confidence: confloat(ge=0.0, le=1.0) = Field(
        1.0, description="AI对该记忆准确性的置信度 (0.0-1.0)"
    )
    priority: conint(ge=1, le=10) = Field(
        5, description="重要性等级 (1-10)，用于冲突解决和遗忘机制"
    )
    tags: List[str] = Field(default_factory=list, description="标签列表，用于分类和检索")
    relations: List[Relation] = Field(default_factory=list, description="与其他知识的关联")

    model_config = ConfigDict(
        use_enum_values=True,  # 序列化时使用枚举的值
    )


class CoreMemory(BaseMemory):
    """核心记忆模型。

    定义AI的核心身份、价值观和行为准则。这类记忆通常是永久性的，
    并具有最高的优先级，是AI决策和行为的基础。

    Attributes:
        type: 记忆类型，固定为 `MemoryType.CORE`。
        ttl: 存活时间，核心记忆默认为永久有效 (None)。
        priority: 重要性等级，核心记忆具有最高优先级 (8-10)。
    """

    type: Literal[MemoryType.CORE] = Field(MemoryType.CORE, description="记忆类型固定为核心记忆")
    ttl: Optional[int] = Field(None, description="核心记忆默认永久有效")
    priority: conint(ge=8, le=10) = Field(10, description="核心记忆具有最高优先级")


class Knowledge(BaseMemory):
    """知识库模型。

    用于存储可跨会話复用的知识、技能和经验。知识会随着时间推移而更新或遗忘，
    并通过 `knowledge_type` 字段进行细分。

    Attributes:
        type: 记忆类型，固定为 `MemoryType.KNOWLEDGE`。
        knowledge_type: 具体的知识类型，使用 `KnowledgeType` 枚举。
        ttl: 存活时间，知识默认存活90天。
    """

    type: Literal[MemoryType.KNOWLEDGE] = Field(
        MemoryType.KNOWLEDGE, description="记忆类型固定为知识"
    )
    knowledge_type: KnowledgeType = Field(..., description="具体的知识类型")
    ttl: Optional[int] = Field(
        int(timedelta(days=90).total_seconds()), description="知识默认存活90天"
    )


class WorkingMemory(BaseMemory):
    """工作记忆模型。

    存储与当前任务相关的即时工作数据和认知上下文。这类记忆是短暂的，
    通常在任务完成后被清理或提炼为长期知识。

    Attributes:
        type: 记忆类型，固定为 `MemoryType.WORKING`。
        task_id: 关联的任务ID，用于将记忆与特定任务联系起来。
        ttl: 存活时间，工作记忆默认存活24小时。
        priority: 重要性等级，工作记忆优先级较高，但低于核心记忆。
    """

    type: Literal[MemoryType.WORKING] = Field(
        MemoryType.WORKING, description="记忆类型固定为工作记忆"
    )
    task_id: Optional[str] = Field(None, description="关联的任务ID")
    ttl: Optional[int] = Field(
        int(timedelta(hours=24).total_seconds()), description="工作记忆默认存活24小时"
    )
    priority: conint(ge=1, le=7) = Field(7, description="工作记忆优先级较高，但低于核心记忆")
