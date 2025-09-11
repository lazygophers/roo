import React, { useState, useEffect, useRef } from 'react';
import { Card, Row, Col, Typography, List, Tag, Space, message, Progress, Badge } from 'antd';
import { 
  CodeOutlined, 
  RocketOutlined,
  BulbOutlined,
  ThunderboltOutlined,
  StarOutlined,
  ApiOutlined,
  DatabaseOutlined,
  CloudOutlined,
  SafetyCertificateOutlined
} from '@ant-design/icons';
import { apiClient, ModelInfo } from '../api';
import { PageTitle, CardTitle, StatTitle } from '../components/UI/TitleComponents';
import { useTheme } from '../contexts/ThemeContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import './Home.css';

const { Paragraph, Text } = Typography;

// 粒子系统组件
const ParticleBackground: React.FC = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const particles: Array<{
      x: number;
      y: number;
      vx: number;
      vy: number;
      size: number;
      opacity: number;
      color: string;
    }> = [];

    const colors = ['#1890ff', '#52c41a', '#722ed1', '#fa8c16', '#13c2c2'];

    // 初始化粒子
    const initParticles = () => {
      particles.length = 0;
      for (let i = 0; i < 50; i++) {
        particles.push({
          x: Math.random() * canvas.width,
          y: Math.random() * canvas.height,
          vx: (Math.random() - 0.5) * 0.5,
          vy: (Math.random() - 0.5) * 0.5,
          size: Math.random() * 3 + 1,
          opacity: Math.random() * 0.5 + 0.2,
          color: colors[Math.floor(Math.random() * colors.length)]
        });
      }
    };

    // 调整canvas大小
    const resizeCanvas = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initParticles();
    };

    // 绘制粒子
    const drawParticles = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      
      particles.forEach((particle, index) => {
        // 更新位置
        particle.x += particle.vx;
        particle.y += particle.vy;

        // 边界检测
        if (particle.x < 0 || particle.x > canvas.width) particle.vx *= -1;
        if (particle.y < 0 || particle.y > canvas.height) particle.vy *= -1;

        // 绘制粒子
        ctx.beginPath();
        ctx.arc(particle.x, particle.y, particle.size, 0, Math.PI * 2);
        ctx.fillStyle = particle.color + Math.floor(particle.opacity * 255).toString(16).padStart(2, '0');
        ctx.fill();

        // 连接附近的粒子
        for (let j = index + 1; j < particles.length; j++) {
          const other = particles[j];
          const distance = Math.sqrt(
            Math.pow(particle.x - other.x, 2) + Math.pow(particle.y - other.y, 2)
          );

          if (distance < 100) {
            ctx.beginPath();
            ctx.moveTo(particle.x, particle.y);
            ctx.lineTo(other.x, other.y);
            ctx.strokeStyle = particle.color + '20';
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      });
    };

    // 动画循环
    const animate = () => {
      drawParticles();
      requestAnimationFrame(animate);
    };

    resizeCanvas();
    animate();

    window.addEventListener('resize', resizeCanvas);
    return () => window.removeEventListener('resize', resizeCanvas);
  }, []);

  return (
    <canvas
      ref={canvasRef}
      className="particle-canvas"
      style={{
        position: 'fixed',
        top: 0,
        left: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0
      }}
    />
  );
};


