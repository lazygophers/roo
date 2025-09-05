# Roo Code Rules Configuration Tool - Frontend

这是一个基于React 18 + TypeScript + Vite的现代化前端应用，用于管理和配置Roo Code规则系统。

## 🚀 技术栈

- **前端框架**: React 18 + TypeScript
- **构建工具**: Vite
- **UI组件库**: Ant Design 5.x
- **状态管理**: React Hooks + Context API
- **路由管理**: React Router 6
- **样式方案**: CSS Modules + CSS变量
- **代码规范**: ESLint + Prettier
- **类型检查**: 严格TypeScript模式

## 🎯 核心功能

- **规则管理**: 动态配置和管理Roo Code规则
- **实时预览**: 选择配置后可预览完整规则内容
- **配置导出**: 支持导出完整的配置文件
- **主题切换**: 支持亮色/暗色主题切换
- **响应式设计**: 完整的移动端适配
- **无障碍访问**: WCAG 2.1 AA标准支持

## 📁 项目结构

```
app/frontend/
├── src/
│   ├── components/          # React组件
│   │   ├── Layout/         # 布局组件
│   │   ├── Router/         # 路由组件
│   │   └── pages/          # 页面组件
│   ├── contexts/          # React Context
│   ├── hooks/            # 自定义Hooks
│   ├── services/         # API服务层
│   ├── types/            # TypeScript类型定义
│   ├── utils/            # 工具函数
│   ├── styles/           # 样式文件
│   │   ├── themes/        # 主题相关样式
│   │   ├── variables.css   # CSS变量
│   │   ├── global.css     # 全局样式
│   │   └── mixins.css     # CSS混合器
│   ├── assets/           # 静态资源
│   │   ├── images/        # 图片资源
│   │   └── fonts/         # 字体资源
│   ├── App.tsx           # 应用根组件
│   └── main.tsx          # 应用入口文件
├── public/                 # 公共资源
├── package.json           # 项目配置
├── tsconfig.json          # TypeScript配置
├── vite.config.ts         # Vite构建配置
├── .eslintrc.json         # ESLint配置
├── .prettierrc.json       # Prettier配置
└── README.md              # 项目说明
```

## 🛠️ 开发环境要求

### 系统要求
- Node.js >= 18.0.0
- Yarn >= 1.22.0
- npm >= 9.0.0

### 依赖安装
```bash
# 安装依赖
yarn install

# 启动开发服务器
yarn dev

# 构建生产版本
yarn build

# 代码格式化
yarn format

# 类型检查
yarn type-check
```

### 开发服务器
- 前端服务: http://localhost:3005
- 后端API: http://localhost:14001/api
- 支持热重载和代理配置

## 🎨 设计系统

### 颜色系统
- **主色调**: #1890ff (亮色) / #40a9ff (暗色)
- **次要色调**: #52c41a
- **中性色系**: 完整的灰度色阶
- **语义化颜色**: 成功、警告、错误、信息等

### 字体系统
- **主字体**: Inter, -apple-system, BlinkMacSystemFont
- **代码字体**: 'Fira Code', 'Consolas', 'Monaco'
- **字号系统**: 12px - 64px，基于rem单位
- **行高系统**: 1.2 - 2.0

### 间距系统
- **基础单位**: 4px (0.25rem)
- **间距层级**: 0, 4, 8, 12, 16, 20, 24, 32, 48, 64px
- **响应式断点**: sm (640px), md (768px), lg (1024px), xl (1280px), 2xl (1536px)

### 阴影系统
- **层级**: 0-5级阴影效果
- **颜色**: 自然阴影，支持主题切换
- **模糊度**: 从2px到32px的渐变效果

### 动画系统
- **持续时间**: 150ms, 200ms, 300ms
- **缓动函数**: ease-in-out, ease-out, cubic-bezier
- **性能优化**: GPU加速，will-change属性

## 📱 响应式设计

### 断点策略
- **移动优先**: 基于移动设备设计
- **渐进增强**: 平板和桌面设备增强
- **完整覆盖**: 从320px到2560px+

### 布局系统
- **Flexbox**: 一维布局和组件对齐
- **Grid**: 复杂页面布局
- **CSS自定义属性**: 现代布局特性

### 触摸优化
- **触摸目标**: 最小44x44px
- **交互反馈**: 视觉和触觉反馈
- **手势支持**: 滑动、缩放、旋转等

## 🌓 主题系统

### 亮色主题
```css
:root {
  --color-primary: #1890ff;
  --color-background: #ffffff;
  --color-text: #262626;
  --color-border: #d9d9d9;
}
```

### 暗色主题
```css
[data-theme="dark"] {
  --color-primary: #40a9ff;
  --color-background: #1f1f1f;
  --color-text: #ffffff;
  --color-border: #434343;
}
```

### 主题切换
- 自动检测系统主题偏好
- 手动切换主题
- 支持高对比度模式
- 减少动画偏好支持

## ♿ 无障碍访问

### 键盘导航
- 完整的键盘导航支持
- 可视焦点指示器
- 跳转到主要内容区域的快捷键

### 屏幕阅读器
- ARIA标签和角色
- 语义化HTML结构
- 隐藏文本描述

### 视觉辅助
- 高对比度模式
- 可调整字体大小
- 减少动画选项

## 🚀 性能优化

### 加载性能
- **代码分割**: 页面级和组件级
- **懒加载**: 图片和组件懒加载
- **预加载**: 关键资源预加载
- **缓存策略**: 浏览器和CDN缓存

