---
name: golang-guide
title: Go编程规范指南
description: "Go语言编程规范和最佳实践，涵盖代码风格、命名约定、错误处理、并发编程和测试规范"
category: language-guide
language: go
priority: high
tags: [Go, 编程规范, 最佳实践, 并发编程]
sections:
  - "代码风格"
  - "编码规范"
  - "错误处理"
  - "并发编程"
  - "Context使用"
  - "泛型使用"
  - "性能优化"
  - "测试规范"
references:
  - "Uber Go 编程规范"
  - "Google Go 编程规范"
---

# Go 编程规范指南

## 🔧 技术栈
- Go 1.21+, Gin, GORM, Redis
- 工具: gofmt, golint, go vet
- 推荐包: testify, zap, viper

## 📝 命名规范

| 元素 | 命名法 | 示例 |
|------|--------|------|
| 包名 | `lowercase` | `http`, `json` |
| 导出类型 | `UpperCamelCase` | `HTTPClient`, `User` |
| 未导出类型 | `lowerCamelCase` | `httpClient`, `userRepo` |
| 常量 | `SCREAMING_SNAKE_CASE` | `MAX_RETRY_COUNT` |
| 变量 | 简短/描述性 | `i`, `maxRetries`, `userID` |
| 接口 | `-er`后缀 | `Reader`, `Writer`, `Handler` |
| 函数/方法 | `UpperCamelCase/lowerCamelCase` | `GetUser()`, `processData()` |

## 🏷️ 类型/接口定义

```go
// 结构体定义
type User struct {
    ID    int64  `json:"id" db:"id"`
    Name  string `json:"name" db:"name"`
    Email string `json:"email" db:"email"`
}

// 接口定义
type UserRepository interface {
    GetByID(ctx context.Context, id int64) (*User, error)
    Create(ctx context.Context, user *User) error
}

// 错误定义
var (
    ErrUserNotFound = errors.New("user not found")
    ErrInvalidInput = errors.New("invalid input")
)

// 方法定义
func (u *User) IsValid() bool {
    return u.Name != "" && u.Email != ""
}
```

## 🧪 测试规范

```go
func TestUserRepository_GetByID(t *testing.T) {
    tests := []struct {
        name    string
        userID  int64
        want    *User
        wantErr bool
    }{
        {"valid user", 1, &User{ID: 1, Name: "John"}, false},
        {"user not found", 999, nil, true},
    }
    
    for _, tt := range tests {
        tt := tt
        t.Run(tt.name, func(t *testing.T) {
            t.Parallel()
            got, err := repo.GetByID(context.Background(), tt.userID)
            
            if tt.wantErr {
                assert.Error(t, err)
                return
            }
            
            require.NoError(t, err)
            assert.Equal(t, tt.want, got)
        })
    }
}
```

## ✅ 核心要求
- 必须使用`gofmt -s`格式化，Tab缩进
- Context作为函数第一参数，命名为`ctx`
- 错误处理：使用`errors.Is/As`，不忽略错误
- 并发：优先使用Channel，谨慎使用Mutex
- 尽早返回，减少嵌套深度
- 使用`var`声明零值，`&T{}`创建指针
- 测试覆盖率≥90%，使用表驱动测试
- 公开API必须有注释，使用中文
