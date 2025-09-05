import React from 'react';
import { Typography, Card, Row, Col, Timeline, Tag, Space, Divider, Badge } from 'antd';
import {
  InfoCircleOutlined,
  HeartFilled,
  GithubOutlined,
  BugOutlined,
  BulbOutlined,
  RocketOutlined,
  TeamOutlined,
  StarFilled,
} from '@ant-design/icons';
import styles from './AboutPage.module.css';

const { Title, Paragraph, Text, Link } = Typography;

interface FeatureCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
  status?: 'completed' | 'in-progress' | 'planned';
}

const FeatureCard: React.FC<FeatureCardProps> = ({
  icon,
  title,
  description,
  status = 'completed',
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'completed':
        return 'success';
      case 'in-progress':
        return 'processing';
      case 'planned':
        return 'default';
      default:
        return 'success';
    }
  };

  const getStatusText = () => {
    switch (status) {
      case 'completed':
        return '已完成';
      case 'in-progress':
        return '开发中';
      case 'planned':
        return '规划中';
      default:
        return '已完成';
    }
  };

  return (
    <Card className={styles.featureCard} hoverable>
      <div className={styles.featureIcon}>{icon}</div>
      <Title level={4} className={styles.featureTitle}>
        {title}
        <Badge
          status={getStatusColor()}
          text={getStatusText()}
          style={{ marginLeft: 8, fontSize: '12px' }}
        />
      </Title>
      <Paragraph className={styles.featureDescription}>{description}</Paragraph>
    </Card>
  );
};

