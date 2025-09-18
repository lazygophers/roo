import React, {useCallback, useEffect, useState} from 'react';
import {
    Alert,
    App,
    Badge,
    Button,
    Col,
    Collapse,
    Divider,
    Empty,
    Form,
    Input,
    Modal,
    Row,
    Select,
    Space,
    Spin,
    Switch,
    Tag,
    Tooltip,
    Typography
} from 'antd';
import {ProCard, ProDescriptions} from '@ant-design/pro-components';
import {
    ApiOutlined,
    BugOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    InfoCircleOutlined,
    ReloadOutlined
} from '@ant-design/icons';
import {apiClient, MCPCategoryInfo, MCPToolInfo} from '../api';
import {useTheme} from '../contexts/ThemeContext';
import FileToolsConfigModal from '../components/FileTools/FileToolsConfigModal';
import TimeToolsConfigModal from '../components/TimeTools/TimeToolsConfigModal';
import GitHubToolsConfigModal from '../components/GitHubTools/GitHubToolsConfigModal';
import CacheToolsConfigModal from '../components/CacheTools/CacheToolsConfigModal';
import './MCPToolsManagement.css';

const {Title, Text, Paragraph} = Typography;
const {Option} = Select;
const {TextArea} = Input;
const {useApp} = App;

const MCPToolsManagement: React.FC = () => {
    // eslint-disable-next-line @typescript-eslint/no-unused-vars
    const {currentTheme, themeType} = useTheme();
    const {message: messageApi} = useApp();
    const [loading, setLoading] = useState(false);
    const [tools, setTools] = useState<MCPToolInfo[]>([]);
    const [categories, setCategories] = useState<MCPCategoryInfo[]>([]);
    const [toolDetailModal, setToolDetailModal] = useState<{
        visible: boolean;
        tool: MCPToolInfo | null;
    }>({visible: false, tool: null});
    const [testToolModal, setTestToolModal] = useState<{
        visible: boolean;
        tool: MCPToolInfo | null;
        form: any;
    }>({visible: false, tool: null, form: null});
    const [testResult, setTestResult] = useState<string>('');
    const [fileToolsConfigModal, setFileToolsConfigModal] = useState(false);
    const [timeToolsConfigModal, setTimeToolsConfigModal] = useState(false);
    const [githubToolsConfigModal, setGithubToolsConfigModal] = useState(false);
    const [cacheToolsConfigModal, setCacheToolsConfigModal] = useState(false);
    const [githubTokenValid, setGithubTokenValid] = useState<boolean | null>(null);

    const [form] = Form.useForm();

    // 检查 GitHub Token 有效性
    const checkGitHubToken = useCallback(async () => {
        try {
            const response = await fetch('/api/mcp/categories/github/token-status');
            const data = await response.json();
            if (data.success) {
                setGithubTokenValid(data.data.valid);
            } else {
                setGithubTokenValid(false);
            }
        } catch (error) {
            console.error('Check GitHub token error:', error);
            setGithubTokenValid(false);
        }
    }, []);

    // 加载数据
    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [, categoriesRes, toolsRes] = await Promise.all([
                apiClient.getMCPStatus().catch(e => ({success: false, data: null})),
                apiClient.getMCPCategories().catch(e => ({
                    success: false,
                    data: {categories: [], total_categories: 0}
                })),
                apiClient.getMCPTools().catch(e => ({success: false, data: {tools: [], server: '', organization: ''}})),
                checkGitHubToken() // 检查GitHub Token状态
            ]);

            // if (statusRes.success && statusRes.data) {
            //   setStatus(statusRes.data);
            // }

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
                        schema: {
                            type: 'object',
                            properties: {format: {type: 'string', enum: ['iso', 'unix', 'formatted']}}
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['时间', '时间戳', '格式化']}
                    },
                    {
                        id: '2',
                        name: 'get_system_info',
                        description: '获取LazyAI Studio系统信息，包括CPU、内存、操作系统等',
                        category: 'system',
                        schema: {
                            type: 'object',
                            properties: {detailed: {type: 'boolean'}, include_performance: {type: 'boolean'}}
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['系统', '监控', '性能']}
                    },
                    {
                        id: '5',
                        name: 'health_check',
                        description: '执行系统健康检查，验证各组件状态',
                        category: 'system',
                        schema: {
                            type: 'object',
                            properties: {check_database: {type: 'boolean'}, check_cache: {type: 'boolean'}}
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['健康检查', '监控', '诊断']}
                    },
                    {
                        id: '6',
                        name: 'read_file',
                        description: '读取文件内容，支持多种编码格式',
                        category: 'file',
                        schema: {
                            type: 'object',
                            properties: {
                                file_path: {type: 'string'},
                                encoding: {type: 'string'},
                                max_lines: {type: 'number'}
                            }
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['文件', '读取', 'I/O']}
                    },
                    {
                        id: '7',
                        name: 'write_file',
                        description: '写入或追加内容到文件',
                        category: 'file',
                        schema: {
                            type: 'object',
                            properties: {file_path: {type: 'string'}, content: {type: 'string'}, mode: {type: 'string'}}
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['文件', '写入', 'I/O']}
                    },
                    {
                        id: '8',
                        name: 'list_directory',
                        description: '列出目录内容，支持递归和详细信息',
                        category: 'file',
                        schema: {
                            type: 'object',
                            properties: {
                                directory_path: {type: 'string'},
                                show_hidden: {type: 'boolean'},
                                recursive: {type: 'boolean'}
                            }
                        },
                        enabled: false,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['目录', '浏览', '文件系统']}
                    },
                    {
                        id: '9',
                        name: 'file_info',
                        description: '获取文件详细信息和元数据',
                        category: 'file',
                        schema: {
                            type: 'object',
                            properties: {file_path: {type: 'string'}, checksum: {type: 'boolean'}}
                        },
                        enabled: true,
                        implementation_type: 'builtin',
                        created_at: new Date().toISOString(),
                        updated_at: new Date().toISOString(),
                        metadata: {tags: ['文件信息', '元数据', '校验']}
                    }
                ];

                const mockCategories: MCPCategoryInfo[] = [
                    {id: 'system', name: '系统工具', description: '系统信息和监控相关工具', icon: '🖥️', enabled: true},
                    {id: 'time', name: '时间工具', description: '时间戳和日期相关工具', icon: '⏰', enabled: true},
                    {id: 'file', name: '文件工具', description: '文件和目录操作相关工具', icon: '📁', enabled: true},
                    {id: 'github', name: 'GitHub工具', description: 'GitHub API集成工具，包括仓库管理、issue处理、PR操作等', icon: '🐙', enabled: true},
                    {
                        id: 'cache',
                        name: '缓存工具',
                        description: '缓存操作相关工具',
                        icon: '🗄️',
                        enabled: true
                    }
                ];

                setTools(mockTools);
                setCategories(mockCategories);
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
                    t.id === tool.id ? {...t, enabled} : t
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
                    c.id === category.id ? {...c, enabled} : c
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

    // 显示所有分类（包括禁用的）
    const filteredCategories = categories;

    // 渲染工具卡片
    const renderToolCard = (tool: MCPToolInfo) => {

        // 使用主题token来获取颜色
        const token = currentTheme.token;
        const cardBorder = tool.enabled ? token?.colorBorder || '#d9d9d9' : token?.colorBorderSecondary || '#f0f0f0';

        // 根据主题类型确定描述文字颜色，确保在所有主题下都可读
        const isDarkTheme = themeType === 'nightRain' || themeType === 'plumRain' ||
            themeType === 'deepSeaMoon' || themeType === 'greenMountain';
        const descriptionColor = token?.colorTextSecondary ||
            (isDarkTheme ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)');

        return (
            <Col xs={24} sm={12} lg={8} xl={6} key={tool.id}>
                <ProCard
                    size="small"
                    hoverable
                    className={`tool-card ${!tool.enabled ? 'disabled' : ''}`}
                    style={{
                        height: '100%',
                        opacity: tool.enabled ? 1 : 0.6,
                        borderColor: cardBorder,
                        backgroundColor: token?.colorBgContainer
                    }}
                    title={
                        <div style={{display: 'flex', alignItems: 'center', justifyContent: 'space-between'}}>
                            <div style={{display: 'flex', alignItems: 'center', gap: 8}}>
                                <Text strong style={{fontSize: 14, color: token?.colorText}}>{tool.name}</Text>
                            </div>
                            <Tag color={tool.implementation_type === 'builtin' ? 'blue' : 'green'}>
                                {tool.implementation_type}
                            </Tag>
                        </div>
                    }
                    extra={
                        <Space size="small">
                            <Tooltip title={tool.enabled ? '禁用工具' : '启用工具'}>
                                <Switch
                                    size="small"
                                    checked={tool.enabled}
                                    onChange={(checked) => toggleTool(tool, checked)}
                                    checkedChildren={<CheckCircleOutlined/>}
                                    unCheckedChildren={<ExclamationCircleOutlined/>}
                                />
                            </Tooltip>
                            <Tooltip title="查看详情">
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<InfoCircleOutlined/>}
                                    onClick={() => setToolDetailModal({visible: true, tool})}
                                />
                            </Tooltip>
                            <Tooltip title={tool.enabled ? '测试工具' : '需要先启用工具'}>
                                <Button
                                    type="text"
                                    size="small"
                                    icon={<BugOutlined/>}
                                    disabled={!tool.enabled}
                                    onClick={() => setTestToolModal({visible: true, tool, form})}
                                />
                            </Tooltip>
                        </Space>
                    }
                >
                    <div>
                        <Typography.Paragraph
                            ellipsis={{rows: 2, tooltip: tool.description}}
                            style={{margin: 0, fontSize: 12, color: descriptionColor}}
                        >
                            {tool.description}
                        </Typography.Paragraph>
                        <div style={{marginTop: 8, display: 'flex', flexWrap: 'wrap', gap: 4}}>
                            {tool.metadata?.tags?.slice(0, 3).map((tag: string, index: number) => (
                                <Tag key={index} color="geekblue" style={{fontSize: '11px'}}>{tag}</Tag>
                            ))}
                            {tool.metadata?.tags?.length > 3 && (
                                <Tag color="default" style={{fontSize: '11px'}}>+{tool.metadata.tags.length - 3}</Tag>
                            )}
                        </div>
                    </div>
                </ProCard>
            </Col>
        );
    };

    return (
        <div className="mcp-tools-management" style={{padding: '0 24px'}}>
            <div style={{marginBottom: 24}}>
                <Title level={2} style={{color: currentTheme.token?.colorText}}>
                    <ApiOutlined/> MCP 工具管理
                </Title>
                <Paragraph style={{color: currentTheme.token?.colorTextSecondary}}>
                    管理 Model Context Protocol (MCP) 工具的启用状态和配置参数
                </Paragraph>
            </div>



            {/* 操作栏 */}
            <Row justify="end" style={{marginBottom: 16}}>
                <Col>
                    <Button
                        type="primary"
                        icon={<ReloadOutlined/>}
                        onClick={refreshTools}
                        loading={loading}
                    >
                        刷新配置
                    </Button>
                </Col>
            </Row>

            {/* 工具分类展示 */}
            <Spin spinning={loading}>
                {filteredCategories.length === 0 ? (
                    <Empty description="暂无工具分类"/>
                ) : (
                    <Collapse
                        defaultActiveKey={filteredCategories.map(c => c.id)}
                        ghost
                        items={filteredCategories.map(category => {
                            const categoryTools = toolsByCategory[category.id] || [];
                            const enabledCount = categoryTools.filter(t => t.enabled).length;

                            return {
                                key: category.id,
                                label: (
                                    <div style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'space-between',
                                        width: '100%'
                                    }}>
                                        <Space>
                                            <Title level={4} style={{margin: 0, opacity: category.enabled ? 1 : 0.5}}>
                                                {category.name}
                                            </Title>
                                            <Text type="secondary">({enabledCount}/{categoryTools.length})</Text>
                                            <div onClick={(e) => e.stopPropagation()}>
                                                <Switch
                                                    size="small"
                                                    checked={category.enabled}
                                                    onChange={(checked) => toggleCategory(category, checked)}
                                                    checkedChildren="启用"
                                                    unCheckedChildren="禁用"
                                                />
                                            </div>
                                            {category.enabled && (
                                                <Tag
                                                    color={enabledCount === categoryTools.length ? 'success' : enabledCount > 0 ? 'warning' : 'default'}>
                                                    {enabledCount === categoryTools.length ? '全部启用' : enabledCount > 0 ? '部分启用' : '全部禁用'}
                                                </Tag>
                                            )}
                                            {!category.enabled && <Tag color="red">分类禁用</Tag>}
                                            {/* 统一的配置按钮样式 */}
                                            {category.id === 'file' && (
                                                <Tooltip title="文件工具安全配置">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setFileToolsConfigModal(true);
                                                        }}
                                                        style={{
                                                            color: currentTheme.token?.colorPrimary,
                                                            borderColor: currentTheme.token?.colorPrimary,
                                                            backgroundColor: 'rgba(24, 144, 255, 0.06)',
                                                            borderRadius: 6,
                                                            border: `1px solid ${currentTheme.token?.colorPrimary}20`,
                                                            transition: 'all 0.2s ease'
                                                        }}
                                                        onMouseEnter={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.12)';
                                                            e.currentTarget.style.borderColor = currentTheme.token?.colorPrimary || '#1890ff';
                                                        }}
                                                        onMouseLeave={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.06)';
                                                            e.currentTarget.style.borderColor = `${currentTheme.token?.colorPrimary}20` || '#1890ff20';
                                                        }}
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {category.id === 'time' && (
                                                <Tooltip title="时间工具配置">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setTimeToolsConfigModal(true);
                                                        }}
                                                        style={{
                                                            color: currentTheme.token?.colorPrimary,
                                                            borderColor: currentTheme.token?.colorPrimary,
                                                            backgroundColor: 'rgba(24, 144, 255, 0.06)',
                                                            borderRadius: 6,
                                                            border: `1px solid ${currentTheme.token?.colorPrimary}20`,
                                                            transition: 'all 0.2s ease'
                                                        }}
                                                        onMouseEnter={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.12)';
                                                            e.currentTarget.style.borderColor = currentTheme.token?.colorPrimary || '#1890ff';
                                                        }}
                                                        onMouseLeave={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.06)';
                                                            e.currentTarget.style.borderColor = `${currentTheme.token?.colorPrimary}20` || '#1890ff20';
                                                        }}
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {category.id === 'cache' && (
                                                <Tooltip title="缓存工具配置">
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setCacheToolsConfigModal(true);
                                                        }}
                                                        style={{
                                                            color: currentTheme.token?.colorPrimary,
                                                            borderColor: currentTheme.token?.colorPrimary,
                                                            backgroundColor: 'rgba(24, 144, 255, 0.06)',
                                                            borderRadius: 6,
                                                            border: `1px solid ${currentTheme.token?.colorPrimary}20`,
                                                            transition: 'all 0.2s ease'
                                                        }}
                                                        onMouseEnter={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.12)';
                                                            e.currentTarget.style.borderColor = currentTheme.token?.colorPrimary || '#1890ff';
                                                        }}
                                                        onMouseLeave={(e) => {
                                                            e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.06)';
                                                            e.currentTarget.style.borderColor = `${currentTheme.token?.colorPrimary}20` || '#1890ff20';
                                                        }}
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {category.id === 'github' && (
                                                <Space>
                                                    {githubTokenValid === false && (
                                                        <Tooltip title="GitHub Token未配置或无效，工具集不可用">
                                                            <Tag color="red" style={{margin: 0}}>
                                                                <ExclamationCircleOutlined /> 不可用
                                                            </Tag>
                                                        </Tooltip>
                                                    )}
                                                    <Tooltip title="GitHub工具配置">
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            onClick={(e) => {
                                                                e.stopPropagation();
                                                                setGithubToolsConfigModal(true);
                                                            }}
                                                            style={{
                                                                color: currentTheme.token?.colorPrimary,
                                                                borderColor: currentTheme.token?.colorPrimary,
                                                                backgroundColor: 'rgba(24, 144, 255, 0.06)',
                                                                borderRadius: 6,
                                                                border: `1px solid ${currentTheme.token?.colorPrimary}20`,
                                                                transition: 'all 0.2s ease'
                                                            }}
                                                            onMouseEnter={(e) => {
                                                                e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.12)';
                                                                e.currentTarget.style.borderColor = currentTheme.token?.colorPrimary || '#1890ff';
                                                            }}
                                                            onMouseLeave={(e) => {
                                                                e.currentTarget.style.backgroundColor = 'rgba(24, 144, 255, 0.06)';
                                                                e.currentTarget.style.borderColor = `${currentTheme.token?.colorPrimary}20` || '#1890ff20';
                                                            }}
                                                        >
                                                            工具配置
                                                        </Button>
                                                    </Tooltip>
                                                </Space>
                                            )}
                                        </Space>
                                    </div>
                                ),
                                extra: (
                                    <Text type="secondary" style={{fontSize: 12}}>
                                        {category.description}
                                    </Text>
                                ),
                                children: !category.enabled ? (
                                    <Alert
                                        message="分类已禁用"
                                        description={`${category.name} 分类当前处于禁用状态。启用分类以查看和管理其中的工具。`}
                                        type="warning"
                                        showIcon
                                        style={{margin: '16px 0'}}
                                    />
                                ) : category.id === 'github' && githubTokenValid === false ? (
                                    <Alert
                                        message="GitHub工具集不可用"
                                        description={
                                            <div>
                                                <p>GitHub工具集当前不可用，原因：GitHub Token未配置或无效。</p>
                                                <p>
                                                    请点击右侧的"工具配置"按钮配置有效的GitHub Token，或者联系管理员获取帮助。
                                                </p>
                                                <ul style={{marginTop: 8}}>
                                                    <li>确保GitHub Token格式正确（以ghp_或github_pat_开头）</li>
                                                    <li>确保Token具有适当的权限</li>
                                                    <li>确保Token未过期</li>
                                                </ul>
                                            </div>
                                        }
                                        type="error"
                                        showIcon
                                        style={{margin: '16px 0'}}
                                        action={
                                            <Button
                                                type="primary"
                                                size="small"
                                                onClick={() => setGithubToolsConfigModal(true)}
                                            >
                                                立即配置
                                            </Button>
                                        }
                                    />
                                ) : categoryTools.length === 0 ? (
                                    <Empty
                                        description={`${category.name} 分类下暂无工具`}
                                        image={Empty.PRESENTED_IMAGE_SIMPLE}
                                    />
                                ) : (
                                    <Row gutter={[16, 16]} style={{marginTop: 16}}>
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
                title="工具详情"
                open={toolDetailModal.visible}
                onCancel={() => setToolDetailModal({visible: false, tool: null})}
                footer={null}
                width={700}
            >
                {toolDetailModal.tool && (
                    <div>
                        <ProDescriptions
                            column={2}
                            bordered
                            dataSource={{
                                '工具名称': toolDetailModal.tool.name,
                                '状态': (
                                    <Badge
                                        status={toolDetailModal.tool.enabled ? 'success' : 'default'}
                                        text={toolDetailModal.tool.enabled ? '启用' : '禁用'}
                                    />
                                ),
                                '分类': categories.find(c => c.id === toolDetailModal.tool!.category)?.name || toolDetailModal.tool.category,
                                '描述': toolDetailModal.tool.description,
                                '实现类型': toolDetailModal.tool.implementation_type,
                                '创建时间': new Date(toolDetailModal.tool.created_at).toLocaleString(),
                            }}
                        />

                        <Divider/>

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
                                <Divider/>
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
                        <BugOutlined/>
                        测试工具: {testToolModal.tool?.name}
                    </Space>
                }
                open={testToolModal.visible}
                onCancel={() => {
                    setTestToolModal({visible: false, tool: null, form: null});
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
                            style={{marginBottom: 16}}
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
                                        <Input placeholder={`输入 ${key}`}/>
                                    )}
                                </Form.Item>
                            ))}
                        </Form>

                        {testResult && (
                            <>
                                <Divider/>
                                <Title level={4}>测试结果</Title>
                                <TextArea
                                    value={testResult}
                                    rows={8}
                                    readOnly
                                    style={{fontFamily: 'monospace', fontSize: 12}}
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

            {/* 时间工具配置Modal */}
            <TimeToolsConfigModal
                visible={timeToolsConfigModal}
                onCancel={() => setTimeToolsConfigModal(false)}
            />

            {/* GitHub工具配置Modal */}
            <GitHubToolsConfigModal
                visible={githubToolsConfigModal}
                onCancel={() => setGithubToolsConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                    checkGitHubToken(); // 重新检查token状态
                }}
            />

            {/* 缓存工具配置Modal */}
            <CacheToolsConfigModal
                visible={cacheToolsConfigModal}
                onCancel={() => setCacheToolsConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                }}
            />
        </div>
    );
};

export default MCPToolsManagement;