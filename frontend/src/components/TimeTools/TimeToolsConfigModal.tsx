import React, {useState} from 'react';
import {Alert, App, Col, Row, Space, Tooltip, Typography} from 'antd';
import {ModalForm, ProCard, ProFormSelect, ProFormSwitch} from '@ant-design/pro-components';
import {ClockCircleOutlined, InfoCircleOutlined, SettingOutlined} from '@ant-design/icons';
import {useTheme} from '../../contexts/ThemeContext';

const {Text, Paragraph} = Typography;

interface TimeToolsConfigModalProps {
    visible: boolean;
    onCancel: () => void;
}

interface TimeToolsConfig {
    default_timezone: string;
    show_timezone_info: boolean;
    auto_detect_timezone: boolean;
    enable_relative_time: boolean;
    cache_timezone_info: boolean;
    enable_business_days: boolean;
}

const timezoneValueEnum = {
    'auto': '🔄 自动检测时区',
    'local': '💻 本地时区',
    'UTC': '🌍 UTC+0 (协调世界时)',
    'UTC+8': '🕐 UTC+8 (北京时间)',
    'UTC+9': '🕘 UTC+9 (日本标准时间)',
    'UTC+1': '🕐 UTC+1 (中欧时间)',
    'UTC-5': '🕐 UTC-5 (美国东部时间)',
    'UTC-8': '🕐 UTC-8 (美国太平洋时间)',
    'UTC-7': '🕐 UTC-7 (美国山地时间)',
    'UTC-6': '🕐 UTC-6 (美国中部时间)',
    // 亚洲时区
    'Asia/Shanghai': '🇨🇳 Asia/Shanghai (中国标准时间)',
    'Asia/Beijing': '🇨🇳 Asia/Beijing (北京时间)',
    'Asia/Hong_Kong': '🇭🇰 Asia/Hong_Kong (香港时间)',
    'Asia/Taipei': '🇹🇼 Asia/Taipei (台北时间)',
    'Asia/Tokyo': '🇯🇵 Asia/Tokyo (日本标准时间)',
    'Asia/Seoul': '🇰🇷 Asia/Seoul (首尔时间)',
    'Asia/Singapore': '🇸🇬 Asia/Singapore (新加坡时间)',
    'Asia/Bangkok': '🇹🇭 Asia/Bangkok (曼谷时间)',
    'Asia/Jakarta': '🇮🇩 Asia/Jakarta (雅加达时间)',
    'Asia/Manila': '🇵🇭 Asia/Manila (马尼拉时间)',
    'Asia/Kolkata': '🇮🇳 Asia/Kolkata (印度标准时间)',
    'Asia/Dubai': '🇦🇪 Asia/Dubai (迪拜时间)',
    'Asia/Riyadh': '🇸🇦 Asia/Riyadh (利雅得时间)',
    // 欧洲时区
    'Europe/London': '🇬🇧 Europe/London (伦敦时间)',
    'Europe/Paris': '🇫🇷 Europe/Paris (巴黎时间)',
    'Europe/Berlin': '🇩🇪 Europe/Berlin (柏林时间)',
    'Europe/Rome': '🇮🇹 Europe/Rome (罗马时间)',
    'Europe/Madrid': '🇪🇸 Europe/Madrid (马德里时间)',
    'Europe/Amsterdam': '🇳🇱 Europe/Amsterdam (阿姆斯特丹时间)',
    'Europe/Brussels': '🇧🇪 Europe/Brussels (布鲁塞尔时间)',
    'Europe/Zurich': '🇨🇭 Europe/Zurich (苏黎世时间)',
    'Europe/Vienna': '🇦🇹 Europe/Vienna (维也纳时间)',
    'Europe/Moscow': '🇷🇺 Europe/Moscow (莫斯科时间)',
    // 美洲时区
    'America/New_York': '🇺🇸 America/New_York (纽约时间)',
    'America/Los_Angeles': '🇺🇸 America/Los_Angeles (洛杉矶时间)',
    'America/Chicago': '🇺🇸 America/Chicago (芝加哥时间)',
    'America/Denver': '🇺🇸 America/Denver (丹佛时间)',
    'America/Phoenix': '🇺🇸 America/Phoenix (凤凰城时间)',
    'America/Anchorage': '🇺🇸 America/Anchorage (安克雷奇时间)',
    'America/Toronto': '🇨🇦 America/Toronto (多伦多时间)',
    'America/Vancouver': '🇨🇦 America/Vancouver (温哥华时间)',
    'America/Mexico_City': '🇲🇽 America/Mexico_City (墨西哥城时间)',
    'America/Sao_Paulo': '🇧🇷 America/Sao_Paulo (圣保罗时间)',
    'America/Argentina/Buenos_Aires': '🇦🇷 Buenos Aires (布宜诺斯艾利斯时间)',
    // 大洋洲时区
    'Australia/Sydney': '🇦🇺 Australia/Sydney (悉尼时间)',
    'Australia/Melbourne': '🇦🇺 Australia/Melbourne (墨尔本时间)',
    'Australia/Perth': '🇦🇺 Australia/Perth (珀斯时间)',
    'Pacific/Auckland': '🇳🇿 Pacific/Auckland (奥克兰时间)',
    // 非洲时区
    'Africa/Cairo': '🇪🇬 Africa/Cairo (开罗时间)',
    'Africa/Johannesburg': '🇿🇦 Africa/Johannesburg (约翰内斯堡时间)',
    'Africa/Lagos': '🇳🇬 Africa/Lagos (拉各斯时间)'
}

