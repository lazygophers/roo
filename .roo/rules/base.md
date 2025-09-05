- 当前端需要校验代码问题时，可以运行 `yarn build`

# 项目基础配置

## 🛠️ 环境配置

### 虚拟环境

```yaml
# 虚拟环境配置
venv_path: ".venv"
python_executables:
  - "uv python"
  - ".venv/bin/python"
```

### 包管理工具

**UV（Python）**：

| 操作     | 命令               | 功能说明                     |
| -------- | ------------------ | ---------------------------- |
| 创建环境 | `uv sync`          | 初始化虚拟环境并安装所有依赖 |
| 添加依赖 | `uv add <package>` | 将新包添加到项目依赖         |
| 运行程序 | `uv run <main.py>` | 在虚拟环境中执行脚本         |

**Yarn（前端）**：

- 前端项目必须使用 Yarn，禁止使用 npm
- 依赖版本必须锁定在 `yarn.lock` 文件中

| 操作 | 命令 | 功能说明 |
|------|------|----------|
| 安装依赖 | `yarn install` | 根据 package.json 安装依赖 |
| 添加依赖 | `yarn add <package>` | 添加生产环境依赖 |
| 运行脚本 | `yarn <script>` | 执行脚本 |

**前端项目目录**：必须位于 `app/frontend` 目录下。

**工作流程**：`yarn init` → `yarn add` → 提交 `yarn.lock`

### 开发工具规范

| 工具 | 配置要求 | 示例 |
|------|----------|------|
| curl | 超时配置 | `curl --connect-timeout 5 --max-time 10 <URL>` |
| grep | 高效搜索 | `grep -rn "pattern" --include="*.py" .` |
| Makefile | 必需目标 | `dev`、`test`、`fmt`、`install`、`build` |

**测试访问**：
- 前端：http://localhost:14001
- 后端：http://localhost:14001/api
- 支持热重载，无需重启服务

## 🏗️ 技术栈

```yaml
# 核心技术栈
languages:
  - python # 后端语言
  - typescript # 前端语言（优先）
  - javascript # 前端语言（兼容）
  - react # 前端框架

frameworks:
  backend: "fastapi" # 后端框架
  frontend: "react" # React 前端框架
  ui_library: "antd" # Ant Design UI 组件库
  build_tools: "vite/webpack" # 构建工具
  database: "tinydb" # 数据库
```

### TypeScript 优先原则

**核心要求**：

- **所有新项目必须使用 TypeScript**
- **现有 JS 项目逐步迁移至 TS**
- **类型定义覆盖率达到 95%+**
- **严格模式启用：`strict: true`**
- **禁止使用 `any` 类型**（特殊情况需注释说明）

**迁移策略**：

1. 先添加 `@types` 依赖
2. 文件扩展名改为 `.ts`/`.tsx`
3. 逐步添加类型注解
4. 启用严格模式检查

**类型规范**：

- 使用接口定义数据结构
- 优先使用联合类型而非 `any`
- 工具类型合理使用 `Partial`、`Pick`、`Omit`、`Record`
- 泛型约束清晰明确
- React 组件使用 `React.FC` 或函数组件语法

**高级类型使用**：

```typescript
// 推荐的类型定义方式
interface User {
  id: string;
  name: string;
  email?: string; // 可选属性
}

type Status = "pending" | "in_progress" | "completed";

// 使用泛型增强复用性
interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

// 使用工具类型
type UserPreview = Pick<User, "id" | "name">;
type PartialUser = Partial<User>;
```

**配置文件要求**：

```jsonc
// tsconfig.json 必须包含
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noImplicitReturns": true,
    "noFallthroughCasesInSwitch": true,
    "esModuleInterop": true,
    "skipLibCheck": true,
    "forceConsistentCasingInFileNames": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "noEmit": true,
    "jsx": "react-jsx"
  },
  "include": ["src/**/*"],
  "exclude": ["node_modules"]
}
```

## 🎯 模式选择指导

### 开发任务模式选择

根据任务类型选择合适的执行模式，确保专业化分工和高效执行。

#### 后端开发任务

**优先模式**: `code-python`

**适用任务类型**:

- Python 后端 API 开发
- 数据库操作和模型定义
- 业务逻辑实现
- 中间件和工具开发
- 自动化脚本编写

**模式特点**:

