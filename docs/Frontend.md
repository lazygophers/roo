# Frontend 技术文档

## 项目概述

Roo 配置管理系统的前端是基于 **React 18** 和 **TypeScript** 构建的现代化单页应用，提供了直观友好的配置管理界面。

## 技术栈

### 核心框架
- **React 18.2.0**: 使用最新的函数式组件和 Hooks
- **TypeScript 4.9+**: 提供完整的类型安全
- **React Router 6**: 单页应用路由管理
- **Create React App**: 项目脚手架，零配置构建

### UI 组件库
- **Ant Design 5.x**: 企业级 UI 组件库
  - 丰富的组件生态
  - 完整的设计规范
  - 内置主题系统
- **Ant Design Icons**: 图标组件

### 状态管理
- **React Hooks**: useState, useEffect, useContext
- **Context API**: 主题管理和全局状态
- **本地状态**: 组件级状态管理

## 项目结构

```
frontend/
├── public/                 # 静态资源
├── src/
│   ├── api/               # API 接口层
│   │   └── index.ts       # API 客户端和类型定义
│   ├── components/        # 可复用组件
│   │   ├── ConfigTabs/    # 配置页签组件
│   │   ├── ExportToolbar/ # 导出工具栏
│   │   ├── Layout/        # 布局组件
│   │   ├── Preview/       # 预览面板
│   │   ├── Theme/         # 主题组件
│   │   └── UI/            # 通用 UI 组件
│   ├── contexts/          # React Context
│   │   └── ThemeContext.tsx
│   ├── pages/             # 页面组件
│   │   ├── Home.tsx       # 首页
│   │   └── ConfigManagementWithSelection.tsx
│   ├── themes/            # 主题配置
│   ├── types/             # TypeScript 类型定义
│   └── App.tsx            # 应用根组件
├── package.json
└── tsconfig.json
```

## 核心特性

### 1. 类型安全的 API 层

```typescript
// api/index.ts
export interface ModelInfo {
  slug: string;
  name: string;
  role_definition: string;
  when_to_use: string;
  description: string;
  groups: any[];
  file_path: string;
  file_size?: number;
  last_modified?: number;
}

export interface SelectedItem {
  id: string;
  type: 'model' | 'command' | 'rule' | 'role';
  name: string;
  data: any;
}
```

### 2. 组件化配置管理

#### 配置页签组件
- **ModesListWithSelection**: 模式选择和关联规则管理
- **CommandsListWithSelection**: 命令文件选择
- **RulesListWithSelection**: 规则文件选择  
- **RolesListWithSelection**: 角色选择

每个组件都支持：
- ✅ 单选/多选切换
- ✅ 全选/清空操作
- ✅ 实时预览
- ✅ 文件信息显示(路径、大小、修改时间)

#### 预览系统
- **SelectionPreviewPanel**: 统一的选择预览面板
- **实时更新**: 选择变化时自动更新预览
- **详细信息**: 显示文件内容、元数据等

### 3. 主题系统

```typescript
// contexts/ThemeContext.tsx
interface ThemeContextType {
  currentTheme: any;
  themeType: string;
  toggleTheme: () => void;
}

// 支持亮色/暗色主题切换
// 自动适配系统主题偏好
// 主题状态持久化
```

### 4. 响应式设计

使用 Ant Design 的栅格系统实现响应式布局：

```tsx
<Row gutter={16}>
  <Col span={10}>
    {/* 配置选择区域 */}
  </Col>
  <Col span={14}>
    {/* 预览区域 */}
  </Col>
</Row>
```

## 关键组件详解

### 1. ConfigManagementWithSelection

主要的配置管理页面，管理全局选择状态：

```typescript
const [selectedItems, setSelectedItems] = useState<SelectedItem[]>([]);
const [modelRuleBindings, setModelRuleBindings] = useState<ModelRuleBinding[]>([]);
const [modelRules, setModelRules] = useState<Record<string, FileMetadata[]>>({});
```

**核心功能**:
- 统一的选择状态管理
- 模式-规则关联关系处理
- 配置导入导出
- 一键部署

### 2. ModesListWithSelection

最复杂的组件，处理模式选择和规则关联：

