# 开发指南

本文档为开发者提供 MCP 服务器的开发指南，包括环境搭建、代码规范、测试指南等内容。

## 📋 目录

- [开发环境搭建](#开发环境搭建)
- [项目结构](#项目结构)
- [代码规范](#代码规范)
- [开发流程](#开发流程)
- [测试指南](#测试指南)
- [调试技巧](#调试技巧)
- [性能优化](#性能优化)
- [贡献指南](#贡献指南)

## 开发环境搭建

### 1. 前置要求

- Python 3.9+
- uv 包管理器
- Git
- Docker（可选）

### 2. 环境初始化

```bash
# 克隆项目
git clone https://github.com/lazygophers/roo.git
cd roo/mcp

# 安装依赖
uv sync

# 安装开发依赖
uv sync --group dev

# 创建 .env 文件
cp .env.example .env
```

### 3. 开发工具配置

#### VS Code 配置

创建 `.vscode/settings.json`：

```json
{
  "python.defaultInterpreterPath": ".venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "editor.codeActionsOnSave": {
    "source.organizeImports": true
  },
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests"]
}
```

#### Git Hooks 配置

```bash
# 安装 pre-commit
uv run pre-commit install

# 运行 pre-commit 检查
uv run pre-commit run --all-files
```

## 项目结构

```
.
├── src/                    # 源代码目录
│   ├── __init__.py
│   ├── server.py       # 服务器核心
│   ├── transport/      # 传输层实现
│   │   ├── __init__.py
│   │   ├── stdio.py
│   │   ├── sse.py
│   │   └── http_stream.py
│   ├── storage/        # 存储层实现
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── lancedb.py
│   │   ├── duckdb.py
│   │   └── tinydb.py
│   ├── tools/          # 工具实现
│   │   ├── __init__.py
│   │   ├── base.py
│   │   └── builtin_tools.py
│   ├── config/         # 配置管理
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── schema.py
│   └── utils/          # 工具函数
│   │   ├── __init__.py
│   │   ├── logger.py
│   │   └── helpers.py
│   └── tools/              # MCP 工具实现
├── tests/                  # 测试文件
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_server.py
│   ├── test_transport/
│   ├── test_storage/
│   └── test_tools/
├── docs/                   # 文档
│   ├── api.md
│   ├── deployment.md
│   └── development.md
├── main.py                 # 主入口文件
├── config.yaml            # 配置文件示例
├── pyproject.toml         # 项目配置
├── .pre-commit-config.yaml
├── .gitignore
├── Dockerfile
├── Makefile
└── README.md
```

## 代码规范

### 1. Python 代码风格

遵循 PEP 8 规范，使用以下工具确保代码质量：

```bash
# 代码格式化
uv run black src/ tests/

# 导入排序
uv run isort src/ tests/

# 代码检查
uv run ruff check src/ tests/

# 类型检查
uv run mypy src/
```

### 2. 命名规范

- **类名**: 使用 PascalCase（如 `McpServer`）
- **函数名**: 使用 snake_case（如 `create_tool`）
- **变量名**: 使用 snake_case（如 `config_path`）
- **常量**: 使用大写 SNAKE_CASE（如 `MAX_CONNECTIONS`）
- **模块名**: 使用小写（如 `transport_layer`）

### 3. 注释规范

- **函数注释**：使用英文，遵循 Google 风格
- **类注释**：使用英文，描述类的用途
- **行内注释**：使用中文，解释复杂逻辑
- **TODO/FIXME**：使用中文，说明待办事项

示例：

```python
class McpServer:
    """MCP server implementation supporting multiple transport protocols."""

    def __init__(self, config: Config):
        """Initialize the MCP server.

        Args:
            config: Server configuration instance
        """
        self.config = config
        self.tools = {}  # 工具注册表

    def register_tool(self, tool: BaseTool) -> None:
        """Register a new tool.

        Args:
            tool: Tool instance to register

        Raises:
            ToolError: If tool name already exists
        """
        if tool.name in self.tools:
            raise ToolError(f"Tool {tool.name} already registered")
        self.tools[tool.name] = tool
```

### 4. 错误处理

使用自定义异常类：

```python
class McpError(Exception):
    """Base MCP exception."""
    pass

class ConfigError(McpError):
    """Configuration related errors."""
    pass

class ToolError(McpError):
    """Tool execution errors."""
    pass
```

## 开发流程

### 1. 分支管理

```bash
# 创建功能分支
git checkout -b feature/your-feature-name

# 开发完成后提交
git add .
git commit -m "feat: add new tool support"

# 推送到远程
git push origin feature/your-feature-name

# 创建 Pull Request
```

### 2. 提交信息规范

使用 Conventional Commits 格式：

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

类型：

- `feat`: 新功能
- `fix`: 修复
- `docs`: 文档更新
- `style`: 代码格式
- `refactor`: 重构
- `test`: 测试
- `chore`: 构建或辅助工具变动

示例：

```bash
git commit -m "feat(tools): add file system tool"
git commit -m "fix(transport): handle connection timeout"
git commit -m "docs: update API documentation"
```

### 3. 代码审查清单

提交 PR 前检查：

- [ ] 代码符合项目规范
- [ ] 所有测试通过
- [ ] 新功能有对应测试
- [ ] 文档已更新
- [ ] 提交信息规范
- [ ] 代码已格式化
- [ ] 类型检查通过

## 测试指南

### 1. 测试结构

```
tests/
├── unit/              # 单元测试
│   ├── test_server.py
│   ├── test_config.py
│   └── test_tools.py
├── integration/       # 集成测试
│   ├── test_transport.py
│   └── test_storage.py
├── e2e/              # 端到端测试
│   └── test_full_flow.py
└── fixtures/         # 测试数据
    ├── config.yaml
    └── test_data.json
```

### 2. 编写测试

使用 pytest：

```python
import pytest
from mcp_server.server import McpServer
from mcp_server.config import Config


@pytest.fixture
def server_config():
    """Create test server configuration."""
    return Config({
        "transport": {
            "type": "stdio"
        },
        "storage": {
            "type": "tinydb",
            "path": ":memory:"
        }
    })


@pytest.fixture
def mcp_server(server_config):
    """Create MCP server instance."""
    return McpServer(server_config)


def test_server_initialization(mcp_server):
    """Test server initialization."""
    assert mcp_server.config is not None
    assert mcp_server.tools == {}


@pytest.mark.asyncio
async def test_tool_registration(mcp_server):
    """Test tool registration."""
    tool = MockTool()
    mcp_server.register_tool(tool)

    assert tool.name in mcp_server.tools
    assert mcp_server.tools[tool.name] is tool
```

### 3. 测试覆盖率

确保测试覆盖率至少 90%：

```bash
# 运行测试并生成覆盖率报告
uv run pytest --cov=src/mcp_server --cov-report=html --cov-report=term-missing

# 查看覆盖率报告
open htmlcov/index.html
```

### 4. Mock 和 Fixture

使用 pytest-mock：

```python
def test_with_mock(mocker):
    """Test with mock object."""
    mock_storage = mocker.Mock()
    mock_storage.save.return_value = True

    result = some_function(mock_storage)
    assert result is True
    mock_storage.save.assert_called_once()
```

## 调试技巧

### 1. 日志配置

开发时启用调试日志：

```python
import logging

# 配置日志
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
# stdio 模式默认不输出日志，其他模式默认输出到控制台

# 或使用环境变量
export MCP_LOG_LEVEL=DEBUG
```

### 2. VS Code 调试配置

创建 `.vscode/launch.json`：

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: MCP Server",
      "type": "python",
      "request": "launch",
      "program": "src/mcp_server/main.py",
      "console": "integratedTerminal",
      "args": ["--config", "config.yaml", "--transport", "stdio"],
      "env": {
        "MCP_LOG_LEVEL": "DEBUG"
      }
    }
  ]
}
```

### 3. 常用调试命令

```bash
# 启动调试模式
uv run python -m pdb main.py

# 使用 ipdb（需要安装）
uv run python -m ipdb main.py

# 内存分析
uv run python -m memory_profiler main.py
```

## 性能优化

### 1. 性能分析工具

```bash
# 使用 cProfile
uv run python -m cProfile -s tottime main.py

# 使用 snakeviz 可视化
uv run snakeviz profile_output

# 使用 line_profiler
uv run kernprof -l -v main.py
```

### 2. 异步优化

```python
import asyncio
from typing import List


async def process_tools_concurrently(tools: List[Tool]) -> List[Result]:
    """Process tools concurrently for better performance."""
    tasks = [tool.execute() for tool in tools]
    return await asyncio.gather(*tasks, return_exceptions=True)
```

### 3. 缓存策略

```python
from functools import lru_cache
from datetime import timedelta


@lru_cache(maxsize=1000)
def get_cached_data(key: str) -> Data:
    """Get cached data with LRU eviction."""
    return load_data(key)


# 或使用 TTL 缓存
from cachetools import TTLCache

cache = TTLCache(maxsize=1000, ttl=timedelta(minutes=5).total_seconds())
```

## 贡献指南

### 1. 报告问题

使用 GitHub Issues 报告问题：

1. 使用搜索检查是否已存在相同问题
2. 使用问题模板提供详细信息
3. 包含复现步骤和期望结果
4. 附上相关日志和错误信息

### 2. 提交 PR

1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 更新文档
5. 提交 PR 并描述变更

### 3. 代码审查

- 及时响应审查意见
- 保持讨论专业和建设性
- 感谢审查者的贡献

### 4. 文档贡献

文档同样重要，欢迎：

- 修复拼写错误
- 改进文档清晰度
- 添加缺失的文档
- 翻译文档到其他语言

## 扩展开发

### 1. 开发自定义工具

```python
from mcp_server.tools.base import BaseTool, ToolResult
from typing import Dict, Any


class CustomTool(BaseTool):
    """Custom tool implementation."""

    name = "custom_tool"
    description = "A custom tool for demonstration"

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def execute(self, args: Dict[str, Any]) -> ToolResult:
        """Execute the tool."""
        try:
            # 工具逻辑
            result = await self._do_work(args)
            return ToolResult(
                success=True,
                data=result
            )
        except Exception as e:
            return ToolResult(
                success=False,
                error=str(e)
            )

    async def _do_work(self, args: Dict[str, Any]) -> Any:
        """Actual work implementation."""
        # 实现具体逻辑
        return {"status": "completed"}
```

### 2. 开发自定义存储后端

```python
from mcp_server.storage.base import BaseStorage
from typing import Any, List


class CustomStorage(BaseStorage):
    """Custom storage backend."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self._initialize()

    def _initialize(self):
        """Initialize storage."""
        pass

    async def save(self, key: str, value: Any) -> bool:
        """Save data to storage."""
        # 实现保存逻辑
        return True

    async def load(self, key: str) -> Any:
        """Load data from storage."""
        # 实现加载逻辑
        return None

    async def delete(self, key: str) -> bool:
        """Delete data from storage."""
        # 实现删除逻辑
        return True

    async def query(self, query: Dict[str, Any]) -> List[Any]:
        """Query data from storage."""
        # 实现查询逻辑
        return []
```

### 3. 开发自定义传输协议

```python
from mcp_server.transport.base import BaseTransport
from typing import AsyncIterator


class CustomTransport(BaseTransport):
    """Custom transport implementation."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config

    async def start(self) -> None:
        """Start the transport."""
        pass

    async def stop(self) -> None:
        """Stop the transport."""
        pass

    async def send(self, data: bytes) -> None:
        """Send data."""
        pass

    async def receive(self) -> AsyncIterator[bytes]:
        """Receive data."""
        while True:
            yield b"data"
```

## 常见问题

### 1. 环境问题

**Q: uv 安装失败怎么办？**

A: 可以使用 pip 安装 uv：

```bash
pip install uv
```

**Q: 依赖冲突如何解决？**

A: 使用 uv 的依赖解析功能：

```bash
uv pip compile requirements.in
```

### 2. 开发问题

**Q: 如何添加新的传输协议？**

A: 继承 `BaseTransport` 类并实现必要方法，参考现有实现。

**Q: 如何调试异步代码？**

A: 使用 asyncio 的调试模式：

```bash
PYTHONASYNCIODEBUG=1 uv run python your_script.py
```

### 3. 测试问题

**Q: 测试数据库如何设置？**

A: 使用 pytest fixtures 创建测试数据库：

```python
@pytest.fixture
def test_db():
    """Create test database."""
    db = TinyDB(":memory:")
    yield db
    db.close()
```

## 资源链接

- [MCP 规范文档](https://modelcontextprotocol.io/)
- [Python 异步编程指南](https://docs.python.org/3/library/asyncio.html)
- [pytest 文档](https://docs.pytest.org/)
- [uv 文档](https://docs.astral.sh/uv/)
