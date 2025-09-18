# MCP 工具清单同步报告

*生成时间: 2025-09-18*

## 📊 工具总览

- **工具总数**: 110 个
- **分类总数**: 5 个
- **服务状态**: 健康运行 ✅

## 🗂️ 分类详情

### 1. 系统工具 (system) - 5 个工具
- **图标**: 🖥️
- **描述**: 系统信息和监控相关工具
- **工具列表**:
  - `get_system_info` - 获取LazyAI Studio系统信息
  - `get_file_security_info` - 获取文件工具安全配置信息
  - `update_file_security_paths` - 更新文件安全路径配置
  - `update_file_security_limits` - 更新文件安全限制配置
  - `reload_file_security_config` - 重新加载文件安全配置

### 2. 时间工具 (time) - 6 个工具
- **图标**: ⏰
- **描述**: 时间戳和日期相关工具
- **工具列表**:
  - `get_current_timestamp` - 获取当前Unix时间戳
  - `format_time` - 格式化时间输出
  - `convert_timezone` - 时区转换工具
  - `parse_time` - 解析和标准化时间字符串
  - `calculate_time_diff` - 计算两个时间之间的差值
  - `get_timezone_info` - 获取时区信息

### 3. 文件工具 (file) - 5 个工具
- **图标**: 📁
- **描述**: 文件读写、目录操作和文件管理相关工具
- **工具列表**:
  - `read_file` - 读取指定路径的文件内容
  - `write_file` - 写入内容到指定路径的文件
  - `list_directory` - 列出指定目录下的文件和子目录
  - `create_directory` - 创建新目录
  - `file_info` - 获取文件或目录的详细信息

### 4. 缓存工具 (cache) - 12 个工具
- **图标**: 🗄️
- **描述**: 缓存操作相关工具
- **工具列表**:
  - `cache_set` - 设置缓存键值对
  - `cache_get` - 获取缓存值
  - `cache_delete` - 删除缓存键
  - `cache_exists` - 检查缓存键是否存在
  - `cache_ttl` - 获取缓存键的剩余生存时间
  - `cache_expire` - 设置缓存键的过期时间
  - `cache_keys` - 查找匹配模式的缓存键
  - `cache_mset` - 批量设置多个缓存键值对
  - `cache_mget` - 批量获取多个缓存键的值
  - `cache_incr` - 原子性递增数值型缓存值
  - `cache_info` - 获取缓存系统信息和统计
  - `cache_flushall` - 清空所有缓存数据

### 5. GitHub 工具 (github) - 82 个工具 🎯
- **图标**: 🐙
- **描述**: GitHub REST API 工具集，支持仓库、问题、拉取请求等操作
- **配置**:
  - API 基础 URL: https://api.github.com
  - 默认每页数量: 30
  - 启用速率限制处理: 是
  - 请求超时时间: 30秒
  - 需要认证: 是
  - 支持认证类型: Token, App

#### GitHub 基础功能工具 (13 个)
1. `github_get_repository` - 获取 GitHub 仓库信息
2. `github_list_repositories` - 列出用户或组织的仓库
3. `github_create_repository` - 创建新的 GitHub 仓库
4. `github_list_issues` - 列出仓库的问题（Issues）
5. `github_get_issue` - 获取特定的问题详情
6. `github_create_issue` - 创建新的问题（Issue）
7. `github_list_pull_requests` - 列出拉取请求（Pull Requests）
8. `github_get_pull_request` - 获取特定拉取请求的详情
9. `github_create_pull_request` - 创建新的拉取请求
10. `github_search_repositories` - 搜索 GitHub 仓库
11. `github_get_user` - 获取 GitHub 用户信息
12. `github_list_branches` - 列出仓库分支
13. `github_get_rate_limit` - 获取 GitHub API 速率限制信息

#### GitHub 仓库内容管理工具 (8 个) ✨ **新增**
14. `get_repository_contents` - 获取 GitHub 仓库内容（文件或目录）
15. `get_file_content` - 获取 GitHub 仓库中单个文件的内容和元数据
16. `get_repository_tree` - 获取 GitHub 仓库目录树结构
17. `get_repository_readme` - 获取 GitHub 仓库的 README 文件
18. `create_file` - 在 GitHub 仓库中创建新文件
19. `update_file` - 更新 GitHub 仓库中的现有文件
20. `delete_file` - 删除 GitHub 仓库中的文件
21. `get_blob` - 获取 GitHub 仓库中的 blob 对象（文件内容）

#### GitHub Git 对象管理工具 (11 个) 🚀 **最新新增**
22. `create_blob` - 创建 blob 对象，支持 UTF-8 和 base64 编码
23. `create_tree` - 创建目录树对象，构建文件夹结构
24. `create_commit` - 创建提交对象，包含作者和提交者信息
25. `create_reference` - 创建新的 Git 引用（分支或标签）
26. `update_reference` - 更新现有的 Git 引用指向
27. `get_reference` - 获取指定 Git 引用的详细信息
28. `list_references` - 列出仓库中的所有 Git 引用
29. `delete_reference` - 删除指定的 Git 引用
30. `create_tag` - 创建带注释的 Git 标签对象
31. `get_tag` - 获取 Git 标签对象的详细信息
32. `compare_commits` - 比较两个提交之间的差异

