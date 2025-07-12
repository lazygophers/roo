# Python编程规范技术文档

## 编码规范

### 命名规范

| 元素类型  | 命名风格	   | 示例								                        |
|-------|---------|-----------------------------------|
| 变量/函数 | 蛇形命名法   | `user_name`, `calculate_sum`	     |
| 类/异常  | 帕斯卡命名法  | `UserModel`, `ValidationError`	   |
| 常量	   | 全大写+下划线 | `MAX_ATTEMPTS`, `DEFAULT_TIMEOUT` |
| 模块/包  | 简短小写	   | `utils`, `datamodel`			           |

### 代码格式

- **缩进**：使用4个空格，禁用Tab
- **行长度**：每行不超过80个字符，文档字符串不超过72个字符
- **空行**：函数/类定义间用2个空行分隔，类方法间用1个空行分隔
- **括号**：避免冗余括号，仅在必要时使用

## 虚拟环境与包管理uv工具

### 安装uv

`curl https://docs.astral.sh/uv/install.sh | bash`

### 常用命令

| 功能	    | 命令							                    | 说明						             |
|--------|------------------------------|----------------------|
| 创建虚拟环境 | `uv init`			                 | 在指定目录创建虚拟环境（默认当前目录）	 |
| 激活虚拟环境 | `uv venv activate`		         | 激活指定虚拟环境				         |
| 安装依赖   | `uv add <package>[@version]` | 安装包及指定版本				         |
| 移除依赖   | `uv remove <package>`		      | 移除指定包					           |
| 更新依赖   | `uv update <package>`		      | 更新指定包至最新版				        |

## 类型注解规范

### 基础类型注解

函数参数和返回值必须明确标注类型：

```python
from typing import List, Dict
from pydantic import Field


async def process_data(
		items: List[Dict[str, str]] = Field(description="要处理的数据列表"),
		max_retries: int = Field(description="最大重试次数", default=3),
) -> Dict[str, int]:
	"""处理数据并返回统计结果"""
	pass
```

### pydantic模型

使用pydantic定义复杂数据结构：

```python
from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
	name: str = Field(description="用户姓名", min_length=2)
	email: EmailStr = Field(description="用户邮箱")
	age: int = Field(description="用户年龄", ge=0, le=150)
```

## 函数参数与返回值规范

### 参数规范

所有函数参数必须包含：

- 类型注解
- 使用Field的description说明
- 必要时添加约束条件（如默认值、范围限制）

```python
from pydantic import Field


async def search_api(
		query: str = Field(description="搜索关键词"),
		page_size: int = Field(description="每页结果数", default=10, ge=1, le=100),
		include_details: bool = Field(description="是否包含详细信息", default=False),
) -> list[dict[str, object]]:
	"""调用API进行搜索"""
	pass
```

### 返回值规范

- 使用类型注解明确返回值结构
- 在docstring中详细说明返回值格式

```python
from pydantic import Field


async def get_user_profile(
		user_id: str = Field(description="用户ID")
) -> dict[str, set[str, int, list[str]]]:
	"""获取用户个人资料

	Returns:
		Dict with the following keys:
		{
			"id": 用户ID,
			"name": 用户姓名,
			"age": 用户年龄,
			"roles": 用户角色列表
		}
	"""
	pass
```

## pydantic最佳实践

### 模型定义

```python
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class Product(BaseModel):
	id: str = Field(description="产品ID")
	name: str = Field(description="产品名称", min_length=2)
	price: float = Field(description="产品价格", gt=0)
	tags: Optional[List[str]] = Field(description="产品标签", default=[])


@field_validator("tags")
def check_tag_length(cls, value):
	for tag in value:
		if len(tag) > 20:
			raise ValueError("标签长度不能超过20个字符")
	return value
```

### 数据验证

```python
from pydantic import ValidationError

try:
	product = Product(id="P001", name="手机", price=999.99, tags=["电子", "通讯"])
except ValidationError as e:
	print(e.json())
```

## 注释规范

### 文档字符串（Docstrings）

使用Google风格的docstring：

```python
from typing import List

from pydantic import Field


async def calculate_statistics(
		data: List[float] = Field(description="要计算的数据集"),
		method: str = Field(description="计算方法", default="mean", enum=["mean", "median", "std"]),
) -> float:
	"""计算数据集的统计量
	
	Args:
		data: 包含数值的列表
		method: 计算方法，可选值为'mean'(均值)、'median'(中位数)、'std'(标准差)
	
	Returns:
		计算得到的统计值
	
	Raises:
		ValueError: 当数据集为空或方法无效时
	"""
	if not data:
		raise ValueError("数据集不能为空")
# 计算逻辑...
```

## 异常处理规范

- **避免空except块**：

```python
try:
	result = api_call()
except APIError as e:
	print(f"API调用失败: {e}")
	raise
```

- **自定义异常**：
  class InvalidParameterError(Exception):
  """参数无效异常"""

## 测试规范

- 使用`pytest`框架编写单元测试
- 测试文件命名：`test_<module>.py`

```python
import pytest
from pydantic import ValidationError


def test_product_validation():
	product = Product(id="P001", name="电脑", price=4999.0)
	assert product.name == "电脑"
	assert product.price > 0


def test_invalid_product():
	with pytest.raises(ValidationError):
		Product(id="P002", name="A", price=-100)
```

## 代码审查指南

- 检查所有函数参数是否有明确的类型和描述
- 验证pydantic模型是否包含必要的约束条件
- 确保docstring完整且准确
- 检查uv依赖管理是否规范