import React, { useState, useEffect } from 'react';
import {
  Card,
  List,
  Switch,
  Button,
  Typography,
  Space,
  message,
  Alert,
  Spin,
  Tag,
  Descriptions,
  Modal,
  Input,
  Form,
} from 'antd';
import {
  SettingOutlined,
  ReloadOutlined,
  SaveOutlined,
  InfoCircleOutlined,
  EditOutlined,
  ExportOutlined,
} from '@ant-design/icons';
import styles from './ConfigPage.module.css';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

// 类型定义
interface Model {
  id: string;
  name: string;
  description: string;
  enabled: boolean;
  version: string;
  category: 'frontend' | 'backend' | 'database' | 'deployment';
  config: Record<string, any>;
  dependencies?: string[];
  tags?: string[];
}

interface ConfigPageProps {
  className?: string;
}

// 模拟数据
const mockModels: Model[] = [
  {
    id: 'react-frontend',
    name: 'React Frontend',
    description: '基于 React 18 + TypeScript + Vite 的现代前端框架配置',
    enabled: true,
    version: '18.2.0',
    category: 'frontend',
    config: {
      strict: true,
      hotReload: true,
      bundler: 'vite',
    },
    dependencies: ['typescript-config', 'eslint-config'],
    tags: ['React', 'TypeScript', 'Vite'],
  },
  {
    id: 'fastapi-backend',
    name: 'FastAPI Backend',
    description: 'FastAPI + Python 异步后端 API 服务框架',
    enabled: true,
    version: '0.104.1',
    category: 'backend',
    config: {
      cors: true,
      docs: true,
      async: true,
    },
    dependencies: ['python-config'],
    tags: ['FastAPI', 'Python', 'API'],
  },
  {
    id: 'typescript-config',
    name: 'TypeScript Config',
    description: '严格模式的 TypeScript 配置，确保类型安全',
    enabled: true,
    version: '5.2.2',
    category: 'frontend',
    config: {
      strict: true,
      noImplicitAny: true,
      strictNullChecks: true,
    },
    tags: ['TypeScript', '类型检查'],
  },
  {
    id: 'tinydb-storage',
    name: 'TinyDB Storage',
    description: '轻量级 JSON 数据库，适合小型项目数据存储',
    enabled: false,
    version: '4.8.0',
    category: 'database',
    config: {
      indent: 2,
      separators: [',', ':'],
    },
    tags: ['TinyDB', 'JSON', '数据库'],
  },
];

