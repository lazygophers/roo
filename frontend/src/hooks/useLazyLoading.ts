import { useState, useEffect, useRef } from 'react';

export interface LazyLoadingOptions {
  /** 是否启用惰性加载 */
  enabled?: boolean;
  /** 组件标识符 */
  key?: string;
  /** 是否自动加载（如果为false，需要手动调用load） */
  autoLoad?: boolean;
  /** 缓存时间（毫秒），0表示不缓存 */
  cacheTime?: number;
}

export interface LazyLoadingState {
  /** 是否正在加载 */
  loading: boolean;
  /** 是否已加载过 */
  loaded: boolean;
  /** 是否有错误 */
  error: Error | null;
  /** 手动触发加载 */
  load: () => void;
  /** 重新加载 */
  reload: () => void;
  /** 清除缓存 */
  clearCache: () => void;
}

/**
 * 惰性加载Hook，支持缓存和手动控制
 */
export const useLazyLoading = (
  loadFunction: () => Promise<void>,
  options: LazyLoadingOptions = {}
): LazyLoadingState => {
  const {
    enabled = true,
    key = 'default',
    autoLoad = true,
    cacheTime = 5 * 60 * 1000 // 默认5分钟缓存
  } = options;

  const [loading, setLoading] = useState(false);
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const loadedRef = useRef(false);
  const lastLoadTimeRef = useRef<number>(0);
  const cacheKey = `lazy-load-${key}`;

  // 检查缓存是否有效
  const isCacheValid = () => {
    if (cacheTime === 0) return false;
    const lastLoadTime = lastLoadTimeRef.current;
    return lastLoadTime > 0 && (Date.now() - lastLoadTime) < cacheTime;
  };

  // 从缓存中恢复状态
  const restoreFromCache = () => {
    const cached = sessionStorage.getItem(cacheKey);
    if (cached) {
      try {
        const { loadTime, loaded: cachedLoaded } = JSON.parse(cached);
        if (cachedLoaded && cacheTime > 0 && (Date.now() - loadTime) < cacheTime) {
          setLoaded(true);
          loadedRef.current = true;
          lastLoadTimeRef.current = loadTime;
          return true;
        }
      } catch (e) {
        // 忽略缓存解析错误
      }
    }
    return false;
  };

  // 保存到缓存
  const saveToCache = () => {
    if (cacheTime > 0) {
      const cacheData = {
        loadTime: Date.now(),
        loaded: true
      };
      sessionStorage.setItem(cacheKey, JSON.stringify(cacheData));
    }
  };

  // 执行加载
  const performLoad = async () => {
    if (loading || (loaded && isCacheValid())) {
      return;
    }

    console.log(`[useLazyLoading] Starting load for key: ${key}`);
    setLoading(true);
    setError(null);

    try {
      await loadFunction();
      setLoaded(true);
      loadedRef.current = true;
      lastLoadTimeRef.current = Date.now();
      saveToCache();
      console.log(`[useLazyLoading] Load completed for key: ${key}`);
    } catch (err) {
      const error = err instanceof Error ? err : new Error('加载失败');
      setError(error);
      console.error(`[useLazyLoading] Load failed for key: ${key}`, error);
    } finally {
      setLoading(false);
    }
  };

  // 重新加载
  const reload = () => {
    setLoaded(false);
    loadedRef.current = false;
    lastLoadTimeRef.current = 0;
    clearCache();
    performLoad();
  };

  // 清除缓存
  const clearCache = () => {
    sessionStorage.removeItem(cacheKey);
  };

  // 初始化时从缓存恢复
  useEffect(() => {
    if (enabled) {
      const restored = restoreFromCache();
      if (!restored && autoLoad) {
        // 延迟一点执行，避免阻塞UI
        setTimeout(() => {
          performLoad();
        }, 100);
      }
    }
  }, [enabled, autoLoad]); // eslint-disable-line react-hooks/exhaustive-deps

  return {
    loading,
    loaded,
    error,
    load: performLoad,
    reload,
    clearCache
  };
};

export default useLazyLoading;