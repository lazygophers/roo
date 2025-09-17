# LazyAI Studio 统一数据库设计文档

## 概述

LazyAI Studio 采用**统一数据库架构**，将所有TinyDB数据库文件合并为单一的 `lazyai.db` 文件，使用不同的表(table)进行数据分离。系统实现了完整的数据验证框架和多级缓存优化。

## 架构设计

### 统一数据层次结构
```
统一数据层次结构
├── 文件系统 (Primary Storage)
│   ├── resources/models/*.yaml         # 模型定义文件
│   ├── resources/hooks/*.md           # Hook文件
│   └── resources/rules*/**/*          # 规则文件
├── 统一数据库 (Single TinyDB File)
│   └── data/lazyai.db                 # 统一数据库文件
│       ├── cache_files                # 缓存文件表
│       ├── cache_metadata             # 缓存元数据表
│       ├── models_cache               # 模型缓存表
│       ├── hooks_cache                # Hook缓存表
│       ├── rules_cache                # 规则缓存表
│       ├── security_paths             # 文件安全路径表
│       ├── security_limits            # 文件安全限制表
│       ├── mcp_tools                  # MCP工具表
│       ├── mcp_categories             # MCP分类表
│       ├── lite_models                # 轻量级模型表
│       └── lite_metadata              # 轻量级元数据表
└── 内存缓存 (Multi-Level)
    ├── L1 Cache (5分钟TTL)
    ├── L2 Cache (30分钟TTL)
    └── L3 Cache (1小时TTL)
```

### 核心服务
- **UnifiedDatabase** (`app/core/unified_database.py`) - 单例模式的统一数据库服务
- **DatabaseValidator** (`app/core/database_validators.py`) - 完整的数据验证框架
- **DatabaseService** - 标准数据库服务（带文件监控）
- **LiteDatabaseService** - 轻量级数据库服务（性能优化）

## 数据表结构

### 1. cache_files - 缓存文件表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| file_path | string | NOT NULL, MAX_LENGTH=255 | - | 文件相对路径 |
| absolute_path | string | NOT NULL, MAX_LENGTH=512 | - | 文件绝对路径 |
| file_name | string | NOT NULL, MAX_LENGTH=100 | - | 文件名称 |
| file_hash | string | NOT NULL, LENGTH=32, REGEX=[a-f0-9]{32} | - | MD5哈希值 |
| file_size | integer | NOT NULL, MIN=0 | 0 | 文件大小（字节） |
| last_modified | integer | NOT NULL, MIN=1 | - | 最后修改时间戳 |
| scan_time | string | NOT NULL, ISO8601 | 当前时间 | 扫描时间 |
| content | object | - | {} | 解析后的文件内容 |
| config_name | string | NOT NULL, MAX_LENGTH=50 | - | 配置名称 |

**唯一性约束**: (file_path, config_name)

### 2. cache_metadata - 缓存元数据表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| config_name | string | NOT NULL, MAX_LENGTH=50, UNIQUE | - | 配置名称 |
| last_sync | string | NOT NULL, ISO8601 | 当前时间 | 最后同步时间 |
| total_files | integer | NOT NULL, MIN=0 | 0 | 文件总数 |
| stats | object | - | {} | 统计信息对象 |

**统计信息结构**:
- `added`: integer - 新增文件数
- `updated`: integer - 更新文件数  
- `deleted`: integer - 删除文件数
- `unchanged`: integer - 未变化文件数

### 3. models_cache - 模型缓存表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| file_path | string | NOT NULL, MAX_LENGTH=255 | - | 文件相对路径 |
| absolute_path | string | NOT NULL, MAX_LENGTH=512 | - | 文件绝对路径 |
| file_name | string | NOT NULL, MAX_LENGTH=100 | - | 文件名称 |
| file_hash | string | NOT NULL, LENGTH=32 | - | MD5哈希值 |
| file_size | integer | NOT NULL, MIN=0 | 0 | 文件大小（字节） |
| last_modified | integer | NOT NULL, MIN=1 | - | 最后修改时间戳 |
| scan_time | string | NOT NULL, ISO8601 | 当前时间 | 扫描时间 |
| content | object | - | {} | 模型定义内容 |
| config_name | string | NOT NULL | "models" | 配置名称 |

