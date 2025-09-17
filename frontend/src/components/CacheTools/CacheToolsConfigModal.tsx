/**
 * 缓存工具配置模态框
 * 支持配置默认TTL、最大内存项、清理间隔等参数
 */

import React, {useState} from 'react';
import {Alert, Space, Tooltip, Typography} from 'antd';
import {ModalForm, ProCard, ProFormDigit, ProFormSelect, ProFormSwitch, ProFormText} from '@ant-design/pro-components';
import {ClockCircleOutlined, DatabaseOutlined, InfoCircleOutlined, SettingOutlined} from '@ant-design/icons';
import {apiClient} from '../../api';
import {useTheme} from '../../contexts/ThemeContext';

const {Text, Paragraph} = Typography;

// const { Text, Title } = Typography;

export interface CacheToolsConfig {
    backend_type: string;
    default_ttl: number;
    persistence_enabled: boolean;
    compression_enabled: boolean;
    stats_enabled: boolean;
    // Backend-specific configs
    diskcache_directory?: string;
    diskcache_size_limit?: number;
    memcached_host?: string;
    memcached_port?: number;
    lmdb_path?: string;
    lmdb_map_size?: number;
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
            if (response.success && response.data) {
                return response.data;
            }
            return {
                backend_type: 'tinydb',
                default_ttl: 3600,
                persistence_enabled: true,
                compression_enabled: false,
                stats_enabled: true
            };
        } catch (error) {
            console.error('Failed to load cache config:', error);
            return {
                backend_type: 'tinydb',
                default_ttl: 3600,
                persistence_enabled: true,
                compression_enabled: false,
                stats_enabled: true
            };
        }
    };

    // 保存配置
    const handleSave = async (values: CacheToolsConfig) => {
        try {
            setLoading(true);

            // 提取后端配置
            const backendConfig: any = {};

            if (values.backend_type === 'diskcache') {
                if (values.diskcache_directory) backendConfig.directory = values.diskcache_directory;
                if (values.diskcache_size_limit) backendConfig.size_limit = values.diskcache_size_limit * 1024 * 1024; // Convert MB to bytes
            } else if (values.backend_type === 'memcached') {
                if (values.memcached_host) backendConfig.host = values.memcached_host;
                if (values.memcached_port) backendConfig.port = values.memcached_port;
            } else if (values.backend_type === 'lmdb') {
                if (values.lmdb_path) backendConfig.path = values.lmdb_path;
                if (values.lmdb_map_size) backendConfig.map_size = values.lmdb_map_size * 1024 * 1024; // Convert MB to bytes
            }

            // 首先更新MCP分类配置
            const categoryResponse = await apiClient.updateCategoryConfigs('cache', {
                backend_type: values.backend_type,
                default_ttl: values.default_ttl,
                persistence_enabled: values.persistence_enabled,
                compression_enabled: values.compression_enabled,
                stats_enabled: values.stats_enabled
            });

            if (!categoryResponse.success) {
                throw new Error(categoryResponse.message || '保存MCP配置失败');
            }

            // 如果需要切换后端，调用后端切换API
            if (values.backend_type && Object.keys(backendConfig).length > 0) {
                const backendResponse = await apiClient.switchCacheBackend(values.backend_type, backendConfig);
                if (!backendResponse.success) {
                    throw new Error(backendResponse.message || '切换存储后端失败');
                }
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

    // 存储后端选项
    const backendOptions = [
        {label: 'TinyDB（默认）', value: 'tinydb', description: '基于文件的轻量级数据库'},
        {label: 'DiskCache', value: 'diskcache', description: '磁盘缓存，支持大容量存储'},
        {label: 'Memcached', value: 'memcached', description: '分布式内存缓存系统'},
        {label: 'LMDB', value: 'lmdb', description: '高性能嵌入式数据库'}
    ];

    const [currentBackend, setCurrentBackend] = useState<string>('tinydb');

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
                message="缓存工具配置"
                description="配置缓存工具的运行参数，包括默认TTL时间、内存限制和持久化选项。"
                type="info"
                showIcon={false}
                style={{marginBottom: 24}}
            />


            {/* 存储后端配置 */}
            <ProCard
                title={
                    <Space>
                        <DatabaseOutlined/>
                        <Text strong>存储后端配置</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
            >

            <ProFormSelect
                name="backend_type"
                label={
                    <Space>
                        <DatabaseOutlined/>
                        存储后端类型
                        <Tooltip title="选择缓存数据的存储后端">
                            <InfoCircleOutlined/>
                        </Tooltip>
                    </Space>
                }
                placeholder="请选择存储后端"
                options={backendOptions}
                fieldProps={{
                    allowClear: false,
                    onChange: (value: string) => setCurrentBackend(value)
                }}
                rules={[
                    {required: true, message: '请选择存储后端'}
                ]}
                extra="TinyDB为默认选项，无需额外服务；Memcached需要独立运行的服务"
                initialValue={'tinydb'}
            />

            {/* DiskCache配置 */}
            {currentBackend === 'diskcache' && (
                <>
                    <ProFormText
                        name="diskcache_directory"
                        label="缓存目录"
                        placeholder="./cache"
                        initialValue="./cache"
                        extra="磁盘缓存存储目录"
                    />
                    <ProFormDigit
                        name="diskcache_size_limit"
                        label="存储上限(MB)"
                        placeholder="1024"
                        initialValue={1024}
                        min={10}
                        formatter={(value?: string | number) => `${value}MB`}
                        parser={(value?: string) => value?.replace('MB', '') || ''}
                        extra="磁盘缓存的最大存储容量"
                    />
                </>
            )}

            {/* Memcached配置 */}
            {currentBackend === 'memcached' && (
                <>
                    <ProFormText
                        name="memcached_host"
                        label="Memcached主机地址"
                        placeholder="localhost"
                        initialValue="localhost"
                        extra="Memcached服务器的主机地址"
                    />
                    <ProFormDigit
                        name="memcached_port"
                        label="Memcached端口"
                        placeholder="11211"
                        initialValue={11211}
                        min={1}
                        max={65535}
                        extra="Memcached服务器的端口号"
                    />
                </>
            )}

            {/* LMDB配置 */}
            {currentBackend === 'lmdb' && (
                <>
                    <ProFormText
                        name="lmdb_path"
                        label="LMDB路径"
                        placeholder="./lmdb_cache"
                        initialValue="./lmdb_cache"
                        extra="LMDB数据库文件路径"
                    />
                    <ProFormDigit
                        name="lmdb_map_size"
                        label="映射大小(MB)"
                        placeholder="1024"
                        initialValue={1024}
                        min={10}
                        formatter={(value?: string | number) => `${value}MB`}
                        parser={(value?: string) => value?.replace('MB', '') || ''}
                        extra="LMDB映射的最大内存大小"
                    />
                </>
            )}
            </ProCard>

            {/* 基础配置 */}
            <ProCard
                title={
                    <Space>
                        <ClockCircleOutlined/>
                        <Text strong>基础配置</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
            >

            <ProFormDigit
                name="default_ttl"
                label={
                    <Space>
                        <ClockCircleOutlined/>
                        默认TTL时间（秒）
                        <Tooltip title="新建缓存项的默认生存时间，单位为秒">
                            <InfoCircleOutlined/>
                        </Tooltip>
                    </Space>
                }
                initialValue="3600"
                min={1}
                max={86400 * 30} // 最多30天
                fieldProps={{
                    precision: 0
                }}
                rules={[
                    {required: true, message: '请输入默认TTL时间'},
                    {type: 'number', min: 1, max: 86400 * 30, message: 'TTL时间范围为1秒到30天'}
                ]}
                extra="缓存项在指定时间后会自动过期删除，建议设置为3600秒（1小时）"
            />
            </ProCard>

            {/* 高级选项 */}
            <ProCard
                title={
                    <Space>
                        <SettingOutlined/>
                        <Text strong>高级选项</Text>
                    </Space>
                }
                size="small"
                style={{marginBottom: 16}}
                collapsible
                defaultCollapsed={false}
            >

            {/* 持久化存储 - TinyDB, DiskCache, LMDB 支持 */}
            {(currentBackend === 'tinydb' || currentBackend === 'diskcache' || currentBackend === 'lmdb') && (
                <ProFormSwitch
                    name="persistence_enabled"
                    label={
                        <Space>
                            <DatabaseOutlined/>
                            启用持久化存储
                            <Tooltip title="将缓存数据保存到数据库，重启后数据不会丢失">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra={`${currentBackend === 'tinydb' ? 'TinyDB' : currentBackend === 'diskcache' ? 'DiskCache' : 'LMDB'} 支持持久化存储，数据会保存到磁盘`}
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />
            )}

            {/* 统计功能 - 所有后端都支持 */}
            <ProFormSwitch
                name="stats_enabled"
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

            {/* 数据压缩 - TinyDB, DiskCache, LMDB 支持 */}
            {(currentBackend === 'tinydb' || currentBackend === 'diskcache' || currentBackend === 'lmdb') && (
                <ProFormSwitch
                    name="compression_enabled"
                    label={
                        <Space>
                            <DatabaseOutlined/>
                            启用数据压缩
                            <Tooltip title="对大型缓存值进行压缩存储，节省存储空间">
                                <InfoCircleOutlined/>
                            </Tooltip>
                        </Space>
                    }
                    extra="对较大的缓存值进行压缩，可以节省存储空间但会增加CPU使用"
                    checkedChildren="开启"
                    unCheckedChildren="关闭"
                />
            )}

            {/* Memcached 特有选项提示 */}
            {currentBackend === 'memcached' && (
                <Alert
                    message="Memcached 存储特性"
                    description={
                        <div>
                            <p><strong>内存存储</strong>：数据存储在内存中，重启后数据会丢失</p>
                            <p><strong>高性能</strong>：提供极高的读写性能</p>
                            <p><strong>分布式</strong>：原生支持分布式部署</p>
                        </div>
                    }
                    type="info"
                    showIcon
                    style={{ marginBottom: 16 }}
                />
            )}
            </ProCard>

            <Alert
                message="配置说明"
                description={
                    <div>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>默认TTL时间</Text>: 建议设置为3600秒（1小时），平衡缓存效果和内存使用
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>持久化存储</Text>: 推荐开启，确保数据不会因重启而丢失
                        </Paragraph>
                        <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                            • <Text strong>存储后端</Text>: 根据性能需求选择合适的存储后端类型
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