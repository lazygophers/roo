/**
 * 工具函数集合
 * Utility Functions Collection
 *
 * 提供通用的工具函数，包括：
 * - 格式化函数
 * - 验证函数
 * - 日期时间处理
 * - 本地存储管理
 * - 深拷贝工具
 * - 防抖节流
 * - 错误处理
 */

// ===== 导入 =====
import type { ThemeConfig } from '@/types';

// ===== 格式化函数 =====

/**
 * 格式化文件大小
 * @param bytes 字节数
 * @param decimals 小数位数
 * @returns 格式化后的文件大小字符串
 */
export function formatFileSize(bytes: number, decimals: number = 2): string {
  if (bytes === 0) return '0 Bytes';

  const k = 1024;
  const dm = decimals < 0 ? 0 : decimals;
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB'];

  const i = Math.floor(Math.log(bytes) / Math.log(k));

  return parseFloat((bytes / Math.pow(k, i)).toFixed(dm)) + ' ' + sizes[i];
}

/**
 * 格式化数字
 * @param num 要格式化的数字
 * @param locale 地区设置，默认为中文
 * @returns 格式化后的数字字符串
 */
export function formatNumber(num: number, locale: string = 'zh-CN'): string {
  return new Intl.NumberFormat(locale).format(num);
}

/**
 * 格式化货币
 * @param amount 金额
 * @param currency 货币代码
 * @param locale 地区设置
 * @returns 格式化后的货币字符串
 */
export function formatCurrency(
  amount: number,
  currency: string = 'CNY',
  locale: string = 'zh-CN'
): string {
  return new Intl.NumberFormat(locale, {
    style: 'currency',
    currency: currency,
  }).format(amount);
}

/**
 * 格式化百分比
 * @param value 数值（0-1）
 * @param decimals 小数位数
 * @returns 格式化后的百分比字符串
 */
export function formatPercentage(value: number, decimals: number = 2): string {
  return `${(value * 100).toFixed(decimals)}%`;
}

/**
 * 格式化日期时间
 * @param date 日期对象或时间戳
 * @param format 格式化模式
 * @param locale 地区设置
 * @returns 格式化后的日期时间字符串
 */
export function formatDateTime(
  date: Date | number | string,
  format: 'short' | 'medium' | 'long' | 'full' = 'medium',
  locale: string = 'zh-CN'
): string {
  const dateObj =
    typeof date === 'string' ? new Date(date) : date instanceof Date ? date : new Date(date);

  const options: Intl.DateTimeFormatOptions = {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit',
    hour12: false,
  };

  switch (format) {
    case 'short':
      return dateObj.toLocaleDateString(locale);
    case 'long':
      options.weekday = 'long';
      options.month = 'long';
      break;
    case 'full':
      options.weekday = 'long';
      options.month = 'long';
      options.timeZoneName = 'short';
      break;
  }

  return dateObj.toLocaleString(locale, options);
}

/**
 * 格式化相对时间
 * @param date 日期对象或时间戳
 * @returns 相对时间字符串（如：5分钟前）
 */
export function formatRelativeTime(date: Date | number | string): string {
  const dateObj =
    typeof date === 'string' ? new Date(date) : date instanceof Date ? date : new Date(date);
  const now = new Date();
  const diff = now.getTime() - dateObj.getTime();

  const minute = 60 * 1000;
  const hour = minute * 60;
  const day = hour * 24;
  const week = day * 7;
  const month = day * 30;
  const year = day * 365;

  const absDiff = Math.abs(diff);

  if (absDiff < minute) {
    return '刚刚';
  } else if (absDiff < hour) {
    return `${Math.floor(absDiff / minute)}分钟前`;
  } else if (absDiff < day) {
    return `${Math.floor(absDiff / hour)}小时前`;
  } else if (absDiff < week) {
    return `${Math.floor(absDiff / day)}天前`;
  } else if (absDiff < month) {
    return `${Math.floor(absDiff / week)}周前`;
  } else if (absDiff < year) {
    return `${Math.floor(absDiff / month)}个月前`;
  } else {
    return `${Math.floor(absDiff / year)}年前`;
  }
}

// ===== 验证函数 =====

/**
 * 验证邮箱格式
 * @param email 邮箱地址
 * @returns 是否为有效邮箱
 */
export function isValidEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  return emailRegex.test(email);
}

/**
 * 验证手机号格式（中国大陆）
 * @param phone 手机号
 * @returns 是否为有效手机号
 */
