import React, { useState, useEffect, useCallback } from 'react';
import { Row, Col, Tabs, theme } from 'antd';
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
import { pageCacheManager } from '../hooks/useLazyLoading';
import './ConfigManagement.css';

const ConfigManagementWithSelection: React.FC = () => {
  // 设置页面标题
  useDocumentTitle('配置管理');

  const { token } = theme.useToken();
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

  // 页面卸载时清除缓存
  useEffect(() => {
    return () => {
      pageCacheManager.clearPageCache('config-management');
    };
  }, []);

  const handleTabChange = (key: string) => {
    setActiveTab(key);

    // 标记该Tab为已加载
    if (!loadedTabs.has(key)) {
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

  // Tab标签配置
  const tabItems = [
    {
      key: 'models',
      label: (
        <span>
          <CodeOutlined />
          Mode 列表
        </span>
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
    },
    {
      key: 'rules',
      label: (
        <span>
          <BookOutlined />
          默认规则列表
        </span>
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
            <div style={{ height: '100%', display: 'flex', flexDirection: 'column' }}>
              {/* Tab标签头部 */}
              <Tabs
                activeKey={activeTab}
                onChange={handleTabChange}
                style={{
                  paddingLeft: '16px',
                  paddingRight: '16px',
                  marginBottom: '0',
                }}
                items={tabItems.map(item => ({
                  key: item.key,
                  label: item.label,
                  children: null, // 不在这里渲染内容
                }))}
              />

              {/* Tab内容区域，保持所有已加载的内容挂载 */}
              <div style={{ flex: 1, position: 'relative', overflow: 'hidden', padding: '0 16px' }}>
                {loadedTabs.has('models') && (
                  <div style={{
                    display: activeTab === 'models' ? 'block' : 'none',
                    height: '100%',
                    overflowY: 'auto'
                  }}>
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
                  </div>
                )}

                {loadedTabs.has('commands') && (
                  <div style={{
                    display: activeTab === 'commands' ? 'block' : 'none',
                    height: '100%',
                    overflowY: 'auto'
                  }}>
                    <CommandsListWithSelection
                      selectedItems={selectedItems}
                      onToggleSelection={handleToggleSelection}
                      onSelectAll={handleSelectAll}
                      onClearSelection={handleClearSelection}
                    />
                  </div>
                )}

                {loadedTabs.has('rules') && (
                  <div style={{
                    display: activeTab === 'rules' ? 'block' : 'none',
                    height: '100%',
                    overflowY: 'auto'
                  }}>
                    <RulesListWithSelection
                      selectedItems={selectedItems}
                      onToggleSelection={handleToggleSelection}
                      onSelectAll={handleSelectAll}
                      onClearSelection={handleClearSelection}
                    />
                  </div>
                )}

                {loadedTabs.has('roles') && (
                  <div style={{
                    display: activeTab === 'roles' ? 'block' : 'none',
                    height: '100%',
                    overflowY: 'auto'
                  }}>
                    <RolesListWithSelection
                      selectedItems={selectedItems}
                      onToggleSelection={handleToggleSelection}
                      onSelectAll={handleSelectAll}
                      onClearSelection={handleClearSelection}
                    />
                  </div>
                )}

                {/* 占位符：当前Tab未加载时显示 */}
                {!loadedTabs.has(activeTab) && (
                  <div style={{
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: token.colorTextSecondary,
                    backgroundColor: token.colorBgContainer
                  }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px', opacity: 0.5 }}>
                      {activeTab === 'models' ? '⚙️' : activeTab === 'commands' ? '📝' : activeTab === 'rules' ? '📋' : '👤'}
                    </div>
                    <div style={{ fontSize: '16px', fontWeight: 500, marginBottom: '8px' }}>
                      {activeTab === 'models' ? '模式列表' : activeTab === 'commands' ? '指令列表' : activeTab === 'rules' ? '规则列表' : '角色选择'}
                    </div>
                    <div style={{ fontSize: '14px', opacity: 0.7 }}>
                      点击此Tab开始加载内容...
                    </div>
                  </div>
                )}
              </div>
            </div>
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