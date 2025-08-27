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
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 2rem;
}

.form-card {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
  margin-bottom: 2rem;
}

.form-group {
  margin-bottom: 1.5rem;
}

.form-group label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #495057;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 0.75rem;
  border: 1px solid #ced4da;
  border-radius: 4px;
  font-size: 1rem;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #42b983;
  box-shadow: 0 0 0 3px rgba(66, 185, 131, 0.1);
}

.form-actions {
  display: flex;
  gap: 1rem;
}

.btn {
  padding: 0.5rem 1rem;
  border-radius: 4px;
  border: none;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #42b983;
  color: white;
}

.btn-primary:hover {
  background-color: #3aa876;
}

.btn-secondary {
  background-color: #6c757d;
  color: white;
}

.btn-secondary:hover {
  background-color: #5a6268;
}

.btn-danger {
  background-color: #dc3545;
  color: white;
}

.btn-danger:hover {
  background-color: #c82333;
}

.btn-sm {
  padding: 0.25rem 0.5rem;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.items-list {
  margin-top: 2rem;
}

.loading,
.error,
.empty-state {
  text-align: center;
  padding: 3rem;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.error {
  color: #dc3545;
}

.grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 1.5rem;
}

.item-card {
  background-color: white;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s, box-shadow 0.2s;
}

.item-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.15);
}

.item-card h3 {
  margin: 0 0 0.5rem 0;
  color: #2c3e50;
}

.item-card p {
  color: #6c757d;
  margin: 0 0 1rem 0;
}

.item-meta {
  margin-bottom: 1rem;
}

.item-meta small {
  color: #adb5bd;
}

.item-actions {
  display: flex;
  gap: 0.5rem;
}
</style>