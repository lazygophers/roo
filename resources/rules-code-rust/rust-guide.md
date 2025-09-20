---
name: rust-guide
title: Rust编程风格指南
description: "Rust编程语言风格指南权威总结，综合官方文档与社区最佳实践，涵盖命名约定、格式化、工具使用等核心规范"
category: 语言指南
language: rust
priority: high
tags: [Rust, 编程规范, 风格指南, 最佳实践]
sections:
  - "核心原则：清晰性、一致性、惯例优于配置"
  - "命名约定：crates、modules、types、functions等"
  - "格式化：行长、缩进、use声明"
  - "工具推荐：rustfmt、clippy"
tools:
  - "rustfmt：官方格式化工具"
  - "clippy：代码检查工具"
references:
  - "Rust官方文档"
  - "社区广泛认可的最佳实践"
---

# Rust 编程风格指南

## 🔧 技术栈
- Rust 1.70+, Cargo, serde, tokio
- IDE: VSCode + rust-analyzer, IntelliJ Rust
- 工具: rustfmt, clippy, cargo-audit

## 📝 命名规范

| 元素 | 命名法 | 示例 |
|------|--------|------|
| Crates | `snake_case` | `my_crate` |
| Modules | `snake_case` | `user_profile` |
| Types/Traits | `UpperCamelCase` | `User`, `Clone`, `HttpError` |
| Enum Variants | `UpperCamelCase` | `Status::Active` |
| Functions/Variables | `snake_case` | `get_user()`, `user_name` |
| Constants/Statics | `SCREAMING_SNAKE_CASE` | `MAX_SIZE` |
| Generics | 简短大写 | `T`, `K`, `V` |
| Macros | `snake_case!` | `println!`, `vec!` |

## 🏷️ 类型/接口定义

```rust
// 结构体定义
#[derive(Debug, Clone)]
pub struct User {
    pub id: u64,
    pub name: String,
}

// 枚举定义
#[derive(Debug, PartialEq)]
pub enum Status {
    Active,
    Inactive,
    Pending { since: DateTime<Utc> },
}

// 特征定义
pub trait Repository<T> {
    type Error;
    fn save(&mut self, item: T) -> Result<(), Self::Error>;
}
```

## 🧪 测试规范

```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_user_creation() {
        let user = User::new("alice");
        assert_eq!(user.name, "alice");
        assert!(user.id > 0);
    }
    
    #[test]
    #[should_panic(expected = "invalid name")]
    fn test_invalid_user() {
        User::new("");
    }
}
```

## ✅ 核心要求
- 使用rustfmt自动格式化（100字符行宽，4空格缩进）
- 启用clippy检查：`cargo clippy -- -D warnings`
- use声明分组：std → 外部crate → 内部模块
- 优先使用`?`操作符处理错误
- 避免不必要的`.clone()`和分配
- 使用`cargo test`确保测试覆盖
- 公共API必须有文档注释(`///`)
