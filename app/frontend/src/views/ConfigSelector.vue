<template>
  <div class="config-selector">
    <div class="container">
      <div class="header">
        <h1>配置选择器</h1>
        <p class="description">选择您需要的 models、rules、roles 和 commands</p>
      </div>
      
      <!-- Global Search Filter -->
      <div class="global-search-section">
        <SearchFilter
          :initial-query="globalSearchQuery"
          placeholder="搜索 modes, rules, roles, commands..."
          :scopes="[
            { value: 'all', label: '全部' },
            { value: 'models', label: 'Modes' },
            { value: 'rules', label: 'Rules' },
            { value: 'roles', label: 'Roles' },
            { value: 'commands', label: 'Commands' }
          ]"
          :quick-filters="[
            { value: 'selected', label: '已选择' },
            { value: 'recent', label: '最近更新' }
          ]"
          @search="handleGlobalSearch"
          @filter-change="handleFilterChange"
        />
      </div>
      
      <div class="config-layout">
        <!-- 左侧选择区域 -->
        <div class="selection-panel">
          <!-- 标签页导航 -->
          <div class="tab-navigation">
            <div class="tab-header">
              <div
                v-for="tab in tabs"
                :key="tab.id"
                class="tab-item"
                :class="{ active: activeTab === tab.id }"
                @click="activeTab = tab.id"
              >
                <span class="tab-icon">{{ tab.icon }}</span>
                <span class="tab-label">{{ tab.label }}</span>
                <span v-if="tab.required" class="required-mark">*</span>
              </div>
            </div>
          </div>

          <!-- 标签页内容 -->
          <div class="tab-content">
            <!-- Models 选择 -->
            <div v-show="activeTab === 'models'" class="config-section">
              <h2>模式 <span class="required">*</span></h2>
              <div class="search-box">
                <div class="search-icon">🔍</div>
                <input
                  v-model="modelSearch"
                  type="text"
                  placeholder="搜索模式..."
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
                      :title="model.slug === BRAIN_MODEL_SLUG ? 'Orchestrator模式为必选项，不可取消' : ''"
                      class="custom-checkbox"
                      :class="{ 'required-checkbox': model.slug === BRAIN_MODEL_SLUG }"
                    />
                    <div class="item-info">
                      <h3 class="text-primary">
                        {{ model.name }}
                        <span v-if="model.slug === BRAIN_MODEL_SLUG" class="required-crown" title="必选项">👑</span>
                      </h3>
                      <p class="slug text-secondary">{{ model.slug }}</p>
                    </div>
                  </div>
                  <p v-if="model.description" class="description text-secondary">
                    {{ model.description }}
                  </p>
                  <div v-if="model.category" class="meta">
                    <span class="category text-inverted">{{ model.category }}</span>
                    <span v-if="model.tags" class="tags text-secondary">
                      {{ model.tags.join(', ') }}
                    </span>
                  </div>
                  
                  <!-- 每个Model的Rules选择区域 -->
                  <div class="model-rules" v-if="selectedModels.some(m => m.slug === model.slug) && modelRules[model.slug]">
                    <div class="model-rules-header">
                      <h4>{{ model.name }} 的规则</h4>
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
                        v-for="(rule, name) in (modelRules[model.slug] || {})"
                        :key="name"
                        class="rule-card"
                        :class="{
                          selected: isRuleSelected(model.slug, name),
                          disabled: model.slug === BRAIN_MODEL_SLUG
                        }"
                        @click.stop="model.slug !== BRAIN_MODEL_SLUG && toggleModelRule(model.slug, name, rule)"
                      >
                        <div class="rule-card-header">
                          <div class="rule-checkbox">
                            <input
                              type="checkbox"
                              :checked="isRuleSelected(model.slug, name)"
                              @change.stop="toggleModelRule(model.slug, name, rule)"
                              :disabled="model.slug === BRAIN_MODEL_SLUG"
                              class="custom-checkbox"
                            />
                          </div>
                          <div class="rule-title-section">
                            <h5 class="rule-title">{{ rule.metadata?.title || formatRuleName(name) }}</h5>
                            <div class="rule-badges" v-if="rule.metadata?.category || rule.metadata?.priority">
                              <span v-if="rule.metadata.category" class="category-badge">{{ rule.metadata.category }}</span>
                              <span v-if="rule.metadata.priority" class="priority-badge" :class="rule.metadata.priority">
                                {{ rule.metadata.priority }}
                              </span>
                            </div>
                          </div>
                          <div class="rule-status">
                            <span v-if="isRuleSelected(model.slug, name)" class="status-indicator selected">✓</span>
                            <span v-else class="status-indicator"></span>
                          </div>
                        </div>
                        <div class="rule-card-body">
                          <div class="rule-description" v-if="rule.metadata?.description">
                            {{ rule.metadata.description }}
                          </div>
                          <div class="rule-tags" v-if="rule.metadata?.tags && rule.metadata.tags.length > 0">
                            <span v-for="tag in rule.metadata.tags" :key="tag" class="tag">{{ tag }}</span>
                          </div>
                        </div>
                        <div class="rule-card-footer" v-if="previewMode === 'detailed' && rule.content">
                          <div class="content-preview">
                            <pre>{{ rule.content.substring(0, PREVIEW_LENGTH) }}{{ rule.content.length > PREVIEW_LENGTH ? '...' : '' }}</pre>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Roles 选择 -->
          <div v-show="activeTab === 'roles'" class="config-section">
            <h2>角色（可选）</h2>
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
                    class="custom-radio"
                  />
                  <div class="item-info">
                    <h3 class="text-primary">{{ name }}</h3>
                  </div>
                </div>
                <div class="role-preview" v-if="role.content || role.metadata">
                  <!-- 简洁模式：只显示标题和描述 -->
                  <div v-if="previewMode === 'simple' && role.metadata" class="role-metadata-simple">
                    <h5 v-if="role.metadata.title" class="role-title">{{ role.metadata.title }}</h5>
                    <p v-if="role.metadata.description" class="role-description">{{ role.metadata.description }}</p>
                    <div v-if="role.metadata.traits" class="role-traits">
                      <span class="traits-label">特质:</span>
                      <span class="traits-value">{{ Array.isArray(role.metadata.traits) ? role.metadata.traits.join(', ') : role.metadata.traits }}</span>
                    </div>
                  </div>
                  <!-- 详细模式：显示内容预览 -->
                  <div v-else class="role-content-preview">
                    <div v-if="role.metadata" class="role-metadata-header">
                      <h5>{{ role.metadata.title || name }}</h5>
                      <p v-if="role.metadata.description" class="meta-description">{{ role.metadata.description }}</p>
                    </div>
                    <p v-if="role.content">{{ role.content.substring(0, PREVIEW_LENGTH) }}{{ role.content.length > PREVIEW_LENGTH ? '...' : '' }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
  
            <!-- Commands 选择 -->
          <div v-show="activeTab === 'commands'" class="config-section">
            <h2>命令（可选）</h2>
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
                    class="custom-checkbox"
                  />
                  <div class="item-info">
                    <h3 class="text-primary">{{ name }}</h3>
                  </div>
                </div>
                <div class="command-preview" v-if="command.content || command.metadata">
                  <!-- 简洁模式：只显示标题和描述 -->
                  <div v-if="previewMode === 'simple' && command.metadata" class="command-metadata-simple">
                    <h5 v-if="command.metadata.title" class="command-title">{{ command.metadata.title }}</h5>
                    <p v-if="command.metadata.description" class="command-description">{{ command.metadata.description }}</p>
                    <div v-if="command.metadata.category || command.metadata.tags" class="command-meta-info">
                      <span v-if="command.metadata.category" class="category-tag">{{ command.metadata.category }}</span>
                      <span v-if="command.metadata.tags && command.metadata.tags.length > 0" class="tags">
                        {{ command.metadata.tags.join(', ') }}
                      </span>
                    </div>
                  </div>
                  <!-- 详细模式：显示内容预览 -->
                  <div v-else class="command-content-preview">
                    <div v-if="command.metadata" class="command-metadata-header">
                      <h5>{{ command.metadata.title || name }}</h5>
                      <p v-if="command.metadata.description" class="meta-description">{{ command.metadata.description }}</p>
                    </div>
                    <pre v-if="command.content">{{ command.content.substring(0, PREVIEW_LENGTH) }}{{ command.content.length > PREVIEW_LENGTH ? '...' : '' }}</pre>
                  </div>
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
              <div class="preview-grid">
                <!-- Models 预览 -->
                <div class="preview-card" v-if="selectedModels.length > 0">
                  <div class="card-header">
                    <div class="card-icon">🤖</div>
                    <h3>模式 ({{ selectedModels.length }})</h3>
                  </div>
                  <div class="card-content">
                    <div v-for="model in selectedModels" :key="model.slug" class="model-item">
                      <div class="model-name">
                        <span class="name-text">{{ model.name }}</span>
                        <span class="slug-text">({{ model.slug }})</span>
                      </div>
                      <!-- 简洁模式：显示模型元数据 -->
                      <div v-if="previewMode === 'simple' && model.metadata" class="model-metadata-simple">
                        <p v-if="model.metadata.description" class="meta-description">{{ model.metadata.description }}</p>
                        <div v-if="model.metadata.category || model.metadata.tags" class="model-meta-info">
                          <span v-if="model.metadata.category" class="category-tag">{{ model.metadata.category }}</span>
                          <span v-if="model.metadata.tags && model.metadata.tags.length > 0" class="tags">
                            {{ model.metadata.tags.join(', ') }}
                          </span>
                        </div>
                      </div>
                      <!-- 详细模式：显示具体规则标题 -->
                      <div v-else-if="selectedModelRules[model.slug] && selectedModelRules[model.slug].length > 0" class="rules-list">
                        <div v-for="ruleName in selectedModelRules[model.slug]" :key="ruleName" class="rule-item-small">
                          <span class="rule-name">{{ modelRules[model.slug]?.[ruleName]?.metadata?.title || ruleName }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Role 预览 -->
                <div class="preview-card" v-if="selectedRole">
                  <div class="card-header">
                    <div class="card-icon">🎭</div>
                    <h3>选择的角色</h3>
                  </div>
                  <div class="card-content">
                    <div class="role-item">
                      <span class="name-text">{{ selectedRole.name }}</span>
                      <!-- 简洁模式：显示角色元数据 -->
                      <div v-if="previewMode === 'simple' && selectedRole.metadata" class="role-metadata-simple">
                        <p v-if="selectedRole.metadata.description" class="meta-description">{{ selectedRole.metadata.description }}</p>
                        <div v-if="selectedRole.metadata.traits" class="role-traits">
                          <span class="traits-label">特质:</span>
                          <span class="traits-value">{{ Array.isArray(selectedRole.metadata.traits) ? selectedRole.metadata.traits.join(', ') : selectedRole.metadata.traits }}</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Commands 预览 -->
                <div class="preview-card" v-if="selectedCommands.length > 0">
                  <div class="card-header">
                    <div class="card-icon">⚡</div>
                    <h3>命令 ({{ selectedCommands.length }})</h3>
                  </div>
                  <div class="card-content">
                    <div class="commands-grid">
                      <div v-for="command in selectedCommands" :key="command.name" class="command-chip">
                        <span class="command-name">{{ command.name }}</span>
                        <!-- 简洁模式：显示命令元数据 -->
                        <div v-if="previewMode === 'simple' && command.metadata" class="command-metadata-simple">
                          <p v-if="command.metadata.description" class="meta-description">{{ command.metadata.description }}</p>
                          <div v-if="command.metadata.category || command.metadata.priority" class="command-meta-info">
                            <span v-if="command.metadata.category" class="category-tag">{{ command.metadata.category }}</span>
                            <span v-if="command.metadata.priority" class="priority-tag" :class="command.metadata.priority">
                              {{ command.metadata.priority }}
                            </span>
                          </div>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- Hooks 预览 -->
            <div class="preview-card" v-if="hooks.before || hooks.after">
              <div class="card-header">
                <div class="card-icon">🔗</div>
                <h3>钩子 ({{ (hooks.before ? 1 : 0) + (hooks.after ? 1 : 0) }})</h3>
              </div>
              <div class="card-content">
                <div class="hooks-list">
                  <!-- Before Hook -->
                  <div v-if="hooks.before" class="hook-item">
                    <div class="hook-name">
                      <span class="name-text">before</span>
                      <span class="hook-type">前置钩子</span>
                    </div>
                    <!-- 简洁模式：显示元数据 -->
                    <div v-if="previewMode === 'simple' && hooks.before.metadata" class="hook-metadata-simple">
                      <p v-if="hooks.before.metadata.title" class="meta-description">{{ hooks.before.metadata.title }}</p>
                      <p v-if="hooks.before.metadata.description" class="hook-description">{{ hooks.before.metadata.description }}</p>
                      <div v-if="hooks.before.metadata.category" class="hook-meta-info">
                        <span class="category-tag">{{ hooks.before.metadata.category }}</span>
                      </div>
                    </div>
                  </div>
                  <!-- After Hook -->
                  <div v-if="hooks.after" class="hook-item">
                    <div class="hook-name">
                      <span class="name-text">after</span>
                      <span class="hook-type">后置钩子</span>
                    </div>
                    <!-- 简洁模式：显示元数据 -->
                    <div v-if="previewMode === 'simple' && hooks.after.metadata" class="hook-metadata-simple">
                      <p v-if="hooks.after.metadata.title" class="meta-description">{{ hooks.after.metadata.title }}</p>
                      <p v-if="hooks.after.metadata.description" class="hook-description">{{ hooks.after.metadata.description }}</p>
                      <div v-if="hooks.after.metadata.category" class="hook-meta-info">
                        <span class="category-tag">{{ hooks.after.metadata.category }}</span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-preview">
              <div class="empty-icon">📋</div>
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
              <span class="btn-icon">📥</span>
              导出配置
            </button>
            <button
              class="btn btn-secondary"
              @click="openConfigManager"
            >
              <span class="btn-icon">💾</span>
              保存配置
            </button>
            <button
              class="btn btn-secondary"
              @click="resetSelection"
            >
              <span class="btn-icon">🔄</span>
              重置选择
            </button>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 配置管理器组件 -->
    <ConfigManager
      v-model:show="showConfigManager"
      @save="handleSaveConfig"
      @load="handleLoadConfig"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch, nextTick } from 'vue'
import api from '@/api'
import axios from 'axios'
import type { Model, Rule, Role, Command } from '@/types'
import SearchFilter from '@/components/SearchFilter.vue'
import ConfigManager from '@/components/ConfigManager.vue'
import '@/assets/optimized-ui.css'

// 常量定义
const BRAIN_MODEL_SLUG = 'orchestrator' as const
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

// 初始化函数
const initializeModelRules = (modelSlug: string) => {
  if (!modelRules.value[modelSlug]) {
    modelRules.value[modelSlug] = {}
  }
  if (!selectedModelRules.value[modelSlug]) {
    selectedModelRules.value[modelSlug] = []
  }
}
const modelSearch = ref('')

// 标签页相关
const activeTab = ref('models')
const tabs = ref([
  { id: 'models', label: '模式', icon: '🤖', required: true },
  { id: 'roles', label: '角色', icon: '🎭', required: false },
  { id: 'commands', label: '命令', icon: '⚡', required: false }
])
const previewMode = ref<'detailed' | 'simple'>('detailed')
const isLoading = ref(false)
const error = ref<string | null>(null)

// 配置管理器相关
const showConfigManager = ref(false)

// 全局搜索相关
const globalSearchQuery = ref('')
const searchFilterRef = ref()
const quickFilters = [
  { id: 'all', label: '全部', scope: 'all' },
  { id: 'models', label: 'Models', scope: 'models' },
  { id: 'rules', label: 'Rules', scope: 'rules' },
  { id: 'roles', label: 'Roles', scope: 'roles' },
  { id: 'commands', label: 'Commands', scope: 'commands' }
]

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
  const modelsArray = models.value || []
  
  if (!searchTerm) {
    return modelsArray
  }
  
  return modelsArray.filter(model =>
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
    const response = await api.post('/api/models')
    console.log('API Response from /api/models:', response)
    models.value = response || []
    console.log('Models value after assignment:', models.value)
    console.log('Models length:', models.value?.length)
    
    // 自动选择 orchestrator 模型
    const orchestratorModel = (models.value || []).find(m => m.slug === BRAIN_MODEL_SLUG)
    console.log('Found orchestrator model:', orchestratorModel)
    if (orchestratorModel) {
      console.log('Adding orchestrator to selected models')
      selectedModels.value.push(orchestratorModel)
      console.log('Selected models after push:', selectedModels.value)
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
    const response = await api.post('/api/rules/get', { slug })
    const rules = response || {}
    
    // 确保数据结构存在
    initializeModelRules(slug)
    
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
    const response = await api.post('/api/models/get', { slug })
    return response || {}
  } catch (error) {
    console.error('Failed to fetch model details:', error)
    return null
  }
}

const fetchRoles = async () => {
  try {
    const response = await api.post('/api/roles')
    availableRoles.value = response || {}
  } catch (error) {
    console.error('Failed to fetch roles:', error)
  }
}

const fetchCommands = async () => {
  try {
    const response = await api.post('/api/commands')
    console.log(response)
    availableCommands.value = response || {}
  } catch (error) {
    console.error('Failed to fetch commands:', error)
  }
}

const fetchHooks = async () => {
  try {
    const [beforeResponse, afterResponse] = await Promise.all([
      api.post('/api/hooks/before'),
      api.post('/api/hooks/after')
    ])
    hooks.value = {
      before: beforeResponse || '',
      after: afterResponse || ''
    }
  } catch (error) {
    console.error('Failed to fetch hooks:', error)
  }
}

const toggleModel = async (model: Model) => {
  const index = selectedModels.value.findIndex(m => m.slug === model.slug)
  
  if (index > -1) {
    // 不能取消选择 orchestrator 模型
    if (model.slug === BRAIN_MODEL_SLUG) {
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
      const response = await api.post('/api/rules/get', { slug: model.slug })
      const newRules = response || {}
      
      // 确保数据结构存在
      initializeModelRules(model.slug)
      
      // 存储模型的 rules
      modelRules.value[model.slug] = newRules
      
      // 如果是orchestrator模式，默认选中所有规则
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
  
  // 确保数据结构存在
  initializeModelRules(modelSlug)
  
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
  // 保留 orchestrator 模型
  const orchestratorModel = selectedModels.value.find(m => m.slug === BRAIN_MODEL_SLUG)
  selectedModels.value = orchestratorModel ? [orchestratorModel] : []
  modelRules.value = {}
  selectedModelRules.value = {}
  selectedRole.value = null
  selectedCommands.value = []
  modelSearch.value = ''
  
  // 如果保留了 orchestrator，重新加载它的 rules
  if (orchestratorModel) {
    fetchModelRules(orchestratorModel.slug)
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

// 生命周期
console.log('🎯 ConfigSelector 组件开始初始化')

onMounted(async () => {
  console.log('🚀 ConfigSelector 组件已挂载，开始获取数据')
  try {
    await Promise.all([
      fetchModels(),
      fetchRoles(),
      fetchCommands(),
      fetchHooks()
    ])
    console.log('✅ 所有初始数据获取完成')
  } catch (error) {
    console.error('❌ 初始数据获取失败:', error)
  }
  
  // 初始化时自动选择 orchestrator
  nextTick(() => {
    console.log('🔄 nextTick 回调执行')
    console.log('当前 models 长度:', (models.value || [])?.length)
    console.log('当前 selectedModels:', selectedModels.value)
    if (((models.value || [])?.length || 0) > 0 && !(selectedModels.value || []).some(m => m.slug === BRAIN_MODEL_SLUG)) {
      console.log('准备自动选择 orchestrator')
      const orchestratorModel = (models.value || []).find(m => m.slug === BRAIN_MODEL_SLUG)
      if (orchestratorModel) {
        console.log('添加 orchestrator 到已选择')
        selectedModels.value.push(orchestratorModel)
        fetchModelRules(orchestratorModel.slug)
      }
    } else {
      console.log('orchestrator 已经存在或 models 为空')
    }
  })
})

// 全局搜索处理函数
const handleGlobalSearch = (query: string, filters: any) => {
  globalSearchQuery.value = query
  
  // 更新搜索查询，但不过滤计算属性
  // 计算属性会根据 globalSearchQuery.value 自动更新
  // 实际的过滤逻辑在 filteredModels 计算属性中处理
}

// 处理搜索过滤器变化
const handleFilterChange = (filters: any) => {
  handleGlobalSearch(globalSearchQuery.value, filters)
}

// 配置管理相关方法
const openConfigManager = () => {
  showConfigManager.value = true
}

const handleSaveConfig = async (configName: string) => {
  // 构建配置数据
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
  
  // 使用配置存储保存
  const { useConfigStore } = await import('@/stores/config')
  const configStore = useConfigStore()
  
  try {
    await configStore.saveConfig(configName, config)
    // 可以在这里添加成功提示
  } catch (error) {
    console.error('保存配置失败:', error)
    // 可以在这里添加错误提示
  }
}

const handleLoadConfig = async (config: any) => {
  // 重置当前选择
  resetSelection()
  
  // 加载models
  if (config.models && Array.isArray(config.models)) {
    selectedModels.value = config.models
    
    // 为每个model加载rules
    for (const model of config.models) {
      await fetchModelRules(model.slug)
      
      // 加载该model选中的rules
      if (config.rules && config.rules[model.slug]) {
        selectedModelRules.value[model.slug] = config.rules[model.slug].map((rule: any) => rule.name)
      }
    }
  }
  
  // 加载role
  if (config.roles && config.roles.length > 0) {
    const role = config.roles[0]
    selectedRole.value = role
  }
  
  // 加载commands
  if (config.commands && Array.isArray(config.commands)) {
    selectedCommands.value = config.commands
  }
}
</script>

<style scoped>
/* 自定义表单控件样式 */
:deep(.custom-checkbox) {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  cursor: pointer;
  accent-color: #10b981;
}

:deep(.custom-radio) {
  width: 24px;
  height: 24px;
  min-width: 24px;
  min-height: 24px;
  cursor: pointer;
  accent-color: #3b82f6;
}

/* 按钮样式增强 */
.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.btn-secondary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  color: #ffffff;
  border: 1px solid rgba(99, 102, 241, 0.5);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-secondary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-color: rgba(99, 102, 241, 0.5);
  transform: translateY(-2px);
}

.btn-success {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
  border: none;
  padding: 0.75rem 2rem;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
  min-height: 44px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.btn-success:hover {
  background: linear-gradient(135deg, #059669 0%, #047857 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(16, 185, 129, 0.6);
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* 搜索清除按钮 */
.clear-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
  width: 28px;
  height: 28px;
  border-radius: 50%;
  background: var(--glass-bg);
  border: 1px solid var(--border-color);
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  transition: all 0.3s ease;
  font-size: 16px;
  line-height: 1;
}

.clear-btn:hover {
  background: var(--danger-color);
  color: white;
  border-color: var(--danger-color);
  transform: translateY(-50%) scale(1.1);
}

.clear-btn:active {
  transform: translateY(-50%) scale(0.95);
}

/* 操作按钮 */
.action-btn {
  background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.3);
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.action-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.action-btn:active {
  transform: translateY(0);
}

/* 模式切换按钮 */
.mode-btn {
  background: var(--glass-bg);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  padding: 0.5rem 1rem;
  border-radius: 6px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  min-height: 36px;
  display: inline-flex;
  align-items: center;
  justify-content: center;
}

.mode-btn:first-child {
  border-top-right-radius: 0;
  border-bottom-right-radius: 0;
  border-right: none;
}

.mode-btn:last-child {
  border-top-left-radius: 0;
  border-bottom-left-radius: 0;
  border-left: none;
}

.mode-btn.active {
  background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
  color: white;
  border-color: transparent;
}

.mode-btn:hover:not(.active) {
  background: rgba(255, 255, 255, 0.1);
}

.btn-icon {
  margin-right: 0.5rem;
}

/* Tab Navigation Styles */
.tab-navigation {
  margin-bottom: 1.5rem;
  position: relative;
}

.tab-navigation::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.3), transparent);
  opacity: 0.5;
}

.tab-header {
  display: flex;
  gap: 0.5rem;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 0.25rem;
  overflow-x: auto;
  scrollbar-width: thin;
  scrollbar-color: rgba(120, 255, 214, 0.3) transparent;
}

.tab-header::-webkit-scrollbar {
  height: 4px;
}

.tab-header::-webkit-scrollbar-track {
  background: transparent;
}

.tab-header::-webkit-scrollbar-thumb {
  background: rgba(120, 255, 214, 0.3);
  border-radius: 2px;
}

.tab-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.25rem;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
  white-space: nowrap;
  user-select: none;
  position: relative;
  overflow: hidden;
}

.tab-item::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.2), transparent);
  transition: left 0.5s ease;
}

