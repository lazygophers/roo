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

## 🔧 技术栈
- Java 8+, Spring Boot, JUnit, Maven/Gradle
- IDE: IntelliJ IDEA, Eclipse
- 工具: Checkstyle, SpotBugs

## 📝 命名规范

| 元素 | 命名法 | 示例 |
|------|--------|------|
| 包名 | `lowercase` | `com.example.util` |
| 类名 | `UpperCamelCase` | `UserService`, `HttpClient` |
| 方法/变量 | `lowerCamelCase` | `getUserName()`, `maxSize` |
| 常量 | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 接口 | `-er`结尾或动作 | `Serializable`, `Runnable` |

## 🏷️ 类型/接口定义

```java
// 类定义
public class UserService {
    private static final int MAX_USERS = 1000;
    
    @Override
    public String toString() {
        return "UserService";
    }
}

// 接口定义
public interface DataProcessor<T> {
    void process(T data);
}

// 枚举定义
public enum Status {
    ACTIVE, INACTIVE, PENDING
}
```

## 🧪 测试规范

```java
@Test
public void testUserCreation() {
    // Given
    String username = "john";
    
    // When
    User user = userService.createUser(username);
    
    // Then
    assertThat(user.getName()).isEqualTo(username);
    assertThat(user.getId()).isNotNull();
}
```

## ✅ 核心要求
- UTF-8编码，2空格缩进，100字符行宽
- K&R大括号风格：`{`不换行，`}`前换行
- 禁用通配符导入，按组排序import
- 必须使用`@Override`注解
- 不忽略异常，捕获具体异常类型
- 谨慎使用`final`修饰符
- 公共API必须有Javadoc注释
