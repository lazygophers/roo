import { useState, useEffect, useRef } from 'react';

export interface LazyLoadingOptions {
  /** 是否启用惰性加载 */
  enabled?: boolean;
  /** 组件标识符 */
  key?: string;
  /** 是否自动加载（如果为false，需要手动调用load） */
  autoLoad?: boolean;
  /** 缓存时间（毫秒），0表示不缓存，-1表示页面级缓存（离开页面时清除） */
  cacheTime?: number;
  /** 页面标识符，用于页面级缓存管理 */
  pageKey?: string;
}

export interface LazyLoadingState {
  /** 是否正在加载 */
  loading: boolean;
  /** 是否已加载过 */
  loaded: boolean;
  /** 是否有错误 */
  error: Error | null;
  /** 手动触发加载 */
  load: () => Promise<void>;
  /** 重新加载 */
  reload: () => void;
  /** 清除缓存 */
  clearCache: () => void;
  /** 清除整个页面的缓存 */
  clearPageCache: () => void;
}

// 全局页面级缓存管理
const pageCacheManager = {
  caches: new Map<string, Map<string, any>>(),

  getPageCache(pageKey: string): Map<string, any> {
    if (!this.caches.has(pageKey)) {
      this.caches.set(pageKey, new Map());
    }
    return this.caches.get(pageKey)!;
  },

  clearPageCache(pageKey: string) {
    this.caches.delete(pageKey);
  },

  get(pageKey: string, key: string) {
    return this.getPageCache(pageKey).get(key);
  },

  set(pageKey: string, key: string, value: any) {
    this.getPageCache(pageKey).set(key, value);
  },

  has(pageKey: string, key: string) {
    return this.getPageCache(pageKey).has(key);
  }
};

/**
 * 惰性加载Hook，支持页面级缓存和手动控制
 */
export const useLazyLoading = (
  loadFunction: () => Promise<void>,
  options: LazyLoadingOptions = {}
): LazyLoadingState => {
  const {
    enabled = true,
    key = 'default',
    autoLoad = true,
    cacheTime = 5 * 60 * 1000, // 默认5分钟缓存
    pageKey = 'default'
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
    if (cacheTime === -1) {
      // 页面级缓存，检查内存中的缓存
      return pageCacheManager.has(pageKey, key);
    }
    const lastLoadTime = lastLoadTimeRef.current;
    return lastLoadTime > 0 && (Date.now() - lastLoadTime) < cacheTime;
  };

  // 从缓存中恢复状态
  const restoreFromCache = () => {
    if (cacheTime === -1) {
      // 页面级缓存，从内存恢复
      const cached = pageCacheManager.get(pageKey, key);
      if (cached && cached.loaded) {
        setLoaded(true);
        loadedRef.current = true;
        lastLoadTimeRef.current = cached.loadTime;
        console.log(`[useLazyLoading] Restored from page cache for key: ${key}`);
        return true;
      }
    } else if (cacheTime > 0) {
      // 时间缓存，从 sessionStorage 恢复
      const cached = sessionStorage.getItem(cacheKey);
      if (cached) {
        try {
          const { loadTime, loaded: cachedLoaded } = JSON.parse(cached);
          if (cachedLoaded && (Date.now() - loadTime) < cacheTime) {
            setLoaded(true);
            loadedRef.current = true;
            lastLoadTimeRef.current = loadTime;
            console.log(`[useLazyLoading] Restored from session cache for key: ${key}`);
            return true;
          }
        } catch (e) {
          // 忽略缓存解析错误
        }
      }
    }
    return false;
  };

  // 保存到缓存
  const saveToCache = () => {
    const loadTime = Date.now();
    if (cacheTime === -1) {
      // 页面级缓存，保存到内存
      pageCacheManager.set(pageKey, key, { loaded: true, loadTime });
      console.log(`[useLazyLoading] Saved to page cache for key: ${key}`);
    } else if (cacheTime > 0) {
      // 时间缓存，保存到 sessionStorage
      const cacheData = { loadTime, loaded: true };
      sessionStorage.setItem(cacheKey, JSON.stringify(cacheData));
      console.log(`[useLazyLoading] Saved to session cache for key: ${key}`);
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
    if (cacheTime === -1) {
      // 页面级缓存，从内存清除
      pageCacheManager.getPageCache(pageKey).delete(key);
    } else {
      // 时间缓存，从 sessionStorage 清除
      sessionStorage.removeItem(cacheKey);
    }
  };

  // 清除整个页面的缓存
  const clearPageCache = () => {
    pageCacheManager.clearPageCache(pageKey);
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
    clearCache,
    clearPageCache
  };
};

// 导出页面缓存管理器，供外部使用
export { pageCacheManager };

export default useLazyLoading;