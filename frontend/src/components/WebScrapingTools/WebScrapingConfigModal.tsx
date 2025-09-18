import React, { useState, useEffect } from 'react';
import {
    Modal,
    Form,
    Input,
    InputNumber,
    Switch,
    Button,
    Space,
    Tabs,
    Row,
    Col,
    Alert,
    Tooltip,
    Typography,
    Card,
    Divider,
    message,
    Tag,
    Badge
} from 'antd';
import {
    GlobalOutlined,
    SettingOutlined,
    ApiOutlined,
    SecurityScanOutlined,
    InfoCircleOutlined,
    CheckCircleOutlined,
    ExclamationCircleOutlined,
    CloudServerOutlined,
    ReloadOutlined
} from '@ant-design/icons';
import { useTheme } from '../../contexts/ThemeContext';

const { TextArea } = Input;
const { Text, Title } = Typography;

interface WebScrapingConfigModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess?: () => void;
}

interface WebScrapingConfig {
    enabled: boolean;
    user_agent: string;
    timeout: number;
    max_retries: number;
    retry_delay: number;
    max_file_size: number;
    allowed_content_types: string[];
    follow_redirects: boolean;
    verify_ssl: boolean;
}

interface MCPGlobalConfig {
    proxy_enabled: boolean;
    global_timeout: number;
    global_user_agent: string;
    ssl_verification: boolean;
}

interface ConfigResponse {
    config: WebScrapingConfig;
    mcp_global_config: MCPGlobalConfig;
}

