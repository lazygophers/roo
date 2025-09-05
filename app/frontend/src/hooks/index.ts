/**
 * 自定义React Hooks集合
 * Custom React Hooks Collection
 *
 * 提供各种自定义Hooks，包括：
 * - 主题管理
 * - 本地存储
 * - API调用
 * - 表单处理
 * - 防抖节流
 * - 权限管理
 * - 性能监控
 * - 事件监听
 * - 媒体查询
 */

// ===== 导入 =====
import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import type {
  ThemeConfig,
  ApiResponse,
  UseApiResult,
  UseAsyncResult,
  UsePaginationResult,
  UseFormResult,
  UsePermissionResult,
  UsePerformanceResult,
  UseMediaQueryResult,
} from '@/types';

// ===== 主题管理Hooks =====

/**
 * 主题管理Hook
 * @returns 主题管理相关的状态和方法
 */
export function useTheme(): {
  theme: ThemeConfig;
  setTheme: (theme: Partial<ThemeConfig>) => void;
  toggleTheme: () => void;
  isDark: boolean;
  isLight: boolean;
} {
  const [theme, setThemeState] = useState<ThemeConfig>(() => {
    if (typeof window !== 'undefined') {
      const saved = localStorage.getItem('theme');
      return saved
        ? JSON.parse(saved)
        : {
            mode: 'light',
            primaryColor: '#1890ff',
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
  });

  const setTheme = useCallback(
    (newTheme: Partial<ThemeConfig>) => {
      const updatedTheme = { ...theme, ...newTheme };
      setThemeState(updatedTheme);
      localStorage.setItem('theme', JSON.stringify(updatedTheme));

      // 应用主题到DOM
      const root = document.documentElement;
      root.setAttribute('data-theme', updatedTheme.mode);
      root.style.setProperty('--color-primary', updatedTheme.primaryColor);
      root.style.setProperty('--color-secondary', updatedTheme.secondaryColor);
      root.style.setProperty('--animations-enabled', updatedTheme.animations ? '1' : '0');

      if (updatedTheme.highContrast) {
        root.setAttribute('data-high-contrast', 'true');
      } else {
        root.removeAttribute('data-high-contrast');
      }

      if (updatedTheme.reducedMotion) {
        root.setAttribute('data-reduced-motion', 'true');
      } else {
        root.removeAttribute('data-reduced-motion');
      }
    },
    [theme]
  );

  const toggleTheme = useCallback(() => {
    setTheme({
      mode: theme.mode === 'light' ? 'dark' : 'light',
    });
  }, [theme.mode, setTheme]);

  useEffect(() => {
    // 监听系统主题变化
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = (e: MediaQueryListEvent) => {
      if (!localStorage.getItem('theme')) {
        setTheme({
          mode: e.matches ? 'dark' : 'light',
        });
      }
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [setTheme]);

  return {
    theme,
    setTheme,
    toggleTheme,
    isDark: theme.mode === 'dark',
    isLight: theme.mode === 'light',
  };
}

// ===== 本地存储Hooks =====

/**
 * 本地存储Hook
 * @param key 存储键
 * @param defaultValue 默认值
 * @returns [存储值, 设置值, 删除值]
 */
export function useLocalStorage<T>(
  key: string,
  defaultValue: T
): [T, (value: T) => void, () => void] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window !== 'undefined') {
      try {
        const item = localStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch {
        return defaultValue;
      }
    }
    return defaultValue;
  });

  const setStoredValue = useCallback(
    (newValue: T) => {
      try {
        setValue(newValue);
        localStorage.setItem(key, JSON.stringify(newValue));
      } catch (error) {
        console.error('Error setting localStorage:', error);
      }
    },
    [key]
  );

  const removeStoredValue = useCallback(() => {
    try {
      localStorage.removeItem(key);
      setValue(defaultValue);
    } catch (error) {
      console.error('Error removing localStorage:', error);
    }
  }, [key, defaultValue]);

  return [value, setStoredValue, removeStoredValue];
}

/**
 * 会话存储Hook
 * @param key 存储键
 * @param defaultValue 默认值
 * @returns [存储值, 设置值, 删除值]
 */
export function useSessionStorage<T>(
  key: string,
  defaultValue: T
): [T, (value: T) => void, () => void] {
  const [value, setValue] = useState<T>(() => {
    if (typeof window !== 'undefined') {
      try {
        const item = sessionStorage.getItem(key);
        return item ? JSON.parse(item) : defaultValue;
      } catch {
        return defaultValue;
      }
    }
    return defaultValue;
  });

  const setStoredValue = useCallback(
    (newValue: T) => {
      try {
        setValue(newValue);
        sessionStorage.setItem(key, JSON.stringify(newValue));
      } catch (error) {
        console.error('Error setting sessionStorage:', error);
      }
    },
    [key]
  );

  const removeStoredValue = useCallback(() => {
    try {
      sessionStorage.removeItem(key);
      setValue(defaultValue);
    } catch (error) {
      console.error('Error removing sessionStorage:', error);
    }
  }, [key, defaultValue]);

  return [value, setStoredValue, removeStoredValue];
}

// ===== API调用Hooks =====

/**
 * API调用Hook
 * @param apiFunction API函数
 * @param options 配置选项
 * @returns API调用结果
 */
export function useApi<T>(
  apiFunction: () => Promise<T>,
  options: {
    immediate?: boolean;
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
    retryCount?: number;
    retryDelay?: number;
  } = {}
): UseApiResult<T> {
  const { immediate = true, onSuccess, onError, retryCount = 3, retryDelay = 1000 } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(async () => {
    setLoading(true);
    setError(null);

    let lastError: Error | null = null;

    for (let i = 0; i < retryCount; i++) {
      try {
        const result = await apiFunction();
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        lastError = err as Error;
        if (i < retryCount - 1) {
          await new Promise(resolve => setTimeout(resolve, retryDelay));
        }
      }
    }

    setError(lastError);
    onError?.(lastError!);
    throw lastError;
  }, [apiFunction, onSuccess, onError, retryCount, retryDelay]);

  useEffect(() => {
    if (immediate) {
      execute();
    }
  }, [execute, immediate]);

  return {
    data,
    loading,
    error,
    execute,
    refresh: execute,
  };
}

/**
 * 异步操作Hook
 * @param asyncFunction 异步函数
 * @param options 配置选项
 * @returns 异步操作结果
 */
export function useAsync<T, Args extends any[] = []>(
  asyncFunction: (...args: Args) => Promise<T>,
  options: {
    onSuccess?: (data: T) => void;
    onError?: (error: Error) => void;
    immediate?: boolean;
  } = {}
): UseAsyncResult<T, Args> {
  const { onSuccess, onError, immediate = false } = options;

  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const execute = useCallback(
    async (...args: Args) => {
      setLoading(true);
      setError(null);

      try {
        const result = await asyncFunction(...args);
        setData(result);
        onSuccess?.(result);
        return result;
      } catch (err) {
        const error = err as Error;
        setError(error);
        onError?.(error);
        throw error;
      } finally {
        setLoading(false);
      }
    },
    [asyncFunction, onSuccess, onError]
  );

  return {
    data,
    loading,
    error,
    execute,
    reset: useCallback(() => {
      setData(null);
      setError(null);
    }, []),
  };
}

// ===== 分页Hooks =====

/**
 * 分页Hook
 * @param options 分页选项
 * @returns 分页结果
 */
export function usePagination<T>(
  options: {
    data: T[];
    pageSize?: number;
    initialPage?: number;
  } = {}
): UsePaginationResult<T> {
  const { data, pageSize = 10, initialPage = 1 } = options;

  const [currentPage, setCurrentPage] = useState(initialPage);

  const totalPages = useMemo(() => {
    return Math.ceil(data.length / pageSize);
  }, [data.length, pageSize]);

  const paginatedData = useMemo(() => {
    const startIndex = (currentPage - 1) * pageSize;
    const endIndex = startIndex + pageSize;
    return data.slice(startIndex, endIndex);
  }, [data, currentPage, pageSize]);

  const goToPage = useCallback(
    (page: number) => {
      if (page >= 1 && page <= totalPages) {
        setCurrentPage(page);
      }
    },
    [totalPages]
  );

  const nextPage = useCallback(() => {
    goToPage(currentPage + 1);
  }, [currentPage, goToPage]);

  const prevPage = useCallback(() => {
    goToPage(currentPage - 1);
  }, [currentPage, goToPage]);

  const firstPage = useCallback(() => {
    goToPage(1);
  }, [goToPage]);

  const lastPage = useCallback(() => {
    goToPage(totalPages);
  }, [totalPages, goToPage]);

  return {
    currentPage,
    totalPages,
    paginatedData,
    goToPage,
    nextPage,
    prevPage,
    firstPage,
    lastPage,
    hasNextPage: currentPage < totalPages,
    hasPrevPage: currentPage > 1,
  };
}

// ===== 表单处理Hooks =====

/**
 * 表单Hook
 * @param initialValues 初始值
 * @param validate 验证函数
 * @returns 表单结果
 */
export function useForm<T extends Record<string, any>>(
  initialValues: T,
  validate?: (values: T) => Record<string, string> | void
): UseFormResult<T> {
  const [values, setValues] = useState<T>(initialValues);
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [touched, setTouched] = useState<Record<string, boolean>>({});

  const setValue = useCallback((name: keyof T, value: any) => {
    setValues(prev => ({ ...prev, [name]: value }));
    setTouched(prev => ({ ...prev, [name]: true }));
  }, []);

  const setValuesBulk = useCallback((newValues: Partial<T>) => {
    setValues(prev => ({ ...prev, ...newValues }));
    setTouched(prev => {
      const newTouched = { ...prev };
      Object.keys(newValues).forEach(key => {
        newTouched[key] = true;
      });
      return newTouched;
    });
  }, []);

  const setError = useCallback((name: keyof T, error: string) => {
    setErrors(prev => ({ ...prev, [name]: error }));
  }, []);

  const clearError = useCallback((name: keyof T) => {
    setErrors(prev => {
      const newErrors = { ...prev };
      delete newErrors[name as string];
      return newErrors;
    });
  }, []);

  const clearErrors = useCallback(() => {
    setErrors({});
  }, []);

  const reset = useCallback(() => {
    setValues(initialValues);
    setErrors({});
    setTouched({});
  }, [initialValues]);

  const validateForm = useCallback(() => {
    if (!validate) {
      return true;
    }

    const validationErrors = validate(values);
    if (validationErrors) {
      setErrors(validationErrors);
      return false;
    }

    setErrors({});
    return true;
  }, [values, validate]);

  const getFieldProps = useCallback(
    (name: keyof T) => ({
      value: values[name] || '',
      onChange: (value: any) => setValue(name, value),
      onBlur: () => setTouched(prev => ({ ...prev, [name]: true })),
      error: touched[name] ? errors[name as string] : undefined,
      touched: touched[name],
    }),
    [values, touched, errors, setValue]
  );

  return {
    values,
    errors,
    touched,
    setValue,
    setValuesBulk,
    setError,
    clearError,
    clearErrors,
    reset,
    validate: validateForm,
    getFieldProps,
    isValid: Object.keys(errors).length === 0,
    isDirty: JSON.stringify(values) !== JSON.stringify(initialValues),
  };
}

// ===== 权限管理Hooks =====

/**
 * 权限管理Hook
 * @param permissions 权限列表
 * @returns 权限结果
 */
export function usePermission(permissions: string[]): UsePermissionResult {
  const [userPermissions, setUserPermissions] = useState<string[]>(() => {
    if (typeof window !== 'undefined') {
      try {
        const stored = localStorage.getItem('userPermissions');
        return stored ? JSON.parse(stored) : [];
      } catch {
        return [];
      }
    }
    return [];
  });

  const hasPermission = useCallback(
    (permission: string) => {
      return userPermissions.includes(permission);
    },
    [userPermissions]
  );

  const hasAnyPermission = useCallback(
    (requiredPermissions: string[]) => {
      return requiredPermissions.some(permission => hasPermission(permission));
    },
    [hasPermission]
  );

  const hasAllPermissions = useCallback(
    (requiredPermissions: string[]) => {
      return requiredPermissions.every(permission => hasPermission(permission));
    },
    [hasPermission]
  );

  const addPermission = useCallback(
    (permission: string) => {
      const newPermissions = [...new Set([...userPermissions, permission])];
      setUserPermissions(newPermissions);
      localStorage.setItem('userPermissions', JSON.stringify(newPermissions));
    },
    [userPermissions]
  );

  const removePermission = useCallback(
    (permission: string) => {
      const newPermissions = userPermissions.filter(p => p !== permission);
      setUserPermissions(newPermissions);
      localStorage.setItem('userPermissions', JSON.stringify(newPermissions));
    },
    [userPermissions]
  );

  const setPermissions = useCallback((newPermissions: string[]) => {
    setUserPermissions(newPermissions);
    localStorage.setItem('userPermissions', JSON.stringify(newPermissions));
  }, []);

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    addPermission,
    removePermission,
    setPermissions,
    permissions: userPermissions,
  };
}

