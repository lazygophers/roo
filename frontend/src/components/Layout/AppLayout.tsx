import React from 'react';
import { Layout, Button, Space, Menu, theme } from 'antd';
import { HomeOutlined, SettingOutlined, GithubOutlined, ApiOutlined } from '@ant-design/icons';
import { useNavigate, useLocation } from 'react-router-dom';
import ThemeToggle from '../Theme/ThemeToggle';
import LicenseInfo from '../License/LicenseInfo';
import './AppLayout.css';

const { Sider, Header, Content } = Layout;

interface AppLayoutProps {
  children: React.ReactNode;
}

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
              height: 64,
              margin: '16px 12px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              cursor: 'pointer',
              borderBottom: `1px solid ${colorBorderSecondary}`,
              flexShrink: 0,
              flexDirection: 'column',
              gap: '4px'
            }}
            onClick={() => navigate('/')}
          >
            <div style={{
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <img
                src="/icon-32.png"
                alt="LazyAI Studio"
                style={{
                  width: 24,
                  height: 24,
                  borderRadius: '4px'
                }}
              />
              <span style={{
                fontWeight: 'bold',
                fontSize: '14px',
                background: 'linear-gradient(135deg, #1890ff 0%, #52c41a 100%)',
                backgroundClip: 'text',
                WebkitBackgroundClip: 'text',
                WebkitTextFillColor: 'transparent',
                fontFamily: 'system-ui, -apple-system, sans-serif'
              }}>
                LazyAI
              </span>
            </div>
            <div style={{
              fontSize: '10px',
              color: colorText,
              opacity: 0.6,
              fontWeight: 400,
              letterSpacing: '0.5px'
            }}>
              Studio
            </div>
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

        {/* 开源协议信息固定在底部 */}
        <div style={{
          position: 'absolute',
          bottom: 0,
          left: 0,
          right: 0
        }}>
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