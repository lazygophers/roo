<template>
  <!--
    HomeView.vue - 首页组件
    
    这是应用的首页，提供：
    1. 欢迎信息和项目介绍
    2. 主要功能的快速入口
    3. 项目特性展示
    4. 快速开始指南
  -->
  <div class="home-container">
    <!-- 欢迎区域 -->
    <section class="hero-section">
      <div class="hero-content">
        <h1 class="hero-title">
          <span class="gradient-text">Roo Code</span> 配置管理工具
        </h1>
        <p class="hero-subtitle">
          为您的 Roo Code 个性化定制完美的规则配置
        </p>
        <div class="hero-actions">
          <router-link to="/config" class="btn btn-primary">
            开始配置
            <i class="fas fa-arrow-right"></i>
          </router-link>
          <a href="https://github.com" target="_blank" class="btn btn-secondary">
            <i class="fab fa-github"></i>
            查看 GitHub
          </a>
        </div>
      </div>
    </section>

    <!-- 特性展示 -->
    <section class="features-section">
      <h2 class="section-title">核心特性</h2>
      <div class="features-grid">
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-magic"></i>
          </div>
          <h3>智能配置</h3>
          <p>自动扫描和索引所有规则文件，提供智能化的配置选择界面</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-layer-group"></i>
          </div>
          <h3>模块化管理</h3>
          <p>支持模式和规则的模块化管理，轻松组织您的配置结构</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-eye"></i>
          </div>
          <h3>实时预览</h3>
          <p>选择配置后可实时预览规则内容，确保配置符合预期</p>
        </div>
        <div class="feature-card">
          <div class="feature-icon">
            <i class="fas fa-download"></i>
          </div>
          <h3>一键导出</h3>
          <p>支持多种格式的配置导出，轻松应用到您的项目中</p>
        </div>
      </div>
    </section>

    <!-- 快速开始 -->
    <section class="quickstart-section">
      <h2 class="section-title">快速开始</h2>
      <div class="quickstart-steps">
        <div class="step">
          <div class="step-number">1</div>
          <div class="step-content">
            <h3>选择配置</h3>
            <p>在配置选择器中选择您需要的模式和规则</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">2</div>
          <div class="step-content">
            <h3>预览确认</h3>
            <p>实时预览所选规则的内容，确保配置正确</p>
          </div>
        </div>
        <div class="step">
          <div class="step-number">3</div>
          <div class="step-content">
            <h3>导出应用</h3>
            <p>一键导出配置文件，应用到您的 Roo Code 中</p>
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
/**
 * HomeView.vue - 首页组件
 * 
 * 这是应用的首页组件，展示项目的主要功能和特性。
 * 使用 Vue 3 的组合式 API 和 TypeScript。
 * 
 * @component
 */
</script>

<style scoped>
/* 首页容器样式 */
.home-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

/* 欢迎区域样式 */
.hero-section {
  text-align: center;
  padding: 4rem 0;
  background: linear-gradient(135deg, rgba(0, 212, 255, 0.1) 0%, rgba(124, 58, 237, 0.1) 100%);
  border-radius: 16px;
  margin-bottom: 4rem;
}

.hero-content {
  padding: 0 2rem;
}

.hero-title {
  font-size: 3rem;
  font-weight: 800;
  margin-bottom: 1rem;
  line-height: 1.2;
}

.gradient-text {
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.hero-subtitle {
  font-size: 1.25rem;
  color: var(--text-secondary);
  margin-bottom: 2rem;
}

.hero-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

/* 按钮样式 */
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

/* 章节标题样式 */
.section-title {
  font-size: 2rem;
  font-weight: 700;
  text-align: center;
  margin-bottom: 3rem;
  position: relative;
}

.section-title::after {
  content: '';
  position: absolute;
  bottom: -10px;
  left: 50%;
  transform: translateX(-50%);
  width: 60px;
  height: 4px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  border-radius: 2px;
}

/* 特性展示样式 */
.features-section {
  margin-bottom: 4rem;
}

.features-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 2rem;
}

.feature-card {
  background: var(--bg-card);
  backdrop-filter: blur(10px);
  -webkit-backdrop-filter: blur(10px);
  padding: 2rem;
  border-radius: 12px;
  border: 1px solid var(--border-color);
  text-align: center;
  transition: var(--transition-smooth);
}

.feature-card:hover {
  transform: translateY(-4px);
  border-color: var(--accent-primary);
  box-shadow: var(--shadow-glow);
}

.feature-icon {
  font-size: 2.5rem;
  color: var(--accent-primary);
  margin-bottom: 1rem;
}

.feature-card h3 {
  font-size: 1.25rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.feature-card p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 快速开始样式 */
.quickstart-section {
  margin-bottom: 4rem;
}

.quickstart-steps {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  gap: 2rem;
  flex-wrap: wrap;
}

.step {
  flex: 1;
  min-width: 250px;
  text-align: center;
  position: relative;
}

.step:not(:last-child)::after {
  content: '\f054';
  font-family: 'Font Awesome 5 Free';
  font-weight: 900;
  position: absolute;
  right: -1.5rem;
  top: 20px;
  color: var(--accent-primary);
  opacity: 0.5;
}

.step-number {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  color: white;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 700;
  font-size: 1.25rem;
  margin: 0 auto 1rem;
}

.step-content h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.step-content p {
  color: var(--text-secondary);
  line-height: 1.6;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .hero-title {
    font-size: 2rem;
  }
  
  .hero-actions {
    flex-direction: column;
    align-items: center;
  }
  
  .btn {
    width: 100%;
    max-width: 300px;
    justify-content: center;
  }
  
  .features-grid {
    grid-template-columns: 1fr;
  }
  
  .quickstart-steps {
    flex-direction: column;
  }
  
  .step:not(:last-child)::after {
    content: '';
    display: block;
    width: 2px;
    height: 30px;
    background: var(--border-color);
    position: absolute;
    bottom: -30px;
    left: 50%;
    transform: translateX(-50%);
    right: auto;
  }
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.feature-card {
  animation: fadeInUp 0.6s ease-out;
}

.feature-card:nth-child(1) { animation-delay: 0.1s; }
.feature-card:nth-child(2) { animation-delay: 0.2s; }
.feature-card:nth-child(3) { animation-delay: 0.3s; }
.feature-card:nth-child(4) { animation-delay: 0.4s; }

.step {
  animation: fadeInUp 0.6s ease-out;
}

.step:nth-child(1) { animation-delay: 0.1s; }
.step:nth-child(2) { animation-delay: 0.2s; }
.step:nth-child(3) { animation-delay: 0.3s; }
</style>