// ===== 性能监控Hooks =====

/**
 * 性能监控Hook
 * @returns 性能监控结果
 */
export function usePerformance(): UsePerformanceResult {
  const [metrics, setMetrics] = useState({
    fps: 0,
    memory: 0,
    timing: 0,
    paint: 0,
  });

  const fpsRef = useRef(0);
  const lastTimeRef = useRef(performance.now());
  const framesRef = useRef(0);

  useEffect(() => {
    if (typeof window === 'undefined' || !('performance' in window)) {
      return;
    }

    // FPS计算
    const calculateFPS = () => {
      framesRef.current++;
      const currentTime = performance.now();
      const deltaTime = currentTime - lastTimeRef.current;

      if (deltaTime >= 1000) {
        fpsRef.current = Math.round((framesRef.current * 1000) / deltaTime);
        framesRef.current = 0;
        lastTimeRef.current = currentTime;

        setMetrics(prev => ({
          ...prev,
          fps: fpsRef.current,
        }));
      }

      requestAnimationFrame(calculateFPS);
    };

    const fpsAnimation = requestAnimationFrame(calculateFPS);

    // 内存监控
    const updateMemory = () => {
      if ('memory' in performance) {
        const memory = (performance as any).memory;
        setMetrics(prev => ({
          ...prev,
          memory: Math.round(memory.usedJSHeapSize / 1024 / 1024),
        }));
      }
    };

    const memoryInterval = setInterval(updateMemory, 5000);

    // 页面加载时间
    const updateTiming = () => {
      const navigation = performance.getEntriesByType(
        'navigation'
      )[0] as PerformanceNavigationTiming;
      setMetrics(prev => ({
        ...prev,
        timing: Math.round(navigation.loadEventEnd - navigation.fetchStart),
      }));
    };

    if (document.readyState === 'complete') {
      updateTiming();
    } else {
      window.addEventListener('load', updateTiming);
    }

    // 绘制时间
    const observer = new PerformanceObserver(list => {
      const paint = list.getEntries().find(entry => entry.name === 'first-contentful-paint');
      if (paint) {
        setMetrics(prev => ({
          ...prev,
          paint: Math.round(paint.startTime),
        }));
      }
    });

    observer.observe({ entryTypes: ['paint'] });

    return () => {
      cancelAnimationFrame(fpsAnimation);
      clearInterval(memoryInterval);
      window.removeEventListener('load', updateTiming);
      observer.disconnect();
    };
  }, []);

  return {
    ...metrics,
    isHighFPS: metrics.fps >= 50,
    isLowMemory: metrics.memory < 100,
    isFastLoad: metrics.timing < 3000,
  };
}

