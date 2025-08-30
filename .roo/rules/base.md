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
grep -rn "TODO\|FIXME" --include="*.py" --include="*.js" .

# 使用正则表达式搜索函数定义
grep -rn "^\s*def \w+" --include="*.py" .

# 搜索包含特定单词但不包含另一个单词的行
grep -rn "import.*pytest" --include="*.py" . | grep -v "test_"

# 搜索多个模式（OR 关系）
grep -rnE "(class|def) \w+.*:" --include="*.py" .

# 使用管道组合多个 grep 命令
grep -rn "async def" --include="*.py" . | grep -v "test_" | head -20

# 搜索并统计出现次数
grep -r "print(" --include="*.py" . | wc -l

# 在特定目录中搜索
grep -rn "API_KEY" src/ config/

# 搜索制表符或空格开头的注释
grep -rn "^[\t ]*#" --include="*.py" .
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

**后端测试**：

- 直接访问 http://localhost:14001/api 进行后端 API 测试

## 🏗️ 技术栈

```yaml
# 核心技术栈
languages:
  - python # 后端语言
  - typescript # 前端语言（优先）
  - javascript # 前端语言（兼容）
  - vue # 前端框架

frameworks:
  backend: "fastapi" # 后端框架
  frontend: "vue" # Vue 前端框架
  build_tools: "vite/webpack" # 构建工具
  database: "tinydb" # 数据库
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

   - 使用 CSS Modules 或 Scoped CSS 避免全局污染
   - 支持在 Vue 单文件组件中使用 `<style>` 标签

2. **样式文件结构**

   ```
   src/
   ├── styles/
   │   ├── variables.css      # CSS 变量定义
   │   ├── mixins.css         # 混合器定义
   │   ├── global.css         # 全局样式
   │   └── components/        # 组件样式目录（可选）
   │       ├── Button.module.css
   │       └── Card.module.css
   └── components/
       ├── Button/
       │   ├── Button.vue
       └── Card/
           ├── Card.vue（包含 <style> 标签）
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