const AboutPage: React.FC = () => {
  const features = [
    {
      icon: <RocketOutlined />,
      title: '快速配置',
      description: '直观的界面让您能够快速浏览、选择和组合各种 Roo Code 规则配置，提升开发效率。',
      status: 'completed' as const,
    },
    {
      icon: <BulbOutlined />,
      title: '智能建议',
      description: '基于项目类型和技术栈，自动推荐最适合的规则配置组合，避免配置冲突。',
      status: 'in-progress' as const,
    },
    {
      icon: <TeamOutlined />,
      title: '团队协作',
      description: '支持配置共享和版本管理，让团队成员能够使用统一的开发规范和工具配置。',
      status: 'planned' as const,
    },
    {
      icon: <BugOutlined />,
      title: '配置验证',
      description: '实时验证配置有效性，确保导出的配置文件符合预期，减少配置错误。',
      status: 'completed' as const,
    },
  ];

  const versionHistory = [
    {
      version: '1.0.0',
      date: '2025-01-20',
      description: '首个正式版本发布',
      features: ['基础规则浏览', '配置导出', '模式管理', '主题切换'],
    },
    {
      version: '0.9.0',
      date: '2025-01-15',
      description: 'Beta 版本',
      features: ['核心功能实现', 'UI 界面优化', '基础测试覆盖'],
    },
    {
      version: '0.8.0',
      date: '2025-01-10',
      description: 'Alpha 版本',
      features: ['项目架构搭建', 'React + TypeScript 基础框架', 'Ant Design 集成'],
    },
  ];

  const techStack = [
    { name: 'React 18', category: '前端框架', color: '#61dafb' },
    { name: 'TypeScript', category: '开发语言', color: '#3178c6' },
    { name: 'Ant Design 5', category: 'UI 组件库', color: '#1890ff' },
    { name: 'Vite', category: '构建工具', color: '#646cff' },
    { name: 'FastAPI', category: '后端框架', color: '#009688' },
    { name: 'Python', category: '后端语言', color: '#3776ab' },
    { name: 'TinyDB', category: '数据存储', color: '#ff6b35' },
    { name: 'CSS Modules', category: '样式方案', color: '#1572b6' },
  ];

  return (
    <div className={styles.container}>
      {/* 页面头部 */}
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <Title level={1} className={styles.title}>
            <InfoCircleOutlined className={styles.titleIcon} />
            关于 Roo Config Manager
          </Title>
          <Paragraph className={styles.subtitle}>
            专为 Roo Code 设计的智能配置管理工具，让开发者能够轻松管理和定制各种规则配置，
            提升开发效率，保证代码质量。
          </Paragraph>
        </div>
      </div>

      {/* 项目愿景 */}
      <Card className={styles.visionCard}>
        <Title level={3}>
          <HeartFilled style={{ color: '#ff4d4f' }} /> 项目愿景
        </Title>
        <Paragraph className={styles.visionText}>
          我们致力于构建一个开放、灵活、易用的配置管理生态系统，
          让每个开发者都能找到最适合自己项目的规则配置，
          同时支持自定义和扩展，真正实现"一次配置，处处使用"的理想。
        </Paragraph>
      </Card>

      {/* 核心特性 */}
      <div className={styles.featuresSection}>
        <Title level={2}>核心特性</Title>
        <Row gutter={[24, 24]}>
          {features.map((feature, index) => (
            <Col xs={24} sm={12} lg={6} key={index}>
              <FeatureCard {...feature} />
            </Col>
          ))}
        </Row>
      </div>

      <Divider />

      {/* 技术栈 */}
      <div className={styles.techSection}>
        <Title level={2}>技术栈</Title>
        <Paragraph>本项目采用现代化的技术栈，确保高性能、可维护性和良好的开发体验：</Paragraph>

        <div className={styles.techGrid}>
          {techStack.map((tech, index) => (
            <Card key={index} className={styles.techCard} size='small' hoverable>
              <div className={styles.techInfo}>
                <div className={styles.techIndicator} style={{ backgroundColor: tech.color }} />
                <div className={styles.techDetails}>
                  <Text strong>{tech.name}</Text>
                  <br />
                  <Text type='secondary' className={styles.techCategory}>
                    {tech.category}
                  </Text>
                </div>
              </div>
            </Card>
          ))}
        </div>
      </div>

      <Divider />

      {/* 版本历史 */}
      <div className={styles.versionSection}>
        <Title level={2}>版本历史</Title>
        <Timeline>
          {versionHistory.map((version, index) => (
            <Timeline.Item key={index} dot={<StarFilled style={{ color: '#1890ff' }} />}>
              <div className={styles.versionItem}>
                <Title level={4} className={styles.versionTitle}>
                  v{version.version}
                  <Tag color='blue' style={{ marginLeft: 8 }}>
                    {version.date}
                  </Tag>
                </Title>
                <Paragraph className={styles.versionDescription}>{version.description}</Paragraph>
                <Space wrap>
                  {version.features.map((feature, featureIndex) => (
                    <Tag key={featureIndex} color='geekblue'>
                      {feature}
                    </Tag>
                  ))}
                </Space>
              </div>
            </Timeline.Item>
          ))}
        </Timeline>
      </div>

      <Divider />

      {/* 联系信息 */}
      <Card className={styles.contactCard}>
        <Title level={3}>联系我们</Title>
        <Row gutter={[24, 16]}>
          <Col xs={24} sm={12}>
            <Space direction='vertical' size='middle'>
              <div>
                <Text strong>项目地址</Text>
                <br />
                <Link
                  href='https://github.com/roo-code/config-manager'
                  target='_blank'
                  className={styles.contactLink}
                >
                  <GithubOutlined /> GitHub Repository
                </Link>
              </div>

              <div>
                <Text strong>问题反馈</Text>
                <br />
                <Link
                  href='https://github.com/roo-code/config-manager/issues'
                  target='_blank'
                  className={styles.contactLink}
                >
                  <BugOutlined /> Issue Tracker
                </Link>
              </div>
            </Space>
          </Col>

          <Col xs={24} sm={12}>
            <Space direction='vertical' size='middle'>
              <div>
                <Text strong>作者信息</Text>
                <br />
                <Text type='secondary'>落心 (Luoxin)</Text>
              </div>

              <div>
                <Text strong>系统环境</Text>
                <br />
                <Text type='secondary'>
                  macOS Sequoia (darwin-arm64)
                  <br />
                  时区: UTF+8 (中国)
                </Text>
              </div>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 页脚信息 */}
      <div className={styles.footer}>
        <Text type='secondary'>
          Made with <HeartFilled style={{ color: '#ff4d4f', margin: '0 4px' }} />
          for the Roo Code Community
        </Text>
      </div>
    </div>
  );
};

export default AboutPage;
