import { StrictMode } from 'react'
import { createRoot } from 'react-dom/client'
import { ConfigProvider, theme } from 'antd';
import './index.css'
import 'antd/dist/reset.css';
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <ConfigProvider theme={{
      algorithm: theme.darkAlgorithm,
    }}>
      <App />
    </ConfigProvider>
  </StrictMode>,
)
