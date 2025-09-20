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
  Col,
  theme
} from 'antd';
import { 
  FileTextOutlined, 
  FolderOutlined,
  CheckOutlined
} from '@ant-design/icons';
import { apiClient, FileMetadata } from '../../api';
import { SelectedItem } from '../../types/selection';

const { Text, Paragraph } = Typography;

interface CommandsListProps {
  selectedItems: SelectedItem[];
  onToggleSelection: (item: SelectedItem) => void;
  onSelectAll: (items: SelectedItem[]) => void;
  onClearSelection: () => void;
}

const CommandsListWithSelection: React.FC<CommandsListProps> = ({ 
  selectedItems, 
  onToggleSelection,
  onSelectAll,
  onClearSelection
}) => {
  const { token } = theme.useToken();
  const [commands, setCommands] = useState<FileMetadata[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadCommands();
  }, []);

  const loadCommands = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getCommands();
      setCommands(response.data);
    } catch (error) {
      console.error('Failed to load commands:', error);
      message.error('加载指令失败');
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


  const isSelected = (commandPath: string) => {
    return selectedItems.some(item => item.id === commandPath && item.type === 'command');
  };

  const handleToggleSelection = (command: FileMetadata) => {
    const selectedItem: SelectedItem = {
      id: command.file_path,
      type: 'command',
      name: command.title || command.name || '未命名指令',
      data: command
    };
    onToggleSelection(selectedItem);
  };

  const handleSelectAllVisible = () => {
    const visibleItems: SelectedItem[] = commands.map(command => ({
      id: command.file_path,
      type: 'command',
      name: command.title || command.name || '未命名指令',
      data: command
    }));
    onSelectAll(visibleItems);
  };

  const selectedCommandCount = selectedItems.filter(item => item.type === 'command').length;

  if (commands.length === 0 && !loading) {
    return (
      <Empty
        image={Empty.PRESENTED_IMAGE_SIMPLE}
        description={
          <span>
            暂无可用指令
            <br />
            <Text type="secondary">commands 目录为空</Text>
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
                总计: {commands.length} 个指令文件
              </Text>
              {commands.length > 0 && (
                <Text type="secondary">
                  总大小: {formatFileSize(commands.reduce((sum, cmd) => sum + cmd.file_size, 0))}
                </Text>
              )}
              <Text type="success">
                已选择: {selectedCommandCount} 个指令
              </Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button 
                size="small"
                
                onClick={handleSelectAllVisible}
                disabled={commands.length === 0}
              >
                全选当前页
              </Button>
              <Button 
                size="small"
                
                onClick={onClearSelection}
                disabled={selectedCommandCount === 0}
              >
                清空选择
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 指令列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={commands}
          renderItem={(command) => {
            const isItemSelected = isSelected(command.file_path);
            return (
              <List.Item style={{ padding: 0, marginBottom: 8 }}>
                <Card
                  size="small"
                 
                  hoverable
                  onClick={() => handleToggleSelection(command)}
                  style={{ 
                    width: '100%', 
                    cursor: 'pointer',
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
                  <div style={{ display: 'flex', alignItems: 'flex-start' }}>
                    <div style={{ marginRight: 12, marginTop: 4 }}>
                      <Checkbox 
                        checked={isItemSelected}
                        onChange={() => handleToggleSelection(command)}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <List.Item.Meta
                        avatar={<FileTextOutlined style={{ fontSize: 16, color: token.colorPrimary }} />}
                        title={
                          <Space>
                            <span style={{ fontWeight: 'bold' }}>
                              {command.title || command.name || '未命名指令'}
                            </span>
                            {command.category && (
                              <Tag color="blue">
                                {command.category}
                              </Tag>
                            )}
                            {command.language && (
                              <Tag color="green">
                                {command.language}
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
                            {command.description && (
                              <Paragraph 
                                ellipsis={{ rows: 2, expandable: false }}
                                style={{ marginBottom: 8, fontSize: 13, color: token.colorTextSecondary }}
                              >
                                {command.description}
                              </Paragraph>
                            )}
                            
                            {/* 标签 */}
                            {command.tags && command.tags.length > 0 && (
                              <div style={{ marginBottom: 8 }}>
                                <Space wrap>
                                  {command.tags.map((tag, index) => (
                                    <Tag key={index} color="processing">
                                      {tag}
                                    </Tag>
                                  ))}
                                </Space>
                              </div>
                            )}

                            {/* 文件信息 */}
                            <div style={{ marginTop: 8 }}>
                              <Space size="large" style={{ fontSize: 11, color: token.colorTextTertiary }}>
                                <Space>
                                  <FolderOutlined />
                                  <Text type="secondary">
                                    {formatFileSize(command.file_size)}
                                  </Text>
                                </Space>
                              </Space>
                            </div>
                            
                            <div style={{ marginTop: 4 }}>
                              <Text 
                                type="secondary" 
                                style={{ fontSize: 10 }}
                              >
                                📁 {command.file_path?.replace(/^.*\/resources\//, '') || 'N/A'}
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
          locale={{ emptyText: '没有找到指令文件' }}
        />
      </Spin>
    </div>
  );
};

export default CommandsListWithSelection;