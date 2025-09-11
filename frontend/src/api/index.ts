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
  database_summary?: any;
}

export interface FileSecurityResponse {
  success: boolean;
  message: string;
  data: FileSecurityInfo;
}

export interface UpdatePathsRequest {
  config_type: 'readable' | 'writable' | 'deletable' | 'forbidden';
  paths: string[];
}

export interface UpdateLimitsRequest {
  limit_type: 'max_file_size' | 'max_read_lines' | 'strict_mode';
  value: number | boolean;
}

export interface SecurityActionResponse {
  success: boolean;
  message: string;
  data?: any;
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

  // File Security API methods
  // 获取文件安全配置信息
  getFileSecurityInfo: async () => {
    const response = await api.post('/mcp/call-tool', {
      name: 'get_file_security_info',
      arguments: {}
    });
    return response.data;
  },

  // 更新文件安全路径配置
  updateFileSecurityPaths: async (request: UpdatePathsRequest) => {
    const response = await api.post('/mcp/call-tool', {
      name: 'update_file_security_paths',
      arguments: request
    });
    return response.data;
  },

  // 更新文件安全限制配置
  updateFileSecurityLimits: async (request: UpdateLimitsRequest) => {
    const response = await api.post('/mcp/call-tool', {
      name: 'update_file_security_limits',
      arguments: request
    });
    return response.data;
  },

  // 重新加载文件安全配置
  reloadFileSecurityConfig: async () => {
    const response = await api.post('/mcp/call-tool', {
      name: 'reload_file_security_config',
      arguments: {}
    });
    return response.data;
  }
};

export default api;