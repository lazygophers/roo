import React, { useState } from 'react';
import { Row, Col, Tabs, TabsProps } from 'antd';
import { CodeOutlined, FileTextOutlined, BookOutlined } from '@ant-design/icons';
import ModesList from '../components/ConfigTabs/ModesList';
import CommandsList from '../components/ConfigTabs/CommandsList';
import RulesList from '../components/ConfigTabs/RulesList';
import PreviewPanel from '../components/Preview/PreviewPanel';
import { ModelInfo, FileMetadata } from '../api';

type ItemType = 'model' | 'command' | 'rule';

const ConfigManagement: React.FC = () => {
  const [selectedItem, setSelectedItem] = useState<ModelInfo | FileMetadata | null>(null);
  const [selectedItemType, setSelectedItemType] = useState<ItemType | null>(null);

  const handleSelectModel = (model: ModelInfo) => {
    setSelectedItem(model);
    setSelectedItemType('model');
  };

  const handleSelectCommand = (command: FileMetadata) => {
    setSelectedItem(command);
    setSelectedItemType('command');
  };

  const handleSelectRule = (rule: FileMetadata) => {
    setSelectedItem(rule);
    setSelectedItemType('rule');
  };

  const handleTabChange = (key: string) => {
    // 切换 tab 时清空选中项
    setSelectedItem(null);
    setSelectedItemType(null);
  };

  const items: TabsProps['items'] = [
    {
      key: 'models',
      label: (
        <span>
          <CodeOutlined />
          Mode 列表
        </span>
      ),
      children: (
        <ModesList onSelectModel={handleSelectModel} />
      ),
    },
    {
      key: 'commands',
      label: (
        <span>
          <FileTextOutlined />
          指令列表
        </span>
      ),
      children: (
        <CommandsList onSelectCommand={handleSelectCommand} />
      ),
    },
    {
      key: 'rules',
      label: (
        <span>
          <BookOutlined />
          默认规则列表
        </span>
      ),
      children: (
        <RulesList onSelectRule={handleSelectRule} />
      ),
    },
  ];

  return (
    <div style={{ height: '100%' }}>
      <Row gutter={16} style={{ height: '100%' }}>
        {/* 左侧配置列表 */}
        <Col span={10} style={{ height: '100%' }}>
          <div style={{ 
            height: '100%', 
            border: '1px solid #d9d9d9', 
            borderRadius: '8px',
            backgroundColor: '#fff'
          }}>
            <Tabs
              defaultActiveKey="models"
              items={items}
              onChange={handleTabChange}
              style={{
                height: '100%',
                padding: '0 16px',
              }}
              tabBarStyle={{
                paddingTop: '16px',
                marginBottom: '16px'
              }}
            />
          </div>
        </Col>

        {/* 右侧预览面板 */}
        <Col span={14} style={{ height: '100%' }}>
          <div style={{ height: '100%' }}>
            <PreviewPanel 
              selectedItem={selectedItem}
              itemType={selectedItemType}
            />
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default ConfigManagement;