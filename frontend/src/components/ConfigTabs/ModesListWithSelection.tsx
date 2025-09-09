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
  Spin,
  Checkbox,
  Button,
  theme
} from 'antd';
import { 
  CodeOutlined, 
  SearchOutlined, 
  SettingOutlined,
  CheckOutlined,
  BookOutlined,
  DownOutlined,
  RightOutlined
} from '@ant-design/icons';
import { apiClient, ModelInfo, FileMetadata } from '../../api';
import { SelectedItem, ModelRuleBinding } from '../../types/selection';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

interface ModesListProps {
  selectedItems: SelectedItem[];
  onToggleSelection: (item: SelectedItem) => void;
  onSelectAll: (items: SelectedItem[]) => void;
  onClearSelection: () => void;
  modelRuleBindings: ModelRuleBinding[];
  onModelRuleBinding: (modelId: string, ruleId: string, selected: boolean) => void;
  getModelRuleBindings: (modelId: string) => string[];
  onUpdateModelRules?: (modelId: string, rules: FileMetadata[]) => void;
}

const ModesListWithSelection: React.FC<ModesListProps> = ({ 
  selectedItems, 
  onToggleSelection,
  onSelectAll,
  onClearSelection,
  modelRuleBindings,
  onModelRuleBinding,
  getModelRuleBindings,
  onUpdateModelRules
}) => {
  const { token } = theme.useToken();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [filteredModels, setFilteredModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [modelRules, setModelRules] = useState<Record<string, FileMetadata[]>>({});
  const [loadingRules, setLoadingRules] = useState<Record<string, boolean>>({});
  const [expandedModels, setExpandedModels] = useState<Set<string>>(new Set());

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

  const isSelected = (modelSlug: string) => {
    return selectedItems.some(item => item.id === modelSlug && item.type === 'model');
  };

  const handleToggleSelection = (model: ModelInfo) => {
    const selectedItem: SelectedItem = {
      id: model.slug,
      type: 'model',
      name: model.name,
      data: model
    };
    onToggleSelection(selectedItem);
    
    // 当选择模式时，自动展开并加载关联规则
    if (!isSelected(model.slug)) {
      handleModelExpand(model.slug);
    }
  };

  const handleRuleToggleSelection = (rule: FileMetadata, modelSlug: string) => {
    const currentlySelected = isRuleSelectedForModel(rule.file_path, modelSlug);
    onModelRuleBinding(modelSlug, rule.file_path, !currentlySelected);
  };
  
  // 检查规则是否被特定模式选择
  const isRuleSelectedForModel = (rulePath: string, modelSlug: string): boolean => {
    const bindings = getModelRuleBindings(modelSlug);
    return bindings.includes(rulePath);
  };

  // 模式slug到规则slug的映射关系
  const getModelRuleSlug = (modelSlug: string): string | null => {
    // 模式和对应的规则目录映射
    const modelRuleMapping: Record<string, string> = {
      'architect': 'rules-code-architect', // 对应 rules-code-architect 目录
      'orchestrator': 'rules-orchestrator', // 对应 rules-orchestrator 目录
      'ask': 'rules-ask', // 对应 rules-ask 目录
      'code-python': 'rules-code-python',
      'code-golang': 'rules-code-golang', 
      'code-java': 'rules-code-java',
      'code-react': 'rules-code-react',
      'code-rust': 'rules-code-rust',
      'code-vue': 'rules-code-vue',
      'debug': 'rules-debug',
      'doc-writer': 'rules-doc-writer',
      'memory': 'rules-memory',
      'project-research': 'rules-project-research'
    };
    
    return modelRuleMapping[modelSlug] || null;
  };

  const handleModelExpand = async (modelSlug: string) => {
    const newExpandedModels = new Set(expandedModels);
    
    if (expandedModels.has(modelSlug)) {
      newExpandedModels.delete(modelSlug);
      setExpandedModels(newExpandedModels);
      return;
    }
    
    newExpandedModels.add(modelSlug);
    setExpandedModels(newExpandedModels);
    
    // 如果还没有加载过这个模式的规则，则加载
    if (!modelRules[modelSlug] && !loadingRules[modelSlug]) {
      const ruleSlug = getModelRuleSlug(modelSlug);
      
      if (!ruleSlug) {
        // 没有对应的规则目录
        setModelRules(prev => ({ ...prev, [modelSlug]: [] }));
        return;
      }
      
      setLoadingRules(prev => ({ ...prev, [modelSlug]: true }));
      
      try {
        // 使用现有的 getRulesBySlug API 获取对应规则目录的内容
        const response = await apiClient.getRulesBySlug(ruleSlug);
        const rules = response.data;
        setModelRules(prev => ({ ...prev, [modelSlug]: rules }));
        
        // 通知父组件更新模式规则详细信息
        if (onUpdateModelRules) {
          onUpdateModelRules(modelSlug, rules);
        }
      } catch (error: any) {
        console.warn(`Failed to load rules for model ${modelSlug} (rule slug: ${ruleSlug}):`, error);
        const emptyRules: FileMetadata[] = [];
        setModelRules(prev => ({ ...prev, [modelSlug]: emptyRules }));
        
        // 通知父组件空规则列表
        if (onUpdateModelRules) {
          onUpdateModelRules(modelSlug, emptyRules);
        }
        
        if (error.response?.status === 404) {
          message.info(`模式 "${modelSlug}" 对应的规则目录 "${ruleSlug}" 不存在`);
        } else {
          message.error(`加载模式 "${modelSlug}" 的关联规则失败`);
        }
      } finally {
        setLoadingRules(prev => ({ ...prev, [modelSlug]: false }));
      }
    }
  };

  const handleSelectAllVisible = () => {
    const visibleItems: SelectedItem[] = filteredModels.map(model => ({
      id: model.slug,
      type: 'model',
      name: model.name,
      data: model
    }));
    onSelectAll(visibleItems);
  };

  const selectedModelCount = selectedItems.filter(item => item.type === 'model').length;

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

      {/* 统计信息和批量操作 */}
      <div style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text type="secondary">
                总计: {models.length} 个模型
              </Text>
              <Text type="secondary">
                当前显示: {filteredModels.length} 个
              </Text>
              <Text type="success">
                已选择: {selectedModelCount} 个模型
              </Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button 
                size="small"
                
                onClick={handleSelectAllVisible}
                disabled={filteredModels.length === 0}
              >
                全选当前页
              </Button>
              <Button 
                size="small"
                
                onClick={onClearSelection}
                disabled={selectedModelCount === 0}
              >
                清空选择
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 模型列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={filteredModels}
          renderItem={(model) => {
            const isItemSelected = isSelected(model.slug);
            const isExpanded = expandedModels.has(model.slug);
            const associatedRules = modelRules[model.slug] || [];
            const isLoadingModelRules = loadingRules[model.slug] || false;
            
            return (
              <List.Item style={{ padding: 0, marginBottom: 8 }}>
                <Card
                  size="small"
                  style={{ 
                    width: '100%',
                    border: isItemSelected 
                      ? `2px solid ${token.colorPrimary}` 
                      : `1px solid ${token.colorBorder}`,
                    backgroundColor: isItemSelected 
                      ? token.colorBgContainer 
                      : token.colorBgContainer,
                    boxShadow: isItemSelected 
                      ? `0 0 0 2px ${token.colorPrimary}20` 
                      : 'none'
                  }}
                  styles={{ body: { padding: '12px 16px' } }}
                >
                  {/* 模式主体 */}
                  <div 
                    style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }}
                    onClick={() => handleToggleSelection(model)}
                  >
                    <div style={{ marginRight: 12, marginTop: 4 }}>
                      <Checkbox 
                        checked={isItemSelected}
                        onChange={() => handleToggleSelection(model)}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <List.Item.Meta
                        avatar={getGroupIcon(model.groups)}
                        title={
                          <Space>
                            <span style={{ fontWeight: 'bold' }}>{model.name}</span>
                            <Tag color={getGroupColor(model.groups)}>
                              {model.groups.includes('core') ? 'Core' : 'Coder'}
                            </Tag>
                            {isItemSelected && (
                              <Tag color="success" icon={<CheckOutlined />}>
                                已选择
                              </Tag>
                            )}
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
                                点击选择/取消
                              </Text>
                            </div>
                          </div>
                        }
                      />
                    </div>
                    <div style={{ marginLeft: 8 }}>
                      <Button
                        type="text"
                        size="small"
                        icon={isExpanded ? <DownOutlined /> : <RightOutlined />}
                        onClick={(e) => {
                          e.stopPropagation();
                          handleModelExpand(model.slug);
                        }}
                        style={{ fontSize: 12 }}
                      >
                        关联规则
                      </Button>
                    </div>
                  </div>

                  {/* 关联规则区域 */}
                  {isExpanded && (
                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                      <div style={{ marginBottom: 8 }}>
                        <Space>
                          <BookOutlined style={{ color: '#722ed1' }} />
                          <Text strong style={{ fontSize: 13 }}>关联规则</Text>
                          {associatedRules.length > 0 && (
                            <Tag color="blue">{associatedRules.length} 个</Tag>
                          )}
                        </Space>
                      </div>
                      
                      {isLoadingModelRules ? (
                        <div style={{ textAlign: 'center', padding: '20px 0' }}>
                          <Spin size="small" />
                          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                            加载关联规则...
                          </Text>
                        </div>
                      ) : associatedRules.length === 0 ? (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          该模式没有关联规则
                        </Text>
                      ) : (
                        <div style={{ maxHeight: '200px', overflowY: 'auto' }}>
                          {associatedRules.map((rule, index) => {
                            const ruleSelected = isRuleSelectedForModel(rule.file_path, model.slug);
                            return (
                              <div
                                key={rule.file_path}
                                style={{
                                  padding: '6px 8px',
                                  border: ruleSelected 
                                    ? `1px solid ${token.colorPrimary}` 
                                    : `1px solid ${token.colorBorderSecondary}`,
                                  borderRadius: '4px',
                                  backgroundColor: ruleSelected 
                                    ? token.colorFillSecondary
                                    : token.colorFillTertiary,
                                  marginBottom: '4px',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                                onClick={() => handleRuleToggleSelection(rule, model.slug)}
                              >
                                <Checkbox
                                  checked={ruleSelected}
                                  style={{ marginRight: 8 }}
                                  onChange={() => handleRuleToggleSelection(rule, model.slug)}
                                />
                                <div style={{ flex: 1 }}>
                                  <div>
                                    <Text style={{ fontSize: 12, fontWeight: ruleSelected ? 'bold' : 'normal' }}>
                                      {rule.title || rule.name || rule.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || '未命名规则'}
                                    </Text>
                                    {rule.category && (
                                      <Tag color="blue" style={{ marginLeft: 4, fontSize: 10 }}>
                                        {rule.category}
                                      </Tag>
                                    )}
                                  </div>
                                  {rule.description && (
                                    <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>
                                      {rule.description.substring(0, 50)}{rule.description.length > 50 ? '...' : ''}
                                    </Text>
                                  )}
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              </List.Item>
            );
          }}
          locale={{ emptyText: '没有找到匹配的模型' }}
        />
      </Spin>
    </div>
  );
};

export default ModesListWithSelection;