// ===== 事件监听Hooks =====

/**
 * 事件监听Hook
 * @param event 事件名称
 * @param handler 事件处理函数
 * @param target 目标元素
 * @param options 选项
 */
export function useEventListener<K extends keyof WindowEventMap>(
  event: K,
  handler: (event: WindowEventMap[K]) => void,
  target: Window | HTMLElement = window,
  options?: AddEventListenerOptions
): void {
  useEffect(() => {
    target.addEventListener(event, handler, options);
    return () => target.removeEventListener(event, handler, options);
  }, [event, handler, target, options]);
}

/**
 * 点击外部Hook
 * @param handler 点击外部时的处理函数
 * @returns ref
 */
export function useClickOutside<T extends HTMLElement>(handler: () => void): React.RefObject<T> {
  const ref = useRef<T>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (ref.current && !ref.current.contains(event.target as Node)) {
        handler();
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [handler]);

  return ref;
}

/**
 * 键盘快捷键Hook
 * @param key 键盘按键
 * @param handler 处理函数
 * @param options 选项
 */
export function useKeyboardShortcut(
  key: string,
  handler: () => void,
  options: {
    ctrl?: boolean;
    alt?: boolean;
    shift?: boolean;
    meta?: boolean;
    preventDefault?: boolean;
  } = {}
): void {
  const { ctrl = false, alt = false, shift = false, meta = false, preventDefault = true } = options;

  useEffect(() => {
    const handleKeyDown = (event: KeyboardEvent) => {
      const isCtrlKey = ctrl ? event.ctrlKey : true;
      const isAltKey = alt ? event.altKey : true;
      const isShiftKey = shift ? event.shiftKey : true;
      const isMetaKey = meta ? event.metaKey : true;

      if (event.key === key && isCtrlKey && isAltKey && isShiftKey && isMetaKey) {
        if (preventDefault) {
          event.preventDefault();
        }
        handler();
      }
    };

    document.addEventListener('keydown', handleKeyDown);
    return () => document.removeEventListener('keydown', handleKeyDown);
  }, [key, handler, ctrl, alt, shift, meta, preventDefault]);
}

