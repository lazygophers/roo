<template>
  <div class="config-selector">
    <div class="container">
      <div class="header">
        <h1>配置选择器</h1>
        <p class="description">选择您需要的 models、rules、roles 和 commands</p>
        
        <!-- 配置统计信息 -->
        <div class="stats-bar">
          <div class="stat-item">
            <span class="stat-value">{{ selectedModels.length }}</span>
            <span class="stat-label">Models</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ totalSelectedRules }}</span>
            <span class="stat-label">Rules</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ selectedRole ? 1 : 0 }}</span>
            <span class="stat-label">Roles</span>
          </div>
          <div class="stat-item">
            <span class="stat-value">{{ selectedCommands.length }}</span>
            <span class="stat-label">Commands</span>
          </div>
        </div>
      </div>
      
      <div class="config-layout">
        <!-- 左侧选择区域 -->
          <div class="selection-panel">
            <!-- Models 选择 -->
            <div class="config-section">
              <h2>Models <span class="required">*</span></h2>
              <div class="search-box">
                <div class="search-icon">🔍</div>
                <input
                  v-model="modelSearch"
                  type="text"
                  placeholder="搜索 models..."
                  @input="debouncedFilterModels"
                />
                <button
                  v-if="modelSearch"
                  class="clear-btn"
                  @click="modelSearch = '';"
                >
                  ✕
                </button>
              </div>
              <div class="items-list">
                <div
                  v-for="model in filteredModels"
                  :key="model.slug"
                  class="item-card"
                  :class="{ selected: selectedModels.some(m => m.slug === model.slug) }"
                  @click="toggleModel(model)"
                >
                  <div class="item-header">
                    <input
                      type="checkbox"
                      :checked="selectedModels.some(m => m.slug === model.slug)"
                      @change="toggleModel(model)"
                      :disabled="model.slug === BRAIN_MODEL_SLUG"
                    />
                    <div class="item-info">
                      <h3>{{ model.name }}</h3>
                      <p class="slug">{{ model.slug }}</p>
                    </div>
                  </div>
                  <p v-if="model.description" class="description">
                    {{ model.description }}
                  </p>
                  <div v-if="model.category" class="meta">
                    <span class="category">{{ model.category }}</span>
                    <span v-if="model.tags" class="tags">
                      {{ model.tags.join(', ') }}
                    </span>
                  </div>
                  
                  <!-- 每个Model的Rules选择区域 -->
                  <div class="model-rules" v-if="selectedModels.some(m => m.slug === model.slug) && modelRules[model.slug]">
                    <div class="model-rules-header">
                      <h4>Rules for {{ model.name }}</h4>
                      <div class="model-rules-actions">
                        <button
                          class="action-btn"
                          @click.stop="toggleAllModelRules(model.slug)"
                          :title="getAllRulesSelected(model.slug) ? '取消全选' : '全选'"
                        >
                          {{ getAllRulesSelected(model.slug) ? '取消全选' : '全选' }}
                        </button>
                      </div>
                    </div>
                    <div class="model-rules-list">
                      <div
                        v-for="(rule, name) in modelRules[model.slug]"
                        :key="name"
                        class="rule-item"
                        :class="{
                          selected: isRuleSelected(model.slug, name),
                          disabled: model.slug === BRAIN_MODEL_SLUG
                        }"
                        @click.stop="model.slug !== BRAIN_MODEL_SLUG && toggleModelRule(model.slug, name, rule)"
                      >
                        <div class="rule-header">
                          <input
                            type="checkbox"
                            :checked="isRuleSelected(model.slug, name)"
                            @change.stop="toggleModelRule(model.slug, name, rule)"
                            :disabled="model.slug === BRAIN_MODEL_SLUG"
                          />
                          <div class="rule-info">
                            <h5>{{ name }}</h5>
                          </div>
                        </div>
                        <div class="rule-preview" v-if="rule.content">
                          <pre>{{ rule.content.substring(0, PREVIEW_LENGTH) }}{{ rule.content.length > PREVIEW_LENGTH ? '...' : '' }}</pre>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

          <!-- Roles 选择 -->
          <div class="config-section">
            <h2>Roles (可选)</h2>
            <div class="items-list">
              <div
                v-for="(role, name) in availableRoles"
                :key="name"
                class="item-card"
                :class="{ selected: selectedRole?.name === name }"
                @click="selectRole(name, role)"
              >
                <div class="item-header">
                  <input
                    type="radio"
                    name="role"
                    :checked="selectedRole?.name === name"
                    @change="selectRole(name, role)"
                  />
                  <div class="item-info">
                    <h3>{{ name }}</h3>
                  </div>
                </div>
                <div class="role-preview" v-if="role.content">
                  <p>{{ role.content.substring(0, PREVIEW_LENGTH) }}{{ role.content.length > PREVIEW_LENGTH ? '...' : '' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Commands 选择 -->
          <div class="config-section">
            <h2>Commands</h2>
            <div class="items-list">
              <div
                v-for="(command, name) in availableCommands"
                :key="name"
                class="item-card"
                :class="{ selected: selectedCommands.some(c => c.name === name) }"
                @click="toggleCommand(name, command)"
              >
                <div class="item-header">
                  <input
                    type="checkbox"
                    :checked="selectedCommands.some(c => c.name === name)"
                    @change="toggleCommand(name, command)"
                  />
                  <div class="item-info">
                    <h3>{{ name }}</h3>
                  </div>
                </div>
                <div class="command-preview" v-if="command.content">
                  <pre>{{ command.content.substring(0, PREVIEW_LENGTH) }}{{ command.content.length > PREVIEW_LENGTH ? '...' : '' }}</pre>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- 右侧预览区域 -->
        <div class="preview-panel">
          <div class="preview-section">
            <div class="preview-header">
              <h2>配置预览</h2>
              <!-- 预览模式切换 -->
              <div class="preview-controls">
                <div class="mode-toggle">
                  <button
                    class="mode-btn"
                    :class="{ active: previewMode === 'detailed' }"
                    @click="previewMode = 'detailed'"
                  >
                    详细
                  </button>
                  <button
                    class="mode-btn"
                    :class="{ active: previewMode === 'simple' }"
                    @click="previewMode = 'simple'"
                  >
                    简洁
                  </button>
                </div>
              </div>
            </div>
            <div class="preview-content" v-if="hasSelection">
              <div class="preview-item" v-if="selectedModels.length > 0">
                <h3>Selected Models ({{ selectedModels.length }})</h3>
                <ul>
                  <li v-for="model in selectedModels" :key="model.slug">
                    <strong>{{ model.name }}</strong> ({{ model.slug }})
                    <ul v-if="selectedModelRules[model.slug] && selectedModelRules[model.slug].length > 0" class="sub-list">
                      <li v-for="ruleName in selectedModelRules[model.slug]" :key="ruleName">
                        {{ ruleName }}
                      </li>
                    </ul>
                  </li>
                </ul>
              </div>
              
              <div class="preview-item" v-if="selectedRole">
                <h3>Selected Role</h3>
                <p><strong>{{ selectedRole.name }}</strong></p>
              </div>
              
              <div class="preview-item" v-if="selectedCommands.length > 0">
                <h3>Selected Commands ({{ selectedCommands.length }})</h3>
                <ul>
                  <li v-for="command in selectedCommands" :key="command.name">{{ command.name }}</li>
                </ul>
              </div>
            </div>
            <div v-else class="empty-preview">
              <p>请选择配置项以查看预览</p>
            </div>
          </div>

          <!-- 操作按钮 -->
          <div class="actions">
            <button
              class="btn btn-primary"
              :disabled="!hasSelectedModels"
              @click="exportConfig"
            >
              导出配置
            </button>
            <button
              class="btn btn-secondary"
              @click="resetSelection"
            >
              重置选择
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import axios from 'axios'
import type { Model, Rule, Role, Command } from '@/types'

// 常量定义
const BRAIN_MODEL_SLUG = 'brain' as const
const PREVIEW_LENGTH = 100 as const
const DEBOUNCE_DELAY = 300 as const

// 简单的防抖函数实现
const debounce = (func: Function, delay: number) => {
  let timeoutId: number
  return function (this: any, ...args: any[]) {
    clearTimeout(timeoutId)
    timeoutId = window.setTimeout(() => func.apply(this, args), delay)
  }
}

// 创建防抖函数
const debouncedFilterModels = debounce(() => {
  // 使用计算属性的结果，无需手动过滤
}, DEBOUNCE_DELAY)

// 响应式数据
const models = ref<Model[]>([])
const selectedModels = ref<Model[]>([])
// availableRules 和 selectedRules 已不再使用，改为 modelRules 和 selectedModelRules
const availableRoles = ref<Record<string, Role>>({})
const selectedRole = ref<Role | null>(null)
const availableCommands = ref<Record<string, Command>>({})
const selectedCommands = ref<Command[]>([])
const hooks = ref({
  before: '',
  after: ''
})
const modelRules = ref<Record<string, Record<string, Rule>>>({})
const selectedModelRules = ref<Record<string, string[]>>({})
const modelSearch = ref('')
const previewMode = ref<'detailed' | 'simple'>('detailed')
const isLoading = ref(false)
const error = ref<string | null>(null)

// 计算属性
const hasSelection = computed(() => {
  return selectedModels.value.length > 0 ||
          Object.keys(selectedModelRules.value).length > 0 ||
          selectedRole.value !== null ||
          selectedCommands.value.length > 0
})

const hasSelectedModels = computed(() => {
  return selectedModels.value.length > 0
})

const hasBrainModel = computed(() => {
  return selectedModels.value.some(m => m.slug === BRAIN_MODEL_SLUG)
})

// 计算选中的rules总数
const totalSelectedRules = computed(() => {
  return Object.values(selectedModelRules.value).reduce((total, rules) => total + rules.length, 0)
})

// 检查规则是否被选中
const isRuleSelected = (modelSlug: string, ruleName: string) => {
  return selectedModelRules.value[modelSlug]?.includes(ruleName) || false
}

// 检查某个model的所有规则是否都被选中
const getAllRulesSelected = (modelSlug: string) => {
  const modelRuleNames = Object.keys(modelRules.value[modelSlug] || {})
  const selectedRuleNames = selectedModelRules.value[modelSlug] || []
  return modelRuleNames.length > 0 && modelRuleNames.every(name => selectedRuleNames.includes(name))
}

// 使用计算属性优化搜索过滤
const filteredModels = computed(() => {
  const searchTerm = modelSearch.value.toLowerCase()
  if (!searchTerm) {
    return models.value
  }
  
  return models.value.filter(model =>
    model.name.toLowerCase().includes(searchTerm) ||
    model.slug.toLowerCase().includes(searchTerm) ||
    model.description?.toLowerCase().includes(searchTerm) ||
    model.category?.toLowerCase().includes(searchTerm) ||
    model.tags?.some(tag => tag.toLowerCase().includes(searchTerm))
  )
})

// API 错误处理
const handleApiError = (error: any, context: string) => {
  console.error(`Failed to ${context}:`, error)
  error.value = `${context} 失败`
}

// 清除错误
const clearError = () => {
  error.value = null
}

// 方法
const fetchModels = async () => {
  clearError()
  try {
    const response = await axios.get('/api/models')
    models.value = response.data
    
    // 自动选择 brain 模型
    const brainModel = models.value.find(m => m.slug === BRAIN_MODEL_SLUG)
    if (brainModel) {
      selectedModels.value.push(brainModel)
      await fetchModelRules(BRAIN_MODEL_SLUG)
    }
  } catch (error) {
    handleApiError(error, 'fetch models')
  }
}

// 获取模型规则
const fetchModelRules = async (slug: string) => {
  clearError()
  try {
    const response = await axios.get(`/api/rules/${slug}`)
    const rules = response.data
    
    // 存储模型的规则
    modelRules.value[slug] = rules
    
    // 如果是brain模式，默认选中所有规则
    if (slug === BRAIN_MODEL_SLUG) {
      selectedModelRules.value[slug] = Object.keys(rules)
    } else {
      // 其他模式默认不选中任何规则
      selectedModelRules.value[slug] = []
    }
  } catch (error) {
    handleApiError(error, `fetch rules for ${slug}`)
  }
}

const fetchModelDetails = async (slug: string) => {
  try {
    const response = await axios.get(`/api/models/${slug}`)
    return response.data
  } catch (error) {
    console.error('Failed to fetch model details:', error)
    return null
  }
}

const fetchRules = async (slug: string) => {
  try {
    const response = await axios.get(`/api/rules/${slug}`)
    availableRules.value = response.data
  } catch (error) {
    console.error('Failed to fetch rules:', error)
  }
}

const fetchRoles = async () => {
  try {
    const response = await axios.get('/api/roles')
    availableRoles.value = response.data
  } catch (error) {
    console.error('Failed to fetch roles:', error)
  }
}

const fetchCommands = async () => {
  try {
    const response = await axios.get('/api/commands')
    availableCommands.value = response.data
  } catch (error) {
    console.error('Failed to fetch commands:', error)
  }
}

const fetchHooks = async () => {
  try {
    const [beforeResponse, afterResponse] = await Promise.all([
      axios.get('/api/hooks/before'),
      axios.get('/api/hooks/after')
    ])
    hooks.value = {
      before: beforeResponse.data,
      after: afterResponse.data
    }
  } catch (error) {
    console.error('Failed to fetch hooks:', error)
  }
}

// filterModels 函数已移除，使用计算属性 filteredModels 替代

const toggleModel = async (model: Model) => {
  const index = selectedModels.value.findIndex(m => m.slug === model.slug)
  
  if (index > -1) {
    // 不能取消选择 brain 模型
    if (model.slug === 'brain') {
      return
    }
    selectedModels.value.splice(index, 1)
    
    // 清理该模型的 rules 选择
    delete selectedModelRules.value[model.slug]
    delete modelRules.value[model.slug]
  } else {
    selectedModels.value.push(model)
    
    // 获取该 model 的 rules
    try {
      const response = await axios.get(`/api/rules/${model.slug}`)
      const newRules = response.data
      
      // 存储模型的 rules
      modelRules.value[model.slug] = newRules
      
      // 如果是brain模式，默认选中所有规则
      if (model.slug === BRAIN_MODEL_SLUG) {
        selectedModelRules.value[model.slug] = Object.keys(newRules)
      } else {
        // 其他模式默认不选中任何规则
        selectedModelRules.value[model.slug] = []
      }
    } catch (error) {
      console.error(`Failed to fetch rules for ${model.slug}:`, error)
    }
  }
}

// toggleRule 函数已移除，现在使用 toggleModelRule

const selectRole = (name: string, role: Role) => {
  if (selectedRole.value?.name === name) {
    selectedRole.value = null
  } else {
    selectedRole.value = { name, content: role.content }
  }
}

const toggleCommand = (name: string, command: Command) => {
  const index = selectedCommands.value.findIndex(c => c.name === name)
  if (index > -1) {
    selectedCommands.value.splice(index, 1)
  } else {
    selectedCommands.value.push({ name, content: command.content })
  }
}

// 切换单个模型的规则选择
const toggleModelRule = (modelSlug: string, ruleName: string, rule: Rule) => {
  // 如果是brain模式，不允许取消选择
  if (modelSlug === BRAIN_MODEL_SLUG) {
    return
  }
  
  if (!selectedModelRules.value[modelSlug]) {
    selectedModelRules.value[modelSlug] = []
  }
  
  const index = selectedModelRules.value[modelSlug].indexOf(ruleName)
  if (index > -1) {
    selectedModelRules.value[modelSlug].splice(index, 1)
  } else {
    selectedModelRules.value[modelSlug].push(ruleName)
  }
}

// 全选或取消全选某个模型的所有规则
const toggleAllModelRules = (modelSlug: string) => {
  // 如果是brain模式，不允许操作
  if (modelSlug === BRAIN_MODEL_SLUG) {
    return
  }
  
  const modelRuleNames = Object.keys(modelRules.value[modelSlug] || {})
  const selectedRuleNames = selectedModelRules.value[modelSlug] || []
  
  if (getAllRulesSelected(modelSlug)) {
    // 取消全选
    selectedModelRules.value[modelSlug] = []
  } else {
    // 全选
    selectedModelRules.value[modelSlug] = [...modelRuleNames]
  }
}

const resetSelection = () => {
  // 保留 brain 模型
  const brainModel = selectedModels.value.find(m => m.slug === 'brain')
  selectedModels.value = brainModel ? [brainModel] : []
  modelRules.value = {}
  selectedModelRules.value = {}
  selectedRole.value = null
  selectedCommands.value = []
  modelSearch.value = ''
  
  // 如果保留了 brain，重新加载它的 rules
  if (brainModel) {
    fetchModelRules(brainModel.slug)
  }
}

const exportConfig = () => {
  // 构建新的配置结构
  const config = {
    models: selectedModels.value,
    rules: {},
    roles: selectedRole.value ? [selectedRole.value] : [],
    commands: selectedCommands.value,
    hooks: hooks.value
  }
  
  // 为每个model添加其选中的rules
  selectedModels.value.forEach(model => {
    const selectedRules = selectedModelRules.value[model.slug] || []
    config.rules[model.slug] = selectedRules.map(ruleName => {
      const rule = modelRules.value[model.slug]?.[ruleName]
      return {
        name: ruleName,
        content: rule?.content || ''
      }
    })
  })
  
  // 创建下载链接
  const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  const modelNames = selectedModels.value.map(m => m.slug).join('-')
  a.download = `config-${modelNames}-${Date.now()}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

// watch 函数已移除，规则选择现在在 toggleModel 中处理

// 生命周期
onMounted(async () => {
  await Promise.all([
    fetchModels(),
    fetchRoles(),
    fetchCommands(),
    fetchHooks()
  ])
})
</script>

<style scoped>
.config-selector {
  min-height: 100vh;
  background: var(--bg-gradient);
  padding: 2rem 0;
  position: relative;
  overflow: hidden;
}

/* 添加科技感背景动画 */
.config-selector::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-image:
    radial-gradient(circle at 20% 20%, rgba(120, 255, 214, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 50%, rgba(120, 119, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 80%, rgba(255, 119, 198, 0.1) 0%, transparent 50%);
  animation: float 20s ease-in-out infinite;
  z-index: 0;
}

.container {
  max-width: 1600px;
  margin: 0 auto;
  padding: 0 2rem;
  position: relative;
  z-index: 1;
}

h1 {
  text-align: center;
  color: var(--text-primary);
  margin-bottom: 1rem;
  font-weight: 700;
  text-shadow: 0 0 20px rgba(120, 255, 214, 0.5);
}

.description {
  text-align: center;
  color: var(--text-secondary);
  margin-bottom: 3rem;
}

/* 左右布局 */
.config-layout {
  display: flex;
  gap: 2rem;
  min-height: 600px;
}

.selection-panel {
  flex: 1;
  overflow-y: auto;
  max-height: calc(100vh - 200px);
  padding-right: 0.5rem;
}

.preview-panel {
  flex: 0 0 400px;
  display: flex;
  flex-direction: column;
}

.config-section {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.3s ease;
}

.config-section:hover {
  border-color: var(--accent-cyan);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 20px rgba(120, 255, 214, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.config-section h2 {
  color: var(--text-primary);
  margin-bottom: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(120, 255, 214, 0.3);
}

.required {
  color: var(--accent-pink);
}

.section-desc {
  color: var(--text-secondary);
  margin-bottom: 1rem;
  font-size: 0.9rem;
}

.search-box {
  margin-bottom: 1rem;
  position: relative;
}

.search-box input {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 2px solid var(--glass-border);
  border-radius: 12px;
  font-size: 1rem;
  background: var(--glass-bg);
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.search-box input:focus {
  outline: none;
  border-color: var(--accent-cyan);
  box-shadow: 0 0 20px rgba(120, 255, 214, 0.3);
}

.search-box .search-icon {
  position: absolute;
  right: 15px;
  top: 50%;
  transform: translateY(-50%);
  color: var(--text-secondary);
  font-size: 1.2rem;
}

.search-box .clear-btn {
  position: absolute;
  right: 45px;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: var(--text-secondary);
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  transition: color 0.3s;
}

.search-box .clear-btn:hover {
  color: var(--accent-pink);
}

.items-list {
  max-height: 300px;
  overflow-y: auto;
  padding-right: 0.5rem;
}

.item-card {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--glass-bg);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  position: relative;
  overflow: hidden;
}

.item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.2), transparent);
  transition: left 0.5s ease;
}

.item-card:hover {
  border-color: var(--accent-cyan);
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(120, 255, 214, 0.2);
}

.item-card:hover::before {
  left: 100%;
}

.item-card.selected {
  border-color: var(--accent-cyan);
  background: var(--glass-bg-selected);
  box-shadow:
    0 8px 24px rgba(120, 255, 214, 0.3),
    inset 0 0 20px rgba(120, 255, 214, 0.1);
}

.item-header {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.item-header input[type="radio"],
.item-header input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0;
  color: #2c3e50;
  font-size: 1.1rem;
}

.slug {
  color: #7f8c8d;
  font-size: 0.85rem;
  margin: 0.25rem 0;
}

.description {
  color: #34495e;
  margin: 0.5rem 0 0 0;
  font-size: 0.9rem;
  line-height: 1.5;
}

.meta {
  display: flex;
  gap: 1rem;
  margin-top: 0.5rem;
}

.category {
  background: #3498db;
  color: white;
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.tags {
  color: #7f8c8d;
  font-size: 0.8rem;
}

.rule-preview,
.command-preview {
  margin-top: 0.5rem;
}

.rule-preview pre,
.command-preview pre {
  background: #f8f9fa;
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: 100px;
  overflow: hidden;
}

.role-preview p {
  color: #34495e;
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0.5rem 0 0 0;
}

.preview-section {
  background: white;
  border-radius: 12px;
  padding: 2rem;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
}

.preview-section h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
}

.preview-content {
  flex: 1;
  margin-bottom: 2rem;
}

.preview-item h3 {
  color: #42b983;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.preview-item ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.preview-item li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #ecf0f1;
  color: #34495e;
}

.preview-item li:last-child {
  border-bottom: none;
}

.preview-item p {
  margin: 0.5rem 0;
  color: #34495e;
}

.preview-item strong {
  color: #2c3e50;
}

.empty-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 200px;
  color: #7f8c8d;
  font-style: italic;
}

.actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 2rem;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background-color: #3aa876;
  transform: translateY(-2px);
}

.btn-secondary {
  background-color: #ecf0f1;
  color: #2c3e50;
}

.btn-secondary:hover {
  background-color: #d5dbdb;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 滚动条样式 */
.items-list::-webkit-scrollbar {
  width: 8px;
}

.items-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.items-list::-webkit-scrollbar-thumb {
  background: #c1c1c1;
  border-radius: 4px;
}

.items-list::-webkit-scrollbar-thumb:hover {
  background: #a8a8a8;
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .config-layout {
    flex-direction: column;
  }
  
  .preview-panel {
    flex: 1;
    max-width: none;
  }
}

@media (max-width: 768px) {
  .container {
    padding: 0 1rem;
  }
  
  .header {
    text-align: center;
  }
  
  .stats-bar {
    flex-wrap: wrap;
    gap: 1rem;
    justify-content: center;
  }
  
  .config-section {
    padding: 1rem;
  }
  
  .search-box {
    position: relative;
  }
  
  .search-box input {
    font-size: 0.9rem;
  }
  
  .preview-panel {
    margin-top: 1rem;
  }
  
  .preview-section {
    padding: 1.5rem;
  }
  
  .actions {
    flex-direction: row;
    justify-content: center;
  }
  
  .btn {
    flex: 1;
    max-width: 200px;
  }
}

@media (max-width: 480px) {
  h1 {
    font-size: 1.5rem;
  }
  
  .description {
    font-size: 0.9rem;
  }
  
  .stats-bar {
    gap: 0.5rem;
  }
  
  .stat-item {
    min-width: 60px;
  }
  
  .stat-value {
    font-size: 1.2rem;
  }
  
  .stat-label {
    font-size: 0.7rem;
  }
  
  .config-section h2 {
    font-size: 1.1rem;
  }
  
  .item-info h3 {
    font-size: 1rem;
  }
  
  .preview-section h2 {
    font-size: 1.1rem;
  }
  
  .mode-toggle {
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .mode-btn {
    padding: 0.5rem 1rem;
    font-size: 0.9rem;
  }
}
</style>