import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

export interface ModelInfo {
  slug: string;
  name: string;
  roleDefinition: string;
  whenToUse: string;
  description: string;
  groups: any[];
  file_path: string;
  file_size?: number;
  last_modified?: number;
}

export interface ModelsResponse {
  success: boolean;
  message: string;
  data: ModelInfo[];
  count: number;
  total: number;
}

export interface FileMetadata {
  name?: string;
  title?: string;
  description?: string;
  category?: string;
  language?: string;
  priority?: string;
  tags?: string[];
  sections?: string[];
  references?: string[];
  file_path: string;
  source_directory: string;
  file_size: number;
  last_modified: number;
}

export interface CommandsResponse {
  success: boolean;
  message: string;
  data: FileMetadata[];
  count: number;
  total: number;
}

export interface RulesResponse {
  success: boolean;
  message: string;
  data: FileMetadata[];
  count: number;
  total: number;
}

export interface HookInfo {
  name: string;
  title: string;
  description: string;
  category: string;
  priority: string;
  tags: string[];
  examples?: string[];
  content: string;
  file_path: string;
}

export interface HookResponse {
  success: boolean;
  message: string;
  data: HookInfo;
}

export interface RoleInfo {
  name: string;
  title: string;
  description: string;
  category: string;
  traits: string[];
  features: string[];
  restrictions?: string[];
  file_path: string;
}

export interface RoleResponse {
  success: boolean;
  message: string;
  data: RoleInfo[];
  total: number;
}

export interface DeployTarget {
  name: string;
  path: string;
  enabled: boolean;
  description: string;
}

export interface DeployRequest {
  selected_models: string[];
  selected_commands: string[];
  selected_rules: string[];
  model_rule_bindings: any[];
  selected_role?: string;
  deploy_targets: string[];
}

export interface DeployResponse {
  success: boolean;
  message: string;
  deployed_files: string[];
  errors: string[];
}

export interface CleanupRequest {
  cleanup_type: 'models' | 'directories';
  deploy_targets: string[];
}

export interface CleanupResponse {
  success: boolean;
  message: string;
  cleaned_items: string[];
  errors: string[];
}

// MCP Types
export interface MCPToolInfo {
  id: string;
  name: string;
  description: string;
  category: string;
  schema: any;
  enabled: boolean;
  implementation_type: string;
  created_at: string;
  updated_at: string;
  metadata?: any;
}

export interface MCPCategoryInfo {
  id: string;
  name: string;
  description: string;
  icon: string;
  enabled: boolean;
  tools_count?: number;
}

export interface MCPStatusResponse {
  success: boolean;
  message: string;
  data: {
    status: string;
    server_name: string;
    tools_count: number;
    total_tools: number;
    categories_count: number;
    tools_by_category: Record<string, number>;
    endpoints: Record<string, string>;
    organization: string;
    motto: string;
    last_updated: string;
  };
}

export interface MCPToolsResponse {
  success: boolean;
  message: string;
  data: {
    tools: MCPToolInfo[];
    server: string;
    organization: string;
  };
}

export interface MCPCategoriesResponse {
  success: boolean;
  message: string;
  data: {
    categories: MCPCategoryInfo[];
    total_categories: number;
  };
}

// File Security Types
export interface FileSecurityInfo {
  readable_directories: string[];
  writable_directories: string[];
  deletable_directories: string[];
  forbidden_directories: string[];
  max_file_size_mb: number;
  max_read_lines: number;
  strict_mode: boolean;
  recycle_bin_enabled?: boolean;
  recycle_bin_retention_days?: number;
  recycle_bin_auto_cleanup_hours?: number;
  database_summary?: any;
}

export interface FileSecurityResponse {
  status: string;
  data: FileSecurityInfo;
}

export interface UpdatePathsRequest {
  config_type: 'readable' | 'writable' | 'deletable' | 'forbidden';
  paths: string[];
}

export interface UpdateLimitsRequest {
  limit_type: 'max_file_size' | 'max_read_lines' | 'strict_mode' | 'recycle_bin_enabled' | 'recycle_bin_retention_days' | 'recycle_bin_auto_cleanup_hours';
  value: number | boolean;
}

export interface SecurityActionResponse {
  status: string;
  message?: string;
  data?: any;
}

