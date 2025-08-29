/**
 * Vue Router 配置文件
 * 
 * 定义应用的所有路由规则，包括：
 * - 首页路由 (/)
 * - 配置选择器路由 (/config)
 * - 404 页面路由
 * 
 * 使用 Vue Router 的 createRouter 和 createWebHistory
 * 创建基于 history 模式的路由实例
 */

// 导入 Vue Router 的核心函数
import { createRouter, createWebHistory } from 'vue-router'

// 导入页面组件
// 使用动态导入（lazy loading）优化性能，组件会在路由被访问时才加载
const HomeView = () => import('../views/HomeView.vue')
const ConfigSelector = () => import('../views/ConfigSelector.vue')

// 定义路由配置
const routes = [
  {
    // 首页路由
    path: '/',
    name: 'home',
    component: HomeView,
    // 路由元信息，可用于页面标题、权限控制等
    meta: {
      title: '首页 - Roo Code 配置管理工具'
    }
  },
  {
    // 配置选择器页面路由
    path: '/config',
    name: 'config',
    component: ConfigSelector,
    // 路由元信息
    meta: {
      title: '配置选择器 - Roo Code 配置管理工具'
    }
  },
  {
    // 404 页面路由 - 捕获所有未匹配的路径
    path: '/:pathMatch(.*)*',
    name: 'not-found',
    component: () => import('../views/NotFound.vue'),
    meta: {
      title: '页面未找到 - Roo Code 配置管理工具'
    }
  }
]

// 创建路由实例
const router = createRouter({
  // 使用 HTML5 History 模式，URL 更美观（无 # 号）
  history: createWebHistory(),
  
  // 路由配置
  routes,
  
  // 滚动行为配置
  // 在路由切换时，页面滚动到顶部
  scrollBehavior(to, from, savedPosition) {
    if (savedPosition) {
      // 如果有保存的滚动位置（通过浏览器前进/后退），恢复到该位置
      return savedPosition
    } else {
      // 否则滚动到页面顶部
      return { top: 0 }
    }
  }
})

// 全局前置守卫
// 用于设置页面标题等全局操作
router.beforeEach((to, from, next) => {
  // 设置页面标题
  if (to.meta.title) {
    document.title = to.meta.title
  } else {
    document.title = 'Roo Code 配置管理工具'
  }
  
  // 继续导航
  next()
})

// 导出路由实例，供 main.ts 使用
export default router