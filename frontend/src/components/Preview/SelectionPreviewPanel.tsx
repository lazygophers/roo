import React from 'react';
import { Card, Typography, Tag, Space, Empty, List, Divider, Row, Col } from 'antd';
import { 
  CodeOutlined, 
  FileTextOutlined, 
  BookOutlined,
  InfoCircleOutlined
} from '@ant-design/icons';
import { ModelInfo, FileMetadata } from '../../api';
import { SelectedItem, ModelRuleBinding } from '../../types/selection';

const { Title, Text, Paragraph } = Typography;

interface SelectionPreviewPanelProps {
  selectedItems: SelectedItem[];
  modelRuleBindings: ModelRuleBinding[];
  modelRules?: Record<string, FileMetadata[]>; // 新增：模式关联规则的详细信息
}

const SelectionPreviewPanel: React.FC<SelectionPreviewPanelProps> = ({ 
  selectedItems,
  modelRuleBindings,
  modelRules = {}
}) => {
  // 多选预览显示
    const modelCount = selectedItems.filter(item => item.type === 'model').length;
    const commandCount = selectedItems.filter(item => item.type === 'command').length;
    const standaloneRuleCount = selectedItems.filter(item => item.type === 'rule').length;
    
    // 计算模式关联的规则数量
    const modelAssociatedRuleCount = modelRuleBindings.reduce((total, binding) => {
      return total + binding.selectedRuleIds.length;
    }, 0);
    
    const totalRuleCount = standaloneRuleCount + modelAssociatedRuleCount;
    const totalCount = selectedItems.length + modelAssociatedRuleCount;

    if (totalCount === 0) {
      return (
        <Card 
          title="项目预览"
          style={{ height: '100%' }}
          styles={{ body: { 
            height: 'calc(100% - 57px)', 
            display: 'flex', 
            alignItems: 'center', 
            justifyContent: 'center' 
          } }}
        >
          <Empty
            image={Empty.PRESENTED_IMAGE_SIMPLE}
            description={
              <span>
                尚未选择任何项目
                <br />
                <Text type="secondary">请从左侧列表中选择要预览的项目</Text>
              </span>
            }
          />
        </Card>
      );
    }

    return (
      <Card 
        title={
          <Space>
            <InfoCircleOutlined />
            项目详细预览 ({totalCount} 项)
          </Space>
        }
        style={{ height: '100%' }}
        styles={{ body: { 
          height: 'calc(100% - 57px)', 
          overflow: 'auto',
          padding: '16px 24px'
        } }}
      >
        {/* 统计信息 */}
        <div style={{ marginBottom: 20 }}>
          <Row gutter={16}>
            <Col span={8}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, color: '#52c41a', fontWeight: 'bold' }}>
                  {modelCount}
                </div>
                <div style={{ color: '#666', fontSize: 12 }}>
                  <CodeOutlined /> 模型
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, color: '#1890ff', fontWeight: 'bold' }}>
                  {commandCount}
                </div>
                <div style={{ color: '#666', fontSize: 12 }}>
                  <FileTextOutlined /> 指令
                </div>
              </Card>
            </Col>
            <Col span={8}>
              <Card size="small" style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, color: '#722ed1', fontWeight: 'bold' }}>
                  {totalRuleCount}
                </div>
                <div style={{ color: '#666', fontSize: 12 }}>
                  <BookOutlined /> 规则
                  {modelAssociatedRuleCount > 0 && (
                    <div style={{ fontSize: 10, color: '#999' }}>
                      ({standaloneRuleCount}独立 + {modelAssociatedRuleCount}关联)
                    </div>
                  )}
                </div>
              </Card>
            </Col>
          </Row>
        </div>

        <Divider />

        {/* 选择项目的详细信息 */}
        <div>
          <Title level={4}>选中项目详细信息</Title>
          
          {/* 选中的模型及其关联规则 */}
          {selectedItems.filter(item => item.type === 'model').map((modelItem) => {
            const modelBinding = modelRuleBindings.find(binding => binding.modelId === modelItem.id);
            const associatedRules = modelBinding?.selectedRuleIds || [];
            
            return (
              <div key={`model-${modelItem.id}`} style={{ marginBottom: 24 }}>
                <Card 
                  size="small" 
                  style={{ width: '100%' }}
                  title={
                    <Space>
                      <CodeOutlined style={{ color: '#52c41a' }} />
                      <span style={{ fontWeight: 'bold' }}>{modelItem.name}</span>
                      <Tag color="green">模型</Tag>
                      {associatedRules.length > 0 && (
                        <Tag color="blue">{associatedRules.length} 个关联规则</Tag>
                      )}
                    </Space>
                  }
                  styles={{ body: { padding: '12px 16px' } }}
                >
                  {/* 模型详细信息 */}
                  <div>
                    <div style={{ marginBottom: 12 }}>
                      <Text strong>Slug: </Text>
                      <Tag color="processing">{(modelItem.data as ModelInfo).slug}</Tag>
                      <Tag color="blue">
                        {(modelItem.data as ModelInfo).groups.includes('core') ? 'Core' : 'Coder'}
                      </Tag>
                    </div>
                    
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>描述：</Text>
                      <Paragraph ellipsis={{ rows: 2, expandable: true }} style={{ marginTop: 4, fontSize: 13 }}>
                        {(modelItem.data as ModelInfo).description}
                      </Paragraph>
                    </div>
                    
                    <div style={{ marginBottom: 8 }}>
                      <Text strong>何时使用：</Text>
                      <Paragraph ellipsis={{ rows: 1, expandable: true }} style={{ marginTop: 4, fontSize: 13 }}>
                        {(modelItem.data as ModelInfo).whenToUse}
                      </Paragraph>
                    </div>
                    
                    {/* 关联规则显示 */}
                    {associatedRules.length > 0 && (
                      <div style={{ marginTop: 16, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
                        <div style={{ marginBottom: 12 }}>
                          <Space>
                            <BookOutlined style={{ color: '#722ed1' }} />
                            <Text strong style={{ fontSize: 13 }}>关联规则 ({associatedRules.length} 个)</Text>
                          </Space>
                        </div>
                        <div style={{ paddingLeft: 8 }}>
                          {associatedRules.map((ruleId) => {
                            // 从 modelRules 中找到对应的规则详细信息
                            const allModelRules = modelRules[modelItem.id] || [];
                            const ruleDetail = allModelRules.find(rule => rule.file_path === ruleId);
                            
                            return (
                              <div key={ruleId} style={{ 
                                marginBottom: 12,
                                padding: '8px 12px',
                                backgroundColor: '#f6ffed',
                                border: '1px solid #b7eb8f',
                                borderRadius: '4px'
                              }}>
                                <div style={{ marginBottom: 6 }}>
                                  <Space>
                                    <Text strong style={{ fontSize: 12 }}>
                                      {ruleDetail?.title || ruleDetail?.name || ruleId.split('/').pop()?.replace(/\.[^/.]+$/, "") || '规则'}
                                    </Text>
                                    {ruleDetail?.category && (
                                      <Tag color="blue" style={{ fontSize: 10 }}>
                                        {ruleDetail.category}
                                      </Tag>
                                    )}
                                    {ruleDetail?.language && (
                                      <Tag color="cyan" style={{ fontSize: 10 }}>
                                        {ruleDetail.language}
                                      </Tag>
                                    )}
                                    {ruleDetail?.priority && (
                                      <Tag color="volcano" style={{ fontSize: 10 }}>
                                        优先级: {ruleDetail.priority}
                                      </Tag>
                                    )}
                                  </Space>
                                </div>
                                
                                {ruleDetail?.description && (
                                  <div style={{ marginBottom: 6 }}>
                                    <Paragraph 
                                      ellipsis={{ rows: 2, expandable: true }}
                                      style={{ 
                                        fontSize: 11, 
                                        color: '#666', 
                                        margin: 0,
                                        lineHeight: '16px'
                                      }}
                                    >
                                      {ruleDetail.description}
                                    </Paragraph>
                                  </div>
                                )}
                                
                                <div style={{ fontSize: 10, color: '#999' }}>
                                  <Space split={<span>|</span>}>
                                    <span>文件: {ruleId.split('/').pop()}</span>
                                    {ruleDetail?.file_size && (
                                      <span>大小: {(ruleDetail.file_size / 1024).toFixed(2)}KB</span>
                                    )}
                                    <span>
                                      来源: {ruleDetail?.source_directory?.split('/').pop() || '规则目录'}
                                    </span>
                                  </Space>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      </div>
                    )}
                  </div>
                </Card>
              </div>
            );
          })}

          {/* 独立选择的指令和规则 */}
          <List
            dataSource={selectedItems.filter(item => item.type !== 'model')}
            renderItem={(item, index) => (
              <List.Item style={{ padding: 0, marginBottom: 16 }}>
                <Card 
                  size="small" 
                  style={{ width: '100%' }}
                  title={
                    <Space>
                      {item.type === 'command' && <FileTextOutlined style={{ color: '#1890ff' }} />}
                      {item.type === 'rule' && <BookOutlined style={{ color: '#722ed1' }} />}
                      <span style={{ fontWeight: 'bold' }}>{item.name}</span>
                      <Tag color={item.type === 'command' ? 'blue' : 'purple'}>
                        {item.type === 'command' ? '指令' : '规则'}
                      </Tag>
                    </Space>
                  }
                  styles={{ body: { padding: '12px 16px' } }}
                >
                  {/* 指令详细信息 */}
                  {item.type === 'command' && (
                    <div>
                      <div style={{ marginBottom: 12 }}>
                        <Space>
                          {(item.data as FileMetadata).category && (
                            <Tag color="blue">{(item.data as FileMetadata).category}</Tag>
                          )}
                          {(item.data as FileMetadata).language && (
                            <Tag color="green">{(item.data as FileMetadata).language}</Tag>
                          )}
                        </Space>
                      </div>
                      
                      {(item.data as FileMetadata).description && (
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>描述：</Text>
                          <Paragraph ellipsis={{ rows: 2, expandable: true }} style={{ marginTop: 4, fontSize: 13 }}>
                            {(item.data as FileMetadata).description}
                          </Paragraph>
                        </div>
                      )}
                      
                      <div style={{ fontSize: 12, color: '#666' }}>
                        <Text type="secondary">
                          文件: {(item.data as FileMetadata).file_path.split('/').pop()} | 
                          大小: {((item.data as FileMetadata).file_size / 1024).toFixed(2)}KB
                        </Text>
                      </div>
                    </div>
                  )}

                  {/* 规则详细信息 */}
                  {item.type === 'rule' && (
                    <div>
                      <div style={{ marginBottom: 12 }}>
                        <Space>
                          <Tag color="purple">
                            {(item.data as FileMetadata).file_path.split('.').pop()?.toUpperCase() || 'FILE'}
                          </Tag>
                          {(item.data as FileMetadata).category && (
                            <Tag color="blue">{(item.data as FileMetadata).category}</Tag>
                          )}
                          {(item.data as FileMetadata).language && (
                            <Tag color="cyan">{(item.data as FileMetadata).language}</Tag>
                          )}
                          {(item.data as FileMetadata).priority && (
                            <Tag color="volcano">优先级: {(item.data as FileMetadata).priority}</Tag>
                          )}
                        </Space>
                      </div>
                      
                      {(item.data as FileMetadata).description && (
                        <div style={{ marginBottom: 8 }}>
                          <Text strong>描述：</Text>
                          <Paragraph ellipsis={{ rows: 2, expandable: true }} style={{ marginTop: 4, fontSize: 13 }}>
                            {(item.data as FileMetadata).description}
                          </Paragraph>
                        </div>
                      )}
                      
                      <div style={{ fontSize: 12, color: '#666' }}>
                        <Text type="secondary">
                          文件: {(item.data as FileMetadata).file_path.split('/').pop()} | 
                          来源: {(item.data as FileMetadata).source_directory.split('/').pop()} | 
                          大小: {((item.data as FileMetadata).file_size / 1024).toFixed(2)}KB
                        </Text>
                      </div>
                    </div>
                  )}
                </Card>
              </List.Item>
            )}
          />
        </div>

        {/* 底部导出提示 */}
        <div style={{ 
          marginTop: 20, 
          padding: '12px 16px', 
          backgroundColor: '#f6ffed', 
          borderRadius: 6,
          border: '1px solid #b7eb8f'
        }}>
          <Title level={5} style={{ color: '#389e0d', margin: 0, marginBottom: 8 }}>
            导出预览
          </Title>
          <Text style={{ fontSize: 12, color: '#666' }}>
            选中的 {totalCount} 个项目将被导出为配置文件，包含所有详细信息和元数据
          </Text>
        </div>
      </Card>
    );
};

export default SelectionPreviewPanel;