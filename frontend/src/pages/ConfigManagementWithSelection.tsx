import React, { useState, useEffect, useCallback, useMemo } from 'react';
import { Row, Col, Tabs, TabsProps, theme, Spin } from 'antd';
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

  // 惰性加载状态管理
  const [activeTab, setActiveTab] = useState<string>('models');
  const [loadedTabs, setLoadedTabs] = useState<Set<string>>(new Set(['models'])); // 默认加载第一个Tab

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
    console.log(`Switching to tab: ${key}`);
    setActiveTab(key);

    // 标记该Tab为已加载
    if (!loadedTabs.has(key)) {
      console.log(`Loading tab for the first time: ${key}`);
      setLoadedTabs(prev => {
        const newSet = new Set(prev);
        newSet.add(key);
        return newSet;
      });
    }
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

  // 处理刷新配置数据
  const handleRefreshConfig = async (configType: string): Promise<{ success: boolean; message: string }> => {
    try {
      const response = await apiClient.syncDatabaseConfig(configType);
      if (response.success) {
        // 刷新后重新获取环境信息以更新页面数据
        await fetchEnvironmentInfo();
        return { success: true, message: `${configType} 数据已刷新` };
      } else {
        return { success: false, message: response.message || '刷新失败' };
      }
    } catch (error) {
      console.error('刷新配置数据失败:', error);
      return { success: false, message: '刷新失败' };
    }
  };

  // 惰性加载组件包装器
  const LazyTabContent: React.FC<{
    tabKey: string;
    children: React.ReactNode;
    fallback?: React.ReactNode;
  }> = ({ tabKey, children, fallback }) => {
    const shouldLoad = loadedTabs.has(tabKey);

    console.log(`LazyTabContent - Tab: ${tabKey}, shouldLoad: ${shouldLoad}, activeTab: ${activeTab}`);

    // 如果Tab已经被标记为加载，直接渲染子组件
    if (shouldLoad) {
      return <>{children}</>;
    }

    // 如果Tab没有被加载过，显示占位符
    return (
      <div style={{
        height: '400px',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        color: token.colorTextSecondary,
        backgroundColor: token.colorBgContainer
      }}>
        <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>
          {tabKey === 'models' ? '⚙️' : tabKey === 'commands' ? '📝' : tabKey === 'rules' ? '📋' : '👤'}
        </div>
        <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
          {tabKey === 'models' ? '模式列表' : tabKey === 'commands' ? '指令列表' : tabKey === 'rules' ? '规则列表' : '角色选择'}
        </div>
        <div style={{ fontSize: '14px', opacity: 0.7 }}>
          {fallback || '点击此Tab开始加载内容...'}
        </div>
      </div>
    );
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
        <LazyTabContent tabKey="models">
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
        </LazyTabContent>
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
        <LazyTabContent tabKey="commands">
          <CommandsListWithSelection
            selectedItems={selectedItems}
            onToggleSelection={handleToggleSelection}
            onSelectAll={handleSelectAll}
            onClearSelection={handleClearSelection}
          />
        </LazyTabContent>
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
        <LazyTabContent tabKey="rules">
          <RulesListWithSelection
            selectedItems={selectedItems}
            onToggleSelection={handleToggleSelection}
            onSelectAll={handleSelectAll}
            onClearSelection={handleClearSelection}
          />
        </LazyTabContent>
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
        <LazyTabContent tabKey="roles">
          <RolesListWithSelection
            selectedItems={selectedItems}
            onToggleSelection={handleToggleSelection}
            onSelectAll={handleSelectAll}
            onClearSelection={handleClearSelection}
          />
        </LazyTabContent>
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
        onRefresh={handleRefreshConfig}
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
              activeKey={activeTab}
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