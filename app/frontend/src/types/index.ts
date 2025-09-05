/**
 * TypeScript 类型定义
 * 集中管理所有应用程序的类型定义
 * 确保类型安全和一致性
 */

// ===== 基础类型定义 =====

/**
 * 通用 API 响应结构
 */
export interface ApiResponse<T = any> {
  data: T;
  success: boolean;
  message?: string;
  error?: string;
  timestamp?: string;
}

/**
 * 分页查询参数
 */
export interface PaginationParams {
  page: number;
  pageSize: number;
  total?: number;
}

/**
 * 分页响应结构
 */
export interface PaginationResponse<T = any> {
  items: T[];
  pagination: {
    current: number;
    pageSize: number;
    total: number;
    totalPages: number;
    hasNext: boolean;
    hasPrevious: boolean;
  };
}

/**
 * 排序参数
 */
export interface SortParams {
  field: string;
  order: 'asc' | 'desc';
}

/**
 * 通用查询参数
 */
export interface QueryParams extends Partial<PaginationParams>, Partial<SortParams> {
  search?: string;
  filters?: Record<string, any>;
}

// ===== 业务实体类型 =====

/**
 * 用户信息
 */
export interface User {
  id: string;
  username: string;
  email: string;
  displayName?: string;
  avatar?: string;
  role: UserRole;
  permissions: Permission[];
  preferences: UserPreferences;
  isActive: boolean;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * 用户角色
 */
export enum UserRole {
  ADMIN = 'admin',
  USER = 'user',
  GUEST = 'guest',
}

/**
 * 用户权限
 */
export interface Permission {
  id: string;
  name: string;
  description?: string;
  resource: string;
  actions: string[];
}

/**
 * 用户偏好设置
 */
export interface UserPreferences {
  theme: ThemeType;
  language: string;
  timezone: string;
  dateFormat: string;
  notifications: NotificationSettings;
  layout: LayoutSettings;
}

/**
 * 通知设置
 */
export interface NotificationSettings {
  email: boolean;
  push: boolean;
  inApp: boolean;
  frequency: 'immediate' | 'daily' | 'weekly' | 'never';
}

/**
 * 布局设置
 */
export interface LayoutSettings {
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  showHeader: boolean;
  showFooter: boolean;
  compactMode: boolean;
}

/**
 * 模型配置
 */
export interface Model {
  id: string;
  name: string;
  displayName: string;
  description?: string;
  version: string;
  type: ModelType;
  status: ModelStatus;
  config: ModelConfig;
  metadata: ModelMetadata;
  tags: string[];
  isActive: boolean;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * 模型类型
 */
export enum ModelType {
  LANGUAGE_MODEL = 'language_model',
  EMBEDDING_MODEL = 'embedding_model',
  CHAT_MODEL = 'chat_model',
  COMPLETION_MODEL = 'completion_model',
}

/**
 * 模型状态
 */
export enum ModelStatus {
  ACTIVE = 'active',
  INACTIVE = 'inactive',
  DEPRECATED = 'deprecated',
  EXPERIMENTAL = 'experimental',
}

/**
 * 模型配置
 */
export interface ModelConfig {
  apiKey?: string;
  baseUrl?: string;
  maxTokens?: number;
  temperature?: number;
  topP?: number;
  frequencyPenalty?: number;
  presencePenalty?: number;
  timeout?: number;
  retries?: number;
  customHeaders?: Record<string, string>;
  customParameters?: Record<string, any>;
}

/**
 * 模型元数据
 */
export interface ModelMetadata {
  provider: string;
  family: string;
  capabilities: string[];
  supportedLanguages: string[];
  contextWindow: number;
  pricing?: {
    inputTokens: number;
    outputTokens: number;
    currency: string;
  };
  performance?: {
    latency: number;
    throughput: number;
    accuracy: number;
  };
}

/**
 * 配置
 */
export interface Configuration {
  id: string;
  name: string;
  displayName: string;
  description?: string;
  type: ConfigurationType;
  category: string;
  content: ConfigurationContent;
  schema?: ConfigurationSchema;
  validation?: ConfigurationValidation;
  tags: string[];
  isActive: boolean;
  isReadonly: boolean;
  version: string;
  createdBy: string;
  createdAt: string;
  updatedAt: string;
}

/**
 * 配置类型
 */
export enum ConfigurationType {
  APPLICATION = 'application',
  MODEL = 'model',
  USER = 'user',
  SYSTEM = 'system',
}

/**
 * 配置内容
 */
export type ConfigurationContent = Record<string, any>;

/**
 * 配置 Schema
 */
export interface ConfigurationSchema {
  type: 'object';
  properties: Record<string, ConfigurationSchemaProperty>;
  required?: string[];
  additionalProperties?: boolean;
}

/**
 * 配置 Schema 属性
 */
export interface ConfigurationSchemaProperty {
  type: 'string' | 'number' | 'boolean' | 'array' | 'object';
  description?: string;
  default?: any;
  enum?: any[];
  minimum?: number;
  maximum?: number;
  pattern?: string;
  format?: string;
  items?: ConfigurationSchemaProperty;
  properties?: Record<string, ConfigurationSchemaProperty>;
}

/**
 * 配置验证规则
 */
export interface ConfigurationValidation {
  rules: ValidationRule[];
  strictMode: boolean;
}

/**
 * 验证规则
 */
export interface ValidationRule {
  field: string;
  type: 'required' | 'format' | 'range' | 'custom';
  message: string;
  params?: Record<string, any>;
}

// ===== UI 相关类型 =====

/**
 * 主题类型
 */
export enum ThemeType {
  LIGHT = 'light',
  DARK = 'dark',
  AUTO = 'auto',
}

/**
 * 主题配置
 */
export interface ThemeConfig {
  type: ThemeType;
  primaryColor: string;
  borderRadius: number;
  fontSize: number;
  fontFamily: string;
  customColors?: Record<string, string>;
  customVariables?: Record<string, string>;
}

/**
 * 导航菜单项
 */
export interface MenuItem {
  key: string;
  label: string;
  icon?: React.ReactNode;
  path?: string;
  children?: MenuItem[];
  disabled?: boolean;
  hidden?: boolean;
  badge?: string | number;
  permissions?: string[];
}

/**
 * 面包屑项
 */
export interface BreadcrumbItem {
  title: string;
  path?: string;
  icon?: React.ReactNode;
}

/**
 * 表格列配置
 */
export interface TableColumn<T = any> {
  key: string;
  title: string;
  dataIndex?: string;
  width?: number | string;
  align?: 'left' | 'center' | 'right';
  sorter?: boolean | ((a: T, b: T) => number);
  filters?: FilterOption[];
  render?: (value: any, record: T, index: number) => React.ReactNode;
  fixed?: 'left' | 'right';
  ellipsis?: boolean;
  hidden?: boolean;
}

/**
 * 筛选选项
 */
export interface FilterOption {
  text: string;
  value: any;
}

/**
 * 表单字段配置
 */
export interface FormField {
  name: string;
  label: string;
  type: FormFieldType;
  required?: boolean;
  disabled?: boolean;
  hidden?: boolean;
  placeholder?: string;
  helpText?: string;
  validation?: FormFieldValidation[];
  options?: FormFieldOption[];
  dependencies?: string[];
  defaultValue?: any;
}

/**
 * 表单字段类型
 */
export enum FormFieldType {
  TEXT = 'text',
  TEXTAREA = 'textarea',
  NUMBER = 'number',
  EMAIL = 'email',
  PASSWORD = 'password',
  URL = 'url',
  SELECT = 'select',
  MULTISELECT = 'multiselect',
  RADIO = 'radio',
  CHECKBOX = 'checkbox',
  SWITCH = 'switch',
  SLIDER = 'slider',
  DATE = 'date',
  DATETIME = 'datetime',
  TIME = 'time',
  FILE = 'file',
  JSON = 'json',
}

/**
 * 表单字段选项
 */
export interface FormFieldOption {
  label: string;
  value: any;
  disabled?: boolean;
  icon?: React.ReactNode;
}

/**
 * 表单字段验证
 */
export interface FormFieldValidation {
  type: 'required' | 'min' | 'max' | 'pattern' | 'custom';
  value?: any;
  message: string;
}

// ===== 状态管理类型 =====

/**
 * 应用状态
 */
export interface AppState {
  user: UserState;
  theme: ThemeState;
  ui: UIState;
  data: DataState;
}

/**
 * 用户状态
 */
export interface UserState {
  currentUser: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  permissions: Permission[];
  preferences: UserPreferences;
}

/**
 * 主题状态
 */
export interface ThemeState {
  current: ThemeType;
  config: ThemeConfig;
  isDark: boolean;
  isAuto: boolean;
}

/**
 * UI 状态
 */
export interface UIState {
  sidebarCollapsed: boolean;
  loading: Record<string, boolean>;
  notifications: Notification[];
  modal: ModalState;
  drawer: DrawerState;
}

/**
 * 数据状态
 */
export interface DataState {
  models: Model[];
  configurations: Configuration[];
  cache: Record<string, any>;
  lastUpdated: Record<string, string>;
}

/**
 * 通知
 */
export interface Notification {
  id: string;
  type: 'success' | 'error' | 'warning' | 'info';
  title: string;
  message?: string;
  duration?: number;
  actions?: NotificationAction[];
  createdAt: string;
  read?: boolean;
}

/**
 * 通知操作
 */
export interface NotificationAction {
  label: string;
  action: () => void;
  type?: 'primary' | 'default' | 'link';
}

/**
 * 模态框状态
 */
export interface ModalState {
  visible: boolean;
  type?: string;
  title?: string;
  content?: React.ReactNode;
  props?: Record<string, any>;
}

/**
 * 抽屉状态
 */
export interface DrawerState {
  visible: boolean;
  type?: string;
  title?: string;
  content?: React.ReactNode;
  placement?: 'left' | 'right' | 'top' | 'bottom';
  props?: Record<string, any>;
}

// ===== Hook 类型 =====

/**
 * API Hook 返回类型
 */
export interface UseApiResult<T = any> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  refetch: () => Promise<void>;
}

/**
 * 异步操作 Hook 返回类型
 */
export interface UseAsyncResult<T = any, P extends any[] = any[]> {
  data: T | null;
  loading: boolean;
  error: Error | null;
  execute: (...args: P) => Promise<T>;
  reset: () => void;
}

/**
 * 分页 Hook 返回类型
 */
export interface UsePaginationResult<T = any> {
  data: T[];
  pagination: PaginationParams & { total: number };
  loading: boolean;
  error: Error | null;
  changePage: (page: number) => void;
  changePageSize: (pageSize: number) => void;
  refetch: () => Promise<void>;
}

// ===== 工具类型 =====

/**
 * 可选属性
 */
export type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>;

/**
 * 必填属性
 */
export type Required<T, K extends keyof T> = T & Required<Pick<T, K>>;

/**
 * 深度可选
 */
export type DeepPartial<T> = {
  [P in keyof T]?: T[P] extends object ? DeepPartial<T[P]> : T[P];
};

/**
 * 深度必填
 */
export type DeepRequired<T> = {
  [P in keyof T]-?: T[P] extends object ? DeepRequired<T[P]> : T[P];
};

/**
 * 键值对
 */
export type KeyValuePair<K extends string | number | symbol = string, V = any> = Record<K, V>;

/**
 * 函数类型
 */
export type AnyFunction = (...args: any[]) => any;

/**
 * 异步函数类型
 */
export type AsyncFunction<T = any, P extends any[] = any[]> = (...args: P) => Promise<T>;

/**
 * 事件处理函数类型
 */
export type EventHandler<T = any> = (event: T) => void;

/**
 * 回调函数类型
 */
export type Callback<T = void, P extends any[] = any[]> = (...args: P) => T;

// ===== 常量类型 =====

/**
 * HTTP 方法
 */
export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH',
  HEAD = 'HEAD',
  OPTIONS = 'OPTIONS',
}

