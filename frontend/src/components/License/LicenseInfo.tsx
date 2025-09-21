import React from 'react';
import { Typography, Space } from 'antd';
import { BookOutlined, GithubOutlined, DesktopOutlined, CloudOutlined } from '@ant-design/icons';
import { useEnvironment } from '../../contexts/EnvironmentContext';
import './LicenseInfo.css';

const { Text, Link } = Typography;

const LicenseInfo: React.FC = () => {
  const { isLocal, isRemote, loading } = useEnvironment();

  const getEnvironmentDisplay = () => {
    if (loading) return { icon: <DesktopOutlined />, text: '检测中...' };
    if (isLocal) return { icon: <DesktopOutlined />, text: '本地环境' };
    if (isRemote) return { icon: <CloudOutlined />, text: '远程环境' };
    return { icon: <DesktopOutlined />, text: '未知环境' };
  };

  const envDisplay = getEnvironmentDisplay();

  return (
    <div className="license-info">
      <Space direction="vertical" size={4}>
        <div className="license-item">
          <BookOutlined className="license-icon" />
          <Text className="license-text">
            <Link
              href="https://github.com/lazygophers/roo/blob/master/LICENSE"
              target="_blank"
              className="license-link"
            >
              AGPL-3.0
            </Link>
          </Text>
        </div>
        <div className="license-item">
          <GithubOutlined className="license-icon" />
          <Text className="license-text">
            <Link
              href="https://github.com/lazygophers"
              target="_blank"
              className="license-link"
            >
              LazyGophers
            </Link>
          </Text>
        </div>
        <div className="license-item">
          {envDisplay.icon && React.cloneElement(envDisplay.icon, { className: "license-icon" })}
          <Text className="license-text">
            {envDisplay.text}
          </Text>
        </div>
      </Space>
    </div>
  );
};

export default LicenseInfo;