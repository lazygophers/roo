"""
MCP工具模型定义
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class MCPTool:
    """MCP工具模型"""
    name: str
    description: str
    category: str
    schema: Dict[str, Any]
    metadata: Dict[str, Any]
    enabled: bool
    returns: Optional[Dict[str, Any]] = None
    implementation_type: str = "builtin"

    # Database fields (optional for initial creation)
    id: Optional[int] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        result = {
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "schema": self.schema,
            "metadata": self.metadata,
            "enabled": self.enabled,
            "implementation_type": self.implementation_type
        }

        # Include returns schema if present
        if self.returns is not None:
            result["returns"] = self.returns

        # Include database fields if present
        if self.id is not None:
            result["id"] = self.id
        if self.created_at is not None:
            result["created_at"] = self.created_at
        if self.updated_at is not None:
            result["updated_at"] = self.updated_at

        return result