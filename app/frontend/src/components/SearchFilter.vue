<template>
  <div class="search-filter">
    <div class="search-container">
      <div class="search-input-wrapper">
        <div class="search-icon">🔍</div>
        <input
          ref="searchInput"
          v-model="searchQuery"
          type="text"
          :placeholder="placeholder"
          @input="handleSearchInput"
          @focus="handleFocus"
          @blur="handleBlur"
          @keydown.down.prevent="highlightNext"
          @keydown.up.prevent="highlightPrevious"
          @keydown.enter.prevent="selectHighlighted"
          @keydown.esc.prevent="clearSearch"
        />
        <button
          v-if="searchQuery"
          class="clear-btn"
          @click="clearSearch"
          title="清除搜索"
        >
          ✕
        </button>
        <button
          class="filter-toggle"
          @click="toggleFilterPanel"
          :class="{ active: showFilterPanel }"
          title="筛选选项"
        >
          ⚙️
        </button>
      </div>
      
      <!-- 搜索历史下拉 -->
      <div
        v-if="showHistory && searchHistory.length > 0 && !searchQuery"
        class="search-history"
      >
        <div class="history-header">
          <span>搜索历史</span>
          <button class="clear-history" @click="clearHistory" title="清除历史">
            清除
          </button>
        </div>
        <div
          v-for="(item, index) in searchHistory"
          :key="index"
          class="history-item"
          :class="{ highlighted: highlightedIndex === index }"
          @click="selectFromHistory(item)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="history-icon">🕐</span>
          <span class="history-text">{{ item }}</span>
          <button class="remove-history" @click.stop="removeFromHistory(index)" title="移除">
            ✕
          </button>
        </div>
      </div>
      
      <!-- 搜索建议下拉 -->
      <div
        v-if="showSuggestions && searchSuggestions.length > 0"
        class="search-suggestions"
      >
        <div
          v-for="(suggestion, index) in searchSuggestions"
          :key="index"
          class="suggestion-item"
          :class="{ highlighted: highlightedIndex === index }"
          @click="applySuggestion(suggestion)"
          @mouseenter="highlightedIndex = index"
        >
          <span class="suggestion-icon">💡</span>
          <span class="suggestion-text">{{ suggestion }}</span>
        </div>
      </div>
      
      <!-- 筛选面板 -->
      <transition name="slide-down">
        <div v-if="showFilterPanel" class="filter-panel">
          <div class="filter-section">
            <h3>搜索范围</h3>
            <div class="filter-options">
              <label v-for="scope in searchScopes" :key="scope.value" class="filter-option">
                <input
                  type="checkbox"
                  :value="scope.value"
                  v-model="selectedScopes"
                  @change="handleFilterChange"
                />
                <span>{{ scope.label }}</span>
              </label>
            </div>
          </div>
          
          <div class="filter-section">
            <h3>搜索选项</h3>
            <div class="filter-options">
              <label class="filter-option">
                <input
                  type="checkbox"
                  v-model="searchOptions.caseSensitive"
                  @change="handleFilterChange"
                />
                <span>区分大小写</span>
              </label>
              <label class="filter-option">
                <input
                  type="checkbox"
                  v-model="searchOptions.wholeWord"
                  @change="handleFilterChange"
                />
                <span>全词匹配</span>
              </label>
              <label class="filter-option">
                <input
                  type="checkbox"
                  v-model="searchOptions.highlightMatches"
                  @change="handleFilterChange"
                />
                <span>高亮匹配</span>
              </label>
            </div>
          </div>
          
          <div class="filter-section">
            <h3>排序方式</h3>
            <select v-model="sortOption" @change="handleFilterChange" class="sort-select">
              <option value="relevance">相关度</option>
              <option value="name">名称</option>
              <option value="category">类别</option>
              <option value="modified">修改时间</option>
            </select>
          </div>
        </div>
      </transition>
    </div>
    
    <!-- 快速筛选标签 -->
    <div v-if="quickFilters.length > 0" class="quick-filters">
      <span class="quick-filter-label">快速筛选:</span>
      <button
        v-for="filter in quickFilters"
        :key="filter.value"
        class="quick-filter-tag"
        :class="{ active: activeQuickFilters.includes(filter.value) }"
        @click="toggleQuickFilter(filter.value)"
      >
        {{ filter.label }}
      </button>
    </div>
    
    <!-- 搜索统计 -->
    <div v-if="showStats && searchQuery" class="search-stats">
      <span class="stats-text">
        找到 <strong>{{ totalResults }}</strong> 个结果
        <span v-if="searchTime" class="search-time">
          ({{ searchTime }}ms)
        </span>
      </span>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { debounce } from 'lodash-es'

