import React, { useState, useEffect } from 'react';
import {
  Card,
  Button,
  Space,
  Typography,
  Tag,
  Divider,
  Row,
  Col,
  Modal,
  Form,
  Input,
  AutoComplete,
  Checkbox,
  theme,
  Select,
  Tooltip,
  Popconfirm,
  App
} from 'antd';
import { 
  DownloadOutlined, 
  ClearOutlined, 
  CodeOutlined,
  FileTextOutlined,
  BookOutlined,
  SaveOutlined,
  SettingOutlined,
  DeleteOutlined,
  RocketOutlined,
  UserOutlined,
  RestOutlined,
  FolderOutlined
} from '@ant-design/icons';
import { SelectedItem, ModelRuleBinding } from '../../types/selection';
import { apiClient, FileMetadata, DeployTarget, DeployRequest, EnvironmentInfo } from '../../api';

const { Text } = Typography;
const { Option } = Select;

interface ConfigurationData {
  name: string;
  description?: string;
  selectedItems: SelectedItem[];
  modelRuleBindings: ModelRuleBinding[];
  modelRules: Record<string, FileMetadata[]>;
  created_at?: string;
  updated_at?: string;
}

interface ExportToolbarProps {
  selectedItems: SelectedItem[];
  onClearSelection: () => void;
  onExport: () => void;
  modelRuleBindings: ModelRuleBinding[];
  modelRules: Record<string, FileMetadata[]>;
  onLoadConfiguration?: (config: ConfigurationData) => void;
  environmentInfo?: EnvironmentInfo | null;
}

