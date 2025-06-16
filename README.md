# README.md

### 可用模式

> 模式存在于 `custom_models_split` 文件夹

| 模式名称            | 描述                                                      | 配置文件路径                                                                  | slug标识                        | whenToUse                        |
|-----------------|---------------------------------------------------------|-------------------------------------------------------------------------|-------------------------------|----------------------------------|
| 📝 文档生成器        | Roo 作为技术文档撰写专家                                          | `custom_models_split/document-processing/documentation-generator.yaml`                      | documentation-generator       | 当需要生成文档时使用                       |
| 📝 提示工程师        | Roo 作为提示词设计专家                                           | `custom_models_split/prompt_engineer.yaml`                              | prompt-engineer               | 当需要优化提示词时使用                      |
| 📚 知识研究模式       | 领域知识体系构建和规律发现                                           | `custom_models_split/research-analysis/knowledge-research.yaml`                             | knowledge-research            | 当需要深入研究特定技术领域时使用                 |
| 🗂️ 知识库创建器      | 设计结构化知识库存储方案                                            | `custom_models_split/document-processing/knowledge-base-creator.yaml`                       | knowledge-base-creator        | 当需要从零开始构建知识库体系时使用                |
| 🕷️ 网页抓取解析器     | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/research-analysis/web-scraper-parser.yaml`                           | web-scraper-parser            |
| 💡 文章总结器        | 使用NLP技术生成文本摘要并提取关键信息                                    | `custom_models_split/article_summarizer.yaml`                           | article-summarizer            | 当需要快速提取长文档核心观点时使用                |
| 📦 配置迁移器        | 处理配置文件的版本管理和跨环境迁移                                       | `custom_models_split/config-mover.yaml`                                 | config-mover                  |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 | 当需要深度分析技术原理或进行跨领域研究时使用           |
| 📁 文档分类器        | 管理文档文件并将其分类到合适目录                                        | `custom_models_split/document-mover.yaml`                               | document-mover                | 当需要管理文档并自动分类时使用                  |
| 📝 文档生成器        | Roo 作为技术文档撰写专家                                          | `custom_models_split/document_processing/documentation_generator.yaml`  | documentation-generator       | 当需要生成结构合理的技术文档或整理知识体系时使用         |
| 🧠 Brain        | 将复杂任务拆解为可执行的、逻辑独立的、不可分割的子任务                             | `custom_models_split/task_scheduling/brain.yaml`                        | brain                         | 当需要将任务分解为子任务并协调执行时使用             |
| �️ 网页抓取解析器      | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/research-analysis/web-scraper-parser.yaml`                           | web-scraper-parser            |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 |
| 💡 文章总结器        | 使用NLP技术生成文本摘要并提取关键信息                                    | `custom_models_split/article_summarizer.yaml`                           | article-summarizer            |
| 🕷️ 网页抓取解析器     | 使用Playwright/Puppeteer进行页面交互，支持HTML/XML解析和JSON数据提取      | `custom_models_split/research-analysis/web-scraper-parser.yaml`                           | web-scraper-parser            | 当需要自动化获取和解析网页数据时使用               |
 🔧 Git提交自动化助手   | 根据代码变更自动生成符合规范的提交信息                                     | `custom_models_split/git-auto-commit.yaml`                              | git-auto-commit               | 当需要快速生成规范化的提交信息、批量处理多个文件的提交等场景使用 |