const ConfigPage: React.FC<ConfigPageProps> = ({ className }) => {
  const [models, setModels] = useState<Model[]>([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [selectedModel, setSelectedModel] = useState<Model | null>(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [form] = Form.useForm();

  // 模拟 API 调用
  useEffect(() => {
    const fetchModels = async () => {
      setLoading(true);
      try {
        // 模拟 API 延迟
        await new Promise(resolve => setTimeout(resolve, 1000));
        setModels(mockModels);
      } catch (error) {
        message.error('获取配置失败');
      } finally {
        setLoading(false);
      }
    };

    fetchModels();
  }, []);

  // 切换模型启用状态
  const handleToggleModel = async (modelId: string, enabled: boolean) => {
    try {
      setModels(prevModels =>
        prevModels.map(model => (model.id === modelId ? { ...model, enabled } : model))
      );
      message.success(`${enabled ? '启用' : '禁用'}配置成功`);
    } catch (error) {
      message.error('操作失败');
    }
  };

  // 保存所有配置
  const handleSaveAll = async () => {
    setSaving(true);
    try {
      // 模拟保存操作
      await new Promise(resolve => setTimeout(resolve, 1500));
      message.success('所有配置已保存');
    } catch (error) {
      message.error('保存失败');
    } finally {
      setSaving(false);
    }
  };

  // 重新加载配置
  const handleReload = async () => {
    setLoading(true);
    try {
      await new Promise(resolve => setTimeout(resolve, 800));
      message.success('配置已重新加载');
    } catch (error) {
      message.error('重新加载失败');
    } finally {
      setLoading(false);
    }
  };

  // 显示模型详情
  const handleShowDetails = (model: Model) => {
    setSelectedModel(model);
    form.setFieldsValue({
      name: model.name,
      description: model.description,
      config: JSON.stringify(model.config, null, 2),
    });
    setModalVisible(true);
  };

  // 保存模型详情
  const handleSaveModel = async () => {
    try {
      const values = await form.validateFields();
      const updatedModel = {
        ...selectedModel!,
        name: values.name,
        description: values.description,
        config: JSON.parse(values.config),
      };

      setModels(prevModels =>
        prevModels.map(model => (model.id === selectedModel!.id ? updatedModel : model))
      );

      setModalVisible(false);
      message.success('配置已更新');
    } catch (error) {
      message.error('保存失败，请检查配置格式');
    }
  };

  // 导出配置
  const handleExport = () => {
    const enabledModels = models.filter(model => model.enabled);
    const config = {
      version: '1.0.0',
      timestamp: new Date().toISOString(),
      models: enabledModels,
    };

    const blob = new Blob([JSON.stringify(config, null, 2)], {
      type: 'application/json',
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'roo-config.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    message.success('配置已导出');
  };

  // 获取分类标签颜色
  const getCategoryColor = (category: Model['category']) => {
    const colorMap = {
      frontend: 'blue',
      backend: 'green',
      database: 'orange',
      deployment: 'purple',
    };
    return colorMap[category];
  };

  // 统计信息
  const stats = {
    total: models.length,
    enabled: models.filter(model => model.enabled).length,
    disabled: models.filter(model => !model.enabled).length,
  };

  if (loading) {
    return (
      <div className={`${styles.container} ${className || ''}`}>
        <div className={styles.loadingContainer}>
          <Spin size='large' />
          <Text className={styles.loadingText}>加载配置中...</Text>
        </div>
      </div>
    );
  }

  return (
    <div className={`${styles.container} ${className || ''}`}>
      <div className={styles.header}>
        <div className={styles.titleSection}>
          <Title level={2} className={styles.title}>
            <SettingOutlined className={styles.titleIcon} />
            配置管理
          </Title>
          <Paragraph className={styles.subtitle}>
            管理 Roo Code 规则配置，自定义选择和组合各种开发工具和框架配置
          </Paragraph>
        </div>

        <Space size='middle' className={styles.actions}>
          <Button icon={<ReloadOutlined />} onClick={handleReload} disabled={loading}>
            重新加载
          </Button>
          <Button icon={<ExportOutlined />} onClick={handleExport} disabled={stats.enabled === 0}>
            导出配置
          </Button>
          <Button type='primary' icon={<SaveOutlined />} onClick={handleSaveAll} loading={saving}>
            保存所有配置
          </Button>
        </Space>
      </div>

      <div className={styles.statsContainer}>
        <Card className={styles.statsCard}>
          <Descriptions column={3} size='small'>
            <Descriptions.Item label='总配置数'>{stats.total}</Descriptions.Item>
            <Descriptions.Item label='已启用'>{stats.enabled}</Descriptions.Item>
            <Descriptions.Item label='已禁用'>{stats.disabled}</Descriptions.Item>
          </Descriptions>
        </Card>
      </div>

      {stats.enabled === 0 && (
        <Alert
          message='未启用任何配置'
          description='请启用至少一个配置模块以确保系统正常运行'
          type='warning'
          showIcon
          className={styles.alert}
        />
      )}

      <Card className={styles.modelsCard}>
        <List
          dataSource={models}
          renderItem={model => (
            <List.Item
              key={model.id}
              className={styles.modelItem}
              actions={[
                <Button
                  type='text'
                  icon={<InfoCircleOutlined />}
                  onClick={() => handleShowDetails(model)}
                >
                  详情
                </Button>,
                <Button
                  type='text'
                  icon={<EditOutlined />}
                  onClick={() => handleShowDetails(model)}
                >
                  编辑
                </Button>,
                <Switch
                  checked={model.enabled}
                  onChange={enabled => handleToggleModel(model.id, enabled)}
                  loading={saving}
                />,
              ]}
            >
              <List.Item.Meta
                title={
                  <div className={styles.modelTitle}>
                    <Text strong>{model.name}</Text>
                    <Text type='secondary' className={styles.version}>
                      v{model.version}
                    </Text>
                    <Tag color={getCategoryColor(model.category)}>{model.category}</Tag>
                  </div>
                }
                description={
                  <div className={styles.modelDescription}>
                    <Paragraph ellipsis={{ rows: 2 }}>{model.description}</Paragraph>
                    {model.tags && (
                      <div className={styles.tags}>
                        {model.tags.map(tag => (
                          <Tag key={tag} size='small'>
                            {tag}
                          </Tag>
                        ))}
                      </div>
                    )}
                    {model.dependencies && model.dependencies.length > 0 && (
                      <div className={styles.dependencies}>
                        <Text type='secondary'>依赖: </Text>
                        {model.dependencies.map(dep => (
                          <Tag key={dep} size='small' color='default'>
                            {dep}
                          </Tag>
                        ))}
                      </div>
                    )}
                  </div>
                }
              />
            </List.Item>
          )}
        />
      </Card>

      {/* 模型详情编辑弹窗 */}
      <Modal
        title={`编辑配置 - ${selectedModel?.name}`}
        open={modalVisible}
        onOk={handleSaveModel}
        onCancel={() => setModalVisible(false)}
        width={800}
        okText='保存'
        cancelText='取消'
      >
        <Form form={form} layout='vertical'>
          <Form.Item
            name='name'
            label='配置名称'
            rules={[{ required: true, message: '请输入配置名称' }]}
          >
            <Input placeholder='输入配置名称' />
          </Form.Item>

          <Form.Item
            name='description'
            label='配置描述'
            rules={[{ required: true, message: '请输入配置描述' }]}
          >
            <TextArea rows={3} placeholder='输入配置描述' />
          </Form.Item>

          <Form.Item
            name='config'
            label='配置内容 (JSON)'
            rules={[
              { required: true, message: '请输入配置内容' },
              {
                validator: (_, value) => {
                  try {
                    JSON.parse(value);
                    return Promise.resolve();
                  } catch {
                    return Promise.reject(new Error('请输入有效的 JSON 格式'));
                  }
                },
              },
            ]}
          >
            <TextArea
              rows={10}
              placeholder='输入 JSON 格式的配置内容'
              className={styles.configTextArea}
            />
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
};

export default ConfigPage;