const WebScrapingConfigModal: React.FC<WebScrapingConfigModalProps> = ({
    visible,
    onCancel,
    onSuccess
}) => {
    const { currentTheme } = useTheme();
    const [form] = Form.useForm();
    const [loading, setLoading] = useState(false);
    const [activeTab, setActiveTab] = useState('basic');
    const [config, setConfig] = useState<ConfigResponse | null>(null);
    const [testing, setTesting] = useState(false);

    // 加载配置
    const loadConfig = async () => {
        try {
            setLoading(true);
            const response = await fetch('/api/fetch/config');
            const data = await response.json();

            if (data.success) {
                setConfig(data.data);
                form.setFieldsValue({
                    ...data.data.config,
                    allowed_content_types: data.data.config.allowed_content_types?.join('\n') || '',
                    max_file_size_mb: Math.round(data.data.config.max_file_size / (1024 * 1024))
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

            // 处理数据格式
            const configData = {
                ...values,
                max_file_size: values.max_file_size_mb * 1024 * 1024,
                allowed_content_types: values.allowed_content_types?.split('\n').filter((t: string) => t.trim()) || []
            };

            delete configData.max_file_size_mb;
            delete configData.allowed_content_types;

            const response = await fetch('/api/fetch/config', {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(configData)
            });

            const data = await response.json();

            if (data.success) {
                message.success('配置保存成功');
                onSuccess?.();
                onCancel();
            } else {
                message.error('配置保存失败: ' + data.message);
            }
        } catch (error) {
            console.error('Save config error:', error);
            message.error('保存配置失败');
        } finally {
            setLoading(false);
        }
    };

    // 测试连接
    const testConnection = async () => {
        try {
            setTesting(true);
            const response = await fetch('/api/fetch/test-connection', {
                method: 'POST'
            });
            const data = await response.json();

            if (data.success) {
                const results = data.data.test_results;
                const successCount = results.filter((r: any) => r.status === 'success').length;

                if (successCount === results.length) {
                    message.success(`连接测试成功！所有 ${successCount} 个测试站点均可访问`);
                } else if (successCount > 0) {
                    message.warning(`部分连接成功：${successCount}/${results.length} 个站点可访问`);
                } else {
                    message.error('连接测试失败：无法访问任何测试站点');
                }
            } else {
                message.error('连接测试失败');
            }
        } catch (error) {
            console.error('Connection test error:', error);
            message.error('连接测试失败');
        } finally {
            setTesting(false);
        }
    };

    useEffect(() => {
        if (visible) {
            loadConfig();
        }
    }, [visible]);

    const handleOk = () => {
        form.validateFields().then(values => {
            saveConfig(values);
        });
    };

    const handleCancel = () => {
        form.resetFields();
        onCancel();
    };

    const renderStatusBadge = (enabled: boolean, label: string) => (
        <Badge
            status={enabled ? "success" : "error"}
            text={
                <Text type={enabled ? "success" : "secondary"}>
                    {label}: {enabled ? "启用" : "禁用"}
                </Text>
            }
        />
    );

    const tabItems = [
        {
            key: 'basic',
            label: <Space><SettingOutlined />基本配置</Space>,
            children: (
                <Card size="small" style={{ marginBottom: 16 }}>
                    <Title level={5} style={{ marginBottom: 16 }}>
                        <ApiOutlined /> 网络请求设置
                    </Title>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="user_agent"
                                label="用户代理 (User-Agent)"
                                rules={[{ required: true, message: '请输入用户代理' }]}
                            >
                                <Input placeholder="LazyAI-Studio-WebScraper/1.0" />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="timeout"
                                label="请求超时(秒)"
                                rules={[
                                    { required: true, message: '请输入超时时间' },
                                    { type: 'number', min: 1, max: 300, message: '超时时间应在1-300秒之间' }
                                ]}
                            >
                                <InputNumber min={1} max={300} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col span={6}>
                            <Form.Item
                                name="max_retries"
                                label="最大重试次数"
                                rules={[
                                    { required: true, message: '请输入重试次数' },
                                    { type: 'number', min: 0, max: 10, message: '重试次数应在0-10之间' }
                                ]}
                            >
                                <InputNumber min={0} max={10} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={8}>
                            <Form.Item
                                name="retry_delay"
                                label="重试延迟(秒)"
                                rules={[
                                    { required: true, message: '请输入重试延迟' },
                                    { type: 'number', min: 0.1, max: 10, message: '重试延迟应在0.1-10秒之间' }
                                ]}
                            >
                                <InputNumber min={0.1} max={10} step={0.1} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="max_file_size_mb"
                                label="最大文件大小(MB)"
                                rules={[
                                    { required: true, message: '请输入文件大小限制' },
                                    { type: 'number', min: 1, max: 1024, message: '文件大小应在1-1024MB之间' }
                                ]}
                            >
                                <InputNumber min={1} max={1024} style={{ width: '100%' }} />
                            </Form.Item>
                        </Col>
                        <Col span={8}>
                            <Form.Item
                                name="follow_redirects"
                                label="跟随重定向"
                                valuePropName="checked"
                            >
                                <Switch
                                    checkedChildren="启用"
                                    unCheckedChildren="禁用"
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Alert
                        message="工具集配置优先级说明"
                        description="这些配置项优先级高于全局MCP配置。如果留空，将使用全局MCP配置中的对应值。"
                        type="info"
                        showIcon
                        style={{ marginTop: 16 }}
                    />
                </Card>
            )
        },
        {
            key: 'security',
            label: <Space><SecurityScanOutlined />安全设置</Space>,
            children: (
                <Card size="small" style={{ marginBottom: 16 }}>
                    <Title level={5} style={{ marginBottom: 16 }}>
                        <SecurityScanOutlined /> 安全配置
                    </Title>

                    <Row gutter={16}>
                        <Col span={12}>
                            <Form.Item
                                name="verify_ssl"
                                label="验证SSL证书"
                                valuePropName="checked"
                            >
                                <Switch
                                    checkedChildren={<CheckCircleOutlined />}
                                    unCheckedChildren={<ExclamationCircleOutlined />}
                                />
                            </Form.Item>
                        </Col>
                    </Row>

                    <Form.Item
                        name="allowed_content_types"
                        label={
                            <Space>
                                允许的内容类型
                                <Tooltip title="每行一个内容类型，支持通配符">
                                    <InfoCircleOutlined />
                                </Tooltip>
                            </Space>
                        }
                    >
                        <TextArea
                            rows={6}
                            placeholder={`text/html
text/plain
application/json
application/xml
text/xml
text/css
text/javascript`}
                        />
                    </Form.Item>

                    <Alert
                        message="安全提示"
                        description="建议启用SSL证书验证以确保连接安全。只允许必要的内容类型可以提高安全性。"
                        type="warning"
                        showIcon
                    />
                </Card>
            )
        },
        {
            key: 'global',
            label: <Space><GlobalOutlined />全局配置</Space>,
            children: config && (
                <Card size="small" style={{ marginBottom: 16 }}>
                    <Title level={5} style={{ marginBottom: 16 }}>
                        <GlobalOutlined /> MCP全局配置状态
                    </Title>

                    <Row gutter={16}>
                        <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                                {renderStatusBadge(config.mcp_global_config?.proxy_enabled, "全局代理")}
                            </div>
                            <div style={{ marginBottom: 8 }}>
                                {renderStatusBadge(config.mcp_global_config?.ssl_verification, "SSL验证")}
                            </div>
                        </Col>
                        <Col span={12}>
                            <div style={{ marginBottom: 8 }}>
                                <Text type="secondary">全局超时: </Text>
                                <Tag>{config.mcp_global_config?.global_timeout}秒</Tag>
                            </div>
                            <div style={{ marginBottom: 8 }}>
                                <Text type="secondary">全局UA: </Text>
                                <Text code style={{ fontSize: '12px' }}>
                                    {config.mcp_global_config?.global_user_agent}
                                </Text>
                            </div>
                        </Col>
                    </Row>

                    <Divider />

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Text type="secondary">网络连接测试</Text>
                        <Button
                            type="default"
                            icon={<CloudServerOutlined />}
                            loading={testing}
                            onClick={testConnection}
                        >
                            测试连接
                        </Button>
                    </div>

                    <Alert
                        message="配置说明"
                        description="网络抓取工具会遵循全局MCP配置中的代理设置。工具集级别的配置（如UA、超时时间）优先级更高。"
                        type="info"
                        showIcon
                        style={{ marginTop: 16 }}
                    />
                </Card>
            )
        }
    ];

    return (
        <Modal
            title={
                <Space>
                    <CloudServerOutlined />
                    网络抓取工具配置
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
                <Button key="test" icon={<CloudServerOutlined />} loading={testing} onClick={testConnection}>
                    测试连接
                </Button>,
                <Button key="cancel" onClick={handleCancel}>
                    取消
                </Button>,
                <Button key="ok" type="primary" loading={loading} onClick={handleOk}>
                    保存配置
                </Button>
            ]}
        >
            {config && (
                <Form
                    form={form}
                    layout="vertical"
                    initialValues={{
                        ...config.config,
                        allowed_content_types: config.config.allowed_content_types?.join('\n') || '',
                        max_file_size_mb: Math.round(config.config.max_file_size / (1024 * 1024))
                    }}
                >
                    <Tabs
                        activeKey={activeTab}
                        onChange={setActiveTab}
                        items={tabItems}
                    />
                </Form>
            )}

            {config && (
                <Card size="small" style={{ marginTop: 16, backgroundColor: currentTheme.token?.colorFillQuaternary }}>
                    <Space split={<Divider type="vertical" />}>
                        <Text type="secondary">工具状态: </Text>
                        <Badge
                            status={config.config.enabled ? "success" : "error"}
                            text={config.config.enabled ? "启用" : "禁用"}
                        />
                        <Text type="secondary">代理状态: </Text>
                        <Badge
                            status={config.mcp_global_config?.proxy_enabled ? "success" : "default"}
                            text={config.mcp_global_config?.proxy_enabled ? "已配置" : "未配置"}
                        />
                    </Space>
                </Card>
            )}
        </Modal>
    );
};

export default WebScrapingConfigModal;