**内容结构**:
- `slug`: string - 模型标识符
- `name`: string - 模型名称
- `roleDefinition`: string - 角色定义
- `whenToUse`: string - 使用场景
- `description`: string - 详细描述

### 4. hooks_cache - Hook缓存表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| file_path | string | NOT NULL, MAX_LENGTH=255 | - | 文件相对路径 |
| absolute_path | string | NOT NULL, MAX_LENGTH=512 | - | 文件绝对路径 |
| file_name | string | NOT NULL, MAX_LENGTH=100 | - | 文件名称 |
| file_hash | string | NOT NULL, LENGTH=32 | - | MD5哈希值 |
| file_size | integer | NOT NULL, MIN=0 | 0 | 文件大小（字节） |
| last_modified | integer | NOT NULL, MIN=1 | - | 最后修改时间戳 |
| scan_time | string | NOT NULL, ISO8601 | 当前时间 | 扫描时间 |
| content | object | - | {} | Hook定义内容 |
| config_name | string | NOT NULL | "hooks" | 配置名称 |

**内容结构**:
- `name`: string - Hook名称
- `title`: string - 显示标题
- `description`: string - 描述信息
- `category`: string - 分类
- `priority`: string - 优先级

### 5. rules_cache - 规则缓存表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| file_path | string | NOT NULL, MAX_LENGTH=255 | - | 文件相对路径 |
| absolute_path | string | NOT NULL, MAX_LENGTH=512 | - | 文件绝对路径 |
| file_name | string | NOT NULL, MAX_LENGTH=100 | - | 文件名称 |
| file_hash | string | NOT NULL, LENGTH=32 | - | MD5哈希值 |
| file_size | integer | NOT NULL, MIN=0 | 0 | 文件大小（字节） |
| last_modified | integer | NOT NULL, MIN=1 | - | 最后修改时间戳 |
| scan_time | string | NOT NULL, ISO8601 | 当前时间 | 扫描时间 |
| content | object | - | {} | 规则定义内容 |
| config_name | string | NOT NULL | "rules" | 配置名称 |

### 6. security_paths - 文件安全路径表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| id | string | NOT NULL, MAX_LENGTH=50, UNIQUE | - | 配置ID |
| config_type | string | NOT NULL, ENUM | - | 配置类型 |
| name | string | NOT NULL, MAX_LENGTH=100 | - | 配置名称 |
| description | string | MAX_LENGTH=500 | "" | 配置描述 |
| paths | array | NOT NULL, MIN_ITEMS=1 | - | 路径列表 |
| enabled | boolean | - | true | 是否启用 |
| created_at | string | NOT NULL, ISO8601 | 当前时间 | 创建时间 |
| updated_at | string | NOT NULL, ISO8601 | 当前时间 | 更新时间 |
| metadata | object | - | {} | 元数据信息 |

**config_type 枚举值**: readable, writable, deletable, forbidden

### 7. security_limits - 文件安全限制表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| id | string | NOT NULL, MAX_LENGTH=50, UNIQUE | - | 限制ID |
| limit_type | string | NOT NULL, ENUM | - | 限制类型 |
| name | string | NOT NULL, MAX_LENGTH=100 | - | 限制名称 |
| value | integer | NOT NULL, MIN=0 | 0 | 限制值 |
| description | string | MAX_LENGTH=500 | "" | 限制描述 |
| enabled | boolean | - | true | 是否启用 |
| created_at | string | NOT NULL, ISO8601 | 当前时间 | 创建时间 |
| updated_at | string | NOT NULL, ISO8601 | 当前时间 | 更新时间 |

**limit_type 枚举值**: max_file_size, max_read_lines, strict_mode

### 8. mcp_tools - MCP工具表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| id | string | NOT NULL, UUID, UNIQUE | 自动生成 | 工具唯一标识符 |
| name | string | NOT NULL, MAX_LENGTH=100 | - | 工具名称 |
| description | string | NOT NULL, MAX_LENGTH=500 | - | 工具描述 |
| category | string | NOT NULL, MAX_LENGTH=50 | - | 工具分类 |
| implementation_type | string | NOT NULL, ENUM | "builtin" | 实现类型 |
| schema | object | - | {} | 工具Schema定义 |
| enabled | boolean | - | true | 是否启用 |
| created_at | string | NOT NULL, ISO8601 | 当前时间 | 创建时间 |
| updated_at | string | NOT NULL, ISO8601 | 当前时间 | 更新时间 |
| metadata | object | - | {} | 扩展元数据 |

