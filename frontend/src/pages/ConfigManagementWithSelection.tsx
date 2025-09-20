import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Tabs, TabsProps, theme } from 'antd';
import { CodeOutlined, FileTextOutlined, BookOutlined, UserOutlined } from '@ant-design/icons';
import ModesListWithSelection from '../components/ConfigTabs/ModesListWithSelection';
import CommandsListWithSelection from '../components/ConfigTabs/CommandsListWithSelection';
import RulesListWithSelection from '../components/ConfigTabs/RulesListWithSelection';
import RolesListWithSelection from '../components/ConfigTabs/RolesListWithSelection';
import SelectionPreviewPanel from '../components/Preview/SelectionPreviewPanel';
import ExportToolbar from '../components/ExportToolbar/ExportToolbar';
import { SelectedItem, ModelRuleBinding } from '../types/selection';
import { FileMetadata, EnvironmentInfo, apiClient } from '../api';
import { useDocumentTitle } from '../hooks/useDocumentTitle';
import { useEnvironment } from '../contexts/EnvironmentContext';
import './ConfigManagement.css';

const ConfigManagementWithSelection: React.FC = () => {
  // 设置页面标题
  useDocumentTitle('配置管理');

  const { token } = theme.useToken();
  const { isRemote, isEditAllowed } = useEnvironment();
  const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([]);
  const [modelRuleBindings, setModelRuleBindings] = useState<ModelRuleBinding[]>([]);
  const [modelRules, setModelRules] = useState<Record<string, FileMetadata[]>>({});
  const [environmentInfo, setEnvironmentInfo] = useState<EnvironmentInfo | null>(null);

  // 获取环境信息
  const fetchEnvironmentInfo = useCallback(async () => {
    try {
      const response = await apiClient.getEnvironmentInfo();
      if (response.success) {
        setEnvironmentInfo(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch environment info:', error);
    }
  }, []);

  useEffect(() => {
    fetchEnvironmentInfo();
  }, [fetchEnvironmentInfo]);

  const handleTabChange = (key: string) => {
    // 切换 tab 时不清空选中项，保持预览状态
  };

  const handleToggleSelection = (item: SelectedItem) => {
    const existingIndex = selectedItems.findIndex(
      selectedItem => selectedItem.id === item.id && selectedItem.type === item.type
    );
    
    // 检查是否为必选模型
    const isRequiredModel = item.type === 'model' && item.id === 'orchestrator';
    
    if (existingIndex >= 0) {
      // 如果是必选模型，不允许移除
      if (isRequiredModel) {
        return;
      }
      // 已选择，移除
      setSelectedItems(selectedItems.filter((_, index) => index !== existingIndex));
    } else {
      // 角色是单选，需要先移除其他角色
      if (item.type === 'role') {
        const nonRoleItems = selectedItems.filter(selectedItem => selectedItem.type !== 'role');
        setSelectedItems([...nonRoleItems, item]);
      } else {
        // 其他类型正常添加
        setSelectedItems([...selectedItems, item]);
      }
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
    // 清空选择时保留必选模型
    const requiredItems = selectedItems.filter(item => 
      item.type === 'model' && item.id === 'orchestrator'
    );
    setSelectedItems(requiredItems);
  };

  const handleExport = () => {
    console.log('导出选中的项目:', selectedItems);
    console.log('导出模式-规则绑定关系:', modelRuleBindings);
    // 这里可以实现具体的导出逻辑
  };

  // 加载配置并应用到当前选择
  const handleLoadConfiguration = (config: any) => {
    // 清除当前选择
    setSelectedItems([]);
    setModelRuleBindings([]);
    setModelRules({});
    
    // 应用配置数据
    if (config.selectedItems) {
      setSelectedItems(config.selectedItems);
    }
    if (config.modelRuleBindings) {
      setModelRuleBindings(config.modelRuleBindings);
    }
    if (config.modelRules) {
      setModelRules(config.modelRules);
    }
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
    {
      key: 'roles',
      label: (
        <span>
          <UserOutlined />
          角色选择
        </span>
      ),
      children: (
        <RolesListWithSelection 
          selectedItems={selectedItems}
          onToggleSelection={handleToggleSelection}
          onSelectAll={handleSelectAll}
          onClearSelection={handleClearSelection}
        />
      ),
    },
  ];

  return (
    <div className="config-management-page" style={{ height: '100%' }}>
      {/* 页面标题 */}
      <h2 style={{ margin: '0 0 16px 0', fontSize: '20px', fontWeight: 'normal' }}>
        配置管理
      </h2>
      
      {/* 导出工具栏 */}
      <ExportToolbar
        selectedItems={selectedItems}
        onClearSelection={handleClearSelectionWithBindings}
        onExport={handleExport}
        modelRuleBindings={modelRuleBindings}
        modelRules={modelRules}
        onLoadConfiguration={handleLoadConfiguration}
        environmentInfo={environmentInfo}
      />

      <Row gutter={16} style={{ height: 'calc(100% - 80px)' }}>
        {/* 左侧配置列表 */}
        <Col span={10} style={{ height: '100%' }}>
          <div style={{ 
            height: '100%', 
            border: `1px solid ${token.colorBorder}`, 
            borderRadius: '4px',
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