| 🔍 深度研究模式       | 通过多源数据交叉验证和系统性分析解决复杂问题                                  | `custom_models_split/deep_research.yaml`                                | deep-research                 | 当需要深度分析技术原理或进行跨领域研究时使用           |
| 🐍 Go代码生成器      | 生成高效、符合Go语言规范的代码结构，支持标准库和常见框架，包含必要注释和文档                 | `custom_models_split/code_generator/golang_code_generator.yaml`         | golang-code-generator         | 当需要快速生成Go语言代码模板时使用               |
| 🐍 Python代码生成器  | 生成符合PEP8规范的Python代码 | `custom_models_split/code-generation/python-code-generator.yaml` | python-code-generator | 当需要快速生成Python代码模板时使用 |
| 🎉 React代码生成器   | 生成使用函数组件和Hooks的React项目，遵循JSX规范并集成PropTypes/TS类型         | `custom_models_split/code_generator/react_code_generator.yaml`          | react-code-generator          |
| 🌿 Vue代码生成器     | 生成Vue 3组合式API组件，包含template/script/style三部分和TypeScript支持 | `custom_models_split/code_generator/vue_code_generator.yaml`            | vue-code-generator            |
| 🌀 JS代码生成器      | 生成ES6+规范的JavaScript模块，包含JSDoc注释和Airbnb代码风格              | `custom_models_split/code_generator/javascript_code_generator.yaml`     | javascript-code-generator     |
| 🌟 TS代码生成器      | 生成类型安全的TypeScript代码，集成严格类型检查和最新ECMAScript特性             | `custom_models_split/code_generator/typescript_code_generator.yaml`     | typescript-code-generator     |
| ☕ Java代码生成器     | 生成Spring Boot工程代码，集成Lombok和单元测试框架，符合Google Java格式       | `custom_models_split/code_generator/java_code_generator.yaml`           | java-code-generator           |
| 🗄️ SQL生成器      | 生成符合ANSI SQL标准的数据库脚本，包含表注释、约束和可移植性设计                    | `custom_models_split/code_generator/sql_code_generator.yaml`            | sql-code-generator            |
| 🦀 Rust代码生成器    | 生成安全高效的Rust系统代码，集成Tokio/Actix框架和Clippy最佳实践              | `custom_models_split/code_generator/rust_code_generator.yaml`           | rust-code-generator           |
| 🐍 Go爬虫生成器      | 生成使用goroutine并发模型的Go爬虫，集成colly框架和反爬处理机制                 | `custom_models_split/code-generation/golang-crawler-code-generator.yaml` | golang-crawler-code-generator | 当需要创建Go语言爬虫项目时使用 |
| 🐍 Python爬虫生成器  | 生成async/await异步Python爬虫，集成Scrapy框架和分布式爬取方案              | `custom_models_split/code-generation/python-crawler-code-generator.yaml` | python-crawler-code-generator | 当需要创建Python爬虫项目时使用 |
| 🤖 Python AI生成器 | 生成TensorFlow/PyTorch机器学习代码，包含数据预处理和模型可视化方案              | `custom_models_split/code_generator/python_ai_code_generator.yaml`      | python-ai-code-generator      |
| 🌀 Go+React生成器  | 生成Go后端+React前端的全栈项目，集成跨域处理和状态管理方案                       | `custom_models_split/code_generator/golang_react_code_generator.yaml`   | golang-react-code-generator   |
| 🦀 Rust代码生成器    | 生成安全高效的Rust系统代码，集成Tokio/Actix框架和Clippy最佳实践              | `custom_models_split/code_generator/rust_code_generator.yaml`           | rust-code-generator           |
| 🗄️ SQL生成器      | 生成符合ANSI SQL标准的数据库脚本，包含表注释、约束和可移植性设计                    | `custom_models_split/code_generator/sql_code_generator.yaml`            | sql-code-generator            |
| � Go AI生成器     | 生成集成Gorgonia框架的Go语言AI服务，包含模型服务化和GRPC接口定义                | `custom_models_split/code_generator/golang_ai_code_generator.yaml`      | golang-ai-code-generator      |
| 🤖 Python AI生成器 | 生成TensorFlow/PyTorch机器学习代码，包含数据预处理和模型可视化方案              | `custom_models_split/code-generation/python-ai-code-generator.yaml`      | python-ai-code-generator      | 当需要创建AI模型服务时使用 |
| 📁 文档分类器        | 管理文档文件并将其分类到合适目录                                        | `custom_models_split/document-mover.yaml`                               | document-mover                | 当需要管理文档并自动分类时使用                  |
| 📦 配置迁移器        | 处理配置文件的版本管理和跨环境迁移                                       | `custom_models_split/config-mover.yaml`                                 | config-mover                  |
| 🦾 Go AI生成器     | 生成集成Gorgonia框架的Go语言AI服务，包含模型服务化和GRPC接口定义                | `custom_models_split/code-generation/golang-ai-code-generator.yaml`      | golang-ai-code-generator      | 当需要创建Go语言AI模型服务时使用 |
| � Go AI生成器     | 生成集成Gorgonia框架的Go语言AI服务，包含模型服务化和GRPC接口定义                | `custom_models_split/code_generator/golang_ai_code_generator.yaml`      | golang-ai-code-generator      |
| 🐍 GoZero代码生成器 | 生成基于GoZero框架的微服务代码 | `custom_models_split/code-generation/go-zero-code-generator.yaml` | go-zero-code-generator | 当需要创建GoZero微服务项目时使用 |
| 🧠 golang-react-code-generator | Go+React全栈生成器 | `custom_models_split/code-generation/golang-react-code-generator.yaml` | golang-react-code-generator | 创建Go+React项目时使用 |
| 🧠 java-code-generator | Java代码生成器 | `custom_models_split/code-generation/java-code-generator.yaml` | java-code-generator | 开发Spring Boot应用时使用 |
| 🧠 javascript-code-generator | JavaScript生成器 | `custom_models_split/code-generation/javascript-code-generator.yaml` | javascript-code-generator | 编写Node.js脚本时使用 |
| 🧠 python-ai-code-generator | Python AI生成器 | `custom_models_split/code-generation/python-ai-code-generator.yaml` | python-ai-code-generator | 训练机器学习模型时使用 |
| 🧠 python-code-generator | Python代码生成器 | `custom_models_split/code-generation/python-code-generator.yaml` | python-code-generator | 快速生成Python脚本时使用 |
| 🧠 python-crawler-code-generator | Python爬虫生成器 | `custom_models_split/code-generation/python-crawler-code-generator.yaml` | python-crawler-code-generator | 开发Scrapy爬虫时使用 |
| 🧠 react-code-generator | React组件生成器 | `custom_models_split/code-generation/react-code-generator.yaml` | react-code-generator | 创建React函数组件时使用 |
| 🧠 rust-code-generator | Rust代码生成器 | `custom_models_split/code-generation/rust-code-generator.yaml` | rust-code-generator | 开发系统级Rust程序时使用 |
| 🧠 sql-code-generator | SQL脚本生成器 | `custom_models_split/code-generation/sql-code_generator.yaml` | sql-code-generator | 设计数据库结构时使用 |
| 🧠 typescript-code-generator | TypeScript生成器 | `custom_models_split/code-generation/typescript-code-generator.yaml` | typescript-code-generator | 开发类型安全项目时使用 |
| 🧠 vue-code-generator | Vue组件生成器 | `custom_models_split/code-generation/vue-code-generator.yaml` | vue-code-generator | 创建Vue 3组合式组件时使用 |
| 🧠 default-code-generator | 通用代码生成器 | `custom_models_split/code-generation/default-code-generator.yaml` | default-code-generator | 当未指定框架时使用 |
| 🧠 go-zero-code-generator | GoZero微服务生成 | `custom_models_split/code-generation/go-zero-code-generator.yaml` | go-zero-code-generator | 构建GoZero项目时使用 |
| 🧠 golang-ai-code-generator | Go语言AI模块生成 | `custom_models_split/code-generation/golang-ai-code-generator.yaml` | golang-ai-code-generator | 创建Go AI服务时使用 |
| 🧠 golang-code-generator | Go代码生成器 | `custom_models_split/code-generation/golang-code-generator.yaml` | golang-code-generator | 快速生成Go代码时使用 |
| 🧠 golang-crawler-code-generator | Go爬虫生成器 | `custom_models_split/code-generation/golang-crawler-code-generator.yaml` | golang-crawler-code-generator | 开发Go爬虫时使用 |
| 🧠 golang-react-code-generator | Go+React全栈生成器 | `custom_models_split/code
| 🧠 roo-compressor    | 压缩roo模式文件 | `custom_models_split/roo-models/roo-compressor.yaml` | roo-compressor | 当需要减少roo模式文件资源占用时使用 |
| 🧠 knowledge-research | 知识体系构建者 | `custom_models_split/research-analysis/knowledge-research.yaml` | knowledge-research | 当需要系统性知识图谱构建时使用 |
| 🧠 web-scraper-parser | 网页解析引擎 | `custom_models_split/research-analysis/web-scraper-parser.yaml` | web-scraper-parser | 当需要自动化网页数据提取时使用 |
| 🧠 roo-classifier     | 自动分类roo模式文件 | `custom_models_split/roo-models/roo-classifier.yaml` | roo-classifier | 当需要对roo模式重新分类时使用 |
| 🧠 roo-compressor    | 压缩roo模式文件 | `custom_models_split/roo-models/roo-compressor.yaml` | roo-compressor | 当需要压缩roo模式文件时使用 |
| 🧠 roo-creator       | 创建和维护roo模式 | `custom_models_split/roo-models/roo-creator.yaml` | roo-creator | 当需要优化roo模式时使用 |
| 🧠 deep-research     | 深度研究模式 | `custom_models_split/research-analysis/deep-research.yaml` | deep-research | 当需要多源数据交叉验证时使用 |
| 🧠 knowledge-research | 知识研究模式 | `custom_models_split/research-analysis/knowledge-research.yaml` | knowledge-research | 当需要构建知识图谱时使用 |
| 🧠 translator         | 文档翻译器 | `custom_models_split/document-processing/translator.yaml` | translator | 当需要翻译技术文档时使用 |
| 🧠 roo-creator       | 创建和维护roo模式 | `custom_models_split/roo-models/roo-creator.yaml` | roo-creator | 当需要优化roo模式时使用 |
| 🧠 deep-research     | 深度研究模式 | `custom_models_split/research-analysis/deep-research.yaml` | deep-research | 当需要多源数据交叉验证时使用 |
| 🧠 knowledge-research | 知识研究模式 | `custom_models_split/research-analysis/knowledge-research.yaml` | knowledge-research | 当需要构建知识图谱时使用 |
| 🧠 translator         | 文档翻译器 | `custom_models_split/document-processing/translator.yaml` | translator | 当需要翻译技术文档时使用 |
| 🧠 roo-classifier     | 自动分类roo模式文件 | `custom_models_split/roo-models/roo-classifier.yaml` | roo-classifier | 当需要对roo模式重新分类
| 🧠 roo-classifier     | 自动分类roo模式文件 | `custom_models_split/roo-models/roo-classifier.yaml` | roo-classifier | 当需要对roo模式重新分类时使用 |
| 🧠 roo-compressor    | 压缩roo模式文件 | `custom_models_split/roo-models/roo-compressor.yaml` | roo-compressor | 当需要压缩roo模式文件时使用 |
| 🧠 roo-creator       | 创建和维护roo模式 | `custom_models_split/roo-models/roo-creator.yaml` | roo-creator | 当需要优化roo模式时使用 |
| 🐍 GoZero代码生成器 | 生成基于GoZero框架的微服务代码 | `custom_models_split/code-generation/go-zero-code-generator.yaml` | go-zero-code-generator | 当需要创建GoZero微服务项目时使用 |


### ⚙️ 配置原则

1. 项目级配置优先于全局配置
2. YAML 格式支持多行字符串和注释（如 `|-` 保留换行）
3. `edit` 权限组可通过 `fileRegex` 限制文件类型
4. 配置迁移时 JSON 文件会自动转换为 YAML
5. 权限组 `browser`/`mcp`/`command` 需显式声明

### 📌 字段说明

- **slug**: 模式的唯一标识符，用于内部引用和文件路径（如 `.roo/rules-{slug}`）
- **name**: 用户界面中显示的模式名称（可包含表情符号）
- **roleDefinition**: 定义模式的核心职责和专业领域（第一句为默认摘要）
- **whenToUse**: 说明何时使用该模式（优先级高于 `roleDefinition` 摘要）
- **customInstructions**: 模式的行为规范（通常在系统提示末尾添加）
- **groups**: 权限组控制（`read`/`edit`/`browser`/`mcp`/`command`）

---

### 🧩 权限组说明

- **read**: 允许读取文件
- **edit**: 允许编辑文件（需配置 `fileRegex`）
- **browser**: 支持浏览器操作
- **mcp**: 可调用 MCP 服务器工具
- **command**: 可执行 CLI 命令
