/**
 * GitHub API 工具配置模态框
 * 支持配置 GitHub Token、API 端点、请求超时等参数
 */

import React, { useState } from 'react';
import { Alert, Space, Tooltip, Typography, Input } from 'antd';
import { ModalForm, ProCard, ProFormDigit, ProFormText, ProFormSwitch, ProFormTextArea } from '@ant-design/pro-components';
import { GithubOutlined, KeyOutlined, GlobalOutlined, InfoCircleOutlined, SettingOutlined, ApiOutlined } from '@ant-design/icons';
import { apiClient } from '../../api';
import { useTheme } from '../../contexts/ThemeContext';

const { Text, Paragraph } = Typography;

export interface GitHubToolsConfig {
    token: string;
    base_url: string;
    request_timeout: number;
    enable_rate_limit_handling: boolean;
    default_per_page: number;
    user_agent: string;
    verify_ssl: boolean;
    auto_retry: boolean;
    max_retries: number;
}

interface GitHubToolsConfigModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess?: () => void;
}

const GitHubToolsConfigModal: React.FC<GitHubToolsConfigModalProps> = ({
    visible,
    onCancel,
    onSuccess
}) => {
    const { currentTheme } = useTheme();
    const [loading, setLoading] = useState(false);

    // 请求初始配置数据
    const handleRequest = async () => {
        try {
            const response = await apiClient.getCategoryConfig('github');
            if (response.success && response.data) {
                return response.data;
            }
            return {
                token: '',
                base_url: 'https://api.github.com',
                request_timeout: 30,
                enable_rate_limit_handling: true,
                default_per_page: 30,
                user_agent: 'LazyAI-Studio-GitHub-Tools/1.0',
                verify_ssl: true,
                auto_retry: true,
                max_retries: 3
            };
        } catch (error) {
            console.error('Failed to load GitHub config:', error);
            return {
                token: '',
                base_url: 'https://api.github.com',
                request_timeout: 30,
                enable_rate_limit_handling: true,
                default_per_page: 30,
                user_agent: 'LazyAI-Studio-GitHub-Tools/1.0',
                verify_ssl: true,
                auto_retry: true,
                max_retries: 3
            };
        }
    };

    // 保存配置
    const handleSave = async (values: GitHubToolsConfig) => {
        try {
            setLoading(true);

            const response = await apiClient.updateCategoryConfigs('github', values);
            if (!response.success) {
                throw new Error(response.message || '保存GitHub配置失败');
            }

            onSuccess?.();
            onCancel();
            return true;
        } catch (error) {
            console.error('Failed to save GitHub config:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };

    return (
        <ModalForm<GitHubToolsConfig>
            title={
                <Space>
                    <GithubOutlined style={{ color: currentTheme.token?.colorPrimary }} />
                    <Text strong style={{ color: currentTheme.token?.colorText, fontSize: 16 }}>
                        GitHub 工具配置
                    </Text>
                </Space>
            }
            open={visible}
            onOpenChange={(open) => !open && onCancel()}
            modalProps={{
                destroyOnHidden: true,
                width: 800
            }}
            submitter={{
                searchConfig: {
                    submitText: '保存配置',
                    resetText: '取消'
                },
                submitButtonProps: {
                    loading
                }
            }}
            request={handleRequest}
            onFinish={handleSave}
        >
            <Alert
                message="GitHub 工具配置"
                description="配置 GitHub API 访问凭证和请求参数，确保工具能正常访问 GitHub 服务。"
                type="info"
                showIcon={false}
                style={{ marginBottom: 24 }}
            />

            {/* 认证配置 */}
            <ProCard
                title={
                    <Space>
                        <KeyOutlined />
                        <Text strong>认证配置</Text>
                    </Space>
                }
                size="small"
                style={{ marginBottom: 16 }}
            >
                <ProFormText
                    name="token"
                    label={
                        <Space>
                            <KeyOutlined />
                            GitHub Token
                            <Tooltip title="GitHub Personal Access Token 或 App Token，用于 API 认证">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    placeholder="ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx"
                    fieldProps={{
                        type: 'password',
                        autoComplete: 'new-password'
                    }}
                    rules={[
                        { required: true, message: '请输入 GitHub Token' },
                        {
                            pattern: /^(ghp_|github_pat_)[a-zA-Z0-9_]{36,}$/,
                            message: '请输入有效的 GitHub Token 格式'
                        }
                    ]}
                    extra="获取方法：GitHub Settings > Developer settings > Personal access tokens"
                />

                <ProFormText
                    name="user_agent"
                    label={
                        <Space>
                            <ApiOutlined />
                            User Agent
                            <Tooltip title="HTTP 请求头中的 User Agent 标识">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    placeholder="LazyAI-Studio-GitHub-Tools/1.0"
                    rules={[
                        { required: true, message: '请输入 User Agent' }
                    ]}
                    extra="用于标识应用程序，建议包含应用名和版本号"
                />
            </ProCard>

            {/* API 端点配置 */}
            <ProCard
                title={
                    <Space>
                        <GlobalOutlined />
                        <Text strong>API 端点配置</Text>
                    </Space>
                }
                size="small"
                style={{ marginBottom: 16 }}
            >
                <ProFormText
                    name="base_url"
                    label={
                        <Space>
                            <GlobalOutlined />
                            API 基础 URL
                            <Tooltip title="GitHub API 服务器地址，Enterprise 用户可自定义">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    placeholder="https://api.github.com"
                    rules={[
                        { required: true, message: '请输入 API 基础 URL' },
                        { type: 'url', message: '请输入有效的 URL 格式' }
                    ]}
                    extra="公共 GitHub 使用默认值，企业版 GitHub 需要修改为对应地址"
                />

                <ProFormDigit
                    name="request_timeout"
                    label={
                        <Space>
                            <SettingOutlined />
                            请求超时时间（秒）
                            <Tooltip title="API 请求的最大等待时间">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    min={5}
                    max={300}
                    fieldProps={{ precision: 0 }}
                    rules={[
                        { required: true, message: '请设置请求超时时间' }
                    ]}
                    extra="建议设置为 30 秒，避免网络问题导致请求卡死"
                />

                <ProFormDigit
                    name="default_per_page"
                    label={
                        <Space>
                            <SettingOutlined />
                            默认分页大小
                            <Tooltip title="列表 API 的默认返回条目数量">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    min={1}
                    max={100}
                    fieldProps={{ precision: 0 }}
                    rules={[
                        { required: true, message: '请设置默认分页大小' }
                    ]}
                    extra="GitHub API 最大支持每页 100 条记录"
                />
            </ProCard>

            {/* 高级选项 */}
            <ProCard
                title={
                    <Space>
                        <SettingOutlined />
                        <Text strong>高级选项</Text>
                    </Space>
                }
                size="small"
                style={{ marginBottom: 16 }}
                collapsible
                defaultCollapsed={false}
            >
                <ProFormSwitch
                    name="enable_rate_limit_handling"
                    label={
                        <Space>
                            <SettingOutlined />
                            启用速率限制处理
                            <Tooltip title="自动处理 GitHub API 速率限制，避免请求被拒绝">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    extra="当达到速率限制时，会自动等待直到重置时间"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormSwitch
                    name="verify_ssl"
                    label={
                        <Space>
                            <KeyOutlined />
                            启用 SSL 证书验证
                            <Tooltip title="验证 HTTPS 连接的 SSL 证书有效性">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    extra="建议保持开启，确保连接安全性"
                    checkedChildren="验证"
                    unCheckedChildren="跳过"
                />

                <ProFormSwitch
                    name="auto_retry"
                    label={
                        <Space>
                            <SettingOutlined />
                            启用自动重试
                            <Tooltip title="网络错误或临时故障时自动重试请求">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    extra="遇到网络错误或服务器错误时会自动重试"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormDigit
                    name="max_retries"
                    label={
                        <Space>
                            <SettingOutlined />
                            最大重试次数
                            <Tooltip title="自动重试的最大次数">
                                <InfoCircleOutlined />
                            </Tooltip>
                        </Space>
                    }
                    min={1}
                    max={10}
                    fieldProps={{ precision: 0 }}
                    extra="建议设置为 3 次，避免过多重试"
                />
            </ProCard>

            <Alert
                message="使用说明"
                description={
                    <div>
                        <Paragraph style={{ margin: '8px 0', fontSize: 13 }}>
                            • <Text strong>GitHub Token</Text>: 必须配置有效的 Token 才能使用 GitHub API 功能
                        </Paragraph>
                        <Paragraph style={{ margin: '8px 0', fontSize: 13 }}>
                            • <Text strong>Token 权限</Text>: 根据需要的功能设置对应的权限范围（repo, issues, pull requests 等）
                        </Paragraph>
                        <Paragraph style={{ margin: '8px 0', fontSize: 13 }}>
                            • <Text strong>速率限制</Text>: GitHub API 有请求频率限制，建议开启自动处理避免被拒绝
                        </Paragraph>
                        <Paragraph style={{ margin: '8px 0', fontSize: 13 }}>
                            • <Text strong>企业版</Text>: 如使用 GitHub Enterprise，请修改 API 基础 URL 为对应地址
                        </Paragraph>
                    </div>
                }
                type="info"
                showIcon
                style={{ fontSize: 12, marginTop: 16 }}
            />
        </ModalForm>
    );
};

export default GitHubToolsConfigModal;