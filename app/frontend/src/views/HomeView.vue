<template>
  <div class="home">
    <div class="container">
      <h1>API 演示</h1>
      <p class="description">输入内容并发送到后端，查看返回结果</p>
      
      <div class="demo-form">
        <div class="input-group">
          <input
            v-model="inputText"
            type="text"
            placeholder="请输入要发送的内容..."
            @keyup.enter="sendToBackend"
            :disabled="loading"
          />
          <button
            @click="sendToBackend"
            :disabled="loading || !inputText.trim()"
            class="send-btn"
          >
            {{ loading ? '发送中...' : '发送' }}
          </button>
        </div>
        
        <div v-if="responseMessage" class="response-box">
          <h3>后端响应：</h3>
          <div class="response-content">
            {{ responseMessage }}
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import api from '@/api'

const inputText = ref('')
const responseMessage = ref('')
const loading = ref(false)

const sendToBackend = async () => {
  if (!inputText.value.trim()) return
  
  loading.value = true
  try {
    const response = await api.post('/api/hello', {
      message: inputText.value
    })
    responseMessage.value = response.message || `收到消息: ${inputText.value}`
  } catch (error) {
    console.error('API 调用失败:', error)
    responseMessage.value = 'API 调用失败，请确保后端服务正在运行'
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.home {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
}

.container {
  background: white;
  padding: 3rem;
  border-radius: 16px;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
  max-width: 600px;
  width: 100%;
  text-align: center;
}

h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.description {
  color: #7f8c8d;
  font-size: 1.1rem;
  margin-bottom: 2rem;
}

.demo-form {
  margin-top: 2rem;
}

.input-group {
  display: flex;
  gap: 1rem;
  margin-bottom: 2rem;
}

input {
  flex: 1;
  padding: 0.75rem 1rem;
  border: 2px solid #e0e0e0;
  border-radius: 8px;
  font-size: 1rem;
  transition: border-color 0.3s;
}

input:focus {
  outline: none;
  border-color: #42b983;
}

input:disabled {
  background-color: #f5f5f5;
  cursor: not-allowed;
}

.send-btn {
  padding: 0.75rem 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 1rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
  position: relative;
  overflow: hidden;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
  background: linear-gradient(135deg, #5a67d8 0%, #6b46c1 100%);
}

.send-btn:active:not(:disabled) {
  transform: translateY(0);
  box-shadow: 0 2px 10px rgba(102, 126, 234, 0.4);
}

.send-btn:disabled {
  background: linear-gradient(135deg, #9ca3af 0%, #6b7280 100%);
  cursor: not-allowed;
  box-shadow: none;
  opacity: 0.7;
}

.send-btn::before {
  content: '';
  position: absolute;
  top: 0;
  left: -100%;
  width: 100%;
  height: 100%;
  background: linear-gradient(90deg, transparent, rgba(255, 255, 255, 0.2), transparent);
  transition: left 0.5s;
}

.send-btn:hover:not(:disabled)::before {
  left: 100%;
}

.response-box {
  background-color: #f8f9fa;
  border-radius: 8px;
  padding: 1.5rem;
  text-align: left;
  border: 1px solid #e9ecef;
}

.response-box h3 {
  color: #2c3e50;
  margin-top: 0;
  margin-bottom: 1rem;
  font-size: 1.1rem;
}

.response-content {
  color: #34495e;
  font-size: 1rem;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}
</style>