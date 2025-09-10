import React from 'react';
import { Typography, Space, Badge, Tag } from 'antd';
import { 
  StarOutlined, 
  FireOutlined, 
  ThunderboltOutlined,
  CrownOutlined
} from '@ant-design/icons';
import './TitleComponents.css';

const { Title } = Typography;

// 页面主标题组件
interface PageTitleProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  level?: 1 | 2 | 3 | 4 | 5;
  gradient?: boolean;
  animated?: boolean;
  className?: string;
}

export const PageTitle: React.FC<PageTitleProps> = ({ 
  title, 
  subtitle, 
  icon,
  level = 1,
  gradient = false,
  animated = false,
  className = ''
}) => {
  const titleClass = [
    'page-title',
    gradient ? 'gradient-title' : '',
    animated ? 'animated-title' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="page-title-container">
      <Title 
        level={level} 
        className={titleClass}
      >
        {icon && <span className="title-icon">{icon}</span>}
        {title}
      </Title>
      {subtitle && (
        <p className="page-subtitle">
          {subtitle}
        </p>
      )}
    </div>
  );
};

// 卡片标题组件
interface CardTitleProps {
  title: string;
  icon?: React.ReactNode;
  badge?: string | number;
  tag?: {
    text: string;
    color?: string;
  };
  status?: 'hot' | 'new' | 'premium' | 'featured';
  size?: 'small' | 'default' | 'large';
  className?: string;
}

export const CardTitle: React.FC<CardTitleProps> = ({
  title,
  icon,
  badge,
  tag,
  status,
  size = 'default',
  className = ''
}) => {
  const getStatusIcon = () => {
    switch (status) {
      case 'hot': return <FireOutlined style={{ color: '#ff4d4f' }} />;
      case 'new': return <ThunderboltOutlined style={{ color: '#52c41a' }} />;
      case 'premium': return <CrownOutlined style={{ color: '#faad14' }} />;
      case 'featured': return <StarOutlined style={{ color: '#1890ff' }} />;
      default: return null;
    }
  };

  const getStatusTag = () => {
    if (!status) return null;
    
    const statusConfig = {
      hot: { text: 'HOT', color: '#ff4d4f' },
      new: { text: 'NEW', color: '#52c41a' },
      premium: { text: 'PRO', color: '#faad14' },
      featured: { text: 'FEATURED', color: '#1890ff' }
    };

    return (
      <Tag 
        color={statusConfig[status]?.color} 
        className={`status-tag status-${status}`}
      >
        {statusConfig[status]?.text}
      </Tag>
    );
  };

  const containerClass = [
    'card-title-container',
    `size-${size}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClass}>
      <Space className="title-content" align="center">
        {icon && <span className="card-title-icon">{icon}</span>}
        <span className="card-title-text">{title}</span>
        {badge && <Badge count={badge} className="title-badge" />}
        {getStatusIcon()}
      </Space>
      
      <Space className="title-extras">
        {getStatusTag()}
        {tag && (
          <Tag color={tag.color || 'default'} className="custom-tag">
            {tag.text}
          </Tag>
        )}
      </Space>
    </div>
  );
};

// 节区标题组件
interface SectionTitleProps {
  title: string;
  subtitle?: string;
  icon?: React.ReactNode;
  level?: 2 | 3 | 4 | 5;
  divider?: boolean;
  extra?: React.ReactNode;
  className?: string;
}

export const SectionTitle: React.FC<SectionTitleProps> = ({
  title,
  subtitle,
  icon,
  level = 3,
  divider = true,
  extra,
  className = ''
}) => {
  const containerClass = [
    'section-title-container',
    divider ? 'with-divider' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClass}>
      <div className="section-title-main">
        <Title level={level} className="section-title">
          {icon && <span className="section-title-icon">{icon}</span>}
          {title}
        </Title>
        {subtitle && (
          <p className="section-subtitle">{subtitle}</p>
        )}
      </div>
      {extra && (
        <div className="section-title-extra">
          {extra}
        </div>
      )}
    </div>
  );
};

// 列表项标题组件
interface ListItemTitleProps {
  title: string;
  subtitle?: string;
  meta?: string[];
  status?: 'active' | 'inactive' | 'pending' | 'error';
  size?: 'small' | 'default' | 'large';
  className?: string;
}

export const ListItemTitle: React.FC<ListItemTitleProps> = ({
  title,
  subtitle,
  meta = [],
  status,
  size = 'default',
  className = ''
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'active': return '#52c41a';
      case 'inactive': return '#d9d9d9';
      case 'pending': return '#faad14';
      case 'error': return '#ff4d4f';
      default: return '#1890ff';
    }
  };

  const containerClass = [
    'list-item-title-container',
    `size-${size}`,
    status ? `status-${status}` : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClass}>
      <div className="list-title-main">
        <h4 className="list-item-title">
          {status && (
            <span 
              className="status-indicator" 
              style={{ backgroundColor: getStatusColor() }}
            />
          )}
          {title}
        </h4>
        {subtitle && (
          <p className="list-item-subtitle">{subtitle}</p>
        )}
      </div>
      {meta.length > 0 && (
        <div className="list-item-meta">
          {meta.map((item, index) => (
            <span key={index} className="meta-item">{item}</span>
          ))}
        </div>
      )}
    </div>
  );
};

// 统计标题组件
interface StatTitleProps {
  title: string;
  value: string | number;
  icon?: React.ReactNode;
  color?: string;
  trend?: 'up' | 'down' | 'stable';
  size?: 'small' | 'default' | 'large';
  animated?: boolean;
  className?: string;
}

export const StatTitle: React.FC<StatTitleProps> = ({
  title,
  value,
  icon,
  color = '#1890ff',
  trend,
  size = 'default',
  animated = false,
  className = ''
}) => {
  const getTrendIcon = () => {
    switch (trend) {
      case 'up': return '↗';
      case 'down': return '↘';
      case 'stable': return '→';
      default: return null;
    }
  };

  const containerClass = [
    'stat-title-container',
    `size-${size}`,
    animated ? 'animated-stat' : '',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={containerClass}>
      <div className="stat-icon" style={{ color }}>
        {icon}
      </div>
      <div className="stat-content">
        <div className="stat-value" style={{ color }}>
          {value}
          {trend && (
            <span className={`trend-indicator trend-${trend}`}>
              {getTrendIcon()}
            </span>
          )}
        </div>
        <div className="stat-title">{title}</div>
      </div>
    </div>
  );
};