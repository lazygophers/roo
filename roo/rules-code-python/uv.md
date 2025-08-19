# uv 使用指南

## 虚拟环境与包管理 uv 工具

### 安装 uv

`curl https://docs.astral.sh/uv/install.sh | bash`

### 常用命令

| 功能         | 命令                         | 说明                                   |
| ------------ | ---------------------------- | -------------------------------------- |
| 创建虚拟环境 | `uv init`                    | 在指定目录创建虚拟环境（默认当前目录） |
| 激活虚拟环境 | `uv venv activate`           | 激活指定虚拟环境                       |
| 安装依赖     | `uv add <package>[@version]` | 安装包及指定版本                       |
| 移除依赖     | `uv remove <package>`        | 移除指定包                             |
| 更新依赖     | `uv update <package>`        | 更新指定包至最新版                     |