// 主页组件
const Home: React.FC = () => {
  // 设置页面标题
  useDocumentTitle('首页');
  
  const { themeType } = useTheme();
  const [stats, setStats] = useState({
    totalModels: 0,
    coderModels: 0,
    coreModels: 0,
    commands: 0,
    rules: 0
  });
  const [recentModels, setRecentModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [headerVisible, setHeaderVisible] = useState(false);

  useEffect(() => {
    const loadData = async () => {
      try {
        setLoading(true);
        
        // 加载统计数据
        const [modelsData, coderData, coreData, commandsData, rulesData] = await Promise.all([
          apiClient.getModels(),
          apiClient.getModels({ category: 'coder' }),
          apiClient.getModels({ category: 'core' }),
          apiClient.getCommands(),
          apiClient.getRules()
        ]);

        setStats({
          totalModels: modelsData.total,
          coderModels: coderData.total,
          coreModels: coreData.total,
          commands: commandsData.total,
          rules: rulesData.total
        });

        // 显示最近的模型（取前6个）
        setRecentModels(modelsData.data.slice(0, 6));
        
      } catch (error) {
        console.error('Failed to load data:', error);
        message.error('加载数据失败');
      } finally {
        setLoading(false);
      }
    };

    loadData();
    
    // 延迟显示头部
    setTimeout(() => setHeaderVisible(true), 300);
  }, []);

  const getGroupColor = (groups: any[]) => {
    if (groups.includes('core')) return '#1890ff';
    if (groups.includes('coder')) return '#52c41a';
    return '#722ed1';
  };

  const getGroupIcon = (groups: any[]) => {
    if (groups.includes('core')) return <DatabaseOutlined />;
    if (groups.includes('coder')) return <CodeOutlined />;
    return <BulbOutlined />;
  };

  return (
    <div className={`home-container ${themeType ? `theme-${themeType}` : ''}`}>
      <ParticleBackground />
      
      <div className="home-content">
        {/* 头部区域 */}
        <div className={`home-header ${headerVisible ? 'visible' : ''}`}>
          <div className="header-content">
            <div className="header-icon">
              <RocketOutlined />
            </div>
            <div className="header-text">
              <PageTitle
                title="Roo AI Configuration Center"
                subtitle="智能模型配置管理平台 - 统一管理您的AI模型、指令和规则配置"
                level={1}
                gradient={true}
                animated={true}
              />
            </div>
            <div className="header-badges">
              <Badge count="AI" style={{ backgroundColor: '#52c41a' }} />
              <Badge count="Config" style={{ backgroundColor: '#1890ff' }} />
              <Badge count="Smart" style={{ backgroundColor: '#722ed1' }} />
            </div>
          </div>
        </div>

        {/* 统计卡片区域 */}
        <div className="stats-section">
          <Row gutter={[24, 24]}>
            <Col xs={24} sm={12} md={6}>
              <StatTitle
                title="AI 模型总数"
                value={stats.totalModels}
                icon={<ApiOutlined />}
                color="#1890ff"
                animated={!loading}
                trend="up"
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <StatTitle
                title="编程助手"
                value={stats.coderModels}
                icon={<CodeOutlined />}
                color="#52c41a"
                animated={!loading}
                trend="stable"
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <StatTitle
                title="核心模型"
                value={stats.coreModels}
                icon={<DatabaseOutlined />}
                color="#722ed1"
                animated={!loading}
                trend="up"
              />
            </Col>
            <Col xs={24} sm={12} md={6}>
              <StatTitle
                title="智能指令"
                value={stats.commands}
                icon={<ThunderboltOutlined />}
                color="#fa8c16"
                animated={!loading}
                trend="stable"
              />
            </Col>
          </Row>
        </div>

        {/* 主要内容区域 */}
        <Row gutter={[24, 24]} className="main-content">
          {/* 模型展示区 */}
          <Col xs={24} lg={16}>
            <Card 
              className="models-card"
              title={
                <CardTitle
                  title="精选AI模型"
                  icon={<StarOutlined />}
                  status="featured"
                  tag={{ text: "最新配置", color: "blue" }}
                />
              }
              loading={loading}
            >
              <List
                className="models-list"
                dataSource={recentModels}
                renderItem={(model, index) => (
                  <List.Item 
                    className={`model-item delay-${index}`}
                    style={{ animationDelay: `${600 + index * 100}ms` }}
                  >
                    <div className="model-content">
                      <div className="model-icon" style={{ color: getGroupColor(model.groups) }}>
                        {getGroupIcon(model.groups)}
                      </div>
                      <div className="model-info">
                        <div className="model-header">
                          <Text strong className="model-name">{model.name}</Text>
                          <div className="model-tags">
                            <Tag 
                              color={getGroupColor(model.groups)} 
                              className="model-tag"
                            >
                              {model.groups.includes('core') ? 'Core' : 
                               model.groups.includes('coder') ? 'Coder' : 'General'}
                            </Tag>
                            <Tag className="model-slug">{model.slug}</Tag>
                          </div>
                        </div>
                        <Paragraph 
                          className="model-description"
                          ellipsis={{ rows: 2, expandable: false }}
                        >
                          {model.description}
                        </Paragraph>
                      </div>
                      <div className="model-status">
                        <div className="status-dot"></div>
                        <Text type="secondary">Active</Text>
                      </div>
                    </div>
                  </List.Item>
                )}
              />
            </Card>
          </Col>

          {/* 系统监控区 */}
          <Col xs={24} lg={8}>
            <Space direction="vertical" style={{ width: '100%' }} size="large">
              {/* 系统状态卡片 */}
              <Card 
                className="system-card"
                title={
                  <CardTitle
                    title="系统状态"
                    icon={<SafetyCertificateOutlined />}
                    status="hot"
                  />
                }
                loading={loading}
              >
                <div className="system-status">
                  <div className="status-item">
                    <div className="status-indicator online"></div>
                    <Text>配置服务</Text>
                    <Tag color="success">正常</Tag>
                  </div>
                  <div className="status-item">
                    <div className="status-indicator online"></div>
                    <Text>模型引擎</Text>
                    <Tag color="success">运行中</Tag>
                  </div>
                  <div className="status-item">
                    <div className="status-indicator online"></div>
                    <Text>数据同步</Text>
                    <Tag color="processing">同步中</Tag>
                  </div>
                </div>
              </Card>

              {/* 快速统计 */}
              <Card 
                className="quick-stats-card"
                title={
                  <CardTitle
                    title="资源概览"
                    icon={<CloudOutlined />}
                    status="new"
                  />
                }
                loading={loading}
              >
                <div className="quick-stats">
                  <div className="stat-row">
                    <span>配置规则</span>
                    <span className="stat-number">{stats.rules}</span>
                  </div>
                  <div className="stat-row">
                    <span>活跃连接</span>
                    <span className="stat-number">127</span>
                  </div>
                  <div className="stat-row">
                    <span>处理请求</span>
                    <span className="stat-number">2.3K</span>
                  </div>
                  <div className="stat-row">
                    <span>响应时间</span>
                    <span className="stat-number">45ms</span>
                  </div>
                </div>
                
                <div className="performance-chart">
                  <Text type="secondary">系统负载</Text>
                  <Progress 
                    percent={75} 
                    strokeColor={{
                      '0%': '#108ee9',
                      '100%': '#87d068',
                    }}
                    size="small"
                  />
                </div>
              </Card>
            </Space>
          </Col>
        </Row>
      </div>
    </div>
  );
};

export default Home;