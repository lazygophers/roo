<![CDATA[
<template>
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <div class="items-view"
    @touchstart="handleTouchStart"
    @touchmove="handleTouchMove"
    @touchend="handleTouchEnd">
    <div class="page-header">
      <h1>项目管理</h1>
      <button @click="showAddForm = true" class="btn btn-primary">
        <span class="btn-icon">+</span>
        <span class="btn-text">添加新项目</span>
      </button>
    </div>

    <!-- 添加/编辑表单 -->
    <div v-if="showAddForm || editingItem" class="form-card">
      <h2>{{ editingItem ? '编辑项目' : '添加新项目' }}</h2>
      <form @submit.prevent="saveItem">
        <div class="form-group">
          <label for="name">名称</label>
          <input
            id="name"
            v-model="formData.name"
            type="text"
            required
            placeholder="输入项目名称"
          />
        </div>
        <div class="form-group">
          <label for="description">描述</label>
          <textarea
            id="description"
            v-model="formData.description"
            rows="3"
            placeholder="输入项目描述"
          ></textarea>
        </div>
        <div class="form-actions">
          <button type="submit" class="btn btn-primary" :disabled="saving">
            {{ saving ? '保存中...' : '保存' }}
          </button>
          <button type="button" @click="cancelForm" class="btn btn-secondary">取消</button>
        </div>
      </form>
    </div>

    <!-- 项目列表 -->
    <div class="items-list">
      <div v-if="loading && items.length === 0" class="loading">加载中...</div>
      <div v-else-if="error" class="error">{{ error }}</div>
      <div v-else-if="items.length === 0" class="empty-state">
        <p>暂无项目，点击"添加新项目"创建第一个项目</p>
      </div>
      <div v-else class="grid">
        <div v-for="item in items" :key="item.id" class="item-card">
          <div class="corner-decoration top-left"></div>
          <div class="corner-decoration top-right"></div>
          <div class="corner-decoration bottom-left"></div>
          <div class="corner-decoration bottom-right"></div>
          
          <h3>{{ item.name }}</h3>
          <p>{{ item.description || '暂无描述' }}</p>
          <div class="item-meta">
            <small>创建时间: {{ formatDate(item.created_at) }}</small>
          </div>
          <div class="item-actions">
            <button @click="editItem(item)" class="btn btn-sm">编辑</button>
            <button @click="deleteItem(item.id)" class="btn btn-sm btn-danger">删除</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import axios from 'axios'

interface Item {
  id?: number
  name: string
  description?: string
  created_at?: string
  updated_at?: string
}

const items = ref<Item[]>([])
const loading = ref(false)
const error = ref('')
const saving = ref(false)
const showAddForm = ref(false)
const editingItem = ref<Item | null>(null)
const formData = ref<Item>({ name: '', description: '' })

const fetchItems = async () => {
  loading.value = true
  error.value = ''
  try {
    const response = await axios.post('/api/items')
    items.value = response
  } catch (err) {
    error.value = '获取项目列表失败'
    console.error(err)
  } finally {
    loading.value = false
  }
}

const saveItem = async () => {
  saving.value = true
  try {
    if (editingItem.value?.id) {
      // 更新
      await axios.post('/api/items/update', formData.value)
    } else {
      // 创建
      await axios.post('/api/items', formData.value)
    }
    await fetchItems()
    cancelForm()
  } catch (err) {
    console.error('保存失败:', err)
    alert('保存失败，请重试')
  } finally {
    saving.value = false
  }
}

const editItem = (item: Item) => {
  editingItem.value = { ...item }
  formData.value = { ...item }
  showAddForm.value = false
}

const deleteItem = async (id: number) => {
  if (!confirm('确定要删除这个项目吗？')) return
  
  try {
    await axios.post('/api/items/delete', { id })
    await fetchItems()
  } catch (err) {
    console.error('删除失败:', err)
    alert('删除失败，请重试')
  }
}

const cancelForm = () => {
  showAddForm.value = false
  editingItem.value = null
  formData.value = { name: '', description: '' }
}

const formatDate = (dateString?: string) => {
  if (!dateString) return '-'
  return new Date(dateString).toLocaleString('zh-CN')
}

// 触摸手势支持
const touchStartX = ref(0)
const touchStartY = ref(0)
const touchEndX = ref(0)
const touchEndY = ref(0)
const isSwiping = ref(false)
const touchStartTime = ref(0)
const swipeFeedback = ref(false)

const handleTouchStart = (e: TouchEvent) => {
  touchStartX.value = e.changedTouches[0].screenX
  touchStartY.value = e.changedTouches[0].screenY
  touchStartTime.value = Date.now()
  isSwiping.value = false
  
  // 防止与滚动冲突
  const target = e.target as HTMLElement
  if (target.closest('.item-card, .form-group, .btn')) {
    e.preventDefault()
  }
}

const handleTouchMove = (e: TouchEvent) => {
  if (!isSwiping.value) {
    const deltaX = e.changedTouches[0].screenX - touchStartX.value
    const deltaY = e.changedTouches[0].screenY - touchStartY.value
    
    // 检测是否为横向滑动
    if (Math.abs(deltaX) > Math.abs(deltaY) && Math.abs(deltaX) > 10) {
      isSwiping.value = true
      e.preventDefault() // 阻止滚动
    }
  }
  
  if (isSwiping.value) {
    e.preventDefault()
    
    // 显示滑动反馈
    const deltaX = e.changedTouches[0].screenX - touchStartX.value
    const progress = Math.min(Math.abs(deltaX) / 100, 1)
    
    if (deltaX > 0) {
      // 右滑反馈
      swipeFeedback.value = true
      document.body.style.background = `linear-gradient(90deg,
        rgba(59, 130, 246, ${0.1 * progress}) 0%,
        transparent 50%)`
    } else {
      // 左滑反馈
      swipeFeedback.value = true
      document.body.style.background = `linear-gradient(270deg,
        rgba(139, 92, 246, ${0.1 * progress}) 0%,
        transparent 50%)`
    }
  }
}

const handleTouchEnd = (e: TouchEvent) => {
  touchEndX.value = e.changedTouches[0].screenX
  touchEndY.value = e.changedTouches[0].screenY
  
  // 清除反馈
  document.body.style.background = ''
  swipeFeedback.value = false
  
  handleSwipe()
}

const handleSwipe = () => {
  const deltaX = touchEndX.value - touchStartX.value
  const deltaY = touchEndY.value - touchStartY.value
  const deltaTime = Date.now() - touchStartTime.value
  const velocity = Math.abs(deltaX) / deltaTime
  
  // 滑动阈值和速度要求
  const minSwipeDistance = 50
  const maxSwipeTime = 500
  const minSwipeVelocity = 0.3
  
  if (deltaTime < maxSwipeTime &&
      Math.abs(deltaX) > Math.abs(deltaY) &&
      Math.abs(deltaX) > minSwipeDistance &&
      velocity > minSwipeVelocity) {
    
    // 触发反馈
    if ('vibrate' in navigator) {
      navigator.vibrate(50)
    }
    
    if (deltaX > 0) {
      // 向右滑动 - 刷新项目列表
      showToast('正在刷新...')
      fetchItems()
    } else {
      // 向左滑动 - 显示添加表单
      showToast('显示添加表单')
      showAddForm.value = true
    }
  }
}

// Toast 提示
const showToast = (message: string) => {
  const toast = document.createElement('div')
  toast.className = 'toast-notification'
  toast.textContent = message
  document.body.appendChild(toast)
  
  setTimeout(() => {
    toast.remove()
  }, 2000)
}

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.items-view {
  max-width: 1400px;
  margin: 0 auto;
  padding: 2rem;
  animation: fadeIn 0.6s cubic-bezier(0.4, 0, 0.2, 1);
  min-height: 100vh;
  background: radial-gradient(ellipse at top, rgba(0, 20, 40, 0.3) 0%, transparent 50%);
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2.5rem;
  padding: 2rem;
  background: linear-gradient(135deg, 
    rgba(15, 23, 42, 0.8) 0%, 
    rgba(30, 41, 59, 0.6) 50%,
    rgba(15, 23, 42, 0.8) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 20px;
  border: 1px solid rgba(99, 179, 237, 0.2);
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.page-header::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(0, 255, 255, 0.15), 
    transparent,
    rgba(147, 51, 234, 0.15),
    transparent);
  animation: shimmer 4s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 200%; }
}

.page-header h1 {
  color: var(--text-primary);
  font-size: 2.25rem;
  font-weight: 700;
  background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 0 40px rgba(96, 165, 250, 0.5);
}

.form-card {
  background: linear-gradient(135deg,
    rgba(15, 23, 42, 0.7) 0%,
    rgba(30, 41, 59, 0.5) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  padding: 2.5rem;
  border-radius: 20px;
  margin-bottom: 2.5rem;
  border: 1px solid rgba(99, 179, 237, 0.2);
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  transform: translateZ(0);
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    #3b82f6, 
    #8b5cf6, 
    #ec4899, 
    #f59e0b);
  animation: gradient-shift 8s ease infinite;
  background-size: 200% 100%;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}

.form-card h2 {
  color: var(--text-primary);
  margin-bottom: 2rem;
  font-size: 1.75rem;
  font-weight: 600;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
}

.form-group {
  margin-bottom: 2rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.75rem;
  font-weight: 600;
  color: var(--text-secondary);
  font-size: 0.95rem;
  letter-spacing: 0.025em;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 1rem 1.25rem;
  border: 1px solid rgba(99, 179, 237, 0.2);
  border-radius: 12px;
  font-size: 1rem;
  background: rgba(15, 23, 42, 0.6);
  backdrop-filter: blur(10px);
  color: var(--text-primary);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #3b82f6;
  box-shadow: 
    0 0 0 4px rgba(59, 130, 246, 0.2),
    0 0 30px rgba(59, 130, 246, 0.15),
    inset 0 0 0 1px rgba(59, 130, 246, 0.1);
  transform: translateY(-2px);
}

.form-actions {
  display: flex;
  gap: 1.25rem;
  margin-top: 2.5rem;
}

/* 基础按钮样式 */
.btn {
  padding: 0.875rem 2rem;
  border-radius: 12px;
  border: none;
  font-weight: 700;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-size: 0.9rem;
  line-height: 1.25rem;
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  outline: none;
  transform: translateZ(0);
}

/* 按钮多层光泽效果 */
.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, 
    transparent, 
    rgba(255, 255, 255, 0.4), 
    transparent,
    rgba(255, 255, 255, 0.2),
    transparent);
  transition: left 0.8s ease;
  z-index: 1;
}