const timezoneOptions = Object.entries(timezoneValueEnum).map(([value, label]) => ({
    label,
    value
}));

const TimeToolsConfigModal: React.FC<TimeToolsConfigModalProps> = ({visible, onCancel}) => {
    const {currentTheme} = useTheme();
    const {message: messageApi} = App.useApp();
    const [loading, setLoading] = useState(false);

    // 保存配置
    const saveConfig = async (values: TimeToolsConfig) => {
        try {
            setLoading(true);
            const response = await fetch('/api/mcp/categories/time/config', {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({config: values}),
            });

            const data = await response.json();

            if (data.success) {
                messageApi.success('时间工具配置已保存');
            } else {
                messageApi.error(data.message || '保存配置失败');
            }
        } catch (error) {
            messageApi.error('保存配置时发生错误');
            console.error('Save time tools config error:', error);
        } finally {
            setLoading(false);
        }
    };

    // 处理表单提交
    const handleFinish = async (values: TimeToolsConfig) => {
        await saveConfig(values);
        return true; // 提交成功后关闭Modal
    };


    return (
        <div id="time-tools-modal-container" style={{position: 'relative', zIndex: 'auto'}}>
            <ModalForm<TimeToolsConfig>
                title={
                    <Space>
                        <ClockCircleOutlined style={{color: currentTheme.token?.colorWarning}}/>
                        <Text strong style={{color: currentTheme.token?.colorText, fontSize: 16}}>
                            时间工具配置
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
                        const response = await fetch('/api/mcp/categories/time/config');
                        const data = await response.json();
                        if (data.success) {
                            return data.data.config;
                        } else {
                            // 返回默认配置
                            return {
                                default_timezone: 'auto',
                                show_timezone_info: true,
                                auto_detect_timezone: true,
                                enable_relative_time: false,
                                cache_timezone_info: true,
                                enable_business_days: false
                            };
                        }
                    } catch (error) {
                        console.error('Load time tools config error:', error);
                        // 返回默认配置
                        return {
                            default_timezone: 'auto',
                            show_timezone_info: true,
                            auto_detect_timezone: true,
                            enable_relative_time: false,
                            cache_timezone_info: true,
                            max_time_diff_unit: 'auto',
                            enable_business_days: false
                        };
                    }
                }}
                width={800}
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
                    message="时间工具配置"
                    description="配置时间工具集的全局参数，这些设置将应用于所有时间相关工具的默认行为。"
                    type="info"
                    showIcon
                    style={{marginBottom: 24}}
                />

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
                    <ProFormSelect
                        name="default_timezone"
                        label={
                            <Space>
                                <Text>默认时区</Text>
                                <Tooltip title="设置时间工具的默认时区，选择auto将自动检测用户设备时区">
                                    <InfoCircleOutlined/>
                                </Tooltip>
                            </Space>
                        }
                        options={timezoneOptions}
                        rules={[{required: true, message: '请选择默认时区'}]}
                        fieldProps={{
                            allowClear: false,
                            showSearch: true,
                            filterOption: (input: string, option: any) => {
                                return option?.label?.toLowerCase()?.includes(input.toLowerCase()) || false;
                            },
                            placeholder: "请选择默认时区"
                        }}
                        initialValue={'auto'}
                    />
                </ProCard>

                {/* 显示选项 */}
                <ProCard
                    title={
                        <Space>
                            <SettingOutlined/>
                            <Text strong>显示选项</Text>
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
                                name="show_timezone_info"
                                label={
                                    <Space>
                                        <Text>显示时区信息</Text>
                                        <Tooltip title="在时间显示中包含时区信息">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="auto_detect_timezone"
                                label={
                                    <Space>
                                        <Text>自动检测时区</Text>
                                        <Tooltip title="自动检测并使用用户的本地时区">
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
                                name="enable_relative_time"
                                label={
                                    <Space>
                                        <Text>启用相对时间</Text>
                                        <Tooltip title="显示相对时间(如几小时前)">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                        <Col span={12}>
                            <ProFormSwitch
                                name="enable_business_days"
                                label={
                                    <Space>
                                        <Text>启用工作日计算</Text>
                                        <Tooltip title="在时间计算中考虑工作日和节假日">
                                            <InfoCircleOutlined/>
                                        </Tooltip>
                                    </Space>
                                }
                            />
                        </Col>
                    </Row>
                </ProCard>

                {/* 性能选项 */}
                <ProCard
                    title={
                        <Space>
                            <SettingOutlined/>
                            <Text strong>性能选项</Text>
                        </Space>
                    }
                    size="small"
                    collapsible
                    defaultCollapsed={false}
                >
                    <Row gutter={16}>
                        <Col span={12}>
                            <ProFormSwitch
                                name="cache_timezone_info"
                                label={
                                    <Space>
                                        <Text>缓存时区信息</Text>
                                        <Tooltip title="缓存时区信息以提高性能">
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
                                • <Text strong>默认时区</Text>: 设置所有时间工具使用的默认时区，"auto"表示自动检测设备时区
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>时区信息</Text>: 控制时间工具是否显示时区相关信息
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>相对时间</Text>: 启用后可以显示"几分钟前"、"几小时前"等相对时间格式
                            </Paragraph>
                            <Paragraph style={{margin: '8px 0', fontSize: 13}}>
                                • <Text strong>缓存选项</Text>: 启用缓存可以提高频繁时间操作的性能
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

export default TimeToolsConfigModal;