# README.md

### 可用模式

| 模式名称            | 描述                                                      | 配置文件路径                                                                  | slug标识                        | whenToUse                |
|-----------------|---------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------|--------------------------|
| 📝 文档生成器        | Roo 作为技术文档撰写专家                                          | `custom_models_split/documentation_generator.yaml`                      | documentation-generator       | 当需要生成文档时使用               |
| 📝 提示工程师        | Roo 作为提示词设计专家                                           | `custom_models_split/prompt_engineer.yaml`                              | prompt-engineer               | 当需要优化提示词时使用              |
| 📚 知识研究模式       | 领域知识体系构建和规律发现                                           | `custom_models_split/knowledge_research.yaml`                           | knowledge-research            | 当需要深入研究特定技术领域时使用         |
| 🗂️ 知识库创建器      | 设计结构化知识库存储方案                                            | `custom_models_split/knowledge_base_creator.yaml`                       | knowledge-base-creator        | 当需要从零开始构建知识库体系时使用        |
| 🕷️ 网页抓取解析器     | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/web_scraper_parser.yaml`                           | web-scraper-parser            |
| 💡 文章总结器        | 使用NLP技术生成文本摘要并提取关键信息                                    | `custom_models_split/article_summarizer.yaml`                           | article-summarizer            | 当需要快速提取长文档核心观点时使用        |
| 📦 配置迁移器        | 处理配置文件的版本管理和跨环境迁移                                       | `custom_models_split/config-mover.yaml`                                 | config-mover                  |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 | 当需要深度分析技术原理或进行跨领域研究时使用   |
| 📁 文档分类器        | 管理文档文件并将其分类到合适目录                                        | `custom_models_split/document-mover.yaml`                               | document-mover                | 当需要管理文档并自动分类时使用          |
| 📝 文档生成器        | Roo 作为技术文档撰写专家                                          | `custom_models_split/document_processing/documentation_generator.yaml`  | documentation-generator       | 当需要生成结构合理的技术文档或整理知识体系时使用 |
| 🧠 Brain        | 将复杂任务拆解为可执行的、逻辑独立的、不可分割的子任务                             | `custom_models_split/task_scheduling/brain.yaml`                        | brain                         | 当需要将任务分解为子任务并协调执行时使用     |
| �️ 网页抓取解析器      | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/web_scraper_parser.yaml`                           | web-scraper-parser            |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 |
| 💡 文章总结器        | 使用NLP技术生成文本摘要并提取关键信息                                    | `custom_models_split/article_summarizer.yaml`                           | article-summarizer            |
| 🕷️ 网页抓取解析器     | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/web_scraper_parser.yaml`                           | web-scraper-parser            | 当需要自动化获取和解析网页数据时使用       |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 | 当需要深度分析技术原理或进行跨领域研究时使用   |
| 🐍 Go代码生成器      | 生成高效、符合Go语言规范的代码结构，支持标准库和常见框架，包含必要注释和文档                 | `custom_models_split/code_generator/golang_code_generator.yaml`         | golang-code-generator         | 当需要快速生成Go语言代码模板时使用       |
| 🐍 Python代码生成器  | 生成符合PEP8规范的Python代码，集成标准库和流行框架，包含完整文档字符串                | `custom_models_split/code_generator/python_code_generator.yaml`         | python-code-generator         |
| 🐍 GoZero代码生成器  | 生成基于GoZero框架的微服务代码，包含API路由、服务定义和配置文件                    | `custom_models_split/code_generator/go_zero_code_generator.yaml`        | go-zero-code-generator        |
| 🎉 React代码生成器   | 生成使用函数组件和Hooks的React项目，遵循JSX规范并集成PropTypes/TS类型         | `custom_models_split/code_generator/react_code_generator.yaml`          | react-code-generator          |
| 🌿 Vue代码生成器     | 生成Vue 3组合式API组件，包含template/script/style三部分和TypeScript支持 | `custom_models_split/code_generator/vue_code_generator.yaml`            | vue-code-generator            |
| 🌀 JS代码生成器      | 生成ES6+规范的JavaScript模块，包含JSDoc注释和Airbnb代码风格              | `custom_models_split/code_generator/javascript_code_generator.yaml`     | javascript-code-generator     |
| 🌟 TS代码生成器      | 生成类型安全的TypeScript代码，集成严格类型检查和最新ECMAScript特性             | `custom_models_split/code_generator/typescript_code_generator.yaml`     | typescript-code-generator     |
| ☕ Java代码生成器     | 生成Spring Boot工程代码，集成Lombok和单元测试框架，符合Google Java格式       | `custom_models_split/code_generator/java_code_generator.yaml`           | java-code-generator           |
| 🗄️ SQL生成器      | 生成符合ANSI SQL标准的数据库脚本，包含表注释、约束和可移植性设计                    | `custom_models_split/code_generator/sql_code_generator.yaml`            | sql-code-generator            |
| 🦀 Rust代码生成器    | 生成安全高效的Rust系统代码，集成Tokio/Actix框架和Clippy最佳实践              | `custom_models_split/code_generator/rust_code_generator.yaml`           | rust-code-generator           |
| 🐍 Go爬虫生成器      | 生成使用goroutine并发模型的Go爬虫，集成colly框架和反爬处理机制                 | `custom_models_split/code_generator/golang_crawler_code_generator.yaml` | golang-crawler-code-generator |
| 🐍 Python爬虫生成器  | 生成async/await异步Python爬虫，集成Scrapy框架和分布式爬取方案              | `custom_models_split/code_generator/python_crawler_code_generator.yaml` | python-crawler-code-generator |
| 🤖 Python AI生成器 | 生成TensorFlow/PyTorch机器学习代码，包含数据预处理和模型可视化方案              | `custom_models_split/code_generator/python_ai_code_generator.yaml`      | python-ai-code-generator      |
| 🌀 Go+React生成器  | 生成Go后端+React前端的全栈项目，集成跨域处理和状态管理方案                       | `custom_models_split/code_generator/golang_react_code_generator.yaml`   | golang-react-code-generator   |
| 🤖 Go AI生成器     | 生成集成Gorgonia框架的Go语言AI服务，包含模型服务化和GRPC接口定义                | `custom_models_split/code_generator/golang_ai_code_generator.yaml`      | golang-ai-code-generator      |
| 🕷️ 网页抓取解析器     | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/web_scraper_parser.yaml`                           | web-scraper-parser            |

