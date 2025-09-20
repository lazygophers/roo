# LazyAI Studio Configuration Management API 文档

## 概述

本文档描述了 LazyAI Studio 配置管理系统的 RESTful API 接口，用于管理 AI 模式、命令、规则和角色的配置，以及 MCP (Model Context Protocol) 工具集成。

## 基础信息

- **Base URL**: `http://localhost:8000`
- **API Version**: v1
- **Content-Type**: `application/json`
- **请求方法**: 主要使用 `POST` 方法

## 认证

目前 API 不需要认证，在本地环境中直接访问。

## 通用响应格式

### 成功响应
```json
{
  "success": true,
  "message": "操作成功",
  "data": {...},
  "total": 10
}
```

### 错误响应
```json
{
  "success": false,
  "message": "错误描述",
  "error_code": "ERROR_CODE"
}
```

## API 接口

### 1. 模式 (Models) 管理

#### 获取模式列表
```http
POST /api/models
Content-Type: application/json

{
  "category": "core",      // 可选: core, coder
  "page": 1,              // 可选: 页码，默认 1
  "page_size": 50         // 可选: 每页大小，默认 50
}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "slug": "orchestrator",
      "name": "🧠 Brain",
      "role_definition": "作为系统级任务调度中心...",
      "when_to_use": "当面对复杂任务需要进行系统性分解...",
      "description": "智能任务调度中心",
      "groups": ["read", "command", "mcp"],
      "file_path": "resources/models/brain.yaml",
      "file_size": 2048,
      "last_modified": 1704067200
    }
  ],
  "total": 15
}
```

#### 按 Slug 获取模式
```http
POST /api/models/by-slug
Content-Type: application/json

{
  "slug": "orchestrator"
}
```

### 2. 命令 (Commands) 管理

#### 获取命令列表
```http
POST /api/commands
Content-Type: application/json

{}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "file_name": "git-commit.sh",
      "file_path": "resources/commands/git-commit.sh",
      "source_directory": "resources/commands",
      "file_size": 512,
      "last_modified": 1704067200
    }
  ],
  "total": 8
}
```

### 3. 规则 (Rules) 管理

#### 获取规则列表
```http
POST /api/rules
Content-Type: application/json

{}
```

#### 按 Slug 获取规则
```http
POST /api/rules/by-slug
Content-Type: application/json

{
  "slug": "rules"  // 注意: 不需要拼接 rules- 前缀
}
```

### 4. 角色 (Roles) 管理

#### 获取角色列表
```http
POST /api/roles
Content-Type: application/json

{}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "name": "bunny_maid",
      "title": "🐰 兔娘女仆小兔",
      "description": "可爱的兔娘女仆，陪伴您的编程时光",
      "features": ["温柔体贴", "专业编程", "可爱互动"],
      "restrictions": ["保持礼貌", "专注技术"],
      "file_path": "resources/roles/bunny_maid.md",
      "file_size": 1024,
      "last_modified": 1704067200
    }
  ],
  "total": 2
}
```

### 5. 部署管理

#### 获取部署目标
```http
POST /api/deploy/targets
Content-Type: application/json

{}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "key": "roo",
      "name": "Roo Code",
      "path": "~/Library/Application Support/Code/User/globalStorage/rooveterinaryinc.roo-cline/",
      "available": true
    }
  ]
}
```

#### 部署配置
```http
POST /api/deploy
Content-Type: application/json

{
  "deploy_targets": ["roo", "kilo"],
  "selected_models": ["orchestrator", "code"],
  "selected_commands": ["git-commit.sh"],
  "selected_rules": ["core-rules.md"],
  "selected_role": "bunny_maid"
}
```

**响应示例**:
```json
{
  "success": true,
  "message": "部署完成",
  "deployed_files": [
    "/Users/user/.roo/custom_models.yaml",
    "/Users/user/.roo/commands/git-commit.sh",
    "/Users/user/.roo/rules/role.md"
  ],
  "errors": []
}
```

#### 清理配置
```http
POST /api/cleanup
Content-Type: application/json

{
  "targets": ["roo"]
}
```

### 6. 文件内容获取

#### 获取文件内容
```http
POST /api/file-content
Content-Type: application/json

{
  "file_path": "resources/models/brain.yaml"
}
```

### 7. Hooks 管理

#### 获取 Before Hook
```http
POST /api/hooks/before
Content-Type: application/json

{}
```

#### 获取 After Hook
```http
POST /api/hooks/after
Content-Type: application/json

{}
```

## 数据类型