.tab-item:hover {
  background: rgba(255, 255, 255, 0.05);
  transform: translateY(-2px);
}

.tab-item:hover::before {
  left: 100%;
}

.tab-item.active {
  background: linear-gradient(135deg, var(--accent-cyan) 0%, var(--accent-purple) 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(120, 255, 214, 0.4);
}

.tab-item.active::before {
  display: none;
}

.tab-icon {
  font-size: 1.2rem;
  filter: grayscale(0.5);
  transition: all 0.3s ease;
}

.tab-item.active .tab-icon {
  filter: grayscale(0);
  transform: scale(1.1);
}

.tab-label {
  font-weight: 500;
  font-size: 0.95rem;
}

.tab-item:not(.active) .tab-label {
  color: var(--text-secondary);
}

.required-mark {
  color: var(--accent-pink);
  font-weight: bold;
  margin-left: 0.25rem;
  animation: pulse 2s ease-in-out infinite;
}

/* Tab Content Styles */
.tab-content {
  min-height: 400px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* Tab content sections should have consistent spacing */
.tab-content .config-section {
  animation: slideIn 0.4s ease;
}

@keyframes slideIn {
  from {
    opacity: 0;
    transform: translateX(-20px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

/* Global Search Section */
.global-search-section {
  margin-bottom: 2rem;
  position: relative;
}

.global-search-section::after {
  content: '';
  position: absolute;
  bottom: -1rem;
  left: 0;
  right: 0;
  height: 1px;
  background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.3), transparent);
  opacity: 0.5;
}

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
  /* 移除固定高度，允许根据内容自动调整 */
}

.selection-panel {
  flex: 1;
  overflow-y: auto;
  /* 移除最大高度限制，允许面板根据内容扩展 */
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
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid rgba(0, 245, 255, 0.3);
  border-radius: 30px;
  background: rgba(15, 23, 42, 0.8);
  color: #ffffff;
  font-size: 1rem;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  min-height: 44px;
}

.search-box input::placeholder {
  color: #64748b;
}

.search-box input:focus {
  outline: none;
  border-color: #00f5ff;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.search-box .search-icon {
  position: absolute;
  left: 1rem;
  top: 50%;
  transform: translateY(-50%);
  color: #64748b;
  font-size: 1.2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.search-box .clear-btn {
  position: absolute;
  right: 1rem;
  top: 50%;
  transform: translateY(-50%);
  background: none;
  border: none;
  color: #64748b;
  cursor: pointer;
  font-size: 1.2rem;
  padding: 0.25rem;
  transition: color 0.3s;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
}

.search-box .clear-btn:hover {
  color: var(--accent-pink);
}

.items-list {
  max-height: none;
  overflow-y: visible;
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
  min-height: 44px;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.item-card:has(.rule-header) {
  min-height: auto;
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

.rule-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  min-height: 44px;
  padding: 12px 0;
.rule-header input[type="radio"],
/* 自定义checkbox样式 */
.rule-header input[type="checkbox"] {
  appearance: none;
  -webkit-appearance: none;
  position: relative;
  border: 2px solid var(--border-color);
  border-radius: 4px;
  background: var(--glass-bg);
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rule-header input[type="checkbox"]:checked {
  background: var(--accent-cyan);
  border-color: var(--accent-cyan);
}

.rule-header input[type="checkbox"]:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 18px;
  font-weight: bold;
}

.rule-header input[type="checkbox"]:hover:not(:disabled) {
  border-color: var(--accent-cyan);
  transform: scale(1.1);
}

.rule-header input[type="checkbox"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

/* 自定义radio样式 */
.rule-header input[type="radio"] {
  appearance: none;
  -webkit-appearance: none;
  position: relative;
  border: 2px solid var(--border-color);
  border-radius: 50%;
  background: var(--glass-bg);
  width: 28px;
  height: 28px;
  min-width: 28px;
  min-height: 28px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.rule-header input[type="radio"]:checked {
  background: var(--accent-cyan);
  border-color: var(--accent-cyan);
}

.rule-header input[type="radio"]:checked::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: white;
}

.rule-header input[type="radio"]:hover:not(:disabled) {
  border-color: var(--accent-cyan);
  transform: scale(1.1);
}

.rule-header input[type="radio"]:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.item-info {
  flex: 1;
}

.item-info h3 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.1rem;
  font-weight: 600;
}

.slug {
  color: var(--text-secondary);
  font-size: 0.85rem;
  margin: 0.25rem 0;
  font-weight: 500;
}

.description {
  color: var(--text-secondary);
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
  background: var(--accent-blue);
  color: var(--text-inverted);
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
}

.tags {
  color: var(--text-tertiary);
  font-size: 0.8rem;
  font-weight: 500;
}

.rule-preview,
.command-preview {
  margin-top: 0.5rem;
}

.rule-preview pre,
.command-preview pre {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 0.5rem;
  border-radius: 4px;
  font-size: 0.8rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  max-height: none;
  overflow: visible;
}

.role-preview p {
  color: var(--text-muted);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0.5rem 0 0 0;
}

.preview-section {
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid var(--glass-border);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
}

.preview-section:hover {
  border-color: var(--accent-cyan);
  box-shadow:
    0 8px 32px rgba(0, 0, 0, 0.4),
    0 0 20px rgba(120, 255, 214, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.preview-section h2 {
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  font-weight: 600;
  text-shadow: 0 0 10px rgba(120, 255, 214, 0.3);
}

.preview-content {
  flex: 1;
  margin-bottom: 2rem;
  max-height: none;
  overflow-y: visible;
  padding-right: 0.5rem;
}

/* 自定义滚动条样式 */
.preview-content::-webkit-scrollbar {
  width: 6px;
}

.preview-content::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb {
  background: rgba(120, 255, 214, 0.3);
  border-radius: 3px;
}

.preview-content::-webkit-scrollbar-thumb:hover {
  background: rgba(120, 255, 214, 0.5);
}

/* 预览网格布局 */
.preview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 20px;
  margin-bottom: 20px;
}

.preview-card {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(147, 51, 234, 0.1) 100%);
  border: 1px solid rgba(99, 102, 241, 0.3);
  border-radius: 12px;
  padding: 20px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.preview-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, #3b82f6, #8b5cf6, #ec4899);
  transform: scaleX(0);
  transition: transform 0.3s ease;
}

.preview-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.5);
}

.preview-card:hover::before {
  transform: scaleX(1);
}

.preview-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.preview-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.preview-title .icon {
  width: 24px;
  height: 24px;
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 14px;
}

.preview-count {
  background: var(--accent-blue-bg);
  color: var(--accent-blue-text);
  padding: 4px 12px;
  border-radius: 20px;
  font-size: 14px;
  font-weight: 500;
  border: 1px solid var(--accent-blue-border);
}

.preview-content {
  color: var(--text-secondary);
  line-height: 1.6;
}

.preview-content .command-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.preview-content .command-chip {
  background: var(--chip-bg);
  border: 1px solid var(--chip-border);
  color: var(--chip-text);
  padding: 6px 12px;
  border-radius: 6px;
  font-size: 13px;
  font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  transition: all 0.2s ease;
}

.preview-content .command-chip:hover {
  background: var(--chip-bg-hover);
  color: var(--chip-text-hover);
  border-color: var(--chip-border-hover);
  transform: scale(1.05);
}

/* 适配原有的卡片结构 */
.preview-card .card-header {
  padding: 0;
  background: none;
  border: none;
}

.preview-card .card-icon {
  width: 24px;
  height: 24px;
  font-size: 14px;
}

.preview-card .card-content {
  padding: 0;
}

.preview-card .model-item {
  padding: 8px 0;
}

.preview-card .model-item:last-child {
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
}

.preview-card .count-badge {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  padding: 4px 12px;
  border-radius: 12px;
  font-size: 13px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(99, 102, 241, 0.3);
}

/* 规则列表样式 */
.rules-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.rule-item-small {
  display: flex;
  align-items: center;
  padding: 0.5rem 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  border-left: 3px solid var(--accent-cyan);
  transition: all 0.3s ease;
}

.rule-item-small:hover {
  background: rgba(59, 130, 246, 0.15);
  transform: translateX(4px);
}

.rule-item-small .rule-name {
  color: var(--text-primary);
  font-size: 0.9rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.preview-card .commands-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.preview-card .role-item {
  padding: 8px 0;
}

.empty-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 120px;
  color: var(--text-secondary);
  background: var(--glass-bg);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  border-style: dashed;
  gap: 1rem;
}

.empty-icon {
  font-size: 3rem;
  opacity: 0.5;
  animation: pulse 2s ease-in-out infinite;
}

@keyframes pulse {
  0%, 100% { transform: scale(1); opacity: 0.5; }
  50% { transform: scale(1.1); opacity: 0.8; }
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
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
  border: none;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

.btn-secondary {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.1) 0%, rgba(255, 255, 255, 0.05) 100%);
  color: #ffffff;
  border: 1px solid rgba(99, 102, 241, 0.5);
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.15) 0%, rgba(255, 255, 255, 0.1) 100%);
  border-color: rgba(99, 102, 241, 0.5);
  transform: translateY(-2px);
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
  background: var(--scrollbar-track);
  border-radius: 4px;
}

