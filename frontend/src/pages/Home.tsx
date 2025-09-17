import React, { useState, useEffect, useRef } from 'react';
import { message, Badge } from 'antd';
import { StatisticCard } from '@ant-design/pro-components';
import { 
  RocketOutlined,
  ThunderboltOutlined,
  ApiOutlined,
  DatabaseOutlined,
  CodeOutlined
} from '@ant-design/icons';
import { apiClient } from '../api';
import { PageTitle } from '../components/UI/TitleComponents';
import { useTheme } from '../contexts/ThemeContext';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import './Home.css';


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
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
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
                title="LazyAI Studio"
                subtitle="懒人的 AI 智能工作室 - 让复杂的开发工作变得简单高效"
                level={1}
                gradient={true}
                animated={true}
              />
            </div>
            <div className="header-badges">
              <Badge count="智能" style={{ backgroundColor: '#52c41a' }} />
              <Badge count="高效" style={{ backgroundColor: '#1890ff' }} />
              <Badge count="便捷" style={{ backgroundColor: '#722ed1' }} />
            </div>
          </div>
        </div>

        {/* 统计卡片区域 */}
        <div className="stats-section">
          <StatisticCard.Group>
            <StatisticCard
              statistic={{
                title: 'AI 模型总数',
                value: stats.totalModels,
                icon: <ApiOutlined style={{ color: '#1890ff' }} />,
                status: 'success'
              }}
              style={{ width: '25%' }}
            />
            <StatisticCard
              statistic={{
                title: '编程助手',
                value: stats.coderModels,
                icon: <CodeOutlined style={{ color: '#52c41a' }} />,
                status: 'success'
              }}
              style={{ width: '25%' }}
            />
            <StatisticCard
              statistic={{
                title: '核心模型',
                value: stats.coreModels,
                icon: <DatabaseOutlined style={{ color: '#722ed1' }} />,
                status: 'success'
              }}
              style={{ width: '25%' }}
            />
            <StatisticCard
              statistic={{
                title: '智能指令',
                value: stats.commands,
                icon: <ThunderboltOutlined style={{ color: '#fa8c16' }} />,
                status: 'success'
              }}
              style={{ width: '25%' }}
            />
          </StatisticCard.Group>
        </div>

      </div>
    </div>
  );
};

export default Home;