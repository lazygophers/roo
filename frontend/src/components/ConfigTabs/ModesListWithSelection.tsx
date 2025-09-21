import React, { useState, useEffect, useRef, useMemo, useCallback } from 'react';
import { 
  List, 
  Card, 
  Tag, 
  Space, 
  Input, 
  Select, 
  Row, 
  Col, 
  Typography,
  message,
  Spin,
  Checkbox,
  Button,
  theme
} from 'antd';
import { 
  CodeOutlined, 
  SearchOutlined, 
  SettingOutlined,
  CheckOutlined,
  BookOutlined
} from '@ant-design/icons';
import { apiClient, ModelInfo, FileMetadata } from '../../api';
import { SelectedItem, ModelRuleBinding } from '../../types/selection';

const { Search } = Input;
const { Option } = Select;
const { Text, Paragraph } = Typography;

interface ModesListProps {
  selectedItems: SelectedItem[];
  onToggleSelection: (item: SelectedItem) => void;
  onSelectAll: (items: SelectedItem[]) => void;
  onClearSelection: () => void;
  modelRuleBindings: ModelRuleBinding[];
  onModelRuleBinding: (modelId: string, ruleId: string, selected: boolean) => void;
  getModelRuleBindings: (modelId: string) => string[];
  onUpdateModelRules?: (modelId: string, rules: FileMetadata[]) => void;
}

