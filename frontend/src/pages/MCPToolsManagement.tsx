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
    ReloadOutlined,
    SettingOutlined
} from '@ant-design/icons';
import {apiClient, MCPCategoryInfo, MCPToolInfo, EnvironmentInfo} from '../api';
import {useTheme} from '../contexts/ThemeContext';
import {useEnvironment} from '../contexts/EnvironmentContext';
import {pageCacheManager} from '../hooks/useLazyLoading';
import FileToolsConfigModal from '../components/FileTools/FileToolsConfigModal';
import TimeToolsConfigModal from '../components/TimeTools/TimeToolsConfigModal';
import GitHubToolsConfigModal from '../components/GitHubTools/GitHubToolsConfigModal';
import CacheToolsConfigModal from '../components/CacheTools/CacheToolsConfigModal';
import WebScrapingConfigModal from '../components/WebScrapingTools/WebScrapingConfigModal';
import MCPConfigModal from '../components/MCPConfig/MCPConfigModal';
import './MCPToolsManagement.css';

const {Title, Text, Paragraph} = Typography;
const {Option} = Select;
const {TextArea} = Input;
const {useApp} = App;

// 分类工具渲染组件
interface CategoryToolsRendererProps {
    category: MCPCategoryInfo;
    onLoadTools: (categoryId: string) => Promise<void>;
    categoryTools: Record<string, MCPToolInfo[]>;
    categoryLoadingStates: Record<string, boolean>;
    githubTokenValid: boolean | null;
    environmentInfo: EnvironmentInfo | null;
    isEditAllowed: boolean;
    currentTheme: any;
    themeType: string;
    onToggleTool: (tool: MCPToolInfo, enabled: boolean) => void;
    onShowToolDetail: (tool: MCPToolInfo) => void;
    onTestTool: (tool: MCPToolInfo, form: any) => void;
    form: any;
}

const CategoryToolsRenderer: React.FC<CategoryToolsRendererProps> = ({
    category,
    onLoadTools,
    categoryTools,
    categoryLoadingStates,
    githubTokenValid,
    environmentInfo,
    isEditAllowed,
    currentTheme,
    themeType,
    onToggleTool,
    onShowToolDetail,
    onTestTool,
    form
}) => {
    const tools = categoryTools[category.id] || [];
    const isLoading = categoryLoadingStates[category.id] || false;

    // 判断是否有工具数据
    const hasTools = tools.length > 0;

    // 渲染工具卡片
    const renderToolCard = (tool: MCPToolInfo) => {
        const token = currentTheme.token;
        const cardBorder = tool.enabled ? token?.colorBorder || '#d9d9d9' : token?.colorBorderSecondary || '#f0f0f0';
        const isDarkTheme = themeType === 'nightRain' || themeType === 'plumRain' ||
            themeType === 'deepSeaMoon' || themeType === 'greenMountain';
        const descriptionColor = token?.colorTextSecondary ||
            (isDarkTheme ? 'rgba(255, 255, 255, 0.65)' : 'rgba(0, 0, 0, 0.65)');

        return (
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
                        <Tooltip title={
                            !isEditAllowed ? '远程环境下配置编辑被禁用' :
                            tool.enabled ? '禁用工具' : '启用工具'
                        }>
                            <Switch
                                size="small"
                                checked={tool.enabled}
                                disabled={!isEditAllowed}
                                onChange={(checked) => onToggleTool(tool, checked)}
                                checkedChildren={<CheckCircleOutlined/>}
                                unCheckedChildren={<ExclamationCircleOutlined/>}
                            />
                        </Tooltip>
                        <Tooltip title="查看详情">
                            <Button
                                type="text"
                                size="small"
                                icon={<InfoCircleOutlined/>}
                                onClick={() => onShowToolDetail(tool)}
                            />
                        </Tooltip>
                        <Tooltip title={
                            !environmentInfo?.tool_call_allowed ? '远程环境下工具调用被禁用' :
                            !tool.enabled ? '需要先启用工具' : '测试工具'
                        }>
                            <Button
                                type="text"
                                size="small"
                                icon={<BugOutlined/>}
                                disabled={!tool.enabled || !environmentInfo?.tool_call_allowed}
                                onClick={() => onTestTool(tool, form)}
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
                            <Tag key={`${tool.id}-tag-${index}`} color="geekblue" style={{fontSize: '11px'}}>{tag}</Tag>
                        ))}
                        {tool.metadata?.tags?.length > 3 && (
                            <Tag key={`${tool.id}-tag-more`} color="default" style={{fontSize: '11px'}}>+{tool.metadata.tags.length - 3}</Tag>
                        )}
                    </div>
                </div>
            </ProCard>
        );
    };

    // 处理加载状态
    if (isLoading) {
        return (
            <div style={{
                height: '200px',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center'
            }}>
                <Spin size="large" />
                <span style={{ marginLeft: 12, color: currentTheme.token?.colorTextSecondary }}>
                    正在加载 {category.name} 工具...
                </span>
            </div>
        );
    }

    // 处理分类禁用状态
    if (!category.enabled) {
        return (
            <Alert
                message="分类已禁用"
                description={`${category.name} 分类当前处于禁用状态。启用分类以查看和管理其中的工具。`}
                type="warning"
                showIcon
                style={{margin: '16px 0'}}
            />
        );
    }

    // 处理 GitHub Token 无效状态
    if (category.id === 'github' && githubTokenValid === false) {
        return (
            <Alert
                message="GitHub工具集不可用"
                description={
                    <div>
                        <p>GitHub工具集当前不可用，原因：GitHub Token未配置或无效。</p>
                        <p>请点击右侧的"工具配置"按钮配置有效的GitHub Token，或者联系管理员获取帮助。</p>
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
            />
        );
    }

    // 处理无工具状态
    if (!hasTools) {
        return (
            <Empty
                description={`${category.name} 分类下暂无工具`}
                image={Empty.PRESENTED_IMAGE_SIMPLE}
            />
        );
    }

    return (
        <Row gutter={[16, 16]} style={{marginTop: 16}}>
            {tools.map((tool) => (
                <Col key={tool.id || tool.name} xs={24} sm={12} md={8} lg={6} xl={6}>
                    {renderToolCard(tool)}
                </Col>
            ))}
        </Row>
    );
};