**implementation_type 枚举值**: builtin, external, plugin  
**唯一性约束**: (name, category)

### 9. mcp_categories - MCP分类表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| id | string | NOT NULL, MAX_LENGTH=50, UNIQUE | - | 分类ID |
| name | string | NOT NULL, MAX_LENGTH=100 | - | 分类名称 |
| description | string | MAX_LENGTH=500 | "" | 分类描述 |
| parent_id | string | MAX_LENGTH=50, FK | null | 父分类ID |
| sort_order | integer | MIN=0 | 0 | 排序顺序 |
| enabled | boolean | - | true | 是否启用 |
| created_at | string | NOT NULL, ISO8601 | 当前时间 | 创建时间 |
| updated_at | string | NOT NULL, ISO8601 | 当前时间 | 更新时间 |

**外键约束**: parent_id → mcp_categories.id

### 10. lite_models - 轻量级模型表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| slug | string | NOT NULL, MAX_LENGTH=100, UNIQUE | - | 模型标识符 |
| name | string | NOT NULL, MAX_LENGTH=200 | - | 模型名称 |
| file_path | string | NOT NULL, MAX_LENGTH=255 | - | 文件路径 |
| file_hash | string | NOT NULL, LENGTH=32 | - | 文件哈希值 |
| last_modified | integer | NOT NULL, MIN=1 | - | 最后修改时间 |
| content | object | - | {} | 模型内容 |
| cached_at | string | NOT NULL, ISO8601 | 当前时间 | 缓存时间 |

### 11. lite_metadata - 轻量级元数据表

| 字段名 | 数据类型 | 约束条件 | 默认值 | 描述 |
|--------|----------|----------|--------|------|
| config_name | string | NOT NULL, MAX_LENGTH=50, UNIQUE | - | 配置名称 |
| last_sync | string | NOT NULL, ISO8601 | 当前时间 | 最后同步时间 |
| total_files | integer | NOT NULL, MIN=0 | 0 | 文件总数 |
| stats | object | - | {} | 统计信息 |

## 约束关系

```
mcp_categories (id) ←─── mcp_categories (parent_id)  [自引用]
mcp_categories (id) ←─── mcp_tools (category)        [外键引用]

cache_files: UNIQUE(file_path, config_name)
mcp_tools: UNIQUE(name, category)
```

## 索引设计

### 主要索引
- **cache_files**: (config_name, file_path), (file_hash)
- **mcp_tools**: (category), (enabled), (name)
- **security_paths**: (config_type), (enabled)
- **security_limits**: (limit_type), (enabled)
- **lite_models**: (slug), (file_hash)

### 复合索引
- **cache_files**: (config_name, scan_time) - 用于时间范围查询
- **mcp_tools**: (category, enabled) - 用于分类筛选
- **security_paths**: (config_type, enabled) - 用于配置查询

## 数据验证系统

### 字段级验证器
- **validate_file_path**: 验证文件路径安全性和长度
- **validate_md5_hash**: 验证MD5哈希值格式（32位十六进制）
- **validate_uuid**: 验证UUID v4格式
- **validate_datetime_string**: 验证ISO 8601日期时间格式
- **validate_json_object/array**: 验证JSON数据格式
- **validate_enum_value**: 验证枚举值有效性
- **validate_string_length**: 验证字符串长度范围
- **validate_integer_range**: 验证整数值范围

### 表级验证器
- **validate_cache_file_record**: 缓存文件记录完整性验证
- **validate_mcp_tool_record**: MCP工具记录验证（自动生成UUID和时间戳）
- **validate_security_paths_record**: 安全路径配置验证
- **validate_security_limits_record**: 安全限制配置验证

### 约束检查器
- **check_file_path_uniqueness**: 检查文件路径唯一性
- **check_tool_name_uniqueness**: 检查工具名称唯一性
- **check_category_exists**: 检查分类存在性
- **validate_referential_integrity**: 验证引用完整性

