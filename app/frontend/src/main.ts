/**
 * Vue 应用程序入口文件
 * 负责初始化 Vue 应用实例、配置插件和挂载应用
 */

// 导入 Vue 3 的 createApp 函数，用于创建 Vue 应用实例
import { createApp } from 'vue'

// 导入 Pinia 状态管理库的 createPinia 函数
// Pinia 是 Vue 3 的官方状态管理解决方案
import { createPinia } from 'pinia'

// 导入根组件 App.vue，这是整个应用的顶层组件
import App from './App.vue'

// 导入路由配置模块
// router 包含了应用的所有路由定义和导航配置
import router from './router'

// 创建 Vue 应用实例
// createApp() 返回一个提供应用上下文的应用实例
const app = createApp(App)

// 创建 Pinia 状态管理实例
// Pinia 提供了响应式的状态存储和管理功能
const pinia = createPinia()

// 注册 Pinia 插件到 Vue 应用
// app.use() 用于安装 Vue 插件
// 注册后，所有组件都可以通过 useStore() 访问状态管理
app.use(pinia)

// 注册路由插件到 Vue 应用
// 注册后，应用将支持基于路由的页面导航和组件渲染
app.use(router)

// 将 Vue 应用挂载到 DOM 元素上
// '#app' 是在 index.html 中定义的根元素 ID
// 挂载后，Vue 将接管该元素及其子元素的管理
app.mount('#app')