# API 参考文档

## 概述

本文档提供了基于 FastAPI 路由文件的完整 API 参考。该应用提供了管理 AI 系统配置、模型、规则和命令的全面接口。

## 基础信息

- **Base URL**: `http://localhost:14001/api`
- **API 版本**: v1
- **认证方式**: 无（当前版本）

## 端点详情

### 1. 问候接口

#### POST /hello

**描述**: 简单的问候端点，用于测试 API 是否正常运行

**请求体**:
```json
{
  "name": "string"
}
```

**响应**:
```json
{
  "message": "Hello {name}!"
}
```

---

### 2. 模型管理

#### POST /models

**描述**: 获取所有可用的模型文件列表

**请求体**: 无

**响应**:
```json
{
  "models": [
    {
      "name": "string",
      "description": "string",
      "path": "string"
    }
  ]
}
```

#### POST /models/get

**描述**: 根据指定的 slug 获取特定模型信息

**请求体**:
```json
{
  "slug": "string"
}
```

**响应**:
```json
{
  "model": {
    "name": "string",
    "description": "string",
    "content": "string",
    "path": "string"
  }
}
```

---

### 3. 钩子函数

#### POST /hooks/before

**描述**: 获取全局前置钩子规则

**请求体**: 无

**响应**:
```json
{
  "hook": {
    "name": "before",
    "title": "string",
    "description": "string",
    "content": "string"
  }
}
```

#### POST /hooks/after

**描述**: 获取全局后置钩子规则

**请求体**: 无

**响应**:
```json
{
  "hook": {
    "name": "after",
    "title": "string",
    "description": "string",
    "content": "string"
  }
}
```

---

### 4. 规则管理

#### POST /rules/get

**描述**: 根据指定的 slug 获取规则内容

**请求体**:
```json
{
  "slug": "string"
}
```

**响应**:
```json
{
  "rule": {
    "name": "string",
    "title": "string",
    "description": "string",
    "content": "string",
    "path": "string"
  }
}
```

---

### 5. 命令管理

#### POST /commands

**描述**: 获取所有可用的命令列表

**请求体**: 无

**响应**:
```json
{
  "commands": [
    {
      "name": "string",
      "description": "string",
      "usage": "string"
    }
  ]
}
```

---

### 6. 角色管理

#### POST /roles

**描述**: 获取所有可用角色列表

**请求体**: 无

**响应**:
```json
{
  "roles": [
    {
      "name": "string",
      "description": "string",
      "traits": ["string"],
      "features": ["string"]
    }
  ]
}
```

#### POST /roles/get

**描述**: 根据指定的名称获取角色详细信息

**请求体**:
```json
{
  "name": "string"
}
```

**响应**:
```json
{
  "role": {
    "name": "string",
    "title": "string",
    "description": "string",
    "traits": ["string"],
    "features": ["string"],
    "content": "string"
  }
}
```

---

### 7. 配置管理

#### POST /configurations/save

**描述**: 保存配置数据

**请求体**:
```json
{
  "data": "object"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Configuration saved successfully"
}
```

#### POST /configurations/get

**描述**: 获取当前配置数据

**请求体**: 无

**响应**:
```json
{
  "data": "object"
}
```

#### POST /configurations/update

**描述**: 更新配置数据

**请求体**:
```json
{
  "data": "object"
}
```

**响应**:
```json
{
  "success": true,
  "message": "Configuration updated successfully"
}
```

#### POST /configurations/delete

**描述**: 删除配置数据

**请求体**: 无

**响应**:
```json
{
  "success": true,
  "message": "Configuration deleted successfully"
}
```

---

### 8. 配置导入导出

#### POST /configurations/export/yaml

**描述**: 导出 YAML 格式的配置

**请求体**:
```json
{
  "shell": "string"
}
```

**响应**:
```yaml
# YAML 配置内容
```

#### POST /configurations/export/json

**描述**: 导出 JSON 格式的配置

**请求体**:
```json
{
  "shell": "string"
}
```

**响应**:
```json
{
  "configuration": "object"
}
```

#### POST /configurations/import/yaml

**描述**: 导入 YAML 格式的配置

**请求体**:
```json
{
  "content": "string"
}
```

**响应**:
```json
{
  "success": true,
  "message": "YAML configuration imported successfully"
}
```

#### POST /configurations/import/json

**描述**: 导入 JSON 格式的配置

**请求体**:
```json
{
  "content": "string"
}
```

**响应**:
```json
{
  "success": true,
  "message": "JSON configuration imported successfully"
}
```

---

### 9. 命令执行

#### POST /commands/execute

**描述**: 执行系统命令

**请求体**:
```json
{
  "command": "string",
  "args": ["string"]
}
```

**响应**:
```json
{
  "success": true,
  "output": "string",
  "error": "string"
}
```

---

## 错误响应

所有端点在发生错误时都会返回以下格式的响应：

```json
{
  "detail": "错误信息"
}
```

## 使用示例

### 测试 API 连接

```bash
curl -X POST "http://localhost:14001/api/hello" \
  -H "Content-Type: application/json" \
  -d '{"name": "World"}'
```

### 获取所有模型

```bash
curl -X POST "http://localhost:14001/api/models" \
  -H "Content-Type: application/json"
```

### 导出配置

```bash
curl -X POST "http://localhost:14001/api/configurations/export/yaml" \
  -H "Content-Type: application/json" \
  -d '{"shell": "default"}'
```

## 注意事项

1. 所有请求必须设置 `Content-Type: application/json` 头
2. 请求体必须为有效的 JSON 格式
3. 某些端点可能需要特定的权限才能访问
4. 文件上传和下载功能支持多种文件格式