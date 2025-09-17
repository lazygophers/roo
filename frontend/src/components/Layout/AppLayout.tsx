import React from 'react';
import { Layout, Button, Space, Menu, theme } from 'antd';

const { Sider, Header, Content } = Layout;
import { HomeOutlined, SettingOutlined, GithubOutlined, ApiOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import ThemeToggle from '../Theme/ThemeToggle';
import SystemMonitorMenuItem from '../SystemMonitor/SystemMonitorMenuItem';
import LicenseInfo from '../License/LicenseInfo';
import './AppLayout.css';


interface AppLayoutProps {
  children: React.ReactNode;
}

const { Header, Content, Sider } = Layout;

const AppLayout: React.FC<AppLayoutProps> = ({ children }) => {
  const {
    token: { colorBgContainer, colorBorderSecondary, colorText },
  } = theme.useToken();

  const navigate = useNavigate();
  const location = useLocation();
  const [collapsed, setCollapsed] = React.useState(false);

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
    {
      key: '/mcp-tools',
      icon: <ApiOutlined />,
      label: 'MCP 工具',
    },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Sider
        breakpoint="lg"
        collapsedWidth="0"
        onCollapse={(collapsed) => setCollapsed(collapsed)}
        style={{
          background: colorBgContainer,
          position: 'fixed',
          left: 0,
          top: 0,
          height: '100vh',
          zIndex: 1000
        }}
      >
        <div style={{
          display: 'flex',
          flexDirection: 'column',
          height: '100%'
        }}>
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
              borderBottom: `1px solid ${colorBorderSecondary}`,
              flexShrink: 0
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
              background: 'transparent',
              flexShrink: 0
            }}
          />

          {/* 填充空间 */}
          <div style={{ flex: 1 }} />
        </div>

        {/* 系统监控和开源协议信息固定在底部 */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0
        }}>
          {/* 系统监控组件 */}
          <SystemMonitorMenuItem />
          {/* 开源协议信息 */}
          <LicenseInfo />
        </div>
      </Sider>
      <Layout style={{ marginLeft: collapsed ? 0 : 200 }}>
        <Header style={{
          padding: 0,
          background: colorBgContainer,
          borderBottom: `1px solid ${colorBorderSecondary}`,
          position: 'fixed',
          top: 0,
          right: 0,
          left: collapsed ? 0 : 200,
          zIndex: 999
        }}>
          <div style={{
            padding: '0 24px',
            display: 'flex',
            justifyContent: 'flex-end',
            alignItems: 'center',
            height: '100%'
          }}>
            <Space size="middle">
              <Button
                type="text"
                icon={<GithubOutlined />}
                onClick={() => window.open('https://github.com/lazygophers/roo', '_blank')}
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  color: colorText
                }}
              >
                GitHub
              </Button>
              <ThemeToggle />
            </Space>
          </div>
        </Header>
        <Content style={{ margin: '88px 16px 24px 16px' }}>
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