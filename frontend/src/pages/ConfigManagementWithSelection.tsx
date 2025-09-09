import React, { useState } from 'react';
import { Row, Col, Tabs, TabsProps, theme } from 'antd';
import { CodeOutlined, FileTextOutlined, BookOutlined } from '@ant-design/icons';
import ModesListWithSelection from '../components/ConfigTabs/ModesListWithSelection';
import CommandsListWithSelection from '../components/ConfigTabs/CommandsListWithSelection';
import RulesListWithSelection from '../components/ConfigTabs/RulesListWithSelection';
import SelectionPreviewPanel from '../components/Preview/SelectionPreviewPanel';
import ExportToolbar from '../components/ExportToolbar/ExportToolbar';
import { SelectedItem, ModelRuleBinding } from '../types/selection';
import { FileMetadata } from '../api';

const ConfigManagementWithSelection: React.FC = () => {
  const { token } = theme.useToken();
  const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([]);
  const [modelRuleBindings, setModelRuleBindings] = useState<ModelRuleBinding[]>([]);
  const [modelRules, setModelRules] = useState<Record<string, FileMetadata[]>>({});

  const handleTabChange = (key: string) => {
    // 切换 tab 时不清空选中项，保持预览状态
  };

  const handleToggleSelection = (item: SelectedItem) => {
    const existingIndex = selectedItems.findIndex(
      selectedItem => selectedItem.id === item.id && selectedItem.type === item.type
    );
    
    if (existingIndex >= 0) {
      // 已选择，移除
      setSelectedItems(selectedItems.filter((_, index) => index !== existingIndex));
    } else {
      // 未选择，添加
      setSelectedItems([...selectedItems, item]);
    }
  };

  const handleSelectAll = (items: SelectedItem[]) => {
    // 合并新选择的项目，避免重复
    const newSelectedItems = [...selectedItems];
    items.forEach(item => {
      const exists = newSelectedItems.some(
        selectedItem => selectedItem.id === item.id && selectedItem.type === item.type
      );
      if (!exists) {
        newSelectedItems.push(item);
      }
    });
    setSelectedItems(newSelectedItems);
  };

  const handleClearSelection = () => {
    setSelectedItems([]);
  };

  const handleExport = () => {
    console.log('导出选中的项目:', selectedItems);
    console.log('导出模式-规则绑定关系:', modelRuleBindings);
    // 这里可以实现具体的导出逻辑
  };

  // 处理模式-规则绑定关系
  const handleModelRuleBinding = (modelId: string, ruleId: string, selected: boolean) => {
    setModelRuleBindings(prev => {
      const existingBinding = prev.find(binding => binding.modelId === modelId);
      
      if (existingBinding) {
        // 更新现有绑定
        return prev.map(binding => {
          if (binding.modelId === modelId) {
            const newRuleIds = selected
              ? [...binding.selectedRuleIds, ruleId].filter((id, index, arr) => arr.indexOf(id) === index) // 去重
              : binding.selectedRuleIds.filter(id => id !== ruleId);
            return { ...binding, selectedRuleIds: newRuleIds };
          }
          return binding;
        });
      } else if (selected) {
        // 创建新绑定
        return [...prev, { modelId, selectedRuleIds: [ruleId] }];
      }
      
      return prev;
    });
  };

  // 获取模式的关联规则选择状态
  const getModelRuleBindings = (modelId: string): string[] => {
    const binding = modelRuleBindings.find(binding => binding.modelId === modelId);
    return binding ? binding.selectedRuleIds : [];
  };

  // 更新模式规则详细信息
  const handleUpdateModelRules = (modelId: string, rules: FileMetadata[]) => {
    setModelRules(prev => ({ ...prev, [modelId]: rules }));
  };

  // 清空选择时也要清空模式-规则绑定
  const handleClearSelectionWithBindings = () => {
    setSelectedItems([]);
    setModelRuleBindings([]);
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
        <ModesListWithSelection 
          selectedItems={selectedItems}
          onToggleSelection={handleToggleSelection}
          onSelectAll={handleSelectAll}
          onClearSelection={handleClearSelection}
          modelRuleBindings={modelRuleBindings}
          onModelRuleBinding={handleModelRuleBinding}
          getModelRuleBindings={getModelRuleBindings}
          onUpdateModelRules={handleUpdateModelRules}
        />
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
        <CommandsListWithSelection 
          selectedItems={selectedItems}
          onToggleSelection={handleToggleSelection}
          onSelectAll={handleSelectAll}
          onClearSelection={handleClearSelection}
        />
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
        <RulesListWithSelection 
          selectedItems={selectedItems}
          onToggleSelection={handleToggleSelection}
          onSelectAll={handleSelectAll}
          onClearSelection={handleClearSelection}
        />
      ),
    },
  ];

  return (
    <div style={{ height: '100%' }}>
      {/* 导出工具栏 */}
      <ExportToolbar
        selectedItems={selectedItems}
        onClearSelection={handleClearSelectionWithBindings}
        onExport={handleExport}
      />

      <Row gutter={16} style={{ height: 'calc(100% - 80px)' }}>
        {/* 左侧配置列表 */}
        <Col span={10} style={{ height: '100%' }}>
          <div style={{ 
            height: '100%', 
            border: `1px solid ${token.colorBorder}`, 
            borderRadius: '8px',
            backgroundColor: token.colorBgContainer
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
            <SelectionPreviewPanel 
              selectedItems={selectedItems}
              modelRuleBindings={modelRuleBindings}
              modelRules={modelRules}
            />
          </div>
        </Col>
      </Row>
    </div>
  );
};

export default ConfigManagementWithSelection;