export function isValidPhone(phone: string): boolean {
  const phoneRegex = /^1[3-9]\d{9}$/;
  return phoneRegex.test(phone);
}

/**
 * 验证URL格式
 * @param url URL地址
 * @returns 是否为有效URL
 */
export function isValidUrl(url: string): boolean {
  try {
    new URL(url);
    return true;
  } catch {
    return false;
  }
}

/**
 * 验证JSON格式
 * @param str JSON字符串
 * @returns 是否为有效JSON
 */
export function isValidJson(str: string): boolean {
  try {
    JSON.parse(str);
    return true;
  } catch {
    return false;
  }
}

/**
 * 验证密码强度
 * @param password 密码
 * @returns 密码强度评分（0-4）
 */
export function getPasswordStrength(password: string): number {
  let strength = 0;

  if (password.length >= 8) strength++;
  if (password.length >= 12) strength++;
  if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
  if (/[0-9]/.test(password)) strength++;
  if (/[^a-zA-Z0-9]/.test(password)) strength++;

  return strength;
}

// ===== 日期时间处理 =====

/**
 * 获取当前时间戳
 * @returns 当前时间戳（毫秒）
 */
export function getCurrentTimestamp(): number {
  return Date.now();
}

/**
 * 时间戳转日期对象
 * @param timestamp 时间戳
 * @returns 日期对象
 */
export function timestampToDate(timestamp: number): Date {
  return new Date(timestamp);
}

/**
 * 日期对象转时间戳
 * @param date 日期对象
 * @returns 时间戳（毫秒）
 */
export function dateToTimestamp(date: Date): number {
  return date.getTime();
}

/**
 * 添加天数
 * @param date 日期对象
 * @param days 要添加的天数
 * @returns 新的日期对象
 */
export function addDays(date: Date, days: number): Date {
  const result = new Date(date);
  result.setDate(result.getDate() + days);
  return result;
}

/**
 * 添加小时
 * @param date 日期对象
 * @param hours 要添加的小时数
 * @returns 新的日期对象
 */
export function addHours(date: Date, hours: number): Date {
  const result = new Date(date);
  result.setHours(result.getHours() + hours);
  return result;
}

/**
 * 获取日期范围
 * @param startDate 开始日期
 * @param endDate 结束日期
 * @returns 日期范围内的日期数组
 */
export function getDateRange(startDate: Date, endDate: Date): Date[] {
  const dates: Date[] = [];
  const currentDate = new Date(startDate);

  while (currentDate <= endDate) {
    dates.push(new Date(currentDate));
    currentDate.setDate(currentDate.getDate() + 1);
  }

  return dates;
}

/**
 * 获取本周开始日期
 * @returns 本周开始日期（周一）
 */
export function getWeekStart(): Date {
  const now = new Date();
  const day = now.getDay();
  const diff = now.getDate() - day + (day === 0 ? -6 : 1); // 调整到周一
  return new Date(now.setDate(diff));
}

/**
 * 获取本周结束日期
 * @returns 本周结束日期（周日）
 */
export function getWeekEnd(): Date {
  const weekStart = getWeekStart();
  return addDays(weekStart, 6);
}

/**
 * 获取本月开始日期
 * @returns 本月开始日期
 */
export function getMonthStart(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth(), 1);
}

/**
 * 获取本月结束日期
 * @returns 本月结束日期
 */
export function getMonthEnd(): Date {
  const now = new Date();
  return new Date(now.getFullYear(), now.getMonth() + 1, 0);
}

// ===== 本地存储管理 =====

/**
 * 获取本地存储值
 * @param key 存储键
 * @returns 存储值
 */
export function getLocalStorage<T>(key: string): T | null {
  try {
    const item = localStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error('Error getting localStorage item:', error);
    return null;
  }
}

/**
 * 设置本地存储值
 * @param key 存储键
 * @param value 存储值
 */
export function setLocalStorage<T>(key: string, value: T): void {
  try {
    localStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error setting localStorage item:', error);
  }
}

/**
 * 删除本地存储值
 * @param key 存储键
 */
export function removeLocalStorage(key: string): void {
  try {
    localStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing localStorage item:', error);
  }
}

/**
 * 清空本地存储
 */
export function clearLocalStorage(): void {
  try {
    localStorage.clear();
  } catch (error) {
    console.error('Error clearing localStorage:', error);
  }
}

