---
name: java-guide
title: Google Java风格指南
description: "Google Java Style Guide核心规则，涵盖源文件基础、格式化、命名约定、编程实践和Javadoc规范"
category: language-guide
language: java
priority: high
tags: [Java, 编程规范, Google风格指南]
sections:
  - "源文件基础"
  - "源文件结构"
  - "格式化"
  - "命名约定"
  - "编程实践"
  - "Javadoc"
references:
  - "Google Java Style Guide官方文档"
---

# Google Java 风格指南

**参考**：[Google Java Style Guide](https://google.github.io/styleguide/javaguide.html)

## 源文件基础

- **文件名**：顶级类名 + `.java`（区分大小写）
- **编码**：UTF-8
- **空白字符**：仅 ASCII 空格 (0x20)，禁用 Tab 缩进
- **特殊字符**：优先使用 Unicode 字符而非转义序列

## 源文件结构

1. 许可证或版权信息
2. `package` 语句（不换行）
3. `import` 语句：
   - 禁用通配符导入
   - 静态导入块 → 非静态导入块
   - 组内 ASCII 排序，组间空行分隔
4. 单个顶级类声明

```java
/*
 * Copyright (C) 2024 Google, Inc.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 */

package com.google.example.style;

import static com.google.common.base.Preconditions.checkNotNull;

import java.util.ArrayList;
import java.util.List;

public class MyClass {
    // ...
}
```

## 3. 格式化

## 格式化

**大括号**：K&R 风格
- `{` 前不换行，后换行
- `}` 前换行，后换行（除非跟 `else` 或逗号）

**缩进**：2 个空格

**列宽**：100 字符

**换行**：
- 优先在运算符、方法名后、逗号处断开
- 续行缩进 +4 个空格

**空白**：
- 保留字后空格：`if (condition)`
- 运算符两侧空格：`a == b`
- 逗号、分号后空格

## 4. 命名约定

### 4.1 通用规则

标识符只使用 ASCII 字母和数字，在少数情况下使用下划线。有效的标识符名称匹配正则表达式 `\w+`。

### 4.2 包名

包名全部小写，单词之间直接连接，不使用下划线。

```
com.example.deepspace
```

### 4.3 类名

类名、接口名、枚举名、注解名都使用 **UpperCamelCase** (大驼峰命名法)。

```java
public class MyClass { ... }
public interface MyInterface { ... }
public enum MyEnum { ... }
```

### 4.4 方法名

方法名使用 **lowerCamelCase** (小驼峰命名法)。

```java
public void doSomething() { ... }
```

### 4.5 常量名

常量名使用 `CONSTANT_CASE`，所有字母大写，单词间用下划线分隔。常量是指使用 `static final` 修饰且其内容不可变的字段。

```java
public static final int NUMBER = 5;
```

### 4.6 非常量字段名

非常量字段名（静态或非静态）使用 **lowerCamelCase**。

```java
private String instanceVariable;
protected static String staticVariable;
```

### 4.7 参数名

参数名使用 **lowerCamelCase**。

```java
public void process(String userName) { ... }
```

### 4.8 局部变量名

局部变量名使用 **lowerCamelCase**。

## 5. 编程实践

### 5.1 `@Override`

只要一个方法是重写超类的方法，就**必须**使用 `@Override` 注解。

```java
@Override
public String toString() {
  return "My custom string";
}
```

### 5.2 捕获的异常

- **不要忽略异常**：捕获异常后不要完全不作处理。如果确实需要忽略，必须在注释中说明原因。
- **捕获具体的异常**：不要捕获通用的 `Exception` 或 `Throwable`，除非确实有必要。

### 5.3 静态成员

使用类名来引用静态成员，而不是通过具体的对象引用。

```java
// 正确
MyClass.staticMethod();

// 错误
MyClass instance = new MyClass();
instance.staticMethod(); // 不推荐
```

### 5.4 `final` 的使用

谨慎使用 `final` 修饰局部变量、参数和字段。虽然它有助于标识不变性，但过度使用会降低代码可读性。

## 6. Javadoc

### 6.1 通用格式

Javadoc 块的基本格式如下：

```java
/**
 * 多行 Javadoc 文本。
 * 每一行都以星号开头。
 */
public int method(String p1) { ... }
```

或者单行格式：

```java
/** 一个非常简短的 Javadoc。 */
```

### 6.2 摘要片段

每个 Javadoc 块都以一个简短的**摘要片段**开始。这个片段非常重要，它会出现在类或方法索引等特定上下文中。

### 6.3 使用场景

- **类/接口**: 至少要为每个 `public` 类/接口编写 Javadoc，以及大多数 `protected` 和 `package-private` 的类/接口。
- **方法/构造函数**: 至少要为每个 `public` 方法/构造函数编写 Javadoc，以及大多数 `protected` 和 `package-private` 的方法/构造函数。

```java
/**
 * 计算并返回两个整数的和。
 *
 * @param a 第一个加数
 * @param b 第二个加数
 * @return 两个参数的和
 */
public int add(int a, int b) {
  return a + b;
}
```
