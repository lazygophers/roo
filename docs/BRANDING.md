# LazyAI Studio 品牌指南

## 概述

LazyAI Studio 是由 LazyGophers 组织出品的 AI 智能工作室，专为懒人开发者设计的综合性 AI 开发解决方案。本文档定义了品牌的视觉识别系统、设计原则和使用规范。

## 品牌理念

### 核心价值
- **高效智能**: 通过 AI 技术简化复杂的开发工作
- **懒人友好**: 为追求效率的开发者提供便捷工具
- **开放包容**: 支持多种技术栈和开发场景
- **创新驱动**: 持续探索和应用最新的 AI 技术

### 品牌定位
面向现代开发者的智能工作室，让复杂的开发工作变得简单高效。

## 视觉识别系统

### 品牌标识 (Logo)

#### 主标识
- **文件**: `frontend/public/icon.svg`
- **设计元素**:
  - 圆形外框象征完整性和包容性
  - 内部几何图形代表 AI 的逻辑性和精确性
  - 渐变色彩体现创新和活力

#### 标识变体
- **完整版**: LazyAI + Studio 组合标识
- **简化版**: 仅 LazyAI 文字标识
- **图标版**: 纯图形标识

#### 尺寸规范
- 最小使用尺寸: 16px × 16px
- 标准尺寸: 32px × 32px
- 大尺寸应用: 可按比例放大至任意尺寸

### 色彩系统

#### 主色调
```css
/* 主蓝色 - 代表专业和可靠 */
#1890ff

/* 辅助绿色 - 代表成长和活力 */
#52c41a
```

#### 渐变色彩
```css
/* 主渐变 - 用于品牌标识 */
background: linear-gradient(135deg, #1890ff 0%, #52c41a 100%);

/* 动态渐变 - 用于交互效果 */
background: linear-gradient(
  135deg,
  #1890ff 0%,
  #36cfc9 25%,
  #52c41a 50%,
  #fadb14 75%,
  #ff7a45 100%
);
```

#### 扩展色板
- **中性色**: `#f0f2f5` (浅灰), `#8c8c8c` (中灰), `#262626` (深灰)
- **功能色**: `#f5222d` (错误), `#fa8c16` (警告), `#1890ff` (信息), `#52c41a` (成功)

### 字体系统

#### 中文字体
```css
font-family:
  'PingFang SC',
  'Hiragino Sans GB',
  'Microsoft YaHei',
  '微软雅黑',
  'Arial',
  sans-serif;
```

#### 英文字体
```css
font-family:
  'Inter',
  'SF Pro Display',
  'Segoe UI',
  'Roboto',
  system-ui,
  sans-serif;
```

#### 代码字体
```css
font-family:
  'JetBrains Mono',
  'Fira Code',
  'SF Mono',
  'Monaco',
  'Consolas',
  monospace;
```

### 图标系统

#### 设计原则
- **一致性**: 统一的视觉风格和比例
- **清晰性**: 在小尺寸下依然清晰可读
- **现代感**: 简洁的线条和几何形状

#### 图标类型
- **轮廓图标**: 用于导航和功能按钮
- **填充图标**: 用于状态指示和重要操作
- **品牌图标**: 用于标识和装饰

### 表情符号分类系统

LazyAI Studio 使用表情符号对不同技术栈和功能进行分类：

#### 编程语言
- 🐍 Python
- 🐹 Go (Golang)
- ☕ Java
- 🟨 JavaScript
- 💙 TypeScript
- 💎 Ruby
- 🦀 Rust
- ⚡ C/C++
- 🔷 C#
- 🐘 PHP

#### 前端技术
- ⚛️ React
- 💚 Vue.js
- 🅰️ Angular
- ⚡ Svelte
- 🎨 CSS/Styling
- 📦 Webpack
- ⚡ Vite