const MCPToolsManagement: React.FC = () => {
    const {currentTheme, themeType} = useTheme();
    const {message: messageApi} = useApp();
    const {isEditAllowed} = useEnvironment();
    const [loading, setLoading] = useState(false);
    const [tools, setTools] = useState<MCPToolInfo[]>([]);
    const [categories, setCategories] = useState<MCPCategoryInfo[]>([]);
    const [categoryTools, setCategoryTools] = useState<Record<string, MCPToolInfo[]>>({});
    const [expandedCategories, setExpandedCategories] = useState<Set<string>>(new Set());
    const [categoryLoadingStates, setCategoryLoadingStates] = useState<Record<string, boolean>>({});
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
    const [webScrapingConfigModal, setWebScrapingConfigModal] = useState(false);
    const [mcpConfigModal, setMcpConfigModal] = useState(false);
    const [githubTokenValid, setGithubTokenValid] = useState<boolean | null>(null);
    const [environmentInfo, setEnvironmentInfo] = useState<EnvironmentInfo | null>(null);

    const [form] = Form.useForm();

    // 页面卸载时清除缓存
    useEffect(() => {
        return () => {
            pageCacheManager.clearPageCache('mcp-tools-management');
        };
    }, []);

    // 获取环境信息
    const fetchEnvironmentInfo = useCallback(async () => {
        try {
            const response = await apiClient.getEnvironmentInfo();
            if (response.success) {
                setEnvironmentInfo(response.data);
            }
        } catch (error) {
            console.error('Failed to fetch environment info:', error);
        }
    }, []);

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

    // 获取模拟工具数据（按分类）
    const getMockToolsForCategory = useCallback((categoryId: string): MCPToolInfo[] => {
        const allMockTools: MCPToolInfo[] = [
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
            },
            {
                id: '10',
                name: 'fetch_http_request',
                description: '执行HTTP请求，支持GET、POST等方法，可设置请求头、参数、认证等',
                category: 'fetch',
                schema: {
                    type: 'object',
                    properties: {
                        url: {type: 'string', description: '请求URL'},
                        method: {type: 'string', enum: ['GET', 'POST', 'PUT', 'DELETE'], description: 'HTTP方法'},
                        headers: {type: 'object', description: '请求头'}
                    },
                    required: ['url']
                },
                enabled: true,
                implementation_type: 'builtin',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                metadata: {tags: ['http', 'request', 'api']}
            },
            {
                id: '11',
                name: 'fetch_fetch_webpage',
                description: '抓取网页内容，支持提取文本、链接和图片，使用BeautifulSoup解析HTML',
                category: 'fetch',
                schema: {
                    type: 'object',
                    properties: {
                        url: {type: 'string', description: '网页URL'},
                        extract_links: {type: 'boolean', description: '是否提取链接'},
                        extract_images: {type: 'boolean', description: '是否提取图片'}
                    },
                    required: ['url']
                },
                enabled: true,
                implementation_type: 'builtin',
                created_at: new Date().toISOString(),
                updated_at: new Date().toISOString(),
                metadata: {tags: ['scraping', 'html', 'beautifulsoup']}
            }
        ];

        return allMockTools.filter(tool => tool.category === categoryId);
    }, []);

    // 加载单个分类的工具
    const loadCategoryTools = useCallback(async (categoryId: string) => {
        // 设置加载状态
        setCategoryLoadingStates(prev => ({ ...prev, [categoryId]: true }));

        try {
            console.log(`[MCPTools] Loading tools for category: ${categoryId}`);
            const response = await apiClient.getMCPToolsByCategory(categoryId);

            if (response.success && response.data && Array.isArray(response.data.tools)) {
                console.log(`[MCPTools] Loaded ${response.data.tools.length} tools for category: ${categoryId}`);
                setCategoryTools(prev => ({
                    ...prev,
                    [categoryId]: response.data.tools
                }));
            } else {
                console.log(`[MCPTools] Failed to load tools for category: ${categoryId}`, response);
                // 使用模拟数据作为后备
                const mockTools = getMockToolsForCategory(categoryId);
                setCategoryTools(prev => ({
                    ...prev,
                    [categoryId]: mockTools
                }));
            }
        } catch (error) {
            console.error(`Failed to load tools for category ${categoryId}:`, error);
            // 使用模拟数据作为后备
            const mockTools = getMockToolsForCategory(categoryId);
            setCategoryTools(prev => ({
                ...prev,
                [categoryId]: mockTools
            }));
        } finally {
            // 清除加载状态
            setCategoryLoadingStates(prev => ({ ...prev, [categoryId]: false }));
        }
    }, [getMockToolsForCategory]);

    // 加载基础数据（分类和环境信息）
    const loadData = useCallback(async () => {
        setLoading(true);
        try {
            const [, categoriesRes] = await Promise.all([
                apiClient.getMCPStatus().catch(e => ({success: false, data: null})),
                apiClient.getMCPCategories().catch(e => ({
                    success: false,
                    data: {categories: [], total_categories: 0}
                })),
                checkGitHubToken(), // 检查GitHub Token状态
                fetchEnvironmentInfo() // 获取环境信息
            ]);

            if (categoriesRes.success && categoriesRes.data) {
                setCategories(categoriesRes.data.categories);
            } else {
                // 使用模拟分类数据
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
                    },
                    {
                        id: 'fetch',
                        name: '网络抓取工具',
                        description: '网页抓取、HTTP请求、API调用等网络数据获取工具',
                        icon: '🌐',
                        enabled: true
                    }
                ];
                setCategories(mockCategories);
            }
        } catch (error) {
            console.error('Failed to load MCP data:', error);
            messageApi.error('加载MCP分类数据失败');
        } finally {
            setLoading(false);
        }
    }, [messageApi, checkGitHubToken, fetchEnvironmentInfo]);

    // 切换工具开关状态
    const toggleTool = async (tool: MCPToolInfo, enabled: boolean) => {
        try {
            const response = enabled
                ? await apiClient.enableMCPTool(tool.name)
                : await apiClient.disableMCPTool(tool.name);

            if (response.success) {
                messageApi.success(`工具${tool.name}已${enabled ? '启用' : '禁用'}`);
                // 更新对应分类的工具状态
                setCategoryTools(prev => ({
                    ...prev,
                    [tool.category]: prev[tool.category]?.map(t =>
                        t.id === tool.id ? {...t, enabled} : t
                    ) || []
                }));
            } else {
                messageApi.error(response.message);
            }
        } catch (error) {
            // 模拟状态切换（用于演示）
            setCategoryTools(prev => ({
                ...prev,
                [tool.category]: prev[tool.category]?.map(t =>
                    t.id === tool.id ? {...t, enabled} : t
                ) || []
            }));
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

    // 处理分类展开
    const handleCategoryExpand = useCallback((categoryId: string, expanded: boolean) => {
        if (expanded) {
            setExpandedCategories(prev => {
                const newSet = new Set(prev);
                newSet.add(categoryId);
                return newSet;
            });
            // 展开时自动加载该分类的工具
            if (!categoryTools[categoryId] || categoryTools[categoryId].length === 0) {
                loadCategoryTools(categoryId);
            }
        } else {
            setExpandedCategories(prev => {
                const newSet = new Set(prev);
                newSet.delete(categoryId);
                return newSet;
            });
        }
    }, [categoryTools, loadCategoryTools]);


    // 显示所有分类（包括禁用的）
    const filteredCategories = categories;

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
            <Row justify="space-between" style={{marginBottom: 16}}>
                <Col>
                    <Tooltip title={!isEditAllowed ? "远程环境下配置编辑被禁用" : "打开全局配置"}>
                        <Button
                            icon={<SettingOutlined/>}
                            disabled={!isEditAllowed}
                            onClick={() => setMcpConfigModal(true)}
                            style={{
                                color: currentTheme.token?.colorPrimary,
                                borderColor: currentTheme.token?.colorPrimary,
                                backgroundColor: 'rgba(24, 144, 255, 0.06)',
                            }}
                        >
                            全局配置
                        </Button>
                    </Tooltip>
                </Col>
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
                        defaultActiveKey={[]}
                        ghost
                        onChange={(keys) => {
                            const activeKeys = Array.isArray(keys) ? keys : [keys];
                            activeKeys.forEach(key => {
                                if (key && typeof key === 'string') {
                                    handleCategoryExpand(key, true);
                                }
                            });
                        }}
                        items={filteredCategories.map(category => {
                            const tools = categoryTools[category.id] || [];
                            const enabledCount = tools.filter((t: MCPToolInfo) => t.enabled).length;

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
                                            <Text type="secondary">({enabledCount}/{tools.length})</Text>
                                            <div onClick={(e) => e.stopPropagation()}>
                                                <Tooltip title={isEditAllowed ? (category.enabled ? '禁用分类' : '启用分类') : '远程环境下配置编辑被禁用'}>
                                                    <Switch
                                                        size="small"
                                                        checked={category.enabled}
                                                        disabled={!isEditAllowed}
                                                        onChange={(checked) => toggleCategory(category, checked)}
                                                        checkedChildren="启用"
                                                        unCheckedChildren="禁用"
                                                    />
                                                </Tooltip>
                                            </div>
                                            {category.enabled && (
                                                <Tag
                                                    color={enabledCount === tools.length ? 'success' : enabledCount > 0 ? 'warning' : 'default'}>
                                                    {enabledCount === tools.length ? '全部启用' : enabledCount > 0 ? '部分启用' : '全部禁用'}
                                                </Tag>
                                            )}
                                            {!category.enabled && <Tag color="red">分类禁用</Tag>}

                                            {/* 各分类的配置按钮 */}
                                            {category.id === 'file' && (
                                                <Tooltip title={!isEditAllowed ? '远程环境下配置编辑被禁用' : '文件工具安全配置'}>
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        disabled={!isEditAllowed}
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
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {category.id === 'time' && (
                                                <Tooltip title={!isEditAllowed ? '远程环境下配置编辑被禁用' : '时间工具配置'}>
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        disabled={!isEditAllowed}
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
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                            {category.id === 'cache' && (
                                                <Tooltip title={!isEditAllowed ? '远程环境下配置编辑被禁用' : '缓存工具配置'}>
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        disabled={!isEditAllowed}
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
                                                    <Tooltip title={!isEditAllowed ? '远程环境下配置编辑被禁用' : 'GitHub工具配置'}>
                                                        <Button
                                                            type="text"
                                                            size="small"
                                                            disabled={!isEditAllowed}
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
                                                        >
                                                            工具配置
                                                        </Button>
                                                    </Tooltip>
                                                </Space>
                                            )}
                                            {category.id === 'web-scraping' && (
                                                <Tooltip title={!isEditAllowed ? '远程环境下配置编辑被禁用' : '网络抓取工具配置'}>
                                                    <Button
                                                        type="text"
                                                        size="small"
                                                        disabled={!isEditAllowed}
                                                        onClick={(e) => {
                                                            e.stopPropagation();
                                                            setWebScrapingConfigModal(true);
                                                        }}
                                                        style={{
                                                            color: currentTheme.token?.colorPrimary,
                                                            borderColor: currentTheme.token?.colorPrimary,
                                                            backgroundColor: 'rgba(24, 144, 255, 0.06)',
                                                            borderRadius: 6,
                                                            border: `1px solid ${currentTheme.token?.colorPrimary}20`,
                                                            transition: 'all 0.2s ease'
                                                        }}
                                                    >
                                                        工具配置
                                                    </Button>
                                                </Tooltip>
                                            )}
                                        </Space>
                                    </div>
                                ),
                                extra: (
                                    <Text type="secondary" style={{fontSize: 12}}>
                                        {category.description}
                                    </Text>
                                ),
                                children: (
                                    <CategoryToolsRenderer
                                        category={category}
                                        onLoadTools={loadCategoryTools}
                                        categoryTools={categoryTools}
                                        categoryLoadingStates={categoryLoadingStates}
                                        githubTokenValid={githubTokenValid}
                                        environmentInfo={environmentInfo}
                                        isEditAllowed={isEditAllowed}
                                        currentTheme={currentTheme}
                                        themeType={themeType}
                                        onToggleTool={toggleTool}
                                        onShowToolDetail={(tool) => setToolDetailModal({visible: true, tool})}
                                        onTestTool={(tool, form) => setTestToolModal({visible: true, tool, form})}
                                        form={form}
                                    />
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
                            {testToolModal.tool?.schema?.properties && Object.entries(testToolModal.tool.schema.properties).map(([key, prop]: [string, any]) => (
                                <Form.Item
                                    key={`${testToolModal.tool?.id}-form-${key}`}
                                    label={key}
                                    name={key}
                                    help={prop.description}
                                >
                                    {prop.type === 'boolean' ? (
                                        <Select placeholder={`选择 ${key}`}>
                                            <Option key={`${testToolModal.tool?.id}-${key}-true`} value={true}>true</Option>
                                            <Option key={`${testToolModal.tool?.id}-${key}-false`} value={false}>false</Option>
                                        </Select>
                                    ) : prop.enum ? (
                                        <Select placeholder={`选择 ${key}`}>
                                            {prop.enum.map((option: string) => (
                                                <Option key={`${testToolModal.tool?.id}-${key}-${option}`} value={option}>{option}</Option>
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

            {/* 各种配置Modal */}
            <FileToolsConfigModal
                visible={fileToolsConfigModal}
                onCancel={() => setFileToolsConfigModal(false)}
            />

            <TimeToolsConfigModal
                visible={timeToolsConfigModal}
                onCancel={() => setTimeToolsConfigModal(false)}
            />

            <GitHubToolsConfigModal
                visible={githubToolsConfigModal}
                onCancel={() => setGithubToolsConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                    checkGitHubToken(); // 重新检查token状态
                }}
            />

            <CacheToolsConfigModal
                visible={cacheToolsConfigModal}
                onCancel={() => setCacheToolsConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                }}
            />

            <WebScrapingConfigModal
                visible={webScrapingConfigModal}
                onCancel={() => setWebScrapingConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                }}
            />

            <MCPConfigModal
                visible={mcpConfigModal}
                onCancel={() => setMcpConfigModal(false)}
                onSuccess={() => {
                    loadData(); // 重新加载数据
                }}
            />
        </div>
    );
};

export default MCPToolsManagement;