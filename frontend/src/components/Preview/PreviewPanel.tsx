import React from 'react';
import { Card, Typography, Tag, Space, Descriptions, Empty, Divider } from 'antd';
import { 
  CodeOutlined, 
  FileTextOutlined, 
  BookOutlined,
  InfoCircleOutlined,
  ClockCircleOutlined,
  FolderOutlined
} from '@ant-design/icons';
import { ModelInfo, FileMetadata } from '../../api';

const { Title, Paragraph, Text } = Typography;

interface PreviewPanelProps {
  selectedItem: ModelInfo | FileMetadata | null;
  itemType: 'model' | 'command' | 'rule' | null;
}

const PreviewPanel: React.FC<PreviewPanelProps> = ({ selectedItem, itemType }) => {
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

  if (!selectedItem || !itemType) {
    return (
      <div style={{ height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <Empty
          image={Empty.PRESENTED_IMAGE_SIMPLE}
          description={
            <span>
              请从左侧列表中选择一个项目
              <br />
              <Text type="secondary">选择后将在此处显示详细信息</Text>
            </span>
          }
        />
      </div>
    );
  }

  const renderModelPreview = (model: ModelInfo) => (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Space>
          <CodeOutlined style={{ fontSize: 20, color: '#1890ff' }} />
          <Title level={3} style={{ margin: 0 }}>
            {model.name}
          </Title>
          <Tag color={model.groups.includes('core') ? 'blue' : 'green'}>
            {model.groups.includes('core') ? 'Core' : 'Coder'}
          </Tag>
        </Space>
      </div>

      <Descriptions column={1} bordered size="middle">
        <Descriptions.Item label="Slug">
          <Text code>{model.slug}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="分组">
          <Space>
            {model.groups.map((group, index) => (
              <Tag key={index} color="blue">
                {group}
              </Tag>
            ))}
          </Space>
        </Descriptions.Item>
        <Descriptions.Item label="文件路径">
          <Text type="secondary" style={{ fontSize: 12 }}>
            {model.file_path}
          </Text>
        </Descriptions.Item>
      </Descriptions>

      <Divider />

      <div style={{ marginBottom: 16 }}>
        <Title level={4}>
          <InfoCircleOutlined style={{ marginRight: 8 }} />
          描述
        </Title>
        <Paragraph style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
          {model.description}
        </Paragraph>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Title level={4}>角色定义</Title>
        <Paragraph style={{ backgroundColor: '#f0f2f5', padding: 12, borderRadius: 6 }}>
          {model.roleDefinition}
        </Paragraph>
      </div>

      <div style={{ marginBottom: 16 }}>
        <Title level={4}>使用场景</Title>
        <Paragraph style={{ backgroundColor: '#f6ffed', padding: 12, borderRadius: 6 }}>
          {model.whenToUse}
        </Paragraph>
      </div>
    </div>
  );

  const renderFilePreview = (file: FileMetadata, icon: React.ReactNode, title: string) => (
    <div>
      <div style={{ marginBottom: 16 }}>
        <Space>
          {icon}
          <Title level={3} style={{ margin: 0 }}>
            {file.title || file.name || file.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || title}
          </Title>
          {file.category && (
            <Tag color="blue">{file.category}</Tag>
          )}
          {file.language && (
            <Tag color="green">{file.language}</Tag>
          )}
        </Space>
      </div>

      <Descriptions column={2} bordered size="middle">
        <Descriptions.Item label="文件名">
          <Text>{file.file_path.split('/').pop()}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="文件大小">
          <Text>{formatFileSize(file.file_size)}</Text>
        </Descriptions.Item>
        <Descriptions.Item label="来源目录">
          <Space size="small">
            <FolderOutlined />
            <Text type="secondary">
              {file.source_directory.split('/').pop()}
            </Text>
          </Space>
        </Descriptions.Item>
      </Descriptions>

      {file.priority && (
        <div style={{ margin: '16px 0' }}>
          <Space>
            <Text strong>优先级:</Text>
            <Tag color="volcano">{file.priority}</Tag>
          </Space>
        </div>
      )}

      {file.description && (
        <div style={{ marginBottom: 16 }}>
          <Divider />
          <Title level={4}>
            <InfoCircleOutlined style={{ marginRight: 8 }} />
            描述
          </Title>
          <Paragraph style={{ backgroundColor: '#f5f5f5', padding: 12, borderRadius: 6 }}>
            {file.description}
          </Paragraph>
        </div>
      )}

      {file.tags && file.tags.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>标签</Title>
          <Space wrap>
            {file.tags.map((tag, index) => (
              <Tag key={index} color="processing">
                {tag}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {file.sections && file.sections.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>章节</Title>
          <Space wrap>
            {file.sections.map((section, index) => (
              <Tag key={index} color="default">
                {section}
              </Tag>
            ))}
          </Space>
        </div>
      )}

      {file.references && file.references.length > 0 && (
        <div style={{ marginBottom: 16 }}>
          <Title level={4}>引用</Title>
          <ul style={{ paddingLeft: 20 }}>
            {file.references.map((ref, index) => (
              <li key={index}>
                <Text type="secondary">{ref}</Text>
              </li>
            ))}
          </ul>
        </div>
      )}

      <div style={{ marginTop: 16, padding: 12, backgroundColor: '#fafafa', borderRadius: 6 }}>
        <Text type="secondary" style={{ fontSize: 12 }}>
          <strong>完整路径:</strong> {file.file_path}
        </Text>
      </div>
    </div>
  );

  const renderContent = () => {
    switch (itemType) {
      case 'model':
        return renderModelPreview(selectedItem as ModelInfo);
      case 'command':
        return renderFilePreview(
          selectedItem as FileMetadata, 
          <FileTextOutlined style={{ fontSize: 20, color: '#1890ff' }} />,
          '指令文件'
        );
      case 'rule':
        return renderFilePreview(
          selectedItem as FileMetadata, 
          <BookOutlined style={{ fontSize: 20, color: '#722ed1' }} />,
          '规则文件'
        );
      default:
        return null;
    }
  };

  return (
    <Card 
      title={`${itemType === 'model' ? '模型' : itemType === 'command' ? '指令' : '规则'}详情`}
      style={{ height: '100%' }}
      bodyStyle={{ 
        height: 'calc(100% - 57px)', 
        overflow: 'auto',
        padding: '16px 24px'
      }}
    >
      {renderContent()}
    </Card>
  );
};

export default PreviewPanel;