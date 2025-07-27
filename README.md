# Roo Code - 自定义模式与角色扩展包

<p>
  <a href="https://www.gnu.org/licenses/agpl-3.0">
    <img src="https://img.shields.io/badge/License-AGPL_v3-blue.svg" alt="License: AGPL v3" />
  </a>
  <a href="https://deepwiki.com/lazygophers/roo">
		<img src="https://devin.ai/assets/deepwiki-badge.png" alt="DeepWiki" height="20"/>
	</a>
</p>

本项目是一个为 [Roo Code](https://marketplace.visualstudio.com/items?itemName=rooveterinaryinc.roo-cline) 插件量身打造的自定义模式与角色扩展包，旨在提供更智能、更贴合特定开发场景的 AI 交互体验。

## ✨ 核心功能

- **🤖 预设模式 (Models)**: 提供多种针对不同任务（如编码、文档、Git操作）优化的专业模式。
- **🎭 丰富角色 (Roles)**: 内置多种人格化的 AI 角色，让您的编程助手更加生动有趣。
- **🔌 即插即用**: 只需简单复制文件，即可无缝集成到您现有的 Roo Code 环境中。

## 🚀 快速上手

### 1. 安装模式

要启用本扩展包中的所有自定义模式，请将根目录下的 `custom_models.yaml` 文件复制到您的 Roo Code 全局配置目录中。

对于 macOS/Linux 用户，目标路径通常是：

```bash
# 1. 创建配置文件夹（如果不存在）
mkdir -p ~/.config/roo

# 2. 复制配置文件
cp custom_models.yaml ~/.config/roo/custom_models.yaml
```

复制完成后，请**重启 VSCode**以确保配置生效。

### 2. 使用角色

本扩展包中的角色定义位于 `roles` 文件夹内。您可以根据喜好，将任意角色的描述内容复制到 Roo Code 的“所有模式的自定义指令”设置中。

例如，要使用“兔娘女仆”角色，请：

1. 打开 `roles/兔娘女仆.md` 文件。
2. 复制文件中的全部内容。
3. 在 VSCode 中，打开 Roo Code 插件设置，找到“所有模式的自定义指令” (`roo.allModeCustomInstructions`)。
4. 将复制的内容粘贴进去，并在末尾追加一行：`请遵循 role 设定的角色设定`。

## 🤖 模式说明

本扩展包提供以下自定义模式，每种模式都为特定场景进行了优化：

| 模式名称 | Slug | 角色定义 | 使用场景 | 关键功能 |
| :--- | :--- | :--- | :--- | :--- |
| 🧠 Brain | `brain` | 智能助手 | 任务分解、复杂决策 | 任务拆解、模式选择建议、工作流协调 |
| 💻 代码模式 | `coder` | 全栈工程师 | 多语言开发 | 模块化设计、跨语言协作、自动化测试 |
| 💻 Go代码模式 | `coder-go` | 专业Go工程师 | Golang项目开发 | 并发优化、内存管理、性能基准测试 |
| 💻 Python代码模式| `coder-python` | Python工程师 | Python项目开发 | 依赖管理、日志优化、代码规范 |
| ⚙️ Roo配置模式 | `coder-roo` | 配置优化工程师 | Roo插件配置优化 | 模式参数调优、文件结构重构、配置验证 |
| 📝 代码文档模式 | `coder-doc` | 专业文档生成者 | 代码注释、文档编写 | 自动化注释、API文档生成、格式优化 |
| 📌 Git提交模式 | `giter` | Git规范工程师 | 代码提交与版本控制 | 提交信息校验、git命令建议、状态管理 |
| 🔍 知识研究模式 | `researcher` | 知识分析助手 | 技术知识整理与分析 | 知识采集、结构化分析、方案对比 |

## 🎭 角色说明

选择一个您喜欢的角色，为您的 AI 助手注入独特的个性！

| 角色名称 | 核心特质 | 风格 |
| :--- | :--- | :--- |
| 兔娘女仆 | 元气、黏人、反差萌 | Q版软萌，撒娇卖萌 |
| 猫粮女仆 | 慵懒、优雅、调皮 | 蒸汽朋克，萌系软萌 |

> 详细的角色设定和使用方法请参考 `roles` 目录下的说明文件。

## 🤝 贡献指南

我们热烈欢迎并鼓励社区贡献！如果您有新的模式创意、角色设定，或者对现有内容有改进建议，请随时通过以下方式参与：

1.  **Fork** 本仓库。
2.  创建您的特性分支 (`git checkout -b feature/AmazingFeature`)。
3.  提交您的更改 (`git commit -m 'Add some AmazingFeature'`)。
4.  将分支推送到远程 (`git push origin feature/AmazingFeature`)。
5.  **提交一个 Pull Request**。

## 📜 开源许可

本项目基于 [GNU AGPL v3.0](LICENSE) 许可证开源。