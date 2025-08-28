/**
 * 配置存储工具类
 * 负责配置的本地存储、版本管理、压缩和备份
 */
import { ConfigData, SavedConfig } from '@/types'

export class ConfigStorage {
  private readonly STORAGE_KEY = 'roo-configs'
  private readonly VERSION_KEY = 'roo-configs-version'
  private readonly BACKUP_KEY = 'roo-configs-backup'
  private readonly CURRENT_VERSION = '1.0.0'

  /**
   * 初始化存储
   */
  async initialize(): Promise<void> {
    // 检查版本，必要时进行迁移
    const storedVersion = localStorage.getItem(this.VERSION_KEY)
    
    if (!storedVersion) {
      // 首次使用，创建备份
      await this.createBackup()
    } else if (storedVersion !== this.CURRENT_VERSION) {
      // 版本升级，执行迁移
      await this.migrateData(storedVersion, this.CURRENT_VERSION)
    }
    
    // 设置当前版本
    localStorage.setItem(this.VERSION_KEY, this.CURRENT_VERSION)
  }

  /**
   * 保存配置
   */
  async saveConfig(name: string, config: ConfigData, description?: string): Promise<void> {
    try {
      // 获取现有配置列表
      const configs = await this.getAllConfigs()
      
      // 创建新配置
      const newConfig: SavedConfig = {
        id: this.generateId(),
        name,
        description: description || '',
        config,
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        version: this.CURRENT_VERSION
      }
      
      // 检查是否已存在同名配置
      const existingIndex = configs.findIndex(c => c.name === name)
      if (existingIndex >= 0) {
        // 更新现有配置
        configs[existingIndex] = {
          ...configs[existingIndex],
          config,
          description: description || configs[existingIndex].description,
          updatedAt: new Date().toISOString()
        }
      } else {
        // 添加新配置
        configs.push(newConfig)
      }
      
      // 压缩并保存
      const compressed = this.compressData(configs)
      localStorage.setItem(this.STORAGE_KEY, compressed)
      
      // 创建备份
      await this.createBackup()
    } catch (error) {
      console.error('Failed to save config:', error)
      throw new Error('保存配置失败')
    }
  }

