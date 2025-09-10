import React from 'react';
import { Layout, Menu, theme } from 'antd';
import { HomeOutlined, SettingOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import ThemeToggle from '../Theme/ThemeToggle';
import './AppLayout.css';

const { Header, Content, Sider } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const {
    token: { colorBgContainer },
  } = theme.useToken();
  
  const navigate = useNavigate();
  const location = useLocation();

  const menuItems = [
    {
      key: '/',
      icon: <HomeOutlined />,
      label: '首页',
    },
    {
      key: '/config',
      icon: <SettingOutlined />,
      label: '配置管理',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        style={{
          background: colorBgContainer,
        }}
      >
        <div 
          className="nav-logo"
          style={{ 
            height: 48, 
            margin: 16, 
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontWeight: 'bold',
            fontSize: '16px',
            cursor: 'pointer',
            borderBottom: '1px solid #f0f0f0'
          }}
          onClick={() => navigate('/')}
        >
          Roo AI
        </div>
        <Menu
          mode="inline"
          selectedKeys={[location.pathname]}
          items={menuItems}
          onClick={(item) => navigate(item.key)}
          style={{ 
            borderRight: 0,
            background: 'transparent'
          }}
        />
      </Sider>
      <Layout>
        <Header style={{ 
          padding: 0, 
          background: colorBgContainer,
          borderBottom: '1px solid #f0f0f0'
        }}>
          <div style={{ 
            padding: '0 24px', 
            display: 'flex',
            justifyContent: 'space-between',
            alignItems: 'center',
            height: '100%'
          }}>
            <h2 style={{ margin: 0, fontSize: '18px', fontWeight: 'normal' }}>
              配置中心
            </h2>
            <ThemeToggle />
          </div>
        </Header>
        <Content style={{ margin: '24px 16px 0' }}>
          <div
            style={{
              padding: 24,
              minHeight: 360,
              background: colorBgContainer,
              borderRadius: 4,
            }}
          >
            {children}
          </div>
        </Content>
      </Layout>
    </Layout>
  );
};

export default AppLayout;