### FileMetadata
```typescript
interface FileMetadata {
  file_name: string;
  file_path: string;
  source_directory: string;
  file_size: number;
  last_modified: number;  // Unix timestamp (seconds)
}
```

### ModelInfo
```typescript
interface ModelInfo {
  slug: string;
  name: string;
  role_definition: string;
  when_to_use: string;
  description: string;
  groups: any[];
  file_path: string;
  file_size?: number;
  last_modified?: number;  // Unix timestamp (seconds)
}
```

### RoleInfo
```typescript
interface RoleInfo {
  name: string;
  title: string;
  description: string;
  features: string[];
  restrictions?: string[];
  file_path: string;
  file_size: number;
  last_modified: number;  // Unix timestamp (seconds)
}
```

## 错误代码

| 错误代码 | 描述 |
|---------|-----|
| `MODEL_NOT_FOUND` | 指定的模式不存在 |
| `FILE_NOT_FOUND` | 文件不存在 |
| `DEPLOY_FAILED` | 部署失败 |
| `INVALID_TARGET` | 无效的部署目标 |
| `PERMISSION_DENIED` | 权限不足 |

## 注意事项

1. **时间戳格式**: 所有时间戳均为 Unix 时间戳(秒级整数)
2. **文件路径**: 使用相对于项目根目录的路径
3. **规则 Slug**: 调用 `/api/rules/by-slug` 时，slug 参数不需要拼接 `rules-` 前缀
4. **部署路径**: 支持 `~` 符号表示用户主目录
5. **错误处理**: 所有接口都包含详细的错误信息

## 示例代码

### JavaScript/TypeScript
```typescript
// 获取模式列表
const response = await fetch('/api/models', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    category: 'core',
    page: 1,
    page_size: 20
  })
});

const data = await response.json();
console.log(data);
```

### Python
```python
import requests

# 部署配置
response = requests.post('/api/deploy', json={
    'deploy_targets': ['roo'],
    'selected_models': ['orchestrator'],
    'selected_role': 'bunny_maid'
})

result = response.json()
print(result)
```

### 8. MCP 工具管理

#### 获取 MCP 工具列表
```http
POST /api/mcp-tools
Content-Type: application/json

{}
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "name": "github",
      "description": "GitHub API integration tools for repository management, issues, PRs, and releases",
      "version": "1.0.0",
      "tools_count": 34,
      "status": "active",
      "categories": ["repository", "issues", "pull_requests", "releases"]
    },
    {
      "name": "fetch",
      "description": "Web scraping and content extraction tools",
      "version": "1.0.0",
      "tools_count": 5,
      "status": "active",
      "categories": ["web_scraping", "content_extraction"]
    },
    {
      "name": "file_tools",
      "description": "Advanced file manipulation and processing utilities",
      "version": "1.0.0",
      "tools_count": 8,
      "status": "active",
      "categories": ["file_operations", "text_processing"]
    }
  ],
  "total": 3
}
```

#### 获取特定 MCP 工具详情
```http
POST /api/mcp-tools/detail
Content-Type: application/json

{
  "tool_name": "github"
}
```

#### 调用 MCP 工具
```http
POST /api/mcp-tools/execute
Content-Type: application/json

{
  "tool_name": "github",
  "function_name": "get_repository",
  "parameters": {
    "owner": "lazygophers",
    "repo": "roo"
  }
}
```

### 9. 系统状态监控

#### 获取系统状态
```http
POST /api/system/status
Content-Type: application/json

{}
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "service_status": "healthy",
    "uptime": 3600,
    "version": "1.0.0",
    "environment": "local",
    "cache_status": {
      "memory_usage": "45%",
      "cache_hits": 1250,
      "cache_misses": 180
    },
    "database_status": {
      "connection": "active",
      "file_watch": "enabled",
      "last_sync": 1704067200
    }
  }
}
```

#### 获取性能指标
```http
POST /api/system/metrics
Content-Type: application/json

{}
```

## 版本历史

- **v1.0.0**: 初始版本，支持基础的 CRUD 操作
- **v1.1.0**: 添加文件元数据支持(文件大小、修改时间)
- **v1.2.0**: 修复规则 slug 前缀问题，优化时间戳格式
- **v2.0.0**: 重大更新 - LazyAI Studio 品牌升级
  - 添加 MCP (Model Context Protocol) 工具集成
  - 新增 GitHub API 工具 (34+ 功能)
  - 添加 Web 抓取和文件操作工具
  - 系统状态监控和性能指标 API
  - 优化缓存系统和数据库性能
  - 支持多主题系统 (9 内置主题)
  - 表情符号模型分类系统