/**
 * API 服务层
 * 统一管理所有 API 调用和数据获取逻辑
 * 使用 Axios 进行 HTTP 请求，支持拦截器和错误处理
 */

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios';
import { ApiResponse, User, Model, Configuration } from '@/types';

// API 基础配置
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:14001/api';
const API_TIMEOUT = 10000; // 10秒超时

/**
 * 创建 Axios 实例
 */
const createAxiosInstance = (): AxiosInstance => {
  const instance = axios.create({
    baseURL: API_BASE_URL,
    timeout: API_TIMEOUT,
    headers: {
      'Content-Type': 'application/json',
    },
  });

  // 请求拦截器
  instance.interceptors.request.use(
    config => {
      // 添加请求时间戳
      config.metadata = { startTime: Date.now() };

      // 可在此处添加认证令牌
      // const token = localStorage.getItem('auth_token');
      // if (token) {
      //   config.headers.Authorization = `Bearer ${token}`;
      // }

      console.log(`[API Request] ${config.method?.toUpperCase()} ${config.url}`);
      return config;
    },
    error => {
      console.error('[API Request Error]', error);
      return Promise.reject(error);
    }
  );

  // 响应拦截器
  instance.interceptors.response.use(
    (response: AxiosResponse) => {
      // 计算请求耗时
      const endTime = Date.now();
      const startTime = response.config.metadata?.startTime || endTime;
      const duration = endTime - startTime;

      console.log(
        `[API Response] ${response.config.method?.toUpperCase()} ${response.config.url} - ${duration}ms`
      );
      return response;
    },
    error => {
      // 统一错误处理
      console.error('[API Response Error]', error);

      if (error.response) {
        // 服务器响应错误
        const { status, data } = error.response;
        throw new ApiError(data?.message || `HTTP ${status} Error`, status, data);
      } else if (error.request) {
        // 网络错误
        throw new ApiError('Network Error', 0, { originalError: error });
      } else {
        // 其他错误
        throw new ApiError(error.message || 'Unknown Error', -1, { originalError: error });
      }
    }
  );

  return instance;
};

/**
 * 自定义 API 错误类
 */
export class ApiError extends Error {
  constructor(
    message: string,
    public status: number,
    public data?: any
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

/**
 * API 客户端实例
 */
const apiClient = createAxiosInstance();

/**
 * 通用请求方法
 */
const request = async <T = any>(config: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  try {
    const response = await apiClient.request<ApiResponse<T>>(config);
    return response.data;
  } catch (error) {
    if (error instanceof ApiError) {
      throw error;
    }
    throw new ApiError(error instanceof Error ? error.message : 'Unknown Error', -1, {
      originalError: error,
    });
  }
};

/**
 * GET 请求
 */
const get = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ method: 'GET', url, ...config });
};

/**
 * POST 请求
 */
const post = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return request<T>({ method: 'POST', url, data, ...config });
};

/**
 * PUT 请求
 */
const put = async <T = any>(
  url: string,
  data?: any,
  config?: AxiosRequestConfig
): Promise<ApiResponse<T>> => {
  return request<T>({ method: 'PUT', url, data, ...config });
};

/**
 * DELETE 请求
 */
const del = async <T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> => {
  return request<T>({ method: 'DELETE', url, ...config });
};

/**
 * 健康检查 API
 */
export const healthApi = {
  /**
   * 获取服务健康状态
   */
  check: () => get<{ status: string; timestamp: string }>('/health'),

  /**
   * 获取系统信息
   */
  info: () =>
    get<{
      version: string;
      environment: string;
      uptime: number;
    }>('/info'),
};

/**
 * 通用 API
 */
export const commonApi = {
  /**
   * Hello World API
   */
  hello: () => get<{ message: string; timestamp: string }>('/hello'),

  /**
   * 获取所有模型配置
   */
  getModels: () => get<Model[]>('/models'),

  /**
   * 获取特定模型配置
   */
  getModel: (modelId: string) => get<Model>(`/models/${modelId}`),

  /**
   * 创建新的模型配置
   */
  createModel: (model: Omit<Model, 'id' | 'created_at' | 'updated_at'>) =>
    post<Model>('/models', model),

  /**
   * 更新模型配置
   */
  updateModel: (modelId: string, updates: Partial<Model>) =>
    put<Model>(`/models/${modelId}`, updates),

  /**
   * 删除模型配置
   */
  deleteModel: (modelId: string) => del<{ success: boolean }>(`/models/${modelId}`),
};

/**
 * 配置管理 API
 */
