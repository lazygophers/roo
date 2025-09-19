import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Tag,
  Space,
  Empty,
  Spin,
  message,
  Row,
  Col,
  Statistic,
  Avatar,
  Tooltip,
  Dropdown,
  Typography,
  Badge,
  Divider
} from 'antd';
import {
  PlusOutlined,
  FolderOutlined,
  FileOutlined,
  SettingOutlined,
  SearchOutlined,
  DeleteOutlined,
  EditOutlined,
  InfoCircleOutlined,
  GlobalOutlined,
  GithubOutlined,
  CloudOutlined,
  DatabaseOutlined,
  BookOutlined,
  EyeOutlined,
  ReloadOutlined,
  MoreOutlined,
  ThunderboltOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import './HierarchicalKnowledgeBase.css';
import VectorDatabaseConfigModal from '../components/VectorDatabaseConfig/VectorDatabaseConfigModal';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Option } = Select;

// 类型定义
interface VectorDatabaseConfig {
  type: string;
  config: Record<string, any>;
  embedding_model: string;
}

interface KnowledgeBase {
  id: string;
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  tags: string[];
  vector_db_config?: VectorDatabaseConfig;
  created_at: string;
  updated_at: string;
  folder_count: number;
  file_count: number;
  total_size: number;
}

interface KnowledgeFolder {
  id: string;
  knowledge_base_id: string;
  parent_folder_id?: string;
  name: string;
  description?: string;
  folder_type: 'local' | 'website' | 'github' | 'cloud' | 'virtual';
  path?: string;
  config: Record<string, any>;
  tags: string[];
  icon?: string;
  color?: string;
  created_at: string;
  updated_at: string;
  sub_folder_count: number;
  file_count: number;
  total_size: number;
  status: 'pending' | 'processing' | 'completed' | 'failed';
}

interface CreateKnowledgeBaseRequest {
  name: string;
  description?: string;
  icon?: string;
  color?: string;
  tags: string[];
  vector_db_config?: VectorDatabaseConfig;
}

interface CreateFolderRequest {
  knowledge_base_id: string;
  parent_folder_id?: string;
  name: string;
  description?: string;
  folder_type: 'local' | 'website' | 'github' | 'cloud' | 'virtual';
  path?: string;
  config: Record<string, any>;
  tags: string[];
  icon?: string;
  color?: string;
}

