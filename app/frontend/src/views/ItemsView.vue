<template>
  <div class="items-view">
    <div class="page-header">
      <h1>项目管理</h1>
      <button @click="showAddForm = true" class="btn btn-primary">添加新项目</button>
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
import { ref, onMounted } from 'vue'
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
    const response = await axios.get('/api/items')
    items.value = response.data
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
      await axios.put(`/api/items/${editingItem.value.id}`, formData.value)
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
    await axios.delete(`/api/items/${id}`)
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

onMounted(() => {
  fetchItems()
})
</script>

<style scoped>
.items-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  animation: fadeIn 0.5s ease-out;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
  padding: 1.5rem;
  background: rgba(30, 41, 59, 0.5);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(99, 179, 237, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
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
  background: linear-gradient(90deg, transparent, rgba(0, 255, 255, 0.1), transparent);
  animation: shimmer 3s infinite;
}

@keyframes shimmer {
  0% { left: -100%; }
  100% { left: 200%; }
}

.page-header h1 {
  color: var(--text-primary);
  font-size: 2rem;
  font-weight: 600;
  text-shadow: 0 0 20px rgba(0, 255, 255, 0.5);
}

.form-card {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 16px;
  margin-bottom: 2rem;
  border: 1px solid rgba(99, 179, 237, 0.3);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  position: relative;
}

.form-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 16px 16px 0 0;
}

.form-card h2 {
  color: var(--text-primary);
  margin-bottom: 1.5rem;
  font-size: 1.5rem;
  font-weight: 500;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: var(--text-secondary);
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem 1rem;
  border: 1px solid rgba(99, 179, 237, 0.3);
  border-radius: 8px;
  font-size: 1rem;
  background: rgba(30, 41, 59, 0.4);
  color: var(--text-primary);
  transition: all 0.3s ease;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: var(--accent-primary);
  box-shadow: 0 0 0 3px rgba(0, 255, 255, 0.2),
            0 0 20px rgba(0, 255, 255, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1.5rem;
  border-radius: 8px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  text-transform: uppercase;
  letter-spacing: 1px;
}

.btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s ease;
}

.btn:hover::before {
  left: 100%;
}

.btn-primary {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.3);
}

.btn-primary:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(0, 255, 255, 0.4);
}

.btn-secondary {
  background: rgba(108, 117, 125, 0.3);
  color: var(--text-secondary);
  border: 1px solid rgba(99, 179, 237, 0.3);
  backdrop-filter: blur(5px);
  -webkit-backdrop-filter: blur(5px);
}

.btn-secondary:hover {
  background: rgba(108, 117, 125, 0.5);
  border-color: var(--accent-primary);
  color: var(--text-primary);
  box-shadow: 0 4px 15px rgba(0, 255, 255, 0.2);
}

.btn-danger {
  background: linear-gradient(135deg, #dc3545, #c82333);
  color: white;
  box-shadow: 0 4px 15px rgba(220, 53, 69, 0.3);
}

.btn-danger:hover {
  transform: translateY(-2px);
  box-shadow: 0 6px 25px rgba(220, 53, 69, 0.4);
}

.btn-sm {
  padding: 0.4rem 1rem;
  font-size: 0.8rem;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
  transform: none !important;
}

.items-list {
  margin-top: 2rem;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 3rem;
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border-radius: 16px;
  border: 1px solid rgba(99, 179, 237, 0.3);
  color: var(--text-secondary);
  font-size: 1.1rem;
}

.error {
  color: #ff6b6b;
  border-color: rgba(255, 107, 107, 0.3);
  animation: pulse 2s infinite;
}

@keyframes pulse {
  0% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
  50% { box-shadow: 0 0 0 10px rgba(255, 107, 107, 0.3); }
  100% { box-shadow: 0 0 0 0 rgba(255, 107, 107, 0); }
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background: rgba(30, 41, 59, 0.3);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  border: 1px solid rgba(99, 179, 237, 0.3);
  border-radius: 16px;
  padding: 1.5rem;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.item-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: linear-gradient(90deg, var(--accent-primary), var(--accent-secondary));
  opacity: 0;
  transition: opacity 0.3s ease;
}

.item-card:hover::before {
  opacity: 1;
}

.item-card:hover {
  transform: translateY(-5px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.3);
  border-color: rgba(99, 179, 237, 0.5);
}

.item-card h3 {
  margin: 0 0 0.5rem 0;
  color: var(--text-primary);
  font-size: 1.25rem;
  font-weight: 500;
}

.item-card p {
  color: var(--text-secondary);
  margin: 0 0 1rem 0;
  line-height: 1.6;
}

.item-meta {
  margin-bottom: 1rem;
}

.item-meta small {
  color: var(--text-tertiary);
  font-size: 0.85rem;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .items-view {
    padding: 1rem;
  }

  .page-header {
    flex-direction: column;
    gap: 1rem;
    padding: 1rem;
  }

  .page-header h1 {
    font-size: 1.5rem;
  }

  .form-card {
    padding: 1.5rem;
  }

  .grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }

  .btn {
    padding: 0.4rem 1rem;
    font-size: 0.9rem;
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

/* 科技感装饰元素 */
.item-card::after {
  content: '';
  position: absolute;
  top: -50%;
  right: -50%;
  width: 200%;
  height: 200%;
  background: radial-gradient(circle, rgba(0, 255, 255, 0.03) 0%, transparent 70%);
  opacity: 0;
  transition: opacity 0.3s ease;
  pointer-events: none;
}

.item-card:hover::after {
  opacity: 1;
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