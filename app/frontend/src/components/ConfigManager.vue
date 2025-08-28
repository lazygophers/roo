<template>
  <div class="config-manager" v-if="show">
    <!-- 遮罩背景 -->
    <div class="modal-backdrop" @click="close"></div>
    
    <!-- 模态框内容 -->
    <div class="modal-content">
      <!-- 头部 -->
      <div class="modal-header">
        <h2>{{ title }}</h2>
        <button class="close-btn" @click="close">✕</button>
      </div>
      
      <!-- 保存配置表单 -->
      <div v-if="mode === 'save'" class="config-form">
        <div class="form-group">
          <label>配置名称 <span class="required">*</span></label>
          <input
            v-model="configName"
            type="text"
            placeholder="输入配置名称..."
            :class="{ error: errors.name }"
            @input="validateName"
          />
          <span v-if="errors.name" class="error-message">{{ errors.name }}</span>
        </div>
        
        <div class="form-group">
          <label>描述（可选）</label>
          <textarea
            v-model="configDescription"
            placeholder="添加配置描述..."
            rows="3"
          ></textarea>
        </div>
        
        <div class="form-actions">
          <button
            class="btn btn-primary"
            :disabled="!configName.trim() || isLoading"
            @click="handleSave"
          >
            {{ isLoading ? '保存中...' : '保存配置' }}
          </button>
          <button class="btn btn-secondary" @click="close">取消</button>
        </div>
      </div>
      
      <!-- 配置列表 -->
      <div v-else-if="mode === 'list'" class="config-list">
        <div v-if="isLoading" class="loading">
          <div class="loading-spinner"></div>
          <p>加载中...</p>
        </div>
        
        <div v-else-if="!hasConfigs" class="empty-state">
          <div class="empty-icon">📁</div>
          <p>暂无保存的配置</p>
          <button class="btn btn-primary" @click="switchMode('save')">
            创建新配置
          </button>
        </div>
        
        <div v-else class="configs-container">
          <!-- 工具栏 -->
          <div class="toolbar">
            <div class="toolbar-info">
              <span class="config-count">{{ savedConfigs.length }} 个配置</span>
              <span class="storage-size">占用空间: {{ formatSize(storageStats.totalSize) }}</span>
            </div>
            <div class="toolbar-actions">
              <button
                class="btn-icon"
                title="刷新"
                @click="refreshConfigs"
                :disabled="isLoading"
              >
                🔄
              </button>
              <button
                class="btn-icon"
                title="导入配置"
                @click="triggerImport"
              >
                📥
              </button>
              <button
                class="btn-icon"
                title="导出所有"
                @click="exportAll"
              >
                📤
              </button>
              <button
                class="btn-icon"
                title="恢复备份"
                @click="handleRestoreBackup"
                :disabled="isLoading"
              >
                💾
              </button>
              <button
                class="btn-icon btn-primary"
                title="创建新配置"
                @click="switchMode('save')"
              >
                ➕
              </button>
            </div>
          </div>
          
          <!-- 配置列表 -->
          <div class="configs-grid">
            <div
              v-for="config in sortedConfigs"
              :key="config.id"
              class="config-card"
            >
              <div class="config-card-header">
                <div class="config-info">
                  <h3>{{ config.name }}</h3>
                  <p v-if="config.description" class="description">{{ config.description }}</p>
                  <div class="meta">
                    <span class="date">创建于: {{ formatDate(config.createdAt) }}</span>
                    <span v-if="config.updatedAt !== config.createdAt" class="date">
                      更新于: {{ formatDate(config.updatedAt) }}
                    </span>
                  </div>
                </div>
              </div>
              
              <div class="config-card-content">
                <div class="config-preview">
                  <div class="preview-item">
                    <span class="label">Models:</span>
                    <span class="value">{{ config.config.models?.length || 0 }} 个</span>
                  </div>
                  <div class="preview-item">
                    <span class="label">Roles:</span>
                    <span class="value">{{ config.config.roles?.length || 0 }} 个</span>
                  </div>
                  <div class="preview-item">
                    <span class="label">Commands:</span>
                    <span class="value">{{ config.config.commands?.length || 0 }} 个</span>
                  </div>
                </div>
                
                <div class="config-actions">
                  <button
                    class="btn-sm btn-primary"
                    @click="applyConfig(config)"
                    title="应用此配置"
                  >
                    应用
                  </button>
                  <button
                    class="btn-sm btn-secondary"
                    @click="loadConfigDetails(config)"
                    title="查看详情"
                  >
                    详情
                  </button>
                  <button
                    class="btn-sm"
                    @click="exportSingleConfig(config.id)"
                    title="导出配置"
                  >
                    📤
                  </button>
                  <button
                    class="btn-sm"
                    @click="renameConfig(config)"
                    title="重命名"
                  >
                    ✏️
                  </button>
                  <button
                    class="btn-sm btn-danger"
                    @click="deleteConfig(config)"
                    title="删除配置"
                  >
                    🗑️
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 导入文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept=".json"
      style="display: none"
      @change="handleFileImport"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, watch } from 'vue'
