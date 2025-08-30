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

| 操作 | 命令 | 功能说明 |
|------|------|----------|
| 创建环境 | `uv sync` | 初始化虚拟环境并安装所有依赖 |
| 添加依赖 | `uv add <package>` | 将新包添加到项目依赖 |
| 运行程序 | `uv run <main.py>` | 在虚拟环境中执行脚本 |

### Yarn 包管理（前端）

**核心原则**：
- 前端项目必须使用 Yarn 作为包管理器
- 禁止使用 npm 直接安装依赖
- 所有依赖版本必须锁定在 `yarn.lock` 文件中

| 操作 | 命令 | 功能说明 |
|------|------|----------|
| 安装依赖 | `yarn install` | 根据 package.json 安装所有依赖 |
| 添加依赖 | `yarn add <package>` | 添加生产环境依赖 |
| 添加开发依赖 | `yarn add -D <package>` | 添加开发环境依赖 |
| 升级依赖 | `yarn upgrade <package>` | 升级指定包到最新版本 |
| 移除依赖 | `yarn remove <package>` | 移除指定依赖 |
| 运行脚本 | `yarn <script>` | 执行 package.json 中定义的脚本 |

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

**后端测试**：
- 直接访问 http://localhost:14001/api 进行后端API测试

## 🏗️ 技术栈

```yaml
# 核心技术栈
languages:
  - python      # 后端语言
  - typescript  # 前端语言（优先）
  - javascript  # 前端语言（兼容）
  - vue         # 前端框架

frameworks:
  backend: "fastapi"           # 后端框架
  frontend: "vue"              # Vue 前端框架
  build_tools: "vite/webpack"  # 构建工具
  database: "tinydb"           # 数据库
```

### TypeScript 优先原则

**核心要求**：
- **所有新项目必须使用 TypeScript**
- **现有 JS 项目逐步迁移至 TS**
- **类型定义覆盖率达到 95%+**
- **严格模式启用：`strict: true`**

**迁移策略**：
1. 先添加 `@types` 依赖
2. 文件扩展名改为 `.ts`/`.tsx`（Vue）或 `.vue`
3. 逐步添加类型注解
4. 启用严格模式检查

**类型规范**：
- 使用接口定义数据结构
- 优先使用联合类型而非 `any`
- 工具类型合理使用 `Partial`、`Pick`、`Omit`
- 泛型约束清晰明确
- Vue 组件使用 `defineComponent` 或 Composition API

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

**优先模式**: `code-vue`

**适用任务类型**:
- Vue 组件开发
- 前端页面构建
- 状态管理（Vuex/Pinia）
- 路由配置
- 前端工程化配置

**模式特点**:
- 深度理解 Vue 3 生态系统
- 熟练使用 Composition API
- 掌握 Vite 构建工具
- 支持 TypeScript 集成
- 擅长前端性能优化

### 模式选择决策流程

1. **识别任务性质**
   - 后端任务 → `code-python`
   - 前端任务 → `code-vue`
   - 架构设计 → `architect`
   - 文档编写 → `doc-writer`
   - 问题调试 → `debug`

2. **考虑技术栈**
   - Python 相关 → 优先 `code-python`
   - Vue/TypeScript → 优先 `code-vue`
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
前端界面 → code-vue
数据库设计 → architect
    ↓ 结果整合
完整系统交付
```

#### 技术迁移场景

```
迁移任务 → orchestrator
    ↓ 评估和规划
架构分析 → architect
代码重构 → code-python/code-vue
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
- **Vite**（推荐）：现代、快速、开箱即用，对 Vue 有原生支持
- **Webpack**：功能强大、生态完善
- 必须配置：
  - 代码分割（Code Splitting）
  - 懒加载（Lazy Loading）
  - Tree Shaking
  - Source Map
- Vue 项目推荐使用 Vite 以获得最佳开发体验

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
- 禁止在组件文件中使用内联样式
- 禁止使用 `!important` 覆盖样式优先级

**样式组织规范**：

1. **模块化样式**
   - 每个组件必须有独立的样式文件
   - 样式文件命名：`ComponentName.module.css`（Vue）
   - 使用 CSS Modules 或 Scoped CSS 避免全局污染

2. **样式文件结构**
   ```
   src/
   ├── styles/
   │   ├── variables.css      # CSS 变量定义
   │   ├── mixins.css         # 混合器定义
   │   ├── global.css         # 全局样式
   │   └── components/        # 组件样式目录
   │       ├── Button.module.css
   │       └── Card.module.css
   └── components/
       ├── Button/
       │   ├── Button.vue
       │   └── Button.module.css
       └── Card/
           ├── Card.vue
           └── Card.module.css
   ```

3. **CSS 命名规范**
   - 使用 BEM（Block Element Modifier）命名规范
   - 类名使用小写字母，单词间用连字符 `-` 连接
   - 避免使用标签选择器和 ID 选择器

4. **响应式设计**
   - 必须使用相对单位（rem、em、%、vw、vh）
   - 使用 CSS Grid 或 Flexbox 进行布局
   - 媒体查询必须使用移动优先（mobile-first）策略

5. **主题支持**
   - 所有颜色、字体、间距等必须使用 CSS 变量
   - 支持亮色/暗色主题切换
   - 主题变量统一在 `variables.css` 中定义

**样式检查**：
- 使用 Stylelint 进行代码检查
- 配合 Prettier 进行格式化
- 在 CI/CD 流程中加入样式检查环节

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