// ===== 媒体查询Hooks =====

/**
 * 媒体查询Hook
 * @param query 媒体查询字符串
 * @returns 媒体查询结果
 */
export function useMediaQuery(query: string): UseMediaQueryResult {
  const [matches, setMatches] = useState(false);

  useEffect(() => {
    if (typeof window === 'undefined') {
      return;
    }

    const mediaQuery = window.matchMedia(query);
    setMatches(mediaQuery.matches);

    const handleChange = (event: MediaQueryListEvent) => {
      setMatches(event.matches);
    };

    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, [query]);

  return {
    matches,
    mediaQueryList: typeof window !== 'undefined' ? window.matchMedia(query) : null,
  };
}

// ===== 常用媒体查询Hooks =====

/**
 * 检测是否为移动设备
 */
export function useIsMobile(): boolean {
  return useMediaQuery('(max-width: 768px)').matches;
}

/**
 * 检测是否为平板设备
 */
export function useIsTablet(): boolean {
  return useMediaQuery('(min-width: 769px) and (max-width: 1024px)').matches;
}

/**
 * 检测是否为桌面设备
 */
export function useIsDesktop(): boolean {
  return useMediaQuery('(min-width: 1025px)').matches;
}

/**
 * 检测是否为暗色主题
 */
export function useIsDarkMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: dark)').matches;
}