/**
 * 获取会话存储值
 * @param key 存储键
 * @returns 存储值
 */
export function getSessionStorage<T>(key: string): T | null {
  try {
    const item = sessionStorage.getItem(key);
    return item ? JSON.parse(item) : null;
  } catch (error) {
    console.error('Error getting sessionStorage item:', error);
    return null;
  }
}

/**
 * 设置会话存储值
 * @param key 存储键
 * @param value 存储值
 */
export function setSessionStorage<T>(key: string, value: T): void {
  try {
    sessionStorage.setItem(key, JSON.stringify(value));
  } catch (error) {
    console.error('Error setting sessionStorage item:', error);
  }
}

/**
 * 删除会话存储值
 * @param key 存储键
 */
export function removeSessionStorage(key: string): void {
  try {
    sessionStorage.removeItem(key);
  } catch (error) {
    console.error('Error removing sessionStorage item:', error);
  }
}

// ===== 深拷贝工具 =====

/**
 * 深拷贝对象
 * @param obj 要拷贝的对象
 * @returns 拷贝后的新对象
 */
export function deepClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  if (obj instanceof Date) {
    return new Date(obj.getTime()) as T;
  }

  if (obj instanceof RegExp) {
    return new RegExp(obj) as T;
  }

  if (obj instanceof Map) {
    const map = new Map();
    obj.forEach((value, key) => {
      map.set(key, deepClone(value));
    });
    return map as T;
  }

  if (obj instanceof Set) {
    const set = new Set();
    obj.forEach(value => {
      set.add(deepClone(value));
    });
    return set as T;
  }

  if (Array.isArray(obj)) {
    return obj.map(item => deepClone(item)) as T;
  }

  const clonedObj = {} as T;
  Object.keys(obj).forEach(key => {
    clonedObj[key as keyof T] = deepClone(obj[key as keyof T]);
  });

  return clonedObj;
}

/**
 * 浅拷贝对象
 * @param obj 要拷贝的对象
 * @returns 拷贝后的新对象
 */
export function shallowClone<T>(obj: T): T {
  if (obj === null || typeof obj !== 'object') {
    return obj;
  }

  return { ...obj };
}

/**
 * 合并对象
 * @param target 目标对象
 * @param sources 源对象数组
 * @returns 合并后的对象
 */
export function mergeObjects<T>(target: T, ...sources: Partial<T>[]): T {
  return Object.assign({}, target, ...sources);
}

// ===== 防抖节流 =====

/**
 * 防抖函数
 * @param func 要防抖的函数
 * @param delay 延迟时间（毫秒）
 * @returns 防抖后的函数
 */
export function debounce<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let timeoutId: NodeJS.Timeout | null = null;

  return (...args: Parameters<T>) => {
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    timeoutId = setTimeout(() => {
      func(...args);
    }, delay);
  };
}

/**
 * 节流函数
 * @param func 要节流的函数
 * @param delay 延迟时间（毫秒）
 * @returns 节流后的函数
 */
export function throttle<T extends (...args: any[]) => any>(
  func: T,
  delay: number
): (...args: Parameters<T>) => void {
  let lastCallTime = 0;

  return (...args: Parameters<T>) => {
    const now = Date.now();

    if (now - lastCallTime >= delay) {
      func(...args);
      lastCallTime = now;
    }
  };
}

/**
 * 一次性函数
 * @param func 要执行的函数
 * @returns 一次性函数
 */
export function once<T extends (...args: any[]) => any>(func: T): (...args: Parameters<T>) => void {
  let executed = false;

  return (...args: Parameters<T>) => {
    if (!executed) {
      func(...args);
      executed = true;
    }
  };
}

// ===== 错误处理 =====

/**
 * 创建错误对象
 * @param message 错误消息
 * @param code 错误代码
 * @param details 错误详情
 * @returns 错误对象
 */
export function createError(message: string, code: string = 'UNKNOWN_ERROR', details?: any): Error {
  const error = new Error(message);
  error.name = 'AppError';
  (error as any).code = code;
  (error as any).details = details;
  return error;
}

/**
 * 安全执行函数
 * @param fn 要执行的函数
 * @param defaultValue 默认返回值
 * @returns 执行结果或默认值
 */
export function safeExecute<T>(fn: () => T, defaultValue: T): T {
  try {
    return fn();
  } catch (error) {
    console.error('Error executing function:', error);
    return defaultValue;
  }
}

