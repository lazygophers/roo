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

// 雾霭晨光 - 莫兰迪灰调明亮主题
export const morningMistTheme: ExtendedThemeConfig = {
  name: 'Morning Mist',
  description: '雾霭晨光',
  preview: {
    primary: '#8B9DC3',
    background: '#F5F5F0',
    surface: '#FAFAF8',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#8B9DC3',
    colorInfo: '#8B9DC3',
    colorSuccess: '#A8C09A',
    colorWarning: '#E6C79C',
    colorError: '#D4A5A5',
    colorBgContainer: '#FAFAF8',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: '#F5F5F0',
    colorBgSpotlight: '#F0F0ED',
    colorBorder: '#E8E8E3',
    colorBorderSecondary: '#F0F0ED',
    colorFill: '#F8F8F5',
    colorFillSecondary: '#F3F3F0',
    colorFillTertiary: '#EDEDE8',
    colorText: '#5A5A54',
    colorTextSecondary: '#8A8A82',
    colorTextTertiary: '#B5B5AD',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#F5F5F0',
      headerBg: '#FAFAF8',
      siderBg: '#F8F8F5',
    },
    Menu: {
      itemBg: '#FAFAF8',
      itemSelectedBg: '#E8E8E3',
      itemHoverBg: '#F0F0ED',
    },
    Card: {
      colorBgContainer: '#FAFAF8',
      colorBorderSecondary: '#E8E8E3',
    },
    Input: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E8E8E3',
    },
    Select: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E8E8E3',
    },
    Button: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E8E8E3',
    },
  },
};

// 夜雨如诗 - 莫兰迪灰调深色主题
export const nightRainTheme: ExtendedThemeConfig = {
  name: 'Night Rain',
  description: '夜雨如诗',
  preview: {
    primary: '#9BB5D1',
    background: '#1a1b19',
    surface: '#2a2b28',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#9BB5D1',
    colorInfo: '#9BB5D1',
    colorSuccess: '#8FA584',
    colorWarning: '#C4A882',
    colorError: '#B89090',
    colorBgContainer: '#2a2b28',
    colorBgElevated: '#32332f',
    colorBgLayout: '#1a1b19',
    colorBgSpotlight: '#3a3b37',
    colorBorder: '#42433f',
    colorBorderSecondary: '#32332f',
    colorFill: '#2a2b28',
    colorFillSecondary: '#32332f',
    colorFillTertiary: '#3a3b37',
    colorText: '#E8E8E3',
    colorTextSecondary: '#C8C8C3',
    colorTextTertiary: '#A8A8A3',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#1a1b19',
      headerBg: '#2a2b28',
      siderBg: '#1a1b19',
    },
    Menu: {
      darkItemBg: '#1a1b19',
      darkItemSelectedBg: '#9BB5D1',
      darkItemHoverBg: '#32332f',
    },
    Card: {
      colorBgContainer: '#2a2b28',
      colorBorderSecondary: '#42433f',
    },
    Input: {
      colorBgContainer: '#2a2b28',
      colorBorder: '#42433f',
    },
    Select: {
      colorBgContainer: '#2a2b28',
      colorBorder: '#42433f',
    },
    Button: {
      colorBgContainer: '#2a2b28',
      colorBorder: '#42433f',
    },
  },
};

// 桃花春雨 - 莫兰迪粉调明亮主题
export const peachBlossomTheme: ExtendedThemeConfig = {
  name: 'Peach Blossom',
  description: '桃花春雨',
  preview: {
    primary: '#C8A2C8',
    background: '#F8F5F5',
    surface: '#FDFCFC',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#C8A2C8',
    colorInfo: '#C8A2C8',
    colorSuccess: '#B5C4B1',
    colorWarning: '#E8C5A0',
    colorError: '#D4A5A5',
    colorBgContainer: '#FDFCFC',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: '#F8F5F5',
    colorBgSpotlight: '#F3F0F0',
    colorBorder: '#EBEBE8',
    colorBorderSecondary: '#F3F0F0',
    colorFill: '#FAF8F8',
    colorFillSecondary: '#F5F3F3',
    colorFillTertiary: '#F0EDED',
    colorText: '#5A5456',
    colorTextSecondary: '#8A8285',
    colorTextTertiary: '#B5B0B2',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#F8F5F5',
      headerBg: '#FDFCFC',
      siderBg: '#FAF8F8',
    },
    Menu: {
      itemBg: '#FDFCFC',
      itemSelectedBg: '#F0EDED',
      itemHoverBg: '#F3F0F0',
    },
    Card: {
      colorBgContainer: '#FDFCFC',
      colorBorderSecondary: '#EBEBE8',
    },
    Input: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#EBEBE8',
    },
    Select: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#EBEBE8',
    },
    Button: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#EBEBE8',
    },
  },
};