.items-list::-webkit-scrollbar-thumb {
  background: var(--scrollbar-thumb);
  border-radius: 4px;
}

.items-list::-webkit-scrollbar-thumb:hover {
  background: var(--scrollbar-thumb-hover);
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .config-container {
    padding: 1.5rem;
  }

  .config-content {
    grid-template-columns: 1fr 300px;
  }
}

@media (max-width: 968px) {
  .config-container {
    padding: 1rem;
  }

  .config-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 1rem;
  }

  .config-content {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }

  .selection-panel {
    order: 2;
  }

  .config-summary {
    order: 1;
    position: sticky;
    top: 1rem;
  }

  .tab-header {
    padding: 0.25rem;
    border-radius: 8px;
  }

  .tab-item {
    padding: 0.6rem 1rem;
    font-size: 0.9rem;
  }

  .tab-icon {
    font-size: 1rem;
  }
}

@media (max-width: 768px) {
  .config-container {
    padding: 0.75rem;
  }

  .config-header h1 {
    font-size: 1.5rem;
  }

  .config-header p {
    font-size: 0.9rem;
  }

  .selection-panel {
    padding: 1rem;
  }

  .section-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .section-title {
    font-size: 1.1rem;
  }

  .search-box {
    position: relative;
  }

  .search-box input {
    padding: 0.6rem 2.25rem 0.6rem 0.875rem;
    font-size: 0.9rem;
  }

  .search-icon {
    left: 0.75rem;
    font-size: 1rem;
  }

  .item-card {
    padding: 0.875rem;
    border-radius: 8px;
  }

  .item-title {
    font-size: 1rem;
  }

  .item-description {
    font-size: 0.85rem;
    line-height: 1.4;
  }

  .item-actions {
    width: 100%;
    gap: 0.5rem;
  }

  .action-button {
    flex: 1;
    padding: 0.5rem;
    font-size: 0.85rem;
    min-height: 36px;
  }

  .config-summary {
    padding: 1rem;
    border-radius: 12px;
  }

  .summary-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .summary-title {
    font-size: 1.1rem;
  }

  .selection-stats {
    grid-template-columns: 1fr;
    gap: 0.75rem;
  }

  .stats-card {
    padding: 0.75rem;
  }

  .stats-value {
    font-size: 1.25rem;
  }

  .stats-label {
    font-size: 0.85rem;
  }

  .selected-items {
    max-height: 300px;
  }

  .selected-item {
    padding: 0.6rem;
    font-size: 0.85rem;
  }

  .empty-state {
    padding: 2rem 1rem;
  }

  .empty-icon {
    font-size: 3rem;
  }

  .export-button {
    width: 100%;
    padding: 0.75rem;
    justify-content: center;
  }

  /* Tab navigation adjustments for mobile */
  .tab-navigation {
    margin-bottom: 1rem;
  }

  .tab-navigation::after {
    bottom: -0.75rem;
  }

  .tab-header {
    gap: 0.25rem;
    padding: 0.125rem;
    background: rgba(255, 255, 255, 0.03);
  }

  .tab-item {
    padding: 0.5rem 0.875rem;
    border-radius: 6px;
    font-size: 0.85rem;
  }

  .tab-item.active {
    transform: scale(1.02);
  }

  .tab-icon {
    font-size: 0.9rem;
  }

  .required-mark {
    font-size: 0.8rem;
  }

  .tab-content {
    min-height: 350px;
  }

  /* Global search section adjustments */
  .global-search-section {
    margin-bottom: 1rem;
  }

  .global-search-section::after {
    bottom: -0.75rem;
  }

  /* Model rules adjustments */
  .model-rules-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.5rem;
  }

  .model-rules-actions {
    width: 100%;
    justify-content: flex-start;
  }

  .model-rules-list {
    gap: 0.75rem;
  }
  
  /* 规则卡片样式 */
  .model-rules-list .rule-item {
    border: 1px solid var(--glass-border);
    border-radius: 12px;
    padding: 1rem;
    background: var(--glass-bg);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
    transition: all 0.3s ease;
    cursor: pointer;
    position: relative;
    overflow: hidden;
  }
  
  .model-rules-list .rule-item::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.1), transparent);
    transition: left 0.5s ease;
  }
  
  .model-rules-list .rule-item:hover {
    border-color: var(--accent-cyan);
    transform: translateY(-2px);
    box-shadow:
      0 8px 24px rgba(0, 0, 0, 0.3),
      0 0 16px rgba(120, 255, 214, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.2);
  }
  
  .model-rules-list .rule-item:hover::before {
    left: 100%;
  }
  
  .model-rules-list .rule-item.selected {
    border-color: var(--accent-cyan);
    background: var(--glass-bg-selected);
    box-shadow:
      0 8px 24px rgba(120, 255, 214, 0.3),
      inset 0 0 20px rgba(120, 255, 214, 0.1);
  }
  
  .model-rules-list .rule-item.selected::before {
    display: none;
  }
  
  .model-rules-list .rule-item.disabled {
    opacity: 0.7;
    cursor: not-allowed;
  }
  
  .model-rules-list .rule-item.disabled:hover {
    transform: none;
    box-shadow:
      0 4px 12px rgba(0, 0, 0, 0.2),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }
  
  /* 规则卡片头部 */
  .model-rules-list .rule-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.5rem 0;
    gap: 1rem;
  }
  
  .model-rules-list .rule-info {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .model-rules-list .rule-info h5 {
    margin: 0;
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
    line-height: 1.4;
  }
  
  .model-rules-list .rule-description {
    color: var(--text-secondary);
    font-size: 0.875rem;
    line-height: 1.5;
    margin: 0;
  }
  
  /* 规则参数区域 */
  .model-rules-list .rule-params {
    margin-top: 0.75rem;
    padding-top: 0.75rem;
    border-top: 1px solid rgba(255, 255, 255, 0.1);
  }
  
  .model-rules-list .param-item {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.25rem 0;
    font-size: 0.875rem;
  }
  
  .model-rules-list .param-name {
    color: var(--accent-cyan);
    font-weight: 600;
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
  }
  
  .model-rules-list .param-value {
    color: var(--text-secondary);
    font-family: 'SF Mono', Monaco, 'Cascadia Code', monospace;
    background: rgba(59, 130, 246, 0.1);
    padding: 0.125rem 0.5rem;
    border-radius: 4px;
  }
  
  /* 响应式调整 */
  @media (max-width: 768px) {
    .model-rules-list {
      gap: 0.5rem;
    }
    
    .model-rules-list .rule-item {
      padding: 0.75rem;
    }
    
    .model-rules-list .rule-info h5 {
      font-size: 0.95rem;
    }
    
    .model-rules-list .rule-description {
      font-size: 0.8rem;
    }
    
    .model-rules-list .param-item {
      flex-direction: column;
      align-items: flex-start;
      gap: 0.25rem;
    }
    
    .model-rules-list .param-value {
      width: 100%;
      text-align: left;
    }
  }
  }

  .rule-item {
    padding: 0.75rem;
  }

  .rule-header {
    padding: 0.75rem 0;
  }

  /* Preview adjustments */
  .preview-panel {
    margin-top: 1rem;
  }

  .preview-section {
    padding: 1.5rem;
  }

  .preview-header {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.75rem;
  }

  .preview-controls {
    width: 100%;
  }

  .mode-toggle {
    width: 100%;
  }

  .preview-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .preview-card {
    padding: 1rem;
  }

  .preview-header {
    margin-bottom: 12px;
  }

  .preview-title {
    font-size: 1rem;
  }

  .preview-title .icon {
    width: 20px;
    height: 20px;
    font-size: 12px;
  }

  .preview-count {
    padding: 0.25rem 0.75rem;
    font-size: 12px;
  }

  /* Actions adjustments */
  .actions {
    flex-direction: column;
    gap: 0.75rem;
  }

  .btn {
    width: 100%;
    max-width: none;
  }
}

