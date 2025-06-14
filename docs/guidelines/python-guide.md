# Python编码规范指南（基于Google标准）

## 核心规则
1. **代码检查**：强制使用`pylint`静态分析（`pylintrc`配置）
2. **导入规范**：禁止`from package import *`，推荐`import package`
3. **异常处理**：优先专用异常类，禁止`assert`用于API验证
4. **全局状态**：禁止可变全局变量，常量使用全大写命名（如`MAX_VALUE=3`）

---

## 重点章节摘要
### 代码风格
- **缩进**：4空格（硬性要求）
- **行长度**：79字符（兼容旧显示器）
- **注释规范**：`TODO(username): 简短说明`

### 类型注解
- **基本规则**：参数/返回类型必写，禁止`typing.Any`
- **特殊场景**：循环导入时用`from __future__ import annotations`

### 争议点决策
| 规则                | 决策依据                          | 最终决策          |
|---------------------|-----------------------------------|-------------------|
| 三元表达式         | 可读性 vs 简洁性                  | 允许单行使用      |
| 全局状态           | 封装 vs 简单性                   | 禁止生产环境使用  |
| 嵌套函数/类        | 可测试性 vs 局部作用域优势        | 允许闭包场景使用  |

---

## 关键决策表
### 异常处理
```python
# Yes:
def connect(port):
    if port < 1024:
        raise ValueError("端口需≥1024")
    # 具体实现...

# No:
def connect(port):
    assert port >= 1024  # 禁止用断言替代显式检查
```

### 默认参数
```python
# Yes:
def process(data, cache=None):
    if cache is None:
        cache = {}

# No:
def process(data, cache=[]):  # 可变默认值陷阱
```

---

## 扩展阅读
- [pylint配置文件](https://google.github.io/styleguide/pylintrc)
- [PEP8官方规范](https://peps.python.org/pep-0008/)