// 梅雨黄昏 - 莫兰迪粉调深色主题
export const plumRainTheme: ExtendedThemeConfig = {
  name: 'Plum Rain',
  description: '梅雨黄昏',
  preview: {
    primary: '#C8A2C8',
    background: '#1f1a1a',
    surface: '#2f2828',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#C8A2C8',
    colorInfo: '#C8A2C8',
    colorSuccess: '#8FA584',
    colorWarning: '#C4A882',
    colorError: '#B89090',
    colorBgContainer: '#2f2828',
    colorBgElevated: '#373030',
    colorBgLayout: '#1f1a1a',
    colorBgSpotlight: '#3f3838',
    colorBorder: '#4f4545',
    colorBorderSecondary: '#373030',
    colorFill: '#2f2828',
    colorFillSecondary: '#373030',
    colorFillTertiary: '#3f3838',
    colorText: '#E8E3E3',
    colorTextSecondary: '#C8C3C3',
    colorTextTertiary: '#A8A3A3',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#1f1a1a',
      headerBg: '#2f2828',
      siderBg: '#1f1a1a',
    },
    Menu: {
      darkItemBg: '#1f1a1a',
      darkItemSelectedBg: '#C8A2C8',
      darkItemHoverBg: '#373030',
    },
    Card: {
      colorBgContainer: '#2f2828',
      colorBorderSecondary: '#4f4545',
    },
    Input: {
      colorBgContainer: '#2f2828',
      colorBorder: '#4f4545',
    },
    Select: {
      colorBgContainer: '#2f2828',
      colorBorder: '#4f4545',
    },
    Button: {
      colorBgContainer: '#2f2828',
      colorBorder: '#4f4545',
    },
  },
};

// 溪水潺潺 - 莫兰迪蓝调明亮主题
export const streamFlowTheme: ExtendedThemeConfig = {
  name: 'Stream Flow',
  description: '溪水潺潺',
  preview: {
    primary: '#9BB5D1',
    background: '#F3F6F8',
    surface: '#FAFCFD',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#9BB5D1',
    colorInfo: '#9BB5D1',
    colorSuccess: '#A8C09A',
    colorWarning: '#E6C79C',
    colorError: '#D4A5A5',
    colorBgContainer: '#FAFCFD',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: '#F3F6F8',
    colorBgSpotlight: '#EDF2F5',
    colorBorder: '#E3E8EB',
    colorBorderSecondary: '#EDF2F5',
    colorFill: '#F7FAFB',
    colorFillSecondary: '#F0F5F7',
    colorFillTertiary: '#EAEEF2',
    colorText: '#4A5568',
    colorTextSecondary: '#7A8396',
    colorTextTertiary: '#A5B2C1',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#F3F6F8',
      headerBg: '#FAFCFD',
      siderBg: '#F7FAFB',
    },
    Menu: {
      itemBg: '#FAFCFD',
      itemSelectedBg: '#EAEEF2',
      itemHoverBg: '#EDF2F5',
    },
    Card: {
      colorBgContainer: '#FAFCFD',
      colorBorderSecondary: '#E3E8EB',
    },
    Input: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E3E8EB',
    },
    Select: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E3E8EB',
    },
    Button: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E3E8EB',
    },
  },
};

// 深海月色 - 莫兰迪蓝调深色主题
export const deepSeaMoonTheme: ExtendedThemeConfig = {
  name: 'Deep Sea Moon',
  description: '深海月色',
  preview: {
    primary: '#9BB5D1',
    background: '#161a1f',
    surface: '#242832',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#9BB5D1',
    colorInfo: '#9BB5D1',
    colorSuccess: '#8FA584',
    colorWarning: '#C4A882',
    colorError: '#B89090',
    colorBgContainer: '#242832',
    colorBgElevated: '#2c303a',
    colorBgLayout: '#161a1f',
    colorBgSpotlight: '#343842',
    colorBorder: '#44485f',
    colorBorderSecondary: '#2c303a',
    colorFill: '#242832',
    colorFillSecondary: '#2c303a',
    colorFillTertiary: '#343842',
    colorText: '#E3E8EB',
    colorTextSecondary: '#C3C8CB',
    colorTextTertiary: '#A3A8AB',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#161a1f',
      headerBg: '#242832',
      siderBg: '#161a1f',
    },
    Menu: {
      darkItemBg: '#161a1f',
      darkItemSelectedBg: '#9BB5D1',
      darkItemHoverBg: '#2c303a',
    },
    Card: {
      colorBgContainer: '#242832',
      colorBorderSecondary: '#44485f',
    },
    Input: {
      colorBgContainer: '#242832',
      colorBorder: '#44485f',
    },
    Select: {
      colorBgContainer: '#242832',
      colorBorder: '#44485f',
    },
    Button: {
      colorBgContainer: '#242832',
      colorBorder: '#44485f',
    },
  },
};