### 运行时性能
- **虚拟列表**: 大数据列表优化
- **防抖节流**: 用户输入优化
- **Web Worker**: 复杂计算后台处理
- **内存管理**: 组件卸载和清理

### 渲染性能
- **CSS containment**: 减少重排和重绘
- **will-change**: GPU加速提示
- **requestAnimationFrame**: 动画优化
- **IntersectionObserver**: 可视性检测

## 🔧 代码规范

### TypeScript规范
- **严格模式**: 启用所有严格类型检查
- **类型安全**: 禁止使用any类型
- **接口定义**: 清晰的API和业务模型类型
- **工具类型**: 充分使用泛型和工具类型

### React规范
- **函数组件**: 优先使用函数组件和Hooks
- **单一职责**: 每个组件只负责一个功能
- **命名规范**: PascalCase组件名，camelCase变量
- **Hooks使用**: 遵循React Hooks最佳实践

### 样式规范
- **CSS Modules**: 组件样式完全隔离
- **CSS变量**: 统一的设计令牌系统
- **BEM命名**: Block-Element-Modifier命名规范
- **响应式**: 移动优先的媒体查询策略

### 文件组织
- **按功能分组**: 相关文件放在同一目录
- **按类型分层**: components, pages, services, utils等
- **命名规范**: 清晰一致的命名约定
- **模块化**: 每个模块职责单一明确

## 🧪 测试策略

### 单元测试
- **Jest + React Testing Library**: 主要测试框架
- **覆盖率要求**: 核心功能90%+覆盖率
- **Mock策略**: 合理的Mock和Stub策略
- **测试工具**: 完整的测试工具链

### 集成测试
- **Cypress**: 端到端测试
- **MSW**: API模拟和拦截
- **测试环境**: 与生产环境一致
- **测试数据**: 真实的测试数据集

### 性能测试
- **Lighthouse**: 性能评分和优化建议
- **WebPageTest**: 核心性能指标监控
- **性能预算**: 设置性能预算并监控
- **持续监控**: 生产环境性能监控

## 📊 监控和分析

### 性能监控
- **Core Web Vitals**: LCP, FID, CLS, TTFB, TBT
- **用户行为分析**: 点击、滚动、页面停留时间
- **错误监控**: 前端错误和性能问题捕获
- **实时告警**: 关键指标异常告警

### 业务分析
- **用户行为分析**: 功能使用频率和路径
- **转化率分析**: 关键操作转化率
- **性能影响**: 性能对业务指标的影响
- **A/B测试**: 功能效果验证

## 🔒 安全考虑

### 内容安全
- **XSS防护**: 输入验证和输出编码
- **CSRF防护**: Token验证和SameSite策略
- **点击劫持**: X-Frame-Options和CSP
- **HTTPS**: 全站HTTPS加密

### 用户数据
- **敏感信息**: 不在前端存储敏感数据
- **输入验证**: 完整的客户端和服务器验证
- **权限控制**: 基于角色的访问控制
- **数据加密**: 传输和存储加密

## 🚀 部署和发布

### 构建优化
- **代码压缩**: Terser压缩JavaScript和CSS
- **资源优化**: 图片压缩和格式转换
- **Tree Shaking**: 移除未使用的代码
- **代码分割**: 按需加载和缓存策略

### 静态资源
- **CDN加速**: 静态资源CDN分发
- **图片优化**: WebP格式和响应式图片
- **字体优化**: WOFF2格式和字体子集化
- **缓存策略**: 浏览器和CDN缓存策略

### 部署流程
- **环境隔离**: 开发、测试、生产环境
- **自动化部署**: CI/CD流水线
- **版本管理**: 语义化版本控制
- **回滚机制**: 快速回滚和恢复策略

## 🤝 贡献指南

### 开发流程
1. Fork项目并创建功能分支
2. 遵循代码规范和最佳实践
3. 编写测试并确保覆盖率
4. 提交Pull Request并描述变更
5. 代码审查和合并流程

### 提交规范
- **语义化提交**: 清晰的提交信息
- **原子提交**: 每次提交包含一个完整功能
- **分支策略**: 功能分支和主分支策略
- **Code Review**: 强制代码审查流程

### 文档要求
- **代码注释**: 复杂逻辑的详细注释
- **API文档**: 完整的API接口文档
- **变更日志**: 版本变更和更新日志
- **使用说明**: 功能使用和配置说明

## 📞 问题反馈

### 问题报告
- **GitHub Issues**: 使用Issue模板报告问题
- **复现步骤**: 详细的问题复现步骤
- **环境信息**: 完整的环境和版本信息
- **预期行为**: 清楚的预期和实际行为

### 功能请求
- **功能描述**: 清晰的功能需求和场景
- **用户价值**: 功能对用户的价值
- **技术方案**: 可能的技术实现方案
- **优先级评估**: 功能优先级和复杂度

## 📄 许可证

本项目采用MIT许可证 - 详见[LICENSE](LICENSE)文件。

## 👥 致谢

感谢所有为这个项目做出贡献的开发者和用户！

## 📞 联系方式

- **项目地址**: [GitHub Repository](https://github.com/your-org/roo-code-frontend)
- **问题反馈**: [GitHub Issues](https://github.com/your-org/roo-code-frontend/issues)
- **功能请求**: [GitHub Discussions](https://github.com/your-org/roo-code-frontend/discussions)
- **邮件联系**: [dev@your-org.com](mailto:dev@your-org.com)