/**
 * 异步安全执行函数
 * @param fn 要执行的异步函数
 * @param defaultValue 默认返回值
 * @returns 执行结果或默认值
 */
export async function safeExecuteAsync<T>(fn: () => Promise<T>, defaultValue: T): Promise<T> {
  try {
    return await fn();
  } catch (error) {
    console.error('Error executing async function:', error);
    return defaultValue;
  }
}

/**
 * 重试函数
 * @param fn 要重试的函数
 * @param maxRetries 最大重试次数
 * @param delay 重试延迟
 * @returns 执行结果
 */
export async function retry<T>(
  fn: () => Promise<T>,
  maxRetries: number = 3,
  delay: number = 1000
): Promise<T> {
  let lastError: Error | null = null;

  for (let i = 0; i < maxRetries; i++) {
    try {
      return await fn();
    } catch (error) {
      lastError = error as Error;

      if (i < maxRetries - 1) {
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }
  }

  throw lastError || new Error('Max retries exceeded');
}

// ===== 其他工具函数 =====

/**
 * 生成唯一ID
 * @param prefix 前缀
 * @returns 唯一ID
 */
export function generateId(prefix: string = ''): string {
  const timestamp = Date.now();
  const random = Math.random().toString(36).substr(2, 9);
  return prefix ? `${prefix}_${timestamp}_${random}` : `${timestamp}_${random}`;
}

/**
 * 生成UUID
 * @returns UUID字符串
 */
export function generateUUID(): string {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0;
    const v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

/**
 * 截断字符串
 * @param str 要截断的字符串
 * @param maxLength 最大长度
 * @param suffix 后缀
 * @returns 截断后的字符串
 */
export function truncateString(str: string, maxLength: number, suffix: string = '...'): string {
  if (str.length <= maxLength) {
    return str;
  }

  return str.substring(0, maxLength - suffix.length) + suffix;
}

/**
 * 驼峰命名转短横线命名
 * @param str 驼峰命名字符串
 * @returns 短横线命名字符串
 */
export function camelToKebab(str: string): string {
  return str.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase();
}

/**
 * 短横线命名转驼峰命名
 * @param str 短横线命名字符串
 * @returns 驼峰命名字符串
 */
export function kebabToCamel(str: string): string {
  return str.replace(/-([a-z])/g, (match, letter) => letter.toUpperCase());
}

/**
 * 获取文件扩展名
 * @param filename 文件名
 * @returns 文件扩展名
 */
export function getFileExtension(filename: string): string {
  return filename.slice(((filename.lastIndexOf('.') - 1) >>> 0) + 2);
}

/**
 * 获取文件名（不含扩展名）
 * @param filename 文件名
 * @returns 文件名（不含扩展名）
 */
export function getFileNameWithoutExtension(filename: string): string {
  const lastDotIndex = filename.lastIndexOf('.');
  return lastDotIndex === -1 ? filename : filename.substring(0, lastDotIndex);
}

/**
 * 检查对象是否为空
 * @param obj 要检查的对象
 * @returns 是否为空
 */
export function isEmpty(obj: any): boolean {
  if (obj === null || obj === undefined) {
    return true;
  }

  if (typeof obj === 'string') {
    return obj.trim().length === 0;
  }

  if (Array.isArray(obj)) {
    return obj.length === 0;
  }

  if (typeof obj === 'object') {
    return Object.keys(obj).length === 0;
  }

  return false;
}

/**
 * 获取对象的深度
 * @param obj 要检查的对象
 * @returns 对象深度
 */
export function getObjectDepth(obj: any): number {
  if (typeof obj !== 'object' || obj === null) {
    return 0;
  }

  let maxDepth = 0;

  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const depth = getObjectDepth(obj[key]);
      if (depth > maxDepth) {
        maxDepth = depth;
      }
    }
  }

  return maxDepth + 1;
}

/**
 * 扁平化对象
 * @param obj 要扁平化的对象
 * @param prefix 前缀
 * @returns 扁平化后的对象
 */
export function flattenObject(obj: any, prefix: string = ''): Record<string, any> {
  const result: Record<string, any> = {};

  for (const key in obj) {
    if (obj.hasOwnProperty(key)) {
      const value = obj[key];
      const newKey = prefix ? `${prefix}.${key}` : key;

      if (typeof value === 'object' && value !== null && !Array.isArray(value)) {
        Object.assign(result, flattenObject(value, newKey));
      } else {
        result[newKey] = value;
      }
    }
  }

  return result;
}

