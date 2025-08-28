// API 配置
export const API_CONFIG = {
  // 基础URL，根据环境自动切换
  baseURL: process.env.NODE_ENV === 'production' ? '' : '',
  
  // 超时设置
  timeout: 10000,
  
  // 重试次数
  retryCount: 3,
  
  // 请求头
  headers: {
    'Content-Type': 'application/json',
  }
}

// API 端点
export const API_ENDPOINTS = {
  models: '/api/models',
  rules: (slug: string) => `/api/rules/${slug}`,
  modelDetails: (slug: string) => `/api/models/${slug}`,
  roles: '/api/roles',
  commands: '/api/commands',
  hooks: {
    before: '/api/hooks/before',
    after: '/api/hooks/after'
  }
}