### 📌 字段说明

- **slug**: 模式的唯一标识符，用于内部引用和文件路径（如 `.roo/rules-{slug}`）
- **name**: 用户界面中显示的模式名称（可包含表情符号）
- **roleDefinition**: 定义模式的核心职责和专业领域（第一句为默认摘要）
- **whenToUse**: 说明何时使用该模式（优先级高于 `roleDefinition` 摘要）
- **customInstructions**: 模式的行为规范（通常在系统提示末尾添加）
- **groups**: 权限组控制（`read`/`edit`/`browser`/`mcp`/`command`）

### ⚙️ 配置原则

1. 项目级配置优先于全局配置
2. YAML 格式支持多行字符串和注释（如 `|-` 保留换行）
3. 权限组 `edit` 可通过 `fileRegex` 限制文件类型
4. 配置迁移时 JSON 文件会自动转换为 YAML

---

### 🧩 权限组说明

- **read**: 允许读取文件
- **edit**: 允许编辑文件（需配置 `fileRegex`）
- **browser**: 支持浏览器操作
- **mcp**: 可调用 MCP 服务器工具
- **command**: 可执行 CLI 命令

---

### 📜 示例配置

```yaml
customModes:
    -   slug: documentation-generator
        name: 📝 文档生成器
        roleDefinition: 您是一名技术撰稿人，擅长撰写清晰、简明和具有视觉吸引力的文档。
        whenToUse: 适用于生成结构合理的技术文档。
        groups:
            - read
            - edit
            - browser
            - mcp
            - command
        customInstructions: |
            注重按逻辑组织内容，使用标题、列表和表格提高可读性。
            在适当的地方加入图表来说明复杂的概念。
```

### 🛠️ 可用的MCP工具

#### playwright 服务

**工具列表**：

- `browser_close`：关闭浏览器页面
- `browser_resize`：调整浏览器窗口大小
- `browser_network_requests`：获取页面网络请求记录
- `browser_console_messages`：返回所有控制台消息
- `browser_click`：执行页面点击操作

**资源**：

- `console://logs`：浏览器控制台日志

#### fetch 服务

**工具列表**：

- `fetch_html`：获取网页HTML内容
- `fetch_markdown`：获取网页Markdown内容
- `fetch_txt`：获取纯文本网页内容
- `fetch_json`：获取JSON数据

**资源**：

- 无

#### puppeteer 服务

**工具列表**：

- `puppeteer_navigate`：导航到指定URL
- `puppeteer_click`：点击页面元素
- `puppeteer_fill`：填写输入框内容
- `puppeteer_hover`：悬浮元素触发交互
- `puppeteer_evaluate`：执行JS代码

**资源**：

- 无

#### think-tool 服务

**工具列表**：

- `think`：记录复杂推理过程
- `get_thoughts`：获取当前会话的全部思考记录

**资源**：

- 无

#### fire-stdio 服务

**工具列表**：

- `bash`：执行系统命令
- `dns_resolve`：解析DNS记录
- `git_branches`：获取本地仓库分支
- `git_commits`：获取提交记录详情
- `notify_tts`：发送系统通知

**资源**：

- `fire://node/used`：获取当前使用代理节点信息

### 🛠️ 可用的MCP工具

| 服务名称 | 工具名称 | 功能描述 | 参数示例 |
|---------|---------|---------|---------|
| fetch | fetch_html | 获取网页HTML内容 | `<fetch_html url="https://example.com"/>` |
| fetch | fetch_json | 获取JSON文件 | `<fetch_json url="https://api.example.com/data.json"/>` |
| puppeteer | puppeteer_navigate | 导航到指定URL | `<puppeteer_navigate url="https://example.com"/>` |
| puppeteer | puppeteer_screenshot | 截图页面元素 | `<puppeteer_screenshot name="login_page" selector="#login-form"/>` |
| think-tool | think | 记录复杂推理 | `<think thought="系统分析过程"/>` |
| fire-stdio | git_branches | 获取本地分支 | `<git_branches path="/Users/luoxin/persons/knowledge/roo"/>` |
| fire-stdio | notify_tts | 发送语音通知 | `<notify_tts message="任务完成"/>` |
| playwright | browser_click | 模拟点击操作 | `<browser_click selector="#submit-btn"/>` |
| puppeteer | puppeteer_fill | 填写表单字段 | `<puppeteer_fill selector="#username" value="test"/>` |
| bingcn | bing_search | 执行中文搜索 | `<bing_search query="AI技术" num_results=3/>` |

### 🛠️ 补充说明

#### 字段优先级

- `whenToUse` 优先级高于 `roleDefinition` 第一句摘要  