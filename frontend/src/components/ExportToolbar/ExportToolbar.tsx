import React from 'react';
import { 
  Card, 
  Button, 
  Space, 
  Typography, 
  Tag, 
  Divider, 
  Row, 
  Col, 
  message 
} from 'antd';
import { 
  DownloadOutlined, 
  ClearOutlined, 
  CodeOutlined,
  FileTextOutlined,
  BookOutlined
} from '@ant-design/icons';
import { SelectedItem } from '../../types/selection';

const { Text } = Typography;

interface ExportToolbarProps {
  selectedItems: SelectedItem[];
  onClearSelection: () => void;
  onExport: () => void;
}

const ExportToolbar: React.FC<ExportToolbarProps> = ({
  selectedItems,
  onClearSelection,
  onExport
}) => {
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
    </Card>
  );
};

export default ExportToolbar;