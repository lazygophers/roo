import { useEffect } from 'react';

/**
 * 自定义 Hook：动态设置页面标题
 * @param title 页面标题
 * @param suffix 标题后缀，默认为应用名称
 */
export const useDocumentTitle = (title: string, suffix = 'LazyAI Studio') => {
  useEffect(() => {
    const prevTitle = document.title;
    const newTitle = title ? `${title} - ${suffix}` : suffix;
    document.title = newTitle;

    // 清理函数，在组件卸载时恢复原标题
    return () => {
      document.title = prevTitle;
    };
  }, [title, suffix]);
};

/**
 * 动态设置页面标题的函数版本
 * @param title 页面标题
 * @param suffix 标题后缀
 */
export const setDocumentTitle = (title: string, suffix = 'LazyAI Studio') => {
  const newTitle = title ? `${title} - ${suffix}` : suffix;
  document.title = newTitle;
};

export default useDocumentTitle;