/**
 * HTTP 状态码
 */
export enum HttpStatus {
  OK = 200,
  CREATED = 201,
  NO_CONTENT = 204,
  BAD_REQUEST = 400,
  UNAUTHORIZED = 401,
  FORBIDDEN = 403,
  NOT_FOUND = 404,
  INTERNAL_SERVER_ERROR = 500,
}

/**
 * 存储键名
 */
export enum StorageKey {
  AUTH_TOKEN = 'auth_token',
  USER_PREFERENCES = 'user_preferences',
  THEME_CONFIG = 'theme_config',
  SIDEBAR_STATE = 'sidebar_state',
  LANGUAGE = 'language',
  RECENT_SEARCHES = 'recent_searches',
}

/**
 * 路由路径
 */
export enum RoutePath {
  HOME = '/',
  CONFIG = '/config',
  ABOUT = '/about',
  NOT_FOUND = '/404',
  LOGIN = '/login',
  LOGOUT = '/logout',
}

/**
 * 事件类型
 */
export enum EventType {
  USER_LOGIN = 'user:login',
  USER_LOGOUT = 'user:logout',
  THEME_CHANGE = 'theme:change',
  CONFIG_UPDATE = 'config:update',
  MODEL_UPDATE = 'model:update',
  NOTIFICATION_ADD = 'notification:add',
  NOTIFICATION_REMOVE = 'notification:remove',
}

// ===== 导出所有类型 =====
export * from './api';
export * from './ui';
export * from './utils';

// 默认导出
export default {
  // 可以在这里添加默认导出的类型或常量
};