/**
 * 检测是否为亮色主题
 */
export function useIsLightMode(): boolean {
  return useMediaQuery('(prefers-color-scheme: light)').matches;
}

/**
 * 检测是否启用了减少动画
 */
export function usePrefersReducedMotion(): boolean {
  return useMediaQuery('(prefers-reduced-motion: reduce)').matches;
}

/**
 * 检测是否为高对比度模式
 */
export function usePrefersHighContrast(): boolean {
  return useMediaQuery('(prefers-contrast: high)').matches;
}

// ===== 生命周期Hooks =====

/**
 * 组件挂载Hook
 * @param effect 挂载时的副作用
 */
export function useOnMount(effect: () => void): void {
  useEffect(effect, []);
}

/**
 * 组件卸载Hook
 * @param effect 卸载时的清理函数
 */
export function useOnUnmount(effect: () => void): void {
  useEffect(() => effect, []);
}

/**
 * 组件更新Hook
 * @param effect 更新时的副作用
 * @param deps 依赖数组
 */
export function useOnUpdate(effect: () => void, deps: any[]): void {
  const isMounted = useRef(false);

  useEffect(() => {
    if (isMounted.current) {
      effect();
    }
    isMounted.current = true;
  }, deps);
}

// ===== 定时器Hooks =====

/**
 * 定时器Hook
 * @param callback 回调函数
 * @param delay 延迟时间
 * @param options 选项
 */
