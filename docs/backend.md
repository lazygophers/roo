# Backend 技术文档

## 项目概述

Roo 配置管理系统的后端基于 **FastAPI** 构建，提供 RESTful API 接口用于管理 AI 模式、命令、规则和角色配置文件。

## 技术栈

### 核心框架
- **FastAPI 0.104+**: 现代、快速的 Python Web 框架
- **Python 3.12+**: 使用最新 Python 版本特性
- **Uvicorn**: ASGI 服务器，生产级性能
- **Pydantic 2.x**: 数据验证和序列化

### 数据存储
- **TinyDB**: 轻量级 JSON 数据库
- **文件系统**: YAML/Markdown 文件管理
- **内存缓存**: 文件内容和元数据缓存

### 开发工具
- **UV**: 现代 Python 包管理工具
- **Rich**: 命令行输出美化
- **PyYAML**: YAML 文件处理
- **Pathlib**: 现代文件路径操作

## 项目结构

```
app/
├── core/                  # 核心业务逻辑
│   ├── __init__.py
│   ├── config.py         # 配置管理
│   └── database_service.py # 数据库服务
├── models/               # 数据模型
│   ├── __init__.py
│   └── schemas.py        # Pydantic 模型
├── routers/              # API 路由
│   ├── __init__.py
│   ├── api_commands.py   # 命令管理
│   ├── api_deploy.py     # 部署管理
│   ├── api_hooks.py      # Hooks 管理
│   ├── api_models.py     # 模式管理
│   ├── api_roles.py      # 角色管理
│   └── api_rules.py      # 规则管理
├── main.py               # FastAPI 应用入口
└── __init__.py
```

## 核心模块详解

### 1. 数据库服务 (database_service.py)

#### 文件扫描和索引
```python
class DatabaseService:
    def scan_yaml_files(self, directory: Path, config_name: str) -> Dict[str, int]:
        """扫描目录下的 YAML 文件并建立索引"""
        stats = {'added': 0, 'updated': 0, 'unchanged': 0}
        
        for file_path in directory.rglob("*.yaml"):
            # 计算文件哈希
            file_hash = self._get_file_hash(file_path)
            
            # 获取文件元数据
            file_stats = file_path.stat()
            file_data = {
                'file_path': str(file_path.relative_to(PROJECT_ROOT)),
                'file_size': file_stats.st_size,
                'last_modified': int(file_stats.st_mtime),  # 整数时间戳
                'file_hash': file_hash,
                'content': content,
                'config_name': config_name
            }
            
            # 增量更新逻辑
            if self._should_update_record(existing_record, file_data):
                table.update(file_data, Query_obj.file_path == file_path)
```

#### 智能更新机制
- **哈希比较**: 通过 MD5 哈希检测文件变化
- **增量更新**: 只更新变化的文件
- **元数据同步**: 自动更新文件大小和修改时间
- **向后兼容**: 自动修复旧格式的时间戳

### 2. 数据模型 (schemas.py)

#### 核心数据模型
```python
from pydantic import BaseModel
from typing import List, Optional, Any

class ModelInfo(BaseModel):
    """AI 模式信息模型"""
    slug: str
    name: str
    role_definition: str
    when_to_use: str
    description: str
    groups: List[Any]
    file_path: str
    file_size: Optional[int] = None
    last_modified: Optional[int] = None  # Unix 时间戳

class FileMetadata(BaseModel):
    """文件元数据模型"""
    file_name: str
    file_path: str
    source_directory: str
    file_size: int
    last_modified: int  # 统一使用整数时间戳

class DeployRequest(BaseModel):
    """部署请求模型"""
    deploy_targets: List[str]
    selected_models: List[str]
    selected_commands: Optional[List[str]] = []
    selected_rules: Optional[List[str]] = []
    selected_role: Optional[str] = None
```

### 3. API 路由设计

#### RESTful 设计原则
- **统一接口**: 所有接口使用 POST 方法简化前端调用
- **标准响应**: 统一的响应格式和错误处理
- **类型安全**: Pydantic 模型确保请求/响应类型安全

