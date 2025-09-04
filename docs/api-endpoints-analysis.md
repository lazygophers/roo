# FastAPI 路由端点分析

## 分析时间
2025-01-04 12:14:53 UTC

## 分析文件
`app/api/routes.py`

## 路由概览

该 FastAPI 应用共包含 23 个路由端点，分为以下几个主要功能模块：

1. **基础功能** (1个端点)
2. **模型管理** (2个端点)
3. **钩子管理** (2个端点)
4. **规则管理** (1个端点)
5. **命令管理** (2个端点)
6. **角色管理** (2个端点)
7. **配置管理** (9个端点)
8. **命令执行** (1个端点)

## 详细端点信息

### 1. 基础功能

#### POST /hello
- **功能**: 简单的问候端点，支持前端调用
- **请求体**: HelloRequest
  ```yaml
  message:
    type: str
    required: false
    default: "Hello from FastAPI!"
  ```
- **响应**: 
  ```yaml
  {
    "message": "string",
    "status": "success"
  }
  ```

### 2. 模型管理

#### POST /models
- **功能**: 获取 models 目录及其子目录的所有文件信息
- **响应**: List[Dict[str, Any]]
- **说明**: 自动排除 customInstructions 字段

#### POST /models/get
- **功能**: 根据 slug 获取 models 目录下具体文件的完整内容
- **请求体**: ModelRequest
  ```yaml
  slug:
    type: str
    required: false
  ```
- **响应**: Dict[str, Any]

### 3. 钩子管理

#### POST /hooks/before
- **功能**: 获取 hooks/before.md 文件的 frontmatter 元数据和内容
- **响应**: Dict[str, Any]

#### POST /hooks/after
- **功能**: 获取 hooks/after.md 文件的 frontmatter 元数据和内容
- **响应**: Dict[str, Any]

### 4. 规则管理

#### POST /rules/get
- **功能**: 根据 slug 获取 rules 目录下的所有文件内容和 frontmatter 元数据
- **请求体**: ModelRequest
  ```yaml
  slug:
    type: str
    required: false
  ```
- **响应**: Dict[str, Dict[str, Any]]
- **搜索顺序**: rules/ -> rules-{slug} -> rules-{prefix}-{subslug}

### 5. 命令管理

#### POST /commands
- **功能**: 获取 commands 目录下的所有文件内容和 frontmatter 元数据
- **响应**: Dict[str, Dict[str, Any]]

#### POST /roles
- **功能**: 获取 roles 目录下的所有文件内容和 frontmatter 元数据
- **响应**: Dict[str, Dict[str, Any]]

### 6. 配置管理

#### POST /configurations
- **功能**: 保存配置到数据库
- **请求体**: Dict[str, Any]
  ```yaml
  name: str
  config: Dict[str, Any]
  description: str
  user_id: str
  ```
- **响应**: Dict[str, Any]
  ```yaml
  {
    "success": true,
    "message": "配置保存成功",
    "config_id": "string",
    "data": Dict[str, Any]
  }
  ```

#### POST /configurations (GET)
- **功能**: 获取所有配置或用户专属配置
- **请求体**: ConfigRequest
  ```yaml
  user_id:
    type: str
    required: false
  ```
- **响应**: List[Dict[str, Any]]

#### POST /configurations/get
- **功能**: 根据 ID 获取单个配置
- **请求体**: ConfigIdRequest
  ```yaml
  config_id:
    type: str
    required: true
  ```
- **响应**: Dict[str, Any]

#### POST /configurations/update
- **功能**: 更新配置
- **请求体**: UpdateConfigRequest
  ```yaml
  config_data:
    config_id: str
    config: Dict[str, Any]
    name: str
    description: str
    user_id: str
  ```
- **响应**: Dict[str, Any]

#### POST /configurations/delete
- **功能**: 删除配置
- **请求体**: ConfigIdRequest
  ```yaml
  config_id:
    type: str
    required: true
  user_id:
    type: str
    required: false
  ```
