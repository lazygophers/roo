/**
 * 向量数据库配置模态框
 * 支持配置不同的向量数据库类型和嵌入模型
 */

import React, { useState, useEffect } from 'react';
import { Alert, Space, Tooltip, Typography } from 'antd';
import {
  ModalForm,
  ProCard,
  ProFormDigit,
  ProFormSelect,
  ProFormSwitch,
  ProFormText,
  ProFormDependency
} from '@ant-design/pro-components';
import {
  DatabaseOutlined,
  InfoCircleOutlined,
  SettingOutlined,
  ThunderboltOutlined
} from '@ant-design/icons';
import { apiClient, VectorDatabaseInfo } from '../../api';
import { useTheme } from '../../contexts/ThemeContext';

const { Text, Paragraph } = Typography;

// 向量数据库配置接口
export interface VectorDatabaseConfig {
  // 基础配置
  database_type: string;

  // 嵌入服务配置
  embedding_provider: string;
  embedding_model: string;
  custom_embedding_model?: string;

  // LanceDB 配置
  lancedb_path?: string;
  lancedb_table_name?: string;

  // ChromaDB 配置
  chroma_host?: string;
  chroma_port?: number;
  chroma_collection_name?: string;
  chroma_persist_directory?: string;

  // Qdrant 配置
  qdrant_host?: string;
  qdrant_port?: number;
  qdrant_collection_name?: string;
  qdrant_api_key?: string;
  qdrant_prefer_grpc?: boolean;

  // Milvus Lite 配置
  milvus_host?: string;
  milvus_port?: number;
  milvus_collection_name?: string;
  milvus_uri?: string;
  milvus_user?: string;
  milvus_password?: string;

  // FAISS 配置
  faiss_index_path?: string;
  faiss_index_type?: string;

  // HNSWLIB 配置
  hnswlib_space?: string;
  hnswlib_max_elements?: number;
  hnswlib_ef_construction?: number;
  hnswlib_m?: number;

  // VectorDB 配置
  vectordb_url?: string;
  vectordb_api_key?: string;

  // Redis Vector 配置
  redis_host?: string;
  redis_port?: number;
  redis_password?: string;
  redis_db?: number;
  redis_index_name?: string;

  // Ollama 配置
  ollama_host?: string;
  ollama_port?: number;

  // OpenAI 配置
  openai_api_key?: string;
  openai_base_url?: string;

  // Gemini 配置
  gemini_api_key?: string;

  // HuggingFace 配置
  huggingface_api_key?: string;

  // 通用配置
  dimension?: number;
  distance_metric?: string;
  batch_size?: number;
  max_retries?: number;
}

interface VectorDatabaseConfigModalProps {
  visible: boolean;
  onCancel: () => void;
  onSuccess?: () => void;
}