interface Props {
  modelValue?: string
  placeholder?: string
  searchScopes?: Array<{ value: string; label: string }>
  quickFilters?: Array<{ value: string; label: string }>
  maxHistory?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', query: string, options: SearchOptions): void
  (e: 'clear'): void
}

interface SearchOptions {
  scopes: string[]
  caseSensitive: boolean
  wholeWord: boolean
  highlightMatches: boolean
  sortBy: string
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '搜索...',
  searchScopes: () => [
    { value: 'models', label: 'Models' },
    { value: 'rules', label: 'Rules' },
    { value: 'roles', label: 'Roles' },
    { value: 'commands', label: 'Commands' }
  ],
  quickFilters: () => [],
  maxHistory: 10
})

const emit = defineEmits<Emits>()

// 响应式数据
const searchQuery = ref(props.modelValue || '')
const searchInput = ref<HTMLInputElement | null>(null)
const showHistory = ref(false)
const showSuggestions = ref(false)
const showFilterPanel = ref(false)
const showStats = ref(false)
const highlightedIndex = ref(-1)
const isFocused = ref(false)

// 搜索历史
const searchHistory = ref<string[]>([])
const HISTORY_KEY = 'config-search-history'

// 搜索建议
const searchSuggestions = ref<string[]>([])

// 筛选选项
const selectedScopes = ref<string[]>(props.searchScopes.map(s => s.value))
const activeQuickFilters = ref<string[]>([])
const sortOption = ref('relevance')

const searchOptions = ref({
  caseSensitive: false,
  wholeWord: false,
  highlightMatches: true
})

// 计算属性
const totalResults = ref(0)
const searchTime = ref(0)

// 防抖搜索
const debouncedSearch = debounce((query: string) => {
  if (query.trim()) {
    const startTime = performance.now()
    
    emit('search', query, {
      scopes: selectedScopes.value,
      caseSensitive: searchOptions.value.caseSensitive,
      wholeWord: searchOptions.value.wholeWord,
      highlightMatches: searchOptions.value.highlightMatches,
      sortBy: sortOption.value
    })
    
    // 模拟搜索时间（实际应用中应该从后端获取）
    searchTime.value = Math.round(performance.now() - startTime)
    showStats.value = true
  }
}, 300)

// 方法
const handleSearchInput = () => {
  emit('update:modelValue', searchQuery.value)
  
  if (searchQuery.value) {
    showHistory.value = false
    debouncedSearch(searchQuery.value)
    
    // 生成搜索建议
    generateSuggestions()
  } else {
    showSuggestions.value = false
    emit('clear')
  }
}