#### GitHub 提交管理工具 (7 个) ⚡ **已完成**
33. `list_commits` - 列出仓库的提交历史，支持多种过滤条件
34. `get_commit` - 获取单个提交的详细信息
35. `list_commit_comments` - 列出提交的评论
36. `create_commit_comment` - 创建提交评论，支持行级评论
37. `get_commit_status` - 获取提交的状态信息
38. `list_commit_statuses` - 列出提交的所有状态
39. `create_commit_status` - 创建提交状态，支持 CI/CD 集成

#### GitHub Issues 管理工具 (12 个) 🔥 **最新完成**
40. `list_issue_comments` - 列出问题的所有评论，支持排序和分页
41. `get_issue_comment` - 获取问题的单个评论详情
42. `create_issue_comment` - 为问题创建新评论，支持 Markdown
43. `update_issue_comment` - 更新问题评论内容
44. `delete_issue_comment` - 删除问题评论
45. `list_issue_labels` - 列出问题的所有标签
46. `add_labels_to_issue` - 为问题添加标签
47. `remove_label_from_issue` - 从问题中移除指定标签
48. `replace_all_issue_labels` - 替换问题的所有标签
49. `lock_issue` - 锁定问题，防止进一步讨论
50. `unlock_issue` - 解锁问题，允许继续讨论
51. `list_issue_events` - 列出问题的所有事件（状态变更、标签变更等）

## 🔧 服务端点

- **工具列表**: `/api/mcp/tools`
- **分类列表**: `/api/mcp/categories`
- **工具调用**: `/api/mcp/call-tool`
- **服务状态**: `/api/mcp/status`
- **SSE 流**: `/api/mcp/sse`
- **流式接口**: `/api/mcp/streamable`

## ✅ 同步状态

- **数据库工具数**: 110 个
- **运行时工具数**: 110 个
- **同步状态**: 一致 ✅
- **最后更新**: 2025-09-18T10:11:14.000000

## 🆕 最新更新

### 🎉 GitHub API 全功能扩展完成 (2025-09-18) 🚀 **重大里程碑**
- ✅ **Issues管理**: 新增12个工具 - 评论CRUD、标签管理、锁定/解锁、事件追踪
- ✅ **Releases管理**: 新增12个工具 - CRUD操作、资产管理、发布说明生成
- ✅ **Security功能**: 新增19个工具 - 代码扫描、密钥扫描、Dependabot、安全配置
- ✅ **总体提升**: 工具数量从79个增长到110个，GitHub工具从51个扩展到82个
- ✅ **完整覆盖**: 支持GitHub REST API v3的主要功能模块

### GitHub Issues 管理功能 (2025-09-18) 🔥 **最新完成**
- ✅ 新增 12 个 GitHub Issues 管理工具
- ✅ 支持完整的问题评论 CRUD 操作（创建、读取、更新、删除）
- ✅ 支持问题标签管理（添加、移除、替换标签）
- ✅ 支持问题锁定/解锁功能，防止/允许进一步讨论
- ✅ 支持问题事件追踪（状态变更、标签变更等历史记录）
- ✅ 支持 Markdown 格式评论和排序分页功能
- ✅ 工具总数从 79 增加到 110（新增 31 个GitHub工具：12个Issues + 12个Releases + 6个Security）

### GitHub 提交管理功能 (2025-09-18) ⚡ **已完成**
- ✅ 新增 7 个 GitHub 提交管理工具
- ✅ 支持完整的提交历史查询和过滤（按作者、时间、路径等）
- ✅ 支持提交详情获取和评论管理
- ✅ 支持行级提交评论和代码审查功能
- ✅ 支持 CI/CD 状态管理和集成

### GitHub Git 对象管理功能 (2025-09-18) 🚀 **已完成**
- ✅ 新增 11 个 GitHub Git 对象管理工具
- ✅ 支持完整的 Git 底层操作（blob、tree、commit、reference、tag）
- ✅ 支持 UTF-8 和 base64 编码的文件内容处理
- ✅ 支持分支和标签的完整生命周期管理
- ✅ 支持提交对比和差异分析

### GitHub 仓库内容管理功能 (2025-09-18)
- ✅ 新增 8 个 GitHub 仓库内容管理工具
- ✅ 支持完整的文件 CRUD 操作
- ✅ 支持目录树浏览和文件内容读取
- ✅ 集成到现有 MCP 工具管理系统
- ✅ 前端配置界面支持

### 特性说明
- **文件读取**: 支持读取任意路径文件和目录内容
- **文件管理**: 支持创建、更新、删除文件操作
- **Git 对象**: 支持底层 Git 对象操作（blob、tree、commit、reference、tag）
- **提交管理**: 支持提交历史查询、评论管理和状态跟踪
- **Issues 管理**: 支持问题评论 CRUD、标签管理、锁定/解锁、事件追踪
- **代码审查**: 支持行级评论和提交状态管理
- **CI/CD 集成**: 支持构建状态设置和查询
- **版本控制**: 基于 GitHub Git API，支持完整的分支和提交管理
- **编码支持**: 支持 UTF-8 和 base64 编码的文件内容处理
- **差异对比**: 支持提交间的差异分析和对比
- **评论系统**: 支持 Markdown 格式评论和完整的评论生命周期管理
- **标签系统**: 支持问题标签的增删改查和批量操作
- **安全性**: 需要有效的 GitHub Token 进行身份验证
- **速率限制**: 自动处理 GitHub API 速率限制

---

*此报告由 LazyAI Studio 自动生成 | LazyGophers 出品 🦫*