export function useTimeout(
  callback: () => void,
  delay: number | null,
  options: {
    immediate?: boolean;
  } = {}
): void {
  const { immediate = false } = options;
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (delay === null) {
      return;
    }

    if (immediate) {
      timeoutRef.current = setTimeout(callback, delay);
    }

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [callback, delay, immediate]);

  const clear = useCallback(() => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
  }, []);

  return clear;
}

/**
 * 间隔器Hook
 * @param callback 回调函数
 * @param delay 间隔时间
 * @param options 选项
 */
export function useInterval(
  callback: () => void,
  delay: number | null,
  options: {
    immediate?: boolean;
  } = {}
): void {
  const { immediate = false } = options;
  const intervalRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (delay === null) {
      return;
    }

    if (immediate) {
      callback();
    }

    intervalRef.current = setInterval(callback, delay);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [callback, delay, immediate]);

  const clear = useCallback(() => {
    if (intervalRef.current) {
      clearInterval(intervalRef.current);
      intervalRef.current = null;
    }
  }, []);

  return clear;
}

// ===== 防抖节流Hooks =====

/**
 * 防抖Hook
 * @param value 要防抖的值
 * @param delay 延迟时间
 * @returns 防抖后的值
 */
export function useDebounce<T>(value: T, delay: number): T {
  const [debouncedValue, setDebouncedValue] = useState<T>(value);

  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedValue(value);
    }, delay);

    return () => {
      clearTimeout(handler);
    };
  }, [value, delay]);

  return debouncedValue;
}

/**
 * 节流Hook
 * @param value 要节流的值
 * @param delay 延迟时间
 * @returns 节流后的值
 */
export function useThrottle<T>(value: T, delay: number): T {
  const [throttledValue, setThrottledValue] = useState<T>(value);
  const lastExecuted = useRef<number>(0);

  useEffect(() => {
    const now = Date.now();
    const timeSinceLastExecution = now - lastExecuted.current;

    if (timeSinceLastExecution >= delay) {
      setThrottledValue(value);
      lastExecuted.current = now;
    } else {
      const timer = setTimeout(() => {
        setThrottledValue(value);
        lastExecuted.current = Date.now();
      }, delay - timeSinceLastExecution);

      return () => clearTimeout(timer);
    }
  }, [value, delay]);

  return throttledValue;
}

// ===== 状态管理Hooks =====

/**
 * 状态切换Hook
 * @param initialValue 初始值
 * @returns [状态, 切换函数, 设置为true, 设置为false]
 */
export function useToggle(
  initialValue: boolean = false
): [boolean, () => void, () => void, () => void] {
  const [value, setValue] = useState(initialValue);

  const toggle = useCallback(() => setValue(prev => !prev), []);
  const setTrue = useCallback(() => setValue(true), []);
  const setFalse = useCallback(() => setValue(false), []);

  return [value, toggle, setTrue, setFalse];
}

/**
 * 数组状态Hook
 * @param initialValue 初始值
 * @returns 数组状态和操作函数
 */
export function useArray<T>(initialValue: T[] = []): {
  array: T[];
  set: React.Dispatch<React.SetStateAction<T[]>>;
  push: (item: T) => void;
  remove: (index: number) => void;
  update: (index: number, item: T) => void;
  clear: () => void;
  filter: (predicate: (item: T) => boolean) => void;
} {
  const [array, setArray] = useState<T[]>(initialValue);

  const push = useCallback((item: T) => {
    setArray(prev => [...prev, item]);
  }, []);

  const remove = useCallback((index: number) => {
    setArray(prev => prev.filter((_, i) => i !== index));
  }, []);

  const update = useCallback((index: number, item: T) => {
    setArray(prev => prev.map((prevItem, i) => (i === index ? item : prevItem)));
  }, []);

  const clear = useCallback(() => {
    setArray([]);
  }, []);

  const filter = useCallback((predicate: (item: T) => boolean) => {
    setArray(prev => prev.filter(predicate));
  }, []);

  return {
    array,
    set: setArray,
    push,
    remove,
    update,
    clear,
    filter,
  };
}

// ===== 导航Hooks =====

/**
 * 页面可见性Hook
 * @returns 页面可见性状态
 */