const generateSuggestions = () => {
  // 这里可以根据实际需求生成更智能的建议
  const suggestions: string[] = []
  
  if (searchQuery.value.length > 2) {
    // 基于历史记录生成建议
    const relevantHistory = searchHistory.value.filter(item => 
      item.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    suggestions.push(...relevantHistory.slice(0, 2))
    
    // 基于常见搜索词生成建议
    const commonTerms = ['code', 'debug', 'architect', 'brain', 'hook', 'before', 'after']
    const matchingTerms = commonTerms.filter(term => 
      term.toLowerCase().includes(searchQuery.value.toLowerCase())
    )
    suggestions.push(...matchingTerms.slice(0, 3 - suggestions.length))
  }
  
  searchSuggestions.value = [...new Set(suggestions)].slice(0, 5)
  showSuggestions.value = suggestions.length > 0
}

const clearSearch = () => {
  searchQuery.value = ''
  emit('update:modelValue', '')
  emit('clear')
  showHistory.value = false
  showSuggestions.value = false
  showStats.value = false
  highlightedIndex.value = -1
  if (searchInput.value) {
    searchInput.value.focus()
  }
}

const toggleFilterPanel = () => {
  showFilterPanel.value = !showFilterPanel.value
}

const handleFocus = () => {
  isFocused.value = true
  if (!searchQuery.value) {
    showHistory.value = true
    highlightedIndex.value = -1
  }
}

const handleBlur = () => {
  isFocused.value = false
  setTimeout(() => {
    if (!isFocused.value) {
      showHistory.value = false
      showSuggestions.value = false
    }
  }, 200)
}

const handleFilterChange = () => {
  if (searchQuery.value) {
    debouncedSearch(searchQuery.value)
  }
}

const toggleQuickFilter = (value: string) => {
  const index = activeQuickFilters.value.indexOf(value)
  if (index > -1) {
    activeQuickFilters.value.splice(index, 1)
  } else {
    activeQuickFilters.value.push(value)
  }
  
  // 如果有搜索词，重新搜索
  if (searchQuery.value) {
    debouncedSearch(searchQuery.value)
  }
}

const selectFromHistory = (item: string) => {
  searchQuery.value = item
  emit('update:modelValue', item)
  showHistory.value = false
  debouncedSearch(item)
  addToHistory(item)
}

const applySuggestion = (suggestion: string) => {
  searchQuery.value = suggestion
  emit('update:modelValue', suggestion)
  showSuggestions.value = false
  debouncedSearch(suggestion)
  addToHistory(suggestion)
}

const addToHistory = (query: string) => {
  const trimmedQuery = query.trim()
  if (!trimmedQuery) return
  
  // 移除重复项
  const index = searchHistory.value.indexOf(trimmedQuery)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
  }
  
  // 添加到开头
  searchHistory.value.unshift(trimmedQuery)
  
  // 限制历史记录数量
  if (searchHistory.value.length > props.maxHistory) {
    searchHistory.value = searchHistory.value.slice(0, props.maxHistory)
  }
  
  // 保存到 localStorage
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

const removeFromHistory = (index: number) => {
  searchHistory.value.splice(index, 1)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
  
  if (searchHistory.value.length === 0) {
    showHistory.value = false
  }
}

const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
  showHistory.value = false
}

const highlightNext = () => {
  const items = showHistory.value ? searchHistory.value : searchSuggestions.value
  if (items.length > 0) {
    highlightedIndex.value = (highlightedIndex.value + 1) % items.length
  }
}

const highlightPrevious = () => {
  const items = showHistory.value ? searchHistory.value : searchSuggestions.value
  if (items.length > 0) {
    highlightedIndex.value = highlightedIndex.value <= 0 
      ? items.length - 1 
      : highlightedIndex.value - 1
  }
}

const selectHighlighted = () => {
  const items = showHistory.value ? searchHistory.value : searchSuggestions.value
  if (highlightedIndex.value >= 0 && highlightedIndex.value < items.length) {
    if (showHistory.value) {
      selectFromHistory(items[highlightedIndex.value])
    } else {
      applySuggestion(items[highlightedIndex.value])
    }
  }
}

// 监听搜索历史变化
watch(searchHistory, (newHistory) => {
  localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory))
})

// 监听外部 modelValue 变化
watch(() => props.modelValue, (newValue) => {
  if (newValue !== searchQuery.value) {
    searchQuery.value = newValue || ''
  }
})

// 暴露方法供父组件调用
const setSearchResults = (results: number) => {
  totalResults.value = results
}

const resetFilters = () => {
  selectedScopes.value = props.searchScopes.map(s => s.value)
  activeQuickFilters.value = []
  searchOptions.value = {
    caseSensitive: false,
    wholeWord: false,
    highlightMatches: true
  }
  sortOption.value = 'relevance'
}

defineExpose({
  setSearchResults,
  resetFilters
})

