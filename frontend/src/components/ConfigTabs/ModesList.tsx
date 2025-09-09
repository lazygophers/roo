import React, { useState, useEffect } from 'react';
import { 
  List, 
  Card, 
  Tag, 
  Space, 
  Input, 
  Select, 
  Row, 
  Col, 
  Typography,
  message,
  Spin
} from 'antd';
import { 
  CodeOutlined, 
  SearchOutlined, 
  SettingOutlined 
} from '@ant-design/icons';
import { apiClient, ModelInfo } from '../../api';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

interface ModesListProps {
  onSelectModel: (model: ModelInfo) => void;
}

const ModesList: React.FC<ModesListProps> = ({ onSelectModel }) => {
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [filteredModels, setFilteredModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');

  useEffect(() => {
    loadModels();
  }, []);

  useEffect(() => {
    filterModels();
  }, [models, searchText, categoryFilter]); // eslint-disable-line react-hooks/exhaustive-deps

  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getModels();
      setModels(response.data);
    } catch (error) {
      console.error('Failed to load models:', error);
      message.error('加载模型失败');
    } finally {
      setLoading(false);
    }
  };

  const filterModels = () => {
    let filtered = models;

    // 分类过滤
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(model => 
        model.groups.includes(categoryFilter)
      );
    }

    // 搜索过滤
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(model =>
        model.name.toLowerCase().includes(searchLower) ||
        model.slug.toLowerCase().includes(searchLower) ||
        model.description.toLowerCase().includes(searchLower) ||
        model.roleDefinition.toLowerCase().includes(searchLower)
      );
    }

    setFilteredModels(filtered);
  };

  const getGroupColor = (groups: any[]) => {
    if (groups.includes('core')) return 'blue';
    if (groups.includes('coder')) return 'green';
    return 'default';
  };

  const getGroupIcon = (groups: any[]) => {
    if (groups.includes('core')) return <SettingOutlined />;
    if (groups.includes('coder')) return <CodeOutlined />;
    return null;
  };

  return (
    <div>
      {/* 搜索和过滤器 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={16}>
          <Search
            placeholder="搜索模型名称、slug、描述..."
            allowClear
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: '100%' }}
          />
        </Col>
        <Col span={8}>
          <Select
            style={{ width: '100%' }}
            value={categoryFilter}
            onChange={setCategoryFilter}
            placeholder="选择分类"
          >
            <Option value="all">全部分类</Option>
            <Option value="core">Core 模式</Option>
            <Option value="coder">Coder 模式</Option>
          </Select>
        </Col>
      </Row>

      {/* 统计信息 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Text type="secondary">
            总计: {models.length} 个模型
          </Text>
          <Text type="secondary">
            当前显示: {filteredModels.length} 个
          </Text>
        </Space>
      </div>

      {/* 模型列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={filteredModels}
          renderItem={(model) => (
            <List.Item style={{ padding: 0, marginBottom: 8 }}>
              <Card
                  size="small"
               
                hoverable
                onClick={() => onSelectModel(model)}
                style={{ width: '100%', cursor: 'pointer' }}
                styles={{ body: { padding: '12px 16px' } }}
              >
                <List.Item.Meta
                  avatar={getGroupIcon(model.groups)}
                  title={
                    <Space>
                      <span style={{ fontWeight: 'bold' }}>{model.name}</span>
                      <Tag 
                        color={getGroupColor(model.groups)}
                      >
                        {model.groups.includes('core') ? 'Core' : 'Coder'}
                      </Tag>
                    </Space>
                  }
                  description={
                    <div>
                      <Paragraph 
                        ellipsis={{ rows: 2, expandable: false }}
                        style={{ marginBottom: 8, fontSize: 13, color: '#666' }}
                      >
                        {model.description}
                      </Paragraph>
                      <div>
                        <Tag color="processing" style={{ fontSize: 10 }}>
                          {model.slug}
                        </Tag>
                        <Text 
                          type="secondary" 
                          style={{ fontSize: 11, marginLeft: 8 }}
                        >
                          点击查看详情
                        </Text>
                      </div>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
          locale={{ emptyText: '没有找到匹配的模型' }}
        />
      </Spin>
    </div>
  );
};

export default ModesList;