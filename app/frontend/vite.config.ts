import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [react()],
  
  // 路径解析配置
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@/components': path.resolve(__dirname, './src/components'),
      '@/pages': path.resolve(__dirname, './src/pages'),
      '@/services': path.resolve(__dirname, './src/services'),
      '@/types': path.resolve(__dirname, './src/types'),
      '@/utils': path.resolve(__dirname, './src/utils'),
      '@/hooks': path.resolve(__dirname, './src/hooks'),
      '@/styles': path.resolve(__dirname, './src/styles'),
    },
  },

  // 开发服务器配置
  server: {
    port: 3005,
    host: true, // 允许外部访问
    open: true, // 自动打开浏览器
    cors: true, // 启用 CORS
    proxy: {
      // 代理后端 API 请求
      '/api': {
        target: 'http://localhost:14001',
        changeOrigin: true,
        secure: false,
      },
    },
  },

  // 构建配置
  build: {
    outDir: 'dist',
    sourcemap: true, // 生产环境也生成 sourcemap
    minify: 'terser',
    terserOptions: {
      compress: {
        drop_console: true, // 生产环境移除 console
        drop_debugger: true, // 生产环境移除 debugger
      },
    },
    rollupOptions: {
      output: {
        // 代码分割策略
        manualChunks: {
          'react-vendor': ['react', 'react-dom'],
          'antd-vendor': ['antd'],
          'router-vendor': ['react-router-dom'],
          'utils': ['axios', 'dayjs'],
        },
        // 文件命名规范
        chunkFileNames: 'assets/js/[name]-[hash].js',
        entryFileNames: 'assets/js/[name]-[hash].js',
        assetFileNames: 'assets/[ext]/[name]-[hash].[ext]',
      },
    },
    // 构建性能预算
    chunkSizeWarningLimit: 1000, // 1MB 警告
  },

  // CSS 配置
  css: {
    modules: {
      // CSS Modules 配置
      localsConvention: 'camelCase',
      generateScopedName: '[name]_[local]_[hash:base64:5]',
    },
    preprocessorOptions: {
      less: {
        // Ant Design 主题定制
        javascriptEnabled: true,
        additionalData: `@import "@/styles/variables.less";`,
      },
    },
    devSourcemap: true, // 开发环境生成 CSS sourcemap
  },

  // 环境变量配置
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version),
    __BUILD_TIME__: JSON.stringify(new Date().toISOString()),
  },

  // 预览服务器配置（用于本地预览构建后的应用）
  preview: {
    port: 3006,
    host: true,
    open: true,
  },

  // 依赖优化
  optimizeDeps: {
    include: [
      'react',
      'react-dom',
      'antd',
      'react-router-dom',
      'axios',
      'dayjs',
    ],
    exclude: ['@vitejs/plugin-react'],
  },

  // ESBuild 配置
  esbuild: {
    // 移除生产环境的调试信息
    drop: process.env.NODE_ENV === 'production' ? ['console', 'debugger'] : [],
  },
})