#### 后端技术
- 🚀 API/Server
- 🗄️ Database
- 🐳 Docker
- ☁️ Cloud
- 🔧 DevOps
- 📊 Analytics

#### AI/ML 技术
- 🧠 AI/Machine Learning
- 🤖 Automation
- 🔮 Prediction
- 📈 Data Science
- 🎯 Optimization

## 应用规范

### 标识使用

#### 正确使用
- 保持标识的完整性，不要拉伸或变形
- 确保足够的留白空间
- 在深色背景上使用浅色版本
- 在浅色背景上使用深色版本

#### 禁止使用
- 改变标识的颜色（除非是单色应用）
- 添加阴影或特效
- 旋转或倾斜标识
- 与其他元素重叠

### 网页应用

#### 导航栏
```tsx
// 标准导航栏标识
<div className="nav-logo">
  <img src="/icon-32.png" alt="LazyAI Studio" />
  <span className="brand-text">LazyAI</span>
  <span className="brand-subtitle">Studio</span>
</div>
```

#### 页面标题
```tsx
// 页面头部标识
<h1>
  <span className="gradient-text">LazyAI Studio</span>
  <span className="subtitle">AI 智能工作室</span>
</h1>
```

### CSS 样式规范

#### 渐变文字效果
```css
.gradient-text {
  background: linear-gradient(135deg, #1890ff 0%, #52c41a 100%);
  background-clip: text;
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-size: 200% 200%;
  animation: gradient-shift 3s ease-in-out infinite;
}

@keyframes gradient-shift {
  0%, 100% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
}
```

#### 悬停效果
```css
.brand-hover {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.brand-hover:hover {
  transform: translateY(-2px);
  filter: brightness(1.1);
}
```

### 多主题适配

LazyAI Studio 支持 9 种内置主题，品牌元素需要在所有主题下保持一致性：

#### 主题列表
1. 默认主题 (Default)
2. 暗黑主题 (Dark)
3. 紧凑主题 (Compact)
4. 宽松主题 (Comfortable)
5. 蓝色主题 (Blue)
6. 绿色主题 (Green)
7. 紫色主题 (Purple)
8. 红色主题 (Red)
9. 金色主题 (Gold)

#### 适配原则
- 品牌标识在所有主题下保持相同的视觉效果
- 渐变色彩可根据主题进行微调
- 文字颜色需要确保在不同背景下的可读性

## 文档和内容

### 语言风格
- **简洁明了**: 使用简短、清晰的句子
- **技术专业**: 准确使用技术术语
- **友好亲切**: 保持轻松、友好的语调
- **中英结合**: 中文为主，适当使用英文术语

### 文档结构
- **清晰的层级**: 使用标准的 Markdown 标题结构
- **代码示例**: 提供完整、可执行的代码示例
- **视觉辅助**: 使用表格、列表和代码块增强可读性

## 品牌扩展

### 社交媒体
- GitHub: 使用标准 logo 和品牌色彩
- 文档网站: 保持一致的视觉风格
- 开源社区: 遵循品牌指南进行宣传

### 合作伙伴
- 在合作项目中正确使用 LazyAI Studio 标识
- 保持品牌形象的一致性和专业性
- 遵循开源协议和使用条款

## 版权和使用许可

LazyAI Studio 品牌标识和相关设计元素受版权保护。在使用时请遵循以下原则：

- **开源项目**: 可在开源项目中使用，需注明出处
- **商业用途**: 需要获得明确的书面许可
- **修改**: 不得擅自修改或创建衍生版本
- **误用**: 不得以可能损害品牌形象的方式使用

## 联系方式

如有品牌使用相关问题，请通过以下方式联系：

- **GitHub Issues**: https://github.com/lazygophers/roo/issues
- **项目主页**: LazyGophers 组织页面
- **开源社区**: 参与项目讨论和贡献

---

本品牌指南会根据项目发展和社区反馈进行更新。最新版本请参考项目文档。