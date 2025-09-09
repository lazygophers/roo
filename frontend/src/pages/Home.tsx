import React, { useState, useEffect } from 'react';
import { Card, Statistic, Row, Col, Typography, List, Tag, Space, message } from 'antd';
import { 
  CodeOutlined, 
  FileTextOutlined, 
  SettingOutlined,
  RocketOutlined 
} from '@ant-design/icons';
import { apiClient, ModelInfo } from '../api';

const { Title, Paragraph } = Typography;

const Home: React.FC = () => {
  const [stats, setStats] = useState({
    totalModels: 0,
    coderModels: 0,
    coreModels: 0,
    commands: 0,
    rules: 0
  });
  const [recentModels, setRecentModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);

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
  }, []);

  const getGroupColor = (groups: any[]) => {
    if (groups.includes('core')) return 'blue';
    if (groups.includes('coder')) return 'green';
    return 'default';
  };

  return (
    <div>
      <div style={{ marginBottom: 24 }}>
        <Title level={2}>
          <RocketOutlined style={{ marginRight: 8, color: '#1890ff' }} />
          Roo Models 配置中心
        </Title>
        <Paragraph type="secondary" style={{ fontSize: 16 }}>
          管理和配置您的 AI 模型、指令和规则，提供统一的配置管理界面
        </Paragraph>
      </div>

      {/* 统计卡片 */}
      <Row gutter={16} style={{ marginBottom: 24 }}>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic 
              title="总模型数量" 
              value={stats.totalModels} 
              prefix={<CodeOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic 
              title="编程模型" 
              value={stats.coderModels} 
              prefix={<CodeOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic 
              title="核心模型" 
              value={stats.coreModels} 
              prefix={<SettingOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card loading={loading}>
            <Statistic 
              title="可用指令" 
              value={stats.commands} 
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>
      </Row>

      <Row gutter={16}>
        {/* 最近模型 */}
        <Col span={16}>
          <Card 
            title={
              <Space>
                <CodeOutlined />
                最近模型
              </Space>
            }
            loading={loading}
          >
            <List
              dataSource={recentModels}
              renderItem={(model) => (
                <List.Item>
                  <List.Item.Meta
                    title={
                      <Space>
                        <span>{model.name}</span>
                        <Tag color={getGroupColor(model.groups)}>
                          {model.groups.includes('core') ? 'Core' : 'Coder'}
                        </Tag>
                      </Space>
                    }
                    description={
                      <div>
                        <Paragraph 
                          ellipsis={{ rows: 2, expandable: false }} 
                          style={{ marginBottom: 4 }}
                        >
                          {model.description}
                        </Paragraph>
                        <Tag color="blue" style={{ fontSize: 10 }}>
                          {model.slug}
                        </Tag>
                      </div>
                    }
                  />
                </List.Item>
              )}
            />
          </Card>
        </Col>

        {/* 系统概览 */}
        <Col span={8}>
          <Card 
            title={
              <Space>
                <SettingOutlined />
                系统概览
              </Space>
            }
            loading={loading}
          >
            <div style={{ textAlign: 'center' }}>
              <div style={{ marginBottom: 16 }}>
                <Title level={4} style={{ margin: 0, color: '#1890ff' }}>
                  {stats.totalModels}
                </Title>
                <div style={{ color: '#666', fontSize: 14 }}>总配置项</div>
              </div>
              
              <Row gutter={16}>
                <Col span={12}>
                  <div style={{ padding: '12px 0' }}>
                    <div style={{ fontSize: 20, fontWeight: 'bold', color: '#52c41a' }}>
                      {stats.commands}
                    </div>
                    <div style={{ fontSize: 12, color: '#999' }}>指令</div>
                  </div>
                </Col>
                <Col span={12}>
                  <div style={{ padding: '12px 0' }}>
                    <div style={{ fontSize: 20, fontWeight: 'bold', color: '#fa8c16' }}>
                      {stats.rules}
                    </div>
                    <div style={{ fontSize: 12, color: '#999' }}>规则目录</div>
                  </div>
                </Col>
              </Row>

              <div style={{ 
                marginTop: 16, 
                padding: 12, 
                backgroundColor: '#f0f2f5', 
                borderRadius: 6 
              }}>
                <div style={{ fontSize: 12, color: '#666' }}>
                  系统运行正常 ✅
                </div>
              </div>
            </div>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

export default Home;