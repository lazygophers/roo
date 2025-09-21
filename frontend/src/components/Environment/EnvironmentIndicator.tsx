import React, { useState, useEffect } from 'react';
import { Tag, Tooltip, theme } from 'antd';
import { CloudOutlined, DesktopOutlined, LoadingOutlined } from '@ant-design/icons';
import { useEnvironment } from '../../contexts/EnvironmentContext';

const EnvironmentIndicator: React.FC = () => {
  const { environment, isLocal, isRemote, loading, error } = useEnvironment();
  const { token } = theme.useToken();
  const [isMobile, setIsMobile] = useState(false);

  // 检测屏幕大小变化
  useEffect(() => {
    const checkIsMobile = () => {
      setIsMobile(window.innerWidth <= 992); // 与Ant Design的lg断点一致
    };

    checkIsMobile();
    window.addEventListener('resize', checkIsMobile);
    return () => window.removeEventListener('resize', checkIsMobile);
  }, []);

  if (loading) {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: 16,
          left: isMobile ? 16 : 216,
          zIndex: 1000
        }}
      >
        <Tag
          icon={<LoadingOutlined />}
          color="processing"
          style={{
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            borderRadius: '16px',
            padding: '6px 12px',
            boxShadow: token.boxShadowSecondary,
            border: 'none',
            fontWeight: 500
          }}
        >
          检测中...
        </Tag>
      </div>
    );
  }

  if (error) {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: 16,
          left: isMobile ? 16 : 216,
          zIndex: 1000
        }}
      >
        <Tooltip title={`环境检测失败: ${error}`}>
          <Tag
            color="error"
            style={{
              fontSize: '12px',
              display: 'flex',
              alignItems: 'center',
              gap: '6px',
              borderRadius: '16px',
              padding: '6px 12px',
              boxShadow: token.boxShadowSecondary,
              border: 'none',
              fontWeight: 500
            }}
          >
            环境未知
          </Tag>
        </Tooltip>
      </div>
    );
  }

  const getEnvironmentConfig = () => {
    if (isLocal) {
      return {
        icon: <DesktopOutlined />,
        color: 'success' as const,
        text: '本地环境',
        description: '当前运行在本地开发环境，具有完整的编辑权限'
      };
    } else if (isRemote) {
      return {
        icon: <CloudOutlined />,
        color: 'processing' as const,
        text: '远程环境',
        description: '当前运行在远程生产环境，某些操作受限'
      };
    } else {
      return {
        icon: <DesktopOutlined />,
        color: 'default' as const,
        text: '未知环境',
        description: '无法确定当前运行环境'
      };
    }
  };

  const config = getEnvironmentConfig();

  return (
    <div
      style={{
        position: 'fixed',
        bottom: 16,
        left: isMobile ? 16 : 216, // 移动端16px，桌面端考虑侧边栏宽度
        zIndex: 1000
      }}
    >
      <Tooltip title={config.description} placement="topLeft">
        <Tag
          icon={config.icon}
          color={config.color}
          style={{
            fontSize: '12px',
            display: 'flex',
            alignItems: 'center',
            gap: '6px',
            borderRadius: '16px',
            padding: '6px 12px',
            boxShadow: token.boxShadowSecondary,
            cursor: 'help',
            border: 'none',
            fontWeight: 500
          }}
        >
          {config.text}
        </Tag>
      </Tooltip>
    </div>
  );
};

export default EnvironmentIndicator;