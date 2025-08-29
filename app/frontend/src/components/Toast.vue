<template>
  <Teleport to="body">
    <div class="toast-container">
      <TransitionGroup name="toast" tag="div">
        <div
          v-for="toast in toasts"
          :key="toast.id"
          :class="['toast', toast.type, toast.show ? 'show' : 'hide']"
          role="alert"
          :aria-live="toast.type === 'error' ? 'assertive' : 'polite'"
        >
          <div class="toast-icon">
            <span v-if="toast.type === 'success'">✓</span>
            <span v-else-if="toast.type === 'error'">✕</span>
            <span v-else-if="toast.type === 'warning'">⚠</span>
            <span v-else>ℹ</span>
          </div>
          <div class="toast-content">
            <div class="toast-title">{{ toast.title }}</div>
            <div class="toast-message">{{ toast.message }}</div>
          </div>
          <button 
            class="toast-close"
            @click="removeToast(toast.id)"
            aria-label="关闭通知"
          >
            ×
          </button>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'

// Toast 状态管理
const toasts = ref([])

// 生成唯一 ID
const generateId = () => `toast-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`

// 添加 Toast
const addToast = ({ title, message, type = 'info', duration = 3000 }) => {
  const id = generateId()
  const toast = {
    id,
    title,
    message,
    type,
    show: false
  }
  
  toasts.value.push(toast)
  
  // 触发显示动画
  setTimeout(() => {
    toast.show = true
  }, 10)
  
  // 自动移除
  if (duration > 0) {
    setTimeout(() => {
      removeToast(id)
    }, duration)
  }
  
  return id
}

// 移除 Toast
const removeToast = (id) => {
  const toast = toasts.value.find(t => t.id === id)
  if (toast) {
    toast.show = false
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 300)
  }
}

// 快捷方法
const success = (title, message, duration) => 
  addToast({ title, message, type: 'success', duration })

const error = (title, message, duration) => 
  addToast({ title, message, type: 'error', duration })

const warning = (title, message, duration) => 
  addToast({ title, message, type: 'warning', duration })

const info = (title, message, duration) => 
  addToast({ title, message, type: 'info', duration })

// 导出方法供全局使用
defineExpose({
  success,
  error,
  warning,
  info,
  addToast,
  removeToast
})
</script>

<style scoped>
/* Toast 通知样式已在 ItemsView.vue 中定义 */
</style>