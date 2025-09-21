/**
 * 缓存工具配置模态框
 * 支持配置默认TTL、最大内存项、清理间隔等参数
 */

import React, {useState} from 'react';
import {Alert, Space, Tooltip, Typography} from 'antd';
import {ModalForm, ProCard, ProFormDigit, ProFormSwitch} from '@ant-design/pro-components';
import {ClockCircleOutlined, DatabaseOutlined, InfoCircleOutlined, SettingOutlined} from '@ant-design/icons';
import {apiClient} from '../../api';
import {useTheme} from '../../contexts/ThemeContext';

const {Text, Paragraph} = Typography;

export interface CacheToolsConfig {
    enabled: boolean;
    backend: string;
    max_size_mb: number;
    timeout_seconds: number;
    auto_create_dirs: boolean;
    ttl: {
        default_ttl_seconds: number;
        enable_ttl: boolean;
    };
    monitoring: {
        enable_statistics: boolean;
        log_operations: boolean;
        metrics_collection: boolean;
    };
}

interface CacheToolsConfigModalProps {
    visible: boolean;
    onCancel: () => void;
    onSuccess?: () => void;
}

const CacheToolsConfigModal: React.FC<CacheToolsConfigModalProps> = ({
                                                                         visible,
                                                                         onCancel,
                                                                         onSuccess
                                                                     }) => {
    const {currentTheme} = useTheme();
    const [loading, setLoading] = useState(false);

    // 请求初始配置数据
    const handleRequest = async () => {
        try {
            const response = await apiClient.getCategoryConfig('cache');
            if (response.data?.success && response.data?.data) {
                const config = response.data.data;
                // 转换配置格式以匹配表单结构
                return {
                    enabled: config.enabled || true,
                    backend: config.backend || 'diskcache',
                    max_size_mb: config.max_size_mb || 1024,
                    timeout_seconds: config.timeout_seconds || 10,
                    auto_create_dirs: config.auto_create_dirs !== false,
                    ttl: {
                        default_ttl_seconds: config.ttl?.default_ttl_seconds || 3600,
                        enable_ttl: config.ttl?.enable_ttl !== false
                    },
                    monitoring: {
                        enable_statistics: config.monitoring?.enable_statistics !== false,
                        log_operations: config.monitoring?.log_operations || false,
                        metrics_collection: config.monitoring?.metrics_collection || false
                    }
                };
            }
            return {
                enabled: true,
                backend: 'diskcache',
                max_size_mb: 1024,
                timeout_seconds: 10,
                auto_create_dirs: true,
                ttl: {
                    default_ttl_seconds: 3600,
                    enable_ttl: true
                },
                monitoring: {
                    enable_statistics: true,
                    log_operations: false,
                    metrics_collection: false
                }
            };
        } catch (error) {
            console.error('Failed to load cache config:', error);
            return {
                enabled: true,
                backend: 'diskcache',
                max_size_mb: 1024,
                timeout_seconds: 10,
                auto_create_dirs: true,
                ttl: {
                    default_ttl_seconds: 3600,
                    enable_ttl: true
                },
                monitoring: {
                    enable_statistics: true,
                    log_operations: false,
                    metrics_collection: false
                }
            };
        }
    };

    // 保存配置
    const handleSave = async (values: CacheToolsConfig) => {
        try {
            setLoading(true);

            // 更新缓存工具配置
            const response = await apiClient.updateCategoryConfigs('cache', values);

            if (!response.data?.success) {
                throw new Error(response.data?.message || '保存配置失败');
            }

            onSuccess?.();
            onCancel();
            return true;
        } catch (error) {
            console.error('Failed to save cache config:', error);
            throw error;
        } finally {
            setLoading(false);
        }
    };


    return (
        <ModalForm<CacheToolsConfig>
            title={
                <Space>
                    <DatabaseOutlined style={{color: currentTheme.token?.colorPrimary}}/>
                    <Text strong style={{color: currentTheme.token?.colorText, fontSize: 16}}>
                        缓存工具配置
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
                message="DiskCache 缓存工具配置"
                description="配置 DiskCache 持久化缓存系统的运行参数。缓存数据固定存储在 data/mcp/cache 目录下。"
                type="info"
                showIcon={false}
                style={{marginBottom: 24}}
            />

            {/* 基础存储配置 */}
            <ProCard
                title={
                    <Space>
                        <DatabaseOutlined/>
                        <Text strong>存储配置</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
            >
                <ProFormSwitch
                    name="enabled"
                    label={
                        <Space>
                            <DatabaseOutlined/>
                            启用缓存工具
                            <Tooltip title="开启或关闭整个缓存系统">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="关闭后所有缓存操作将不可用"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormDigit
                    name="max_size_mb"
                    label={
                        <Space>
                            <DatabaseOutlined/>
                            最大缓存大小(MB)
                            <Tooltip title="缓存的最大存储容量">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    placeholder="1024"
                    min={10}
                    max={10240}
                    formatter={(value?: string | number) => `${value}MB`}
                    parser={(value?: string) => value?.replace('MB', '') || ''}
                    rules={[
                        {required: true, message: '请输入最大缓存大小'},
                        {type: 'number', min: 10, max: 10240, message: '缓存大小范围为10MB到10GB'}
                    ]}
                    extra="达到限制时会自动清理旧数据"
                />

                <ProFormDigit
                    name="timeout_seconds"
                    label={
                        <Space>
                            <ClockCircleOutlined/>
                            操作超时时间(秒)
                            <Tooltip title="DiskCache 操作的超时时间">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    placeholder="10"
                    min={1}
                    max={300}
                    rules={[
                        {required: true, message: '请输入超时时间'},
                        {type: 'number', min: 1, max: 300, message: '超时时间范围为1秒到5分钟'}
                    ]}
                    extra="缓存操作的最大等待时间"
                />

                <ProFormSwitch
                    name="auto_create_dirs"
                    label={
                        <Space>
                            <DatabaseOutlined/>
                            自动创建目录
                            <Tooltip title="自动创建不存在的缓存目录">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="启用后会自动创建缓存目录"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />
            </ProCard>

            {/* TTL 配置 */}
            <ProCard
                title={
                    <Space>
                        <ClockCircleOutlined/>
                        <Text strong>TTL 过期配置</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
            >
                <ProFormSwitch
                    name={['ttl', 'enable_ttl']}
                    label={
                        <Space>
                            <ClockCircleOutlined/>
                            启用TTL功能
                            <Tooltip title="开启缓存项的自动过期功能">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="启用后缓存项会在指定时间后自动过期"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormDigit
                    name={['ttl', 'default_ttl_seconds']}
                    label={
                        <Space>
                            <ClockCircleOutlined/>
                            默认TTL时间（秒）
                            <Tooltip title="新建缓存项的默认生存时间">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    placeholder="3600"
                    min={1}
                    max={86400 * 30}
                    fieldProps={{
                        precision: 0
                    }}
                    rules={[
                        {required: true, message: '请输入默认TTL时间'},
                        {type: 'number', min: 1, max: 86400 * 30, message: 'TTL时间范围为1秒到30天'}
                    ]}
                    extra="建议设置为3600秒（1小时）"
                />

            </ProCard>

            {/* 监控配置 */}
            <ProCard
                title={
                    <Space>
                        <SettingOutlined/>
                        <Text strong>监控和日志</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
                collapsible
                defaultCollapsed={true}
            >
                <ProFormSwitch
                    name={['monitoring', 'enable_statistics']}
                    label={
                        <Space>
                            <InfoCircleOutlined/>
                            启用统计功能
                            <Tooltip title="收集访问统计、命中率等性能指标">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="收集缓存访问统计信息，包括命中率、访问次数等"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormSwitch
                    name={['monitoring', 'log_operations']}
                    label={
                        <Space>
                            <InfoCircleOutlined/>
                            记录操作日志
                            <Tooltip title="记录所有缓存操作的详细日志">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="记录所有缓存操作，可能影响性能"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />

                <ProFormSwitch
                    name={['monitoring', 'metrics_collection']}
                    label={
                        <Space>
                            <InfoCircleOutlined/>
                            收集性能指标
                            <Tooltip title="收集详细的性能指标数据">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="收集性能指标，用于系统监控和优化"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />
            </ProCard>

            <Alert
                message="DiskCache 特性说明"
                description={
                    <div>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>持久化存储</Text>: 数据保存在磁盘上，重启后不会丢失
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>线程安全</Text>: 支持多线程并发访问
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>自动淘汰</Text>: 当达到大小限制时自动清理最久未使用的数据
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>高性能</Text>: 针对大容量存储和频繁访问进行优化
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>固定目录</Text>: 缓存数据统一存储在 data/mcp/cache 目录
                        </Paragraph>
                    </div>
                }
                type="info"
                showIcon
                style={{fontSize: 12, marginTop: 16}}
            />
        </ModalForm>
    );
};

export default CacheToolsConfigModal;