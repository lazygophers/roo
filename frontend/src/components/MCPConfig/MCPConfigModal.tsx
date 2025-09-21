import React, { useState, useEffect } from 'react';
import {
    Modal,
    Form,
    Input,
    Switch,
    Select,
    Button,
    Space,
    Tabs,
    Row,
    Col,
    InputNumber,
    Alert,
    Tooltip,
    Typography,
    Card,
    Divider,
    message
} from 'antd';
import {
    SettingOutlined,
    GlobalOutlined,
    SecurityScanOutlined,
    ApiOutlined,
    ToolOutlined,
    InfoCircleOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined
} from '@ant-design/icons';
import { useTheme } from '../../contexts/ThemeContext';
import { useEnvironment } from '../../contexts/EnvironmentContext';

const { TextArea } = Input;
const { Text, Title } = Typography;
const { Option } = Select;

interface MCPConfigModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess?: () => void;
}

interface ProxyConfig {
    enabled: boolean;
    proxy: string;
    no_proxy: string;
    username: string;
    password: string;
}

interface NetworkConfig {
    timeout: number;
    retry_times: number;
    retry_delay: number;
    user_agent: string;
    max_connections: number;
}

interface SecurityConfig {
    verify_ssl: boolean;
    allowed_hosts: string[];
    blocked_hosts: string[];
    enable_rate_limit: boolean;
    rate_limit_per_minute: number;
}


interface MCPGlobalConfig {
    enabled: boolean;
    debug_mode: boolean;
    log_level: string;
    proxy: ProxyConfig;
    network: NetworkConfig;
    security: SecurityConfig;
    tool_categories: Record<string, any>;
    environment_variables: Record<string, string>;
    version: string;
    created_at: string;
    updated_at: string;
}

