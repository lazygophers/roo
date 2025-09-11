import React from 'react';
import { Typography, Space } from 'antd';
import { BookOutlined, GithubOutlined } from '@ant-design/icons';
import './LicenseInfo.css';

const { Text, Link } = Typography;

const LicenseInfo: React.FC = () => {
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
      </Space>
    </div>
  );
};

export default LicenseInfo;