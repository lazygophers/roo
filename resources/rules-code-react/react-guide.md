---
name: react-guide
title: React风格指南
description: "React风格指南总结，基于Airbnb广泛采纳的黄金标准，涵盖命名规范、文件结构、Props使用、State与Hooks等最佳实践"
category: language-guide
language: react
priority: high
tags: [React, JSX, 风格指南, 最佳实践, Airbnb]
sections:
  - "命名规范：文件、组件、引用、高阶组件、Props"
  - "文件结构：单一组件原则、目录组织"
  - "Props使用：布尔属性简写、默认Props、Props展开"
  - "State与Hooks：函数组件优先、useState、useEffect"
references:
  - "Airbnb React/JSX Style Guide"
  - "Google无官方React风格指南"
note: "虽然Google没有发布官方的React风格指南，但Airbnb的指南已成为社区广泛采纳的黄金标准"
---

# React 风格指南

本指南旨在总结业界公认的 React 最佳实践与风格指南。虽然 Google 没有发布官方的 React 风格指南，但 Airbnb 的 React/JSX 风格指南已成为社区广泛采纳的黄金标准。

[TOC]

## 1. 命名规范 (Naming Conventions)

| 类别         | 规则                                                                   | 示例                                                                                             |
| ------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------ |
| **文件**     | 使用帕斯卡命名法 (`PascalCase`) 和 `.jsx` (或 `.tsx`) 扩展名。         | `MyComponent.jsx`                                                                                |
| **组件**     | 组件名称应与文件名一致，并使用 `PascalCase`。                          | `function MyComponent() { ... }`                                                                 |
| **引用**     | React 组件引用使用 `PascalCase`，其实例使用 `camelCase`。              | `const myComponentInstance = <MyComponent />;`                                                   |
| **高阶组件** | HOC 名称应由 `hocName(WrappedComponent)` 组合而成。                    | `const withSubscription = (WrappedComponent) => { ... }`                                         |
| **Props**    | 避免使用 DOM 元素的原生属性名（如 `style`, `className`）用于其他目的。 | **Good**: `<MyComponent representationStyle={...} />`<br/>**Bad**: `<MyComponent style={...} />` |

---

## 2. 文件结构 (File Structure)

- **单一组件原则**: 每个文件只导出一个 React 组件。
  > 这使得组件更易于查找、阅读和测试。
- **目录组织**: 将组件、其样式文件和测试文件放在同一个目录中。
  ```
  /components
  └── /MyComponent
      ├── MyComponent.jsx
      ├── MyComponent.module.css
      └── MyComponent.test.js
  ```

---

## 3. Props 使用规范

- **布尔属性简写**: 如果 prop 的值为 `true`，请省略其值。

  ````jsx
  // Bad
  <MyComponent isVisible={true} />

  // Good
  <MyComponent isVisible />
  ```- **默认 Props**: 对于非必需的 Props，应使用 ES6 的默认参数来定义其默认值。
  ```jsx
  function MyComponent({ name = 'Guest' }) {
    return <div>Hello, {name}</div>;
  }
  ````

- **Props 展开**: 始终将 props 展开放在组件声明的最后，以确保可读性。

  ```jsx
  // Bad
  <MyComponent {...props} name="override" />

  // Good
  <MyComponent name="override" {...props} />
  ```

---

## 4. State 与 Hooks 使用规范

- **优先使用函数组件与 Hooks**: 除非需要类组件特有的生命周期方法（现代 React 中已很少见），否则应始终使用函数组件和 Hooks。
- **`useState`**: 用于管理简单的组件内部状态。

  ```jsx
  import React, { useState } from 'react';

  function Counter
  ```
