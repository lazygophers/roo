<template>
  <!--
    NotFound.vue - 404 页面组件
    
    当用户访问不存在的路径时显示此页面。
    提供返回首页的链接。
  -->
  <div class="not-found-container">
    <div class="not-found-content">
      <div class="error-code">404</div>
      <h1 class="error-title">页面未找到</h1>
      <p class="error-message">
        抱歉，您访问的页面不存在或已被移除。
      </p>
      <div class="error-actions">
        <router-link to="/" class="btn btn-primary">
          <i class="fas fa-home"></i>
          返回首页
        </router-link>
        <button @click="goBack" class="btn btn-secondary">
          <i class="fas fa-arrow-left"></i>
          返回上一页
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
/**
 * NotFound.vue - 404 页面组件
 * 
 * 当用户访问不存在的路径时显示此页面。
 * 提供返回首页和返回上一页的选项。
 * 
 * @component
 */

// 导入 Vue Router 的 useRoute 和 useRouter
import { useRoute, useRouter } from 'vue-router'

// 获取当前路由和路由器实例
const route = useRoute()
const router = useRouter()

// 返回上一页的方法
const goBack = () => {
  // 如果有历史记录，则返回上一页
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    // 否则返回首页
    router.push('/')
  }
}
</script>

<style scoped>
/* 404 页面容器样式 */
.not-found-container {
  min-height: 60vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.not-found-content {
  text-align: center;
  max-width: 600px;
}

.error-code {
  font-size: 8rem;
  font-weight: 800;
  color: var(--accent-primary);
  line-height: 1;
  margin-bottom: 1rem;
  text-shadow: 0 0 20px rgba(0, 212, 255, 0.3);
}

.error-title {
  font-size: 2.5rem;
  font-weight: 700;
  color: var(--text-primary);
  margin-bottom: 1rem;
}

.error-message {
  font-size: 1.125rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
  line-height: 1.6;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 按钮样式复用 */
.btn {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 8px;
  text-decoration: none;
  font-weight: 600;
  transition: var(--transition-smooth);
  border: none;
  cursor: pointer;
  font-size: 1rem;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 16px rgba(0, 212, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(0, 212, 255, 0.4);
}

.btn-secondary {
  background: var(--bg-card);
  color: var(--text-primary);
  border: 1px solid var(--border-color);
}

.btn-secondary:hover {
  background: rgba(0, 212, 255, 0.1);
  border-color: var(--accent-primary);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .error-code {
    font-size: 6rem;
  }
  
  .error-title {
    font-size: 2rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
}

/* 动画效果 */
@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.not-found-content {
  animation: fadeIn 0.6s ease-out;
}
</style>