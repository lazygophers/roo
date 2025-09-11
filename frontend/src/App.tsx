import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider, App as AntdApp } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import AppLayout from './components/Layout/AppLayout';
import ErrorBoundary from './components/ErrorBoundary';
import Home from './pages/Home';
import ConfigManagementWithSelection from './pages/ConfigManagementWithSelection';
import MCPToolsManagement from './pages/MCPToolsManagement';
import FileSecurityManagement from './pages/FileSecurityManagement';
import './App.css';
import './styles/theme.css';

const AppContent: React.FC = () => {
  const { currentTheme } = useTheme();

  return (
    <ConfigProvider 
      locale={zhCN}
      theme={currentTheme}
    >
      <AntdApp>
        <Router>
          <AppLayout>
            <Routes>
              <Route path="/" element={<Home />} />
              <Route path="/config" element={<ConfigManagementWithSelection />} />
              <Route path="/mcp-tools" element={<MCPToolsManagement />} />
              <Route path="/file-security" element={<FileSecurityManagement />} />
            </Routes>
          </AppLayout>
        </Router>
      </AntdApp>
    </ConfigProvider>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <ThemeProvider>
        <AppContent />
      </ThemeProvider>
    </ErrorBoundary>
  );
}

export default App;