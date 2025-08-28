// 测试 API 响应数据结构修复
import { createApp } from 'vue'
import api from './src/api/index.ts'

// 创建 Vue 应用实例
const app = createApp({})

// 测试 /api/models 端点
const testModelsApi = async () => {
  console.log('测试 /api/models 端点...')
  try {
    const response = await api.post('/api/models')
    console.log('API Response:', response)
    
    // 检查响应数据结构
    if (Array.isArray(response)) {
      console.log('✅ 数据结构正确：响应是数组')
      console.log(`📊 数据长度: ${response.length}`)
      
      if (response.length > 0) {
        console.log('📝 示例数据:', response[0])
      }
    } else {
      console.log('❌ 数据结构错误：响应不是数组')
      console.log('实际响应类型:', typeof response)
      console.log('响应内容:', response)
    }
  } catch (error) {
    console.error('❌ API 调用失败:', error)
  }
}

// 测试 /api/hello 端点
const testHelloApi = async () => {
  console.log('\n测试 /api/hello 端点...')
  try {
    const response = await api.post('/api/hello', { message: '测试消息' })
    console.log('API Response:', response)
    
    // 检查响应数据结构
    if (response && response.message) {
      console.log('✅ 数据结构正确：包含 message 字段')
      console.log('📝 消息内容:', response.message)
    } else {
      console.log('❌ 数据结构错误：缺少 message 字段')
      console.log('实际响应:', response)
    }
  } catch (error) {
    console.error('❌ API 调用失败:', error)
  }
}

// 运行所有测试
const runTests = async () => {
  console.log('🧪 开始 API 响应数据结构测试...\n')
  
  await testModelsApi()
  await testHelloApi()
  
  console.log('\n✨ 测试完成！')
}

// 如果直接运行此脚本
if (typeof window === 'undefined') {
  // Node.js 环境
  const axios = require('axios')
  
  // 模拟 api 实例
  const mockApi = {
    post: async (url, data) => {
      console.log(`模拟请求: POST ${url}`, data)
      // 模拟响应
      if (url === '/api/models') {
        return [{ name: '模型1', slug: 'model1' }]
      } else if (url === '/api/hello') {
        return { message: 'Hello from API!' }
      }
      return {}
    }
  }
  
  // 替换全局 api
  global.api = mockApi
  
  runTests()
} else {
  // 浏览器环境
  window.testApiFix = runTests
}