```typescript
// 模式-规则关联逻辑
const getModelRuleSlug = (modelSlug: string): string[] => {
  const parts = modelSlug.split('-');
  const ruleSlugs: string[] = [];
  
  // 添加基础的 rules 目录
  ruleSlugs.push('rules');
  
  // 逐级构建规则目录名称，不添加 rules- 前缀
  let currentPath = '';
  for (const part of parts) {
    if (part) {
      if (currentPath === '') {
        currentPath = part;
      } else {
        currentPath += `-${part}`;
      }
      ruleSlugs.push(currentPath);
    }
  }
  
  return ruleSlugs;
};
```

### 3. ExportToolbar

部署和导出工具栏：

```typescript
// 部署配置
const handleDeploy = async (selectedTargets: string[]) => {
  const deployData: DeployRequest = {
    deploy_targets: selectedTargets,
    selected_models: getSelectedSlugs('model'),
    selected_commands: getSelectedSlugs('command'), 
    selected_rules: getSelectedSlugs('rule'),
    selected_role: getSelectedRole()
  };
  
  const response = await apiClient.deployConfiguration(deployData);
  // 处理部署结果
};
```

## 数据流设计

### 1. 状态流转

```
用户选择 → 更新 selectedItems → 触发预览更新 → 模式-规则关联计算 → UI 重新渲染
```

### 2. API 交互

```
组件请求 → API 客户端 → HTTP 请求 → 后端处理 → 响应数据 → 组件状态更新
```

### 3. 主题切换

```
用户切换 → ThemeContext 更新 → 所有消费组件重新渲染 → 主题样式生效
```

## 性能优化

### 1. 组件优化
- **React.memo**: 避免不必要的重渲染
- **useMemo/useCallback**: 缓存计算结果和回调函数
- **条件渲染**: 大数据列表的懒加载

### 2. API 优化
- **批量请求**: 合并多个 API 调用
- **错误边界**: 优雅的错误处理
- **Loading 状态**: 用户友好的加载体验

### 3. 代码分割
- **路由级分割**: 页面按需加载
- **组件懒加载**: 减少初始包大小

## 开发规范

### 1. 代码风格
- **ESLint + Prettier**: 自动代码格式化
- **TypeScript Strict**: 严格类型检查
- **函数式组件**: 统一使用 Hooks

### 2. 组件设计原则
- **单一职责**: 每个组件负责特定功能
- **Props 接口化**: 明确的组件接口定义
- **状态提升**: 合理的状态管理层级

### 3. 文件命名
- **PascalCase**: 组件文件名
- **camelCase**: 工具函数和变量
- **kebab-case**: CSS 类名

## 构建和部署

### 开发环境
```bash
npm start          # 开发服务器 (http://localhost:3000)
npm test           # 运行测试
npm run build      # 生产构建
npm run eject      # 弹出 CRA 配置 (不可逆)
```

### 生产构建
```bash
npm run build
# 输出到 build/ 目录
# 自动优化: 代码分割、压缩、TreeShaking
```

### 部署选项
- **静态文件服务**: nginx, Apache
- **CDN 部署**: 配合 API 跨域设置
- **Docker 容器**: 容器化部署

## 问题排查

### 1. 常见问题

**TypeScript 编译错误**
```bash
# 清除缓存重新构建
rm -rf node_modules/.cache .eslintcache
npm run build
```

**API 调用失败**  
```typescript
// 检查 API 基础 URL 配置
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';
```

**主题不生效**
```typescript
// 确保组件正确使用 ThemeContext
const { currentTheme } = useTheme();
```

### 2. 调试工具
- **React Developer Tools**: 组件状态调试
- **Network Panel**: API 请求监控  
- **Console**: 错误日志分析

## 未来规划

### 1. 功能增强
- [ ] 配置模板系统
- [ ] 批量操作优化
- [ ] 高级过滤和搜索
- [ ] 配置差异对比

### 2. 技术升级
- [ ] React 19 升级
- [ ] Vite 构建工具迁移
- [ ] PWA 支持
- [ ] 国际化支持

### 3. 用户体验
- [ ] 键盘快捷键
- [ ] 撤销/重做功能
- [ ] 拖拽排序
- [ ] 暗色模式完善

## 贡献指南

### 开发流程
1. Fork 项目
2. 创建功能分支
3. 编写代码和测试
4. 提交 PR

### 代码质量
- 遵循 ESLint 规则
- 编写单元测试
- 更新相关文档
- 确保 TypeScript 类型完整