.btn:hover::before {
  left: 100%;
}

/* 按钮内发光效果 */
.btn::after {
  content: '';
  position: absolute;
  top: 50%;
  left: 50%;
  width: 0;
  height: 0;
  border-radius: 50%;
  background: radial-gradient(circle, 
    rgba(255, 255, 255, 0.4) 0%, 
    transparent 70%);
  transform: translate(-50%, -50%);
  transition: width 0.8s ease, height 0.8s ease;
}

.btn:active::after {
  width: 400px;
  min-height: 400px;
}

/* 主要按钮 - 蓝紫色渐变 */
.btn-primary {
  background: linear-gradient(135deg, 
    #3b82f6 0%, 
    #8b5cf6 50%,
    #ec4899 100%);
  color: white;
  box-shadow:
    0 6px 20px rgba(59, 130, 246, 0.4),
    0 0 40px rgba(139, 92, 246, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
  position: relative;
}

.btn-primary::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(135deg,
    rgba(255, 255, 255, 0.2) 0%,
    transparent 50%,
    rgba(255, 255, 255, 0.1) 100%);
  border-radius: 12px;
  opacity: 0;
  transition: opacity 0.3s ease;
}

.btn-primary:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow:
    0 8px 30px rgba(59, 130, 246, 0.5),
    0 0 60px rgba(139, 92, 246, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.btn-primary:hover::before {
  opacity: 1;
}

.btn-primary:active {
  transform: translateY(-1px) scale(0.99);
}

/* 次要按钮 - 玻璃态效果 */
.btn-secondary {
  background: linear-gradient(135deg,
    rgba(148, 163, 184, 0.3) 0%,
    rgba(100, 116, 139, 0.4) 100%);
  color: var(--text-primary);
  border: 1px solid rgba(148, 163, 184, 0.3);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  box-shadow:
    0 6px 20px rgba(0, 0, 0, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
}

.btn-secondary:hover {
  background: linear-gradient(135deg,
    rgba(148, 163, 184, 0.4) 0%,
    rgba(100, 116, 139, 0.5) 100%);
  border-color: #3b82f6;
  color: white;
  transform: translateY(-3px);
  box-shadow:
    0 8px 30px rgba(59, 130, 246, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.3);
}

/* 危险按钮 - 红橙渐变 */
.btn-danger {
  background: linear-gradient(135deg, 
    #ef4444 0%,
    #f97316 50%,
    #eab308 100%);
  color: white;
  box-shadow:
    0 6px 20px rgba(239, 68, 68, 0.4),
    0 0 40px rgba(249, 115, 22, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.btn-danger:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow:
    0 8px 30px rgba(239, 68, 68, 0.5),
    0 0 60px rgba(249, 115, 22, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.btn-danger:active {
  transform: translateY(-1px) scale(0.99);
}

/* 小型按钮 */
.btn-sm {
  padding: 0.5rem 1.25rem;
  font-size: 0.825rem;
  font-weight: 600;
  border-radius: 10px;
}

/* 禁用状态 */
.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
  box-shadow: none !important;
  filter: grayscale(0.8);
}

.btn:disabled::before,
.btn:disabled::after {
  display: none;
}

/* 按钮图标 */
.btn-icon {
  width: 1.25rem;
  height: 1.25rem;
  display: inline-block;
  vertical-align: middle;
  filter: drop-shadow(0 1px 2px rgba(0, 0, 0, 0.3));
}

/* 加载状态 */
.btn-loading {
  position: relative;
  color: transparent;
}

.btn-loading::after {
  content: '';
  position: absolute;
  width: 1.25rem;
  height: 1.25rem;
  top: 50%;
  left: 50%;
  margin-left: -0.625rem;
  margin-top: -0.625rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: btn-spin 0.8s linear infinite;
}

@keyframes btn-spin {
  to { transform: rotate(360deg); }
}

/* 成功按钮 */
.btn-success {
  background: linear-gradient(135deg, 
    #10b981 0%,
    #06b6d4 50%,
    #6366f1 100%);
  color: white;
  box-shadow:
    0 6px 20px rgba(16, 185, 129, 0.4),
    0 0 40px rgba(6, 182, 212, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.4);
}

.btn-success:hover {
  transform: translateY(-3px) scale(1.03);
  box-shadow:
    0 8px 30px rgba(16, 185, 129, 0.5),
    0 0 60px rgba(6, 182, 212, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

.items-list {
  margin-top: 2.5rem;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 4rem;
  background: linear-gradient(135deg,
    rgba(15, 23, 42, 0.8) 0%,
    rgba(30, 41, 59, 0.6) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border-radius: 20px;
  border: 1px solid rgba(99, 179, 237, 0.2);
  color: var(--text-secondary);
  font-size: 1.1rem;
  font-weight: 500;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  position: relative;
  overflow: hidden;
}

.loading::before,
.error::before,
.empty-state::before {
  content: '';
  position: absolute;
  top: -50%;
  left: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, 
    rgba(59, 130, 246, 0.1) 0%, 
    transparent 50%);
  animation: rotate 20s linear infinite;
}

.error {
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
  50% { box-shadow: 0 0 0 20px rgba(255, 107, 107, 0.4); }
  100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
  gap: 2rem;
}

.item-card {
  background: linear-gradient(135deg,
    rgba(15, 23, 42, 0.9) 0%,
    rgba(30, 41, 59, 0.7) 50%,
    rgba(15, 23, 42, 0.9) 100%);
  backdrop-filter: blur(20px) saturate(180%);
  -webkit-backdrop-filter: blur(20px) saturate(180%);
  border: 1px solid rgba(99, 179, 237, 0.2);
  border-radius: 20px;
  padding: 2rem;
  box-shadow: 
    0 10px 40px rgba(0, 0, 0, 0.3),
    inset 0 1px 0 rgba(255, 255, 255, 0.1);
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
  position: relative;
  overflow: hidden;
  transform: translateZ(0);
}

.item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 3px;
  background: linear-gradient(90deg, 
    #3b82f6,
    #8b5cf6,
    #ec4899,
    #f59e0b);
  opacity: 0;
  transition: opacity 0.4s ease;
  animation: gradient-shift 8s ease infinite;
  background-size: 200% 100%;
}

.item-card::after {
  content: '';
  position: absolute;
  top: -2px;
  left: -2px;
  right: -2px;
  bottom: -2px;
  background: linear-gradient(45deg,
    transparent,
    rgba(59, 130, 246, 0.3),
    transparent);
  border-radius: 20px;
  opacity: 0;
  transition: opacity 0.4s ease;
  z-index: -1;
}

.item-card:hover {
  transform: translateY(-6px);
  box-shadow: 
    0 15px 50px rgba(0, 0, 0, 0.4),
    0 0 60px rgba(59, 130, 246, 0.2),
    inset 0 1px 0 rgba(255, 255, 255, 0.2);
  border-color: rgba(99, 179, 237, 0.5);
}

.item-card:hover::before {
  opacity: 1;
}

.item-card:hover::after {
  opacity: 1;
}

.item-card h3 {
  margin: 0 0 1rem 0;
  color: var(--text-primary);
  font-size: 1.5rem;
  font-weight: 600;
  background: linear-gradient(135deg, #60a5fa, #a78bfa, #f472b6);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  text-shadow: 0 2px 10px rgba(96, 165, 250, 0.4);
}

.item-card p {
  color: var(--text-secondary);
  margin: 0 0 1.5rem 0;
  line-height: 1.7;
  font-size: 1rem;
}

.item-meta {
  margin-bottom: 1.5rem;
  padding-bottom: 1rem;
  border-bottom: 1px solid rgba(99, 179, 237, 0.1);
}

.item-meta small {
  color: var(--text-tertiary);
  font-size: 0.875rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-meta small::before {
  content: '📅';
  font-size: 1rem;
}

.item-actions {
  display: flex;
  gap: 0.75rem;
  margin-top: 1.5rem;
}

/* 科技感装饰元素 */
.item-card .corner-decoration {
  position: absolute;
  width: 20px;
  height: 20px;
  border: 2px solid rgba(99, 179, 237, 0.4);
  transition: all 0.3s ease;
}

.item-card .corner-decoration::before {
  content: '';
  position: absolute;
  top: 2px;
  left: 2px;
  width: 6px;
  height: 6px;
  background: #3b82f6;
  border-radius: 50%;
  box-shadow: 0 0 10px rgba(59, 130, 246, 0.5);
}

.item-card .corner-decoration.top-left {
  top: 10px;
  left: 10px;
  border-right: none;
  border-bottom: none;
}

.item-card .corner-decoration.top-right {
  top: 10px;
  right: 10px;
  border-left: none;
  border-bottom: none;
}

.item-card .corner-decoration.bottom-left {
  bottom: 10px;
  left: 10px;
  border-right: none;
  border-top: none;
}

.item-card .corner-decoration.bottom-right {
  bottom: 10px;
  right: 10px;
  border-left: none;
  border-top: none;
}

.item-card:hover .corner-decoration {
  border-color: #3b82f6;
  box-shadow: 
    0 0 15px rgba(59, 130, 246, 0.5),
    0 0 20px rgba(59, 130, 246, 0.3);
}

/* 移动端优先的响应式设计 */
/* 基础样式 - 移动端默认 */
.items-view {
  padding: 1rem;
}

.page-header {
  flex-direction: column;
  gap: 1.5rem;
  padding: 1.5rem;
}

.page-header h1 {
  font-size: 1.75rem;
  text-align: center;
}

.form-card {
  padding: 1.5rem;
}

.grid {
  grid-template-columns: 1fr;
  gap: 1rem;
}

.btn {
  padding: 0.75rem 1.5rem;
  font-size: 0.9rem;
  min-height: 44px; /* 确保触摸目标足够大 */
}

/* 按钮触摸目标优化 */
.btn-sm {
  min-height: 40px;
  min-width: 44px;
  padding: 0.5rem 1rem;
}

.item-actions {
  gap: 0.5rem;
}

.item-actions .btn {
  flex: 1; /* 让按钮平均分配宽度 */
}

/* 平板设备 */
@media (min-width: 768px) {
  .items-view {
    padding: 1.5rem;
  }

  .page-header {
    flex-direction: row;
    padding: 2rem;
  }

  .page-header h1 {
    font-size: 2rem;
    text-align: left;
  }

  .form-card {
    padding: 2rem;
  }

  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 1.5rem;
  }

  .btn {
    padding: 0.875rem 2rem;
  }

  .item-actions .btn {
    flex: none; /* 恢复默认宽度 */
  }
}

/* 桌面设备 */
@media (min-width: 1024px) {
  .items-view {
    padding: 2rem;
  }

  .page-header h1 {
    font-size: 2.25rem;
  }

  .form-card {
    padding: 2.5rem;
  }

  .grid {
    grid-template-columns: repeat(auto-fill, minmax(320px, 1fr));
    gap: 2rem;
  }
}

/* 大屏设备 */
@media (min-width: 1440px) {
  .items-view {
    max-width: 1400px;
    margin: 0 auto;
  }
}

/* 触摸设备优化 */
@media (hover: none) and (pointer: coarse) {
  /* 增大所有可点击元素 */
  .btn,
  .item-card,
  input,
  textarea,
  select {
    min-height: 44px;
    min-width: 44px;
  }
  
  /* 增加间距 */
  .form-group {
    margin-bottom: 1.5rem;
  }
  
  .item-actions {
    gap: 1rem;
  }
  
  /* 优化表单输入 */
  input,
  textarea,
  select {
    font-size: 16px; /* 防止iOS缩放 */
    padding: 0.75rem 1rem;
  }
  
  /* 去除悬停效果 */
  .item-card:hover {
    transform: none;
  }
  
  .btn:hover {
    transform: none;
  }
}

/* 横屏模式优化 */
@media (max-width: 768px) and (orientation: landscape) {
  .items-view {
    padding: 0.75rem;
  }
  
  .page-header {
    padding: 1rem;
    flex-direction: row;
  }
  
  .page-header h1 {
    font-size: 1.5rem;
  }
  
  .grid {
    grid-template-columns: repeat(2, 1fr);
    gap: 0.75rem;
  }
  
  .item-card {
    padding: 1.25rem;
  }
}

/* 深色模式支持 */
@media (prefers-color-scheme: dark) {
  .items-view {
    background: radial-gradient(ellipse at top, rgba(0, 0, 0, 0.3) 0%, transparent 50%);
  }
  
  .form-card,
  .item-card,
  .loading,
  .error,
  .empty-state {
    background: linear-gradient(135deg,
      rgba(0, 0, 0, 0.9) 0%,
      rgba(15, 15, 15, 0.7) 100%);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* 减少动画偏好支持 */
@media (prefers-reduced-motion: reduce) {
  *,
  *::before,
  *::after {
    animation-duration: 0.01ms !important;
    animation-iteration-count: 1 !important;
    transition-duration: 0.01ms !important;
    scroll-behavior: auto !important;
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

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: rgba(30, 41, 59, 0.3);
  border-radius: 4px;
}

::-webkit-scrollbar-thumb {
  background: rgba(99, 179, 237, 0.5);
  border-radius: 4px;
  border: 1px solid rgba(99, 179, 237, 0.3);
}

::-webkit-scrollbar-thumb:hover {
  background: rgba(99, 179, 237, 0.7);
}
</style>
]]>

/* Toast 通知样式 */
.toast-container {
  position: fixed;
  top: 20px;
  right: 20px;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  gap: 10px;
  pointer-events: none;
}

.toast {
  background: linear-gradient(135deg, rgba(30, 41, 59, 0.95) 0%, rgba(15, 23, 42, 0.98) 100%);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  padding: 16px 20px;
  min-width: 280px;
  max-width: 400px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  gap: 12px;
  pointer-events: auto;
  animation: slideIn 0.3s ease-out;
  transition: all 0.3s ease;
}

.toast.show {
  animation: slideIn 0.3s ease-out;
}

.toast.hide {
  animation: slideOut 0.3s ease-in forwards;
}

@keyframes slideIn {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}

@keyframes slideOut {
  from {
    transform: translateX(0);
    opacity: 1;
  }
  to {
    transform: translateX(100%);
    opacity: 0;
  }
}

.toast-icon {
  font-size: 20px;
  flex-shrink: 0;
}

.toast-content {
  flex: 1;
}

.toast-title {
  font-weight: 600;
  font-size: 0.875rem;
  margin-bottom: 2px;
}

.toast-message {
  font-size: 0.8125rem;
  opacity: 0.9;
  line-height: 1.4;
}

.toast-close {
  background: none;
  border: none;
  color: rgba(255, 255, 255, 0.5);
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  font-size: 16px;
  line-height: 1;
  transition: all 0.2s ease;
}

.toast-close:hover {
  color: rgba(255, 255, 255, 0.8);
  background: rgba(255, 255, 255, 0.1);
}

/* Toast 类型样式 */
.toast.success {
  border-color: rgba(120, 255, 214, 0.3);
  background: linear-gradient(135deg, rgba(16, 185, 129, 0.1) 0%, rgba(5, 150, 105, 0.05) 100%);
}

.toast.success .toast-icon {
  color: #78ff9c;
}

.toast.error {
  border-color: rgba(239, 68, 68, 0.3);
  background: linear-gradient(135deg, rgba(239, 68, 68, 0.1) 0%, rgba(220, 38, 38, 0.05) 100%);
}

.toast.error .toast-icon {
  color: #ff6b6b;
}

.toast.warning {
  border-color: rgba(251, 191, 36, 0.3);
  background: linear-gradient(135deg, rgba(251, 191, 36, 0.1) 0%, rgba(245, 158, 11, 0.05) 100%);
}

.toast.warning .toast-icon {
  color: #fbbf24;
}

.toast.info {
  border-color: rgba(59, 130, 246, 0.3);
  background: linear-gradient(135deg, rgba(59, 130, 246, 0.1) 0%, rgba(37, 99, 235, 0.05) 100%);
}

.toast.info .toast-icon {
  color: #60a5fa;
}

/* 移动端优化 */
@media (max-width: 768px) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: 10px;
  }
  
  .toast {
    min-width: auto;
    max-width: none;
    margin: 0 auto;
  }
}

@media (max-width: 480px) {
  .toast {
    padding: 12px 16px;
    min-width: auto;
  }
  
  .toast-icon {
    font-size: 18px;
  }
  
  .toast-title {
    font-size: 0.8125rem;
  }
  
  .toast-message {
    font-size: 0.75rem;
  }
}

/* 横屏模式 */
@media (max-width: 768px) and (orientation: landscape) {
  .toast-container {
    top: 10px;
    right: 10px;
    left: auto;
  }
  
  .toast {
    min-width: 300px;
    max-width: 350px;
  }
}

/* 深色模式适配 */
@media (prefers-color-scheme: dark) {
  .toast {
    background: linear-gradient(135deg, rgba(0, 0, 0, 0.95) 0%, rgba(15, 15, 15, 0.98) 100%);
    border-color: rgba(255, 255, 255, 0.1);
  }
}

/* 减少动画支持 */
@media (prefers-reduced-motion: reduce) {
  .toast {
    animation: none;
    transition: none;
  }
  
  .toast.show,
  .toast.hide {
    animation: none;
  }
}