// Recycle Bin Types
export enum RecycleBinItemType {
  MODEL = "model",
  COMMAND = "command",
  RULE = "rule",
  HOOK = "hook",
  ROLE = "role",
  CONFIGURATION = "configuration",
  SECURITY_PATH = "security_path",
  SECURITY_LIMIT = "security_limit",
  MCP_TOOL = "mcp_tool",
  MCP_CATEGORY = "mcp_category",
  CACHE_FILE = "cache_file",
  CACHE_METADATA = "cache_metadata"
}

export interface RecycleBinItem {
  id: string;
  original_id: string;
  item_type: string;
  original_table: string;
  original_data: any;
  deleted_by: string;
  deleted_reason: string;
  deleted_at: string;
  expires_at: string;
  is_expired: boolean;
  remaining_days: number;
  metadata?: any;
}

export interface SoftDeleteRequest {
  table_name: string;
  item_id: string;
  item_type: RecycleBinItemType;
  deleted_by?: string;
  deleted_reason?: string;
  retention_days?: number;
}

export interface RecycleBinStatsResponse {
  total_items: number;
  by_type: Record<string, number>;
  expired_items: number;
  expiring_soon: number;
  oldest_item?: string;
  newest_item?: string;
}

export interface RecycleBinResponse {
  status: string;
  message?: string;
  data?: any;
}

// 环境信息类型
export interface EnvironmentInfo {
  environment: 'local' | 'remote';
  is_local: boolean;
  is_remote: boolean;
  tool_call_allowed: boolean;
  tool_edit_allowed: boolean;
}

export interface EnvironmentResponse {
  success: boolean;
  message: string;
  data: EnvironmentInfo;
}