import { useConfigStore } from '@/stores/config'
import type { SavedConfig, ConfigData } from '@/types'

interface Props {
  show: boolean
  initialMode?: 'save' | 'list'
  currentConfig?: ConfigData
}

const props = withDefaults(defineProps<Props>(), {
  show: false,
  initialMode: 'list',
  currentConfig: undefined
})

const emit = defineEmits<{
  'update:show': [value: boolean]
  'apply': [config: ConfigData]
  'close': []
}>()

const configStore = useConfigStore()

// 响应式数据
const mode = ref<'save' | 'list'>(props.initialMode)
const configName = ref('')
const configDescription = ref('')
const isLoading = ref(false)
const errors = ref<Record<string, string>>({})
const fileInput = ref<HTMLInputElement>()

// 计算属性
const savedConfigs = computed(() => configStore.savedConfigs)
const sortedConfigs = computed(() => configStore.sortedConfigs)
const hasConfigs = computed(() => configStore.hasConfigs)
const storageStats = computed(() => configStore.storageStats)

// 方法
const close = () => {
  emit('update:show', false)
  resetForm()
}

const switchMode = (newMode: 'save' | 'list') => {
  mode.value = newMode
  if (newMode === 'save') {
    nextTick(() => {
      const input = document.querySelector('input[type="text"]')
      input?.focus()
    })
  }
}

const validateName = () => {
  if (!configName.value.trim()) {
    errors.value.name = '配置名称不能为空'
    return false
  }
  
  // 检查是否重名
  const existing = savedConfigs.value.find(c => c.name === configName.value.trim())
  if (existing) {
    errors.value.name = '配置名称已存在'
    return false
  }
  
  delete errors.value.name
  return true
}

const handleSave = async () => {
  if (!validateName() || !props.currentConfig) return
  
  try {
    isLoading.value = true
    await configStore.saveConfig(
      configName.value.trim(),
      props.currentConfig,
      configDescription.value.trim() || undefined
    )
    
    // 保存成功后切换到列表模式
    mode.value = 'list'
    resetForm()
  } catch (error) {
    console.error('Save failed:', error)
  } finally {
    isLoading.value = false
  }
}

const applyConfig = (config: SavedConfig) => {
  emit('apply', config.config)
  close()
}

const loadConfigDetails = (config: SavedConfig) => {
  // 这里可以显示配置详情
  console.log('Load config details:', config)
}

const exportSingleConfig = async (id: string) => {
  try {
    await configStore.exportConfig(id)
  } catch (error) {
    console.error('Export failed:', error)
  }
}