## 数据库迁移

### 自动迁移机制
系统启动时自动检查并迁移旧的数据库文件：

```python
# 旧数据库文件映射
old_dbs_mapping = {
    "cache.db": {
        "files": "cache_files",
        "metadata": "cache_metadata", 
        "models_cache": "models_cache",
        "hooks_cache": "hooks_cache",
        "rules_cache": "rules_cache"
    },
    "file_security.db": {
        "security_paths": "security_paths",
        "security_limits": "security_limits"
    },
    "mcp_tools.db": {
        "mcp_tools": "mcp_tools",
        "mcp_categories": "mcp_categories"
    },
    "lite_cache.db": {
        "models": "lite_models",
        "metadata": "lite_metadata"
    }
}
```

### 手动迁移
```bash
# 通过API触发
curl -X POST http://localhost:8000/api/database/migrate

# 或通过Python代码
from app.core.unified_database import init_unified_database
db, migration_log = init_unified_database()
```

## API端点

### 核心端点

| 端点 | 方法 | 功能 | 描述 |
|------|------|------|------|
| `/database/status` | GET | 获取同步状态 | 返回同步状态和统一数据库信息 |
| `/database/sync/{config_name}` | POST | 手动同步 | 触发指定配置的同步 |
| `/database/data/{config_name}` | GET | 获取缓存数据 | 从缓存获取数据，支持过滤 |
| `/database/file/{config_name}` | GET | 获取文件数据 | 根据路径获取特定文件 |
| `/database/models/fast` | GET | 快速获取模型 | 从缓存快速返回模型列表 |
| `/database/migrate` | POST | 数据库迁移 | 手动执行从旧数据库到统一数据库的迁移 |
| `/database/tables` | GET | 获取表信息 | 返回统一数据库中所有表及记录数 |

### 过滤参数
- `slug`: 按slug过滤
- `name`: 按名称模糊搜索
- `file_name`: 按文件名精确匹配

## 性能特性

### 服务选择建议

| 场景 | 推荐服务 | 理由 |
|------|----------|------|
| 开发环境 | DatabaseService | 完整功能，实时监控，便于调试 |
| 生产环境(中等负载) | LiteDatabaseService | 平衡性能与功能 |
| 生产环境(高负载) | UltraCacheSystem | 极致性能优化 |

### 缓存策略
- **内存缓存**: TTL=300秒的内存缓存层
- **LRU缓存**: 带64项LRU缓存的YAML解析器
- **多级缓存**: L1(5分钟) → L2(30分钟) → L3(1小时) → 磁盘缓存

## 安全特性

### 日志安全
使用 `app/core/secure_logging.py` 防止日志注入：
```python
from app.core.secure_logging import sanitize_for_log
logger.info(f"Processing file: {sanitize_for_log(filename)}")
```

### 输入验证
- 文件路径验证，防止目录遍历攻击
- YAML内容验证，防止恶意解析
- 所有用户输入自动应用验证规则

## 最佳实践

### 缓存键设计
```python
# 良好的缓存键命名
"models:all"                    # 所有模型
"models:group:ai-assistant"     # 特定分组
"models:slug:claude-3"          # 特定模型
"rules:category:programming"    # 特定规则分类
```

### 监控指标
关键性能指标：
- 缓存命中率 (>90% 为优秀)
- 平均响应时间 (<50ms)
- 内存使用率 (<80%)
- 文件同步延迟 (<1s)

## 故障排查

### 常见问题
1. **缓存未命中率高** - 检查TTL设置，确认预热策略
2. **文件同步延迟** - 检查文件系统监控和权限
3. **内存使用过高** - 调整缓存大小，检查内存泄漏
4. **数据库迁移失败** - 检查文件权限和磁盘空间

### 诊断命令
```python
# 获取统一数据库信息
unified_db = get_unified_database()
tables_info = unified_db.get_all_tables()

# 手动执行迁移
migration_log = unified_db.migrate_from_old_databases()

# 检查数据库状态
db = get_database_service()
status = db.get_sync_status()
```

---

*最后更新: 2025-09-12*