@media (max-width: 480px) {
  .config-container {
    padding: 0.5rem;
  }

  .config-header h1 {
    font-size: 1.25rem;
  }

  .config-header p {
    font-size: 0.85rem;
    margin-bottom: 1.5rem;
  }

  .global-search-section {
    margin-bottom: 0.75rem;
  }

  .search-box {
    margin-bottom: 0.75rem;
  }

  .search-box input {
    padding: 0.5rem 2.125rem 0.5rem 0.875rem;
  }

  .item-card {
    padding: 0.75rem;
  }

  .item-actions {
    flex-direction: column;
  }

  .action-button {
    width: 100%;
    min-height: 44px;
  }

  .config-summary {
    padding: 0.75rem;
  }

  .stats-card {
    padding: 0.625rem;
  }

  .stats-value {
    font-size: 1.125rem;
  }

  .selected-items {
    max-height: 250px;
  }

  .selected-item {
    padding: 0.5rem;
  }

  .empty-state {
    padding: 1.5rem 0.75rem;
  }

  .empty-icon {
    font-size: 2.5rem;
  }

  /* Touch-friendly adjustments */
  .tab-item {
    min-height: 44px;
    padding: 0.625rem 1rem;
  }

  .action-button {
    min-height: 44px;
  }

  /* Compact mode for very small screens */
  .tab-header {
    gap: 0.125rem;
  }

  .tab-item {
    padding: 0.5rem 0.75rem;
    font-size: 0.8rem;
  }

  .tab-icon {
    font-size: 0.85rem;
  }

  .required-mark {
    font-size: 0.75rem;
  }

  .config-section h2 {
    font-size: 1rem;
  }

  .item-info h3 {
    font-size: 0.95rem;
  }

  .preview-section h2 {
    font-size: 1rem;
  }

  .mode-btn {
    padding: 0.5rem 0.875rem;
    font-size: 0.85rem;
  }
}
</style>

