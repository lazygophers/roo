import React, {useState} from 'react';
import {Alert, App, Col, Row, Space, Tooltip, Typography} from 'antd';
import {ModalForm, ProCard, ProFormDigit, ProFormSelect, ProFormSwitch, ProFormText} from '@ant-design/pro-components';
import {GithubOutlined, InfoCircleOutlined, SettingOutlined, ApiOutlined} from '@ant-design/icons';
import {useTheme} from '../../contexts/ThemeContext';

const {Text, Paragraph} = Typography;

interface GitHubToolsConfigModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess?: () => void;
}

interface GitHubToolsConfig {
    api_base_url: string;
    github_token: string;
    default_per_page: number;
    enable_rate_limit_check: boolean;
    enable_auto_retry: boolean;
    max_retry_attempts: number;
    retry_delay_seconds: number;
    timeout_seconds: number;
    enable_request_logging: boolean;
    cache_responses: boolean;
    cache_ttl_seconds: number;
    default_branch: string;
    enable_webhook_verification: boolean;
    enable_enterprise_features: boolean;
    enable_graphql_api: boolean;
    enable_security_scanning: boolean;
    enable_dependabot_integration: boolean;
}

const GitHubToolsConfigModal: React.FC<GitHubToolsConfigModalProps> = ({visible, onCancel, onSuccess}) => {
    const {currentTheme} = useTheme();
    const {message: messageApi} = App.useApp();
    const [loading, setLoading] = useState(false);

    // 保存配置
    const saveConfig = async (values: GitHubToolsConfig) => {
        try {
            setLoading(true);
            const response = await fetch('/api/mcp/categories/github/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({config: values}),
            });

            const data = await response.json();

            if (data.success) {
                messageApi.success('GitHub工具配置已保存');
                onSuccess?.(); // 调用成功回调
            } else {
                messageApi.error(data.message || '保存配置失败');
            }
        } catch (error) {
            messageApi.error('保存配置时发生错误');
            console.error('Save GitHub tools config error:', error);
        } finally {
            setLoading(false);
        }
    };

    // 处理表单提交
    const handleFinish = async (values: GitHubToolsConfig) => {
        await saveConfig(values);
        return true; // 提交成功后关闭Modal
    };

    return (
        <div id="github-tools-modal-container" style={{position: 'relative', zIndex: 'auto'}}>
            <ModalForm<GitHubToolsConfig>
                title={
                    <Space>
                        <GithubOutlined style={{color: currentTheme.token?.colorPrimary}}/>
                        <Text strong style={{color: currentTheme.token?.colorText, fontSize: 16}}>
                            GitHub工具配置
                        </Text>
                    </Space>
                }
                open={visible}
                onOpenChange={(open) => {
                    if (!open) {
                        onCancel();
                    }
                }}
                onFinish={handleFinish}
                request={async () => {
                    try {
                        const response = await fetch('/api/mcp/categories/github/config');
                        const data = await response.json();
                        if (data.success) {
                            return data.data.config;
                        } else {
                            // 返回默认配置
                            return {
                                api_base_url: 'https://api.github.com',
                                github_token: '',
                                default_per_page: 30,
                                enable_rate_limit_check: true,
                                enable_auto_retry: true,
                                max_retry_attempts: 3,
                                retry_delay_seconds: 1,
                                timeout_seconds: 30,
                                enable_request_logging: false,
                                cache_responses: true,
                                cache_ttl_seconds: 300,
                                default_branch: 'master',
                                enable_webhook_verification: true,
                                enable_enterprise_features: false,
                                enable_graphql_api: false,
                                enable_security_scanning: true,
                                enable_dependabot_integration: true
                            };
                        }
                    } catch (error) {
                        console.error('Load GitHub tools config error:', error);
                        // 返回默认配置
                        return {
                            api_base_url: 'https://api.github.com',
                            github_token: '',
                            default_per_page: 30,
                            enable_rate_limit_check: true,
                            enable_auto_retry: true,
                            max_retry_attempts: 3,
                            retry_delay_seconds: 1,
                            timeout_seconds: 30,
                            enable_request_logging: false,
                            cache_responses: true,
                            cache_ttl_seconds: 300,
                            default_branch: 'master',
                            enable_webhook_verification: true,
                            enable_enterprise_features: false,
                            enable_graphql_api: false,
                            enable_security_scanning: true,
                            enable_dependabot_integration: true
                        };
                    }
                }}
                width={900}
                layout="horizontal"
                labelCol={{span: 8}}
                wrapperCol={{span: 16}}
                submitter={{
                    searchConfig: {
                        resetText: '重置',
                        submitText: '保存配置'
                    },
                    submitButtonProps: {
                        loading: loading
                    }
                }}
                modalProps={{
                    destroyOnHidden: true,
                    maskClosable: false,
                    zIndex: 1000,
                    styles: {
                        body: {
                            position: 'relative',
                            zIndex: 1,
                            overflow: 'visible',
                            maxHeight: '80vh',
                            overflowY: 'auto',
                            overflowX: 'visible'
                        }
                    },
                    style: {
                        top: 50
                    }
                }}
            >
                <Alert
                    message="GitHub工具配置"
                    description="配置GitHub工具集的全局参数，这些设置将应用于所有GitHub API相关工具的默认行为。"
                    type="info"
                    showIcon
                    style={{marginBottom: 24}}
                />

                {/* API基础配置 */}
                <ProCard
                    title={
                        <Space>
                            <ApiOutlined/>
                            <Text strong>API基础配置</Text>
                        </Space>
                    }
                    size="small"
                    style={{marginBottom: 16}}
                >
                    <ProFormText
                        name="api_base_url"
                        label={
                            <Space>
                                <Text>API基础URL</Text>
                                <Tooltip title="GitHub API的基础URL，企业版GitHub可以修改此设置">
                                    <InfoCircleOutlined/>
                                </Tooltip>
                            </Space>
                        }
                        rules={[{required: true, message: '请输入API基础URL'}]}
                        placeholder="https://api.github.com"
                    />

                    <ProFormText.Password
                        name="github_token"
                        label={
                            <Space>
                                <Text>GitHub Token</Text>
                                <Tooltip title="GitHub Personal Access Token或GitHub App Token，用于API认证">
                                    <InfoCircleOutlined/>
                                </Tooltip>
                            </Space>
                        }
                        rules={[
                            {required: true, message: '请输入GitHub Token'},
                            {
                                pattern: /^(ghp_|github_pat_)[A-Za-z0-9_]{20,}$/,
                                message: 'GitHub Token格式无效，必须以ghp_或github_pat_开头且长度足够'
                            }
                        ]}
                        placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                        fieldProps={{
                            visibilityToggle: true
                        }}
                    />

                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormDigit
                                name="default_per_page"
                                label={
                                    <Space>
                                        <Text>默认分页大小</Text>
                                        <Tooltip title="API请求返回结果的默认每页数量">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                min={1}
                                max={100}
                                fieldProps={{precision: 0}}
                                rules={[{required: true, message: '请输入分页大小'}]}
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSelect
                                name="default_branch"
                                label={
                                    <Space>
                                        <Text>默认分支</Text>
                                        <Tooltip title="仓库操作的默认分支名称">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                options={[
                                    {label: 'master', value: 'master'},
                                    {label: 'main', value: 'main'},
                                    {label: 'develop', value: 'develop'},
                                    {label: 'dev', value: 'dev'}
                                ]}
                                rules={[{required: true, message: '请选择默认分支'}]}
                            />
                        </Col>
                    </Row>
                </ProCard>

                {/* 重试和错误处理 */}
                <ProCard
                    title={
                        <Space>
                            <SettingOutlined/>
                            <Text strong>重试和错误处理</Text>
                        </Space>
                    }
                    size="small"
                    style={{marginBottom: 16}}
                    collapsible
                    defaultCollapsed={false}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_rate_limit_check"
                                label={
                                    <Space>
                                        <Text>启用速率限制检查</Text>
                                        <Tooltip title="自动检查GitHub API速率限制并在必要时等待">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_auto_retry"
                                label={
                                    <Space>
                                        <Text>启用自动重试</Text>
                                        <Tooltip title="API请求失败时自动重试">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={8}>
                            <ProFormDigit
                                name="max_retry_attempts"
                                label={
                                    <Space>
                                        <Text>最大重试次数</Text>
                                        <Tooltip title="API请求失败时的最大重试次数">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                min={1}
                                max={10}
                                fieldProps={{precision: 0}}
                            />
                        </Col>
                        <Col span={8}>
                            <ProFormDigit
                                name="retry_delay_seconds"
                                label={
                                    <Space>
                                        <Text>重试延迟（秒）</Text>
                                        <Tooltip title="重试请求之间的延迟时间">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                min={0.1}
                                max={60}
                                fieldProps={{precision: 1}}
                            />
                        </Col>
                        <Col span={8}>
                            <ProFormDigit
                                name="timeout_seconds"
                                label={
                                    <Space>
                                        <Text>请求超时（秒）</Text>
                                        <Tooltip title="API请求的超时时间">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                min={5}
                                max={120}
                                fieldProps={{precision: 0}}
                            />
                        </Col>
                    </Row>
                </ProCard>

                {/* 缓存和性能 */}
                <ProCard
                    title={
                        <Space>
                            <SettingOutlined/>
                            <Text strong>缓存和性能</Text>
                        </Space>
                    }
                    size="small"
                    style={{marginBottom: 16}}
                    collapsible
                    defaultCollapsed={false}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="cache_responses"
                                label={
                                    <Space>
                                        <Text>启用响应缓存</Text>
                                        <Tooltip title="缓存API响应以提高性能">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormDigit
                                name="cache_ttl_seconds"
                                label={
                                    <Space>
                                        <Text>缓存过期时间（秒）</Text>
                                        <Tooltip title="缓存数据的生存时间">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                                min={60}
                                max={3600}
                                fieldProps={{precision: 0}}
                            />
                        </Col>
                    </Row>
                </ProCard>

                {/* 高级功能 */}
                <ProCard
                    title={
                        <Space>
                            <SettingOutlined/>
                            <Text strong>高级功能</Text>
                        </Space>
                    }
                    size="small"
                    style={{marginBottom: 16}}
                    collapsible
                    defaultCollapsed={true}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_request_logging"
                                label={
                                    <Space>
                                        <Text>启用请求日志</Text>
                                        <Tooltip title="记录所有API请求的详细日志">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_webhook_verification"
                                label={
                                    <Space>
                                        <Text>启用Webhook验证</Text>
                                        <Tooltip title="验证来自GitHub的Webhook请求">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_enterprise_features"
                                label={
                                    <Space>
                                        <Text>启用企业功能</Text>
                                        <Tooltip title="启用GitHub Enterprise相关功能">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_graphql_api"
                                label={
                                    <Space>
                                        <Text>启用GraphQL API</Text>
                                        <Tooltip title="使用GitHub GraphQL API替代REST API">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                    </Row>

                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_security_scanning"
                                label={
                                    <Space>
                                        <Text>启用安全扫描</Text>
                                        <Tooltip title="启用代码安全扫描功能">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_dependabot_integration"
                                label={
                                    <Space>
                                        <Text>启用Dependabot集成</Text>
                                        <Tooltip title="启用Dependabot依赖项管理功能">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                    </Row>
                </ProCard>

                <Alert
                    message="配置说明"
                    description={
                        <div>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>API基础URL</Text>: 企业版GitHub用户可以修改为自己的企业GitHub地址
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>GitHub Token</Text>: <Text type="danger">必填</Text> - 用于API认证的Personal Access Token，必须以ghp_或github_pat_开头
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>速率限制</Text>: 启用后会自动检查GitHub API配额，避免超出限制
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>自动重试</Text>: 网络错误或临时故障时自动重试请求
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>响应缓存</Text>: 缓存API响应可以显著提高频繁操作的性能
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>高级功能</Text>: 包括企业功能、GraphQL API、安全扫描等可选功能
                            </Paragraph>
                        </div>
                    }
                    type="info"
                    showIcon
                    style={{fontSize: 12, marginTop: 16}}
                />
            </ModalForm>
        </div>
    );
};

export default GitHubToolsConfigModal;