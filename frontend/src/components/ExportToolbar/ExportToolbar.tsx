import React, { useState } from 'react';
import { 
  Card, 
  Button, 
  Space, 
  Typography, 
  Tag, 
  Divider, 
  Row, 
  Col, 
  message,
  Modal,
  Form,
  Input,
  Checkbox
} from 'antd';
import { 
  DownloadOutlined, 
  ClearOutlined, 
  CodeOutlined,
  FileTextOutlined,
  BookOutlined,
  SaveOutlined
} from '@ant-design/icons';
import { SelectedItem, ModelRuleBinding } from '../../types/selection';
import { apiClient, FileMetadata } from '../../api';

const { Text } = Typography;

interface ExportToolbarProps {
  selectedItems: SelectedItem[];
  onClearSelection: () => void;
  onExport: () => void;
  modelRuleBindings: ModelRuleBinding[];
  modelRules: Record<string, FileMetadata[]>;
}

const ExportToolbar: React.FC<ExportToolbarProps> = ({
  selectedItems,
  onClearSelection,
  onExport,
  modelRuleBindings,
  modelRules
}) => {
  const [saveModalVisible, setSaveModalVisible] = useState(false);
  const [saveLoading, setSaveLoading] = useState(false);
  const [form] = Form.useForm();
  const modelCount = selectedItems.filter(item => item.type === 'model').length;
  const commandCount = selectedItems.filter(item => item.type === 'command').length;
  const ruleCount = selectedItems.filter(item => item.type === 'rule').length;
  const totalCount = selectedItems.length;

  const handleExport = () => {
    if (totalCount === 0) {
      message.warning('请先选择要导出的项目');
      return;
    }
    
    // 这里暂不实现具体的导出逻辑，只显示提示
    message.info(`准备导出 ${totalCount} 个项目（模拟功能）`);
    onExport();
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
            
            <Button
              size="small"
              icon={<SaveOutlined />}
              onClick={handleSaveConfiguration}
              disabled={totalCount === 0}
            >
              保存配置
            </Button>
            
            <Button
              size="small"
              type="primary"
              icon={<DownloadOutlined />}
              onClick={handleExport}
              disabled={totalCount === 0}
            >
              导出 ({totalCount})
            </Button>
          </Space>
        </Col>
      </Row>

      {/* 选中项详情（当有选择时显示） */}
      {totalCount > 0 && (
        <div style={{ marginTop: 12, paddingTop: 12, borderTop: '1px solid #f0f0f0' }}>
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
            name="name"
            label="配置名称"
            rules={[
              { required: true, message: '请输入配置名称' },
              { min: 2, message: '配置名称至少2个字符' },
              { max: 50, message: '配置名称不能超过50个字符' }
            ]}
          >
            <Input placeholder="请输入配置名称，例如：我的开发配置" />
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
            backgroundColor: '#f5f5f5', 
            borderRadius: 6 
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
    </Card>
  );
};

export default ExportToolbar;