// 生命周期
onMounted(() => {
  // 加载搜索历史
  try {
    const saved = localStorage.getItem(HISTORY_KEY)
    if (saved) {
      searchHistory.value = JSON.parse(saved)
    }
  } catch (error) {
    console.error('Failed to load search history:', error)
  }
  
  // 添加键盘快捷键
  document.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})

const handleKeyDown = (e: KeyboardEvent) => {
  // Cmd/Ctrl + K 聚焦搜索框
  if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
    e.preventDefault()
    searchInput.value?.focus()
  }
  
  // Esc 关闭面板
  if (e.key === 'Escape') {
    if (showFilterPanel.value) {
      showFilterPanel.value = false
    } else if (showHistory.value || showSuggestions.value) {
      showHistory.value = false
      showSuggestions.value = false
    } else {
      clearSearch()
    }
  }
}
</script>

<style scoped>
.search-filter {
  width: 100%;
  margin-bottom: 1rem;
}

.search-container {
  position: relative;
}

.search-input-wrapper {
  position: relative;
  display: flex;
  align-items: center;
  background: rgba(15, 23, 42, 0.8);
  border: 2px solid rgba(0, 245, 255, 0.3);
  border-radius: 30px;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
}

.search-input-wrapper:focus-within {
  border-color: #00f5ff;
  box-shadow: 0 0 20px rgba(0, 245, 255, 0.3);
}

.search-icon {
  position: absolute;
  left: 1rem;
  color: #94a3b8;
  font-size: 1.2rem;
  z-index: 1;
}

.search-input-wrapper input {
  width: 100%;
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: none;
  background: transparent;
  color: #f1f5f9;
  font-size: 1rem;
  outline: none;
}

.search-input-wrapper input::placeholder {
  color: #94a3b8;
}

.clear-btn,
.filter-toggle {
  position: absolute;
  right: 0.5rem;
  background: none;
  border: none;
  color: #94a3b8;
  cursor: pointer;
  font-size: 1rem;
  width: 2.5rem;
  height: 2.5rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  z-index: 1;
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.clear-btn:hover,
.filter-toggle:hover {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  transform: scale(1.1);
}

.filter-toggle:hover {
  background: rgba(0, 245, 255, 0.1);
  color: #67e8f9;
}

.filter-toggle.active {
  background: rgba(0, 245, 255, 0.2);
  color: #67e8f9;
  box-shadow: 0 0 15px rgba(0, 245, 255, 0.3);
}

.search-history,
.search-suggestions {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 12px;
  margin-top: 0.5rem;
  max-height: 300px;
  overflow-y: auto;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.75rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
  font-size: 0.85rem;
  color: #cbd5e1;
  font-weight: 500;
}

.clear-history {
  background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
  border: none;
  color: white;
  cursor: pointer;
  font-size: 0.75rem;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(239, 68, 68, 0.3);
  position: relative;
  overflow: hidden;
}

.clear-history::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.5s ease;
}

.clear-history:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.4);
}

.clear-history:hover::before {
  left: 100%;
}

.clear-history:active {
  transform: translateY(0);
  box-shadow: 0 2px 6px rgba(239, 68, 68, 0.3);
}

.history-item,
.suggestion-item {
  display: flex;
  align-items: center;
  padding: 1rem;
  cursor: pointer;
  transition: background 0.2s ease;
  gap: 0.75rem;
  min-height: 44px;
}

.history-item:hover,
.suggestion-item:hover {
  background: rgba(59, 130, 246, 0.1);
}

.history-item.highlighted,
.suggestion-item.highlighted {
  background: rgba(59, 130, 246, 0.2);
  color: #e0e7ff;
}

.history-icon,
.suggestion-icon {
  font-size: 1rem;
  opacity: 0.7;
}

.history-text,
.suggestion-text {
  flex: 1;
  color: #f1f5f9;
  font-size: 0.9rem;
}

