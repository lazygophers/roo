<template>
  <!--
    App.vue 模板部分 - 应用的整体布局结构
    
    采用经典的页面布局模式：
    - 顶部导航栏：包含网站Logo和主导航链接
    - 主内容区域：使用 router-view 动态渲染当前路由对应的页面组件
    - 底部页脚：显示版权信息
  -->
  <div id="app">
    <!--
      顶部导航栏
      - 使用 sticky 定位，滚动时固定在顶部
      - 包含品牌Logo和主导航链接
      - 支持响应式设计
    -->
    <nav class="navbar">
      <!-- 导航栏左侧品牌区域 -->
      <div class="nav-brand">
        <!--
          网站Logo链接
          - 点击返回首页（"/"）
          - 使用渐变色文字效果增强视觉吸引力
        -->
        <router-link to="/">Roo Code 配置管理工具</router-link>
      </div>
      <!-- 导航链接区域 -->
      <div class="nav-links">
        <!--
          主导航菜单
          - 首页：返回网站主页
          - 配置选择器：进入配置管理页面
          - router-link-active 类会自动添加到当前活动链接
        -->
        <router-link to="/">首页</router-link>
        <router-link to="/config">配置选择器</router-link>
      </div>
    </nav>
    
    <!--
      主内容区域
      - 使用 flex-grow 占据剩余空间
      - 设置最大宽度和居中对齐，优化大屏幕显示效果
      - router-view 是 Vue Router 的路由出口组件
        * 根据当前路由动态渲染对应的页面组件
        * 支持路由过渡动画和嵌套路由
    -->
    <main class="main-content">
      <router-view />
    </main>
    
    <!--
      页面底部
      - 包含版权信息
      - 使用半透明背景与整体设计风格保持一致
    -->
    <footer class="footer">
      <p>&copy; 2025 Roo Code 配置管理工具</p>
    </footer>
  </div>
</template>

<script setup lang="ts">
/**
 * App.vue - 应用程序的根组件
 *
 * 这是整个 Vue 应用的最顶层组件，使用 Vue 3 的组合式 API（Composition API）
 * 和 TypeScript 进行开发，作为所有页面的容器组件。
 *
 * 主要职责：
 * 1. 定义应用的整体布局结构（导航栏、主内容区、页脚）
 * 2. 设置全局样式和主题变量，统一应用的视觉风格
 * 3. 提供路由出口（router-view），渲染当前路由对应的页面组件
 * 4. 作为全局状态的入口点，管理应用级别的数据和逻辑
 *
 * 技术特点：
 * - 使用 <script setup> 语法，这是 Vue 3 推荐的组合式 API 写法
 * - 使用 TypeScript 提供类型安全，减少运行时错误
 * - 无需额外配置即可使用全局组件和指令
 *
 * @author 开发团队
 * @since 2024
 */
</script>

<style>
/**
 * 全局样式定义
 *
 * 这里定义了应用的全局样式，包括：
 * 1. CSS变量系统 - 定义主题色彩和设计token
 * 2. 全局基础样式 - 重置和标准化
 * 3. 组件样式 - 导航栏、主内容区、页脚等
 * 4. 滚动条自定义 - 美化滚动条外观
 * 5. 动画效果 - 定义关键帧动画
 */

/* CSS变量（CSS Custom Properties）定义 */
/*
 * 这里定义了整个应用的设计系统变量，包括：
 * - 颜色变量：主色调、辅助色、中性色等
 * - 阴影变量：不同层级的阴影效果
 * - 过渡变量：统一的动画时间曲线
 *
 * 使用CSS变量的好处：
 * 1. 便于主题切换和动态修改
 * 2. 保持设计一致性
 * 3. 减少重复代码
 */