export function usePageVisibility(): {
  isVisible: boolean;
  onVisibilityChange: (callback: (isVisible: boolean) => void) => void;
} {
  const [isVisible, setIsVisible] = useState(!document.hidden);

  useEffect(() => {
    const handleVisibilityChange = () => {
      setIsVisible(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  const onVisibilityChange = useCallback((callback: (isVisible: boolean) => void) => {
    const handleVisibilityChange = () => {
      callback(!document.hidden);
    };

    document.addEventListener('visibilitychange', handleVisibilityChange);
    return () => document.removeEventListener('visibilitychange', handleVisibilityChange);
  }, []);

  return {
    isVisible,
    onVisibilityChange,
  };
}

/**
 * 在线状态Hook
 * @returns 在线状态
 */
export function useOnlineStatus(): boolean {
  const [isOnline, setIsOnline] = useState(navigator.onLine);

  useEffect(() => {
    const handleOnline = () => setIsOnline(true);
    const handleOffline = () => setIsOnline(false);

    window.addEventListener('online', handleOnline);
    window.addEventListener('offline', handleOffline);

    return () => {
      window.removeEventListener('online', handleOnline);
      window.removeEventListener('offline', handleOffline);
    };
  }, []);

  return isOnline;
}

/**
 * 窗口尺寸Hook
 * @returns 窗口尺寸
 */
export function useWindowSize(): {
  width: number;
  height: number;
} {
  const [windowSize, setWindowSize] = useState({
    width: typeof window !== 'undefined' ? window.innerWidth : 0,
    height: typeof window !== 'undefined' ? window.innerHeight : 0,
  });

  useEffect(() => {
    const handleResize = () => {
      setWindowSize({
        width: window.innerWidth,
        height: window.innerHeight,
      });
    };

    window.addEventListener('resize', handleResize);
    return () => window.removeEventListener('resize', handleResize);
  }, []);

  return windowSize;
}

/**
 * 滚动位置Hook
 * @returns 滚动位置
 */
export function useScrollPosition(): {
  x: number;
  y: number;
} {
  const [scrollPosition, setScrollPosition] = useState({
    x: typeof window !== 'undefined' ? window.scrollX : 0,
    y: typeof window !== 'undefined' ? window.scrollY : 0,
  });

  useEffect(() => {
    const handleScroll = () => {
      setScrollPosition({
        x: window.scrollX,
        y: window.scrollY,
      });
    };

    window.addEventListener('scroll', handleScroll);
    return () => window.removeEventListener('scroll', handleScroll);
  }, []);

  return scrollPosition;
}

// ===== 复制粘贴Hooks =====

/**
 * 复制到剪贴板Hook
 * @returns 复制功能
 */
export function useCopyToClipboard(): {
  copy: (text: string) => Promise<boolean>;
  copied: boolean;
  reset: () => void;
} {
  const [copied, setCopied] = useState(false);

  const copy = useCallback(async (text: string): Promise<boolean> => {
    try {
      if (navigator.clipboard && window.isSecureContext) {
        await navigator.clipboard.writeText(text);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
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
        setCopied(result);
        setTimeout(() => setCopied(false), 2000);
        return result;
      }
    } catch (error) {
      console.error('Error copying to clipboard:', error);
      return false;
    }
  }, []);

  const reset = useCallback(() => {
    setCopied(false);
  }, []);

  return {
    copy,
    copied,
    reset,
  };
}

// ===== 默认导出 =====

export default {
  useTheme,
  useLocalStorage,
  useSessionStorage,
  useApi,
  useAsync,
  usePagination,
  useForm,
  usePermission,
  usePerformance,
  useEventListener,
  useClickOutside,
  useKeyboardShortcut,
  useMediaQuery,
  useIsMobile,
  useIsTablet,
  useIsDesktop,
  useIsDarkMode,
  useIsLightMode,
  usePrefersReducedMotion,
  usePrefersHighContrast,
  useOnMount,
  useOnUnmount,
  useOnUpdate,
  useTimeout,
  useInterval,
  useDebounce,
  useThrottle,
  useToggle,
  useArray,
  usePageVisibility,
  useOnlineStatus,
  useWindowSize,
  useScrollPosition,
  useCopyToClipboard,
};
