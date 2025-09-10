import React, { useState, useEffect } from 'react';
import { 
  List, 
  Card, 
  Tag, 
  Space, 
  Typography,
  message,
  Spin,
  Empty
} from 'antd';
import { 
  FileTextOutlined, 
  ClockCircleOutlined,
  FolderOutlined
} from '@ant-design/icons';
import { apiClient, FileMetadata } from '../../api';

const { Text, Paragraph } = Typography;

interface CommandsListProps {
  onSelectCommand: (command: FileMetadata) => void;
}

const CommandsList: React.FC<CommandsListProps> = ({ onSelectCommand }) => {
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

  const formatDate = (timestamp: number): string => {
    return new Date(timestamp * 1000).toLocaleString('zh-CN');
  };

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
      {/* 统计信息 */}
      <div style={{ marginBottom: 16 }}>
        <Space>
          <Text type="secondary">
            总计: {commands.length} 个指令文件
          </Text>
          {commands.length > 0 && (
            <Text type="secondary">
              总大小: {formatFileSize(commands.reduce((sum, cmd) => sum + cmd.file_size, 0))}
            </Text>
          )}
        </Space>
      </div>

      {/* 指令列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={commands}
          renderItem={(command) => (
            <List.Item style={{ padding: 0, marginBottom: 8 }}>
              <Card
                  size="small"
               
                hoverable
                onClick={() => onSelectCommand(command)}
                style={{ width: '100%', cursor: 'pointer' }}
                bodyStyle={{ padding: '12px 16px' }}
              >
                <List.Item.Meta
                  avatar={<FileTextOutlined style={{ fontSize: 16, color: '#1890ff' }} />}
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
                    </Space>
                  }
                  description={
                    <div>
                      {command.description && (
                        <Paragraph 
                          ellipsis={{ rows: 2, expandable: false }}
                          style={{ marginBottom: 8, fontSize: 13, color: '#666' }}
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
                        <Space size="large" style={{ fontSize: 11, color: '#999' }}>
                          <Space>
                            <FolderOutlined />
                            <Text type="secondary">
                              {formatFileSize(command.file_size)}
                            </Text>
                          </Space>
                          <Space>
                            <ClockCircleOutlined />
                            <Text type="secondary">
                              {formatDate(command.last_modified)}
                            </Text>
                          </Space>
                        </Space>
                      </div>
                      
                      <div style={{ marginTop: 4 }}>
                        <Text 
                          type="secondary" 
                          style={{ fontSize: 10 }}
                        >
                          {command.file_path.split('/').pop()}
                        </Text>
                      </div>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
          locale={{ emptyText: '没有找到指令文件' }}
        />
      </Spin>
    </div>
  );
};

export default CommandsList;