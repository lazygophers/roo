import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { configStorage } from '@/utils/configStorage'
import type { ConfigData, SavedConfig } from '@/types'

export const useConfigStore = defineStore('config', () => {
  // 状态
  const savedConfigs = ref<SavedConfig[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const storageStats = ref<{
    totalConfigs: number
    totalSize: number
    lastBackup?: Date
  }>({
    totalConfigs: 0,
    totalSize: 0
  })

  // 计算属性
  const hasConfigs = computed(() => savedConfigs.value.length > 0)
  const sortedConfigs = computed(() => {
    return [...savedConfigs.value].sort((a, b) => 
      new Date(b.updatedAt).getTime() - new Date(a.updatedAt).getTime()
    )
  })

  // 初始化
  const initialize = async () => {
    try {
      isLoading.value = true
      await configStorage.initialize()
      await loadConfigs()
      await updateStorageStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '初始化失败'
    } finally {
      isLoading.value = false
    }
  }

  // 加载所有配置
  const loadConfigs = async () => {
    try {
      isLoading.value = true
      error.value = null
      savedConfigs.value = await configStorage.getAllConfigs()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 保存配置
  const saveConfig = async (name: string, config: ConfigData, description?: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await configStorage.saveConfig(name, config, description)
      await loadConfigs()
      await updateStorageStats()
      
      return true
    } catch (err) {
      error.value = err instanceof Error ? err.message : '保存配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 加载配置
  const loadConfig = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      const config = await configStorage.loadConfig(id)
      return config
    } catch (err) {
      error.value = err instanceof Error ? err.message : '加载配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 删除配置
  const deleteConfig = async (id: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await configStorage.deleteConfig(id)
      await loadConfigs()
      await updateStorageStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '删除配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 重命名配置
  const renameConfig = async (id: string, newName: string) => {
    try {
      isLoading.value = true
      error.value = null
      
      await configStorage.renameConfig(id, newName)
      await loadConfigs()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '重命名配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 导出配置
  const exportConfig = async (id: string) => {
    try {
      await configStorage.exportConfig(id)
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导出配置失败'
      throw err
    }
  }

  // 导入配置
  const importConfig = async (file: File) => {
    try {
      isLoading.value = true
      error.value = null
      
      await configStorage.importConfig(file)
      await loadConfigs()
      await updateStorageStats()
    } catch (err) {
      error.value = err instanceof Error ? err.message : '导入配置失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 恢复备份
  const restoreBackup = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      const success = await configStorage.restoreBackup()
      if (success) {
        await loadConfigs()
        await updateStorageStats()
      }
      return success
    } catch (err) {
      error.value = err instanceof Error ? err.message : '恢复备份失败'
      throw err
    } finally {
      isLoading.value = false
    }
  }

  // 更新存储统计
  const updateStorageStats = async () => {
    try {
      storageStats.value = await configStorage.getStorageStats()
    } catch (err) {
      console.error('Failed to update storage stats:', err)
    }
  }

  // 清除错误
  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    savedConfigs,
    isLoading,
    error,
    storageStats,
    
    // 计算属性
    hasConfigs,
    sortedConfigs,
    
    // 方法
    initialize,
    loadConfigs,
    saveConfig,
    loadConfig,
    deleteConfig,
    renameConfig,
    exportConfig,
    importConfig,
    restoreBackup,
    updateStorageStats,
    clearError
  }
})