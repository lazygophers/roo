import React from 'react';
import { Tag, Tooltip, theme } from 'antd';
import { CloudOutlined, DesktopOutlined, LoadingOutlined } from '@ant-design/icons';
import { useEnvironment } from '../../contexts/EnvironmentContext';

const EnvironmentIndicator: React.FC = () => {
  const { environment, isLocal, isRemote, loading, error } = useEnvironment();
  const { token } = theme.useToken();

  if (loading) {
    return (
      <div
        style={{
          position: 'fixed',
          bottom: 16,
          left: 16,
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
            gap: '4px',
            borderRadius: '12px',
            padding: '4px 8px'
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
          left: 16,
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
              gap: '4px',
              borderRadius: '12px',
              padding: '4px 8px'
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
        left: 16,
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
            gap: '4px',
            borderRadius: '12px',
            padding: '4px 8px',
            boxShadow: token.boxShadowSecondary,
            cursor: 'help'
          }}
        >
          {config.text}
        </Tag>
      </Tooltip>
    </div>
  );
};

export default EnvironmentIndicator;