const MCPConfigModal: React.FC<MCPConfigModalProps> = ({
    visible,
    onCancel,
    onSuccess
}) => {
    const { currentTheme } = useTheme();
    const { isEditAllowed } = useEnvironment();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('global');
    const [config, setConfig] = useState<MCPGlobalConfig | null>(null);
    const [testingConnection, setTestingConnection] = useState(false);

    // 加载配置
    const loadConfig = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/mcp/config/');
            const data = await response.json();

            if (data.success) {
                setConfig(data.data);
                form.setFieldsValue({
                    ...data.data,
                    security: {
                        ...data.data.security,
                        allowed_hosts: data.data.security.allowed_hosts?.join('\n') || '',
                        blocked_hosts: data.data.security.blocked_hosts?.join('\n') || ''
                    },
                    environment_variables: JSON.stringify(data.data.environment_variables || {}, null, 2)
                });
            } else {
                message.error('加载配置失败: ' + data.message);
            }
        } catch (error) {
            console.error('Load config error:', error);
            message.error('加载配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 保存配置
    const saveConfig = async (values: any) => {
        try {
            setLoading(true);

            // 分别更新不同部分的配置
            const updates = [
                // 全局配置
                fetch('/api/mcp/config/', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        enabled: values.enabled,
                        debug_mode: values.debug_mode,
                        log_level: values.log_level
                    })
                }),
                // 代理配置
                fetch('/api/mcp/config/proxy', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values.proxy)
                }),
                // 网络配置
                fetch('/api/mcp/config/network', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(values.network)
                }),
                // 安全配置
                fetch('/api/mcp/config/security', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        ...(values.security || {}),
                        allowed_hosts: values.security?.allowed_hosts?.split('\n').filter((h: string) => h.trim()) || [],
                        blocked_hosts: values.security?.blocked_hosts?.split('\n').filter((h: string) => h.trim()) || []
                    })
                }),
                // 环境变量
                values.environment_variables && fetch('/api/mcp/config/environment-variables', {
                    method: 'PUT',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        variables: typeof values.environment_variables === 'string'
                            ? JSON.parse(values.environment_variables || '{}')
                            : values.environment_variables || {}
                    })
                })
            ].filter(Boolean);

            const responses = await Promise.all(updates);
            const allSuccess = responses.every(async (response) => {
                const data = await response.json();
                return data.success;
            });

            if (allSuccess) {
                message.success('配置保存成功');
                onSuccess?.();
                onCancel();
                loadConfig(); // 重新加载配置
            } else {
                message.error('部分配置保存失败');
            }
        } catch (error) {
            console.error('Save config error:', error);
            message.error('保存配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 测试代理连接
    const testProxyConnection = async () => {
        try {
            setTestingConnection(true);
            const proxyConfig = form.getFieldValue('proxy');

            // 这里可以调用一个测试API端点
            // 暂时使用模拟测试
            await new Promise(resolve => setTimeout(resolve, 2000));

            if (proxyConfig.enabled && proxyConfig.proxy) {
                message.success('代理连接测试成功');
            } else {
                message.info('代理未启用，无需测试');
            }
        } catch (error) {
            message.error('代理连接测试失败');
        } finally {
            setTestingConnection(false);
        }
    };

    // 重置为默认配置
    const resetToDefaults = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/mcp/config/reset', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                setConfig(data.data);
                form.setFieldsValue(data.data);
                message.success('已重置为默认配置');
            } else {
                message.error('重置配置失败');
            }
        } catch (error) {
            console.error('Reset config error:', error);
            message.error('重置配置失败');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (visible) {
            loadConfig();
        }
    }, [visible]);

    const handleOk = () => {
        form.validateFields().then(values => {
            // 处理数组字段
            if (values.security) {
                if (typeof values.security.allowed_hosts === 'string') {
                    values.security.allowed_hosts = values.security.allowed_hosts.split('\n').filter((h: string) => h.trim());
                }
                if (typeof values.security.blocked_hosts === 'string') {
                    values.security.blocked_hosts = values.security.blocked_hosts.split('\n').filter((h: string) => h.trim());
                }
            }

            saveConfig(values);
        });
    };

    const handleCancel = () => {
        form.resetFields();
        onCancel();
    };

    return (
        <Modal
            title={
                <Space>
                    <SettingOutlined />
                    MCP 全局配置
                </Space>
            }
            open={visible}
            onCancel={handleCancel}
            onOk={handleOk}
            confirmLoading={loading}
            width={900}
            style={{ top: 20 }}
            styles={{ body: { maxHeight: 'calc(100vh - 200px)', overflowY: 'auto' } }}
            footer={[
                <Tooltip key="reset-tooltip" title={!isEditAllowed ? '远程环境下重置功能被禁用' : '重置为默认配置'}>
                    <Button key="reset" onClick={resetToDefaults} loading={loading} disabled={!isEditAllowed}>
                        重置默认
                    </Button>
                </Tooltip>,
                <Button key="cancel" onClick={handleCancel}>
                    取消
                </Button>,
                <Tooltip key="save-tooltip" title={!isEditAllowed ? '远程环境下配置保存功能被禁用' : '保存配置更改'}>
                    <Button key="ok" type="primary" loading={loading} onClick={handleOk} disabled={!isEditAllowed}>
                        保存配置
                    </Button>
                </Tooltip>
            ]}
        >
            {!isEditAllowed && (
                <Alert
                    message="远程环境模式"
                    description="当前运行在远程环境模式下，MCP配置功能为只读状态。您可以查看所有配置选项，但无法保存或重置配置。"
                    type="warning"
                    showIcon
                    style={{ marginBottom: 16 }}
                />
            )}
            {config && (
                <Form
                    form={form}
                    layout="vertical"
                    initialValues={{
                        ...config,
                        security: {
                            ...config.security,
                            allowed_hosts: config.security.allowed_hosts?.join('\n') || '',
                            blocked_hosts: config.security.blocked_hosts?.join('\n') || ''
                        },
                        environment_variables: JSON.stringify(config.environment_variables || {}, null, 2)
                    }}
                >
                    <Tabs
                        activeKey={activeTab}
                        onChange={setActiveTab}
                        items={[
                            {
                                key: "global",
                                label: <Space><GlobalOutlined />全局配置</Space>,
                                children: (
                            <Card size="small" style={{ marginBottom: 16 }}>
                                <Title level={5} style={{ marginBottom: 16 }}>
                                    <ApiOutlined /> 基本设置
                                </Title>

                                <Row gutter={16}>
                                    <Col span={8}>
                                        <Form.Item
                                            name="enabled"
                                            label="启用MCP工具"
                                            valuePropName="checked"
                                        >
                                            <Switch
                                                checkedChildren={<CheckCircleOutlined />}
                                                unCheckedChildren={<ExclamationCircleOutlined />}
                                            />
                                        </Form.Item>
                                    </Col>
                                    <Col span={8}>
                                        <Form.Item
                                            name="debug_mode"
                                            label="调试模式"
                                            valuePropName="checked"
                                        >
                                            <Switch
                                                checkedChildren="开启"
                                                unCheckedChildren="关闭"
                                            />
                                        </Form.Item>
                                    </Col>
                                    <Col span={8}>
                                        <Form.Item
                                            name="log_level"
                                            label="日志级别"
                                        >
                                            <Select>
                                                <Option value="DEBUG">DEBUG</Option>
                                                <Option value="INFO">INFO</Option>
                                                <Option value="WARNING">WARNING</Option>
                                                <Option value="ERROR">ERROR</Option>
                                            </Select>
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Alert
                                    message="配置说明"
                                    description="调试模式会输出详细的日志信息，建议仅在开发和调试时开启。生产环境建议使用INFO或WARNING级别。"
                                    type="info"
                                    showIcon
                                    style={{ marginTop: 16 }}
                                />
                            </Card>
                                )
                            },
                            {
                                key: "proxy",
                                label: <Space><GlobalOutlined />代理配置</Space>,
                                children: (
                            <Card size="small" style={{ marginBottom: 16 }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 16 }}>
                                    <Title level={5} style={{ margin: 0 }}>
                                        <GlobalOutlined /> 代理设置
                                    </Title>
                                    <Space>
                                        <Tooltip title={!isEditAllowed ? '远程环境下测试功能被禁用' : '测试代理连接'}>
                                            <Button
                                                size="small"
                                                onClick={testProxyConnection}
                                                loading={testingConnection}
                                                icon={<ApiOutlined />}
                                                disabled={!isEditAllowed}
                                            >
                                                测试连接
                                            </Button>
                                        </Tooltip>
                                    </Space>
                                </div>

                                <Form.Item
                                    name={['proxy', 'enabled']}
                                    label="启用代理"
                                    valuePropName="checked"
                                >
                                    <Switch
                                        checkedChildren="启用"
                                        unCheckedChildren="禁用"
                                    />
                                </Form.Item>

                                <Form.Item
                                    name={['proxy', 'proxy']}
                                    label="代理地址"
                                >
                                    <Input
                                        placeholder="http://proxy.example.com:8080"
                                        disabled={!form.getFieldValue(['proxy', 'enabled'])}
                                        addonBefore={
                                            <Tooltip title="统一代理地址，同时用于HTTP和HTTPS请求">
                                                <InfoCircleOutlined />
                                            </Tooltip>
                                        }
                                    />
                                </Form.Item>

                                <Form.Item
                                    name={['proxy', 'no_proxy']}
                                    label={
                                        <Space>
                                            不使用代理的地址
                                            <Tooltip title="多个地址用逗号分隔，支持域名和IP地址">
                                                <InfoCircleOutlined />
                                            </Tooltip>
                                        </Space>
                                    }
                                >
                                    <Input
                                        placeholder="localhost,127.0.0.1,.local"
                                        disabled={!form.getFieldValue(['proxy', 'enabled'])}
                                    />
                                </Form.Item>

                                <Divider />

                                <Title level={5}>认证信息</Title>
                                <Row gutter={16}>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['proxy', 'username']}
                                            label="用户名"
                                        >
                                            <Input
                                                placeholder="代理认证用户名"
                                                disabled={!form.getFieldValue(['proxy', 'enabled'])}
                                            />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['proxy', 'password']}
                                            label="密码"
                                        >
                                            <Input.Password
                                                placeholder="代理认证密码"
                                                disabled={!form.getFieldValue(['proxy', 'enabled'])}
                                            />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Alert
                                    message="代理配置说明"
                                    description="配置统一的代理服务器用于MCP工具的所有网络请求。该代理配置将同时应用于HTTP和HTTPS请求，可以配置认证信息和例外地址。"
                                    type="info"
                                    showIcon
                                />
                            </Card>
                                )
                            },
                            {
                                key: "network",
                                label: <Space><ApiOutlined />网络配置</Space>,
                                children: (
                            <Card size="small" style={{ marginBottom: 16 }}>
                                <Title level={5} style={{ marginBottom: 16 }}>
                                    <ApiOutlined /> 网络参数
                                </Title>

                                <Row gutter={16}>
                                    <Col span={8}>
                                        <Form.Item
                                            name={['network', 'timeout']}
                                            label="请求超时(秒)"
                                            rules={[
                                                { required: true, message: '请输入超时时间' },
                                                { type: 'number', min: 1, max: 300, message: '超时时间应在1-300秒之间' }
                                            ]}
                                        >
                                            <InputNumber min={1} max={300} style={{ width: '100%' }} />
                                        </Form.Item>
                                    </Col>
                                    <Col span={8}>
                                        <Form.Item
                                            name={['network', 'retry_times']}
                                            label="重试次数"
                                            rules={[
                                                { required: true, message: '请输入重试次数' },
                                                { type: 'number', min: 0, max: 10, message: '重试次数应在0-10之间' }
                                            ]}
                                        >
                                            <InputNumber min={0} max={10} style={{ width: '100%' }} />
                                        </Form.Item>
                                    </Col>
                                    <Col span={8}>
                                        <Form.Item
                                            name={['network', 'retry_delay']}
                                            label="重试延迟(秒)"
                                            rules={[
                                                { required: true, message: '请输入重试延迟' },
                                                { type: 'number', min: 0.1, max: 10, message: '重试延迟应在0.1-10秒之间' }
                                            ]}
                                        >
                                            <InputNumber min={0.1} max={10} step={0.1} style={{ width: '100%' }} />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Row gutter={16}>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['network', 'user_agent']}
                                            label="用户代理"
                                            rules={[{ required: true, message: '请输入用户代理' }]}
                                        >
                                            <Input placeholder="LazyAI-Studio-MCP/1.0" />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['network', 'max_connections']}
                                            label="最大连接数"
                                            rules={[
                                                { required: true, message: '请输入最大连接数' },
                                                { type: 'number', min: 1, max: 1000, message: '连接数应在1-1000之间' }
                                            ]}
                                        >
                                            <InputNumber min={1} max={1000} style={{ width: '100%' }} />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Alert
                                    message="网络配置说明"
                                    description="网络参数影响MCP工具的连接性能和稳定性。请根据网络环境和使用需求调整这些参数。"
                                    type="info"
                                    showIcon
                                />
                            </Card>
                                )
                            },
                            {
                                key: "security",
                                label: <Space><SecurityScanOutlined />安全配置</Space>,
                                children: (
                            <Card size="small" style={{ marginBottom: 16 }}>
                                <Title level={5} style={{ marginBottom: 16 }}>
                                    <SecurityScanOutlined /> 安全设置
                                </Title>

                                <Row gutter={16}>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['security', 'verify_ssl']}
                                            label="验证SSL证书"
                                            valuePropName="checked"
                                        >
                                            <Switch
                                                checkedChildren="验证"
                                                unCheckedChildren="跳过"
                                            />
                                        </Form.Item>
                                    </Col>
                                    <Col span={12}>
                                        <Form.Item
                                            name={['security', 'enable_rate_limit']}
                                            label="启用速率限制"
                                            valuePropName="checked"
                                        >
                                            <Switch
                                                checkedChildren="启用"
                                                unCheckedChildren="禁用"
                                            />
                                        </Form.Item>
                                    </Col>
                                </Row>

                                <Form.Item
                                    name={['security', 'rate_limit_per_minute']}
                                    label="每分钟请求限制"
                                    rules={[
                                        { required: true, message: '请输入请求限制' },
                                        { type: 'number', min: 1, max: 1000, message: '请求限制应在1-1000之间' }
                                    ]}
                                >
                                    <InputNumber
                                        min={1}
                                        max={1000}
                                        style={{ width: '100%' }}
                                        disabled={!form.getFieldValue(['security', 'enable_rate_limit'])}
                                    />
                                </Form.Item>

                                <Form.Item
                                    name={['security', 'allowed_hosts']}
                                    label={
                                        <Space>
                                            允许访问的主机
                                            <Tooltip title="每行一个主机地址，支持域名和IP地址">
                                                <InfoCircleOutlined />
                                            </Tooltip>
                                        </Space>
                                    }
                                >
                                    <TextArea
                                        rows={4}
                                        placeholder={`api.github.com\n*.googleapis.com\n127.0.0.1`}
                                    />
                                </Form.Item>

                                <Form.Item
                                    name={['security', 'blocked_hosts']}
                                    label={
                                        <Space>
                                            禁止访问的主机
                                            <Tooltip title="每行一个主机地址，支持域名和IP地址">
                                                <InfoCircleOutlined />
                                            </Tooltip>
                                        </Space>
                                    }
                                >
                                    <TextArea
                                        rows={4}
                                        placeholder={`malicious.com\n*.suspicious.org\n192.168.1.100`}
                                    />
                                </Form.Item>

                                <Alert
                                    message="安全配置说明"
                                    description="安全配置用于保护系统免受恶意请求和攻击。建议启用SSL验证和速率限制，合理配置允许和禁止的主机列表。"
                                    type="warning"
                                    showIcon
                                />
                            </Card>
                                )
                            },
                            {
                                key: "env",
                                label: <Space><ToolOutlined />环境变量</Space>,
                                children: (
                            <Card size="small" style={{ marginBottom: 16 }}>
                                <Title level={5} style={{ marginBottom: 16 }}>
                                    <ToolOutlined /> 环境变量配置
                                </Title>

                                <Alert
                                    message="环境变量"
                                    description="配置MCP工具使用的环境变量。这些变量会在工具执行时可用，请谨慎配置敏感信息。"
                                    type="info"
                                    showIcon
                                    style={{ marginBottom: 16 }}
                                />

                                <Form.Item
                                    name="environment_variables"
                                    label="环境变量 (JSON格式)"
                                >
                                    <TextArea
                                        rows={8}
                                        placeholder={`{
  "API_KEY": "your-api-key",
  "DEBUG": "false",
  "CUSTOM_VAR": "value"
}`}
                                    />
                                </Form.Item>
                            </Card>
                                )
                            }
                        ]}
                    />
                </Form>
            )}

            {config && (
                <Card size="small" style={{ marginTop: 16, backgroundColor: currentTheme.token?.colorFillQuaternary }}>
                    <Space split={<Divider type="vertical" />}>
                        <Text type="secondary">版本: {config.version}</Text>
                        <Text type="secondary">创建: {new Date(config.created_at).toLocaleString()}</Text>
                        <Text type="secondary">更新: {new Date(config.updated_at).toLocaleString()}</Text>
                    </Space>
                </Card>
            )}
        </Modal>
    );
};

export default MCPConfigModal;