import React, { useState, useEffect } from 'react';
import { 
  List, 
  Card, 
  Tag, 
  Space, 
  Typography,
  message,
  Spin,
  Empty,
  Checkbox,
  Button,
  Row,
  Col
} from 'antd';
import { 
  BookOutlined, 
  ClockCircleOutlined,
  FolderOutlined,
  CheckOutlined
} from '@ant-design/icons';
import { apiClient, FileMetadata } from '../../api';
import { SelectedItem } from '../../types/selection';

const { Text, Paragraph } = Typography;

interface RulesListProps {
  selectedItems: SelectedItem[];
  onToggleSelection: (item: SelectedItem) => void;
  onSelectAll: (items: SelectedItem[]) => void;
  onClearSelection: () => void;
}

const RulesListWithSelection: React.FC<RulesListProps> = ({ 
  selectedItems, 
  onToggleSelection,
  onSelectAll,
  onClearSelection
}) => {
  const [rules, setRules] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);
  const [directories, setDirectories] = useState<any[]>([]);

  useEffect(() => {
    loadRules();
  }, []);

  const loadRules = async () => {
    try {
      setLoading(true);
      // 获取可用的 rules 目录列表
      const dirsResponse = await apiClient.getRules();
      setDirectories(dirsResponse.data);

      // 获取默认 rules 目录的内容
      try {
        const rulesResponse = await apiClient.getRulesBySlug('rules');
        setRules(rulesResponse.data);
      } catch (error) {
        console.warn('No default rules directory found');
        setRules([]);
      }
    } catch (error) {
      console.error('Failed to load rules:', error);
      message.error('加载规则失败');
    } finally {
      setLoading(false);
    }
  };

  const formatFileSize = (bytes: number): string => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const formatDate = (dateString: string): string => {
    return new Date(dateString).toLocaleString('zh-CN');
  };

  const getFileExtension = (filePath: string): string => {
    return filePath.split('.').pop()?.toUpperCase() || 'FILE';
  };

  const getExtensionColor = (extension: string): string => {
    const colorMap: Record<string, string> = {
      'MD': 'blue',
      'TXT': 'green',
      'YML': 'orange',
      'YAML': 'orange',
      'JSON': 'purple'
    };
    return colorMap[extension] || 'default';
  };

  const isSelected = (rulePath: string) => {
    return selectedItems.some(item => item.id === rulePath && item.type === 'rule');
  };

  const handleToggleSelection = (rule: FileMetadata) => {
    const selectedItem: SelectedItem = {
      id: rule.file_path,
      type: 'rule',
      name: rule.title || rule.name || rule.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || '未命名规则',
      data: rule
    };
    onToggleSelection(selectedItem);
  };

  const handleSelectAllVisible = () => {
    const visibleItems: SelectedItem[] = rules.map(rule => ({
      id: rule.file_path,
      type: 'rule',
      name: rule.title || rule.name || rule.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || '未命名规则',
      data: rule
    }));
    onSelectAll(visibleItems);
  };

  const selectedRuleCount = selectedItems.filter(item => item.type === 'rule').length;

  if (rules.length === 0 && !loading) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={
          <span>
            暂无默认规则文件
            <br />
            <Text type="secondary">
              找到 {directories.length} 个规则目录，但默认 rules 目录为空
            </Text>
          </span>
        }
      />
    );
  }

  return (
    <div>
      {/* 统计信息和批量操作 */}
      <div style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text type="secondary">
                默认规则: {rules.length} 个文件
              </Text>
              <Text type="secondary">
                规则目录: {directories.length} 个
              </Text>
              {rules.length > 0 && (
                <Text type="secondary">
                  总大小: {formatFileSize(rules.reduce((sum, rule) => sum + rule.file_size, 0))}
                </Text>
              )}
              <Text type="success">
                已选择: {selectedRuleCount} 个规则
              </Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button 
                size="small"
                
                onClick={handleSelectAllVisible}
                disabled={rules.length === 0}
              >
                全选当前页
              </Button>
              <Button 
                size="small"
                
                onClick={onClearSelection}
                disabled={selectedRuleCount === 0}
              >
                清空选择
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 规则列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={rules}
          renderItem={(rule) => {
            const isItemSelected = isSelected(rule.file_path);
            return (
              <List.Item style={{ padding: 0, marginBottom: 8 }}>
                <Card
                  size="small"
                 
                  hoverable
                  onClick={() => handleToggleSelection(rule)}
                  style={{ 
                    width: '100%', 
                    cursor: 'pointer',
                    border: isItemSelected ? '2px solid #1890ff' : '1px solid #d9d9d9',
                    backgroundColor: isItemSelected ? '#f6ffed' : '#fff'
                  }}
                  styles={{ body: { padding: '12px 16px' } }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <div style={{ marginRight: 12, marginTop: 4 }}>
                      <Checkbox 
                        checked={isItemSelected}
                        onChange={() => handleToggleSelection(rule)}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <List.Item.Meta
                        avatar={<BookOutlined style={{ fontSize: 16, color: '#722ed1' }} />}
                        title={
                          <Space>
                            <span style={{ fontWeight: 'bold' }}>
                              {rule.title || rule.name || rule.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || '未命名规则'}
                            </span>
                            <Tag 
                              color={getExtensionColor(getFileExtension(rule.file_path))}
                            >
                              {getFileExtension(rule.file_path)}
                            </Tag>
                            {rule.category && (
                              <Tag color="blue">
                                {rule.category}
                              </Tag>
                            )}
                            {isItemSelected && (
                              <Tag color="success" icon={<CheckOutlined />}>
                                已选择
                              </Tag>
                            )}
                          </Space>
                        }
                        description={
                          <div>
                            {rule.description && (
                              <Paragraph 
                                ellipsis={{ rows: 2, expandable: false }}
                                style={{ marginBottom: 8, fontSize: 13, color: '#666' }}
                              >
                                {rule.description}
                              </Paragraph>
                            )}
                            
                            {/* 标签和章节 */}
                            {((rule.tags && rule.tags.length > 0) || (rule.sections && rule.sections.length > 0)) && (
                              <div style={{ marginBottom: 8 }}>
                                <Space wrap>
                                  {rule.tags?.map((tag, index) => (
                                    <Tag key={`tag-${index}`} color="processing">
                                      {tag}
                                    </Tag>
                                  ))}
                                  {rule.sections?.slice(0, 3).map((section, index) => (
                                    <Tag key={`section-${index}`} color="default">
                                      {section}
                                    </Tag>
                                  ))}
                                  {rule.sections && rule.sections.length > 3 && (
                                    <Tag color="default">
                                      +{rule.sections.length - 3} 更多
                                    </Tag>
                                  )}
                                </Space>
                              </div>
                            )}

                            {/* 优先级和语言 */}
                            {(rule.priority || rule.language) && (
                              <div style={{ marginBottom: 8 }}>
                                <Space>
                                  {rule.priority && (
                                    <Tag color="volcano">
                                      优先级: {rule.priority}
                                    </Tag>
                                  )}
                                  {rule.language && (
                                    <Tag color="cyan">
                                      {rule.language}
                                    </Tag>
                                  )}
                                </Space>
                              </div>
                            )}

                            {/* 文件信息 */}
                            <div style={{ marginTop: 8 }}>
                              <Space size="large" style={{ fontSize: 11, color: '#999' }}>
                                <Space>
                                  <FolderOutlined />
                                  <Text type="secondary">
                                    {formatFileSize(rule.file_size)}
                                  </Text>
                                </Space>
                                <Space>
                                  <ClockCircleOutlined />
                                  <Text type="secondary">
                                    {formatDate(rule.last_modified)}
                                  </Text>
                                </Space>
                              </Space>
                            </div>
                            
                            <div style={{ marginTop: 4 }}>
                              <Text 
                                type="secondary" 
                                style={{ fontSize: 10 }}
                              >
                                {rule.file_path.split('/').pop()}
                              </Text>
                              <Text 
                                type="secondary" 
                                style={{ fontSize: 10, marginLeft: 8 }}
                              >
                                来自: {rule.source_directory.split('/').pop()}
                              </Text>
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
                  </div>
                </Card>
              </List.Item>
            );
          }}
          locale={{ emptyText: '没有找到规则文件' }}
        />
      </Spin>
    </div>
  );
};

export default RulesListWithSelection;