import React, { useState, useEffect } from 'react';
import {
  Modal,
  Form,
  Input,
  InputNumber,
  Switch,
  Tabs,
  Button,
  Space,
  Table,
  Tag,
  Alert,
  Divider,
  Typography,
  Card,
  Statistic,
  Row,
  Col,
  Tooltip,
  App
} from 'antd';
import {
  SecurityScanOutlined,
  FolderOutlined,
  EditOutlined,
  DeleteOutlined,
  PlusOutlined,
  ReloadOutlined,
  FileTextOutlined,
  WarningOutlined,
  CheckCircleOutlined
} from '@ant-design/icons';
import { 
  apiClient, 
  FileSecurityInfo, 
  UpdatePathsRequest, 
  UpdateLimitsRequest 
} from '../../api';
import { useTheme } from '../../contexts/ThemeContext';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { useApp } = App;

interface FileToolsConfigModalProps {
  visible: boolean;
  onCancel: () => void;
}

const FileToolsConfigModal: React.FC<FileToolsConfigModalProps> = ({
  visible,
  onCancel
}) => {
  const { currentTheme } = useTheme();
  const { message: messageApi } = useApp();
  const [loading, setLoading] = useState(false);
  const [securityInfo, setSecurityInfo] = useState<FileSecurityInfo | null>(null);
  const [activeTab, setActiveTab] = useState('overview');
  const [pathForm] = Form.useForm();
  const [limitForm] = Form.useForm();
  const [editingPaths, setEditingPaths] = useState<{
    type: 'readable' | 'writable' | 'deletable' | 'forbidden' | null;
    paths: string[];
  }>({ type: null, paths: [] });

  // 加载文件安全配置信息
  const loadSecurityInfo = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getFileSecurityInfo();
      
      if (response.status === 'success' && response.data) {
        setSecurityInfo(response.data);
        // 更新限制表单的初始值
        limitForm.setFieldsValue({
          max_file_size_mb: response.data.max_file_size_mb,
          max_read_lines: response.data.max_read_lines,
          strict_mode: response.data.strict_mode
        });
      }
    } catch (error) {
      console.error('Failed to load file security info:', error);
      messageApi.error('加载文件安全配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新路径配置
  const updatePaths = async (type: 'readable' | 'writable' | 'deletable' | 'forbidden', paths: string[]) => {
    try {
      setLoading(true);
      const request: UpdatePathsRequest = { config_type: type, paths };
      const response = await apiClient.updateFileSecurityPaths(request);
      
      if (response.status === 'success') {
        messageApi.success(`${type}路径配置更新成功`);
        await loadSecurityInfo(); // 重新加载配置
        setEditingPaths({ type: null, paths: [] });
      } else {
        messageApi.error(response.message || '更新路径配置失败');
      }
    } catch (error) {
      console.error('Failed to update paths:', error);
      messageApi.error('更新路径配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新限制配置
  const updateLimits = async (limitType: 'max_file_size' | 'max_read_lines' | 'strict_mode', value: number | boolean) => {
    try {
      setLoading(true);
      const request: UpdateLimitsRequest = { limit_type: limitType, value };
      const response = await apiClient.updateFileSecurityLimits(request);
      
      if (response.status === 'success') {
        messageApi.success(`${limitType}限制配置更新成功`);
        await loadSecurityInfo(); // 重新加载配置
      } else {
        messageApi.error(response.message || '更新限制配置失败');
      }
    } catch (error) {
      console.error('Failed to update limits:', error);
      messageApi.error('更新限制配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 重新加载配置
  const reloadConfig = async () => {
    try {
      setLoading(true);
      
      try {
        const response = await apiClient.reloadFileSecurityConfig();
        if (response.status === 'success') {
          messageApi.success('文件安全配置重新加载成功');
          await loadSecurityInfo();
          return;
        } else {
          console.warn('Reload config API failed, falling back to reload security info');
        }
      } catch (error) {
        console.warn('Reload config API error, falling back to reload security info:', error);
      }
      
      // 备用方案：直接重新加载安全信息
      await loadSecurityInfo();
      messageApi.success('配置信息已刷新');
      
    } catch (error) {
      console.error('Failed to reload config:', error);
      messageApi.error('重新加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 处理限制表单提交
  const handleLimitSubmit = async (values: any) => {
    for (const [key, value] of Object.entries(values)) {
      if (key === 'max_file_size_mb' && value !== securityInfo?.max_file_size_mb) {
        await updateLimits('max_file_size', (value as number) * 1024 * 1024); // 转换为字节
      } else if (key === 'max_read_lines' && value !== securityInfo?.max_read_lines) {
        await updateLimits('max_read_lines', value as number);
      } else if (key === 'strict_mode' && value !== securityInfo?.strict_mode) {
        await updateLimits('strict_mode', value as boolean);
      }
    }
  };

  // 处理路径编辑
  const handleEditPaths = (type: 'readable' | 'writable' | 'deletable' | 'forbidden') => {
    if (!securityInfo) return;
    
    let paths: string[] = [];
    switch (type) {
      case 'readable':
        paths = [...securityInfo.readable_directories];
        break;
      case 'writable':
        paths = [...securityInfo.writable_directories];
        break;
      case 'deletable':
        paths = [...securityInfo.deletable_directories];
        break;
      case 'forbidden':
        paths = [...securityInfo.forbidden_directories];
        break;
    }
    
    setEditingPaths({ type, paths });
    pathForm.setFieldsValue({ paths: paths.join('\n') });
  };

  // 处理路径表单提交
  const handlePathSubmit = async (values: any) => {
    if (!editingPaths.type) return;
    
    const paths = values.paths
      .split('\n')
      .map((path: string) => path.trim())
      .filter((path: string) => path.length > 0);
    
    await updatePaths(editingPaths.type, paths);
  };

  useEffect(() => {
    if (visible) {
      loadSecurityInfo();
    }
  }, [visible]);

  // 计算安全评分
  const getSecurityScore = () => {
    if (!securityInfo) return 0;
    
    let score = 0;
    
    // 严格模式加分
    if (securityInfo.strict_mode) score += 30;
    
    // 有禁止目录加分
    if (securityInfo.forbidden_directories.length > 0) score += 20;
    
    // 有限制设置加分
    if (securityInfo.max_file_size_mb < 1000) score += 25;
    if (securityInfo.max_read_lines < 10000) score += 25;
    
    return Math.min(score, 100);
  };

  const securityScore = getSecurityScore();
  const getScoreStatus = (score: number) => {
    if (score >= 80) return { status: 'success', text: '安全' };
    if (score >= 60) return { status: 'warning', text: '中等' };
    return { status: 'error', text: '风险' };
  };

  const scoreStatus = getScoreStatus(securityScore);

  return (
    <Modal
      title={
        <Space>
          <SecurityScanOutlined />
          文件工具集安全配置
        </Space>
      }
      open={visible}
      onCancel={onCancel}
      footer={null}
      width={800}
      destroyOnClose
    >
      <Tabs activeKey={activeTab} onChange={setActiveTab}>
        <TabPane 
          tab={
            <span>
              <CheckCircleOutlined />
              安全概览
            </span>
          } 
          key="overview"
        >
          <div style={{ padding: '16px 0' }}>
            {securityInfo && (
              <>
                <Row gutter={16} style={{ marginBottom: 24 }}>
                  <Col span={8}>
                    <Card style={{ 
                      backgroundColor: currentTheme.token?.colorBgContainer,
                      borderColor: currentTheme.token?.colorBorder
                    }}>
                      <Statistic
                        title={<span style={{ color: currentTheme.token?.colorTextSecondary }}>安全评分</span>}
                        value={securityScore}
                        suffix="/ 100"
                        valueStyle={{ 
                          color: scoreStatus.status === 'success' 
                            ? (currentTheme.token?.colorSuccess || '#3f8600')
                            : scoreStatus.status === 'warning' 
                            ? (currentTheme.token?.colorWarning || '#faad14')
                            : (currentTheme.token?.colorError || '#ff4d4f')
                        }}
                        prefix={scoreStatus.status === 'success' ? <CheckCircleOutlined /> : <WarningOutlined />}
                      />
                      <div style={{ marginTop: 8 }}>
                        <Tag color={scoreStatus.status === 'success' ? 'green' : scoreStatus.status === 'warning' ? 'orange' : 'red'}>
                          {scoreStatus.text}
                        </Tag>
                      </div>
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card style={{ 
                      backgroundColor: currentTheme.token?.colorBgContainer,
                      borderColor: currentTheme.token?.colorBorder
                    }}>
                      <Statistic
                        title={<span style={{ color: currentTheme.token?.colorTextSecondary }}>安全模式</span>}
                        value={securityInfo.strict_mode ? '严格模式' : '宽松模式'}
                        valueStyle={{ 
                          color: securityInfo.strict_mode 
                            ? (currentTheme.token?.colorSuccess || '#3f8600')
                            : (currentTheme.token?.colorWarning || '#faad14')
                        }}
                      />
                    </Card>
                  </Col>
                  <Col span={8}>
                    <Card style={{ 
                      backgroundColor: currentTheme.token?.colorBgContainer,
                      borderColor: currentTheme.token?.colorBorder
                    }}>
                      <Statistic
                        title={<span style={{ color: currentTheme.token?.colorTextSecondary }}>配置目录</span>}
                        value={securityInfo.readable_directories.length + securityInfo.writable_directories.length + securityInfo.deletable_directories.length + securityInfo.forbidden_directories.length}
                        suffix="个"
                        valueStyle={{ color: currentTheme.token?.colorText }}
                      />
                    </Card>
                  </Col>
                </Row>

                <Alert
                  message={<span style={{ color: currentTheme.token?.colorText }}>文件工具集安全说明</span>}
                  description={
                    <div style={{ color: currentTheme.token?.colorTextSecondary }}>
                      <p><strong style={{ color: currentTheme.token?.colorText }}>严格模式：</strong>所有文件工具只能访问明确配置的允许目录</p>
                      <p><strong style={{ color: currentTheme.token?.colorText }}>宽松模式：</strong>所有文件工具可以访问除禁止目录外的所有目录</p>
                      <p><strong style={{ color: currentTheme.token?.colorText }}>路径权限：</strong>统一配置所有文件工具的读取、写入、删除权限</p>
                      <p><strong style={{ color: currentTheme.token?.colorText }}>安全限制：</strong>统一限制所有文件工具的文件大小和读取行数，防止资源滥用</p>
                    </div>
                  }
                  type="info"
                  showIcon
                  style={{
                    backgroundColor: currentTheme.token?.colorInfoBg,
                    borderColor: currentTheme.token?.colorInfoBorder
                  }}
                />
              </>
            )}
          </div>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <FolderOutlined />
              路径管理
            </span>
          } 
          key="paths"
        >
          <div style={{ padding: '16px 0' }}>
            {securityInfo && (
              <>
                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={12}>
                    <Card 
                      title={<span style={{ color: currentTheme.token?.colorText }}>📖 可读取目录</span>}
                      size="small" 
                      extra={
                        <Button type="text" size="small" icon={<EditOutlined />} 
                          onClick={() => handleEditPaths('readable')}>编辑</Button>
                      }
                      style={{
                        backgroundColor: currentTheme.token?.colorBgContainer,
                        borderColor: currentTheme.token?.colorBorder
                      }}
                    >
                      <div style={{ maxHeight: 120, overflow: 'auto' }}>
                        {securityInfo.readable_directories.length > 0 ? (
                          securityInfo.readable_directories.map((path, index) => (
                            <div key={index} style={{ marginBottom: 4 }}>
                              <Text code style={{ 
                                backgroundColor: currentTheme.token?.colorFillQuaternary,
                                color: currentTheme.token?.colorText
                              }}>{path}</Text>
                            </div>
                          ))
                        ) : (
                          <Text type="secondary" style={{ color: currentTheme.token?.colorTextSecondary }}>未配置</Text>
                        )}
                      </div>
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card 
                      title={<span style={{ color: currentTheme.token?.colorText }}>✏️ 可写入目录</span>}
                      size="small" 
                      extra={
                        <Button type="text" size="small" icon={<EditOutlined />} 
                          onClick={() => handleEditPaths('writable')}>编辑</Button>
                      }
                      style={{
                        backgroundColor: currentTheme.token?.colorBgContainer,
                        borderColor: currentTheme.token?.colorBorder
                      }}
                    >
                      <div style={{ maxHeight: 120, overflow: 'auto' }}>
                        {securityInfo.writable_directories.length > 0 ? (
                          securityInfo.writable_directories.map((path, index) => (
                            <div key={index} style={{ marginBottom: 4 }}>
                              <Text code style={{ 
                                backgroundColor: currentTheme.token?.colorFillQuaternary,
                                color: currentTheme.token?.colorText
                              }}>{path}</Text>
                            </div>
                          ))
                        ) : (
                          <Text type="secondary" style={{ color: currentTheme.token?.colorTextSecondary }}>未配置</Text>
                        )}
                      </div>
                    </Card>
                  </Col>
                </Row>

                <Row gutter={16} style={{ marginBottom: 16 }}>
                  <Col span={12}>
                    <Card 
                      title={<span style={{ color: currentTheme.token?.colorText }}>🗑️ 可删除目录</span>}
                      size="small" 
                      extra={
                        <Button type="text" size="small" icon={<EditOutlined />} 
                          onClick={() => handleEditPaths('deletable')}>编辑</Button>
                      }
                      style={{
                        backgroundColor: currentTheme.token?.colorBgContainer,
                        borderColor: currentTheme.token?.colorBorder
                      }}
                    >
                      <div style={{ maxHeight: 120, overflow: 'auto' }}>
                        {securityInfo.deletable_directories.length > 0 ? (
                          securityInfo.deletable_directories.map((path, index) => (
                            <div key={index} style={{ marginBottom: 4 }}>
                              <Text code style={{ 
                                backgroundColor: currentTheme.token?.colorFillQuaternary,
                                color: currentTheme.token?.colorText
                              }}>{path}</Text>
                            </div>
                          ))
                        ) : (
                          <Text type="secondary" style={{ color: currentTheme.token?.colorTextSecondary }}>未配置</Text>
                        )}
                      </div>
                    </Card>
                  </Col>
                  <Col span={12}>
                    <Card 
                      title={<span style={{ color: currentTheme.token?.colorText }}>🚫 禁止访问目录</span>}
                      size="small" 
                      extra={
                        <Button type="text" size="small" icon={<EditOutlined />} 
                          onClick={() => handleEditPaths('forbidden')}>编辑</Button>
                      }
                      style={{
                        backgroundColor: currentTheme.token?.colorBgContainer,
                        borderColor: currentTheme.token?.colorBorder
                      }}
                    >
                      <div style={{ maxHeight: 120, overflow: 'auto' }}>
                        {securityInfo.forbidden_directories.length > 0 ? (
                          securityInfo.forbidden_directories.map((path, index) => (
                            <div key={index} style={{ marginBottom: 4 }}>
                              <Text code style={{ 
                                backgroundColor: currentTheme.token?.colorFillQuaternary,
                                color: currentTheme.token?.colorText
                              }}>{path}</Text>
                            </div>
                          ))
                        ) : (
                          <Text type="secondary" style={{ color: currentTheme.token?.colorTextSecondary }}>未配置</Text>
                        )}
                      </div>
                    </Card>
                  </Col>
                </Row>

                {editingPaths.type && (
                  <Card title={`编辑${editingPaths.type}路径`} style={{ marginTop: 16 }}>
                    <Form form={pathForm} onFinish={handlePathSubmit} layout="vertical">
                      <Form.Item
                        name="paths"
                        label="路径列表（每行一个路径，空表示允许所有路径）"
                      >
                        <TextArea rows={6} placeholder="留空表示允许所有路径&#10;或指定具体路径：&#10;/home/user/documents&#10;/var/www/html&#10;/tmp" />
                      </Form.Item>
                      <Form.Item>
                        <Space>
                          <Button type="primary" htmlType="submit" loading={loading}>
                            保存配置
                          </Button>
                          <Button onClick={() => setEditingPaths({ type: null, paths: [] })}>
                            取消
                          </Button>
                        </Space>
                      </Form.Item>
                    </Form>
                  </Card>
                )}
              </>
            )}
          </div>
        </TabPane>

        <TabPane 
          tab={
            <span>
              <FileTextOutlined />
              限制设置
            </span>
          } 
          key="limits"
        >
          <div style={{ padding: '16px 0' }}>
            {securityInfo && (
              <Card 
                title={<span style={{ color: currentTheme.token?.colorText }}>文件操作限制设置</span>}
                style={{
                  backgroundColor: currentTheme.token?.colorBgContainer,
                  borderColor: currentTheme.token?.colorBorder
                }}
              >
                <Form form={limitForm} onFinish={handleLimitSubmit} layout="vertical">
                  <Row gutter={16}>
                    <Col span={12}>
                      <Form.Item
                        name="max_file_size_mb"
                        label={<span style={{ color: currentTheme.token?.colorText }}>最大文件大小 (MB)</span>}
                        rules={[{ required: true, min: 1, type: 'number', message: '请输入有效的文件大小' }]}
                      >
                        <InputNumber
                          min={1}
                          max={10000}
                          style={{ 
                            width: '100%',
                            backgroundColor: currentTheme.token?.colorBgContainer,
                            borderColor: currentTheme.token?.colorBorder,
                            color: currentTheme.token?.colorText
                          }}
                          placeholder="单位：MB"
                        />
                      </Form.Item>
                    </Col>
                    <Col span={12}>
                      <Form.Item
                        name="max_read_lines"
                        label={<span style={{ color: currentTheme.token?.colorText }}>最大读取行数</span>}
                        rules={[{ required: true, min: 1, type: 'number', message: '请输入有效的行数' }]}
                      >
                        <InputNumber
                          min={1}
                          max={100000}
                          style={{ 
                            width: '100%',
                            backgroundColor: currentTheme.token?.colorBgContainer,
                            borderColor: currentTheme.token?.colorBorder,
                            color: currentTheme.token?.colorText
                          }}
                          placeholder="单位：行"
                        />
                      </Form.Item>
                    </Col>
                  </Row>

                  <Form.Item
                    name="strict_mode"
                    label="严格模式"
                    valuePropName="checked"
                  >
                    <Switch
                      checkedChildren="严格"
                      unCheckedChildren="宽松"
                    />
                  </Form.Item>

                  <Form.Item>
                    <Button type="primary" htmlType="submit" loading={loading}>
                      更新限制设置
                    </Button>
                  </Form.Item>
                </Form>

                <Divider />

                <Alert
                  message="文件工具集限制配置说明"
                  description={
                    <div>
                      <p><strong>最大文件大小：</strong>统一限制所有文件工具可操作的单个文件大小，超过此大小的文件将被拒绝操作</p>
                      <p><strong>最大读取行数：</strong>统一限制所有文件工具读取文件时的最大行数，防止读取超大文件导致内存溢出</p>
                      <p><strong>严格模式：</strong>启用后所有文件工具只能访问明确配置的目录，禁用后可访问除禁止目录外的所有目录</p>
                    </div>
                  }
                  type="info"
                  showIcon
                />
              </Card>
            )}
          </div>
        </TabPane>
      </Tabs>

      <div style={{ textAlign: 'right', paddingTop: 16, borderTop: '1px solid #f0f0f0' }}>
        <Space>
          <Button icon={<ReloadOutlined />} onClick={reloadConfig} loading={loading}>
            重新加载配置
          </Button>
          <Button onClick={onCancel}>关闭</Button>
        </Space>
      </div>
    </Modal>
  );
};

export default FileToolsConfigModal;