const VectorDatabaseConfigModal: React.FC<VectorDatabaseConfigModalProps> = ({
  visible,
  onCancel,
  onSuccess
}) => {
  const { currentTheme } = useTheme();
  const [loading, setLoading] = useState(false);
  const [databaseType, setDatabaseType] = useState<string>('lancedb');
  const [embeddingProvider, setEmbeddingProvider] = useState<string>('local');
  const [availableDatabases, setAvailableDatabases] = useState<VectorDatabaseInfo[]>([]);
  const [loadingDatabases, setLoadingDatabases] = useState(false);

  // 加载支持的向量数据库列表
  const loadSupportedDatabases = async () => {
    try {
      setLoadingDatabases(true);
      const response = await apiClient.getSupportedVectorDatabases();
      if (response.success && response.data) {
        setAvailableDatabases(response.data);
      }
    } catch (error) {
      console.error('Failed to load supported vector databases:', error);
      // 使用默认数据库列表作为fallback
      setAvailableDatabases([
        {
          type: 'lancedb',
          name: 'LanceDB',
          description: '高性能向量数据库，适合本地部署',
          default_config: { type: 'lancedb', path: './data/lancedb' }
        }
      ]);
    } finally {
      setLoadingDatabases(false);
    }
  };

  // 组件加载时获取数据库列表
  useEffect(() => {
    if (visible) {
      loadSupportedDatabases();
    }
  }, [visible]);

  // 根据数据库信息生成选项
  const generateDatabaseOptions = () => {
    return availableDatabases.map(db => ({
      label: (
        <Space>
          {db.type === 'lancedb' ? <ThunderboltOutlined /> : <DatabaseOutlined />}
          <span>{db.name}</span>
          <Text type="secondary">（{db.description}）</Text>
        </Space>
      ),
      value: db.type,
    }));
  };

  // 请求初始配置数据
  const handleRequest = async () => {
    try {
      const response = await apiClient.getCategoryConfig('vector-database');
      if (response.success && response.data) {
        return response.data;
      }
      // 返回默认配置
      return {
        database_type: 'lancedb',
        embedding_provider: 'local',
        embedding_model: 'all-MiniLM-L6-v2',
        lancedb_path: './data/vector_db',
        lancedb_table_name: 'embeddings',
        ollama_host: 'localhost',
        ollama_port: 11434,
        dimension: 384,
        distance_metric: 'cosine',
        batch_size: 100,
        max_retries: 3
      };
    } catch (error) {
      console.error('Failed to load vector database config:', error);
      throw error;
    }
  };

  // 提交配置
  const handleSubmit = async (values: VectorDatabaseConfig) => {
    setLoading(true);
    try {
      // 处理自定义模型逻辑
      const processedValues = { ...values };

      if (values.embedding_model === '__custom__' && values.custom_embedding_model) {
        // 如果选择了自定义模型，使用自定义模型名称
        processedValues.embedding_model = values.custom_embedding_model;
        delete processedValues.custom_embedding_model;
      } else if (values.embedding_model !== '__custom__') {
        // 如果选择了预设模型，清除自定义模型字段
        delete processedValues.custom_embedding_model;
      }

      const response = await apiClient.updateCategoryConfigs('vector-database', processedValues);
      if (response.success) {
        onSuccess?.();
        return true;
      } else {
        throw new Error(response.message || '配置保存失败');
      }
    } catch (error) {
      console.error('Failed to save vector database config:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  // 获取自定义模型的占位符文本
  const getCustomModelPlaceholder = (provider: string) => {
    switch (provider) {
      case 'local':
        return '例如: custom-model-name';
      case 'ollama':
        return '例如: llama2:7b-chat 或 mistral:latest';
      case 'openai':
        return '例如: text-embedding-ada-002';
      case 'gemini':
        return '例如: embedding-001';
      case 'huggingface':
        return '例如: sentence-transformers/your-model';
      default:
        return '输入模型名称';
    }
  };

  // 获取模型名称验证正则表达式
  const getModelNamePattern = (provider: string) => {
    switch (provider) {
      case 'ollama':
        return /^[a-zA-Z0-9_-]+(?::[a-zA-Z0-9_.-]+)?$/;
      case 'openai':
        return /^text-embedding-[a-zA-Z0-9-]+$/;
      case 'gemini':
        return /^[a-zA-Z0-9_-]+$/;
      case 'huggingface':
        return /^[a-zA-Z0-9_.-]+\/[a-zA-Z0-9_.-]+$/;
      default:
        return /^[a-zA-Z0-9_.-]+$/;
    }
  };

  // 获取模型名称验证错误消息
  const getModelNamePatternMessage = (provider: string) => {
    switch (provider) {
      case 'ollama':
        return '模型名称格式：model-name 或 model-name:tag';
      case 'openai':
        return '模型名称必须以 text-embedding- 开头';
      case 'gemini':
        return '请输入有效的 Gemini 模型名称';
      case 'huggingface':
        return '模型名称格式：username/model-name';
      default:
        return '请输入有效的模型名称';
    }
  };

  // 获取嵌入模型选项
  const getEmbeddingModelOptions = (provider: string) => {
    switch (provider) {
      case 'local':
        return [
          { label: 'all-MiniLM-L6-v2 (轻量级，384维)', value: 'all-MiniLM-L6-v2' },
          { label: 'all-mpnet-base-v2 (高质量，768维)', value: 'all-mpnet-base-v2' },
          { label: 'paraphrase-MiniLM-L6-v2 (释义专用，384维)', value: 'paraphrase-MiniLM-L6-v2' },
          { label: 'multilingual-e5-base (多语言支持，768维)', value: 'multilingual-e5-base' },
        ];
      case 'ollama':
        return [
          { label: 'nomic-embed-text (通用文本)', value: 'nomic-embed-text' },
          { label: 'mxbai-embed-large (高质量)', value: 'mxbai-embed-large' },
          { label: 'all-minilm (轻量级)', value: 'all-minilm' },
          { label: 'snowflake-arctic-embed (多语言)', value: 'snowflake-arctic-embed' },
        ];
      case 'openai':
        return [
          { label: 'text-embedding-ada-002 (1536维)', value: 'text-embedding-ada-002' },
          { label: 'text-embedding-3-small (1536维)', value: 'text-embedding-3-small' },
          { label: 'text-embedding-3-large (3072维)', value: 'text-embedding-3-large' },
        ];
      case 'gemini':
        return [
          { label: 'embedding-001 (768维)', value: 'embedding-001' },
          { label: 'text-embedding-004 (768维)', value: 'text-embedding-004' },
        ];
      case 'huggingface':
        return [
          { label: 'sentence-transformers/all-MiniLM-L6-v2', value: 'sentence-transformers/all-MiniLM-L6-v2' },
          { label: 'sentence-transformers/all-mpnet-base-v2', value: 'sentence-transformers/all-mpnet-base-v2' },
          { label: 'intfloat/e5-large-v2', value: 'intfloat/e5-large-v2' },
          { label: 'BAAI/bge-large-en-v1.5', value: 'BAAI/bge-large-en-v1.5' },
        ];
      default:
        return [];
    }
  };

  // 渲染嵌入服务特定配置
  const renderEmbeddingProviderConfig = (provider: string) => {
    switch (provider) {
      case 'local':
        return (
          <ProCard title="本地嵌入模型配置" collapsible>
            <Alert
              message="本地模式说明"
              description={
                <div>
                  <p>使用项目内置的嵌入模型，无需外部服务，数据安全性更高。</p>
                  <p><strong>支持的功能：</strong></p>
                  <ul style={{ margin: 0, paddingLeft: 20 }}>
                    <li>内置多种预训练模型</li>
                    <li>支持自定义模型路径</li>
                    <li>完全离线运行，保护隐私</li>
                    <li>自动管理模型下载和缓存</li>
                  </ul>
                </div>
              }
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
          </ProCard>
        );

      case 'ollama':
        return (
          <ProCard title="Ollama 配置" collapsible>
            <ProFormText
              name="ollama_host"
              label="Ollama 主机"
              placeholder="例如: localhost"
              tooltip="Ollama 服务器地址"
              rules={[{ required: true, message: '请输入 Ollama 主机地址' }]}
            />
            <ProFormDigit
              name="ollama_port"
              label="端口号"
              placeholder="11434"
              tooltip="Ollama 服务器端口"
              min={1}
              max={65535}
              rules={[{ required: true, message: '请输入端口号' }]}
            />
          </ProCard>
        );

      case 'openai':
        return (
          <ProCard title="OpenAI 配置" collapsible>
            <ProFormText.Password
              name="openai_api_key"
              label="API 密钥"
              placeholder="sk-..."
              tooltip="OpenAI API 密钥"
              rules={[{ required: true, message: '请输入 OpenAI API 密钥' }]}
            />
            <ProFormText
              name="openai_base_url"
              label="API 基础URL"
              placeholder="https://api.openai.com/v1"
              tooltip="OpenAI API 基础URL，可用于自定义代理"
            />
          </ProCard>
        );

      case 'gemini':
        return (
          <ProCard title="Google Gemini 配置" collapsible>
            <ProFormText.Password
              name="gemini_api_key"
              label="API 密钥"
              placeholder="输入 Gemini API 密钥"
              tooltip="Google Gemini API 密钥"
              rules={[{ required: true, message: '请输入 Gemini API 密钥' }]}
            />
          </ProCard>
        );

      case 'huggingface':
        return (
          <ProCard title="HuggingFace 配置" collapsible>
            <ProFormText.Password
              name="huggingface_api_key"
              label="API 密钥"
              placeholder="hf_..."
              tooltip="HuggingFace API 密钥"
              rules={[{ required: true, message: '请输入 HuggingFace API 密钥' }]}
            />
          </ProCard>
        );

      default:
        return null;
    }
  };

  // 渲染数据库特定配置
  const renderDatabaseSpecificConfig = (dbType: string) => {
    switch (dbType) {
      case 'lancedb':
        return (
          <ProCard title="LanceDB 配置" collapsible>
            <ProFormText
              name="lancedb_path"
              label="数据库路径"
              placeholder="例如: ./data/vector_db"
              tooltip="LanceDB 数据库文件存储路径"
              rules={[{ required: true, message: '请输入数据库路径' }]}
            />
            <ProFormText
              name="lancedb_table_name"
              label="表名称"
              placeholder="例如: embeddings"
              tooltip="存储向量的表名称"
              rules={[{ required: true, message: '请输入表名称' }]}
            />
          </ProCard>
        );

      case 'chroma':
        return (
          <ProCard title="ChromaDB 配置" collapsible>
            <ProFormText
              name="chroma_host"
              label="主机地址"
              placeholder="例如: localhost"
              tooltip="ChromaDB 服务器地址"
              rules={[{ required: true, message: '请输入主机地址' }]}
            />
            <ProFormDigit
              name="chroma_port"
              label="端口号"
              placeholder="8000"
              tooltip="ChromaDB 服务器端口"
              min={1}
              max={65535}
              rules={[{ required: true, message: '请输入端口号' }]}
            />
            <ProFormText
              name="chroma_collection_name"
              label="集合名称"
              placeholder="例如: knowledge_base"
              tooltip="ChromaDB 集合名称"
              rules={[{ required: true, message: '请输入集合名称' }]}
            />
            <ProFormText
              name="chroma_persist_directory"
              label="持久化目录"
              placeholder="例如: ./chroma_db"
              tooltip="ChromaDB 持久化存储目录（可选）"
            />
          </ProCard>
        );

      case 'qdrant':
        return (
          <ProCard title="Qdrant 配置" collapsible>
            <ProFormText
              name="qdrant_host"
              label="主机地址"
              placeholder="例如: localhost"
              tooltip="Qdrant 服务器地址"
              rules={[{ required: true, message: '请输入主机地址' }]}
            />
            <ProFormDigit
              name="qdrant_port"
              label="端口号"
              placeholder="6333"
              tooltip="Qdrant 服务器端口"
              min={1}
              max={65535}
              rules={[{ required: true, message: '请输入端口号' }]}
            />
            <ProFormText
              name="qdrant_collection_name"
              label="集合名称"
              placeholder="例如: knowledge_base"
              tooltip="Qdrant 集合名称"
              rules={[{ required: true, message: '请输入集合名称' }]}
            />
            <ProFormText
              name="qdrant_api_key"
              label="API 密钥"
              placeholder="可选，用于认证"
              tooltip="Qdrant API 密钥（可选）"
            />
            <ProFormSwitch
              name="qdrant_prefer_grpc"
              label="优先使用 gRPC"
              tooltip="是否优先使用 gRPC 协议连接 Qdrant"
              checkedChildren="开启"
              unCheckedChildren="关闭"
            />
          </ProCard>
        );

      case 'milvus':
        return (
          <ProCard title="Milvus Lite 配置" collapsible>
            <ProFormText
              name="milvus_uri"
              label="连接 URI"
              placeholder="例如: ./milvus_lite.db 或 http://localhost:19530"
              tooltip="Milvus Lite 数据库文件路径或服务器地址"
              rules={[{ required: true, message: '请输入连接 URI' }]}
            />
            <ProFormText
              name="milvus_collection_name"
              label="集合名称"
              placeholder="例如: knowledge_base"
              tooltip="Milvus 集合名称"
              rules={[{ required: true, message: '请输入集合名称' }]}
            />
            <ProFormText
              name="milvus_user"
              label="用户名"
              placeholder="可选，用于认证"
              tooltip="Milvus 用户名（可选）"
            />
            <ProFormText.Password
              name="milvus_password"
              label="密码"
              placeholder="可选，用于认证"
              tooltip="Milvus 密码（可选）"
            />
          </ProCard>
        );

      case 'faiss':
        return (
          <ProCard title="FAISS 配置" collapsible>
            <ProFormText
              name="faiss_index_path"
              label="索引文件路径"
              placeholder="例如: ./faiss_index.bin"
              tooltip="FAISS 索引文件存储路径"
              rules={[{ required: true, message: '请输入索引文件路径' }]}
            />
            <ProFormSelect
              name="faiss_index_type"
              label="索引类型"
              placeholder="请选择索引类型"
              tooltip="FAISS 索引类型"
              options={[
                { label: 'Flat (精确搜索)', value: 'Flat' },
                { label: 'IVFFlat (倒排文件)', value: 'IVFFlat' },
                { label: 'HNSW (层次化小世界)', value: 'HNSW' },
                { label: 'LSH (局部敏感哈希)', value: 'LSH' },
              ]}
              rules={[{ required: true, message: '请选择索引类型' }]}
            />
          </ProCard>
        );

      case 'hnswlib':
        return (
          <ProCard title="HNSWLIB 配置" collapsible>
            <ProFormSelect
              name="hnswlib_space"
              label="距离空间"
              placeholder="请选择距离空间"
              tooltip="HNSWLIB 距离度量空间"
              options={[
                { label: 'l2 (欧几里得距离)', value: 'l2' },
                { label: 'ip (内积)', value: 'ip' },
                { label: 'cosine (余弦相似度)', value: 'cosine' },
              ]}
              rules={[{ required: true, message: '请选择距离空间' }]}
            />
            <ProFormDigit
              name="hnswlib_max_elements"
              label="最大元素数量"
              placeholder="1000000"
              tooltip="HNSWLIB 索引中的最大元素数量"
              min={1}
              rules={[{ required: true, message: '请输入最大元素数量' }]}
            />
            <ProFormDigit
              name="hnswlib_ef_construction"
              label="构建参数 ef"
              placeholder="200"
              tooltip="HNSWLIB 索引构建时的 ef 参数"
              min={1}
            />
            <ProFormDigit
              name="hnswlib_m"
              label="连接数 M"
              placeholder="16"
              tooltip="HNSWLIB 每个节点的最大连接数"
              min={1}
            />
          </ProCard>
        );

      case 'vectordb':
        return (
          <ProCard title="VectorDB 配置" collapsible>
            <ProFormText
              name="vectordb_url"
              label="服务器 URL"
              placeholder="例如: https://api.vectordb.com"
              tooltip="VectorDB 服务器地址"
              rules={[{ required: true, message: '请输入服务器 URL' }]}
            />
            <ProFormText.Password
              name="vectordb_api_key"
              label="API 密钥"
              placeholder="输入 VectorDB API 密钥"
              tooltip="VectorDB API 密钥"
              rules={[{ required: true, message: '请输入 API 密钥' }]}
            />
          </ProCard>
        );

      case 'redis':
        return (
          <ProCard title="Redis Vector 配置" collapsible>
            <ProFormText
              name="redis_host"
              label="主机地址"
              placeholder="例如: localhost"
              tooltip="Redis 服务器地址"
              rules={[{ required: true, message: '请输入主机地址' }]}
            />
            <ProFormDigit
              name="redis_port"
              label="端口号"
              placeholder="6379"
              tooltip="Redis 服务器端口"
              min={1}
              max={65535}
              rules={[{ required: true, message: '请输入端口号' }]}
            />
            <ProFormText.Password
              name="redis_password"
              label="密码"
              placeholder="可选，Redis 认证密码"
              tooltip="Redis 密码（可选）"
            />
            <ProFormDigit
              name="redis_db"
              label="数据库编号"
              placeholder="0"
              tooltip="Redis 数据库编号"
              min={0}
              max={15}
            />
            <ProFormText
              name="redis_index_name"
              label="索引名称"
              placeholder="例如: vector_index"
              tooltip="Redis 向量索引名称"
              rules={[{ required: true, message: '请输入索引名称' }]}
            />
          </ProCard>
        );

      default:
        return null;
    }
  };

  return (
    <ModalForm<VectorDatabaseConfig>
      title={
        <Space>
          <DatabaseOutlined style={{ color: currentTheme.token?.colorPrimary }} />
          <span>向量数据库配置</span>
        </Space>
      }
      open={visible}
      onFinish={handleSubmit}
      onOpenChange={(open) => {
        if (!open) {
          onCancel();
        }
      }}
      request={handleRequest}
      loading={loading}
      width={800}
      layout="horizontal"
      labelCol={{ span: 6 }}
      wrapperCol={{ span: 18 }}
      submitter={{
        searchConfig: {
          submitText: '保存配置',
          resetText: '取消',
        },
      }}
    >
      <Alert
        message="向量数据库配置"
        description="配置用于存储和检索文档向量的数据库。不同数据库类型适用于不同的使用场景。"
        type="info"
        icon={<InfoCircleOutlined />}
        style={{ marginBottom: 24 }}
      />

      {/* 基础配置 */}
      <ProCard title="基础配置" collapsible>
        <ProFormSelect
          name="database_type"
          label="数据库类型"
          tooltip="选择向量数据库类型"
          placeholder="请选择数据库类型"
          options={generateDatabaseOptions()}
          rules={[{ required: true, message: '请选择数据库类型' }]}
          fieldProps={{
            loading: loadingDatabases,
            onChange: (value: string) => setDatabaseType(value),
          }}
        />

        <ProFormSelect
          name="embedding_provider"
          label="嵌入服务提供商"
          tooltip="选择嵌入服务提供商"
          placeholder="请选择嵌入服务提供商"
          options={[
            {
              label: (
                <Space>
                  <DatabaseOutlined />
                  <span>本地模式</span>
                  <Text type="secondary">（项目内置，无需外部服务）</Text>
                </Space>
              ),
              value: 'local',
            },
            {
              label: (
                <Space>
                  <ThunderboltOutlined />
                  <span>Ollama</span>
                  <Text type="secondary">（本地 LLM 服务）</Text>
                </Space>
              ),
              value: 'ollama',
            },
            {
              label: (
                <Space>
                  <InfoCircleOutlined />
                  <span>OpenAI</span>
                  <Text type="secondary">（商业 API 服务）</Text>
                </Space>
              ),
              value: 'openai',
            },
            {
              label: (
                <Space>
                  <InfoCircleOutlined />
                  <span>Google Gemini</span>
                  <Text type="secondary">（谷歌 AI 服务）</Text>
                </Space>
              ),
              value: 'gemini',
            },
            {
              label: (
                <Space>
                  <InfoCircleOutlined />
                  <span>HuggingFace</span>
                  <Text type="secondary">（开源模型平台）</Text>
                </Space>
              ),
              value: 'huggingface',
            },
          ]}
          rules={[{ required: true, message: '请选择嵌入服务提供商' }]}
          fieldProps={{
            onChange: (value: string) => setEmbeddingProvider(value),
          }}
        />

        {/* 动态模型选择 */}
        <ProFormSelect
          name="embedding_model"
          label="嵌入模型"
          tooltip="选择文本向量化模型，或选择'自定义模型'输入模型名称"
          placeholder="请选择嵌入模型"
          options={[
            ...getEmbeddingModelOptions(embeddingProvider),
            ...(embeddingProvider !== 'local' ? [{ label: '自定义模型...', value: '__custom__' }] : [])
          ]}
          rules={[{ required: true, message: '请选择嵌入模型' }]}
        />

        {/* 自定义模型输入 - 仅非本地模式显示 */}
        {embeddingProvider !== 'local' && (
          <ProFormDependency name={['embedding_model']}>
            {({ embedding_model }) => {
              if (embedding_model === '__custom__') {
                return (
                  <ProFormText
                    name="custom_embedding_model"
                    label="自定义模型名称"
                    tooltip="输入自定义的嵌入模型名称"
                    placeholder={getCustomModelPlaceholder(embeddingProvider)}
                    rules={[
                      { required: true, message: '请输入自定义模型名称' },
                      {
                        pattern: getModelNamePattern(embeddingProvider),
                        message: getModelNamePatternMessage(embeddingProvider)
                      }
                    ]}
                  />
                );
              }
              return null;
            }}
          </ProFormDependency>
        )}
      </ProCard>

      {/* 嵌入服务特定配置 */}
      {renderEmbeddingProviderConfig(embeddingProvider)}

      {/* 数据库特定配置 */}
      {renderDatabaseSpecificConfig(databaseType)}

      {/* 性能配置 */}
      <ProCard title="性能配置" collapsible>
        <ProFormDigit
          name="dimension"
          label="向量维度"
          placeholder="384"
          tooltip="向量的维度，需要与嵌入模型匹配"
          min={1}
          max={4096}
          rules={[{ required: true, message: '请输入向量维度' }]}
        />

        <ProFormSelect
          name="distance_metric"
          label="距离度量"
          tooltip="向量相似度计算方法"
          placeholder="请选择距离度量"
          options={[
            { label: '余弦相似度 (Cosine)', value: 'cosine' },
            { label: '欧几里得距离 (Euclidean)', value: 'euclidean' },
            { label: '点积 (Dot Product)', value: 'dot_product' },
          ]}
          rules={[{ required: true, message: '请选择距离度量' }]}
        />

        <ProFormDigit
          name="batch_size"
          label="批处理大小"
          placeholder="100"
          tooltip="批量处理向量的数量"
          min={1}
          max={1000}
          rules={[{ required: true, message: '请输入批处理大小' }]}
        />

        <ProFormDigit
          name="max_retries"
          label="最大重试次数"
          placeholder="3"
          tooltip="操作失败时的最大重试次数"
          min={0}
          max={10}
          rules={[{ required: true, message: '请输入最大重试次数' }]}
        />
      </ProCard>
    </ModalForm>
  );
};

export default VectorDatabaseConfigModal;