const KnowledgeBase: React.FC = () => {
  const [knowledgeBases, setKnowledgeBases] = useState<KnowledgeBase[]>([]);
  const [selectedKB, setSelectedKB] = useState<KnowledgeBase | null>(null);
  const [folders, setFolders] = useState<KnowledgeFolder[]>([]);
  const [loading, setLoading] = useState(false);
  const [createKBModalVisible, setCreateKBModalVisible] = useState(false);
  const [createFolderModalVisible, setCreateFolderModalVisible] = useState(false);
  const [vectorDbConfigModalVisible, setVectorDbConfigModalVisible] = useState(false);
  const [selectedFolder, setSelectedFolder] = useState<KnowledgeFolder | null>(null);

  const [createKBForm] = Form.useForm();
  const [createFolderForm] = Form.useForm();

  useEffect(() => {
    fetchKnowledgeBases();
  }, []);

  const fetchKnowledgeBases = async () => {
    setLoading(true);
    try {
      const response = await fetch('/api/knowledge-base/knowledge-bases');
      const data = await response.json();
      if (Array.isArray(data)) {
        setKnowledgeBases(data);
      } else {
        setKnowledgeBases([]);
      }
    } catch (error) {
      message.error('获取知识库列表失败');
      console.error('Error fetching knowledge bases:', error);
    } finally {
      setLoading(false);
    }
  };

  const fetchFolders = async (knowledgeBaseId: string) => {
    try {
      const response = await fetch(`/api/knowledge-base/folders?knowledge_base_id=${knowledgeBaseId}`);
      const result = await response.json();
      if (result.success && Array.isArray(result.data)) {
        setFolders(result.data);
      } else {
        setFolders([]);
      }
    } catch (error) {
      message.error('获取文件夹列表失败');
      console.error('Error fetching folders:', error);
    }
  };

  const handleCreateKnowledgeBase = async (values: any) => {
    try {
      const requestData: CreateKnowledgeBaseRequest = {
        name: values.name,
        description: values.description,
        color: values.color,
        tags: values.tags || []
      };

      const response = await fetch('/api/knowledge-base/knowledge-bases', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData),
      });

      if (response.ok) {
        const newKB = await response.json();
        message.success('知识库创建成功');
        setKnowledgeBases(prev => [...prev, newKB]);
        setCreateKBModalVisible(false);
        createKBForm.resetFields();
      } else {
        message.error('创建知识库失败');
      }
    } catch (error) {
      message.error('创建知识库失败');
      console.error('Error creating knowledge base:', error);
    }
  };

  const handleCreateFolder = async (values: CreateFolderRequest) => {
    try {
      const folderData = {
        ...values,
        knowledge_base_id: selectedKB?.id,
        config: values.folder_type === 'github' ? { github_token: values.config?.github_token } : {}
      };

      const response = await fetch('/api/knowledge-base/folders', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(folderData),
      });

      if (response.ok) {
        const newFolder = await response.json();
        message.success('文件夹创建成功');
        setFolders(prev => [...prev, newFolder]);
        setCreateFolderModalVisible(false);
        createFolderForm.resetFields();
      } else {
        message.error('创建文件夹失败');
      }
    } catch (error) {
      message.error('创建文件夹失败');
      console.error('Error creating folder:', error);
    }
  };

  const getFolderTypeIcon = (type: string) => {
    switch (type) {
      case 'local':
        return <FolderOutlined style={{ color: '#1890ff' }} />;
      case 'website':
        return <GlobalOutlined style={{ color: '#52c41a' }} />;
      case 'github':
        return <GithubOutlined style={{ color: '#24292e' }} />;
      case 'cloud':
        return <CloudOutlined style={{ color: '#722ed1' }} />;
      case 'virtual':
        return <DatabaseOutlined style={{ color: '#fa8c16' }} />;
      default:
        return <FolderOutlined />;
    }
  };

  const getFolderTypeText = (type: string) => {
    switch (type) {
      case 'local': return '本地文件夹';
      case 'website': return '网站';
      case 'github': return 'GitHub';
      case 'cloud': return '云存储';
      case 'virtual': return '虚拟文件夹';
      default: return type;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'green';
      case 'processing': return 'blue';
      case 'failed': return 'red';
      case 'pending': return 'orange';
      default: return 'default';
    }
  };

  const getStatusText = (status: string) => {
    switch (status) {
      case 'completed': return '已完成';
      case 'processing': return '处理中';
      case 'failed': return '失败';
      case 'pending': return '待处理';
      default: return status;
    }
  };

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  };

  const renderKnowledgeBaseCard = (kb: KnowledgeBase) => (
    <Card
      key={kb.id}
      className="knowledge-base-card"
      hoverable
      onClick={() => {
        setSelectedKB(kb);
        fetchFolders(kb.id);
      }}
      style={{ borderColor: selectedKB?.id === kb.id ? '#1890ff' : undefined }}
      actions={[
        <Tooltip title="查看详情">
          <EyeOutlined key="view" />
        </Tooltip>,
        <Tooltip title="编辑">
          <EditOutlined key="edit" />
        </Tooltip>,
        <Dropdown menu={{
          items: [
            {
              key: 'delete',
              danger: true,
              label: (
                <span onClick={(e) => {
                  e.stopPropagation();
                  // TODO: 实现删除功能
                }}>
                  <DeleteOutlined /> 删除
                </span>
              )
            }
          ]
        }}>
          <MoreOutlined key="more" onClick={(e) => e.stopPropagation()} />
        </Dropdown>
      ]}
    >
      <Card.Meta
        avatar={
          <Avatar
            style={{ backgroundColor: kb.color || '#1890ff' }}
            icon={<BookOutlined />}
          />
        }
        title={kb.name}
        description={
          <div>
            {kb.tags && kb.tags.length > 0 && (
              <div style={{ marginBottom: '8px' }}>
                <Space size={[4, 4]} wrap>
                  {kb.tags.map(tag => (
                    <Tag key={tag} color="default">{tag}</Tag>
                  ))}
                </Space>
              </div>
            )}
            <Paragraph ellipsis={{ rows: 2 }}>
              {kb.description || '暂无描述'}
            </Paragraph>
            <Divider style={{ margin: '8px 0' }} />
            <Row gutter={16}>
              <Col span={8}>
                <Statistic
                  title="文件夹"
                  value={kb.folder_count}
                  prefix={<FolderOutlined />}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="文件"
                  value={kb.file_count}
                  prefix={<FileOutlined />}
                  valueStyle={{ fontSize: '14px' }}
                />
              </Col>
              <Col span={8}>
                <Statistic
                  title="大小"
                  value={formatFileSize(kb.total_size)}
                  valueStyle={{ fontSize: '12px' }}
                />
              </Col>
            </Row>
          </div>
        }
      />
    </Card>
  );

  const renderFolderCard = (folder: KnowledgeFolder) => (
    <Card
      key={folder.id}
      className="folder-card"
      hoverable
      size="small"
      actions={[
        <Tooltip title="查看内容">
          <EyeOutlined key="view" />
        </Tooltip>,
        <Tooltip title="编辑">
          <EditOutlined key="edit" />
        </Tooltip>,
        <Tooltip title="删除">
          <DeleteOutlined key="delete" />
        </Tooltip>
      ]}
    >
      <Card.Meta
        avatar={getFolderTypeIcon(folder.folder_type)}
        title={
          <Space>
            <span>{folder.name}</span>
            <Badge
              status={getStatusColor(folder.status) as any}
              text={getStatusText(folder.status)}
            />
          </Space>
        }
        description={
          <div>
            <Text type="secondary">{getFolderTypeText(folder.folder_type)}</Text>
            {folder.path && (
              <div>
                <Text code style={{ fontSize: '12px' }}>{folder.path}</Text>
              </div>
            )}
            {folder.tags.length > 0 && (
              <div style={{ marginTop: '4px' }}>
                {folder.tags.map(tag => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </div>
            )}
            <Row gutter={8} style={{ marginTop: '8px' }}>
              <Col span={12}>
                <Text style={{ fontSize: '12px' }}>
                  <FolderOutlined /> {folder.sub_folder_count}
                </Text>
              </Col>
              <Col span={12}>
                <Text style={{ fontSize: '12px' }}>
                  <FileOutlined /> {folder.file_count}
                </Text>
              </Col>
            </Row>
          </div>
        }
      />
    </Card>
  );

  return (
    <div className="hierarchical-knowledge-base-container">
      <div className="hierarchical-knowledge-base-header">
        <Title level={2}>
          <BookOutlined /> 知识库管理
        </Title>
        <Text type="secondary">
          支持多层级组织结构的智能知识库系统，集成本地文件、网站内容、GitHub仓库等多种数据源。
        </Text>
      </div>

      {/* 全局向量数据库配置 */}
      <Card
        title={
          <Space>
            <DatabaseOutlined />
            <span>向量数据库配置</span>
          </Space>
        }
        extra={
          <Button
            type="primary"
            icon={<SettingOutlined />}
            onClick={() => setVectorDbConfigModalVisible(true)}
          >
            配置向量数据库
          </Button>
        }
        style={{ marginBottom: 24 }}
        size="small"
      >
        <Row gutter={16}>
          <Col span={8}>
            <Statistic
              title="数据库类型"
              value="LanceDB"
              prefix={<DatabaseOutlined />}
              valueStyle={{ fontSize: '14px' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="嵌入模型"
              value="all-MiniLM-L6-v2"
              prefix={<ThunderboltOutlined />}
              valueStyle={{ fontSize: '14px' }}
            />
          </Col>
          <Col span={8}>
            <Statistic
              title="状态"
              value="已配置"
              prefix={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
              valueStyle={{ fontSize: '14px', color: '#52c41a' }}
            />
          </Col>
        </Row>
      </Card>

      <Row gutter={24}>
        {/* 左侧：知识库列表 */}
        <Col span={selectedKB ? 10 : 24}>
          <Card
            title="知识库"
            extra={
              <Space>
                <Button
                  type="primary"
                  icon={<PlusOutlined />}
                  onClick={() => setCreateKBModalVisible(true)}
                >
                  创建知识库
                </Button>
                <Button
                  icon={<ReloadOutlined />}
                  onClick={fetchKnowledgeBases}
                  loading={loading}
                >
                  刷新
                </Button>
              </Space>
            }
          >
            {loading ? (
              <div style={{ textAlign: 'center', padding: '40px' }}>
                <Spin size="large" />
              </div>
            ) : knowledgeBases.length === 0 ? (
              <Empty description="暂无知识库，点击上方按钮创建第一个知识库" />
            ) : (
              <div className="knowledge-bases-grid">
                {knowledgeBases.map(renderKnowledgeBaseCard)}
              </div>
            )}
          </Card>
        </Col>

        {/* 右侧：选中知识库的文件夹 */}
        {selectedKB && (
          <Col span={14}>
            <Card
              title={
                <Space>
                  <Avatar
                    size="small"
                    style={{ backgroundColor: selectedKB.color || '#1890ff' }}
                    icon={<BookOutlined />}
                  />
                  {selectedKB.name} - 文件夹
                </Space>
              }
              extra={
                <Space>
                  <Button
                    type="primary"
                    icon={<PlusOutlined />}
                    onClick={() => setCreateFolderModalVisible(true)}
                  >
                    添加文件夹
                  </Button>
                  <Button
                    icon={<ReloadOutlined />}
                    onClick={() => fetchFolders(selectedKB.id)}
                  >
                    刷新
                  </Button>
                </Space>
              }
            >
              {folders.length === 0 ? (
                <Empty description="暂无文件夹，点击上方按钮添加数据源" />
              ) : (
                <Row gutter={[16, 16]}>
                  {folders.map(folder => (
                    <Col span={12} key={folder.id}>
                      {renderFolderCard(folder)}
                    </Col>
                  ))}
                </Row>
              )}
            </Card>
          </Col>
        )}
      </Row>

      {/* 创建知识库模态框 */}
      <Modal
        title="创建知识库"
        open={createKBModalVisible}
        onCancel={() => {
          setCreateKBModalVisible(false);
          createKBForm.resetFields();
        }}
        onOk={() => createKBForm.submit()}
        destroyOnHidden
      >
        <Form
          form={createKBForm}
          layout="vertical"
          onFinish={handleCreateKnowledgeBase}
        >
          <Form.Item
            name="name"
            label="知识库名称"
            rules={[{ required: true, message: '请输入知识库名称' }]}
          >
            <Input placeholder="输入知识库名称" />
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={3} placeholder="输入知识库描述（可选）" />
          </Form.Item>
          <Form.Item name="color" label="主题色">
            <Select placeholder="选择主题色（可选）">
              <Option value="#1890ff">蓝色</Option>
              <Option value="#52c41a">绿色</Option>
              <Option value="#fa8c16">橙色</Option>
              <Option value="#722ed1">紫色</Option>
              <Option value="#eb2f96">粉色</Option>
            </Select>
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Select
              mode="tags"
              placeholder="输入标签（可选）"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 创建文件夹模态框 */}
      <Modal
        title="添加数据源"
        open={createFolderModalVisible}
        onCancel={() => {
          setCreateFolderModalVisible(false);
          createFolderForm.resetFields();
        }}
        onOk={() => createFolderForm.submit()}
        destroyOnHidden
        width={600}
      >
        <Form
          form={createFolderForm}
          layout="vertical"
          onFinish={handleCreateFolder}
        >
          <Form.Item
            name="name"
            label="文件夹名称"
            rules={[{ required: true, message: '请输入文件夹名称' }]}
          >
            <Input placeholder="输入文件夹名称" />
          </Form.Item>
          <Form.Item
            name="folder_type"
            label="数据源类型"
            rules={[{ required: true, message: '请选择数据源类型' }]}
          >
            <Select placeholder="选择数据源类型">
              <Option value="local">
                <FolderOutlined /> 本地文件夹
              </Option>
              <Option value="website">
                <GlobalOutlined /> 网站链接
              </Option>
              <Option value="github">
                <GithubOutlined /> GitHub仓库
              </Option>
              <Option value="cloud">
                <CloudOutlined /> 云存储
              </Option>
              <Option value="virtual">
                <DatabaseOutlined /> 虚拟文件夹
              </Option>
            </Select>
          </Form.Item>
          <Form.Item
            noStyle
            shouldUpdate={(prevValues, currentValues) =>
              prevValues.folder_type !== currentValues.folder_type
            }
          >
            {({ getFieldValue }) => {
              const folderType = getFieldValue('folder_type');
              if (folderType === 'virtual') return null;

              return (
                <Form.Item
                  name="path"
                  label={
                    folderType === 'local' ? '本地路径' :
                    folderType === 'website' ? '网站URL' :
                    folderType === 'github' ? 'GitHub仓库URL' :
                    folderType === 'cloud' ? '云存储路径' : '路径'
                  }
                  rules={[{ required: true, message: '请输入路径' }]}
                >
                  <Input
                    placeholder={
                      folderType === 'local' ? '/path/to/folder' :
                      folderType === 'website' ? 'https://example.com' :
                      folderType === 'github' ? 'https://github.com/user/repo' :
                      folderType === 'cloud' ? 'cloud://path' : '输入路径'
                    }
                  />
                </Form.Item>
              );
            }}
          </Form.Item>
          <Form.Item name="description" label="描述">
            <TextArea rows={2} placeholder="输入描述（可选）" />
          </Form.Item>
          <Form.Item name="tags" label="标签">
            <Select
              mode="tags"
              placeholder="输入标签（可选）"
              style={{ width: '100%' }}
            />
          </Form.Item>
        </Form>
      </Modal>

      {/* 向量数据库配置模态框 */}
      <VectorDatabaseConfigModal
        visible={vectorDbConfigModalVisible}
        onCancel={() => setVectorDbConfigModalVisible(false)}
        onSuccess={() => {
          setVectorDbConfigModalVisible(false);
          // 可以在这里刷新配置状态
        }}
      />
    </div>
  );
};

export default KnowledgeBase;