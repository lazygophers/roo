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
  BookOutlined, 
  FolderOutlined
} from '@ant-design/icons';
import { apiClient, FileMetadata } from '../../api';

const { Text, Paragraph } = Typography;

interface RulesListProps {
  onSelectRule: (rule: FileMetadata) => void;
}

const RulesList: React.FC<RulesListProps> = ({ onSelectRule }) => {
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

      // 由于默认规则目录是 "rules"，我们获取 rules 目录的内容
      // 但首先检查 API 中是否有专门获取默认规则的接口
      // 这里我们尝试获取 "rules" slug 的规则
      try {
        const rulesResponse = await apiClient.getRulesBySlug('rules');
        setRules(rulesResponse.data);
      } catch (error) {
        // 如果没有 rules 目录，显示空列表
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
      {/* 统计信息 */}
      <div style={{ marginBottom: 16 }}>
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
        </Space>
      </div>

      {/* 规则列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={rules}
          renderItem={(rule) => (
            <List.Item style={{ padding: 0, marginBottom: 8 }}>
              <Card
                  size="small"
               
                hoverable
                onClick={() => onSelectRule(rule)}
                style={{ width: '100%', cursor: 'pointer' }}
                styles={{ body: { padding: '12px 16px' } }}
              >
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
                      </div>
                    </div>
                  }
                />
              </Card>
            </List.Item>
          )}
          locale={{ emptyText: '没有找到规则文件' }}
        />
      </Spin>
    </div>
  );
};

export default RulesList;