// 竹林晨露 - 莫兰迪绿调明亮主题
export const bambooForestTheme: ExtendedThemeConfig = {
  name: 'Bamboo Forest',
  description: '竹林晨露',
  preview: {
    primary: '#A8C09A',
    background: '#F5F8F3',
    surface: '#FBFCFA',
  },
  algorithm: theme.defaultAlgorithm,
  token: {
    colorPrimary: '#A8C09A',
    colorInfo: '#A8C09A',
    colorSuccess: '#A8C09A',
    colorWarning: '#E6C79C',
    colorError: '#D4A5A5',
    colorBgContainer: '#FBFCFA',
    colorBgElevated: '#FFFFFF',
    colorBgLayout: '#F5F8F3',
    colorBgSpotlight: '#EEF2ED',
    colorBorder: '#E5EBE3',
    colorBorderSecondary: '#EEF2ED',
    colorFill: '#F8FAF7',
    colorFillSecondary: '#F2F5F0',
    colorFillTertiary: '#EBEEE9',
    colorText: '#4A5A48',
    colorTextSecondary: '#7A8A76',
    colorTextTertiary: '#A5B5A1',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#F5F8F3',
      headerBg: '#FBFCFA',
      siderBg: '#F8FAF7',
    },
    Menu: {
      itemBg: '#FBFCFA',
      itemSelectedBg: '#EBEEE9',
      itemHoverBg: '#EEF2ED',
    },
    Card: {
      colorBgContainer: '#FBFCFA',
      colorBorderSecondary: '#E5EBE3',
    },
    Input: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E5EBE3',
    },
    Select: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E5EBE3',
    },
    Button: {
      colorBgContainer: '#FFFFFF',
      colorBorder: '#E5EBE3',
    },
  },
};

// 青山暮雪 - 莫兰迪绿调深色主题
export const greenMountainTheme: ExtendedThemeConfig = {
  name: 'Green Mountain',
  description: '青山暮雪',
  preview: {
    primary: '#A8C09A',
    background: '#161a16',
    surface: '#242a24',
  },
  algorithm: theme.darkAlgorithm,
  token: {
    colorPrimary: '#A8C09A',
    colorInfo: '#A8C09A',
    colorSuccess: '#A8C09A',
    colorWarning: '#C4A882',
    colorError: '#B89090',
    colorBgContainer: '#242a24',
    colorBgElevated: '#2c322c',
    colorBgLayout: '#161a16',
    colorBgSpotlight: '#343a34',
    colorBorder: '#444a44',
    colorBorderSecondary: '#2c322c',
    colorFill: '#242a24',
    colorFillSecondary: '#2c322c',
    colorFillTertiary: '#343a34',
    colorText: '#E5EBE3',
    colorTextSecondary: '#C5CBC3',
    colorTextTertiary: '#A5ABA3',
    borderRadius: 12,
    borderRadiusLG: 16,
    borderRadiusSM: 8,
  },
  components: {
    Layout: {
      bodyBg: '#161a16',
      headerBg: '#242a24',
      siderBg: '#161a16',
    },
    Menu: {
      darkItemBg: '#161a16',
      darkItemSelectedBg: '#A8C09A',
      darkItemHoverBg: '#2c322c',
    },
    Card: {
      colorBgContainer: '#242a24',
      colorBorderSecondary: '#444a44',
    },
    Input: {
      colorBgContainer: '#242a24',
      colorBorder: '#444a44',
    },
    Select: {
      colorBgContainer: '#242a24',
      colorBorder: '#444a44',
    },
    Button: {
      colorBgContainer: '#242a24',
      colorBorder: '#444a44',
    },
  },
};

export const themeRegistry = {
  morningMist: morningMistTheme,
  nightRain: nightRainTheme,
  peachBlossom: peachBlossomTheme,
  plumRain: plumRainTheme,
  streamFlow: streamFlowTheme,
  deepSeaMoon: deepSeaMoonTheme,
  bambooForest: bambooForestTheme,
  greenMountain: greenMountainTheme,
};

export type ThemeName = keyof typeof themeRegistry;