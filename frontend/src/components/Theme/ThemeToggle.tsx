import React from 'react';
import { Button, Dropdown, Space, theme, Divider } from 'antd';
import { 
  BulbOutlined, 
  BulbFilled, 
  DesktopOutlined,
  SunOutlined,
  MoonOutlined,
  BgColorsOutlined
} from '@ant-design/icons';
import { useTheme, ThemeType } from '../../contexts/ThemeContext';
import { ThemeName } from '../../themes/themeConfig';

const ThemeToggle: React.FC = () => {
  const { themeType, themeName, isDark, availableThemes, setThemeType, setThemeName, toggleTheme } = useTheme();
  const { token } = theme.useToken();

  const getThemeIcon = (theme?: ThemeName) => {
    const currentTheme = theme || themeName;
    
    if (currentTheme === 'dark' || currentTheme === 'compactDark') {
      return <MoonOutlined />;
    } else if (currentTheme === 'light') {
      return <SunOutlined />;
    } else if (currentTheme === 'blue') {
      return <BgColorsOutlined style={{ color: '#2f54eb' }} />;
    } else if (currentTheme === 'green') {
      return <BgColorsOutlined style={{ color: '#52c41a' }} />;
    } else if (currentTheme === 'purple') {
      return <BgColorsOutlined style={{ color: '#722ed1' }} />;
    }
    
    return <BgColorsOutlined />;
  };

  const getThemeLabel = () => {
    const theme = availableThemes[themeName];
    return theme ? theme.description : '主题';
  };

  // 创建主题预览小圆点
  const ThemePreview: React.FC<{ name: ThemeName }> = ({ name }) => {
    const theme = availableThemes[name];
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <div style={{
          width: 12,
          height: 12,
          borderRadius: 6,
          background: `linear-gradient(45deg, ${theme.preview.primary}, ${theme.preview.surface})`,
          border: `1px solid ${theme.preview.primary}`,
          marginRight: 4
        }} />
        <span>{theme.description}</span>
      </div>
    );
  };

  const basicThemeItems = [
    {
      key: 'light',
      icon: <SunOutlined />,
      label: '浅色模式',
      onClick: () => setThemeType('light'),
    },
    {
      key: 'dark',
      icon: <MoonOutlined />,
      label: '深色模式',  
      onClick: () => setThemeType('dark'),
    },
    {
      key: 'auto',
      icon: <DesktopOutlined />,
      label: '跟随系统',
      onClick: () => setThemeType('auto'),
    },
  ];

  const customThemeItems = Object.entries(availableThemes).map(([key, theme]) => ({
    key,
    icon: getThemeIcon(key as ThemeName),
    label: <ThemePreview name={key as ThemeName} />,
    onClick: () => setThemeName(key as ThemeName),
  }));

  const menuItems = [
    ...basicThemeItems,
    { type: 'divider' as const },
    {
      key: 'custom-themes',
      label: '自定义主题',
      type: 'group' as const,
      children: customThemeItems,
    },
  ];

  return (
    <Dropdown
      menu={{ items: menuItems, selectedKeys: [themeName] }}
      placement="bottomRight"
      arrow
      trigger={['click']}
    >
      <Button
        type="text"
        size="small"
        style={{
          color: token.colorText,
          display: 'flex',
          alignItems: 'center',
          gap: '4px',
          padding: '4px 8px',
          height: 'auto',
        }}
      >
        <Space size={4}>
          {getThemeIcon()}
          <span style={{ fontSize: '12px' }}>{getThemeLabel()}</span>
        </Space>
      </Button>
    </Dropdown>
  );
};

export default ThemeToggle;