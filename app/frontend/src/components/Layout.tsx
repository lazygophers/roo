import React from 'react';
import { Layout, Menu, theme } from 'antd';
import { Outlet, Link } from 'react-router-dom';

const { Header, Content, Footer } = Layout;

const AppLayout: React.FC = () => {
  const {
    token: { colorBgContainer, borderRadiusLG },
  } = theme.useToken();

  const menuItems = [
    { key: '/', label: <Link to="/">首页</Link> },
    { key: '/settings', label: <Link to="/settings">配置管理</Link> },
  ];

  return (
    <Layout style={{ minHeight: '100vh' }}>
      <Header style={{ display: 'flex', alignItems: 'center', backgroundColor: '#fff', padding: '0 24px' }}>
        <div className="demo-logo" style={{ color: '#000', fontSize: '20px', fontWeight: 'bold' }}>
          管理平台
        </div>
        <Menu
          theme="light"
          mode="horizontal"
          defaultSelectedKeys={['/']}
          items={menuItems}
          style={{ flex: 1, minWidth: 0, marginLeft: '20px' }}
        />
      </Header>
      <Content style={{ margin: '24px 16px 0' }}>
        <div
          style={{
            padding: 24,
            minHeight: 'calc(100vh - 170px)',
            background: colorBgContainer,
            borderRadius: borderRadiusLG,
          }}
        >
          <Outlet />
        </div>
      </Content>
      <Footer style={{ textAlign: 'center' }}>Ant Design 管理平台 ©{new Date().getFullYear()} Created by React魔法师</Footer>
    </Layout>
  );
};

export default AppLayout;