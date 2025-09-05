import React from 'react';
import { createRoot } from 'react-dom/client';
import { ConfigProvider, App } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import 'dayjs/locale/zh-cn';

import { AppProvider } from '@/contexts/AppContext';
import { ThemeProvider } from '@/contexts/ThemeContext';
import AppRouter from '@/router';
import '@/styles/global.css';

const root = createRoot(document.getElementById('root')!);

root.render(
  <React.StrictMode>
    <ConfigProvider locale={zhCN}>
      <App>
        <ThemeProvider>
          <AppProvider>
            <AppRouter />
          </AppProvider>
        </ThemeProvider>
      </App>
    </ConfigProvider>
  </React.StrictMode>
);
