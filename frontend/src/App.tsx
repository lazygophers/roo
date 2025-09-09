import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { ConfigProvider } from 'antd';
import zhCN from 'antd/locale/zh_CN';
import { ThemeProvider, useTheme } from './contexts/ThemeContext';
import AppLayout from './components/Layout/AppLayout';
import Home from './pages/Home';
import ConfigManagementWithSelection from './pages/ConfigManagementWithSelection';
import './App.css';

const AppContent: React.FC = () => {
  const { currentTheme } = useTheme();

  return (
    <ConfigProvider 
      locale={zhCN}
      theme={currentTheme}
    >
      <Router>
        <AppLayout>
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/config" element={<ConfigManagementWithSelection />} />
          </Routes>
        </AppLayout>
      </Router>
    </ConfigProvider>
  );
};

function App() {
  return (
    <ThemeProvider>
      <AppContent />
    </ThemeProvider>
  );
}

export default App;