:root {
  /* 背景色系 - 深色主题 */
  --bg-primary: #0a0e1a;           /* 主背景色 - 深蓝黑色 */
  --bg-secondary: rgba(20, 25, 40, 0.7);  /* 次要背景色 - 半透明深蓝 */
  --bg-card: rgba(30, 35, 55, 0.6);     /* 卡片背景色 - 半透明灰蓝 */
  
  /* 文本色系 */
  --text-primary: #e0e6ed;         /* 主要文字颜色 - 浅灰白 */
  --text-secondary: #8892b0;       /* 次要文字颜色 - 中灰色 */
  
  /* 强调色系 */
  --accent-primary: #00d4ff;       /* 主要强调色 - 青蓝色 */
  --accent-secondary: #7c3aed;     /* 次要强调色 - 紫色 */
  --accent-success: #10b981;       /* 成功色 - 绿色 */
  
  /* 边框和装饰 */
  --border-color: rgba(0, 212, 255, 0.3);  /* 边框颜色 - 半透明青蓝 */
  
  /* 阴影系统 */
  --shadow-glow: 0 0 20px rgba(0, 212, 255, 0.3);  /* 发光效果 - 用于强调 */
  --shadow-card: 0 8px 32px rgba(0, 0, 0, 0.3);    /* 卡片阴影 - 深度感 */
  
  /* 动画系统 */
  --transition-smooth: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);  /* 平滑过渡 - 贝塞尔曲线 */
}

/* 全局盒子模型重置 */
/*
 * box-sizing: border-box 是现代CSS开发的最佳实践
 * - 宽度和高度包含内边距和边框
 * - 避免布局计算错误
 * - 更直观的尺寸控制
 */
* {
  box-sizing: border-box;
}

/* 页面基础样式 */
body {
  /* 使用CSS变量设置背景和文字颜色 */
  background: var(--bg-primary);        /* 深色背景 */
  color: var(--text-primary);          /* 浅色文字 */
  
  /* 字体栈设置 - 优雅降级 */
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  line-height: 1.6;                   /* 舒适的行高 */
  
  /* 字体渲染优化 */
  -webkit-font-smoothing: antialiased;  /* WebKit浏览器抗锯齿 */
  -moz-osx-font-smoothing: grayscale;   /* Firefox灰度渲染 */
}

#app {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background:
    radial-gradient(circle at 20% 50%, rgba(0, 212, 255, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 80% 80%, rgba(124, 58, 237, 0.1) 0%, transparent 50%),
    radial-gradient(circle at 40% 20%, rgba(16, 185, 129, 0.05) 0%, transparent 50%),
    var(--bg-primary);
  background-attachment: fixed;
}

/* 导航栏样式 */
.navbar {
  background: var(--bg-secondary);          /* 使用次要背景色，半透明效果 */
  backdrop-filter: blur(20px);               /* 背景模糊效果，创建毛玻璃质感 */
  -webkit-backdrop-filter: blur(20px);      /* WebKit浏览器兼容性前缀 */
  padding: 1rem 2rem;                       /* 内边距：上下1rem，左右2rem */
  display: flex;                            /* 使用Flexbox布局 */
  justify-content: space-between;          /* 两端对齐：品牌在左，链接在右 */
  align-items: center;                     /* 垂直居中对齐 */
  border-bottom: 1px solid var(--border-color);  /* 底部边框，使用定义的边框色 */
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.4); /* 深度阴影，增强层次感 */
  position: sticky;                        /* 粘性定位 */
  top: 0;                                   /* 固定在顶部 */
  z-index: 100;                             /* 确保导航栏在最上层 */
}

/* 导航品牌Logo样式 */
.nav-brand a {
  color: var(--text-primary);              /* 使用主要文字颜色 */
  font-size: 1.5rem;                       /* 较大的字体尺寸，突出品牌 */
  font-weight: 700;                       /* 粗体字重，增强视觉重量 */
  text-decoration: none;                   /* 移除默认的下划线 */
  /* 创建渐变文字效果 */
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  -webkit-background-clip: text;          /* WebKit：将背景裁剪到文字形状 */
  -webkit-text-fill-color: transparent;   /* WebKit：文字填充透明，显示背景 */
  background-clip: text;                  /* 标准：背景裁剪到文字 */
  transition: var(--transition-smooth);   /* 应用平滑过渡效果 */
}

/* Logo悬停效果 */
.nav-brand a:hover {
  filter: brightness(1.2);               /* 增加亮度，创造发光效果 */
}

/* 导航链接容器 */
.nav-links {
  display: flex;                            /* Flexbox布局，水平排列链接 */
  gap: 2rem;                               /* 链接之间的间距 */
}

