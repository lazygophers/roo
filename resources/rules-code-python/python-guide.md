---
name: python-guide
title: Python编程规范指南
description: "Python开发规范和最佳实践"
category: 语言指南
language: python
priority: high
tags: [Python, uv, pydantic, 类型注解]
---

# Python 编程规范

## 🔧 工具栈
- **包管理**: `uv` (优先使用)
- **类型验证**: `pydantic` 
- **测试**: `pytest`

## 📝 命名规范
| 类型 | 规范 | 示例 |
|------|------|------|
| 变量/函数 | 蛇形 | `user_name`, `get_data` |
| 类/异常 | 帕斯卡 | `UserModel`, `ApiError` |
| 常量 | 大写+下划线 | `MAX_SIZE`, `API_URL` |

## 🏷️ 类型注解要求
- **必须**: 函数参数和返回值明确注解
- **Field描述**: 使用`pydantic.Field`添加描述和约束

```python
from pydantic import BaseModel, Field

class User(BaseModel):
    name: str = Field(description="姓名", min_length=2)
    age: int = Field(description="年龄", ge=0, le=150)

async def search_api(
    query: str = Field(description="搜索关键词"),
    limit: int = Field(description="结果限制", default=10, ge=1, le=100)
) -> list[dict]:
    """API搜索接口"""
    pass
```

## 🧪 测试规范
- **框架**: pytest
- **文件命名**: `test_*.py`

```python
import pytest
from pydantic import ValidationError

def test_user_validation():
    user = User(name="张三", age=25)
    assert user.name == "张三"
    
def test_invalid_user():
    with pytest.raises(ValidationError):
        User(name="A", age=-1)
```

## ⚠️ 异常处理
```python
try:
    result = api_call()
except ApiError as e:
    logger.error(f"API失败: {e}")
    raise
```

## ✅ 代码检查要点
- 函数参数有类型注解和Field描述
- pydantic模型包含约束条件  
- 使用uv管理依赖
- 编写对应测试
