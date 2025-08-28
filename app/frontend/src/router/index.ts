import { createRouter, createWebHashHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/HomeView.vue'),
    meta: {
      title: '首页'
    }
  },
  {
    path: '/config',
    name: 'Config',
    component: () => import('@/views/ConfigSelector.vue'),
    meta: {
      title: '配置选择器'
    }
  },
]

const router = createRouter({
  history: createWebHashHistory(),
  routes
})

// 路由守卫：设置页面标题
router.beforeEach((to, from, next) => {
  document.title = `${to.meta.title} - FastAPI + Vue3 示例` || 'FastAPI + Vue3 示例'
  next()
})

export default router