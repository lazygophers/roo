import React, { createContext, useContext, useState, useEffect } from 'react';
import { theme } from 'antd';
import { themeRegistry, ThemeName, ExtendedThemeConfig } from '../themes/themeConfig';

export type ThemeType = 'light' | 'dark' | 'auto';

interface ThemeContextType {
  themeType: ThemeType;
  themeName: ThemeName;
  isDark: boolean;
  currentTheme: ExtendedThemeConfig;
  availableThemes: Record<ThemeName, ExtendedThemeConfig>;
  setThemeType: (theme: ThemeType) => void;
  setThemeName: (name: ThemeName) => void;
  toggleTheme: () => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [themeType, setThemeTypeState] = useState<ThemeType>(() => {
    const saved = localStorage.getItem('theme-type');
    return (saved as ThemeType) || 'dark'; // 默认深色模式
  });

  const [themeName, setThemeNameState] = useState<ThemeName>(() => {
    const saved = localStorage.getItem('theme-name');
    return (saved as ThemeName) || 'dark'; // 默认深色主题
  });

  const [isDark, setIsDark] = useState(() => {
    if (themeType === 'auto') {
      return window.matchMedia('(prefers-color-scheme: dark)').matches;
    }
    return themeType === 'dark' || themeName === 'dark' || themeName === 'compactDark';
  });

  // 获取当前主题配置
  const getCurrentTheme = (): ExtendedThemeConfig => {
    if (themeType === 'auto') {
      return isDark ? themeRegistry.dark : themeRegistry.light;
    } else if (themeType === 'dark') {
      return themeRegistry.dark;
    } else if (themeType === 'light') {
      return themeRegistry.light;
    }
    return themeRegistry[themeName];
  };

  const [currentTheme, setCurrentTheme] = useState<ExtendedThemeConfig>(getCurrentTheme);

  // 监听系统主题变化
  useEffect(() => {
    if (themeType === 'auto') {
      const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
      const handleChange = (e: MediaQueryListEvent) => {
        setIsDark(e.matches);
      };
      
      mediaQuery.addEventListener('change', handleChange);
      return () => mediaQuery.removeEventListener('change', handleChange);
    }
  }, [themeType]);

  // 更新主题类型
  const setThemeType = (newTheme: ThemeType) => {
    setThemeTypeState(newTheme);
    localStorage.setItem('theme-type', newTheme);
    
    if (newTheme === 'auto') {
      const systemDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
      setIsDark(systemDark);
      setThemeNameState(systemDark ? 'dark' : 'light');
    } else {
      setIsDark(newTheme === 'dark');
      setThemeNameState(newTheme === 'dark' ? 'dark' : 'light');
    }
  };

  // 设置具体主题
  const setThemeName = (name: ThemeName) => {
    setThemeNameState(name);
    localStorage.setItem('theme-name', name);
    
    const theme = themeRegistry[name];
    const isDarkTheme = name === 'dark' || name === 'compactDark';
    setIsDark(isDarkTheme);
    
    if (isDarkTheme) {
      setThemeTypeState('dark');
    } else {
      setThemeTypeState('light');
    }
  };

  // 切换明暗主题
  const toggleTheme = () => {
    if (themeType === 'auto') {
      setThemeType('light');
    } else if (themeType === 'light') {
      setThemeType('dark');
    } else {
      setThemeType('light');
    }
  };

  // 更新当前主题
  useEffect(() => {
    setCurrentTheme(getCurrentTheme());
  }, [themeType, themeName, isDark]);

  // 更新body类名以支持全局样式
  useEffect(() => {
    const themeClass = isDark ? 'dark-theme' : 'light-theme';
    document.body.className = `${themeClass} theme-${themeName}`;
  }, [isDark, themeName]);

  const contextValue: ThemeContextType = {
    themeType,
    themeName,
    isDark,
    currentTheme,
    availableThemes: themeRegistry,
    setThemeType,
    setThemeName,
    toggleTheme,
  };

  return (
    <ThemeContext.Provider value={contextValue}>
      {children}
    </ThemeContext.Provider>
  );
};

export const useTheme = (): ThemeContextType => {
  const context = useContext(ThemeContext);
  if (context === undefined) {
    throw new Error('useTheme must be used within a ThemeProvider');
  }
  return context;
};