#### 路由组织
```python
# 模式管理 - api_models.py
@router.post("/models", response_model=ModelsResponse)
@router.post("/models/by-slug", response_model=ModelInfo)

# 部署管理 - api_deploy.py  
@router.post("/deploy/targets", response_model=DeployTargetsResponse)
@router.post("/deploy", response_model=DeployResponse)
@router.post("/cleanup", response_model=CleanupResponse)

# 规则管理 - api_rules.py
@router.post("/rules", response_model=RulesResponse)
@router.post("/rules/by-slug", response_model=RulesResponse)
```

### 4. 部署系统 (api_deploy.py)

#### 多目标部署支持
```python
# 部署目标配置
DEPLOY_CONFIGS = {
    "roo": {
        "name": "Roo Code",
        "path": "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/"
    },
    "roo-nightly": {
        "name": "Roo Code Nightly", 
        "path": "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-code-nightly/"
    },
    "kilo": {
        "name": "Kilo Code",
        "path": "~/Library/Application Support/Code/User/globalStorage/kilocode.kilo-code/"
    }
}

# 命令和规则部署路径
COMMAND_DEPLOY_PATHS = {
    "roo": "~/.roo/commands",
    "roo-nightly": "~/.roo/commands", 
    "kilo": "~/.kilocode/commands"
}

RULES_DEPLOY_PATHS = {
    "roo": "~/.roo/rules",
    "roo-nightly": "~/.roo/rules",
    "kilo": "~/.kilocode/rules"
}
```

#### 部署流程
1. **目标检测**: 检查部署目标目录是否存在
2. **配置生成**: 动态生成 `custom_models.yaml`
3. **文件复制**: 复制选中的命令和规则文件
4. **角色部署**: 将角色文件部署为 `role.md`
5. **错误处理**: 记录部署错误和警告
6. **结果返回**: 返回部署结果和文件列表

### 5. 文件管理系统

#### 递归文件搜索
```python
def find_models_recursively(models_dir: Path) -> List[Path]:
    """递归查找模型文件，支持子目录"""
    # 使用 rglob 进行递归搜索
    model_files = list(models_dir.rglob("*.yaml"))
    return sorted(model_files)
```

#### YAML 文件处理
```python
def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """安全加载 YAML 文件"""
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file) or {}
    except Exception as e:
        logger.error(f"Failed to load YAML file {file_path}: {e}")
        return {}
```

#### 文件系统抽象
- **跨平台路径**: 使用 `pathlib.Path` 处理路径
- **用户目录展开**: 支持 `~` 符号自动展开
- **权限检查**: 部署前检查目录权限
- **原子操作**: 确保文件操作的原子性

## 性能优化

### 1. 数据库优化
- **增量扫描**: 只更新变化的文件
- **哈希缓存**: 避免重复计算文件哈希
- **批量操作**: 批量更新数据库记录
- **索引优化**: 基于文件路径的快速查询

### 2. 内存管理
- **惰性加载**: 按需加载文件内容
- **缓存策略**: 智能缓存热点数据
- **对象池**: 复用文件处理对象
- **垃圾回收**: 及时释放不用的资源

### 3. I/O 优化  
- **异步文件操作**: 非阻塞文件读写
- **并发扫描**: 并行扫描多个目录
- **流式处理**: 大文件流式读取
- **压缩传输**: API 响应压缩

## 错误处理和日志

### 1. 异常处理层级
```python
# 全局异常处理
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"success": False, "message": "Internal server error"}
    )

# 业务异常
class ConfigurationError(Exception):
    """配置相关错误"""
    pass

class DeploymentError(Exception):  
    """部署相关错误"""
    pass
```

### 2. 结构化日志
```python
import logging
from rich.logging import RichHandler

# 配置 Rich 日志处理器
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)]
)

logger = logging.getLogger(__name__)

# 使用示例
logger.info(f"Successfully deployed to {target_config['name']}")
logger.error(f"Deployment failed: {str(e)}")
logger.debug(f"File hash: {file_hash}")
```