- 专精 Python 生态系统
- 熟悉 FastAPI、Django、Flask 等框架
- 擅长数据库操作（SQL、NoSQL）
- 支持异步编程和性能优化

#### 前端开发任务

**优先模式**: `code-react`

**适用任务类型**:

- React 组件开发
- 前端页面构建
- 状态管理（Redux/Context API）
- 路由配置（React Router）
- 前端工程化配置

**模式特点**:

- 深度理解 React 生态系统
- 熟练使用 Hooks API
- 掌握 Vite/Webpack 构建工具
- 支持 TypeScript 集成
- 擅长前端性能优化

### 模式选择决策流程

1. **识别任务性质**

   - 后端任务 → `code-python`
   - 前端任务 → `code-react`
   - 架构设计 → `architect`
   - 文档编写 → `doc-writer`
   - 问题调试 → `debug`

2. **考虑技术栈**

   - Python 相关 → 优先 `code-python`
   - React/TypeScript → 优先 `code-react`
   - 多语言混合 → `orchestrator` 协调

3. **评估复杂度**
   - 简单任务 → 直接对应模式
   - 复杂任务 → `orchestrator` 分解

### 模式协作示例

#### 全栈开发场景

```
用户需求 → orchestrator
    ↓ 任务分解
后端 API → code-python
前端界面 → code-react
数据库设计 → architect
    ↓ 结果整合
完整系统交付
```

#### 技术迁移场景

```
迁移任务 → orchestrator
    ↓ 评估和规划
架构分析 → architect
代码重构 → code-python/code-react
测试验证 → debug
    ↓ 交付
迁移完成
```

## 📋 开发规范

### 质量标准

- **测试覆盖率**: ≥ 90%
- **代码质量**: 严格遵循代码规范
- **架构设计**: 合理的分层分包
- **开发方式**: 渐进式开发

### 工程化要求

**代码规范**：

- 使用 ESLint/Prettier 统一代码风格
- 遵循 Airbnb/Standard 规范
- 强制代码检查通过才能提交
- 使用 Husky 管理 Git hooks

**构建工具配置**：

- **Vite**（推荐）：现代、快速、开箱即用，对 React 有原生支持
- **Webpack**：功能强大、生态完善
- 必须配置：
  - 代码分割（Code Splitting）
  - 懒加载（Lazy Loading）
  - Tree Shaking
  - Source Map
- React 项目推荐使用 Vite 以获得最佳开发体验

**开发环境**：

- 热模块替换（HMR）
- 开发服务器代理配置
- 环境变量管理（.env 文件）
- 跨域处理（CORS）

**构建优化**：

- 代码压缩混淆
- 静态资源 CDN 配置
- 缓存策略配置
- 性能预算（Performance Budget）

### CSS 样式分离要求

**核心原则**：

- 严格遵循样式与结构分离的原则
- **禁止在组件文件中使用内联样式**（包括 `style` 属性和 `style` 对象）
- **禁止使用 `!important` 覆盖样式优先级**
- **每个组件必须使用单独的样式文件**，禁止在组件文件中嵌入任何样式代码

**样式组织规范**：

1. **模块化样式**

   - 使用 CSS Modules 或 CSS-in-JS 避免全局污染
   - 支持在 React 组件中使用 CSS Modules 或 styled-components
   - **样式文件必须与组件文件放在同一目录下**

2. **样式文件结构**

   ```
   src/
   ├── styles/
   │   ├── variables.css      # CSS 变量定义
   │   ├── mixins.css         # 混合器定义
   │   ├── global.css         # 全局样式
   │   └── themes/            # 主题相关样式
   │       ├── light.css       # 亮色主题
   │       └── dark.css        # 暗色主题
   └── components/
       ├── Button/
       │   ├── Button.jsx
       │   ├── Button.module.css
       │   └── Button.test.js
       ├── Card/
       │   ├── Card.jsx
       │   ├── Card.module.css
       │   └── Card.styled.js (可选)
       └── Layout/
           ├── Layout.jsx
           ├── Layout.module.css
           └── Layout.context.js (主题上下文)
   ```

3. **CSS 命名规范**

   - 使用 BEM（Block Element Modifier）命名规范
   - 类名使用小写字母，单词间用连字符 `-` 连接
   - 避免使用标签选择器和 ID 选择器
   - CSS Modules 类名必须使用 `moduleName_className` 格式