  /**
   * 获取所有配置
   */
  async getAllConfigs(): Promise<SavedConfig[]> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY)
      if (!data) return []
      
      const decompressed = this.decompressData(data)
      return decompressed || []
    } catch (error) {
      console.error('Failed to load configs:', error)
      throw new Error('加载配置失败')
    }
  }

  /**
   * 加载指定配置
   */
  async loadConfig(id: string): Promise<ConfigData | null> {
    try {
      const configs = await this.getAllConfigs()
      const config = configs.find(c => c.id === id)
      return config ? config.config : null
    } catch (error) {
      console.error('Failed to load config:', error)
      throw new Error('加载配置失败')
    }
  }

  /**
   * 删除配置
   */
  async deleteConfig(id: string): Promise<void> {
    try {
      const configs = await this.getAllConfigs()
      const filtered = configs.filter(c => c.id !== id)
      
      const compressed = this.compressData(filtered)
      localStorage.setItem(this.STORAGE_KEY, compressed)
      
      // 创建备份
      await this.createBackup()
    } catch (error) {
      console.error('Failed to delete config:', error)
      throw new Error('删除配置失败')
    }
  }

  /**
   * 重命名配置
   */
  async renameConfig(id: string, newName: string): Promise<void> {
    try {
      const configs = await this.getAllConfigs()
      const config = configs.find(c => c.id === id)
      
      if (!config) {
        throw new Error('配置不存在')
      }
      
      config.name = newName
      config.updatedAt = new Date().toISOString()
      
      const compressed = this.compressData(configs)
      localStorage.setItem(this.STORAGE_KEY, compressed)
    } catch (error) {
      console.error('Failed to rename config:', error)
      throw new Error('重命名配置失败')
    }
  }

  /**
   * 导出配置到文件
   */
  async exportConfig(id: string): Promise<void> {
    try {
      const configs = await this.getAllConfigs()
      const config = configs.find(c => c.id === id)
      
      if (!config) {
        throw new Error('配置不存在')
      }
      
      // 创建下载
      const blob = new Blob([JSON.stringify(config, null, 2)], { type: 'application/json' })
      const url = URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `config-${config.name}-${Date.now()}.json`
      document.body.appendChild(a)
      a.click()
      document.body.removeChild(a)
      URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Failed to export config:', error)
      throw new Error('导出配置失败')
    }
  }

  /**
   * 从文件导入配置
   */
  async importConfig(file: File): Promise<void> {
    try {
      const text = await file.text()
      const importedConfig: SavedConfig = JSON.parse(text)
      
      // 验证配置格式
      if (!this.validateConfig(importedConfig)) {
        throw new Error('配置格式无效')
      }
      
      // 生成新ID避免冲突
      importedConfig.id = this.generateId()
      importedConfig.updatedAt = new Date().toISOString()
      
      const configs = await this.getAllConfigs()
      configs.push(importedConfig)
      
      const compressed = this.compressData(configs)
      localStorage.setItem(this.STORAGE_KEY, compressed)
      
      // 创建备份
      await this.createBackup()
    } catch (error) {
      console.error('Failed to import config:', error)
      throw new Error('导入配置失败')
    }
  }

  /**
   * 创建备份
   */
  private async createBackup(): Promise<void> {
    try {
      const data = localStorage.getItem(this.STORAGE_KEY)
      if (data) {
        localStorage.setItem(this.BACKUP_KEY, data)
        localStorage.setItem(`${this.BACKUP_KEY}-timestamp`, Date.now().toString())
      }
    } catch (error) {
      console.error('Failed to create backup:', error)
    }
  }

  /**
   * 恢复备份
   */
  async restoreBackup(): Promise<void> {
    try {
      const backup = localStorage.getItem(this.BACKUP_KEY)
      if (backup) {
        localStorage.setItem(this.STORAGE_KEY, backup)
        return true
      }
      return false
    } catch (error) {
      console.error('Failed to restore backup:', error)
      throw new Error('恢复备份失败')
    }
  }

  /**
   * 数据压缩
   */
  private compressData(data: any): string {
    try {
      const json = JSON.stringify(data)
      // 简单的 Base64 压缩
      return btoa(unescape(encodeURIComponent(json)))
    } catch (error) {
      console.error('Compression failed:', error)
      return JSON.stringify(data)
    }
  }

  /**
   * 数据解压
   */
  private decompressData(data: string): any {
    try {
      // 尝试 Base64 解压
      const json = decodeURIComponent(escape(atob(data)))
      return JSON.parse(json)
    } catch (error) {
      // 如果解压失败，直接解析
      try {
        return JSON.parse(data)
      } catch (e) {
        console.error('Decompression failed:', error)
        return null
      }
    }
  }

  /**
   * 版本迁移
   */
  private async migrateData(fromVersion: string, toVersion: string): Promise<void> {
    console.log(`Migrating from ${fromVersion} to ${toVersion}`)
    // 这里可以添加版本迁移逻辑
    await this.createBackup()
  }

  /**
   * 验证配置格式
   */
  private validateConfig(config: any): config is SavedConfig {
    return (
      config &&
      typeof config.id === 'string' &&
      typeof config.name === 'string' &&
      typeof config.config === 'object' &&
      Array.isArray(config.config.models) &&
      typeof config.config.rules === 'object'
    )
  }

  /**
   * 生成唯一ID
   */
  private generateId(): string {
    return `config_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  /**
   * 获取存储统计信息
   */
  async getStorageStats(): Promise<{
    totalConfigs: number
    totalSize: number
    lastBackup?: Date
  }> {
    const configs = await this.getAllConfigs()
    const data = localStorage.getItem(this.STORAGE_KEY)
    const backupTimestamp = localStorage.getItem(`${this.BACKUP_KEY}-timestamp`)
    
    return {
      totalConfigs: configs.length,
      totalSize: data ? new Blob([data]).size : 0,
      lastBackup: backupTimestamp ? new Date(parseInt(backupTimestamp)) : undefined
    }
  }
}

// 导出单例实例
export const configStorage = new ConfigStorage()