const ExportToolbar: React.FC<ExportToolbarProps> = ({
  selectedItems,
  onClearSelection,
  onExport,
  modelRuleBindings,
  modelRules,
  onLoadConfiguration,
  environmentInfo
}) => {
  const { token } = theme.useToken();
  const { message } = App.useApp();
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [configManageModalVisible, setConfigManageModalVisible] = useState(false);
  const [deployModalVisible, setDeployModalVisible] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [deployLoading, setDeployLoading] = useState(false);
  const [configurations, setConfigurations] = useState<ConfigurationData[]>([]);
  const [deployTargets, setDeployTargets] = useState<Record<string, DeployTarget>>({});
  const [selectedDeployTargets, setSelectedDeployTargets] = useState<string[]>([]);
  const [configurationsLoading, setConfigurationsLoading] = useState(false);
  const [selectedConfigName, setSelectedConfigName] = useState<string | null>(null);
  const [cleanupLoading, setCleanupLoading] = useState(false);
  const [exportLoading, setExportLoading] = useState(false);
  const [form] = Form.useForm();
  const [deployForm] = Form.useForm();
  const modelCount = selectedItems.filter(item => item.type === 'model').length;
  const commandCount = selectedItems.filter(item => item.type === 'command').length;
  const ruleCount = selectedItems.filter(item => item.type === 'rule').length;
  const totalCount = selectedItems.length;

  // 加载配置列表
  const loadConfigurations = async () => {
    try {
      setConfigurationsLoading(true);
      const result = await apiClient.getConfigurations();
      if (result.success) {
        setConfigurations(result.data || []);
      }
    } catch (error) {
      message.error('获取配置列表失败');
    } finally {
      setConfigurationsLoading(false);
    }
  };

  // 检测操作系统
  const getOperatingSystem = () => {
    const platform = navigator.platform.toLowerCase();
    if (platform.includes('mac')) return 'macOS';
    if (platform.includes('win')) return 'Windows';
    if (platform.includes('linux')) return 'Linux';
    return 'Unknown';
  };

  // 加载部署目标
  const loadDeployTargets = async () => {
    try {
      const result = await apiClient.getDeployTargets();
      setDeployTargets(result);
      // 默认选择所有目标
      const defaultTargets = Object.keys(result);
      setSelectedDeployTargets(defaultTargets);
    } catch (error) {
      message.error('获取部署目标失败');
    }
  };

  // 组件加载时获取配置列表和部署目标
  useEffect(() => {
    loadConfigurations();
    loadDeployTargets();
  }, []);

  const handleExport = async () => {
    // 检查是否选择了指令
    const hasCommands = selectedItems.some(item => item.type === 'command');

    if (!hasCommands) {
      // 未选择指令时，自动下载 custom_modes.yaml
      await handleDownloadCustomModes();
      return;
    }

    if (totalCount === 0) {
      message.warning('请先选择要导出的项目');
      return;
    }

    // 这里暂不实现具体的导出逻辑，只显示提示
    message.info(`准备导出 ${totalCount} 个项目（模拟功能）`);
    onExport();
  };

  const handleDownloadCustomModes = async () => {
    try {
      setExportLoading(true);

      // 构建部署请求，和部署功能使用相同的逻辑
      const roleItem = selectedItems.find(item => item.type === 'role');

      const deployRequest = {
        selected_models: selectedItems
          .filter(item => item.type === 'model')
          .map(item => item.id),
        selected_commands: [], // 指令为空
        selected_rules: selectedItems
          .filter(item => item.type === 'rule')
          .map(item => item.id),
        model_rule_bindings: modelRuleBindings,
        selected_role: roleItem?.id,
        deploy_targets: ['vscode'] // 默认导出到 vscode 目标
      };

      // 调用导出 API
      const response = await fetch('/api/deploy/export', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(deployRequest),
      });

      if (!response.ok) {
        throw new Error('生成配置文件失败');
      }

      const result = await response.json();

      if (result.success) {
        // 创建隐藏的下载链接并触发点击
        const downloadUrl = result.data.download_url;
        const link = document.createElement('a');
        link.href = downloadUrl;
        link.download = result.data.filename;
        link.style.display = 'none';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        const isCompressed = result.data.filename.endsWith('.tar.gz');
        const fileType = isCompressed ? '配置压缩包' : 'YAML文件';
        message.success(`${fileType} ${result.data.filename} 下载已开始`);
      } else {
        message.error('生成配置文件失败：' + result.message);
      }
    } catch (error) {
      console.error('Export error:', error);
      message.error('导出失败：' + (error instanceof Error ? error.message : '未知错误'));
    } finally {
      setExportLoading(false);
    }
  };


  const handleDeploy = () => {
    if (totalCount === 0) {
      message.warning('请先选择要部署的项目');
      return;
    }
    setDeployModalVisible(true);
  };

  const handleDeployConfirm = async () => {
    try {
      setDeployLoading(true);
      
      // 构建部署请求
      const roleItem = selectedItems.find(item => item.type === 'role');
      
      const deployRequest: DeployRequest = {
        selected_models: selectedItems
          .filter(item => item.type === 'model')
          .map(item => item.id),
        selected_commands: selectedItems
          .filter(item => item.type === 'command')
          .map(item => item.id),
        selected_rules: selectedItems
          .filter(item => item.type === 'rule')
          .map(item => item.id),
        model_rule_bindings: modelRuleBindings,
        selected_role: roleItem?.id,
        deploy_targets: selectedDeployTargets
      };

      const result = await apiClient.deployCustomModes(deployRequest);
      
      if (result.success) {
        message.success(`部署成功！已部署到 ${result.deployed_files.length} 个目标位置`);
        if (result.errors.length > 0) {
          result.errors.forEach(error => {
            message.error(error);
          });
        }
      } else {
        message.error(`部署失败: ${result.message}`);
      }
      
      setDeployModalVisible(false);
      
    } catch (error: any) {
      message.error('部署失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setDeployLoading(false);
    }
  };

  const handleSaveConfiguration = () => {
    if (totalCount === 0) {
      message.warning('请先选择要保存的项目');
      return;
    }
    setSaveModalVisible(true);
  };

  const handleSaveModalCancel = () => {
    setSaveModalVisible(false);
    form.resetFields();
  };

  const handleSaveModalOk = async () => {
    try {
      const values = await form.validateFields();
      setSaveLoading(true);

      const configData = {
        name: values.name,
        description: values.description || '',
        selectedItems: selectedItems,
        modelRuleBindings: modelRuleBindings,
        modelRules: modelRules,
        overwrite: values.overwrite || false
      };

      const result = await apiClient.saveConfiguration(configData);
      
      if (result.success) {
        message.success(result.message);
        setSaveModalVisible(false);
        form.resetFields();
        setSelectedConfigName(null);
        // 重新加载配置列表
        await loadConfigurations();
      } else {
        message.error(result.message || '保存配置失败');
      }
    } catch (error: any) {
      if (error.response?.status === 409) {
        message.error('配置名称已存在，请启用覆盖选项或使用其他名称');
      } else {
        message.error('保存配置失败: ' + (error.message || '未知错误'));
      }
    } finally {
      setSaveLoading(false);
    }
  };

  // 处理配置选择
  const handleConfigSelect = async (configName: string | null) => {
    setSelectedConfigName(configName);
    if (configName) {
      const config = configurations.find(c => c.name === configName);
      if (config) {
        form.setFieldsValue({
          name: config.name,
          description: config.description,
          overwrite: true
        });
      }
    } else {
      form.setFieldsValue({
        name: '',
        description: '',
        overwrite: false
      });
    }
  };

  // 加载配置并应用到当前选择
  const handleLoadConfiguration = async (configName: string) => {
    try {
      const result = await apiClient.getConfiguration(configName);
      if (result.success && onLoadConfiguration) {
        onLoadConfiguration(result.data);
        message.success(`已加载配置: ${configName}`);
      }
    } catch (error) {
      message.error('加载配置失败');
    }
  };

  // 删除配置
  const handleDeleteConfiguration = async (configName: string) => {
    try {
      const result = await apiClient.deleteConfiguration(configName);
      if (result.success) {
        message.success(`已删除配置: ${configName}`);
        await loadConfigurations();
        if (selectedConfigName === configName) {
          setSelectedConfigName(null);
          form.resetFields();
        }
      }
    } catch (error) {
      message.error('删除配置失败');
    }
  };

  // 打开配置管理对话框
  const handleConfigManage = () => {
    setConfigManageModalVisible(true);
    loadConfigurations();
  };

  // 清空模型配置
  const handleCleanupModels = async () => {
    try {
      setCleanupLoading(true);
      
      const result = await apiClient.cleanupConfigurations({
        cleanup_type: 'models',
        deploy_targets: selectedDeployTargets
      });

      if (result.success) {
        message.success(`清空成功！已清理 ${result.cleaned_items.length} 个模型配置文件`);
        if (result.errors.length > 0) {
          result.errors.forEach(error => {
            message.error(error);
          });
        }
      } else {
        message.error(`清空失败: ${result.message}`);
      }

    } catch (error: any) {
      message.error('清空失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCleanupLoading(false);
    }
  };

  // 清空目录（包括模型配置和命令文件）
  const handleCleanupDirectories = async () => {
    try {
      setCleanupLoading(true);
      
      const result = await apiClient.cleanupConfigurations({
        cleanup_type: 'directories',
        deploy_targets: selectedDeployTargets
      });

      if (result.success) {
        message.success(`清空成功！已清理 ${result.cleaned_items.length} 个文件和目录`);
        if (result.errors.length > 0) {
          result.errors.forEach(error => {
            message.error(error);
          });
        }
      } else {
        message.error(`清空失败: ${result.message}`);
      }

    } catch (error: any) {
      message.error('清空失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setCleanupLoading(false);
    }
  };

  return (
    <Card 
      size="small"
      style={{ marginBottom: 16 }}
      styles={{ body: { padding: '12px 16px' } }}
    >
      <Row justify="space-between" align="middle">
        <Col flex="1">
          <Space split={<Divider type="vertical" />}>
            <div>
              <Text strong>导出工具栏</Text>
            </div>
            
            {/* 选择统计 */}
            <div>
              <Space>
                <Text type="secondary">已选择:</Text>
                {modelCount > 0 && (
                  <Tag color="green" icon={<CodeOutlined />}>
                    {modelCount} 个模型
                  </Tag>
                )}
                {commandCount > 0 && (
                  <Tag color="blue" icon={<FileTextOutlined />}>
                    {commandCount} 个指令
                  </Tag>
                )}
                {ruleCount > 0 && (
                  <Tag color="purple" icon={<BookOutlined />}>
                    {ruleCount} 个规则
                  </Tag>
                )}
                {totalCount === 0 && (
                  <Text type="secondary">无</Text>
                )}
              </Space>
            </div>
          </Space>
        </Col>

        {/* 操作按钮 */}
        <Col>
          <Space>
            <Button
              size="small"
              icon={<ClearOutlined />}
              onClick={onClearSelection}
              disabled={totalCount === 0}
            >
              清空选择
            </Button>
            
            <Tooltip title={
              !environmentInfo?.tool_edit_allowed ? '远程环境下配置保存功能被禁用' :
              totalCount === 0 ? '请先选择要保存的项目' : '保存当前配置'
            }>
              <Button
                size="small"
                icon={<SaveOutlined />}
                onClick={handleSaveConfiguration}
                disabled={totalCount === 0 || !environmentInfo?.tool_edit_allowed}
              >
                保存配置
              </Button>
            </Tooltip>
            
            <Tooltip title={
              !environmentInfo?.tool_edit_allowed ? '远程环境下VS Code扩展部署功能被禁用' :
              totalCount === 0 ? '请先选择要部署的项目' : '部署配置到VS Code扩展'
            }>
              <Button
                size="small"
                icon={<RocketOutlined />}
                onClick={handleDeploy}
                disabled={totalCount === 0 || !environmentInfo?.tool_edit_allowed}
                type="primary"
                style={{ background: '#722ed1' }}
              >
                部署配置
              </Button>
            </Tooltip>
            
            <Tooltip title={
              !environmentInfo?.tool_edit_allowed ? '远程环境下配置管理功能被禁用' : '管理已保存的配置'
            }>
              <Button
                size="small"
                icon={<SettingOutlined />}
                onClick={handleConfigManage}
                disabled={!environmentInfo?.tool_edit_allowed}
              >
                配置管理
              </Button>
            </Tooltip>
            
            <Tooltip title={
              selectedItems.some(item => item.type === 'command')
                ? '导出配置压缩包（包含 custom_modes.yaml 和 .roo/commands/ 目录）'
                : '下载 custom_modes.yaml 文件'
            }>
              <Button
                size="small"
                type="primary"
                icon={<DownloadOutlined />}
                onClick={handleExport}
                loading={exportLoading}
              >
                {selectedItems.some(item => item.type === 'command')
                  ? `导出 (${totalCount})`
                  : '导出 YAML'
                }
              </Button>
            </Tooltip>
          </Space>
        </Col>
      </Row>

      {/* 选中项详情（当有选择时显示） */}
      {totalCount > 0 && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${token.colorBorderSecondary}` }}>
          <Text type="secondary" style={{ fontSize: 12 }}>
            选中的项目将被导出为配置文件，包含所有相关的元数据信息
          </Text>
          {totalCount > 5 && (
            <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
              （仅显示部分选中项）
            </Text>
          )}
          <div style={{ marginTop: 4 }}>
            <Space wrap size="small">
              {selectedItems.slice(0, 5).map((item) => (
                <Tag
                  key={item.id}
                  color={
                    item.type === 'model' ? 'green' :
                    item.type === 'command' ? 'blue' : 'purple'
                  }
                  style={{ fontSize: 10 }}
                >
                  {item.name}
                </Tag>
              ))}
              {totalCount > 5 && (
                <Tag color="default" style={{ fontSize: 10 }}>
                  +{totalCount - 5} 更多
                </Tag>
              )}
            </Space>
          </div>
        </div>
      )}

      {/* 保存配置对话框 */}
      <Modal
        title="保存配置"
        open={saveModalVisible}
        onOk={handleSaveModalOk}
        onCancel={handleSaveModalCancel}
        confirmLoading={saveLoading}
        width={500}
      >
        <Form
          form={form}
          layout="vertical"
          initialValues={{ overwrite: false }}
        >
          <Form.Item
            label="选择已有配置（可选）"
          >
            <Select
              value={selectedConfigName}
              onChange={handleConfigSelect}
              placeholder="选择已有配置进行修改，或留空创建新配置"
              allowClear
              loading={configurationsLoading}
            >
              {configurations.map(config => (
                <Option key={config.name} value={config.name}>
                  <div>
                    <strong>{config.name}</strong>
                    {config.description && (
                      <div style={{ fontSize: 12, color: token.colorTextTertiary }}>
                        {config.description}
                      </div>
                    )}
                  </div>
                </Option>
              ))}
            </Select>
          </Form.Item>

          <Form.Item
            name="name"
            label="配置名称"
            rules={[
              { required: true, message: '请输入配置名称' },
              { min: 2, message: '配置名称至少2个字符' },
              { max: 50, message: '配置名称不能超过50个字符' }
            ]}
          >
            <AutoComplete
              placeholder="请输入配置名称，例如：我的开发配置"
              options={configurations.map(config => ({
                value: config.name,
                label: (
                  <div>
                    <div>{config.name}</div>
                    {config.description && (
                      <div style={{ fontSize: 12, color: token.colorTextTertiary }}>
                        {config.description}
                      </div>
                    )}
                  </div>
                )
              }))}
              filterOption={(inputValue, option) =>
                option?.value?.toLowerCase().includes(inputValue.toLowerCase()) || false
              }
              onSelect={(value) => {
                const config = configurations.find(c => c.name === value);
                if (config) {
                  form.setFieldsValue({
                    name: config.name,
                    description: config.description,
                    overwrite: true
                  });
                }
              }}
            />
          </Form.Item>

          <Form.Item
            name="description"
            label="配置描述"
          >
            <Input.TextArea 
              placeholder="请输入配置描述（可选）" 
              rows={3}
              showCount
              maxLength={200}
            />
          </Form.Item>

          <Form.Item
            name="overwrite"
            valuePropName="checked"
          >
            <Checkbox>如果配置名称已存在，允许覆盖</Checkbox>
          </Form.Item>

          <div style={{ 
            marginTop: 16, 
            padding: 12, 
            backgroundColor: token.colorFillAlter, 
            borderRadius: 6,
            border: `1px solid ${token.colorBorderSecondary}`
          }}>
            <Text type="secondary" style={{ fontSize: 12 }}>
              <strong>将要保存的内容：</strong>
            </Text>
            <div style={{ marginTop: 4 }}>
              <Space wrap size="small">
                {modelCount > 0 && (
                  <Tag color="green">
                    {modelCount} 个模型
                  </Tag>
                )}
                {commandCount > 0 && (
                  <Tag color="blue">
                    {commandCount} 个指令
                  </Tag>
                )}
                {ruleCount > 0 && (
                  <Tag color="purple">
                    {ruleCount} 个规则
                  </Tag>
                )}
                {modelRuleBindings.length > 0 && (
                  <Tag color="orange">
                    {modelRuleBindings.length} 个模型-规则绑定
                  </Tag>
                )}
              </Space>
            </div>
          </div>
        </Form>
      </Modal>

      {/* 配置管理对话框 */}
      <Modal
        title="配置管理"
        open={configManageModalVisible}
        onCancel={() => setConfigManageModalVisible(false)}
        footer={[
          <Button key="close" onClick={() => setConfigManageModalVisible(false)}>
            关闭
          </Button>
        ]}
        width={700}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            管理已保存的配置，您可以加载配置到当前选择或删除不需要的配置
          </Text>
        </div>
        
        {configurationsLoading ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Text>加载中...</Text>
          </div>
        ) : configurations.length === 0 ? (
          <div style={{ textAlign: 'center', padding: 40 }}>
            <Text type="secondary">暂无已保存的配置</Text>
          </div>
        ) : (
          <div style={{ maxHeight: 400, overflowY: 'auto' }}>
            {configurations.map(config => (
              <Card
                key={config.name}
                size="small"
                style={{ marginBottom: 8 }}
                title={
                  <div>
                    <strong>{config.name}</strong>
                    {config.updated_at && (
                      <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
                        更新于: {new Date(config.updated_at).toLocaleString()}
                      </Text>
                    )}
                  </div>
                }
                extra={
                  <Space>
                    <Tooltip title={!environmentInfo?.tool_edit_allowed ? '远程环境下配置加载功能被禁用' : '加载配置到当前选择'}>
                      <Button
                        size="small"
                        type="primary"
                        ghost
                        icon={<DownloadOutlined />}
                        onClick={() => {
                          handleLoadConfiguration(config.name);
                          setConfigManageModalVisible(false);
                        }}
                        disabled={!environmentInfo?.tool_edit_allowed}
                      >
                        加载
                      </Button>
                    </Tooltip>
                    <Popconfirm
                      title="确认删除"
                      description={`确定要删除配置 "${config.name}" 吗？此操作不可撤销。`}
                      onConfirm={() => handleDeleteConfiguration(config.name)}
                      okText="确定"
                      cancelText="取消"
                      disabled={!environmentInfo?.tool_edit_allowed}
                    >
                      <Tooltip title={!environmentInfo?.tool_edit_allowed ? '远程环境下配置删除功能被禁用' : '删除配置'}>
                        <Button
                          size="small"
                          danger
                          icon={<DeleteOutlined />}
                          disabled={!environmentInfo?.tool_edit_allowed}
                        >
                          删除
                        </Button>
                      </Tooltip>
                    </Popconfirm>
                  </Space>
                }
              >
                {config.description && (
                  <div style={{ marginBottom: 8 }}>
                    <Text>{config.description}</Text>
                  </div>
                )}
                
                <div>
                  <Space wrap size="small">
                    {config.selectedItems && (
                      <>
                        {config.selectedItems.filter(item => item.type === 'model').length > 0 && (
                          <Tag color="green">
                            {config.selectedItems.filter(item => item.type === 'model').length} 个模型
                          </Tag>
                        )}
                        {config.selectedItems.filter(item => item.type === 'command').length > 0 && (
                          <Tag color="blue">
                            {config.selectedItems.filter(item => item.type === 'command').length} 个指令
                          </Tag>
                        )}
                        {config.selectedItems.filter(item => item.type === 'rule').length > 0 && (
                          <Tag color="purple">
                            {config.selectedItems.filter(item => item.type === 'rule').length} 个规则
                          </Tag>
                        )}
                      </>
                    )}
                    {config.modelRuleBindings && config.modelRuleBindings.length > 0 && (
                      <Tag color="orange">
                        {config.modelRuleBindings.length} 个绑定
                      </Tag>
                    )}
                  </Space>
                </div>
              </Card>
            ))}
          </div>
        )}
      </Modal>

      {/* 部署模态框 */}
      <Modal
        title={
          <Space>
            <RocketOutlined style={{ color: '#722ed1' }} />
            部署配置到VS Code扩展
          </Space>
        }
        open={deployModalVisible}
        onCancel={() => setDeployModalVisible(false)}
        confirmLoading={deployLoading}
        width={600}
        footer={[
          <Popconfirm
            key="cleanup-models"
            title="清空模型配置"
            description="确定要清空选中目标的模型配置文件吗？"
            onConfirm={handleCleanupModels}
            okText="确定"
            cancelText="取消"
            disabled={cleanupLoading || !environmentInfo?.tool_edit_allowed}
          >
            <Tooltip title={!environmentInfo?.tool_edit_allowed ? '远程环境下清空功能被禁用' : '清空模型配置'}>
              <Button
                icon={<RestOutlined />}
                loading={cleanupLoading}
                danger
                disabled={!environmentInfo?.tool_edit_allowed}
              >
                清空模型
              </Button>
            </Tooltip>
          </Popconfirm>,
          <Popconfirm
            key="cleanup-directories"
            title="清空所有配置"
            description="确定要清空选中目标的配置文件和命令目录吗？此操作不可撤销。"
            onConfirm={handleCleanupDirectories}
            okText="确定"
            cancelText="取消"
            disabled={cleanupLoading || !environmentInfo?.tool_edit_allowed}
          >
            <Tooltip title={!environmentInfo?.tool_edit_allowed ? '远程环境下清空功能被禁用' : '清空所有配置和目录'}>
              <Button
                icon={<FolderOutlined />}
                loading={cleanupLoading}
                danger
                disabled={!environmentInfo?.tool_edit_allowed}
              >
                清空目录
              </Button>
            </Tooltip>
          </Popconfirm>,
          <Button key="cancel" onClick={() => setDeployModalVisible(false)}>
            取消
          </Button>,
          <Tooltip title={!environmentInfo?.tool_edit_allowed ? '远程环境下部署功能被禁用' : '确认部署到VS Code扩展'}>
            <Button
              key="deploy"
              type="primary"
              loading={deployLoading}
              onClick={handleDeployConfirm}
              disabled={!environmentInfo?.tool_edit_allowed}
            >
              确认部署
            </Button>
          </Tooltip>
        ]}
      >
        <div style={{ marginBottom: 16 }}>
          <Text type="secondary">
            将当前选择的配置生成为custom_modes.yaml并部署到指定的VS Code扩展目录
          </Text>
          <div style={{ marginTop: 8 }}>
            <Tag color="blue">当前操作系统: {getOperatingSystem()}</Tag>
            <Text type="secondary" style={{ fontSize: 12, marginLeft: 8 }}>
              路径将根据您的操作系统自动调整
            </Text>
          </div>
        </div>

        {/* 当前选择概览 */}
        <Card size="small" style={{ marginBottom: 16 }}>
          <div style={{ marginBottom: 8 }}>
            <Text strong>当前选择概览：</Text>
          </div>
          <Space wrap>
            {modelCount > 0 && (
              <Tag color="green" icon={<CodeOutlined />}>
                {modelCount} 个模型
              </Tag>
            )}
            {commandCount > 0 && (
              <Tag color="blue" icon={<FileTextOutlined />}>
                {commandCount} 个指令
              </Tag>
            )}
            {ruleCount > 0 && (
              <Tag color="purple" icon={<BookOutlined />}>
                {ruleCount} 个规则
              </Tag>
            )}
            {selectedItems.filter(item => item.type === 'role').length > 0 && (
              <Tag color="orange" icon={<UserOutlined />}>
                {selectedItems.filter(item => item.type === 'role').length} 个角色
              </Tag>
            )}
          </Space>
        </Card>

        {/* 部署目标选择 */}
        <Form form={deployForm} layout="vertical">
          <Form.Item 
            label="选择部署目标" 
            name="deploy_targets"
            rules={[{ required: true, message: '请选择至少一个部署目标' }]}
          >
            <Checkbox.Group 
              value={selectedDeployTargets}
              onChange={setSelectedDeployTargets}
              style={{ width: '100%' }}
            >
              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                {Object.entries(deployTargets).map(([key, target]) => (
                  <div key={key} style={{ 
                    padding: 8, 
                    border: `1px solid ${token.colorBorderSecondary}`,
                    borderRadius: 4,
                    backgroundColor: selectedDeployTargets.includes(key) 
                      ? token.colorFillSecondary 
                      : 'transparent'
                  }}>
                    <Checkbox value={key} style={{ width: '100%' }}>
                      <div>
                        <div style={{ fontWeight: 500 }}>{target.name}</div>
                        <div style={{ fontSize: 11, color: token.colorTextTertiary, marginTop: 2 }}>
                          {target.description}
                        </div>
                        <div style={{ fontSize: 10, color: token.colorTextTertiary, marginTop: 2 }}>
                          路径: {target.path}
                        </div>
                      </div>
                    </Checkbox>
                  </div>
                ))}
              </div>
            </Checkbox.Group>
          </Form.Item>
        </Form>

        <div style={{ marginTop: 16, padding: 8, backgroundColor: token.colorFillTertiary, borderRadius: 4 }}>
          <Text style={{ fontSize: 12, color: token.colorTextSecondary }}>
            💡 提示：部署将会自动拼接before/after钩子、选中的规则到模型的customInstructions中，
            然后生成custom_modes.yaml文件并复制到选定的VS Code扩展目录。
          </Text>
        </div>
      </Modal>
    </Card>
  );
};

export default ExportToolbar;