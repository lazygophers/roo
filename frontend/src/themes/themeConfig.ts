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

// 蓝色明亮主题
export const blueTheme: ExtendedThemeConfig = {
  name: 'Blue Light',
  description: '蓝色明亮主题',
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

// 蓝色深色主题
export const blueDarkTheme: ExtendedThemeConfig = {
  name: 'Blue Dark',
  description: '蓝色深色主题',
  preview: {
    primary: '#597ef7',
    background: '#111b58',
    surface: '#1a2980',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#597ef7',
    colorInfo: '#597ef7',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#1a2980',
    colorBgElevated: '#2f4091',
    colorBgLayout: '#111b58',
    colorBgSpotlight: '#3851c4',
    colorBorder: '#434ea6',
    colorBorderSecondary: '#2f4091',
    colorFill: '#1a2980',
    colorFillSecondary: '#2f4091',
    colorFillTertiary: '#434ea6',
    colorText: '#ffffffd9',
    colorTextSecondary: '#ffffff73',
    colorTextTertiary: '#ffffff40',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#111b58',
      headerBg: '#1a2980',
      siderBg: '#111b58',
    },
    Menu: {
      darkItemBg: '#111b58',
      darkItemSelectedBg: '#597ef7',
      darkItemHoverBg: '#2f4091',
    },
    Card: {
      colorBgContainer: '#1a2980',
      colorBorderSecondary: '#434ea6',
    },
    Input: {
      colorBgContainer: '#1a2980',
      colorBorder: '#434ea6',
    },
    Select: {
      colorBgContainer: '#1a2980',
      colorBorder: '#434ea6',
    },
    Button: {
      colorBgContainer: '#1a2980',
      colorBorder: '#434ea6',
    },
  },
};

// 绿色明亮主题
export const greenTheme: ExtendedThemeConfig = {
  name: 'Green Light',
  description: '绿色明亮主题',
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

// 绿色深色主题
export const greenDarkTheme: ExtendedThemeConfig = {
  name: 'Green Dark',
  description: '绿色深色主题',
  preview: {
    primary: '#73d13d',
    background: '#162312',
    surface: '#274916',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#73d13d',
    colorInfo: '#73d13d',
    colorSuccess: '#73d13d',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#274916',
    colorBgElevated: '#3f6622',
    colorBgLayout: '#162312',
    colorBgSpotlight: '#52c41a',
    colorBorder: '#52844a',
    colorBorderSecondary: '#3f6622',
    colorFill: '#274916',
    colorFillSecondary: '#3f6622',
    colorFillTertiary: '#52844a',
    colorText: '#ffffffd9',
    colorTextSecondary: '#ffffff73',
    colorTextTertiary: '#ffffff40',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#162312',
      headerBg: '#274916',
      siderBg: '#162312',
    },
    Menu: {
      darkItemBg: '#162312',
      darkItemSelectedBg: '#73d13d',
      darkItemHoverBg: '#3f6622',
    },
    Card: {
      colorBgContainer: '#274916',
      colorBorderSecondary: '#52844a',
    },
    Input: {
      colorBgContainer: '#274916',
      colorBorder: '#52844a',
    },
    Select: {
      colorBgContainer: '#274916',
      colorBorder: '#52844a',
    },
    Button: {
      colorBgContainer: '#274916',
      colorBorder: '#52844a',
    },
  },
};

// 紫色明亮主题
export const purpleTheme: ExtendedThemeConfig = {
  name: 'Purple Light',
  description: '紫色明亮主题',
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

// 紫色深色主题
export const purpleDarkTheme: ExtendedThemeConfig = {
  name: 'Purple Dark',
  description: '紫色深色主题',
  preview: {
    primary: '#b37feb',
    background: '#22075e',
    surface: '#391085',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#b37feb',
    colorInfo: '#b37feb',
    colorSuccess: '#52c41a',
    colorWarning: '#faad14',
    colorError: '#f5222d',
    colorBgContainer: '#391085',
    colorBgElevated: '#531dab',
    colorBgLayout: '#22075e',
    colorBgSpotlight: '#722ed1',
    colorBorder: '#723dc4',
    colorBorderSecondary: '#531dab',
    colorFill: '#391085',
    colorFillSecondary: '#531dab',
    colorFillTertiary: '#723dc4',
    colorText: '#ffffffd9',
    colorTextSecondary: '#ffffff73',
    colorTextTertiary: '#ffffff40',
    borderRadius: 8,
    borderRadiusLG: 12,
    borderRadiusSM: 4,
  },
  components: {
    Layout: {
      bodyBg: '#22075e',
      headerBg: '#391085',
      siderBg: '#22075e',
    },
    Menu: {
      darkItemBg: '#22075e',
      darkItemSelectedBg: '#b37feb',
      darkItemHoverBg: '#531dab',
    },
    Card: {
      colorBgContainer: '#391085',
      colorBorderSecondary: '#723dc4',
    },
    Input: {
      colorBgContainer: '#391085',
      colorBorder: '#723dc4',
    },
    Select: {
      colorBgContainer: '#391085',
      colorBorder: '#723dc4',
    },
    Button: {
      colorBgContainer: '#391085',
      colorBorder: '#723dc4',
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
  blueDark: blueDarkTheme,
  green: greenTheme,
  greenDark: greenDarkTheme,
  purple: purpleTheme,
  purpleDark: purpleDarkTheme,
  compactDark: compactDarkTheme,
};

export type ThemeName = keyof typeof themeRegistry;