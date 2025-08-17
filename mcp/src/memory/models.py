# -*- coding: utf-8 -*-
"""
@Time    : 2025/8/17 10:50
@Author  : roo
@File    : models.py
@Software: PyCharm
@Desc    : 记忆库核心数据模型
"""

import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, ConfigDict, Field, conint, confloat


class MemoryType(str, Enum):
    """
    记忆类型枚举
    - CORE: 核心记忆，定义AI身份与边界
    - KNOWLEDGE: 知识库，跨会话学习积累
    - WORKING: 工作记忆，当前任务上下文
    """

    CORE = "CORE"
    KNOWLEDGE = "KNOWLEDGE"
    WORKING = "WORKING"


class KnowledgeType(str, Enum):
    """
    知识类型枚举
    - SOLUTION: 经过验证的问题解决方案
    - PATTERN: 可复用的架构和设计模式
    - FACT: 确定的技术事实和规范
    - SKILL: 具体的操作技能和方法
    - EXPERIENCE: 从实践中提炼的经验
    - PRINCIPLE: 特定领域的指导原则
    """

    SOLUTION = "solution"
    PATTERN = "pattern"
    FACT = "fact"
    SKILL = "skill"
    EXPERIENCE = "experience"
    PRINCIPLE = "principle"


class Relation(BaseModel):
    """
    知识关联模型
    """

    target_id: str = Field(..., description="关联的目标知识ID")
    type: str = Field(..., description="关联类型 (e.g., 'extends', 'conflicts_with')")


class BaseMemory(BaseModel):
    """
    基础记忆模型，包含所有记忆类型的通用字段
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
    """
    核心记忆模型
    - 定义AI的核心身份、价值观和行为准则
    - 通常是永久性的
    """

    type: Literal[MemoryType.CORE] = Field(
        MemoryType.CORE, description="记忆类型固定为核心记忆"
    )
    ttl: Optional[int] = Field(None, description="核心记忆默认永久有效")
    priority: conint(ge=8, le=10) = Field(10, description="核心记忆具有最高优先级")


class Knowledge(BaseMemory):
    """
    知识库模型
    - 存储可跨会话复用的知识、技能和经验
    - 具有默认的TTL，并可通过学习更新
    """

    type: Literal[MemoryType.KNOWLEDGE] = Field(
        MemoryType.KNOWLEDGE, description="记忆类型固定为知识"
    )
    knowledge_type: KnowledgeType = Field(..., description="具体的知识类型")
    ttl: Optional[int] = Field(
        int(timedelta(days=90).total_seconds()), description="知识默认存活90天"
    )


class WorkingMemory(BaseMemory):
    """
    工作记忆模型
    - 存储当前任务的即时工作数据和认知上下文
    - TTL较短，任务完成后通常会被清理或提炼
    """

    type: Literal[MemoryType.WORKING] = Field(
        MemoryType.WORKING, description="记忆类型固定为工作记忆"
    )
    task_id: Optional[str] = Field(None, description="关联的任务ID")
    ttl: Optional[int] = Field(
        int(timedelta(hours=24).total_seconds()), description="工作记忆默认存活24小时"
    )
    priority: conint(ge=1, le=7) = Field(7, description="工作记忆优先级较高，但低于核心记忆")