4. **响应式设计**

   - 必须使用相对单位（rem、em、%、vw、vh）
   - 使用 CSS Grid 或 Flexbox 进行布局
   - 媒体查询必须使用移动优先（mobile-first）策略
   - 断点必须使用预定义的变量（如 `--breakpoint-md`、`--breakpoint-lg`）

5. **主题支持**
   - 所有颜色、字体、间距等必须使用 CSS 变量
   - 支持亮色/暗色主题切换
   - 主题变量统一在 `variables.css` 中定义
   - 使用 CSS 自定义属性（CSS Variables）而非 Sass/Less 变量

**样式检查**：

- 使用 Stylelint 进行代码检查
- 配合 Prettier 进行格式化
- 在 CI/CD 流程中加入样式检查环节
- **必须配置 stylelint-config-recommended 和 stylelint-config-prettier**

**性能要求**：

- CSS 文件大小不得超过 50KB（压缩后）
- 每个组件的样式文件必须独立，避免合并
- 使用 `@import` 时必须指定媒体查询条件
- 禁止使用 `@import` 导入非 CSS 文件

**开发规范**：

- 所有样式变更必须经过代码审查
- 禁止在生产环境使用内联样式
- 样式文件必须与组件文件同步更新
- 使用 CSS 预处理器时必须配置 source maps

**React 组件样式使用示例**：

```jsx
// ❌ 错误示例：内联样式（禁止）
const BadComponent = () => {
  return (
    <div style={{ backgroundColor: '#f0f0f0', padding: '20px' }}>
      <h3 style={{ color: 'red' }}>错误示范</h3>
    </div>
  );
};

// ✅ 正确示例：使用 CSS Modules
import styles from './Component.module.css';

const GoodComponent = () => {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>正确示范</h3>
    </div>
  );
};
```

**CSS 变量定义示例**：

```css
/* src/styles/variables.css */
:root {
  /* 颜色系统 */
  --color-primary: #1890ff;
  --color-background: #ffffff;
  --color-text: #262626;
  
  /* 间距系统 */
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  
  /* 字体系统 */
  --font-size-md: 16px;
  --font-weight-normal: 400;
}

/* 暗色主题 */
[data-theme="dark"] {
  --color-primary: #40a9ff;
  --color-background: #1f1f1f;
  --color-text: #ffffff;
}
```

### 开发流程

#### 渐进式开发流程

**核心理念**：

- **快速验证**：先实现核心功能，快速获得反馈
- **迭代优化**：基于反馈持续改进，避免过度设计
- **质量保证**：每个阶段都确保代码质量和测试覆盖

**开发阶段**：

1. **第一阶段：MVP（最小可行产品）**

   - 实现核心业务逻辑
   - 基础用户界面
   - 基本功能测试
   - 部署验证

2. **第二阶段：功能完善**

   - 扩展功能特性
   - 优化用户体验
   - 完善错误处理
   - 集成测试覆盖

3. **第三阶段：性能优化**

   - 代码重构优化
   - 性能瓶颈解决
   - 缓存策略实施
   - 负载测试验证

4. **第四阶段：生产就绪**
   - 安全加固
   - 监控告警
   - 文档完善
   - 上线部署

**各阶段要求**：

- **MVP 阶段**：

  - 功能：仅包含核心功能，去除所有非必需特性
  - 质量：基础测试覆盖，主要流程可验证
  - 时间：控制在 1-2 周内完成
  - 目标：快速验证产品价值

- **功能完善阶段**：

  - 功能：实现 80% 的规划功能
  - 质量：单元测试覆盖率 ≥ 80%
  - 时间：根据项目规模，2-4 周
  - 目标：获得用户真实使用反馈

- **性能优化阶段**：

  - 功能：全部功能完成
  - 质量：性能指标达标，自动化测试完善
  - 时间：1-2 周
  - 目标：系统稳定可靠

- **生产就绪阶段**：
  - 功能：功能冻结，仅修复问题
  - 质量：生产环境验证通过
  - 时间：1 周
  - 目标：安全稳定上线

**迭代原则**：

- 每个迭代周期不超过 2 周
- 每次迭代必须有可交付的成果
- 保持与用户的持续沟通
- 及时调整开发优先级

## 🔒 决策授权

**必须获得用户明确授权的操作**：

