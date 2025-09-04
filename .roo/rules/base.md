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

### UV 包管理

| 操作     | 命令               | 功能说明                     |
| -------- | ------------------ | ---------------------------- |
| 创建环境 | `uv sync`          | 初始化虚拟环境并安装所有依赖 |
| 添加依赖 | `uv add <package>` | 将新包添加到项目依赖         |
| 运行程序 | `uv run <main.py>` | 在虚拟环境中执行脚本         |

### Yarn 包管理（前端）

**核心原则**：

- 前端项目必须使用 Yarn 作为包管理器
- 禁止使用 npm 直接安装依赖
- 所有依赖版本必须锁定在 `yarn.lock` 文件中

| 操作         | 命令                     | 功能说明                       |
| ------------ | ------------------------ | ------------------------------ |
| 安装依赖     | `yarn install`           | 根据 package.json 安装所有依赖 |
| 添加依赖     | `yarn add <package>`     | 添加生产环境依赖               |
| 添加开发依赖 | `yarn add -D <package>`  | 添加开发环境依赖               |
| 升级依赖     | `yarn upgrade <package>` | 升级指定包到最新版本           |
| 移除依赖     | `yarn remove <package>`  | 移除指定依赖                   |
| 运行脚本     | `yarn <script>`          | 执行 package.json 中定义的脚本 |

**前端项目目录要求**：

- **前端项目必须位于 `app/frontend` 目录下**
- 所有前端源代码、配置文件、静态资源等都必须放置在此目录中
- 禁止在项目根目录或其他位置存放前端相关文件
- 确保前端项目的独立性和模块化

**工作流程**：

1. 新建前端项目时先执行 `yarn init` 创建 package.json
2. 使用 `yarn add` 添加所需依赖
3. 提交代码时必须包含 `yarn.lock` 文件
4. 团队成员使用 `yarn install` 同步依赖

### 网络请求规范

**curl 超时配置**：

- 强制要求所有 curl 命令设置超时
- 连接超时：`--connect-timeout 5`
- 总体超时：`--max-time 10`
- 标准格式：`curl --connect-timeout 5 --max-time 10 <URL>`

### grep 代码搜索规范

**核心原则**：

- grep 是 Linux/Unix 系统中最强大的文本搜索工具之一
- 使用 grep 可以快速在代码库中查找特定的代码模式、函数名、变量等
- 掌握 grep 的高级用法可以大幅提升代码搜索效率

**基础用法**：

```bash
# 在当前目录及子目录中搜索
grep -r "search_pattern" .

# 递归搜索，但忽略二进制文件
grep -rI "search_pattern" .

# 搜索时显示行号
grep -rn "search_pattern" .

# 显示匹配的上下文（前后各 2 行）
grep -rnC 2 "search_pattern" .
```

**常用选项组合**：

| 选项 | 说明 | 示例 |
|------|------|------|
| `-i` | 忽略大小写 | `grep -ri "function" .` |
| `-w` | 匹配整个单词 | `grep -rw "import" .` |
| `-l` | 只显示文件名 | `grep -rl "TODO" .` |
| `-L` | 只显示不匹配的文件名 | `grep -rL "FIXME" .` |
| `-n` | 显示行号 | `grep -rn "class User" .` |
| `-C` | 显示上下文 | `grep -rnC 3 "def main" .` |
| `--include` | 只搜索特定文件 | `grep -rn "import" --include="*.py" .` |
| `--exclude` | 排除特定文件 | `grep -rn "debug" --exclude="*.log" .` |
| `--exclude-dir` | 排除特定目录 | `grep -rn "test" --exclude-dir=vendor .` |

**高级用法示例**：

```bash
# 搜索特定文件类型中的模式
grep -rn "TODO\|FIXME" --include="*.py" --include="*.jsx" .

# 使用正则表达式搜索函数定义
grep -rn "^\s*function \w+" --include="*.jsx" .
grep -rn "^\s*const \w+.*=.*=>" --include="*.jsx" .

# 搜索包含特定单词但不包含另一个单词的行
grep -rn "import.*react" --include="*.jsx" . | grep -v "test_"

# 搜索多个模式（OR 关系）
grep -rnE "(function|const) \w+.*:" --include="*.jsx" .

# 使用管道组合多个 grep 命令
grep -rn "useState.*=>" --include="*.jsx" . | grep -v "test_" | head -20

# 搜索并统计出现次数
grep -r "useState(" --include="*.jsx" . | wc -l

# 在特定目录中搜索
grep -rn "API_KEY" src/ config/

# 搜索制表符或空格开头的注释
grep -rn "^[\t ]*#" --include="*.jsx" .
```

