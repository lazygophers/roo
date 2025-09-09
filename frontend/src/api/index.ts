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
}

export interface ModelsResponse {
  success: boolean;
  message: string;
  data: ModelInfo[];
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
  last_modified: string;
}

export interface CommandsResponse {
  success: boolean;
  message: string;
  data: FileMetadata[];
  total: number;
}

export interface RulesResponse {
  success: boolean;
  message: string;
  data: FileMetadata[];
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
    const response = await api.get(`/config/${name}`);
    return response.data;
  },

  // 删除配置
  deleteConfiguration: async (name: string) => {
    const response = await api.delete(`/config/${name}`);
    return response.data;
  }
};

export default api;