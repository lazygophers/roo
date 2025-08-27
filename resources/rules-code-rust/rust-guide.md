---
name: rust-guide
title: Rust编程风格指南
description: "Rust编程语言风格指南权威总结，综合官方文档与社区最佳实践，涵盖命名约定、格式化、工具使用等核心规范"
category: language-guide
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

# Rust 编程语言风格指南权威总结

本指南旨在综合 Rust 官方文档与社区广泛认可的最佳实践，为您提供一份关于 Rust 编程风格的权威、详尽的参考。遵循统一的风格不仅能提升代码的可读性、可维护性，也是成为一名专业 Rust 开发者（Rustacean）的必经之路。

## 核心原则

Rust 的风格指南根植于几个核心原则：

- **清晰性 (Clarity)**: 代码首先是写给人读的。应优先选择最能清晰表达意图的写法。
- **一致性 (Consistency)**: 在整个项目中保持风格的统一至关重要。利用 `rustfmt` 和 `clippy` 等工具可以自动化地保证一致性。
- **惯例优于配置 (Convention over Configuration)**: Rust 社区已经形成了一套强大的编码惯例。遵循这些惯例可以减少沟通成本，让代码更容易被他人理解。

---

## 命名约定 (Naming Conventions)

| 元素                               | 命名法                  | 示例                                              |
| ---------------------------------- | ----------------------- | ------------------------------------------------- |
| **Crates**                         | `snake_case`            | `my_crate`                                        |
| **Modules**                        | `snake_case`            | `user_profile`                                    |
| **Types** (Structs, Enums, Traits) | `UpperCamelCase`        | `struct User;` `enum Role;` `trait Serializable;` |
| **Enum Variants**                  | `UpperCamelCase`        | `enum Role { Admin, Guest };`                     |
| **Functions, Methods, Variables**  | `snake_case`            | `fn get_user()` `let user_name = ...`             |
| **Constants**                      | `SCREAMING_SNAKE_CASE`  | `const MAX_CONNECTIONS: u32 = 100;`               |
| **Statics**                        | `SCREAMING_SNAKE_CASE`  | `static mut REQUEST_COUNT: u64 = 0;`              |
| **Generic Parameters**             | 简短的 `UpperCamelCase` | `fn foo<T: Trait>(arg: T)` `struct Point<X, Y>`   |
| **Macros**                         | `snake_case`!           | `println!`                                        |

---

## 格式化 (Formatting)

Rust 社区强烈推荐使用官方的格式化工具 `rustfmt` 来保证代码风格的统一。绝大多数格式化问题都可以通过配置和运行 `rustfmt` 解决。

### 行长 (Line Length)

- **建议**: 每行不超过 100 个字符。
- **工具**: `rustfmt` 默认会尝试将代码格式化到这个宽度内。

### 缩进 (Indentation)

- **标准**: 使用 4 个空格进行缩进，而不是制表符 (Tab)。
- **工具**: `rustfmt` 会自动处理。

### `use` 声明

- **分组与排序**: `use` 声明应该按字母顺序排列，并按照以下顺序分组，组间用空行隔开：

  1.  `std` 和 `core`
  2.  外部 Crate
  3.  项目内部模块 (`self`, `super`, `crate`)

  ```rust
  use std::collections::HashMap;
  use std::io::Write;
  ```