const renameConfig = async (config: SavedConfig) => {
  const newName = prompt('请输入新的配置名称:', config.name)
  if (newName && newName.trim() && newName.trim() !== config.name) {
    try {
      await configStore.renameConfig(config.id, newName.trim())
    } catch (error) {
      console.error('Rename failed:', error)
    }
  }
}

const deleteConfig = async (config: SavedConfig) => {
  if (confirm(`确定要删除配置 "${config.name}" 吗？此操作不可恢复。`)) {
    try {
      await configStore.deleteConfig(config.id)
    } catch (error) {
      console.error('Delete failed:', error)
    }
  }
}

const refreshConfigs = async () => {
  try {
    isLoading.value = true
    await configStore.loadConfigs()
    await configStore.updateStorageStats()
  } catch (error) {
    console.error('Refresh failed:', error)
  } finally {
    isLoading.value = false
  }
}

const triggerImport = () => {
  fileInput.value?.click()
}

const handleFileImport = async (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (file) {
    try {
      isLoading.value = true
      await configStore.importConfig(file)
    } catch (error) {
      console.error('Import failed:', error)
    } finally {
      isLoading.value = false
      // 重置文件输入
      target.value = ''
    }
  }
}

const exportAll = () => {
  // 导出所有配置
  const blob = new Blob([JSON.stringify(savedConfigs.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `all-configs-${Date.now()}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

const handleRestoreBackup = async () => {
  if (confirm('确定要恢复到最近的备份吗？这将覆盖当前的配置。')) {
    try {
      const success = await configStore.restoreBackup()
      if (success) {
        alert('备份恢复成功！')
      } else {
        alert('没有找到可用的备份')
      }
    } catch (error) {
      console.error('Restore backup failed:', error)
      alert('恢复备份失败')
    }
  }
}

const resetForm = () => {
  configName.value = ''
  configDescription.value = ''
  errors.value = {}
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN')
}

const formatSize = (bytes: number) => {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// 标题
const title = computed(() => {
  return mode.value === 'save' ? '保存配置' : '我的配置'
})

// 监听
watch(() => props.show, (newVal) => {
  if (newVal) {
    // 重置状态
    mode.value = props.initialMode
    resetForm()
    configStore.clearError()
  }
})
</script>

<style scoped>
.config-manager {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.modal-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.7);
  backdrop-filter: blur(4px);
}

.modal-content {
  background: var(--glass-bg);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--glass-border);
  border-radius: 20px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  width: 90%;
  max-width: 800px;
  max-height: 90vh;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  position: relative;
}

.modal-header {
  padding: 2rem 2rem 1.5rem;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.modal-header h2 {
  margin: 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
}

.close-btn {
  background: none;
  border: none;
  font-size: 1.5rem;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0.5rem;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.close-btn:hover {
  background: rgba(255, 59, 48, 0.1);
  color: #ff3b30;
}

.config-form {
  padding: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  color: var(--text-primary);
  font-weight: 500;
}

.required {
  color: var(--accent-pink);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.875rem 1.25rem;
  border: 2px solid rgba(120, 255, 214, 0.3);
  border-radius: 12px;
  background: linear-gradient(135deg, rgba(15, 23, 42, 0.9) 0%, rgba(30, 41, 59, 0.8) 100%);
  color: #e2e8f0;
  font-size: 1rem;
  transition: all 0.3s ease;
  backdrop-filter: blur(10px);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #78ff9c;
  box-shadow: 0 0 30px rgba(120, 255, 214, 0.4), inset 0 0 0 3px rgba(120, 255, 214, 0.1);
  transform: translateY(-1px);
}

.form-group input::placeholder,
.form-group textarea::placeholder {
  color: #64748b;
  font-style: italic;
}

.form-group input.error {
  border-color: var(--accent-pink);
}

.error-message {
  color: var(--accent-pink);
  font-size: 0.875rem;
  margin-top: 0.25rem;
  display: block;
}

.form-actions {
  display: flex;
  gap: 1rem;
  margin-top: 2rem;
}

.btn {
  padding: 0.875rem 2.25rem;
  border: none;
  border-radius: 12px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5);
  position: relative;
  overflow: hidden;
}

.btn-primary::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.6s, height 0.6s;
}

.btn-primary:hover:not(:disabled)::after {
  width: 300px;
  height: 300px;
}

.btn-primary:hover:not(:disabled) {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  transform: translateY(-3px);
  box-shadow: 0 8px 25px rgba(102, 126, 234, 0.7);
}

.btn-secondary {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.15) 0%, rgba(139, 92, 246, 0.1) 100%);
  color: #e0e7ff;
  border: 2px solid rgba(99, 102, 241, 0.4);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

.btn-secondary:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.25) 0%, rgba(139, 92, 246, 0.2) 100%);
  border-color: rgba(99, 102, 241, 0.6);
  transform: translateY(-3px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none;
}

.btn:disabled::before,
.btn:disabled::after {
  display: none;
}

.config-list {
  padding: 0;
  display: flex;
  flex-direction: column;
  height: 100%;
}

.loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--accent-cyan);
  border-top-color: transparent;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 3rem;
  color: var(--text-secondary);
  text-align: center;
}

.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
  opacity: 0.5;
}

.toolbar {
  padding: 1.5rem;
  border-bottom: 1px solid var(--glass-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 1rem;
}

.toolbar-info {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.config-count {
  font-weight: 600;
  color: var(--text-primary);
}

.storage-size {
  font-size: 0.875rem;
  color: var(--text-secondary);
}

.toolbar-actions {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-icon {
  background: linear-gradient(135deg, rgba(120, 255, 214, 0.1) 0%, rgba(120, 255, 214, 0.05) 100%);
  border: 2px solid rgba(120, 255, 214, 0.4);
  border-radius: 12px;
  padding: 0.625rem;
  font-size: 1.25rem;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.3s ease;
  width: 44px;
  height: 44px;
  display: flex;
  align-items: center;
  justify-content: center;
  backdrop-filter: blur(10px);
  position: relative;
  overflow: hidden;
}

.btn-icon::before {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: rgba(120, 255, 214, 0.3);
  transform: translate(-50%, -50%);
  transition: width 0.4s, height 0.4s;
}

.btn-icon:hover {
  border-color: var(--accent-cyan);
  color: var(--accent-cyan);
  background: linear-gradient(135deg, rgba(120, 255, 214, 0.2) 0%, rgba(120, 255, 214, 0.15) 100%);
  transform: translateY(-3px) scale(1.1);
  box-shadow: 0 8px 20px rgba(120, 255, 214, 0.4);
}

.btn-icon:hover::before {
  width: 100px;
  height: 100px;
}

.btn-icon.btn-primary {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border: none;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
}

.btn-icon.btn-primary:hover {
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
}

.btn-icon:disabled {
  opacity: 0.4;
  cursor: not-allowed;
  transform: scale(0.95);
}

.btn-icon:disabled::before {
  display: none;
}

.configs-container {
  flex: 1;
  overflow-y: auto;
  padding: 1.5rem;
}

.configs-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.config-card {
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.05) 0%, rgba(139, 92, 246, 0.05) 100%);
  border: 1px solid rgba(99, 102, 241, 0.2);
  border-radius: 12px;
  overflow: hidden;
  transition: all 0.3s ease;
}

.config-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 12px 24px rgba(99, 102, 241, 0.2);
  border-color: rgba(99, 102, 241, 0.4);
}

.config-card-header {
  padding: 1.5rem;
  background: rgba(255, 255, 255, 0.03);
  border-bottom: 1px solid rgba(99, 102, 241, 0.1);
}

.config-info h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 600;
}

.config-info .description {
  color: var(--text-secondary);
  font-size: 0.875rem;
  margin: 0 0 0.5rem 0;
  line-height: 1.4;
}

.meta {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.meta .date {
  font-size: 0.75rem;
  color: #94a3b8;
}

.config-card-content {
  padding: 1.5rem;
}

.config-preview {
  margin-bottom: 1rem;
}

.preview-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 0;
  background: rgba(15, 23, 42, 0.6);
  border-radius: 8px;
  margin-bottom: 0.5rem;
}

.preview-item:last-child {
  margin-bottom: 0;
}

.preview-item .label {
  color: #94a3b8;
  font-size: 0.875rem;
}

.preview-item .value {
  color: var(--text-primary);
  font-weight: 500;
}

.config-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.btn-sm {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 8px;
  font-size: 0.875rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  backdrop-filter: blur(10px);
}

/* Shine effect for small buttons */
.btn-sm::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.3), transparent);
  transition: left 0.6s ease;
}

.btn-sm:hover::before {
  left: 100%;
}

/* Primary small button */
.btn-sm.btn-primary {
  background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
  color: white;
  box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
}

.btn-sm.btn-primary:hover {
  background: linear-gradient(135deg, #2563eb 0%, #7c3aed 100%);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
}

/* Secondary small button */
.btn-sm.btn-secondary {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.1) 0%, rgba(139, 92, 246, 0.05) 100%);
  color: #a5b4fc;
  border: 1px solid rgba(99, 102, 241, 0.3);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.btn-sm.btn-secondary:hover {
  background: linear-gradient(135deg, rgba(99, 102, 241, 0.2) 0%, rgba(139, 92, 246, 0.15) 100%);
  color: #e2e8f0;
  border-color: rgba(99, 102, 241, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(99, 102, 241, 0.3);
}

/* Danger small button */
.btn-sm.btn-danger {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(248, 113, 113, 0.05) 100%);
  color: #f87171;
  border: 1px solid rgba(239, 68, 68, 0.3);
  box-shadow: 0 4px 12px rgba(239, 68, 68, 0.2);
}

.btn-sm.btn-danger:hover {
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.2) 0%, rgba(248, 113, 113, 0.15) 100%);
  color: #fee2e2;
  border-color: rgba(239, 68, 68, 0.5);
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(239, 68, 68, 0.4);
}

/* Default small button (icon buttons) */
.btn-sm:not(.btn-primary):not(.btn-secondary):not(.btn-danger) {
  background: linear-gradient(135deg, rgba(120, 255, 214, 0.1) 0%, rgba(120, 255, 214, 0.05) 100%);
  color: #78ff9c;
  border: 1px solid rgba(120, 255, 214, 0.3);
  box-shadow: 0 4px 12px rgba(120, 255, 214, 0.2);
}

.btn-sm:not(.btn-primary):not(.btn-secondary):not(.btn-danger):hover {
  background: linear-gradient(135deg, rgba(120, 255, 214, 0.2) 0%, rgba(120, 255, 214, 0.15) 100%);
  color: #78ff9c;
  border-color: rgba(120, 255, 214, 0.5);
  transform: translateY(-2px) scale(1.05);
  box-shadow: 0 6px 20px rgba(120, 255, 214, 0.4);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    margin: 1rem;
  }
  
  .configs-grid {
    grid-template-columns: 1fr;
  }
  
  .toolbar {
    flex-direction: column;
    align-items: stretch;
  }
  
  .toolbar-info {
    align-items: center;
    text-align: center;
  }
  
  .config-actions {
    justify-content: center;
  }
}

@media (max-width: 480px) {
  .modal-header {
    padding: 1.5rem 1.5rem 1rem;
  }
  
  .modal-header h2 {
    font-size: 1.25rem;
  }
  
  .config-form {
    padding: 1.5rem;
  }
  
  .btn {
    padding: 0.625rem 1.5rem;
    font-size: 0.875rem;
  }
  
  .config-card {
    margin-bottom: 1rem;
  }
  
  .config-actions {
    justify-content: center;
  }
  
  .btn-sm {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
  }
}
</style>