.remove-history {
  background: rgba(15, 23, 42, 0.8);
  border: 1px solid rgba(239, 68, 68, 0.3);
  color: #94a3b8;
  cursor: pointer;
  font-size: 0.7rem;
  width: 2rem;
  height: 2rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.history-item:hover .remove-history {
  opacity: 1;
  transform: scale(1.05);
}

.remove-history:hover {
  background: rgba(239, 68, 68, 0.2);
  border-color: #fca5a5;
  color: #fca5a5;
  box-shadow: 0 0 10px rgba(239, 68, 68, 0.3);
}

.filter-panel {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  background: rgba(15, 23, 42, 0.95);
  border: 1px solid rgba(0, 245, 255, 0.3);
  border-radius: 12px;
  margin-top: 0.5rem;
  padding: 1.5rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
  z-index: 1000;
}

.filter-section {
  margin-bottom: 1.5rem;
}

.filter-section:last-child {
  margin-bottom: 0;
}

.filter-section h3 {
  color: #f1f5f9;
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.75rem;
}

.filter-options {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.filter-option {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  color: #e2e8f0;
  font-size: 0.9rem;
  cursor: pointer;
  padding: 0.5rem;
  border-radius: 8px;
  transition: background 0.2s ease;
}

.filter-option:hover {
  background: rgba(59, 130, 246, 0.1);
}

.filter-option input[type="checkbox"] {
  width: 20px;
  height: 20px;
  cursor: pointer;
  appearance: none;
  -webkit-appearance: none;
  position: relative;
  border: 2px solid rgba(148, 163, 184, 0.3);
  border-radius: 4px;
  background: rgba(30, 41, 59, 0.8);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
  flex-shrink: 0;
}

.filter-option input[type="checkbox"]:hover {
  border-color: #67e8f9;
  box-shadow: 0 0 8px rgba(0, 245, 255, 0.2);
  transform: scale(1.05);
}

.filter-option input[type="checkbox"]:checked {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-color: transparent;
  box-shadow: 0 0 12px rgba(59, 130, 246, 0.4);
}

.filter-option input[type="checkbox"]:checked::after {
  content: '✓';
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  color: white;
  font-size: 14px;
  font-weight: bold;
}

.filter-option input[type="checkbox"]:focus {
  outline: none;
  border-color: #67e8f9;
  box-shadow: 0 0 0 2px rgba(0, 245, 255, 0.3);
}

.sort-select {
  width: 100%;
  padding: 0.875rem 1rem;
  background: rgba(30, 41, 59, 0.8);
  border: 2px solid rgba(0, 245, 255, 0.3);
  border-radius: 12px;
  color: #f1f5f9;
  font-size: 0.9rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  appearance: none;
  -webkit-appearance: none;
  background-image: url("data:image/svg+xml;charset=UTF-8,%3csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%2367e8f9' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3e%3cpolyline points='6 9 12 15 18 9'%3e%3c/polyline%3e%3c/svg%3e");
  background-repeat: no-repeat;
  background-position: right 1rem center;
  background-size: 1rem;
  padding-right: 2.5rem;
}

.sort-select:focus {
  outline: none;
  border-color: #67e8f9;
  box-shadow: 0 0 0 2px rgba(0, 245, 255, 0.3);
}

.quick-filters {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.75rem;
  flex-wrap: wrap;
}

.quick-filter-label {
  color: #cbd5e1;
  font-size: 0.85rem;
}

.quick-filter-tag {
  padding: 0.5rem 1rem;
  background: rgba(30, 41, 59, 0.6);
  border: 1px solid rgba(148, 163, 184, 0.2);
  border-radius: 20px;
  color: #cbd5e1;
  font-size: 0.8rem;
  cursor: pointer;
  transition: all 0.2s ease;
  min-height: 36px;
  display: inline-flex;
  align-items: center;
}

.quick-filter-tag:hover {
  background: rgba(30, 41, 59, 0.8);
  color: #e2e8f0;
}

.quick-filter-tag.active {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  border-color: transparent;
  color: white;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.4);
}

.search-stats {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem;
  background: rgba(59, 130, 246, 0.1);
  border-radius: 8px;
  font-size: 0.85rem;
}

.stats-text {
  color: #c7d2fe;
}

.search-time {
  color: #94a3b8;
  font-size: 0.75rem;
}

/* 动画效果 */
.slide-down-enter-active,
.slide-down-leave-active {
  transition: all 0.3s ease;
}

.slide-down-enter-from {
  opacity: 0;
  transform: translateY(-10px);
}

.slide-down-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 滚动条样式 */
.search-history::-webkit-scrollbar,
.search-suggestions::-webkit-scrollbar {
  width: 8px;
}

.search-history::-webkit-scrollbar-track,
.search-suggestions::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);
  border-radius: 4px;
}

