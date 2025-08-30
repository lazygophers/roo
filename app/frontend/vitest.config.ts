import { defineConfig } from 'vitest/config'
import vue from '@vitejs/plugin-vue'
import { resolve } from 'path'

export default defineConfig({
  plugins: [vue()],
  test: {
    // 启用类似 jest 的全局测试 API
    globals: true,
    // 模拟 DOM 环境
    environment: 'jsdom',
    // 支持 Vue 组件测试
    include: ['tests/**/*.{test,spec}.{js,ts,jsx,tsx}', 'src/**/*.{test,spec}.{js,ts,jsx,tsx}'],
    // 排除的文件
    exclude: ['node_modules/**', 'dist/**', '.idea/**', '.vscode/**', '.git/**'],
    // 别名配置
    alias: {
      '@': resolve(__dirname, './src'),
    },
    // 覆盖率配置
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      exclude: [
        'node_modules/**',
        'src/main.ts',
        'src/router/**',
        'src/stores/**',
        '**/*.d.ts',
        '**/*.config.{js,ts}',
        '**/index.ts',
      ],
      include: ['src/**/*.{js,ts,jsx,tsx,vue}'],
      thresholds: {
        global: {
          branches: 80,
          functions: 80,
          lines: 80,
          statements: 80,
        },
      },
    },
    // 设置超时时间
    timeout: 10000,
    // 在测试文件中使用 .vue 后缀
    includeSource: ['src/**/*.vue'],
  },
  resolve: {
    alias: {
      '@': resolve(__dirname, './src'),
    },
  },
})