import React from 'react';
import { Layout, Menu, Avatar, Dropdown, Switch, Space, Typography, Button } from 'antd';
import {
  MenuOutlined,
  UserOutlined,
  SettingOutlined,
  LogoutOutlined,
  BulbOutlined,
  BulbFilled,
  HomeOutlined,
  AppstoreOutlined,
} from '@ant-design/icons';
import type { MenuProps } from 'antd';
import { useTheme } from '@/contexts/ThemeContext';
import styles from './AppLayout.module.css';

const { Header, Sider, Content } = Layout;
const { Text } = Typography;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const { isDark, toggleTheme } = useTheme();
  const [collapsed, setCollapsed] = React.useState(false);

  // 用户菜单配置
  const userMenuItems: MenuProps['items'] = [
    {
      key: 'profile',
      icon: <UserOutlined />,
      label: '个人资料',
    },
    {
      key: 'settings',
      icon: <SettingOutlined />,
      label: '账户设置',
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: '退出登录',
      danger: true,
    },
  ];

  // 侧边栏菜单配置
  const sideMenuItems: MenuProps['items'] = [
    {
      key: 'home',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: 'configurations',
      icon: <AppstoreOutlined />,
      label: '配置管理',
    },
  ];

  const handleUserMenuClick: MenuProps['onClick'] = e => {
    switch (e.key) {
      case 'profile':
        console.log('跳转到个人资料页面');
        break;
      case 'settings':
        console.log('跳转到账户设置页面');
        break;
      case 'logout':
        console.log('执行退出登录');
        break;
    }
  };

  const handleSideMenuClick: MenuProps['onClick'] = e => {
    console.log('导航到:', e.key);
    // 这里后续会集成 React Router 进行页面导航
  };

  return (
    <Layout className={styles.layout}>
      {/* 侧边栏 */}
      <Sider
        trigger={null}
        collapsible
        collapsed={collapsed}
        className={styles.sider}
        theme={isDark ? 'dark' : 'light'}
      >
        {/* Logo区域 */}
        <div className={styles.logo}>
          <Space>
            <AppstoreOutlined className={styles.logoIcon} />
            {!collapsed && (
              <Text strong className={styles.logoText}>
                Roo Config
              </Text>
            )}
          </Space>
        </div>

        {/* 侧边栏菜单 */}
        <Menu
          theme={isDark ? 'dark' : 'light'}
          mode='inline'
          defaultSelectedKeys={['home']}
          items={sideMenuItems}
          onClick={handleSideMenuClick}
          className={styles.sideMenu}
        />
      </Sider>

      <Layout>
        {/* 顶部导航栏 */}
        <Header className={styles.header}>
          <div className={styles.headerLeft}>
            {/* 折叠按钮 */}
            <Button
              type='text'
              icon={<MenuOutlined />}
              onClick={() => setCollapsed(!collapsed)}
              className={styles.trigger}
            />
          </div>

          <div className={styles.headerRight}>
            <Space size='middle'>
              {/* 主题切换 */}
              <div className={styles.themeSwitch}>
                <Space align='center'>
                  <BulbOutlined className={!isDark ? styles.activeThemeIcon : ''} />
                  <Switch
                    checked={isDark}
                    onChange={toggleTheme}
                    size='small'
                    className={styles.themeSwitchControl}
                  />
                  <BulbFilled className={isDark ? styles.activeThemeIcon : ''} />
                </Space>
              </div>

              {/* 用户头像和下拉菜单 */}
              <Dropdown
                menu={{
                  items: userMenuItems,
                  onClick: handleUserMenuClick,
                }}
                placement='bottomRight'
                arrow={{ pointAtCenter: true }}
              >
                <Space className={styles.userInfo} style={{ cursor: 'pointer' }}>
                  <Avatar size='small' icon={<UserOutlined />} className={styles.avatar} />
                  <Text className={styles.username}>管理员</Text>
                </Space>
              </Dropdown>
            </Space>
          </div>
        </Header>

        {/* 主内容区域 */}
        <Content className={styles.content}>
          <div className={styles.contentInner}>{children}</div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;
