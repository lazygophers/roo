---
name: java-guide
title: Google Java风格指南
description: "Google Java Style Guide核心规则总结，涵盖源文件基础、格式化、命名约定、编程实践和Javadoc规范"
category: language-guide
language: java
priority: high
tags: [Java, 编程规范, Google风格指南]
sections:
  - "源文件基础：文件名、编码、特殊字符"
  - "源文件结构：许可证、package语句、import语句、类声明"
  - "格式化：大括号、缩进、列宽、换行、空白"
  - "命名约定：通用规则、包名、类名、方法名等"
  - "编程实践：@Override、异常处理、静态成员、final使用"
  - "Javadoc：基本格式、摘要片段、使用场景"
references:
  - "Google Java Style Guide官方文档"
---

# Google Java 风格指南核心规则总结

本指南是对 [Google Java Style Guide](https://google.github.io/styleguide/javaguide.html) 的核心内容进行总结，旨在提供一个快速参考，帮助开发者理解和应用 Google 的 Java 编程规范。

## 1. 源文件基础

### 1.1 文件名

源文件名由其包含的顶级类的名称（区分大小写）加上 `.java` 扩展名组成。

### 1.2 文件编码

源文件编码格式为 **UTF-8**。

### 1.3 特殊字符

- **空白字符**: 除了行终止符序列，ASCII 水平空格字符 (0x20) 是源文件中唯一出现的空白字符。这意味着：
  1.  字符串和字符字面量中的所有其他空白字符都需要转义。
  2.  **不使用制表符（Tab）进行缩进**。
- **特殊转义序列**: 对于有特殊转义序列的字符（`\b`, `\t`, `\n`, `\f`, `\r`, `\"`, `\'`, `\\`），应使用这些序列而不是对应的八进制或 Unicode 转义。
- **非 ASCII 字符**: 对于非 ASCII 字符，建议使用实际的 Unicode 字符（如 `∞`），而不是其等效的 Unicode 转义（如 `\u221e`），这样更易于阅读和理解。

## 2. 源文件结构

一个源文件按顺序包含以下部分：

1.  **许可证或版权信息** (如果存在)
2.  **`package` 语句**: 不换行，且不受列宽限制。
3.  **`import` 语句**:
    - **不使用通配符导入** (无论是静态导入还是普通导入)。
    - `import` 语句不换行，不受列宽限制。
    - 导入顺序：
      1.  所有静态导入，单个块。
      2.  所有非静态导入，单个块。
    - 组内按 ASCII 码排序，组间用一个空行分隔。
4.  **一个顶级类声明**：每个源文件只有一个顶级类或接口。

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

### 3.1 大括号

大括号遵循 K&R 风格 ("Egyptian brackets"):

- 左大括号 (`{`) 前不换行。
- 左大括号 (`{`) 后换行。
- 右大括号 (`}`) 前换行。
- 右大括号 (`}`) 后换行，仅当它结束一个语句或方法、构造函数、类的代码体时。例如，如果 `}` 后面跟着 `else` 或逗号，则其后不换行。

```java
// 正确示例
return new MyClass() {
  @Override public void method() {
    if (condition()) {
      try {
        something();
      } catch (ProblemException e) {
        recover();
      }
    } else if (otherCondition()) {
      somethingElse();
    } else {
      lastThing();
    }
  }
};
```

### 3.2 块缩进

每当打开一个新的块或块状结构时，缩进增加 **2 个空格**。当块结束时，缩进回到之前的级别。

```java
public void myMethod() {
  if (isTrue) {
    // 缩进 +2 个空格
    System.out.println("Hello, World!");
  }
}
```

### 3.3 每行一个语句

每个语句后都跟一个换行符。

### 3.4 列宽限制

Java 代码的列宽限制为 **100 个字符**。

### 3.5 换行

当一行代码超过列宽限制时，将其拆分为多行。

- **换行点**: 通常在更高语法级别处断开。优先选择：
  1.  在非赋值运算符处断开。
  2.  在赋值运算符处断开。
  3.  在方法或构造函数名后的左括号 `(` 处断开。
  4.  在逗号 `,` 处断开。
  5.  在 Lambda 箭头的 `->` 处断开。
- **续行缩进**: **+4 个空格**。

```java
// 续行缩进 +4
someMethod(
    "longArgument1",
    "longArgument2",
    "longArgument3");
```

### 3.6 空白

- **垂直空白**:
  - 在类的连续成员（字段、构造函数、方法、内部类）之间使用一个空行。
  - 方法体内，根据需要使用空行来创建逻辑分组。
- **水平空白**:
  - 在任何保留字（如 `if`, `for`, `catch`）和其后的括号之间加一个空格。
  - 在任何二元或三元运算符的两侧加一个空格。
  - 在逗号 `,`、分号 `;`、类型转换的右括号 `)` 之后加一个空格。

```java
// 正确
if (a == b) { // if 后、== 两侧有空格
  // ...
}
```

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
