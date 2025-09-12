# Roo 配置管理系统 - 文档中心

## 📚 文档导航

欢迎使用 Roo 配置管理系统！这里是完整的文档中心，提供了从快速开始到深度定制的全面指导。

### 🚀 快速开始
- [README.md](../README.md) - 项目概述和快速安装指南
- [快速开始指南](#quick-start) - 5分钟快速体验

### 🏗️ 架构和设计
- [API 文档](./API.md) - 完整的 RESTful API 接口文档
- [前端技术文档](./Frontend.md) - React + TypeScript 前端架构
- [后端技术文档](./Backend.md) - FastAPI + Python 后端架构

### 🚀 部署运维
- [部署指南](./Deployment.md) - 开发、测试、生产环境部署
- [配置管理指南](./Configuration.md) - 系统配置和环境变量
- [监控和日志](./Monitoring.md) - 系统监控、日志分析

### 👥 开发指南
- [开发环境搭建](./Development.md) - 本地开发环境配置
- [贡献指南](./Contributing.md) - 如何为项目做贡献
- [代码规范](./CodeStyle.md) - 代码风格和最佳实践

### 📖 用户手册
- [用户使用手册](./UserGuide.md) - 详细的功能使用说明
- [常见问题](./FAQ.md) - 常见问题解答
- [故障排除](./Troubleshooting.md) - 问题诊断和解决方案

### 🔧 扩展开发
- [插件开发指南](./PluginDevelopment.md) - 自定义扩展开发
- [主题定制](./ThemeCustomization.md) - 界面主题定制
- [API 扩展](./APIExtension.md) - API 接口扩展

---

## <a id="quick-start"></a>🚀 5分钟快速开始

### 前置条件
- Python 3.12+
- Node.js 20+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/your-org/roo-config-management.git
cd roo-config-management
```

### 2. 启动后端服务
```bash
# 安装依赖
uv sync

# 启动后端 (端口 8000)
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 启动前端应用
```bash
# 新终端窗口
cd frontend
npm install
npm start  # 端口 3000
```

### 4. 访问应用
- 前端界面: http://localhost:3000
- API 文档: http://localhost:8000/docs
- 健康检查: http://localhost:8000/health

### 5. 基本使用
1. 在前端界面选择需要的 AI 模式和角色
2. 预览选中的配置
3. 点击"部署配置"到 VS Code 扩展
4. 在 VS Code 中享受增强的 AI 编码体验

---

## 📋 文档版本历史

| 版本 | 日期 | 主要更新 |
|------|------|----------|
| v1.0.0 | 2024-01 | 初始文档，包含基础架构和API |
| v1.1.0 | 2024-01 | 添加部署指南和配置管理 |
| v1.2.0 | 2024-01 | 完善开发指南和贡献流程 |

---

## 🤝 获取帮助

### 社区资源
- 📧 **邮件支持**: support@roo-ai.com
- 💬 **在线讨论**: GitHub Discussions
- 🐛 **问题报告**: GitHub Issues
- 📖 **Wiki 文档**: GitHub Wiki

### 紧急支持
如果您遇到紧急问题或安全漏洞，请直接发送邮件至 security@roo-ai.com

### 文档改进
发现文档问题或有改进建议？
1. 在 GitHub 上提交 Issue
2. 直接提交 Pull Request
3. 发送邮件至 docs@roo-ai.com

---

## 📄 许可证

本项目遵循 MIT 许可证，详情请查看 [LICENSE](../LICENSE) 文件。