/**
 * 等待指定时间
 * @param ms 等待时间（毫秒）
 * @returns Promise
 */
export function sleep(ms: number): Promise<void> {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * 获取浏览器信息
 * @returns 浏览器信息对象
 */
export function getBrowserInfo(): BrowserInfo {
  const userAgent = navigator.userAgent;
  let browserName = 'Unknown';
  let browserVersion = 'Unknown';

  // 检测 Chrome
  if (userAgent.indexOf('Chrome') > -1) {
    browserName = 'Chrome';
    browserVersion = userAgent.match(/Chrome\/(\d+)/)?.[1] || 'Unknown';
  }
  // 检测 Firefox
  else if (userAgent.indexOf('Firefox') > -1) {
    browserName = 'Firefox';
    browserVersion = userAgent.match(/Firefox\/(\d+)/)?.[1] || 'Unknown';
  }
  // 检测 Safari
  else if (userAgent.indexOf('Safari') > -1) {
    browserName = 'Safari';
    browserVersion = userAgent.match(/Version\/(\d+)/)?.[1] || 'Unknown';
  }
  // 检测 Edge
  else if (userAgent.indexOf('Edge') > -1) {
    browserName = 'Edge';
    browserVersion = userAgent.match(/Edge\/(\d+)/)?.[1] || 'Unknown';
  }

  return {
    name: browserName,
    version: browserVersion,
    userAgent,
    isMobile: /Mobile|Android|iPhone|iPad|iPod/i.test(userAgent),
    isTablet: /iPad|Tablet/i.test(userAgent),
    isDesktop: !/Mobile|Android|iPhone|iPad|iPod|Tablet/i.test(userAgent),
  };
}

/**
 * 检查是否为移动设备
 * @returns 是否为移动设备
 */
export function isMobile(): boolean {
  return getBrowserInfo().isMobile;
}

/**
 * 检查是否为桌面设备
 * @returns 是否为桌面设备
 */
export function isDesktop(): boolean {
  return getBrowserInfo().isDesktop;
}

/**
 * 获取屏幕尺寸信息
 * @returns 屏幕尺寸信息
 */
export function getScreenInfo() {
  return {
    width: window.innerWidth,
    height: window.innerHeight,
    availWidth: screen.availWidth,
    availHeight: screen.availHeight,
    colorDepth: screen.colorDepth,
    pixelDepth: screen.pixelDepth,
    orientation: window.screen.orientation?.type || 'unknown',
  };
}

/**
 * 复制文本到剪贴板
 * @param text 要复制的文本
 * @returns 是否复制成功
 */
export async function copyToClipboard(text: string): Promise<boolean> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      await navigator.clipboard.writeText(text);
      return true;
    } else {
      // 降级方案
      const textArea = document.createElement('textarea');
      textArea.value = text;
      textArea.style.position = 'fixed';
      textArea.style.left = '-999999px';
      textArea.style.top = '-999999px';
      document.body.appendChild(textArea);
      textArea.focus();
      textArea.select();
      const result = document.execCommand('copy');
      document.body.removeChild(textArea);
      return result;
    }
  } catch (error) {
    console.error('Error copying to clipboard:', error);
    return false;
  }
}

/**
 * 从剪贴板粘贴文本
 * @returns 剪贴板文本
 */
export async function pasteFromClipboard(): Promise<string> {
  try {
    if (navigator.clipboard && window.isSecureContext) {
      return await navigator.clipboard.readText();
    } else {
      // 降级方案
      return '';
    }
  } catch (error) {
    console.error('Error pasting from clipboard:', error);
    return '';
  }
}

/**
 * 下载文件
 * @param content 文件内容
 * @param filename 文件名
 * @param contentType 文件类型
 */