- 更新任务清单
- 规划任务执行路径
- 确定任务优先级
- 确认技术方案选择

## 🚀 执行原则

### 模式切换

- **禁止使用** `switch_mode`。通过 `new_task` 委派给专业模式。

### 任务粒度

- 非 orchestrator 模式下，任务必须原子化，确保可独立执行和验证。

### 决策确认

- L1 级决策必须通过 `ask_followup_question` 获得用户明确授权。

### 信息呈现

- 使用流程图、清单、表格等可视化方式，确保信息清晰易懂。

### 模式专业化

- 严格专业分工，超出能力的任务必须委派给对应的专业模式。

### 上下文精简

- 仅传递任务相关上下文，避免信息过载，保持高效沟通。

---

## 📖 产品说明

### 项目定位

帮助用户对多个 Roo Code 规则配置进行自定义选择、组合的工具。

### 目录结构

```
resources/
├── modes/                    # 模式配置目录
│   └── <mode-name>/          # 各模式具体配置
├── rules-<slug>/            # 模式特异性规则
├── rules/                   # 全局通用规则
└── hooks/                   # 钩子脚本
    ├── before.md            # 全局前置规则 ✨
    └── after.md             # 全局后置规则

# 其他重要目录
logs/                         # 日志文件目录
    ├── app.log              # 应用程序日志
    ├── error.log             # 错误日志
    └── access.log            # 访问日志

data/                         # 数据库文件目录
    ├── database.json         # TinyDB 数据库文件
    ├── backup/               # 数据库备份目录
    └── cache/                # 缓存数据目录

tests/                        # 测试文件目录
    ├── unit/                 # 单元测试
    ├── integration/          # 集成测试
    └── fixtures/             # 测试数据
```

### 核心功能

- **自动索引**：启动时扫描并生成数据库索引
- **实时监听**：监听文件变化，自动更新索引
- **规则预览**：选择配置后可预览完整规则内容
- **配置导出**：支持导出完整的配置文件

### 导出规范

- 参考模板：[`custom_mmodels.yaml`](custom_mmodels.yaml)
- 支持通过 Shell 指定导出内容范围
- 支持通过 Shell 生成定制化规则

## 💡 提示词说明

### 提示词层次结构

| 层级 | 路径 | 职责 |
|------|------|------|
| 全局前置规则 | `hooks/before.md` | 核心原则、行为准则、专业分工 |
| 项目基础规则 | `rules/base.md` | 项目配置、技术栈、执行原则 |
| 模式特异性规则 | `rules-<slug>/` | 模式行为规范、工具限制 |
| 通用规则 | `rules/` | 跨模式规范、工具标准 |

### 设计原则

- **层级明确**：避免规则冲突，确保可维护性
- **专业分工**：通过 `new_task` 协作，禁止跨模式处理
- **用户主导**：关键决策用户确认，使用 `ask_followup_question`
- **结果导向**：注重产出价值，追求专业标准

### 扩展机制

- **模式定义**：`resources/modes/` 创建新模式
- **规则注入**：Shell 动态生成规则
- **插件机制**：第三方提示词插件

### 接口变更自动更新文档规范

**核心理念**：

- **代码即文档**：确保接口文档与代码实现保持同步
- **自动化优先**：通过工具自动检测接口变更并更新文档
- **版本化管理**：所有文档变更纳入版本控制，支持历史追溯

**检测机制**：

| 层级 | 功能 | 支持文件类型 |
|------|------|-------------|
| 代码分析 | AST解析、接口定义扫描 | Python: `*.py`, TS: `*.ts` |
| 文件监听 | 实时变更监控 | API/Router/Model文件 |
| 变更分析 | 增删改检测、破坏性变更标记 | 所有接口相关文件 |

**实现工具**：

| 技术栈 | 推荐工具 | 配置示例 |
|--------|----------|----------|
| Python | FastAPI OpenAPI | `from fastapi.openapi.utils import get_openapi` |
| TypeScript | TypeDoc | TSDoc + 类型定义生成 |
| 通用 | Git Hooks | Pre-commit 检测API变更 |

**最佳实践**：

- **注释规范**：使用标准格式，包含Args/Returns/Raises
- **版本控制**：PR审核，破坏性变更需major版本更新
- **质量保证**：CI/CD检查、文档同步验证
- **监控告警**：自动检测不同步，生成使用报告