.search-history::-webkit-scrollbar-thumb,
.search-suggestions::-webkit-scrollbar-thumb {
  background: rgba(120, 255, 214, 0.3);
  border-radius: 4px;
}

.search-history::-webkit-scrollbar-thumb:hover,
.search-suggestions::-webkit-scrollbar-thumb:hover {
  background: rgba(120, 255, 214, 0.5);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-input-wrapper {
    border-radius: 20px;
  }
  
  .search-icon {
    left: 0.75rem;
    font-size: 1.1rem;
  }
  
  .search-input-wrapper input {
    padding: 1rem 1rem 1rem 2.75rem;
    font-size: 1rem;
  }
  
  .clear-btn,
  .filter-toggle {
    width: 3rem;
    height: 3rem;
    right: 0.25rem;
    font-size: 1.1rem;
  }
  
  .filter-toggle {
    right: 3.5rem;
  }
  
  .search-history,
  .search-suggestions {
    max-height: 250px;
    border-radius: 8px;
    margin-top: 0.25rem;
  }
  
  .history-item,
  .suggestion-item {
    padding: 0.875rem;
    min-height: 44px;
  }
  
  .history-header {
    padding: 0.625rem 0.875rem;
    font-size: 0.8rem;
  }
  
  .clear-history {
    padding: 0.375rem 0.75rem;
    font-size: 0.7rem;
  }
  
  .filter-panel {
    padding: 1rem;
    border-radius: 8px;
    margin-top: 0.25rem;
  }
  
  .filter-section {
    margin-bottom: 1rem;
  }
  
  .filter-section h3 {
    font-size: 0.9rem;
    margin-bottom: 0.5rem;
  }
  
  .filter-option {
    padding: 0.625rem;
    font-size: 0.85rem;
  }
  
  .filter-option input[type="checkbox"] {
    width: 22px;
    height: 22px;
  }
  
  .sort-select {
    padding: 0.75rem 0.875rem;
    font-size: 0.85rem;
    background-size: 0.875rem;
    padding-right: 2.25rem;
  }
  
  .quick-filters {
    gap: 0.375rem;
    margin-bottom: 0.625rem;
  }
  
  .quick-filter-label {
    font-size: 0.8rem;
  }
  
  .quick-filter-tag {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
    min-height: 32px;
  }
  
  .search-stats {
    padding: 0.5rem;
    font-size: 0.8rem;
  }
}

@media (max-width: 480px) {
  .search-filter {
    margin-bottom: 0.75rem;
  }
  
  .search-input-wrapper {
    border-radius: 16px;
  }
  
  .search-icon {
    left: 0.625rem;
  }
  
  .search-input-wrapper input {
    padding: 0.875rem 0.875rem 0.875rem 2.5rem;
    font-size: 0.9rem;
  }
  
  .clear-btn,
  .filter-toggle {
    width: 2.75rem;
    height: 2.75rem;
    font-size: 1rem;
  }
  
  .filter-toggle {
    right: 3.25rem;
  }
  
  .search-history,
  .search-suggestions {
    max-height: 200px;
  }
  
  .history-item,
  .suggestion-item {
    padding: 0.75rem;
    gap: 0.5rem;
  }
  
  .history-text,
  .suggestion-text {
    font-size: 0.85rem;
  }
  
  .remove-history {
    width: 1.75rem;
    height: 1.75rem;
  }
  
  .filter-panel {
    padding: 0.75rem;
  }
  
  .filter-section h3 {
    font-size: 0.85rem;
  }
  
  .filter-option {
    font-size: 0.8rem;
    gap: 0.5rem;
  }
  
  .quick-filter-tag {
    padding: 0.25rem 0.625rem;
    font-size: 0.7rem;
    min-height: 28px;
  }
}
</style>