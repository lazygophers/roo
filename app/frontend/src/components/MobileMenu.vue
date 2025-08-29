<template>
  <div class="mobile-menu">
    <!-- 背景遮罩 -->
    <div 
      v-if="isOpen" 
      class="menu-backdrop"
      @click="$emit('close')"
    ></div>
    
    <!-- 侧边栏菜单 -->
    <Transition name="slide">
      <div v-if="isOpen" class="menu-sidebar">
        <!-- 菜单头部 -->
        <div class="menu-header">
          <h3 class="menu-title">菜单</h3>
          <button class="close-button" @click="$emit('close')">
            <span class="close-icon">&times;</span>
          </button>
        </div>
        
        <!-- 菜单内容 -->
        <div class="menu-content">
          <!-- 导航链接 -->
          <div class="menu-section">
            <h4 class="section-title">导航</h4>
            <nav class="menu-nav">
              <router-link 
                v-for="item in navItems" 
                :key="item.path"
                :to="item.path" 
                class="menu-item"
                @click="$emit('close')"
              >
                <i :class="item.icon"></i>
                <span>{{ item.title }}</span>
              </router-link>
            </nav>
          </div>
          
          <!-- 功能链接 -->
          <div class="menu-section">
            <h4 class="section-title">功能</h4>
            <div class="menu-items">
              <button 
                v-for="item in featureItems" 
                :key="item.id"
                class="menu-item"
                @click="handleFeatureClick(item)"
              >
                <i :class="item.icon"></i>
                <span>{{ item.title }}</span>
              </button>
            </div>
          </div>
          
          <!-- 设置链接 -->
          <div class="menu-section">
            <h4 class="section-title">设置</h4>
            <div class="menu-items">
              <button 
                v-for="item in settingItems" 
                :key="item.id"
                class="menu-item"
                @click="handleSettingClick(item)"
              >
                <i :class="item.icon"></i>
                <span>{{ item.title }}</span>
              </button>
            </div>
          </div>
        </div>
        
        <!-- 菜单底部 -->
        <div class="menu-footer">
          <div class="user-info">
            <img :src="userAvatar" alt="用户头像" class="user-avatar" />
            <div class="user-details">
              <div class="user-name">{{ userName }}</div>
              <div class="user-role">{{ userRole }}</div>
            </div>
          </div>
        </div>
      </div>
    </Transition>
  </div>
</template>

<script>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'

export default {
  name: 'MobileMenu',
  props: {
    isOpen: {
      type: Boolean,
      default: false
    },
    userAvatar: {
      type: String,
      default: ''
    },
    userName: {
      type: String,
      default: '用户'
    },
    userRole: {
      type: String,
      default: '开发者'
    }
  },
  emits: ['close', 'feature-click', 'setting-click'],
  setup(props, { emit }) {
    const router = useRouter()
    
    // 导航项目
    const navItems = [
      { path: '/', title: '首页', icon: 'fas fa-home' },
      { path: '/items', title: '项目', icon: 'fas fa-folder' },
      { path: '/config', title: '配置', icon: 'fas fa-cog' },
      { path: '/about', title: '关于', icon: 'fas fa-info-circle' }
    ]
    
    // 功能项目
    const featureItems = [
      { id: 'search', title: '搜索', icon: 'fas fa-search' },
      { id: 'favorites', title: '收藏夹', icon: 'fas fa-star' },
      { id: 'recent', title: '最近使用', icon: 'fas fa-clock' },
      { id: 'trash', title: '回收站', icon: 'fas fa-trash' }
    ]
    
    // 设置项目
    const settingItems = [
      { id: 'theme', title: '主题设置', icon: 'fas fa-palette' },
      { id: 'language', title: '语言设置', icon: 'fas fa-language' },
      { id: 'notifications', title: '通知设置', icon: 'fas fa-bell' },
      { id: 'privacy', title: '隐私设置', icon: 'fas fa-lock' },
      { id: 'help', title: '帮助中心', icon: 'fas fa-question-circle' },
      { id: 'logout', title: '退出登录', icon: 'fas fa-sign-out-alt' }
    ]
    
    // 处理功能点击
    const handleFeatureClick = (item) => {
      emit('feature-click', item)
      emit('close')
    }
    
    // 处理设置点击
    const handleSettingClick = (item) => {
      if (item.id === 'logout') {
        // 处理退出登录逻辑
        console.log('退出登录')
      }
      emit('setting-click', item)
      emit('close')
    }
    
    return {
      navItems,
      featureItems,
      settingItems,
      handleFeatureClick,
      handleSettingClick
    }
  }
}
</script>

<style scoped>
.mobile-menu {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  pointer-events: none;
}

.mobile-menu * {
  pointer-events: auto;
}

.menu-backdrop {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

.menu-sidebar {
  position: absolute;
  top: 0;
  left: 0;
  bottom: 0;
  width: 280px;
  max-width: 80%;
  background: var(--bg-secondary);
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.15);
  display: flex;
  flex-direction: column;
}

.menu-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1rem;
  border-bottom: 1px solid var(--border-color);
}

.menu-title {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--text-primary);
}

.close-button {
  background: none;
  border: none;
  padding: 0.5rem;
  border-radius: 50%;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 36px;
  height: 36px;
}

.close-button:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
}

.close-icon {
  font-size: 1.5rem;
  font-family: auto;
}

.menu-content {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 0;
}

.menu-section {
  margin-bottom: 1.5rem;
}

.menu-section:last-child {
  margin-bottom: 0;
}

.section-title {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  margin: 0 0 0.75rem 1rem;
  padding: 0 1rem;
}

.menu-nav {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.menu-items {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  text-decoration: none;
  color: var(--text-primary);
  background: none;
  border: none;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
  width: 100%;
  text-align: left;
}

.menu-item:hover {
  background: var(--bg-hover);
  color: var(--text-primary);
  transform: translateX(4px);
}

.menu-item.router-link-active {
  background: var(--primary-color);
  color: white;
}

.menu-item i {
  width: 20px;
  text-align: center;
}

.menu-footer {
  padding: 1rem;
  border-top: 1px solid var(--border-color);
}

.user-info {
  display: flex;
  align-items: center;
  gap: 0.75rem;
}

.user-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  object-fit: cover;
}

.user-details {
  flex: 1;
}

.user-name {
  font-weight: 600;
  color: var(--text-primary);
  font-size: 0.875rem;
}

.user-role {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

/* 进入动画 */
.slide-enter-active,
.slide-leave-active {
  transition: transform 0.3s ease;
}

.slide-enter-from {
  transform: translateX(-100%);
}

.slide-leave-to {
  transform: translateX(-100%);
}

/* 横屏适配 */
@media (min-width: 768px) and (orientation: landscape) {
  .menu-sidebar {
    width: 320px;
  }
}

/* 暗色模式支持 */
@media (prefers-color-scheme: dark) {
  .menu-sidebar {
    background: var(--bg-secondary-dark);
  }
}

/* 减少动画偏好 */
@media (prefers-reduced-motion: reduce) {
  .slide-enter-active,
  .slide-leave-active,
  .menu-item,
  .close-button {
    transition: none;
  }
}
</style>