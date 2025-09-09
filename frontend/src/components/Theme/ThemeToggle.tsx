import React from 'react';
import { Button, Dropdown, Space, theme, MenuProps } from 'antd';
import { 
  BgColorsOutlined,
  DownOutlined
} from '@ant-design/icons';
import { useTheme } from '../../contexts/ThemeContext';
import { ThemeName, themeRegistry } from '../../themes/themeConfig';

const ThemeToggle: React.FC = () => {
  const { themeType, setThemeType, currentTheme } = useTheme();
  const { token } = theme.useToken();

  // 创建主题预览小圆点
  const ThemePreview: React.FC<{ name: ThemeName }> = ({ name }) => {
    const themeConfig = themeRegistry[name];
    if (!themeConfig) return null;
    
    return (
      <div style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
        <div style={{
          width: 12,
          height: 12,
          borderRadius: 6,
          background: `linear-gradient(45deg, ${themeConfig.preview.primary}, ${themeConfig.preview.surface})`,
          border: '1px solid #d9d9d9'
        }} />
      </div>
    );
  };

  // 分组主题
  const themeGroups = {
    雾霭系列: ['morningMist', 'nightRain'],
    桃花系列: ['peachBlossom', 'plumRain'],
    溪水系列: ['streamFlow', 'deepSeaMoon'],
    竹林系列: ['bambooForest', 'greenMountain'],
  };

  const menuItems: MenuProps['items'] = Object.entries(themeGroups).map(([groupName, themes]) => ({
    key: groupName,
    label: groupName,
    type: 'group',
    children: themes.map((name) => {
      const themeConfig = themeRegistry[name as ThemeName];
      if (!themeConfig) return null;
      
      return {
        key: name,
        label: (
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', minWidth: 160 }}>
            <span>{themeConfig.description}</span>
            <ThemePreview name={name as ThemeName} />
          </div>
        ),
        onClick: () => setThemeType(name as ThemeName),
      };
    }).filter(Boolean),
  }));

  return (
    <Dropdown 
      menu={{ items: menuItems, selectedKeys: [themeType] }}
      trigger={['click']}
      placement="bottomRight"
    >
      <Button 
        type="text" 
        icon={<BgColorsOutlined />}
        style={{ 
          display: 'flex', 
          alignItems: 'center',
          color: token.colorText
        }}
      >
        <Space>
          {currentTheme?.description || '主题'}
          <DownOutlined style={{ fontSize: 10 }} />
        </Space>
      </Button>
    </Dropdown>
  );
};

export default ThemeToggle;