**性能优化建议**：

1. **使用 `--include` 限制搜索范围**：只搜索相关文件类型
2. **排除不必要的目录**：如 `node_modules`、`.git`、`vendor` 等
3. **使用 `head` 或 `tail` 限制输出**：避免输出过多结果
4. **组合使用其他工具**：
   - 使用 `xargs` 处理大量文件
   - 使用 `find` + `grep` 进行更精确的搜索

```bash
# 结合 find 使用，性能更好
find . -name "*.py" -type f -exec grep -l "import.*pandas" {} \;

# 使用 xargs 处理大量文件
find . -name "*.js" -type f -print0 | xargs -0 grep -l "React"
```

### Makefile 规范

**核心原则**：

- 项目必须提供 [`Makefile`](Makefile)
- 通用操作必须通过 Makefile 执行
- 禁止直接使用 `uv run` 等命令
- **禁止直接使用 `python` 或 `pip` 命令**
- **所有 Python 相关操作必须通过 `uv` 命令或 Makefile 目标执行**
- Makefile 需包含：开发、测试、构建、部署等目标

**标准 Makefile 模板**：

```makefile
# 开发环境运行
dev:
	uv run main.py

# 执行测试套件
test:
	uv run pytest

# 代码格式化和检查
fmt:
	uv run ruff check --fix .
	uv run ruff format .

# 安装/更新依赖
install:
	uv sync

# 项目构建
build:
	@echo "Building project..."
```

### 测试访问说明

**前端测试**：

- 执行 `make build` 构建项目
- 访问 http://localhost:14001 进行前端测试
- **热重载支持**：前端服务支持自动热重载，代码变更后无需重新运行服务，可直接在浏览器中验证效果

**后端测试**：

- 直接访问 http://localhost:14001/api 进行后端 API 测试
- **热重载支持**：后端服务支持自动热重载，代码变更后无需重新运行服务，API 修改会立即生效

**开发体验优化**：

- 前后端服务均配置了文件监听机制，支持开发时的实时热重载
- 出现代码变更后，系统会自动重新加载相关模块，保持服务运行状态
- 开发者可以专注于代码编写，无需手动重启服务，提高开发效率

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

type Status = 'pending' | 'in_progress' | 'completed';

// 使用泛型增强复用性
interface ApiResponse<T> {
  data: T;
  success: boolean;
  error?: string;
}

// 使用工具类型
type UserPreview = Pick<User, 'id' | 'name'>;
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
    <div style={{
      backgroundColor: '#f0f0f0',
      padding: '20px',
      borderRadius: '8px'
    }}>
      <h3 style={{ color: 'red', fontSize: '18px' }}>错误示范</h3>
    </div>
  );
};

// ✅ 正确示例：使用 CSS Modules
import styles from './GoodComponent.module.css';

const GoodComponent = () => {
  return (
    <div className={styles.container}>
      <h3 className={styles.title}>正确示范</h3>
      <button className={styles.button}>点击按钮</button>
    </div>
  );
};

// ✅ 正确示例：使用 styled-components
import styled from 'styled-components';

const StyledContainer = styled.div`
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  
  @media (min-width: 768px) {
    padding: var(--spacing-lg);
  }
`;

const StyledTitle = styled.h3`
  color: var(--color-primary);
  font-size: var(--font-size-lg);
  margin-bottom: var(--spacing-sm);
`;

const StyledComponent = () => {
  return (
    <StyledContainer>
      <StyledTitle>正确示范</StyledTitle>
      <button className="btn btn-primary">点击按钮</button>
    </StyledContainer>
  );
};

// ✅ 正确示例：使用 CSS-in-JS with emotion
/** @jsx jsx */
import { jsx, css } from '@emotion/react';

const containerStyle = css`
  background-color: var(--color-background);
  padding: var(--spacing-md);
  border-radius: var(--border-radius-md);
  
  &:hover {
    box-shadow: var(--shadow-md);
  }
`;

