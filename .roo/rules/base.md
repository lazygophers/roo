## 基本规则

- 虚拟环境路径 `.venv`
- 使用 `uv python` 或 `.venv/bin/python`替代`python`
- 使用 uv 作为包管理工具和环境隔离工具
  - 创建虚拟环境 `uv sync`
  - 安装依赖 `uv add <package>`
  - 运行程序 `uv run <main.py>`
- 使用 python + vue 作为主要开发语言
  - 使用 fastapi 作为主框架
  - 使用 vuepy 作为前端框架
  - 使用 tinydb 作为数据库
- 任何决策前都要获得用户授权，包括但不限于：
  - 更新任务清单
  - 规划任务
  - 确定任务执行顺序
  - 确认方案
- 需确保测试覆盖率不低于 90%
- 需确保代码质量
- 合理的分层分包
- 使用渐进式开发的方式，先实现一个最小化的功能，然后逐步添加功能

## 产品说明

- 这是一个帮助用户对多个 roo code 的规则配置进行自定义选择、组合的工具
- 模式配置位于 `resources/modes` 目录下
  - 不同模式有这对应的特异性规则，位于 `resources/rules-<slug>/` 目录下
  - `resources/rules/` 目录下的规则是所有人都生效的规则
- 全局公共的前置规则位于 `resources/hooks/brefor.md` 文件
- 全局公共的后置规则位于 `resources/hooks/after.md` 文件
- 启动时，自动扫描并生成索引更新到数据库的中。同时需要监听文件变化，并更新索引
- 允许用户选择后，预览和导出规则
- 导出的规则样式参考 `custom_mmodels.yaml` 文件
- 允许导出配置，并允许用户通过 shell，指定配置导出内容
- 允许用户通过 shell，指定配置生成导出的规则