/* 导航链接样式 */
.nav-links a {
  color: var(--text-secondary);            /* 默认使用次要文字颜色 */
  text-decoration: none;                   /* 移除下划线 */
  font-weight: 500;                       /* 中等字重 */
  padding: 0.5rem 1rem;                   /* 内边距，增大点击区域 */
  border-radius: 8px;                     /* 圆角边框 */
  transition: var(--transition-smooth);   /* 平滑过渡效果 */
  position: relative;                     /* 相对定位，为伪元素定位做准备 */
  overflow: hidden;                       /* 隐藏溢出，用于背景效果 */
}

/* 导航链接背景效果 - 使用伪元素创建渐变背景 */
.nav-links a::before {
  content: '';                             /* 必须设置content属性 */
  position: absolute;                     /* 绝对定位 */
  top: 0;                                 /* 从顶部开始 */
  left: 0;                                /* 从左侧开始 */
  width: 100%;                            /* 宽度100%覆盖父元素 */
  height: 100%;                           /* 高度100%覆盖父元素 */
  background: linear-gradient(135deg, var(--accent-primary), var(--accent-secondary));
  opacity: 0;                             /* 默认透明不可见 */
  transition: opacity 0.3s;               /* 背景透明度过渡 */
  z-index: -1;                            /* 置于文字下方 */
}

/* 导航链接悬停效果 */
.nav-links a:hover {
  color: var(--text-primary);              /* 悬停时显示主要文字颜色 */
  transform: translateY(-2px);            /* 轻微上移，增强交互感 */
}

/* 显示背景效果 - 悬停或活动状态时 */
.nav-links a:hover::before,
.nav-links a.router-link-active::before {
  opacity: 0.2;                           /* 半透明背景效果 */
}

/* 当前活动路由链接样式 */
.nav-links a.router-link-active {
  color: var(--accent-primary);            /* 使用强调色标识当前页面 */
  font-weight: 600;                       /* 加粗字重，增强视觉提示 */
}

/* 主内容区域样式 */
.main-content {
  flex: 1;                                 /* 占据所有可用空间，将页脚推到底部 */
  padding: 2rem;                           /* 内边距，提供内容呼吸空间 */
  max-width: 1400px;                       /* 最大宽度，避免在大屏幕上过宽 */
  margin: 0 auto;                          /* 水平居中 */
  width: 100%;                             /* 确保在小屏幕上占满宽度 */
}

/* 页脚样式 */
.footer {
  background: var(--bg-secondary);          /* 使用次要背景色，与导航栏保持一致 */
  backdrop-filter: blur(10px);               /* 背景模糊效果 */
  -webkit-backdrop-filter: blur(10px);      /* WebKit兼容性 */
  padding: 1.5rem;                         /* 内边距 */
  text-align: center;                      /* 文字居中对齐 */
  border-top: 1px solid var(--border-color);  /* 顶部边框，与导航栏呼应 */
  color: var(--text-secondary);            /* 使用次要文字颜色 */
}

/* 自定义滚动条样式 */
::-webkit-scrollbar {
  width: 8px;                              /* 垂直滚动条宽度 */
  height: 8px;                             /* 水平滚动条高度 */
}

/* 滚动条轨道样式 */
::-webkit-scrollbar-track {
  background: rgba(255, 255, 255, 0.05);   /* 半透明背景 */
  border-radius: 4px;                     /* 圆角边框 */
}

/* 滚动条滑块样式 */
::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.2);   /* 半透明滑块 */
  border-radius: 4px;                     /* 圆角边框 */
  transition: background 0.3s;             /* 背景色过渡效果 */
}

/* 滚动条滑块悬停效果 */
::-webkit-scrollbar-thumb:hover {
  background: rgba(255, 255, 255, 0.3);   /* 悬停时变得更明显 */
}

/* 淡入动画关键帧定义 */
@keyframes fadeIn {
  from {
    opacity: 0;                            /* 初始透明 */
    transform: translateY(20px);           /* 初始位置向下偏移 */
  }
  to {
    opacity: 1;                            /* 最终完全不透明 */
    transform: translateY(0);             /* 最终位置回到原位 */
  }
}

/* 淡入动画类 */
.fade-in {
  animation: fadeIn 0.6s ease-out;        /* 应用淡入动画，持续0.6秒，缓出效果 */
}
</style>