const EmotionComponent = () => {
  return (
    <div css={containerStyle}>
      <h3 css={css`
        color: var(--color-primary);
        font-size: var(--font-size-lg);
      `>
        正确示范
      </h3>
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
  --color-secondary: #52c41a;
  --color-danger: #ff4d4f;
  --color-warning: #faad14;
  --color-background: #ffffff;
  --color-surface: #f5f5f5;
  --color-text: #262626;
  --color-text-secondary: #8c8c8c;
  
  /* 间距系统 */
  --spacing-xs: 4px;
  --spacing-sm: 8px;
  --spacing-md: 16px;
  --spacing-lg: 24px;
  --spacing-xl: 32px;
  
  /* 字体系统 */
  --font-size-xs: 12px;
  --font-size-sm: 14px;
  --font-size-md: 16px;
  --font-size-lg: 18px;
  --font-size-xl: 20px;
  --font-size-xxl: 24px;
  --font-weight-normal: 400;
  --font-weight-medium: 500;
  --font-weight-bold: 600;
  
  /* 边框和圆角 */
  --border-radius-sm: 4px;
  --border-radius-md: 8px;
  --border-radius-lg: 12px;
  --border-width: 1px;
  --border-color: #d9d9d9;
  
  /* 阴影 */
  --shadow-sm: 0 2px 4px rgba(0, 0, 0, 0.1);
  --shadow-md: 0 4px 8px rgba(0, 0, 0, 0.15);
  --shadow-lg: 0 8px 16px rgba(0, 0, 0, 0.2);
  
  /* 断点 */
  --breakpoint-sm: 576px;
  --breakpoint-md: 768px;
  --breakpoint-lg: 992px;
  --breakpoint-xl: 1200px;
  
  /* 动画 */
  --transition-fast: 0.2s ease;
  --transition-normal: 0.3s ease;
  --transition-slow: 0.5s ease;
}

/* 暗色主题 */
[data-theme="dark"] {
  --color-primary: #40a9ff;
  --color-background: #1f1f1f;
  --color-surface: #2d2d2d;
  --color-text: #ffffff;
  --color-text-secondary: #bfbfbf;
  --border-color: #434343;
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

### 提示词使用指南

本项目的提示词系统采用分层架构设计，确保 AI 系统的行为可控、可预测且专业化。

#### 提示词层次结构

1. **全局前置规则 (hooks/before.md)**

   - 定义 AI 系统的核心原则和价值观
   - 设定不可动摇的行为准则
   - 建立专业分工和协作机制

2. **项目基础规则 (rules/base.md)**

   - 定义项目特定的配置和规范
   - 设定技术栈和开发标准
   - 建立执行原则和决策流程

3. **模式特异性规则 (rules-<slug>/)**

   - 定义各专业模式的具体行为规范
   - 设定模式内的工具使用限制
   - 建立模式间的协作接口

4. **通用规则 (rules/)**
   - 定义跨模式的通用规范
   - 设定工具使用标准
   - 建立质量保证机制

#### 提示词设计原则

1. **层级明确**

   - 每层规则有明确的职责边界
   - 避免规则冲突和重复
   - 确保规则的可维护性

2. **专业分工**

   - 每个模式专注于特定领域
   - 通过 `new_task` 实现模式间协作
   - 禁止跨模式处理不擅长任务

3. **用户主导**

   - 关键决策必须用户确认
   - 使用 `ask_followup_question` 获取授权
   - 保持透明度和可控性

4. **结果导向**
   - 注重产出价值而非过程
   - 追求极致的专业标准
   - 建立质量反馈机制

#### 提示词更新机制

1. **动态加载**

   - 系统启动时自动扫描所有规则文件
   - 实时监听文件变化并更新缓存
   - 支持热更新而不影响运行

2. **版本控制**

   - 所有提示词文件纳入 Git 版本控制
   - 记录变更历史和影响分析
   - 支持回滚和分支管理

3. **冲突解决**
   - 采用层级优先级解决冲突
   - 下层规则可以覆盖上层规则
   - 记录冲突日志用于优化

#### 提示词最佳实践

1. **编写规范**

   - 使用清晰简洁的语言
   - 避免模糊和歧义表述
   - 提供具体的执行标准

2. **测试验证**

   - 建立提示词效果测试机制
   - 收集用户反馈并持续优化
   - 定期审查和更新规则

3. **文档维护**
   - 保持提示词文档的同步更新
   - 提供变更说明和迁移指南
   - 建立知识库沉淀经验

#### 提示词扩展接口

系统支持通过以下方式扩展提示词：

1. **模式定义**

   - 在 `resources/modes/` 下创建新模式
   - 定义模式的核心能力和边界
   - 建立与其他模式的协作关系

2. **规则注入**

   - 通过 Shell 动态生成规则
   - 支持条件化规则加载
   - 实现个性化的行为定制

3. **插件机制**
   - 支持第三方提示词插件
   - 提供标准化的插件接口
   - 建立插件市场和评分系统


### 接口变更自动更新文档规范

**核心理念**：

- **代码即文档**：确保接口文档与代码实现保持同步
- **自动化优先**：通过工具自动检测接口变更并更新文档
- **版本化管理**：所有文档变更纳入版本控制，支持历史追溯

**接口变更检测机制**：

1. **代码分析层**
   - 使用 AST 解析器扫描代码中的接口定义
   - 监控函数签名、参数、返回值的变化
   - 检测数据模型（Pydantic 模型、TypeScript 接口）的变更
   - 识别路由端点的增删改

2. **文件监听层**
   - 实时监听 API 相关文件变更
   - 支持的文件类型：
     - Python: `*.py`, `*api*.py`, `*router*.py`
     - TypeScript/JavaScript: `*.ts`, `*.tsx`, `*.js`, `*.jsx`
     - 接口定义文件: `*.proto`, OpenAPI 规范文件
   - 忽略测试文件和私有实现文件

3. **变更分析层**
   - 提取接口变更的详细信息：
     - 新增接口：检测新增的路由和函数
     - 修改接口：识别参数类型、默认值、验证规则的变化
     - 删除接口：标记废弃的接口，生成迁移指南
     - 破坏性变更：自动标记并要求审核

**文档自动更新流程**：

1. **变更触发**
   ```bash
   # 开发者提交代码变更
   git commit -m "feat(api): add user management endpoints"
   
   # 或者在开发服务器上保存文件
   # 文件系统监听器自动触发
   ```

2. **文档生成**
   - 自动从代码中提取最新的接口信息
   - 生成/更新以下文档：
     - OpenAPI/Swagger 规范
     - API 参考文档
     - 客户端 SDK 文档
     - 集成测试用例

3. **变更对比**
   - 生成变更前后对比报告
   - 高亮显示：
     - 新增的接口和参数
     - 修改的类型和验证规则
     - 废弃的功能和替代方案

4. **审核发布**
   - 对于破坏性变更，创建审核任务
   - 自动通知相关团队成员
   - 集成到 CI/CD 流程，阻止未审核的破坏性变更合并

**实现工具要求**：

1. **Python 项目**
   ```python
   # 使用 pydantic 和 fastapi 的 OpenAPI 生成
   from fastapi.openapi.utils import get_openapi
   
   # 或使用第三方工具
   # - sphinxcontrib-openapi
   # - apispec
   # - swagger-codegen
   ```

2. **TypeScript 项目**
   ```typescript
   // 使用 TSDoc 和类型定义生成
   // 工具选择：
   // - TypeDoc
   // - Swagger UI
   // - OpenAPI Generator
   ```

3. **通用解决方案**
   ```yaml
   # Git hooks 配置 (.git/hooks/pre-commit)
   #!/bin/bash
   # 检测 API 文件变更
   if git diff --cached --name-only | grep -E "(api|router|model)"; then
       npm run docs:generate
       git add docs/
   fi
   ```

**最佳实践**：

1. **注释规范**
   ```python
   # 使用标准注释格式
   def create_user(
       username: str = Field(..., description="用户名"),
       email: EmailStr = Field(..., description="邮箱地址")
   ) -> User:
       """
       创建新用户
       
       Args:
           username: 必需，长度 3-20 字符
           email: 必需，有效的邮箱格式
           
       Returns:
           User: 创建的用户对象，包含 ID 和创建时间
           
       Raises:
           400: 用户名或邮箱格式错误
           409: 用户名或邮箱已存在
       """
   ```

2. **版本控制**
   - 所有文档变更必须通过 PR 审核
   - 破坏性变更需要 major 版本号更新
   - 保留历史版本的文档，支持 API 版本切换

3. **质量保证**
   ```bash
   # CI/CD 检查
   make docs-test  # 验证文档与代码同步
   make api-lint   # 检查 API 设计规范
   make integration-test # 运行 API 集成测试
   ```

**监控与告警**：

1. **文档同步状态**
   - 在项目 README 中显示文档最后更新时间
   - 定期检查代码与文档的一致性
   - 发现不同步时自动创建修复任务

2. **使用统计**
   - 记录接口调用频率，识别常用接口
   - 监控废弃接口的使用情况
   - 生成 API 使用报告，指导优化方向

3. **自动化告警**
   ```yaml
   # GitHub Actions 配置
   name: API Documentation Check
   on:
     push:
       paths: ['src/api/**', 'src/models/**']
   jobs:
     check-docs:
       runs-on: ubuntu-latest
       steps:
         - uses: actions/checkout@v3
         - name: Generate Docs
           run: npm run docs:generate
         - name: Check Changes
           run: |
             if git diff --quiet docs/; then
               echo "✅ 文档已自动更新"
             else
               echo "❌ 发现文档变更，请提交更新"
               exit 1
             fi
     ```