- **响应**: Dict[str, Any]

#### POST /configurations/export/yaml
- **功能**: 导出配置为 YAML 文件
- **请求体**: ConfigIdRequest
- **响应**: StreamingResponse (application/x-yaml)
- **说明**: 自动移除数据库内部字段，只保留用户配置数据

#### POST /configurations/export/json
- **功能**: 导出配置为 JSON 文件
- **请求体**: ConfigIdRequest
- **响应**: StreamingResponse (application/json)
- **说明**: 自动移除数据库内部字段，只保留用户配置数据

#### POST /configurations/import/yaml
- **功能**: 从 YAML 文件导入配置
- **请求参数**:
  - file: UploadFile (必需)
  - user_id: str (可选)
- **响应**: Dict[str, Any]

#### POST /configurations/import/json
- **功能**: 从 JSON 文件导入配置
- **请求参数**:
  - file: UploadFile (必需)
  - user_id: str (可选)
- **响应**: Dict[str, Any]

### 7. 命令执行

#### POST /commands/execute
- **功能**: 执行系统命令并返回输出结果
- **请求体**: CommandExecuteRequest
  ```yaml
  command:
    type: str
    required: true
  working_dir:
    type: str
    required: false
  user_id:
    type: str
    required: false
  ```
- **响应**: Dict[str, Any]
  ```yaml
  {
    "success": "boolean",
    "command": "str",
    "exit_code": "int",
    "stdout": "str",
    "stderr": "str"
  }
  ```
- **安全特性**:
  - 验证 Bearer Token
  - 记录所有命令执行日志
  - 限制命令执行权限

### 8. 角色管理

#### POST /roles/get
- **功能**: 获取指定角色的详细信息
- **请求体**: RoleRequest
  ```yaml
  role_name:
    type: str
    required: true
  ```
- **响应**: RoleResponse
  ```yaml
  {
    "name": "str",
    "title": "str",
    "description": "str",
    "category": "str",
    "traits": ["str"],
    "features": {},
    "content": "str"
  }
  ```

#### GET /roles
- **功能**: 列出所有可用的角色
- **响应**: List[Dict[str, Any]]
- **返回信息**: 名称、标题、描述、分类、特质

## 数据模型定义

### 请求模型
1. **HelloRequest**
   - message: Optional[str]

2. **ModelRequest**
   - slug: Optional[str]

3. **ConfigRequest**
   - user_id: Optional[str]

4. **ConfigIdRequest**
   - config_id: str

5. **UpdateConfigRequest**
   - config_data: Dict[str, Any]

6. **CommandRequest**
   - command: str (description: 要执行的命令字符串)
   - working_dir: Optional[str] (description: 工作目录路径)

7. **CommandExecuteRequest**
   - command: str (description: 要执行的命令字符串)
   - working_dir: Optional[str] (description: 工作目录路径)
   - user_id: Optional[str] (description: 用户ID，用于权限控制)

8. **RoleRequest**
   - role_name: str (description: 角色名称)

### 响应模型
1. **RoleResponse**
   - name: str (description: 角色名称)
   - title: str (description: 角色标题)
   - description: str (description: 角色描述)
   - category: str (description: 角色分类)
   - traits: List[str] (default: [], description: 角色特质列表)
   - features: Dict[str, Any] (default: {}, description: 角色特性字典)
   - content: str (description: 角色完整内容)

## 文件上传端点

以下端点支持文件上传：
- POST /configurations/import/yaml
- POST /configurations/import/json

## 文件下载端点

以下端点返回文件流：
- POST /configurations/export/yaml
- POST /configurations/export/json

## 特殊说明

1. **错误处理**: 所有端点都有完善的错误处理机制，返回适当的 HTTP 状态码
2. **文件路径**: 使用相对路径，基于 RESOURCES_DIR
3. **安全考虑**: 命令执行端点包含认证和授权检查
4. **数据格式**: YAML 文件处理时排除 customInstructions 字段