<!-- 元数据显示样式增强 -->
<style scoped>
/* 元数据显示通用样式 */
.metadata-simple {
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.08);
  border-radius: 8px;
  border-left: 3px solid var(--accent-cyan);
  margin-top: 0.5rem;
}

.meta-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 0.5rem 0;
  font-style: italic;
  font-weight: 500;
}

/* 分类和标签样式 */
.category-tag {
  background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-block;
  margin-right: 0.5rem;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.tags {
  color: var(--text-muted);
  font-size: 0.8rem;
}

/* 规则特定样式 */
.rule-metadata-simple .rule-title {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.rule-metadata-simple .rule-title::before {
  content: '📋';
  font-size: 1.1rem;
}

.rule-metadata-simple .rule-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0 0 0.5rem 0;
  font-weight: 500;
}

.rule-meta-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
}

/* 角色特定样式 */
.role-metadata-simple .role-title {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.role-metadata-simple .role-title::before {
  content: '🎭';
  font-size: 1.1rem;
}

.role-traits {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem;
  background: rgba(147, 51, 234, 0.15);
  border-radius: 6px;
  margin-top: 0.5rem;
}

.traits-label {
  color: var(--accent-purple);
  font-weight: 600;
  font-size: 0.85rem;
}

.traits-value {
  color: var(--text-secondary);
  font-size: 0.9rem;
  font-weight: 500;
}

/* 命令特定样式 */
.command-metadata-simple .command-title {
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  margin: 0 0 0.25rem 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.command-metadata-simple .command-title::before {
  content: '⚡';
  font-size: 1.1rem;
}

.command-meta-info {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.priority-tag {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-tag.high {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.priority-tag.medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.priority-tag.low {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.priority-tag.critical {
  background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

/* 模型元数据样式 */
.model-metadata-simple {
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.05);
  border-radius: 8px;
  border: 1px solid rgba(59, 130, 246, 0.2);
  margin-top: 0.5rem;
}

.model-meta-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-top: 0.5rem;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .metadata-simple {
    padding: 0.5rem;
  }
  
  .rule-meta-info,
  .command-meta-info,
  .model-meta-info {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .role-traits {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
}
</style>
  
  /* Hooks 特定样式 */
  .hook-metadata-simple .hook-title {
    color: var(--text-primary);
    font-size: 1rem;
    font-weight: 600;
    margin: 0 0 0.25rem 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
  }
  
  .hook-metadata-simple .hook-title::before {
    content: '🔗';
    font-size: 1.1rem;
  }
  
  .hook-metadata-simple .hook-description {
    color: var(--text-secondary);
    font-size: 0.9rem;
    line-height: 1.5;
    margin: 0 0 0.5rem 0;
    font-weight: 500;
  }
  
  .hook-metadata-simple .hook-type {
    display: inline-block;
    padding: 0.25rem 0.5rem;
    background: var(--accent-blue);
    color: white;
    border-radius: 4px;
    font-size: 0.75rem;
    font-weight: 500;
    margin-left: 0.5rem;
  }
  
  .hook-meta-info {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    flex-wrap: wrap;
    margin-top: 0.5rem;
  }
  
  .hook-name {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-bottom: 0.5rem;
  }
  
  .hook-name .name-text {
    color: var(--text-primary);
    font-weight: 600;
  }
  
  .hook-name .hook-type {
    font-size: 0.85rem;
    padding: 0.25rem 0.75rem;
    border-radius: 12px;
    font-weight: 500;
  }
  
  .hook-name .hook-type.before {
    background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
    color: white;
  }
  
  .hook-name .hook-type.after {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
  }

/* Rule Card Styles */
.rule-card {
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1rem;
  margin-bottom: 0.75rem;
  cursor: pointer;
  transition: all 0.3s ease;
  background: var(--glass-bg);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.rule-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(120, 255, 214, 0.2), transparent);
  transition: left 0.5s ease;
}

.rule-card:hover {
  border-color: var(--accent-cyan);
  transform: translateY(-2px);
  box-shadow: 
    0 8px 24px rgba(0, 0, 0, 0.3),
    0 0 16px rgba(120, 255, 214, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.rule-card:hover::before {
  left: 100%;
}

.rule-card.selected {
  border-color: var(--accent-cyan);
  background: var(--glass-bg-selected);
  box-shadow: 
    0 8px 24px rgba(120, 255, 214, 0.3),
    inset 0 0 20px rgba(120, 255, 214, 0.1);
}

.rule-card.selected::before {
  display: none;
}

.rule-card.disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.rule-card.disabled:hover {
  transform: none;
  box-shadow: 
    0 4px 12px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
}

.rule-card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 0.75rem;
  gap: 1rem;
}

.rule-checkbox {
  flex-shrink: 0;
}

.rule-title-section {
  flex: 1;
  min-width: 0;
}

.rule-title {
  margin: 0;
  color: var(--text-primary);
  font-size: 1rem;
  font-weight: 600;
  line-height: 1.4;
}

.rule-badges {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-top: 0.25rem;
}

.category-badge {
  background: linear-gradient(135deg, var(--accent-blue) 0%, var(--accent-purple) 100%);
  color: white;
  padding: 0.25rem 0.75rem;
  border-radius: 12px;
  font-size: 0.75rem;
  font-weight: 500;
  display: inline-block;
  box-shadow: 0 2px 4px rgba(59, 130, 246, 0.3);
}

.priority-badge {
  padding: 0.25rem 0.5rem;
  border-radius: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  text-transform: uppercase;
}

.priority-badge.critical {
  background: linear-gradient(135deg, #ef4444 0%, #991b1b 100%);
  color: white;
  animation: pulse 2s ease-in-out infinite;
}

.priority-badge.high {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  color: white;
}

.priority-badge.medium {
  background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
  color: white;
}

.priority-badge.low {
  background: linear-gradient(135deg, #10b981 0%, #059669 100%);
  color: white;
}

.rule-status {
  flex-shrink: 0;
  width: 24px;
  height: 24px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.status-indicator {
  width: 20px;
  height: 20px;
  border-radius: 50%;
  background: var(--glass-bg);
  border: 2px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 12px;
  font-weight: bold;
  transition: all 0.3s ease;
}

.status-indicator.selected {
  background: var(--accent-cyan);
  border-color: var(--accent-cyan);
  color: white;
}

.rule-card-body {
  margin-bottom: 0.75rem;
}

.rule-description {
  color: var(--text-secondary);
  font-size: 0.9rem;
  line-height: 1.5;
  margin: 0;
}

.rule-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-top: 0.5rem;
}

.rule-tags .tag {
  background: rgba(59, 130, 246, 0.1);
  color: var(--text-secondary);
  padding: 0.25rem 0.75rem;
  border-radius: 16px;
  font-size: 0.8rem;
  font-weight: 500;
  border: 1px solid rgba(59, 130, 246, 0.2);
  transition: all 0.3s ease;
}

.rule-tags .tag:hover {
  background: rgba(59, 130, 246, 0.2);
  color: var(--text-primary);
  transform: scale(1.05);
}

.rule-card-footer {
  border-top: 1px solid rgba(255, 255, 255, 0.1);
  padding-top: 0.75rem;
}

.content-preview pre {
  background: var(--code-bg);
  color: var(--code-text);
  padding: 0.75rem;
  border-radius: 8px;
  font-size: 0.85rem;
  white-space: pre-wrap;
  word-wrap: break-word;
  overflow-x: auto;
  margin: 0;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .rule-card {
    padding: 0.75rem;
  }
  
  .rule-card-header {
    margin-bottom: 0.5rem;
  }
  
  .rule-title {
    font-size: 0.95rem;
  }
  
  .rule-description {
    font-size: 0.85rem;
  }
  
  .rule-badges {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.25rem;
  }
  
  .rule-tags {
    margin-top: 0.25rem;
  }
  
  .content-preview pre {
    font-size: 0.8rem;
    padding: 0.5rem;
  }
}