### 3. 监控和指标
- **API 调用统计**: 记录 API 调用次数和耗时
- **文件操作监控**: 监控文件读写性能
- **错误率统计**: 跟踪错误发生频率
- **资源使用**: 监控 CPU 和内存使用

## 安全考虑

### 1. 输入验证
- **Pydantic 验证**: 自动验证所有输入参数
- **路径安全**: 防止路径遍历攻击
- **文件类型检查**: 只允许处理特定类型文件
- **大小限制**: 限制上传文件大小

### 2. 权限控制
- **文件权限**: 检查文件读写权限
- **目录访问**: 限制目录访问范围
- **用户隔离**: 每个用户独立的配置空间

### 3. 数据保护
- **敏感信息**: 避免记录敏感信息到日志
- **文件加密**: 重要配置文件加密存储
- **备份恢复**: 定期备份和恢复机制

## 开发和测试

### 1. 开发环境设置
```bash
# 使用 UV 管理依赖
uv sync                    # 安装依赖
uv run uvicorn app.main:app --reload  # 开发服务器
uv run pytest tests/ -v   # 运行测试
```

### 2. 测试策略
- **单元测试**: pytest + pytest-asyncio
- **集成测试**: 端到端 API 测试
- **性能测试**: 负载和压力测试
- **覆盖率**: pytest-cov 生成覆盖率报告

### 3. 代码质量
- **类型检查**: mypy 静态类型检查
- **代码格式**: black + isort 自动格式化
- **代码分析**: flake8 + pylint 静态分析

## 部署和运维

### 1. 生产部署
```bash
# Docker 容器化
FROM python:3.12-slim
COPY . /app
WORKDIR /app
RUN uv sync --frozen
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# 直接部署  
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

### 2. 配置管理
```python
# config.py
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent
DATABASE_PATH = PROJECT_ROOT / "config_database.json"
RESOURCES_DIR = PROJECT_ROOT / "resources"

# 环境变量配置
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
DEBUG_MODE = os.getenv("DEBUG", "false").lower() == "true"
```

### 3. 监控和维护
- **健康检查**: `/health` 端点监控服务状态
- **指标收集**: Prometheus 指标导出
- **日志聚合**: ELK Stack 日志分析
- **告警系统**: 异常情况自动告警

## API 设计原则

### 1. RESTful 风格
- **资源导向**: 每个端点代表特定资源
- **HTTP 动词**: 使用 POST 简化前端处理
- **状态码**: 标准 HTTP 状态码
- **版本控制**: API 版本管理策略

### 2. 响应格式标准化
```python
class StandardResponse(BaseModel):
    """标准 API 响应格式"""
    success: bool
    message: str
    data: Optional[Any] = None
    total: Optional[int] = None
    errors: Optional[List[str]] = None
```

### 3. 分页和过滤
```python
class PaginationRequest(BaseModel):
    """分页请求参数"""
    page: int = 1
    page_size: int = 50
    category: Optional[str] = None
    search: Optional[str] = None
```

## 未来规划

### 1. 功能扩展
- [ ] GraphQL API 支持
- [ ] 实时推送更新
- [ ] 配置版本管理
- [ ] 多租户支持

### 2. 性能优化
- [ ] Redis 缓存层
- [ ] 数据库分片
- [ ] CDN 静态资源
- [ ] 连接池优化

### 3. 可观测性
- [ ] 分布式链路追踪
- [ ] 业务指标监控
- [ ] 自动化告警
- [ ] 性能分析

## 贡献指南

### 开发流程
1. Fork 项目仓库
2. 创建功能分支
3. 编写代码和测试
4. 运行质量检查
5. 提交 Pull Request

### 代码标准
- 遵循 PEP 8 风格
- 编写完整的类型注解
- 添加单元测试
- 更新相关文档