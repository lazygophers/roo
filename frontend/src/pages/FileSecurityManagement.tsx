import React, { useState, useEffect, useCallback } from 'react';
import {
  Card,
  Button,
  Switch,
  Tag,
  Space,
  Modal,
  Form,
  Input,
  InputNumber,
  Row,
  Col,
  Statistic,
  Alert,
  Spin,
  Typography,
  Empty,
  Tabs,
  App,
  List,
  Tooltip,
  Badge,
} from 'antd';
import {
  SecurityScanOutlined,
  ReloadOutlined,
  EditOutlined,
  DeleteOutlined,
  InfoCircleOutlined,
  FolderOpenOutlined,
  LockOutlined,
  UnlockOutlined,
  SettingOutlined,
} from '@ant-design/icons';
import {
  apiClient,
  FileSecurityInfo,
  UpdatePathsRequest,
  UpdateLimitsRequest
} from '../api';
import { useTheme } from '../contexts/ThemeContext';
import './FileSecurityManagement.css';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { TabPane } = Tabs;
const { useApp } = App;

const FileSecurityManagement: React.FC = () => {
  const { currentTheme } = useTheme();
  const { message: messageApi } = useApp();
  const [loading, setLoading] = useState(false);
  const [securityInfo, setSecurityInfo] = useState<FileSecurityInfo | null>(null);
  const [editModal, setEditModal] = useState<{
    visible: boolean;
    type: 'paths' | 'limits' | null;
    configType?: string;
    title?: string;
  }>({ visible: false, type: null });
  
  const [form] = Form.useForm();

  // 加载文件安全配置信息
  const loadSecurityInfo = useCallback(async () => {
    setLoading(true);
    try {
      const response = await apiClient.getFileSecurityInfo();
      if (response.success && response.data) {
        // 解析返回的字符串数据
        const content = response.data;
        // 从返回的字符串中提取配置信息
        const lines = content.split('\n');
        const info: Partial<FileSecurityInfo> = {};
        
        let currentSection = '';
        const pathSections: Record<string, string[]> = {};
        
        lines.forEach((line: string) => {
          const trimmed = line.trim();
          if (trimmed.includes('可读取目录')) {
            currentSection = 'readable_directories';
            pathSections[currentSection] = [];
          } else if (trimmed.includes('可写入目录')) {
            currentSection = 'writable_directories';
            pathSections[currentSection] = [];
          } else if (trimmed.includes('可删除目录')) {
            currentSection = 'deletable_directories';
            pathSections[currentSection] = [];
          } else if (trimmed.includes('禁止访问目录')) {
            currentSection = 'forbidden_directories';
            pathSections[currentSection] = [];
          } else if (trimmed.includes('严格模式')) {
            info.strict_mode = trimmed.includes('严格模式');
          } else if (trimmed.includes('最大文件大小')) {
            const match = trimmed.match(/(\d+\.?\d*)\s*MB/);
            if (match) {
              info.max_file_size_mb = parseFloat(match[1]);
            }
          } else if (trimmed.includes('最大读取行数')) {
            const match = trimmed.match(/(\d+)\s*行/);
            if (match) {
              info.max_read_lines = parseInt(match[1]);
            }
          } else if (trimmed.startsWith('📁') || trimmed.startsWith('📝') || 
                     trimmed.startsWith('🗂️') || trimmed.startsWith('⛔')) {
            if (currentSection && pathSections[currentSection]) {
              const path = trimmed.replace(/^[📁📝🗂️⛔]\s*/, '');
              if (path) {
                pathSections[currentSection].push(path);
              }
            }
          }
        });
        
        const securityData: FileSecurityInfo = {
          readable_directories: pathSections.readable_directories || [],
          writable_directories: pathSections.writable_directories || [],
          deletable_directories: pathSections.deletable_directories || [],
          forbidden_directories: pathSections.forbidden_directories || [],
          max_file_size_mb: info.max_file_size_mb || 100,
          max_read_lines: info.max_read_lines || 10000,
          strict_mode: info.strict_mode || false
        };
        
        setSecurityInfo(securityData);
      } else {
        messageApi.error('获取文件安全配置失败: ' + response.message);
      }
    } catch (error) {
      console.error('Failed to load file security info:', error);
      messageApi.error('加载文件安全配置失败');
    } finally {
      setLoading(false);
    }
  }, [messageApi]);

  // 更新路径配置
  const updatePaths = async (configType: string, paths: string[]) => {
    try {
      setLoading(true);
      const request: UpdatePathsRequest = {
        config_type: configType as any,
        paths
      };
      
      const response = await apiClient.updateFileSecurityPaths(request);
      if (response.success) {
        messageApi.success(`${configType} 路径配置已更新`);
        loadSecurityInfo();
      } else {
        messageApi.error('更新失败: ' + response.message);
      }
    } catch (error) {
      messageApi.error('更新路径配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 更新限制配置
  const updateLimits = async (limitType: string, value: number | boolean) => {
    try {
      setLoading(true);
      const request: UpdateLimitsRequest = {
        limit_type: limitType as any,
        value
      };
      
      const response = await apiClient.updateFileSecurityLimits(request);
      if (response.success) {
        messageApi.success(`${limitType} 配置已更新`);
        loadSecurityInfo();
      } else {
        messageApi.error('更新失败: ' + response.message);
      }
    } catch (error) {
      messageApi.error('更新限制配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 重新加载配置
  const reloadConfig = async () => {
    try {
      setLoading(true);
      const response = await apiClient.reloadFileSecurityConfig();
      if (response.success) {
        messageApi.success('配置已重新加载');
        loadSecurityInfo();
      } else {
        messageApi.error('重新加载失败: ' + response.message);
      }
    } catch (error) {
      messageApi.error('重新加载配置失败');
    } finally {
      setLoading(false);
    }
  };

  // 打开编辑对话框
  const openEditModal = (type: 'paths' | 'limits', configType?: string, title?: string) => {
    setEditModal({ visible: true, type, configType, title });
    
    if (type === 'paths' && configType && securityInfo) {
      const paths = (securityInfo as any)[`${configType}_directories`] || [];
      form.setFieldsValue({ paths: paths.join('\n') });
    } else if (type === 'limits' && securityInfo) {
      form.setFieldsValue({
        max_file_size_mb: securityInfo.max_file_size_mb,
        max_read_lines: securityInfo.max_read_lines,
        strict_mode: securityInfo.strict_mode
      });
    }
  };

  // 处理编辑表单提交
  const handleEditSubmit = async () => {
    try {
      const values = await form.validateFields();
      
      if (editModal.type === 'paths' && editModal.configType) {
        const paths = values.paths ? values.paths.split('\n').filter((p: string) => p.trim()) : [];
        await updatePaths(editModal.configType, paths);
      } else if (editModal.type === 'limits') {
        if (values.max_file_size_mb !== undefined) {
          await updateLimits('max_file_size', values.max_file_size_mb * 1024 * 1024); // 转换为字节
        }
        if (values.max_read_lines !== undefined) {
          await updateLimits('max_read_lines', values.max_read_lines);
        }
        if (values.strict_mode !== undefined) {
          await updateLimits('strict_mode', values.strict_mode);
        }
      }
      
      setEditModal({ visible: false, type: null });
      form.resetFields();
    } catch (error) {
      console.error('Edit submit failed:', error);
    }
  };

  useEffect(() => {
    loadSecurityInfo();
  }, [loadSecurityInfo]);

  // 渲染路径列表组件
  const renderPathList = (title: string, paths: string[], configType: string, icon: React.ReactNode, color: string) => (
    <Card 
      size="small" 
      title={
        <Space>
          {icon}
          <span>{title}</span>
          <Badge count={paths.length} style={{ backgroundColor: color }} />
        </Space>
      }
      extra={
        <Button 
          type="text" 
          size="small" 
          icon={<EditOutlined />}
          onClick={() => openEditModal('paths', configType, title)}
        >
          编辑
        </Button>
      }
      style={{ marginBottom: 16 }}
    >
      {paths.length === 0 ? (
        <Empty description="暂无配置路径" image={Empty.PRESENTED_IMAGE_SIMPLE} />
      ) : (
        <List
          size="small"
          dataSource={paths}
          renderItem={(path) => (
            <List.Item>
              <Text code style={{ fontSize: 12, wordBreak: 'break-all' }}>
                {path}
              </Text>
            </List.Item>
          )}
        />
      )}
    </Card>
  );

  return (
    <div style={{ padding: '0 24px' }}>
      <div style={{ marginBottom: 24 }}>
        <Title level={2} style={{ color: currentTheme.token?.colorText }}>
          <SecurityScanOutlined /> 文件安全管理
        </Title>
        <Paragraph style={{ color: currentTheme.token?.colorTextSecondary }}>
          管理文件工具的安全配置，包括目录访问权限和操作限制
        </Paragraph>
      </div>

      {/* 状态卡片 */}
      {securityInfo && (
        <Row gutter={16} style={{ marginBottom: 24 }}>
          <Col span={6}>
            <Card>
              <Statistic
                title="可读取目录"
                value={securityInfo.readable_directories.length}
                prefix={<FolderOpenOutlined />}
                valueStyle={{ color: '#1890ff' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="可写入目录"
                value={securityInfo.writable_directories.length}
                prefix={<EditOutlined />}
                valueStyle={{ color: '#52c41a' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="可删除目录"
                value={securityInfo.deletable_directories.length}
                prefix={<DeleteOutlined />}
                valueStyle={{ color: '#faad14' }}
              />
            </Card>
          </Col>
          <Col span={6}>
            <Card>
              <Statistic
                title="禁止访问目录"
                value={securityInfo.forbidden_directories.length}
                prefix={<LockOutlined />}
                valueStyle={{ color: '#ff4d4f' }}
              />
            </Card>
          </Col>
        </Row>
      )}

      {/* 操作栏 */}
      <Card style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text strong>安全配置状态:</Text>
              <Tag color={securityInfo?.strict_mode ? 'red' : 'green'}>
                {securityInfo?.strict_mode ? '严格模式' : '宽松模式'}
              </Tag>
              <Tooltip title="严格模式下只能访问明确允许的目录">
                <InfoCircleOutlined />
              </Tooltip>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                icon={<SettingOutlined />}
                onClick={() => openEditModal('limits')}
              >
                限制设置
              </Button>
              <Button
                type="primary"
                icon={<ReloadOutlined />}
                onClick={reloadConfig}
                loading={loading}
              >
                重新加载
              </Button>
            </Space>
          </Col>
        </Row>
      </Card>

      {/* 配置内容 */}
      <Spin spinning={loading}>
        {!securityInfo ? (
          <Empty description="暂无安全配置信息" />
        ) : (
          <Tabs defaultActiveKey="paths" type="card">
            <TabPane tab="目录权限" key="paths">
              <Row gutter={16}>
                <Col span={12}>
                  {renderPathList(
                    '可读取目录',
                    securityInfo.readable_directories,
                    'readable',
                    <FolderOpenOutlined />,
                    '#1890ff'
                  )}
                  {renderPathList(
                    '可删除目录',
                    securityInfo.deletable_directories,
                    'deletable',
                    <DeleteOutlined />,
                    '#faad14'
                  )}
                </Col>
                <Col span={12}>
                  {renderPathList(
                    '可写入目录',
                    securityInfo.writable_directories,
                    'writable',
                    <EditOutlined />,
                    '#52c41a'
                  )}
                  {renderPathList(
                    '禁止访问目录',
                    securityInfo.forbidden_directories,
                    'forbidden',
                    <LockOutlined />,
                    '#ff4d4f'
                  )}
                </Col>
              </Row>
            </TabPane>
            
            <TabPane tab="安全限制" key="limits">
              <Row gutter={16}>
                <Col span={8}>
                  <Card title="文件大小限制" size="small">
                    <Statistic
                      title="最大文件大小"
                      value={securityInfo.max_file_size_mb}
                      suffix="MB"
                      precision={1}
                      valueStyle={{ color: '#1890ff' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="读取行数限制" size="small">
                    <Statistic
                      title="最大读取行数"
                      value={securityInfo.max_read_lines}
                      suffix="行"
                      valueStyle={{ color: '#52c41a' }}
                    />
                  </Card>
                </Col>
                <Col span={8}>
                  <Card title="安全模式" size="small">
                    <div style={{ textAlign: 'center', padding: '20px 0' }}>
                      <div style={{ fontSize: 24, marginBottom: 8 }}>
                        {securityInfo.strict_mode ? <LockOutlined style={{ color: '#ff4d4f' }} /> : <UnlockOutlined style={{ color: '#52c41a' }} />}
                      </div>
                      <Text strong style={{ color: securityInfo.strict_mode ? '#ff4d4f' : '#52c41a' }}>
                        {securityInfo.strict_mode ? '严格模式' : '宽松模式'}
                      </Text>
                    </div>
                  </Card>
                </Col>
              </Row>
              
              <Alert
                style={{ marginTop: 16 }}
                message="安全限制说明"
                description={
                  <ul style={{ paddingLeft: 20, marginTop: 8 }}>
                    <li><strong>文件大小限制:</strong> 单个文件的最大大小限制，超过此限制的文件无法读取</li>
                    <li><strong>读取行数限制:</strong> 单次文件读取的最大行数，防止内存溢出</li>
                    <li><strong>严格模式:</strong> 启用后只能访问明确允许的目录，禁用后除禁止目录外都可访问</li>
                  </ul>
                }
                type="info"
                showIcon
              />
            </TabPane>
          </Tabs>
        )}
      </Spin>

      {/* 编辑对话框 */}
      <Modal
        title={editModal.title ? `编辑${editModal.title}` : '编辑配置'}
        open={editModal.visible}
        onCancel={() => {
          setEditModal({ visible: false, type: null });
          form.resetFields();
        }}
        onOk={handleEditSubmit}
        width={600}
        confirmLoading={loading}
      >
        <Form form={form} layout="vertical">
          {editModal.type === 'paths' && (
            <Form.Item
              label="目录路径（每行一个）"
              name="paths"
              rules={[{ required: false, message: '请输入目录路径' }]}
            >
              <TextArea
                rows={10}
                placeholder="请输入目录路径，每行一个&#10;例如：&#10;/home/user/documents&#10;/tmp&#10;/var/log"
              />
            </Form.Item>
          )}
          
          {editModal.type === 'limits' && (
            <>
              <Form.Item
                label="最大文件大小 (MB)"
                name="max_file_size_mb"
                rules={[{ required: true, message: '请输入最大文件大小' }]}
              >
                <InputNumber
                  min={1}
                  max={1000}
                  precision={1}
                  style={{ width: '100%' }}
                  addonAfter="MB"
                />
              </Form.Item>
              
              <Form.Item
                label="最大读取行数"
                name="max_read_lines"
                rules={[{ required: true, message: '请输入最大读取行数' }]}
              >
                <InputNumber
                  min={100}
                  max={100000}
                  style={{ width: '100%' }}
                  addonAfter="行"
                />
              </Form.Item>
              
              <Form.Item
                label="严格模式"
                name="strict_mode"
                valuePropName="checked"
              >
                <Switch
                  checkedChildren="启用"
                  unCheckedChildren="禁用"
                />
              </Form.Item>
            </>
          )}
        </Form>
      </Modal>
    </div>
  );
};

export default FileSecurityManagement;