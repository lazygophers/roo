<template>
  <div class="about-view">
    <div class="hero">
      <h1>关于本项目</h1>
      <p class="subtitle">一个现代化的 FastAPI + Vue3 全栈开发示例</p>
    </div>

    <div class="content">
      <section class="section">
        <h2>项目简介</h2>
        <p>
          本项目是一个使用 FastAPI 和 Vue3 构建的全栈应用示例。
          展示了如何使用现代化的技术栈来构建高性能、类型安全的 Web 应用程序。
        </p>
      </section>

      <section class="section">
        <h2>技术栈详情</h2>
        <div class="tech-stack">
          <div class="tech-category">
            <h3>后端技术</h3>
            <ul>
              <li><strong>FastAPI</strong> - 现代化的 Python Web 框架</li>
              <li><strong>Python 3.9+</strong> - 高级编程语言</li>
              <li><strong>Pydantic</strong> - 数据验证和序列化</li>
              <li><strong>Uvicorn</strong> - ASGI 服务器</li>
              <li><strong>Type Hints</strong> - 类型提示支持</li>
            </ul>
          </div>

          <div class="tech-category">
            <h3>前端技术</h3>
            <ul>
              <li><strong>Vue 3</strong> - 渐进式 JavaScript 框架</li>
              <li><strong>TypeScript</strong> - JavaScript 的超集，提供静态类型检查</li>
              <li><strong>Vite</strong> - 下一代前端构建工具</li>
              <li><strong>Vue Router</strong> - 官方路由管理器</li>
              <li><strong>Pinia</strong> - 状态管理库</li>
              <li><strong>Axios</strong> - HTTP 客户端</li>
            </ul>
          </div>

          <div class="tech-category">
            <h3>开发工具</h3>
            <ul>
              <li><strong>UV</strong> - Python 包管理器</li>
              <li><strong>ESLint</strong> - JavaScript 代码检查工具</li>
              <li><strong>Prettier</strong> - 代码格式化工具</li>
              <li><strong>Git</strong> - 版本控制系统</li>
            </ul>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>项目特性</h2>
        <div class="features">
          <div class="feature">
            <h3>🚀 高性能</h3>
            <p>基于 FastAPI 的异步支持和高性能特性</p>
          </div>
          <div class="feature">
            <h3>🔒 类型安全</h3>
            <p>全程使用 TypeScript 和 Python 类型提示</p>
          </div>
          <div class="feature">
            <h3>📚 自动文档</h3>
            <p>FastAPI 自动生成交互式 API 文档</p>
          </div>
          <div class="feature">
            <h3>🎨 现代化 UI</h3>
            <p>使用 Vue 3 组合式 API 和响应式设计</p>
          </div>
          <div class="feature">
            <h3>⚡ 热重载</h3>
            <p>开发时支持前端和后端的热重载</p>
          </div>
          <div class="feature">
            <h3>🧪 测试支持</h3>
            <p>完整的单元测试和集成测试支持</p>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>快速开始</h2>
        <div class="getting-started">
          <div class="step">
            <h3>1. 克隆项目</h3>
            <pre><code>git clone &lt;repository-url&gt;
cd fastapi-vue3-example</code></pre>
          </div>

          <div class="step">
            <h3>2. 启动后端</h3>
            <pre><code>cd app
uv sync
uv run uvicorn main:app --reload</code></pre>
          </div>

          <div class="step">
            <h3>3. 启动前端</h3>
            <pre><code>cd frontend
npm install
npm run dev</code></pre>
          </div>

          <div class="step">
            <h3>4. 访问应用</h3>
            <p>打开浏览器访问 <a href="http://localhost:5173" target="_blank">http://localhost:5173</a></p>
            <p>API 文档: <a href="http://localhost:8001/docs" target="_blank">http://localhost:8001/docs</a></p>
          </div>
        </div>
      </section>

      <section class="section">
        <h2>项目结构</h2>
        <pre><code>app/
├── main.py              # FastAPI 应用入口
├── api/
│   ├── __init__.py
│   └── routes.py         # API 路由
├── static/               # 静态文件
└── frontend/            # 前端应用
    ├── src/
    │   ├── components/  # Vue 组件
    │   ├── views/       # 页面视图
    │   ├── stores/      # Pinia 状态管理
    │   ├── types/       # TypeScript 类型定义
    │   ├── utils/       # 工具函数
    │   ├── App.vue      # 根组件
    │   └── main.ts     # 应用入口
    ├── package.json
    ├── vite.config.ts
    └── tsconfig.json</code></pre>
      </section>

      <section class="section">
        <h2>贡献</h2>
        <p>
          欢迎提交 Issue 和 Pull Request 来改进这个项目。
          在提交之前，请确保代码符合项目的编码规范，并且所有测试都通过。
        </p>
      </section>

      <section class="section">
        <h2>许可证</h2>
        <p>
          本项目采用 MIT 许可证。详情请参阅 <a href="#">LICENSE</a> 文件。
        </p>
      </section>
    </div>
  </div>
</template>

<script setup lang="ts">
// About 组件
</script>

<style scoped>
.about-view {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.hero {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  margin-bottom: 3rem;
}

.hero h1 {
  font-size: 3rem;
  margin-bottom: 1rem;
}

.subtitle {
  font-size: 1.5rem;
  opacity: 0.9;
}

.content {
  display: flex;
  flex-direction: column;
  gap: 3rem;
}

.section {
  background-color: #f8f9fa;
  padding: 2rem;
  border-radius: 8px;
}

.section h2 {
  color: #2c3e50;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #42b983;
}

.tech-stack {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 2rem;
}

.tech-category h3 {
  color: #42b983;
  margin-bottom: 1rem;
}

.tech-category ul {
  list-style: none;
  padding: 0;
}

.tech-category li {
  padding: 0.5rem 0;
  border-bottom: 1px solid #e9ecef;
}

.tech-category li:last-child {
  border-bottom: none;
}

.features {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1.5rem;
}

.feature {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  text-align: center;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  transition: transform 0.2s;
}

.feature:hover {
  transform: translateY(-2px);
}

.feature h3 {
  margin-bottom: 0.5rem;
  color: #2c3e50;
}

.getting-started {
  display: grid;
  gap: 1.5rem;
}

.step {
  background-color: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.step h3 {
  color: #42b983;
  margin-bottom: 1rem;
}

.step pre {
  background-color: #2d3748;
  color: #e2e8f0;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin: 0;
}

.step code {
  font-family: 'Fira Code', 'Monaco', 'Consolas', monospace;
  font-size: 0.9rem;
}

.step p {
  margin: 0.5rem 0 0 0;
}

.step a {
  color: #42b983;
  text-decoration: none;
}

.step a:hover {
  text-decoration: underline;
}

section:last-child pre {
  background-color: #f8f9fa;
  padding: 1.5rem;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  overflow-x: auto;
}

section:last-child code {
  color: #2d3748;
}
</style>