const ModesListWithSelection: React.FC<ModesListProps> = ({ 
  selectedItems, 
  onToggleSelection,
  onSelectAll,
  onClearSelection,
  // modelRuleBindings, // 目前未使用，保留以供将来扩展
  onModelRuleBinding,
  getModelRuleBindings,
  onUpdateModelRules
}) => {
  const { token } = theme.useToken();
  const [models, setModels] = useState<ModelInfo[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchText, setSearchText] = useState('');
  const [categoryFilter, setCategoryFilter] = useState<string>('all');
  const [modelRules, setModelRules] = useState<Record<string, FileMetadata[]>>({});
  const [loadingRules, setLoadingRules] = useState<Record<string, boolean>>({});
  const [expandedModels, setExpandedModels] = useState<Set<string>>(new Set());
  const modelRulesRef = useRef<Record<string, FileMetadata[]>>({});
  const loadingRulesRef = useRef<Record<string, boolean>>({});

  // Optimized filteredModels with useMemo to prevent unnecessary re-computations
  const filteredModels = useMemo(() => {
    let filtered = models;

    // 分类过滤
    if (categoryFilter !== 'all') {
      filtered = filtered.filter(model => 
        model.groups.includes(categoryFilter)
      );
    }

    // 搜索过滤
    if (searchText) {
      const searchLower = searchText.toLowerCase();
      filtered = filtered.filter(model =>
        model.name.toLowerCase().includes(searchLower) ||
        model.slug.toLowerCase().includes(searchLower) ||
        model.description.toLowerCase().includes(searchLower) ||
        model.roleDefinition.toLowerCase().includes(searchLower)
      );
    }

    // 排序：参考 merge.py 的排序逻辑
    // 'orchestrator' 类型的模型优先级最高，其他的按 slug 字母顺序排列
    filtered.sort((a, b) => {
      if (a.slug === "orchestrator" && b.slug !== "orchestrator") {
        return -1; // a 排在前面
      }
      if (b.slug === "orchestrator" && a.slug !== "orchestrator") {
        return 1; // b 排在前面
      }
      // 两者都是或都不是 orchestrator，按 slug 字母顺序排序
      return a.slug.localeCompare(b.slug);
    });

    return filtered;
  }, [models, categoryFilter, searchText]);

  useEffect(() => {
    loadModels();
  }, []);

  // 同步 modelRules 和 loadingRules 到 ref
  useEffect(() => {
    modelRulesRef.current = modelRules;
  }, [modelRules]);

  useEffect(() => {
    loadingRulesRef.current = loadingRules;
  }, [loadingRules]);

  // 初始化时设置 orchestrator 模式默认展开
  useEffect(() => {
    if (models.length > 0) {
      const orchestratorModel = models.find(model => model.slug === 'orchestrator');
      if (orchestratorModel) {
        setExpandedModels(prev => {
          const newSet = new Set(prev);
          newSet.add('orchestrator');
          return newSet;
        });
        // 如果 orchestrator 还未加载规则，则加载
        if (!modelRules['orchestrator'] && !loadingRules['orchestrator']) {
          loadModelRules('orchestrator');
        }
      }
    }
  }, [models]); // eslint-disable-line react-hooks/exhaustive-deps

  // 当模型加载完成后，自动选择 orchestrator 模型
  useEffect(() => {
    if (models.length > 0) {
      const orchestratorModel = models.find(model => model.slug === 'orchestrator');
      if (orchestratorModel && !isSelected('orchestrator')) {
        const orchestratorItem: SelectedItem = {
          id: orchestratorModel.slug,
          type: 'model',
          name: orchestratorModel.name,
          data: orchestratorModel
        };
        onToggleSelection(orchestratorItem);
        // orchestrator 已在上面的 useEffect 中设置为展开状态，这里不需要再次调用 handleModelExpand
      }
    }
  }, [models]); // eslint-disable-line react-hooks/exhaustive-deps

  // 当 orchestrator 模式的规则加载完成后，自动选择所有规则
  useEffect(() => {
    const orchestratorRules = modelRules['orchestrator'];
    if (orchestratorRules && orchestratorRules.length > 0 && isSelected('orchestrator')) {
      // 检查是否已有规则绑定，如果没有则自动选择所有规则
      const currentBindings = getModelRuleBindings('orchestrator');
      if (currentBindings.length === 0) {
        orchestratorRules.forEach(rule => {
          onModelRuleBinding('orchestrator', rule.file_path, true);
        });
      }
    }
  }, [modelRules, selectedItems]); // eslint-disable-line react-hooks/exhaustive-deps


  const loadModels = async () => {
    try {
      setLoading(true);
      const response = await apiClient.getModels();
      setModels(response.data);
    } catch (error) {
      console.error('Failed to load models:', error);
      message.error('加载模型失败');
    } finally {
      setLoading(false);
    }
  };


  const getGroupColor = (groups: any[]) => {
    if (groups.includes('core')) return 'blue';
    if (groups.includes('coder')) return 'green';
    return 'default';
  };

  const getGroupIcon = (groups: any[]) => {
    if (groups.includes('core')) return <SettingOutlined />;
    if (groups.includes('coder')) return <CodeOutlined />;
    return null;
  };

  const isSelected = (modelSlug: string) => {
    return selectedItems.some(item => item.id === modelSlug && item.type === 'model');
  };

  // 检查是否为必选模型（不可取消）
  const isRequiredModel = (modelSlug: string) => {
    return modelSlug === 'orchestrator';
  };

  // 检查规则是否被特定模式选择
  const isRuleSelectedForModel = useCallback((rulePath: string, modelSlug: string): boolean => {
    const bindings = getModelRuleBindings(modelSlug);
    return bindings.includes(rulePath);
  }, [getModelRuleBindings]);

  // 智能等待规则加载完成并自动选择
  const autoSelectRulesAfterLoading = useCallback(async (modelSlug: string) => {
    console.log(`Starting auto-select for model: ${modelSlug}`);

    const maxWaitTime = 5000; // 最多等待5秒
    const checkInterval = 100; // 每100ms检查一次
    const startTime = Date.now();

    // 持续检查直到规则加载完成或超时
    while (Date.now() - startTime < maxWaitTime) {
      // 使用 ref 获取最新状态
      const isLoading = loadingRulesRef.current[modelSlug];
      const rules = modelRulesRef.current[modelSlug];

      console.log(`Checking model ${modelSlug}: loading=${isLoading}, rules=${rules ? rules.length : 'undefined'}`);

      // 检查是否不再加载且有规则数据
      if (!isLoading && rules !== undefined) {
        if (rules.length > 0) {
          console.log(`Auto-selecting ${rules.length} rules for model: ${modelSlug}`);
          // 自动选择所有规则
          rules.forEach(rule => {
            if (!isRuleSelectedForModel(rule.file_path, modelSlug)) {
              console.log(`Selecting rule: ${rule.file_path} for model: ${modelSlug}`);
              onModelRuleBinding(modelSlug, rule.file_path, true);
            }
          });
          return; // 成功完成
        } else {
          // 规则已加载但为空数组，也算完成
          console.log(`No rules to auto-select for model: ${modelSlug} (empty array)`);
          return;
        }
      }

      // 等待一小段时间再检查
      await new Promise(resolve => setTimeout(resolve, checkInterval));
    }

    console.warn(`Timeout waiting for rules to load for model: ${modelSlug}, final state: loading=${loadingRulesRef.current[modelSlug]}, rules=${modelRulesRef.current[modelSlug] ? modelRulesRef.current[modelSlug].length : 'undefined'}`);
  }, [isRuleSelectedForModel, onModelRuleBinding]);

  const handleToggleSelection = async (model: ModelInfo) => {
    // 如果是必选模型且已经选中，阻止取消选择
    if (isRequiredModel(model.slug) && isSelected(model.slug)) {
      return;
    }

    const currentlySelected = isSelected(model.slug);

    const selectedItem: SelectedItem = {
      id: model.slug,
      type: 'model',
      name: model.name,
      data: model
    };
    onToggleSelection(selectedItem);

    // 根据选中状态自动展开或收起关联规则
    if (!currentlySelected) {
      // 从未选中变为选中，自动展开并加载关联规则
      handleModelExpand(model.slug);

      // 延迟一下再启动自动选择逻辑，确保规则加载已经开始
      setTimeout(() => {
        autoSelectRulesAfterLoading(model.slug);
      }, 50);
    } else {
      // 从选中变为未选中，自动收起，并取消选择所有关联规则
      setExpandedModels(prev => {
        const newSet = new Set(prev);
        newSet.delete(model.slug);
        return newSet;
      });

      // 取消选择该模式下的所有规则
      const associatedRules = modelRules[model.slug] || [];
      associatedRules.forEach(rule => {
        if (isRuleSelectedForModel(rule.file_path, model.slug)) {
          onModelRuleBinding(model.slug, rule.file_path, false);
        }
      });
    }
  };

  const handleRuleToggleSelection = (rule: FileMetadata, modelSlug: string) => {
    const currentlySelected = isRuleSelectedForModel(rule.file_path, modelSlug);
    onModelRuleBinding(modelSlug, rule.file_path, !currentlySelected);
  };

  // 批量操作函数
  const handleRulesBatchOperation = (modelSlug: string, operation: 'selectAll' | 'deselectAll' | 'invert' | 'clear') => {
    const associatedRules = modelRules[modelSlug] || [];
    
    switch (operation) {
      case 'selectAll':
        // 全选：选择所有关联规则
        associatedRules.forEach(rule => {
          if (!isRuleSelectedForModel(rule.file_path, modelSlug)) {
            onModelRuleBinding(modelSlug, rule.file_path, true);
          }
        });
        break;
        
      case 'deselectAll':
        // 取消全选：取消选择所有关联规则
        associatedRules.forEach(rule => {
          if (isRuleSelectedForModel(rule.file_path, modelSlug)) {
            onModelRuleBinding(modelSlug, rule.file_path, false);
          }
        });
        break;
        
      case 'invert':
        // 反选：切换所有关联规则的选择状态
        associatedRules.forEach(rule => {
          const currentlySelected = isRuleSelectedForModel(rule.file_path, modelSlug);
          onModelRuleBinding(modelSlug, rule.file_path, !currentlySelected);
        });
        break;
        
      case 'clear':
        // 清空：等同于取消全选
        associatedRules.forEach(rule => {
          if (isRuleSelectedForModel(rule.file_path, modelSlug)) {
            onModelRuleBinding(modelSlug, rule.file_path, false);
          }
        });
        break;
    }
  };

  // 获取模式的规则选择统计信息
  const getRuleSelectionStats = (modelSlug: string) => {
    const associatedRules = modelRules[modelSlug] || [];
    const selectedCount = associatedRules.filter(rule => 
      isRuleSelectedForModel(rule.file_path, modelSlug)
    ).length;
    
    return {
      total: associatedRules.length,
      selected: selectedCount,
      isAllSelected: selectedCount === associatedRules.length && associatedRules.length > 0,
      isNoneSelected: selectedCount === 0,
      hasPartialSelection: selectedCount > 0 && selectedCount < associatedRules.length
    };
  };
  
  // 模式slug到规则slug的映射关系 - 根据slug层级查找规则目录
  const getModelRuleSlug = (modelSlug: string): string[] => {
    // 将 slug 按 '-' 分割，生成层级结构的规则目录名称
    const parts = modelSlug.split('-');
    const ruleSlugs: string[] = [];
    
    // 添加基础的 rules 目录
    ruleSlugs.push('rules');
    
    // 逐级构建规则目录名称，不添加 rules- 前缀
    let currentPath = '';
    for (const part of parts) {
      if (part) { // 忽略空字符串
        if (currentPath === '') {
          currentPath = part;
        } else {
          currentPath += `-${part}`;
        }
        ruleSlugs.push(currentPath);
      }
    }
    
    return ruleSlugs;
  };

  // 加载模型规则的独立函数 (Memoized for performance)
  const loadModelRules = useCallback(async (modelSlug: string) => {
    const ruleSlugs = getModelRuleSlug(modelSlug);
    
    if (ruleSlugs.length === 0) {
      setModelRules(prev => ({ ...prev, [modelSlug]: [] }));
      return;
    }
    
    setLoadingRules(prev => ({ ...prev, [modelSlug]: true }));
    
    try {
      const allRules: FileMetadata[] = [];
      const ruleSlugResults: string[] = [];
      
      // Use Promise.allSettled for parallel API calls instead of sequential
      const promises = ruleSlugs.map(async (ruleSlug) => {
        try {
          const response = await apiClient.getRulesBySlug(ruleSlug);
          return { ruleSlug, data: response.data || [] };
        } catch (error) {
          console.debug(`Rule directory ${ruleSlug} not found for model ${modelSlug}, continuing...`);
          return { ruleSlug, data: [] };
        }
      });
      
      const results = await Promise.allSettled(promises);
      
      // Process results in chunks to avoid blocking the main thread
      for (const result of results) {
        if (result.status === 'fulfilled' && result.value.data.length > 0) {
          allRules.push(...result.value.data);
          ruleSlugResults.push(result.value.ruleSlug);
        }
        // Yield control to browser between processing chunks
        await new Promise(resolve => setTimeout(resolve, 0));
      }
      
      // Use Map for O(1) lookup instead of findIndex for deduplication
      const rulesMap = new Map<string, FileMetadata>();
      for (const rule of allRules) {
        rulesMap.set(rule.file_path, rule);
        // Yield control periodically during large operations
        if (rulesMap.size % 10 === 0) {
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      }
      const uniqueRules = Array.from(rulesMap.values());
      
      setModelRules(prev => ({ ...prev, [modelSlug]: uniqueRules }));
      
      if (onUpdateModelRules) {
        onUpdateModelRules(modelSlug, uniqueRules);
      }
      
      if (ruleSlugResults.length > 0) {
        console.log(`Loaded rules for model ${modelSlug} from directories: ${ruleSlugResults.join(', ')}`);
      }
    } catch (error: any) {
      console.warn(`Failed to load rules for model ${modelSlug}:`, error);
      const emptyRules: FileMetadata[] = [];
      setModelRules(prev => ({ ...prev, [modelSlug]: emptyRules }));
      
      if (onUpdateModelRules) {
        onUpdateModelRules(modelSlug, emptyRules);
      }
    } finally {
      setLoadingRules(prev => ({ ...prev, [modelSlug]: false }));
    }
  }, [onUpdateModelRules]);

  // 强制展开模型（不包含 toggle 逻辑）
  const forceExpandModel = useCallback(async (modelSlug: string) => {
    console.log(`Force expanding model: ${modelSlug}`);

    // 如果还没有加载过这个模式的规则，则异步加载（不阻塞 UI）
    if (!modelRulesRef.current[modelSlug] && !loadingRulesRef.current[modelSlug]) {
      console.log(`Loading rules for model: ${modelSlug}`);
      // Use setTimeout to defer rule loading and prevent blocking
      setTimeout(() => {
        loadModelRules(modelSlug);
      }, 0);
    } else {
      console.log(`Rules already loaded for model: ${modelSlug}`);
    }
  }, [loadModelRules]);

  // 切换模型展开状态（用于用户点击）
  const handleModelExpand = async (modelSlug: string) => {
    const newExpandedModels = new Set(expandedModels);
    
    if (expandedModels.has(modelSlug)) {
      newExpandedModels.delete(modelSlug);
      setExpandedModels(newExpandedModels);
      return;
    }
    
    newExpandedModels.add(modelSlug);
    setExpandedModels(newExpandedModels);
    
    // 如果还没有加载过这个模式的规则，则异步加载（不阻塞 UI）
    if (!modelRules[modelSlug] && !loadingRules[modelSlug]) {
      // Use setTimeout to defer rule loading and prevent blocking
      setTimeout(() => {
        loadModelRules(modelSlug);
      }, 0);
    }
  };

  // 全选所有模式
  const handleSelectAll = async () => {
    console.log('handleSelectAll called');
    const allItems: SelectedItem[] = models.map(model => ({
      id: model.slug,
      type: 'model',
      name: model.name,
      data: model
    }));
    console.log('All items:', allItems.map(item => item.id));
    onSelectAll(allItems);

    // 立即展开所有模型
    const newExpandedModels = new Set(models.map(model => model.slug));
    setExpandedModels(newExpandedModels);
    console.log('Expanded all models:', Array.from(newExpandedModels));

    // 获取需要加载规则的模型
    const modelsToLoadRules = models.filter(model =>
      !modelRules[model.slug] && !loadingRules[model.slug]
    );
    console.log('Models to load rules:', modelsToLoadRules.map(model => model.slug));

    if (modelsToLoadRules.length > 0) {
      message.info(`正在加载 ${modelsToLoadRules.length} 个模型的关联规则...`);

      // Process models in batches to prevent blocking the main thread
      const batchSize = 3;
      const processBatch = async (batch: typeof modelsToLoadRules) => {
        for (const model of batch) {
          console.log(`Loading rules for model: ${model.slug}`);
          // Load rules for the model
          await forceExpandModel(model.slug);

          // Defer rule selection to prevent blocking
          setTimeout(() => {
            const associatedRules = modelRulesRef.current[model.slug] || [];
            console.log(`Auto-selecting ${associatedRules.length} rules for model: ${model.slug}`);
            console.log(`Rules for ${model.slug}:`, associatedRules.map(r => r.name || r.file_path));
            associatedRules.forEach(rule => {
              if (!isRuleSelectedForModel(rule.file_path, model.slug)) {
                onModelRuleBinding(model.slug, rule.file_path, true);
              }
            });
          }, 500);

          // Yield control between models
          await new Promise(resolve => setTimeout(resolve, 0));
        }
      };

      // Process models in batches with yielding
      for (let i = 0; i < modelsToLoadRules.length; i += batchSize) {
        const batch = modelsToLoadRules.slice(i, i + batchSize);
        await processBatch(batch);
        // Yield control between batches
        await new Promise(resolve => setTimeout(resolve, 10));
      }

      console.log('All models processed for rule loading and selection');
    }
  };

  // 反选所有模式
  const handleReverseSelection = async () => {
    console.log('handleReverseSelection called');
    const currentSelectedIds = selectedItems
      .filter(item => item.type === 'model')
      .map(item => item.id);
    
    const reversedItems: SelectedItem[] = models
      .filter(model => !currentSelectedIds.includes(model.slug))
      .map(model => ({
        id: model.slug,
        type: 'model',
        name: model.name,
        data: model
      }));
    
    // 清空当前选择，然后选择反选的项目
    onClearSelection();
    setTimeout(() => {
      onSelectAll(reversedItems);
    }, 100);
  };

  // 取消全选（仅取消选中状态，保留必选项）
  const handleUnselectAll = () => {
    const requiredModels = ['orchestrator']; // 必选模式列表
    const requiredItems = selectedItems.filter(item => 
      item.type === 'model' && requiredModels.includes(item.id)
    );
    
    // 清空所有选择
    onClearSelection();
    
    // 重新添加必选项
    if (requiredItems.length > 0) {
      setTimeout(() => {
        requiredItems.forEach(item => onToggleSelection(item));
      }, 100);
    }
  };

  const selectedModelCount = selectedItems.filter(item => item.type === 'model').length;

  return (
    <div>
      {/* 搜索和过滤器 */}
      <Row gutter={16} style={{ marginBottom: 16 }}>
        <Col span={16}>
          <Search
            placeholder="搜索模型名称、slug、描述..."
            allowClear
            prefix={<SearchOutlined />}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
            style={{ width: '100%' }}
          />
        </Col>
        <Col span={8}>
          <Select
            style={{ width: '100%' }}
            value={categoryFilter}
            onChange={setCategoryFilter}
            placeholder="选择分类"
          >
            <Option value="all">全部分类</Option>
            <Option value="core">Core 模式</Option>
            <Option value="coder">Coder 模式</Option>
          </Select>
        </Col>
      </Row>

      {/* 统计信息和批量操作 */}
      <div style={{ marginBottom: 16 }}>
        <Row justify="space-between" align="middle">
          <Col>
            <Space>
              <Text type="secondary">
                总计: {models.length} 个模型
              </Text>
              <Text type="secondary">
                当前显示: {filteredModels.length} 个
              </Text>
              <Text type="success">
                已选择: {selectedModelCount} 个模型
              </Text>
            </Space>
          </Col>
          <Col>
            <Space>
              <Button
                size="small"
                onClick={handleSelectAll}
                disabled={models.length === 0}
              >
                全选
              </Button>
              <Button
                size="small"
                onClick={onClearSelection}
                disabled={selectedModelCount === 0}
              >
                清空
              </Button>
            </Space>
          </Col>
        </Row>
      </div>

      {/* 模型列表 */}
      <Spin spinning={loading}>
        <List
          dataSource={filteredModels}
          renderItem={(model) => {
            const isItemSelected = isSelected(model.slug);
            // 只有选中的模式才展开关联规则
            const isExpanded = isItemSelected && expandedModels.has(model.slug);
            const associatedRules = modelRules[model.slug] || [];
            const isLoadingModelRules = loadingRules[model.slug] || false;
            
            return (
              <List.Item style={{ padding: 0, marginBottom: 8 }}>
                <Card
                  size="small"
                  style={{ 
                    width: '100%',
                    border: isItemSelected 
                      ? `2px solid ${token.colorPrimary}` 
                      : `1px solid ${token.colorBorder}`,
                    backgroundColor: isItemSelected 
                      ? token.colorBgContainer 
                      : token.colorBgContainer,
                    boxShadow: isItemSelected 
                      ? `0 0 0 2px ${token.colorPrimary}20` 
                      : 'none'
                  }}
                  styles={{ body: { padding: '12px 16px' } }}
                >
                  {/* 模式主体 */}
                  <div 
                    style={{ display: 'flex', alignItems: 'flex-start', cursor: 'pointer' }}
                    onClick={() => handleToggleSelection(model)}
                  >
                    <div style={{ marginRight: 12, marginTop: 4 }}>
                      <Checkbox 
                        checked={isItemSelected}
                        disabled={isRequiredModel(model.slug) && isItemSelected}
                        onChange={() => handleToggleSelection(model)}
                      />
                    </div>
                    <div style={{ flex: 1 }}>
                      <List.Item.Meta
                        avatar={getGroupIcon(model.groups)}
                        title={
                          <Space>
                            <span style={{ fontWeight: 'bold' }}>{model.name}</span>
                            <Tag color={getGroupColor(model.groups)}>
                              {model.groups.includes('core') ? 'Core' : 'Coder'}
                            </Tag>
                            {isRequiredModel(model.slug) && (
                              <Tag color="volcano">
                                必选
                              </Tag>
                            )}
                            {isItemSelected && (
                              <Tag color="success" icon={<CheckOutlined />}>
                                已选择
                              </Tag>
                            )}
                          </Space>
                        }
                        description={
                          <div>
                            <Paragraph 
                              ellipsis={{ rows: 2, expandable: false }}
                              style={{ marginBottom: 8, fontSize: 13, color: token.colorTextSecondary }}
                            >
                              {model.description}
                            </Paragraph>
                            <div>
                              <Tag color="processing" style={{ fontSize: 10 }}>
                                {model.slug}
                              </Tag>
                              <Text 
                                type="secondary" 
                                style={{ fontSize: 11, marginLeft: 8 }}
                              >
                                {isRequiredModel(model.slug) 
                                  ? (isItemSelected ? '必选模型（已选择）' : '点击选择（必选）')
                                  : '点击选择/取消'
                                }
                              </Text>
                              {isItemSelected && associatedRules.length > 0 && (
                                <Tag color="purple" style={{ fontSize: 10, marginLeft: 8 }}>
                                  {associatedRules.length} 个关联规则
                                </Tag>
                              )}
                            </div>
                            
                            {/* 文件信息 */}
                            <div style={{ marginTop: 6, fontSize: 11, color: token.colorTextTertiary }}>
                              <Space split={<span style={{ color: token.colorTextTertiary }}>|</span>} size={8}>
                                <Text type="secondary" style={{ fontSize: 10 }}>
                                  📁 {model.file_path?.replace(/^.*\/resources\//, '') || 'N/A'}
                                </Text>
                                <Text type="secondary" style={{ fontSize: 10 }}>
                                  📏 {model.file_size ? `${(model.file_size / 1024).toFixed(1)}KB` : 'N/A'}
                                </Text>
                              </Space>
                            </div>
                          </div>
                        }
                      />
                    </div>
                  </div>

                  {/* 关联规则区域 - 选中后自动展开 */}
                  {isExpanded && (
                    <div style={{ marginTop: 12, paddingTop: 12, borderTop: `1px solid ${token.colorBorderSecondary}` }}>
                      <div style={{ marginBottom: 8 }}>
                        <Row justify="space-between" align="middle">
                          <Col>
                            <Space>
                              <BookOutlined style={{ color: token.colorPrimary }} />
                              <Text strong style={{ fontSize: 13 }}>关联规则</Text>
                              {associatedRules.length > 0 && (
                                <Tag color="blue">{associatedRules.length} 个</Tag>
                              )}
                              {(() => {
                                const stats = getRuleSelectionStats(model.slug);
                                if (stats.total > 0) {
                                  return (
                                    <Tag color={stats.selected > 0 ? "green" : "default"} style={{ fontSize: 10 }}>
                                      已选择 {stats.selected}/{stats.total}
                                    </Tag>
                                  );
                                }
                                return null;
                              })()}
                            </Space>
                          </Col>
                          <Col>
                            {associatedRules.length > 0 && (
                              <Space size={4}>
                                <Button
                                  type="link"
                                  size="small"
                                  style={{ 
                                    fontSize: 11, 
                                    padding: '0 6px', 
                                    height: 20,
                                    color: (() => {
                                      const stats = getRuleSelectionStats(model.slug);
                                      return stats.isAllSelected ? token.colorTextDisabled : token.colorPrimary;
                                    })()
                                  }}
                                  onClick={() => handleRulesBatchOperation(model.slug, 'selectAll')}
                                  disabled={(() => {
                                    const stats = getRuleSelectionStats(model.slug);
                                    return stats.isAllSelected;
                                  })()}
                                >
                                  全选
                                </Button>
                                <span style={{ color: token.colorBorderSecondary, fontSize: 10 }}>|</span>
                                <Button
                                  type="link"
                                  size="small"
                                  style={{ 
                                    fontSize: 11, 
                                    padding: '0 6px', 
                                    height: 20,
                                    color: (() => {
                                      const stats = getRuleSelectionStats(model.slug);
                                      return stats.isNoneSelected ? token.colorTextDisabled : token.colorError;
                                    })()
                                  }}
                                  onClick={() => handleRulesBatchOperation(model.slug, 'deselectAll')}
                                  disabled={(() => {
                                    const stats = getRuleSelectionStats(model.slug);
                                    return stats.isNoneSelected;
                                  })()}
                                >
                                  取消全选
                                </Button>
                                <span style={{ color: token.colorBorderSecondary, fontSize: 10 }}>|</span>
                                <Button
                                  type="link"
                                  size="small"
                                  style={{ 
                                    fontSize: 11, 
                                    padding: '0 6px', 
                                    height: 20,
                                    color: token.colorPrimary
                                  }}
                                  onClick={() => handleRulesBatchOperation(model.slug, 'invert')}
                                  disabled={associatedRules.length === 0}
                                >
                                  反选
                                </Button>
                                <span style={{ color: token.colorBorderSecondary, fontSize: 10 }}>|</span>
                                <Button
                                  type="link"
                                  size="small"
                                  style={{ 
                                    fontSize: 11, 
                                    padding: '0 6px', 
                                    height: 20,
                                    color: (() => {
                                      const stats = getRuleSelectionStats(model.slug);
                                      return stats.isNoneSelected ? token.colorTextDisabled : token.colorWarning;
                                    })()
                                  }}
                                  onClick={() => handleRulesBatchOperation(model.slug, 'clear')}
                                  disabled={(() => {
                                    const stats = getRuleSelectionStats(model.slug);
                                    return stats.isNoneSelected;
                                  })()}
                                >
                                  清空
                                </Button>
                              </Space>
                            )}
                          </Col>
                        </Row>
                      </div>
                      
                      {isLoadingModelRules ? (
                        <div style={{ textAlign: 'center', padding: '20px 0' }}>
                          <Spin size="small" />
                          <Text type="secondary" style={{ marginLeft: 8, fontSize: 12 }}>
                            加载关联规则...
                          </Text>
                        </div>
                      ) : associatedRules.length === 0 ? (
                        <Text type="secondary" style={{ fontSize: 12 }}>
                          该模式没有关联规则
                        </Text>
                      ) : (
                        <div>
                          {associatedRules.map((rule) => {
                            const ruleSelected = isRuleSelectedForModel(rule.file_path, model.slug);
                            return (
                              <div
                                key={rule.file_path}
                                style={{
                                  padding: '6px 8px',
                                  border: ruleSelected 
                                    ? `1px solid ${token.colorPrimary}` 
                                    : `1px solid ${token.colorBorderSecondary}`,
                                  borderRadius: '4px',
                                  backgroundColor: ruleSelected 
                                    ? token.colorFillSecondary
                                    : token.colorFillTertiary,
                                  marginBottom: '4px',
                                  cursor: 'pointer',
                                  display: 'flex',
                                  alignItems: 'center'
                                }}
                                onClick={() => handleRuleToggleSelection(rule, model.slug)}
                              >
                                <Checkbox
                                  checked={ruleSelected}
                                  style={{ marginRight: 8 }}
                                  onChange={() => handleRuleToggleSelection(rule, model.slug)}
                                />
                                <div style={{ flex: 1 }}>
                                  <div>
                                    <Text style={{ fontSize: 12, fontWeight: ruleSelected ? 'bold' : 'normal' }}>
                                      {rule.title || rule.name || rule.file_path.split('/').pop()?.replace(/\.[^/.]+$/, "") || '未命名规则'}
                                    </Text>
                                    {rule.category && (
                                      <Tag color="blue" style={{ marginLeft: 4, fontSize: 10 }}>
                                        {rule.category}
                                      </Tag>
                                    )}
                                  </div>
                                  {rule.description && (
                                    <Text type="secondary" style={{ fontSize: 11, display: 'block' }}>
                                      {rule.description.substring(0, 50)}{rule.description.length > 50 ? '...' : ''}
                                    </Text>
                                  )}
                                  
                                  {/* 规则文件信息 */}
                                  <div style={{ marginTop: 4, fontSize: 10, color: token.colorTextTertiary }}>
                                    <Space split={<span>|</span>} size={4}>
                                      <Text type="secondary" style={{ fontSize: 9 }}>
                                        📁 {rule.file_path?.replace(/^.*\/resources\//, '') || 'N/A'}
                                      </Text>
                                      <Text type="secondary" style={{ fontSize: 9 }}>
                                        📏 {rule.file_size ? `${(rule.file_size / 1024).toFixed(1)}KB` : 'N/A'}
                                      </Text>
                                    </Space>
                                  </div>
                                </div>
                              </div>
                            );
                          })}
                        </div>
                      )}
                    </div>
                  )}
                </Card>
              </List.Item>
            );
          }}
          locale={{ emptyText: '没有找到匹配的模型' }}
        />
      </Spin>
    </div>
  );
};

export default ModesListWithSelection;