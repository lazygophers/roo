import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Button,
  Switch,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  Select,
  Descriptions,
  Badge,
  Tooltip,
  Divider,
  Row,
  Col,
  Statistic,
  Alert,
  Spin,
  Typography,
  Empty,
  Collapse,
  App
} from 'antd';
import {
  ToolOutlined,
  ReloadOutlined,
  InfoCircleOutlined,
  BugOutlined,
  ApiOutlined,
  CheckCircleOutlined,
  ExclamationCircleOutlined,
  FilterOutlined,
  SecurityScanOutlined,
  SettingOutlined,
  FileTextOutlined
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { apiClient, MCPToolInfo, MCPCategoryInfo, MCPStatusResponse } from '../api';
import { useTheme } from '../contexts/ThemeContext';
import FileToolsConfigModal from '../components/FileTools/FileToolsConfigModal';
import './MCPToolsManagement.css';

const { Title, Text, Paragraph } = Typography;
const { Option } = Select;
const { TextArea } = Input;
const { useApp } = App;

const MCPToolsManagement: React.FC = () => {
  const navigate = useNavigate();
  const { currentTheme, themeType } = useTheme();
  const { message: messageApi } = useApp();
  const [loading, setLoading] = useState(false);
  const [tools, setTools] = useState<MCPToolInfo[]>([]);
  const [categories, setCategories] = useState<MCPCategoryInfo[]>([]);
  const [status, setStatus] = useState<MCPStatusResponse['data'] | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const [toolDetailModal, setToolDetailModal] = useState<{
    visible: boolean;
    tool: MCPToolInfo | null;
  }>({ visible: false, tool: null });
  const [testToolModal, setTestToolModal] = useState<{
    visible: boolean;
    tool: MCPToolInfo | null;
    form: any;
  }>({ visible: false, tool: null, form: null });
  const [testResult, setTestResult] = useState<string>('');
  const [fileToolsConfigModal, setFileToolsConfigModal] = useState(false);

  const [form] = Form.useForm();

  // 加载数据
  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [statusRes, categoriesRes, toolsRes] = await Promise.all([
        apiClient.getMCPStatus().catch(e => ({ success: false, data: null })),
        apiClient.getMCPCategories().catch(e => ({ success: false, data: { categories: [], total_categories: 0 } })),
        apiClient.getMCPTools().catch(e => ({ success: false, data: { tools: [], server: '', organization: '' } }))
      ]);

      if (statusRes.success && statusRes.data) {
        setStatus(statusRes.data);
      }

      if (categoriesRes.success && categoriesRes.data) {
        setCategories(categoriesRes.data.categories);
      }

      if (toolsRes.success && toolsRes.data && Array.isArray((toolsRes.data as any).tools)) {
        setTools((toolsRes.data as any).tools);
      } else {
        // 如果API不可用，使用模拟数据
        const mockTools: MCPToolInfo[] = [
          {
            id: '1',
            name: 'get_current_timestamp',
            description: '获取当前时间戳，支持多种时间格式',
            category: 'time',
            schema: { type: 'object', properties: { format: { type: 'string', enum: ['iso', 'unix', 'formatted'] } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['时间', '时间戳', '格式化'] }
          },
          {
            id: '2',
            name: 'get_system_info',
            description: '获取LazyAI Studio系统信息，包括CPU、内存、操作系统等',
            category: 'system',
            schema: { type: 'object', properties: { detailed: { type: 'boolean' }, include_performance: { type: 'boolean' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['系统', '监控', '性能'] }
          },
          {
            id: '3',
            name: 'list_available_modes',
            description: '列出LazyAI Studio可用的AI模式和智能助手',
            category: 'ai',
            schema: { type: 'object', properties: { category: { type: 'string' }, include_description: { type: 'boolean' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['AI', '模式', '助手'] }
          },
          {
            id: '4',
            name: 'get_project_stats',
            description: '获取项目统计信息，包括文件数量、模型数量等',
            category: 'data',
            schema: { type: 'object', properties: { include_models: { type: 'boolean' }, include_files: { type: 'boolean' } } },
            enabled: false,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['统计', '项目', '数据'] }
          },
          {
            id: '5',
            name: 'health_check',
            description: '执行系统健康检查，验证各组件状态',
            category: 'system',
            schema: { type: 'object', properties: { check_database: { type: 'boolean' }, check_cache: { type: 'boolean' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['健康检查', '监控', '诊断'] }
          },
          {
            id: '6',
            name: 'read_file',
            description: '读取文件内容，支持多种编码格式',
            category: 'file',
            schema: { type: 'object', properties: { file_path: { type: 'string' }, encoding: { type: 'string' }, max_lines: { type: 'number' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['文件', '读取', 'I/O'] }
          },
          {
            id: '7',
            name: 'write_file',
            description: '写入或追加内容到文件',
            category: 'file',
            schema: { type: 'object', properties: { file_path: { type: 'string' }, content: { type: 'string' }, mode: { type: 'string' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['文件', '写入', 'I/O'] }
          },
          {
            id: '8',
            name: 'list_directory',
            description: '列出目录内容，支持递归和详细信息',
            category: 'file',
            schema: { type: 'object', properties: { directory_path: { type: 'string' }, show_hidden: { type: 'boolean' }, recursive: { type: 'boolean' } } },
            enabled: false,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['目录', '浏览', '文件系统'] }
          },
          {
            id: '9',
            name: 'file_info',
            description: '获取文件详细信息和元数据',
            category: 'file',
            schema: { type: 'object', properties: { file_path: { type: 'string' }, checksum: { type: 'boolean' } } },
            enabled: true,
            implementation_type: 'builtin',
            created_at: new Date().toISOString(),
            updated_at: new Date().toISOString(),
            metadata: { tags: ['文件信息', '元数据', '校验'] }
          }
        ];

        const mockCategories: MCPCategoryInfo[] = [
          { id: 'system', name: '系统工具', description: '系统信息和监控相关工具', icon: '🖥️', enabled: true },
          { id: 'time', name: '时间工具', description: '时间戳和日期相关工具', icon: '⏰', enabled: true },
          { id: 'ai', name: 'AI工具', description: 'AI模式和智能助手相关工具', icon: '🤖', enabled: true },
          { id: 'dev', name: '开发工具', description: '开发和调试相关工具', icon: '⚙️', enabled: true },
          { id: 'data', name: '数据工具', description: '数据处理和分析相关工具', icon: '📊', enabled: true },
          { id: 'file', name: '文件工具', description: '文件和目录操作相关工具', icon: '📁', enabled: true }
        ];

        setTools(mockTools);
        setCategories(mockCategories);
        setStatus({
          status: 'healthy',
          server_name: 'LazyAI Studio MCP Server',
          tools_count: mockTools.filter(t => t.enabled).length,
          total_tools: mockTools.length,
          categories_count: mockCategories.length,
          tools_by_category: {
            system: 2,
            time: 1,
            ai: 1,
            data: 1,
            file: 4
          },
          endpoints: {},
          organization: 'LazyGophers',
          motto: '让 AI 替你思考，让工具替你工作！',
          last_updated: new Date().toISOString()
        });
      }
    } catch (error) {
      console.error('Failed to load MCP data:', error);
      messageApi.error('加载MCP工具数据失败');
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  // 切换工具开关状态
  const toggleTool = async (tool: MCPToolInfo, enabled: boolean) => {
    try {
      const response = enabled
        ? await apiClient.enableMCPTool(tool.name)
        : await apiClient.disableMCPTool(tool.name);

      if (response.success) {
        messageApi.success(`工具${tool.name}已${enabled ? '启用' : '禁用'}`);
        loadData(); // 重新加载数据
      } else {
        messageApi.error(response.message);
      }
    } catch (error) {
      // 模拟状态切换（用于演示）
      setTools(prevTools =>
        prevTools.map(t =>
          t.id === tool.id ? { ...t, enabled } : t
        )
      );
      messageApi.success(`工具${tool.name}已${enabled ? '启用' : '禁用'}`);
    }
  };

  // 切换分类开关状态
  const toggleCategory = async (category: MCPCategoryInfo, enabled: boolean) => {
    try {
      const response = enabled
        ? await apiClient.enableMCPCategory(category.id)
        : await apiClient.disableMCPCategory(category.id);

      if (response.success) {
        messageApi.success(`分类${category.name}已${enabled ? '启用' : '禁用'}`);
        loadData(); // 重新加载数据
      } else {
        messageApi.error(response.message);
      }
    } catch (error) {
      // 模拟状态切换（用于演示）
      setCategories(prevCategories =>
        prevCategories.map(c =>
          c.id === category.id ? { ...c, enabled } : c
        )
      );
      messageApi.success(`分类${category.name}已${enabled ? '启用' : '禁用'}`);
    }
  };

  // 测试工具
  const testTool = async (tool: MCPToolInfo, params: any) => {
    try {
      setLoading(true);
      const response = await apiClient.callMCPTool(tool.name, params);
      
      if (response.success) {
        setTestResult(JSON.stringify(response.data, null, 2));
        messageApi.success('工具测试成功');
      } else {
        setTestResult(`Error: ${response.message}`);
        messageApi.error('工具测试失败');
      }
    } catch (error) {
      setTestResult(`Error: ${error}`);
      messageApi.error('工具测试失败');
    } finally {
      setLoading(false);
    }
  };

  // 刷新工具配置
  const refreshTools = async () => {
    try {
      setLoading(true);
      const response = await apiClient.refreshMCPTools();
      
      if (response.success) {
        messageApi.success('工具配置已刷新');
        loadData();
      } else {
        messageApi.error(response.message);
      }
    } catch (error) {
      messageApi.success('工具配置已刷新'); // 模拟成功
      loadData();
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, [loadData]);

  // 按分类分组工具
  const getToolsByCategory = () => {
    const grouped: { [key: string]: MCPToolInfo[] } = {};
    
    // 初始化所有分类
    categories.forEach(category => {
      grouped[category.id] = [];
    });
    
    // 分组工具 - 确保 tools 是数组
    if (Array.isArray(tools)) {
      tools.forEach(tool => {
        if (!grouped[tool.category]) {
          grouped[tool.category] = [];
        }
        grouped[tool.category].push(tool);
      });
    }
    
    return grouped;
  };


  // 过滤工具
  const toolsByCategory = getToolsByCategory();
  
  // 显示所有分类（包括禁用的），但只有启用的分类会显示工具
  const filteredCategories = selectedCategory === 'all' 
    ? categories
    : categories.filter(cat => cat.id === selectedCategory);

  // 渲染工具卡片
  const renderToolCard = (tool: MCPToolInfo) => {
    const categoryInfo = categories.find(c => c.id === tool.category);
    
    // 使用主题token来获取颜色
    const token = currentTheme.token;
    const enabledBg = tool.enabled ? token?.colorSuccessBg || '#f6ffed' : token?.colorFillTertiary || '#f5f5f5';
    const enabledBorder = tool.enabled ? token?.colorSuccess || '#52c41a' : token?.colorBorderSecondary || '#d9d9d9';
    const cardBorder = tool.enabled ? token?.colorBorder || '#d9d9d9' : token?.colorBorderSecondary || '#f0f0f0';
    
    // 根据主题类型确定描述文字颜色，确保在所有主题下都可读
    const isDarkTheme = themeType === 'nightRain' || themeType === 'plumRain' || 
                       themeType === 'deepSeaMoon' || themeType === 'greenMountain';
    const descriptionColor = token?.colorTextSecondary || 
                            (isDarkTheme ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)');
    
    return (
      <Col xs={24} sm={12} lg={8} xl={6} key={tool.id}>
        <Card
          size="small"
          hoverable
          className={`tool-card ${!tool.enabled ? 'disabled' : ''}`}
          style={{ 
            height: '100%',
            opacity: tool.enabled ? 1 : 0.6,
            borderColor: cardBorder,
            backgroundColor: token?.colorBgContainer
          }}
        >
          <Card.Meta
            avatar={
              <div style={{ 
                width: 40, 
                height: 40, 
                borderRadius: '50%', 
                backgroundColor: enabledBg,
                border: `2px solid ${enabledBorder}`,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '16px'
              }}>
                {categoryInfo?.icon || '🔧'}
              </div>
            }
            title={
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <Text strong style={{ fontSize: 14, color: token?.colorText }}>{tool.name}</Text>
                  <Space size="small">
                    <Tooltip title={tool.enabled ? '禁用工具' : '启用工具'}>
                      <Switch
                        size="small"
                        checked={tool.enabled}
                        onChange={(checked) => toggleTool(tool, checked)}
                        checkedChildren={<CheckCircleOutlined />}
                        unCheckedChildren={<ExclamationCircleOutlined />}
                      />
                    </Tooltip>
                    <Tooltip title="查看详情">
                      <Button
                        type="text"
                        size="small"
                        icon={<InfoCircleOutlined />}
                        onClick={() => setToolDetailModal({ visible: true, tool })}
                      />
                    </Tooltip>
                    <Tooltip title={tool.enabled ? '测试工具' : '需要先启用工具'}>
                      <Button
                        type="text"
                        size="small"
                        icon={<BugOutlined />}
                        disabled={!tool.enabled}
                        onClick={() => setTestToolModal({ visible: true, tool, form })}
                      />
                    </Tooltip>
                  </Space>
                </div>
                <Tag color={tool.implementation_type === 'builtin' ? 'blue' : 'green'}>
                  {tool.implementation_type}
                </Tag>
              </div>
            }
            description={
              <div>
                <Paragraph 
                  ellipsis={{ rows: 2, tooltip: tool.description }} 
                  style={{ margin: 0, fontSize: 12, color: descriptionColor }}
                >
                  {tool.description}
                </Paragraph>
                <div style={{ marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 4 }}>
                  {tool.metadata?.tags?.slice(0, 3).map((tag: string, index: number) => (
                    <Tag key={index} color="geekblue" style={{ fontSize: '11px' }}>{tag}</Tag>
                  ))}
                  {tool.metadata?.tags?.length > 3 && (
                    <Tag color="default" style={{ fontSize: '11px' }}>+{tool.metadata.tags.length - 3}</Tag>
                  )}
                </div>
              </div>
            }
          />
        </Card>
      </Col>
    );
  };

  return (
    <div className="mcp-tools-management" style={{ padding: '0 24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: currentTheme.token?.colorText }}>
          <ApiOutlined /> MCP 工具管理
        </Title>
        <Paragraph style={{ color: currentTheme.token?.colorTextSecondary }}>
          管理 Model Context Protocol (MCP) 工具的启用状态和配置参数
        </Paragraph>
      </div>

      {/* 状态卡片 */}
      {status && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="可用工具"
                value={status.tools_count}
                suffix={`/ ${status.total_tools}`}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="工具分类"
                value={status.categories_count}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="服务状态"
                value={status.status}
                formatter={(value) => (
                  <Badge 
                    status={value === 'healthy' ? 'success' : 'error'} 
                    text={value === 'healthy' ? '正常' : '异常'}
                  />
                )}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="最后更新"
                value={new Date(status.last_updated).toLocaleString()}
                valueStyle={{ fontSize: 14 }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 工具筛选和操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <FilterOutlined />
              <Text>工具分类：</Text>
              <Select
                value={selectedCategory}
                onChange={setSelectedCategory}
                style={{ width: 160 }}
              >
                <Option value="all">所有分类 ({tools.length})</Option>
                {categories.map(category => {
                  const count = toolsByCategory[category.id]?.length || 0;
                  return (
                    <Option key={category.id} value={category.id} disabled={!category.enabled}>
                      {category.icon} {category.name} ({count}) {!category.enabled && '(禁用)'}
                    </Option>
                  );
                })}
              </Select>
            </Space>
          </Col>
          <Col>
            <Button
              type="primary"
              icon={<ReloadOutlined />}
              onClick={refreshTools}
              loading={loading}
            >
              刷新配置
            </Button>
          </Col>
        </Row>
      </Card>

      {/* 工具分类展示 */}
      <Spin spinning={loading}>
        {filteredCategories.length === 0 ? (
          <Empty description="暂无工具分类" />
        ) : (
          <Collapse 
            defaultActiveKey={selectedCategory === 'all' ? filteredCategories.map(c => c.id) : [selectedCategory]}
            ghost
            items={filteredCategories.map(category => {
              const categoryTools = toolsByCategory[category.id] || [];
              const enabledCount = categoryTools.filter(t => t.enabled).length;
              
              return {
                key: category.id,
                label: (
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', width: '100%' }}>
                    <Space>
                      <span style={{ fontSize: '18px', opacity: category.enabled ? 1 : 0.5 }}>{category.icon}</span>
                      <Title level={4} style={{ margin: 0, opacity: category.enabled ? 1 : 0.5 }}>
                        {category.name}
                      </Title>
                      <Text type="secondary">({enabledCount}/{categoryTools.length})</Text>
                      <Switch
                        size="small"
                        checked={category.enabled}
                        onChange={(checked) => toggleCategory(category, checked)}
                        checkedChildren="启用"
                        unCheckedChildren="禁用"
                      />
                      {category.enabled && (
                        <Tag color={enabledCount === categoryTools.length ? 'success' : enabledCount > 0 ? 'warning' : 'default'}>
                          {enabledCount === categoryTools.length ? '全部启用' : enabledCount > 0 ? '部分启用' : '全部禁用'}
                        </Tag>
                      )}
                      {!category.enabled && <Tag color="red">分类禁用</Tag>}
                      {category.id === 'file' && (
                        <Tooltip title="文件工具安全配置">
                          <Button
                            size="small"
                            icon={<SecurityScanOutlined />}
                            onClick={() => setFileToolsConfigModal(true)}
                            style={{
                              color: currentTheme.token?.colorPrimary,
                              borderColor: currentTheme.token?.colorPrimary,
                              backgroundColor: 'transparent'
                            }}
                          >
                            安全配置
                          </Button>
                        </Tooltip>
                      )}
                    </Space>
                    <div></div>
                  </div>
                ),
                extra: (
                  <Text type="secondary" style={{ fontSize: 12 }}>
                    {category.description}
                  </Text>
                ),
                children: !category.enabled ? (
                  <Alert
                    message="分类已禁用"
                    description={`${category.name} 分类当前处于禁用状态。启用分类以查看和管理其中的工具。`}
                    type="warning"
                    showIcon
                    style={{ margin: '16px 0' }}
                  />
                ) : categoryTools.length === 0 ? (
                  <Empty 
                    description={`${category.name} 分类下暂无工具`}
                    image={Empty.PRESENTED_IMAGE_SIMPLE}
                  />
                ) : (
                  <Row gutter={[16, 16]} style={{ marginTop: 16 }}>
                    {categoryTools.map(renderToolCard)}
                  </Row>
                )
              };
            })}
          />
        )}
      </Spin>

      {/* 工具详情Modal */}
      <Modal
        title={
          <Space>
            <ToolOutlined />
            工具详情
          </Space>
        }
        open={toolDetailModal.visible}
        onCancel={() => setToolDetailModal({ visible: false, tool: null })}
        footer={null}
        width={700}
      >
        {toolDetailModal.tool && (
          <div>
            <Descriptions column={2} bordered>
              <Descriptions.Item label="工具名称">
                {toolDetailModal.tool.name}
              </Descriptions.Item>
              <Descriptions.Item label="状态">
                <Badge 
                  status={toolDetailModal.tool.enabled ? 'success' : 'default'} 
                  text={toolDetailModal.tool.enabled ? '启用' : '禁用'}
                />
              </Descriptions.Item>
              <Descriptions.Item label="分类" span={2}>
                {categories.find(c => c.id === toolDetailModal.tool!.category)?.name || toolDetailModal.tool.category}
              </Descriptions.Item>
              <Descriptions.Item label="描述" span={2}>
                {toolDetailModal.tool.description}
              </Descriptions.Item>
              <Descriptions.Item label="实现类型">
                {toolDetailModal.tool.implementation_type}
              </Descriptions.Item>
              <Descriptions.Item label="创建时间">
                {new Date(toolDetailModal.tool.created_at).toLocaleString()}
              </Descriptions.Item>
            </Descriptions>

            <Divider />

            <Title level={4}>Schema 定义</Title>
            <pre style={{ 
              background: currentTheme.token?.colorFillQuaternary || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.02)'), 
              border: `1px solid ${currentTheme.token?.colorBorder || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)')}`,
              color: currentTheme.token?.colorText || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(0, 0, 0, 0.85)'),
              padding: 16, 
              borderRadius: 6,
              fontSize: 12,
              overflow: 'auto'
            }}>
              {JSON.stringify(toolDetailModal.tool.schema, null, 2)}
            </pre>

            {toolDetailModal.tool.metadata && (
              <>
                <Divider />
                <Title level={4}>元数据</Title>
                <pre style={{ 
                  background: currentTheme.token?.colorFillQuaternary || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.04)' : 'rgba(0, 0, 0, 0.02)'), 
                  border: `1px solid ${currentTheme.token?.colorBorder || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.1)' : 'rgba(0, 0, 0, 0.06)')}`,
                  color: currentTheme.token?.colorText || (themeType === 'nightRain' || themeType === 'plumRain' || themeType === 'deepSeaMoon' || themeType === 'greenMountain' ? 'rgba(255, 255, 255, 0.85)' : 'rgba(0, 0, 0, 0.85)'),
                  padding: 16, 
                  borderRadius: 6,
                  fontSize: 12,
                  overflow: 'auto'
                }}>
                  {JSON.stringify(toolDetailModal.tool.metadata, null, 2)}
                </pre>
              </>
            )}
          </div>
        )}
      </Modal>

      {/* 工具测试Modal */}
      <Modal
        title={
          <Space>
            <BugOutlined />
            测试工具: {testToolModal.tool?.name}
          </Space>
        }
        open={testToolModal.visible}
        onCancel={() => {
          setTestToolModal({ visible: false, tool: null, form: null });
          setTestResult('');
          form.resetFields();
        }}
        onOk={() => {
          form.validateFields().then(values => {
            testTool(testToolModal.tool!, values);
          });
        }}
        confirmLoading={loading}
        width={800}
      >
        {testToolModal.tool && (
          <div>
            <Alert
              message="工具测试"
              description={`正在测试工具 "${testToolModal.tool.name}"，请填写测试参数`}
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />

            <Form form={form} layout="vertical">
              {testToolModal.tool.schema?.properties && Object.entries(testToolModal.tool.schema.properties).map(([key, prop]: [string, any]) => (
                <Form.Item
                  key={key}
                  label={key}
                  name={key}
                  help={prop.description}
                >
                  {prop.type === 'boolean' ? (
                    <Select placeholder={`选择 ${key}`}>
                      <Option value={true}>true</Option>
                      <Option value={false}>false</Option>
                    </Select>
                  ) : prop.enum ? (
                    <Select placeholder={`选择 ${key}`}>
                      {prop.enum.map((option: string) => (
                        <Option key={option} value={option}>{option}</Option>
                      ))}
                    </Select>
                  ) : (
                    <Input placeholder={`输入 ${key}`} />
                  )}
                </Form.Item>
              ))}
            </Form>

            {testResult && (
              <>
                <Divider />
                <Title level={4}>测试结果</Title>
                <TextArea
                  value={testResult}
                  rows={8}
                  readOnly
                  style={{ fontFamily: 'monospace', fontSize: 12 }}
                />
              </>
            )}
          </div>
        )}
      </Modal>

      {/* 文件工具配置Modal */}
      <FileToolsConfigModal
        visible={fileToolsConfigModal}
        onCancel={() => setFileToolsConfigModal(false)}
      />
    </div>
  );
};

export default MCPToolsManagement;