export function downloadFile(
  content: string | Blob,
  filename: string,
  contentType: string = 'text/plain'
): void {
  const blob = typeof content === 'string' ? new Blob([content], { type: contentType }) : content;

  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * 打印页面
 */
export function printPage(): void {
  window.print();
}

/**
 * 全屏显示
 * @param element 要全屏的元素
 */
export function fullscreen(element?: HTMLElement): void {
  const elem = element || document.documentElement;

  if (elem.requestFullscreen) {
    elem.requestFullscreen();
  } else if ((elem as any).webkitRequestFullscreen) {
    (elem as any).webkitRequestFullscreen();
  } else if ((elem as any).msRequestFullscreen) {
    (elem as any).msRequestFullscreen();
  }
}

/**
 * 退出全屏
 */
export function exitFullscreen(): void {
  if (document.exitFullscreen) {
    document.exitFullscreen();
  } else if ((document as any).webkitExitFullscreen) {
    (document as any).webkitExitFullscreen();
  } else if ((document as any).msExitFullscreen) {
    (document as any).msExitFullscreen();
  }
}

/**
 * 检查是否为全屏
 * @returns 是否为全屏
 */
export function isFullscreen(): boolean {
  return !!(
    document.fullscreenElement ||
    (document as any).webkitFullscreenElement ||
    (document as any).msFullscreenElement
  );
}

/**
 * 获取主题配置
 * @returns 主题配置
 */
export function getThemeConfig(): ThemeConfig {
  const savedTheme = getLocalStorage<ThemeConfig>('theme');

  if (savedTheme) {
    return savedTheme;
  }

  // 检查系统主题偏好
  if (window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches) {
    return {
      mode: 'dark',
      primaryColor: '#40a9ff',
      secondaryColor: '#52c41a',
      fontSize: 'medium',
      animations: true,
      reducedMotion: false,
      highContrast: false,
    };
  }

  return {
    mode: 'light',
    primaryColor: '#1890ff',
    secondaryColor: '#52c41a',
    fontSize: 'medium',
    animations: true,
    reducedMotion: false,
    highContrast: false,
  };
}

/**
 * 保存主题配置
 * @param config 主题配置
 */
export function saveThemeConfig(config: ThemeConfig): void {
  setLocalStorage('theme', config);
}

/**
 * 应用主题到DOM
 * @param config 主题配置
 */
export function applyTheme(config: ThemeConfig): void {
  const root = document.documentElement;

  // 设置主题模式
  root.setAttribute('data-theme', config.mode);

  // 设置CSS变量
  root.style.setProperty('--color-primary', config.primaryColor);
  root.style.setProperty('--color-secondary', config.secondaryColor);

  // 设置字体大小
  root.style.setProperty(
    '--font-size-multiplier',
    config.fontSize === 'small' ? '0.875' : config.fontSize === 'large' ? '1.125' : '1'
  );

  // 设置动画偏好
  root.style.setProperty('--animations-enabled', config.animations ? '1' : '0');

  // 设置高对比度
  if (config.highContrast) {
    root.setAttribute('data-high-contrast', 'true');
  } else {
    root.removeAttribute('data-high-contrast');
  }

  // 设置减少动画
  if (config.reducedMotion) {
    root.setAttribute('data-reduced-motion', 'true');
  } else {
    root.removeAttribute('data-reduced-motion');
  }
}

/**
 * 监听系统主题变化
 * @param callback 回调函数
 */
export function watchSystemTheme(callback: (theme: 'light' | 'dark') => void): () => void {
  const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');

  const handleChange = (e: MediaQueryListEvent) => {
    callback(e.matches ? 'dark' : 'light');
  };

  mediaQuery.addEventListener('change', handleChange);

  // 返回取消监听的函数
  return () => {
    mediaQuery.removeEventListener('change', handleChange);
  };
}

/**
 * 获取性能指标
 * @returns 性能指标
 */
export function getPerformanceMetrics() {
  if ('performance' in window) {
    const navigation = performance.getEntriesByType('navigation')[0] as PerformanceNavigationTiming;
    const paint = performance.getEntriesByType('paint');

    return {
      // 页面加载时间
      pageLoad: navigation.loadEventEnd - navigation.fetchStart,

      // 首次内容绘制
      firstContentfulPaint:
        paint.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,

      // 首次有意义绘制
      largestContentfulPaint:
        paint.find(entry => entry.name === 'largest-contentful-paint')?.startTime || 0,

      // DOM构建时间
      domContentLoaded: navigation.domContentLoadedEventEnd - navigation.domContentLoadedEventStart,

      // 重定向时间
      redirectTime: navigation.redirectEnd - navigation.redirectStart,

      // DNS查询时间
      dnsTime: navigation.domainLookupEnd - navigation.domainLookupStart,

      // TCP连接时间
      tcpTime: navigation.connectEnd - navigation.connectStart,

      // 请求响应时间
      requestTime: navigation.responseEnd - navigation.requestStart,

      // 服务器响应时间
      serverTime: navigation.responseEnd - navigation.requestStart,

      // 页面准备时间
      domInteractive: navigation.domInteractive - navigation.fetchStart,

      // 完全加载时间
      loadComplete: navigation.loadEventEnd - navigation.fetchStart,
    };
  }

  return {};
}

/**
 * 生成随机颜色
 * @returns 随机颜色十六进制值
 */
export function generateRandomColor(): string {
  return `#${Math.floor(Math.random() * 16777215)
    .toString(16)
    .padStart(6, '0')}`;
}

/**
 * 将颜色转换为RGB
 * @param hex 颜色十六进制值
 * @returns RGB值
 */
export function hexToRgb(hex: string): { r: number; g: number; b: number } {
  const result = /^#?([a-f\d]{2})([a-f\d]{2})([a-f\d]{2})$/i.exec(hex);

  return result
    ? {
        r: parseInt(result[1], 16),
        g: parseInt(result[2], 16),
        b: parseInt(result[3], 16),
      }
    : { r: 0, g: 0, b: 0 };
}

/**
 * 将RGB转换为十六进制
 * @param r 红色值
 * @param g 绿色值
 * @param b 蓝色值
 * @returns 十六进制颜色值
 */
export function rgbToHex(r: number, g: number, b: number): string {
  return `#${[r, g, b]
    .map(x => {
      const hex = x.toString(16);
      return hex.length === 1 ? '0' + hex : hex;
    })
    .join('')}`;
}

/**
 * 获取颜色的对比度
 * @param color1 颜色1
 * @param color2 颜色2
 * @returns 对比度值
 */
export function getColorContrast(color1: string, color2: string): number {
  const rgb1 = hexToRgb(color1);
  const rgb2 = hexToRgb(color2);

  const getLuminance = (r: number, g: number, b: number) => {
    const [rs, gs, bs] = [r, g, b].map(c => {
      c = c / 255;
      return c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    });
    return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
  };

  const lum1 = getLuminance(rgb1.r, rgb1.g, rgb1.b);
  const lum2 = getLuminance(rgb2.r, rgb2.g, rgb2.b);

  const brightest = Math.max(lum1, lum2);
  const darkest = Math.min(lum1, lum2);

  return (brightest + 0.05) / (darkest + 0.05);
}

/**
 * 检查颜色对比度是否符合WCAG标准
 * @param color1 颜色1
 * @param color2 颜色2
 * @param level WCAG级别 ('AA' 或 'AAA')
 * @returns 是否符合标准
 */
export function isColorContrastValid(
  color1: string,
  color2: string,
  level: 'AA' | 'AAA' = 'AA'
): boolean {
  const contrast = getColorContrast(color1, color2);

  if (level === 'AAA') {
    return contrast >= 7;
  }

  return contrast >= 4.5;
}

// ===== 导出 =====

// 默认导出
export default {
  formatFileSize,
  formatNumber,
  formatCurrency,
  formatPercentage,
  formatDateTime,
  formatRelativeTime,
  isValidEmail,
  isValidPhone,
  isValidUrl,
  isValidJson,
  getPasswordStrength,
  getCurrentTimestamp,
  timestampToDate,
  dateToTimestamp,
  addDays,
  addHours,
  getDateRange,
  getWeekStart,
  getWeekEnd,
  getMonthStart,
  getMonthEnd,
  getLocalStorage,
  setLocalStorage,
  removeLocalStorage,
  clearLocalStorage,
  getSessionStorage,
  setSessionStorage,
  removeSessionStorage,
  deepClone,
  shallowClone,
  mergeObjects,
  debounce,
  throttle,
  once,
  createError,
  safeExecute,
  safeExecuteAsync,
  retry,
  generateId,
  generateUUID,
  truncateString,
  camelToKebab,
  kebabToCamel,
  getFileExtension,
  getFileNameWithoutExtension,
  isEmpty,
  getObjectDepth,
  flattenObject,
  sleep,
  getBrowserInfo,
  isMobile,
  isDesktop,
  getScreenInfo,
  copyToClipboard,
  pasteFromClipboard,
  downloadFile,
  printPage,
  fullscreen,
  exitFullscreen,
  isFullscreen,
  getThemeConfig,
  saveThemeConfig,
  applyTheme,
  watchSystemTheme,
  getPerformanceMetrics,
  generateRandomColor,
  hexToRgb,
  rgbToHex,
  getColorContrast,
  isColorContrastValid,
};
