import React, { createContext, useContext, useState, useEffect } from 'react';
import { themeRegistry, ThemeName, ExtendedThemeConfig } from '../themes/themeConfig';

interface ThemeContextType {
  themeType: ThemeName;
  currentTheme: ExtendedThemeConfig;
  setThemeType: (theme: ThemeName) => void;
}

const ThemeContext = createContext<ThemeContextType | undefined>(undefined);

interface ThemeProviderProps {
  children: React.ReactNode;
}

export const ThemeProvider: React.FC<ThemeProviderProps> = ({ children }) => {
  const [themeType, setThemeTypeState] = useState<ThemeName>(() => {
    const saved = localStorage.getItem('theme-type');
    const defaultTheme = (saved as ThemeName) || 'nightRain'; // 默认夜雨如诗深色模式
    // 确保主题存在，否则使用第一个可用主题
    return themeRegistry[defaultTheme] ? defaultTheme : Object.keys(themeRegistry)[0] as ThemeName;
  });

  const currentTheme = themeRegistry[themeType] || themeRegistry[Object.keys(themeRegistry)[0] as ThemeName];

  // 更新主题类型
  const setThemeType = (newTheme: ThemeName) => {
    setThemeTypeState(newTheme);
    localStorage.setItem('theme-type', newTheme);
  };

  // 根据主题判断是否为深色模式
  const isDark = themeType === 'nightRain' || themeType === 'plumRain' || 
                 themeType === 'deepSeaMoon' || themeType === 'greenMountain';

  // 更新body类名以支持全局样式
  useEffect(() => {
    const themeClass = isDark ? 'dark-theme' : 'light-theme';
    document.body.className = `${themeClass} theme-${themeType}`;
  }, [isDark, themeType]);

  const contextValue: ThemeContextType = {
    themeType,
    currentTheme,
    setThemeType,
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