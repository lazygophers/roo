import { ThemeConfig, theme } from 'antd';

export interface ExtendedThemeConfig extends ThemeConfig {
  name: string;
  description: string;
  preview: {
    primary: string;
    background: string;
    surface: string;
  };
}

// 深色主题
export const darkTheme: ExtendedThemeConfig = {
  name: 'Dark',
  description: '深色主题',
  preview: {
    primary: '#1890ff',
    background: '#000000',
    surface: '#141414',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorInfo: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#141414',
    colorBgElevated: '#1f1f1f',
    colorBgLayout: '#000000',
    colorBgSpotlight: '#424242',
    colorBorder: '#434343',
    colorBorderSecondary: '#424242',
    colorFill: '#1f1f1f',
    colorFillSecondary: '#303030',
    colorFillTertiary: '#434343',
    colorFillQuaternary: '#595959',
    colorText: '#ffffffd9',
    colorTextSecondary: '#ffffff73',
    colorTextTertiary: '#ffffff40',
    colorTextQuaternary: '#ffffff26',
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    boxShadow: '0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
  },
  components: {
    Layout: {
      bodyBg: '#000000',
      headerBg: '#141414',
      siderBg: '#001529',
    },
    Menu: {
      darkItemBg: '#001529',
      darkItemSelectedBg: '#1890ff',
      darkItemHoverBg: '#112545',
    },
    Card: {
      colorBgContainer: '#141414',
      colorBorderSecondary: '#434343',
    },
    Input: {
      colorBgContainer: '#1f1f1f',
      colorBorder: '#434343',
    },
    Select: {
      colorBgContainer: '#1f1f1f',
      colorBorder: '#434343',
    },
    Button: {
      colorBgContainer: '#1f1f1f',
      colorBorder: '#434343',
    },
  },
};

// 浅色主题
export const lightTheme: ExtendedThemeConfig = {
  name: 'Light',
  description: '浅色主题',
  preview: {
    primary: '#1890ff',
    background: '#ffffff',
    surface: '#f5f5f5',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    colorInfo: '#1890ff',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f0f2f5',
    colorBgSpotlight: '#ffffff',
    colorBorder: '#d9d9d9',
    colorBorderSecondary: '#f0f0f0',
    colorFill: '#f5f5f5',
    colorFillSecondary: '#fafafa',
    colorFillTertiary: '#f0f0f0',
    colorFillQuaternary: '#f5f5f5',
    colorText: '#000000d9',
    colorTextSecondary: '#00000073',
    colorTextTertiary: '#00000040',
    colorTextQuaternary: '#00000026',
    borderRadius: 6,
    borderRadiusLG: 8,
    borderRadiusSM: 4,
    boxShadow: '0 6px 16px 0 rgba(0, 0, 0, 0.08), 0 3px 6px -4px rgba(0, 0, 0, 0.12), 0 9px 28px 8px rgba(0, 0, 0, 0.05)',
  },
  components: {
    Layout: {
      bodyBg: '#f0f2f5',
      headerBg: '#ffffff',
      siderBg: '#ffffff',
    },
    Menu: {
      itemBg: '#ffffff',
      itemSelectedBg: '#e6f7ff',
      itemHoverBg: '#f5f5f5',
    },
    Card: {
      colorBgContainer: '#ffffff',
      colorBorderSecondary: '#f0f0f0',
    },
    Input: {
      colorBgContainer: '#ffffff',
      colorBorder: '#d9d9d9',
    },
    Select: {
      colorBgContainer: '#ffffff',
      colorBorder: '#d9d9d9',
    },
    Button: {
      colorBgContainer: '#ffffff',
      colorBorder: '#d9d9d9',
    },
  },
};

// 蓝色主题
export const blueTheme: ExtendedThemeConfig = {
  name: 'Blue',
  description: '蓝色主题',
  preview: {
    primary: '#2f54eb',
    background: '#f0f5ff',
    surface: '#ffffff',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#2f54eb',
    colorInfo: '#2f54eb',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f0f5ff',
    colorBgSpotlight: '#e6f7ff',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#f0f5ff',
      headerBg: '#ffffff',
      siderBg: '#e6f7ff',
    },
    Menu: {
      itemSelectedBg: '#bae7ff',
      itemHoverBg: '#e6f7ff',
    },
  },
};

// 绿色主题
export const greenTheme: ExtendedThemeConfig = {
  name: 'Green',
  description: '绿色主题',
  preview: {
    primary: '#52c41a',
    background: '#f6ffed',
    surface: '#ffffff',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#52c41a',
    colorInfo: '#52c41a',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f6ffed',
    colorBgSpotlight: '#d9f7be',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#f6ffed',
      headerBg: '#ffffff',
      siderBg: '#f6ffed',
    },
    Menu: {
      itemSelectedBg: '#d9f7be',
      itemHoverBg: '#f6ffed',
    },
  },
};

// 紫色主题
export const purpleTheme: ExtendedThemeConfig = {
  name: 'Purple',
  description: '紫色主题',
  preview: {
    primary: '#722ed1',
    background: '#f9f0ff',
    surface: '#ffffff',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#722ed1',
    colorInfo: '#722ed1',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#ffffff',
    colorBgElevated: '#ffffff',
    colorBgLayout: '#f9f0ff',
    colorBgSpotlight: '#efdbff',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#f9f0ff',
      headerBg: '#ffffff',
      siderBg: '#f9f0ff',
    },
    Menu: {
      itemSelectedBg: '#efdbff',
      itemHoverBg: '#f9f0ff',
    },
  },
};

// 紧凑深色主题
export const compactDarkTheme: ExtendedThemeConfig = {
  name: 'CompactDark',
  description: '紧凑深色主题',
  preview: {
    primary: '#1890ff',
    background: '#141414',
    surface: '#262626',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    ...darkTheme.token,
    borderRadius: 2,
    borderRadiusLG: 4,
    borderRadiusSM: 2,
    sizeStep: 3,
    controlHeight: 28,
  },
  components: {
    ...darkTheme.components,
    Button: {
      ...darkTheme.components?.Button,
      controlHeight: 28,
      paddingContentHorizontal: 8,
    },
    Input: {
      ...darkTheme.components?.Input,
      controlHeight: 28,
      paddingContentHorizontal: 8,
    },
  },
};

export const themeRegistry = {
  dark: darkTheme,
  light: lightTheme,
  blue: blueTheme,
  green: greenTheme,
  purple: purpleTheme,
  compactDark: compactDarkTheme,
};

export type ThemeName = keyof typeof themeRegistry;