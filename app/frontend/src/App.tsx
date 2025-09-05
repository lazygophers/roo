import React from 'react';
import { BrowserRouter } from 'react-router-dom';
import { ConfigProvider, theme, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';

import { useTheme } from '@/contexts/ThemeContext';
import AppLayout from '@/components/Layout/AppLayout';
import AppRouter from '@/router';

const App: React.FC = () => {
  const { isDark } = useTheme();

  return (
    <ConfigProvider
      locale={zhCN}
      theme={{
        algorithm: isDark ? theme.darkAlgorithm : theme.defaultAlgorithm,
        token: {
          colorPrimary: '#1890ff',
          borderRadius: 6,
          fontSize: 14,
        },
      }}
    >
      <AntdApp>
        <BrowserRouter>
          <AppLayout>
            <AppRouter />
          </AppLayout>
        </BrowserRouter>
      </AntdApp>
    </ConfigProvider>
  );
};

export default App;