export const configApi = {
  /**
   * 获取所有配置
   */
  getConfigurations: () => get<Configuration[]>('/configurations'),

  /**
   * 获取特定配置
   */
  getConfiguration: (configId: string) => get<Configuration>(`/configurations/${configId}`),

  /**
   * 创建新配置
   */
  createConfiguration: (config: Omit<Configuration, 'id' | 'created_at' | 'updated_at'>) =>
    post<Configuration>('/configurations', config),

  /**
   * 更新配置
   */
  updateConfiguration: (configId: string, updates: Partial<Configuration>) =>
    put<Configuration>(`/configurations/${configId}`, updates),

  /**
   * 删除配置
   */
  deleteConfiguration: (configId: string) =>
    del<{ success: boolean }>(`/configurations/${configId}`),

  /**
   * 导出配置
   */
  exportConfiguration: (configId: string) =>
    get<{ data: string; filename: string }>(`/configurations/${configId}/export`),

  /**
   * 导入配置
   */
  importConfiguration: (file: File) => {
    const formData = new FormData();
    formData.append('file', file);
    return post<Configuration>('/configurations/import', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
  },
};

/**
 * 用户管理 API
 */
export const userApi = {
  /**
   * 获取当前用户信息
   */
  getCurrentUser: () => get<User>('/user/me'),

  /**
   * 更新用户信息
   */
  updateUser: (updates: Partial<User>) => put<User>('/user/me', updates),

  /**
   * 获取用户偏好设置
   */
  getPreferences: () => get<Record<string, any>>('/user/preferences'),

  /**
   * 更新用户偏好设置
   */
  updatePreferences: (preferences: Record<string, any>) =>
    put<Record<string, any>>('/user/preferences', preferences),
};

/**
 * 文件上传 API
 */
export const uploadApi = {
  /**
   * 上传单个文件
   */
  uploadFile: (file: File, onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    formData.append('file', file);

    return post<{
      filename: string;
      size: number;
      url: string;
    }>('/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  },

  /**
   * 上传多个文件
   */
  uploadFiles: (files: File[], onProgress?: (progress: number) => void) => {
    const formData = new FormData();
    files.forEach((file, index) => {
      formData.append(`files[${index}]`, file);
    });

    return post<{
      files: Array<{
        filename: string;
        size: number;
        url: string;
      }>;
    }>('/upload/multiple', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: progressEvent => {
        if (onProgress && progressEvent.total) {
          const progress = Math.round((progressEvent.loaded * 100) / progressEvent.total);
          onProgress(progress);
        }
      },
    });
  },
};

/**
 * WebSocket 连接管理
 */
export class WebSocketManager {
  private ws: WebSocket | null = null;
  private reconnectAttempts = 0;
  private maxReconnectAttempts = 5;
  private reconnectDelay = 1000;
  private listeners = new Map<string, Set<Function>>();

  constructor(private url: string = 'ws://localhost:14001/ws') {}

  /**
   * 连接 WebSocket
   */
  connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(this.url);

        this.ws.onopen = () => {
          console.log('[WebSocket] Connected');
          this.reconnectAttempts = 0;
          resolve();
        };

        this.ws.onmessage = event => {
          try {
            const data = JSON.parse(event.data);
            this.emit(data.type || 'message', data);
          } catch (error) {
            console.error('[WebSocket] Message parse error:', error);
          }
        };

        this.ws.onclose = () => {
          console.log('[WebSocket] Disconnected');
          this.handleReconnect();
        };

        this.ws.onerror = error => {
          console.error('[WebSocket] Error:', error);
          reject(error);
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  /**
   * 发送消息
   */
  send(type: string, data: any): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ type, data }));
    } else {
      console.warn('[WebSocket] Cannot send message, not connected');
    }
  }

  /**
   * 监听事件
   */
  on(event: string, callback: Function): void {
    if (!this.listeners.has(event)) {
      this.listeners.set(event, new Set());
    }
    this.listeners.get(event)!.add(callback);
  }

  /**
   * 取消监听
   */
  off(event: string, callback: Function): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.delete(callback);
    }
  }

  /**
   * 触发事件
   */
  private emit(event: string, data: any): void {
    const listeners = this.listeners.get(event);
    if (listeners) {
      listeners.forEach(callback => callback(data));
    }
  }

  /**
   * 处理重连
   */
  private handleReconnect(): void {
    if (this.reconnectAttempts < this.maxReconnectAttempts) {
      this.reconnectAttempts++;
      console.log(
        `[WebSocket] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`
      );

      setTimeout(() => {
        this.connect().catch(error => {
          console.error('[WebSocket] Reconnect failed:', error);
        });
      }, this.reconnectDelay * this.reconnectAttempts);
    } else {
      console.error('[WebSocket] Max reconnection attempts reached');
    }
  }
}

// 导出 WebSocket 实例
export const wsManager = new WebSocketManager();

// 导出所有 API 方法
export const api = {
  health: healthApi,
  common: commonApi,
  config: configApi,
  user: userApi,
  upload: uploadApi,
};

// 类型扩展
declare module 'axios' {
  export interface AxiosRequestConfig {
    metadata?: {
      startTime: number;
    };
  }
}

export default api;