// API 方法
export const apiClient = {
  // 获取所有模型
  getModels: async (params: { category?: string; search?: string } = {}) => {
    const response = await api.post<ModelsResponse>('/models', params);
    return response.data;
  },

  // 获取单个模型
  getModelBySlug: async (slug: string) => {
    const response = await api.post<ModelInfo>('/models/by-slug', { slug });
    return response.data;
  },

  // 获取模型分类
  getModelCategories: async () => {
    const response = await api.post('/models/categories/list');
    return response.data;
  },

  // 获取指令列表
  getCommands: async () => {
    const response = await api.post<CommandsResponse>('/commands', {});
    return response.data;
  },

  // 获取规则列表（默认规则目录）
  getRules: async () => {
    const response = await api.post<RulesResponse>('/rules', {});
    return response.data;
  },

  // 根据 slug 获取规则
  getRulesBySlug: async (slug: string) => {
    const response = await api.post('/rules/by-slug', { slug });
    return response.data;
  },

  // 获取 hooks
  getBeforeHook: async () => {
    const response = await api.post<HookResponse>('/hooks/before');
    return response.data;
  },

  getAfterHook: async () => {
    const response = await api.post<HookResponse>('/hooks/after');
    return response.data;
  },

  getAllHooks: async () => {
    const response = await api.post('/hooks');
    return response.data;
  },

  // 保存配置
  saveConfiguration: async (configData: {
    name: string;
    description?: string;
    selectedItems: any[];
    modelRuleBindings: any[];
    modelRules: Record<string, any[]>;
    overwrite?: boolean;
  }) => {
    const response = await api.post('/config/save', configData);
    return response.data;
  },

  // 获取配置列表
  getConfigurations: async () => {
    const response = await api.post('/config/list');
    return response.data;
  },

  // 获取单个配置
  getConfiguration: async (name: string) => {
    const response = await api.post('/config/get', { name });
    return response.data;
  },

  // 删除配置
  deleteConfiguration: async (name: string) => {
    const response = await api.post('/config/delete', { name });
    return response.data;
  },

  // 获取角色列表
  getRoles: async () => {
    const response = await api.post<RoleResponse>('/roles/list', {});
    return response.data;
  },

  // 获取部署目标
  getDeployTargets: async () => {
    const response = await api.get<Record<string, DeployTarget>>('/deploy/targets');
    return response.data;
  },

  // 生成custom_modes.yaml
  generateCustomModes: async (request: DeployRequest) => {
    const response = await api.post('/deploy/generate', request);
    return response.data;
  },

  // 部署配置
  deployCustomModes: async (request: DeployRequest) => {
    const response = await api.post<DeployResponse>('/deploy/deploy', request);
    return response.data;
  },

  // 清空配置
  cleanupConfigurations: async (request: CleanupRequest) => {
    const response = await api.post<CleanupResponse>('/deploy/cleanup', request);
    return response.data;
  },

  // MCP API methods
  // 获取MCP服务器状态
  getMCPStatus: async () => {
    const response = await api.get<MCPStatusResponse>('/mcp/status');
    return response.data;
  },

  // 获取MCP工具分类
  getMCPCategories: async () => {
    const response = await api.get<MCPCategoriesResponse>('/mcp/categories');
    return response.data;
  },

  // 获取所有MCP工具
  getMCPTools: async () => {
    const response = await api.get<MCPToolsResponse>('/mcp/tools');
    return response.data;
  },

  // 根据分类获取MCP工具
  getMCPToolsByCategory: async (category: string) => {
    const response = await api.get<MCPToolsResponse>(`/mcp/tools/${category}`);
    return response.data;
  },

  // 获取单个MCP工具信息
  getMCPToolInfo: async (toolName: string) => {
    const response = await api.get<{ success: boolean; message: string; data: { tool: MCPToolInfo } }>(`/mcp/tools/info/${toolName}`);
    return response.data;
  },

  // 调用MCP工具
  callMCPTool: async (toolName: string, arguments_: any = {}) => {
    const response = await api.post('/mcp/call-tool', {
      name: toolName,
      arguments: arguments_
    });
    return response.data;
  },

  // 刷新MCP工具配置
  refreshMCPTools: async () => {
    const response = await api.post('/mcp/tools/refresh');
    return response.data;
  },

  // 启用MCP工具
  enableMCPTool: async (toolName: string) => {
    const response = await api.post('/mcp/tools/enable', { name: toolName });
    return response.data;
  },

  // 禁用MCP工具
  disableMCPTool: async (toolName: string) => {
    const response = await api.post('/mcp/tools/disable', { name: toolName });
    return response.data;
  },

  // 启用MCP工具分类
  enableMCPCategory: async (categoryId: string) => {
    const response = await api.post('/mcp/categories/enable', { id: categoryId });
    return response.data;
  },

  // 禁用MCP工具分类
  disableMCPCategory: async (categoryId: string) => {
    const response = await api.post('/mcp/categories/disable', { id: categoryId });
    return response.data;
  },

  // 获取分类配置
  getCategoryConfig: async (categoryId: string) => {
    const response = await api.get(`/mcp/categories/${categoryId}/config`);
    return response.data;
  },

  // 更新分类配置
  updateCategoryConfigs: async (categoryId: string, configs: any) => {
    const response = await api.put(`/mcp/categories/${categoryId}/config`, { config: configs });
    return response.data;
  },

  // File Security API methods
  // 获取文件安全配置信息
  getFileSecurityInfo: async (): Promise<FileSecurityResponse> => {
    const response = await api.get('/file-security/status');
    return response.data;
  },

  // 更新文件安全路径配置
  updateFileSecurityPaths: async (request: UpdatePathsRequest): Promise<SecurityActionResponse> => {
    const response = await api.put(`/file-security/paths/${request.config_type}`, {
      paths: request.paths
    });
    return response.data;
  },

  // 更新文件安全限制配置
  updateFileSecurityLimits: async (request: UpdateLimitsRequest): Promise<SecurityActionResponse> => {
    const response = await api.put(`/file-security/limits/${request.limit_type}`, {
      value: request.value
    });
    return response.data;
  },

  // 重新加载文件安全配置
  reloadFileSecurityConfig: async (): Promise<FileSecurityResponse> => {
    // 新的API架构下，配置会自动重新加载，所以只需要获取最新状态
    const response = await api.get('/file-security/status');
    return response.data;
  },

  // Recycle Bin API methods
  // 软删除项目
  softDeleteItem: async (request: SoftDeleteRequest): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/soft-delete', request);
    return response.data;
  },

  // 获取回收站项目列表
  getRecycleBinItems: async (options: {
    item_type?: RecycleBinItemType;
    include_expired?: boolean;
    limit?: number;
  } = {}): Promise<RecycleBinItem[]> => {
    const params = new URLSearchParams();
    if (options.item_type) params.append('item_type', options.item_type);
    if (options.include_expired !== undefined) params.append('include_expired', String(options.include_expired));
    if (options.limit) params.append('limit', String(options.limit));
    
    const response = await api.get(`/recycle-bin/items?${params}`);
    return response.data;
  },

  // 获取单个回收站项目
  getRecycleBinItem: async (recycleBinId: string): Promise<RecycleBinItem> => {
    const response = await api.get(`/recycle-bin/items/${recycleBinId}`);
    return response.data;
  },

  // 恢复回收站项目
  restoreRecycleBinItem: async (recycleBinId: string): Promise<RecycleBinResponse> => {
    const response = await api.post(`/recycle-bin/items/${recycleBinId}/restore`);
    return response.data;
  },

  // 永久删除回收站项目
  permanentDeleteRecycleBinItem: async (recycleBinId: string): Promise<RecycleBinResponse> => {
    const response = await api.delete(`/recycle-bin/items/${recycleBinId}`);
    return response.data;
  },

  // 批量恢复
  batchRestoreRecycleBinItems: async (recycleBinIds: string[]): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/batch-restore', recycleBinIds);
    return response.data;
  },

  // 批量永久删除
  batchDeleteRecycleBinItems: async (recycleBinIds: string[]): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/batch-delete', recycleBinIds);
    return response.data;
  },

  // 清空回收站
  emptyRecycleBin: async (force: boolean = false): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/empty', { force });
    return response.data;
  },

  // 清理过期项目
  cleanupExpiredItems: async (): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/cleanup');
    return response.data;
  },

  // 获取回收站统计
  getRecycleBinStatistics: async (): Promise<RecycleBinStatsResponse> => {
    const response = await api.get('/recycle-bin/statistics');
    return response.data;
  },

  // 获取调度器状态
  getRecycleBinSchedulerStatus: async (): Promise<RecycleBinResponse> => {
    const response = await api.get('/recycle-bin/scheduler/status');
    return response.data;
  },

  // 手动触发清理
  triggerManualCleanup: async (): Promise<RecycleBinResponse> => {
    const response = await api.post('/recycle-bin/scheduler/manual-cleanup');
    return response.data;
  },

  // 获取调度器统计信息
  getSchedulerStatistics: async (): Promise<RecycleBinResponse> => {
    const response = await api.get('/recycle-bin/scheduler/statistics');
    return response.data;
  },

  // Cache API methods
  // 获取缓存系统信息
  getCacheInfo: async () => {
    const response = await api.get('/cache/info');
    return response.data;
  },

  // 获取可用存储后端
  getCacheBackends: async () => {
    const response = await api.get('/cache/backends');
    return response.data;
  },

  // 切换存储后端
  switchCacheBackend: async (backend_type: string, backend_config?: any) => {
    const response = await api.post('/cache/switch-backend', {
      backend_type,
      backend_config
    });
    return response.data;
  },

  // 设置缓存值
  setCacheValue: async (key: string, value: any, ttl?: number) => {
    const response = await api.post('/cache/set', {
      key,
      value,
      ttl
    });
    return response.data;
  },

  // 获取缓存值
  getCacheValue: async (key: string) => {
    const response = await api.post('/cache/get', {
      key
    });
    return response.data;
  },

  // 删除缓存键
  deleteCacheKey: async (key: string) => {
    const response = await api.post('/cache/delete', {
      key
    });
    return response.data;
  },

  // 检查缓存键是否存在
  cacheKeyExists: async (key: string) => {
    const response = await api.post('/cache/exists', {
      key
    });
    return response.data;
  },

  // 获取缓存键的TTL
  getCacheKeyTTL: async (key: string) => {
    const response = await api.post('/cache/ttl', {
      key
    });
    return response.data;
  },

  // 获取匹配模式的缓存键列表
  getCacheKeys: async (pattern: string = '*') => {
    const response = await api.post('/cache/keys', {
      pattern
    });
    return response.data;
  },

  // 批量获取缓存值
  getCacheMultiple: async (keys: string[]) => {
    const response = await api.post('/cache/mget', {
      keys
    });
    return response.data;
  },

  // 批量设置缓存值
  setCacheMultiple: async (key_values: Record<string, any>, ttl?: number) => {
    const response = await api.post('/cache/mset', {
      key_values,
      ttl
    });
    return response.data;
  },

  // 递增缓存值
  incrementCacheValue: async (key: string, amount: number = 1) => {
    const response = await api.post('/cache/incr', {
      key,
      amount
    });
    return response.data;
  },

  // 清空所有缓存
  flushCache: async () => {
    const response = await api.post('/cache/flush');
    return response.data;
  },

  // 获取环境信息
  getEnvironmentInfo: async () => {
    const response = await api.get('/mcp/environment');
    return response.data;
  },

};

export default api;