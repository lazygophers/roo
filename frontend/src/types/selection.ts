export interface SelectedItem {
  id: string;
  type: 'model' | 'command' | 'rule';
  name: string;
  data: any;
}

// 模式关联规则的绑定关系
export interface ModelRuleBinding {
  modelId: string;
  selectedRuleIds: string[];
}

export interface SelectionState {
  selectedItems: SelectedItem[];
  selectionMode: boolean;
  modelRuleBindings: ModelRuleBinding[];
}

export interface SelectionActions {
  toggleSelectionMode: () => void;
  selectItem: (item: SelectedItem) => void;
  unselectItem: (id: string) => void;
  clearSelection: () => void;
  selectAll: (items: SelectedItem[]) => void;
  updateModelRuleBinding: (modelId: string, ruleId: string, selected: boolean) => void;
}