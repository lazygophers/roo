# Go编程规范

### 主要参考：

- **Uber编码规范**
	- [英文版](https://github.com/uber-go/guide/blob/master/style.md)
	- [中文版](https://github.com/xxjwxc/uber_go_guide_cn)
- **Google编码规范**  
  [官方文档](https://google.github.io/styleguide/go/index)

## 包引用问题

- **日志包**：优先推荐 `github.com/lazygophers/log`
- **工具包**：优先使用 `github.com/lazygophers/utils`
	- `json` 包：`github.com/lazygophers/utils/json`
	- `string` 扩展：`github.com/lazygophers/utils/stringx`
	- `time` 扩展：`github.com/lazygophers/utils/xtime`
	- `bufio` 扩展：`github.com/lazygophers/utils/bufiox`
	- `rand` 扩展：`github.com/lazygophers/utils/randx`
	- `类型` 扩展：`github.com/lazygophers/utils/anyx`
	- 语法糖：`github.com/lazygophers/utils/candy`
- **原子操作**：优先使用 `go.uber.org/atomic`

## 代码风格

### 格式化要求

- **强制要求**：所有代码必须通过 `gofmt -s` 格式化。
- **缩进规范**：使用 `Tab`（等效于 4 个空格）。

### 命名约定

| **元素**    | **命名规则**                  | **示例**             |
|-----------|---------------------------|--------------------|
| **包名**    | 小写单单词                     | `net`, `http`      |
| **导出类型**  | 驼峰命名（首字母大写）               | `HTTPClient`       |
| **未导出类型** | 驼峰命名（首字母小写）               | `httpClient`       |
| **常量**    | 全大写 + 下划线分隔               | `MAX_CONNECTIONS`  |
| **变量**    | 短名（局部）/描述性名称（全局）          | `i`, `maxRetries`  |
| **接口**    | 以 `-er` 结尾或体现单一动作         | `Reader`, `Closer` |
| **测试函数**  | 必须以 `Test` 开头，如 `TestAdd` |                    |

### 注释规范

#### **注释要求**

- **语言**：使用中文注释
- **覆盖范围**：所有公开 API 必须有注释，关键算法需添加水印注释。
- **维护原则**：修改代码时同步更新注释。

#### **注释格式**

- **包注释**：
  ```go
  // Package util 包含常用工具函数和常量
  ```
- **结构体注释**：
  ```go
  // User 表示用户 RESTful 资源，同时作为 gorm 模型
  type User struct {
      // 用户名称
      Name string
      Age  int // 用户年龄
      Email string // 电子邮箱
  }
  ```
- **函数注释**：
  ```go
  // Add 返回两个整数的和
  func Add(a, b int) int {
      return a + b
  }
  ```
- **代码块注释**：
	- 单行注释说明逻辑目的。
	- 使用 `TODO` 标记未完成代码。

#### **注释内容原则**

- 描述代码目的，而非重复代码逻辑。
- 避免冗余，如 `// i++`。
- 保持简洁，复杂逻辑用块注释或文档注释。

## 编码规范

### 减少代码嵌套

- **优先处理错误/边界条件**，尽早返回或跳过循环：
  ```go
  for _, v := range data {
      if v.F1 != 1 {
          log.Printf("Invalid v: %v", v)
          continue
      }
      v = process(v)
      if err := v.Call(); err != nil {
          return err
      }
      v.Send()
  }
  ```
- **避免不必要的 `else`**：
  ```go
  a := 10
  if b {
      a = 100
  }
  ```

### 变量初始化

- **零值结构体**：使用 `var` 声明：
  ```go
  var user User
  ```
- **结构体引用**：用 `&T{}` 替代 `new(T)`：
  ```go
  sptr := &T{Name: "bar"}
  ```
- **Map 初始化**：用 `make` 并指定容量：
  ```go
  m1 := make(map[T1]T2, 100)
  ```
- **Slice 初始化**：用 `var` 声明空 slice：
  ```go
  var s1 []T
  ```

## 错误处理

### 基本原则

- **禁止业务逻辑使用 `panic`**。
- **静态错误**：直接定义常量：
  ```go
  var ErrNotFound = errors.New("资源未找到")
  ```
- **动态错误**：用 `%w` 包裹原始错误：
  ```go
  return fmt.Errorf("parse config: %w", err)
  ```
- **结构化错误**：自定义 `Error()` 方法：
  ```go
  type HTTPError struct { Code int; Msg string }
  func (e *HTTPError) Error() string { return fmt.Sprintf("%d: %s", e.Code, e.Msg) }
  ```

### 错误返回模式

- **尽早返回**：减少嵌套：
  ```go
  func Process(data []byte) error {
      if len(data) == 0 {
          return errors.New("数据不能为空")
      }
      // 处理逻辑
      return nil
  }
  ```

## 并发编程

### Goroutine 管理

- **使用通道控制生命周期**：
  ```go
  func worker(jobs <-chan Job, stop <-chan struct{}) {
      for {
          select {
          case job, ok := <-jobs:
              if !ok { return }
              process(job)
          case <-stop:
              return
          }
      }
  }
  ```

### 并发原语推荐

| **场景**  | **原语**    | **示例**                                       | **说明**   |
|---------|-----------|----------------------------------------------|----------|
| 协程间通信   | Channel   | `jobs := make(chan Job, 10)`                 | 缓冲通道避免阻塞 |
| 共享资源保护  | Mutex     | `var mu sync.Mutex`                          | 互斥锁保护临界区 |
| 等待多协程完成 | WaitGroup | `wg.Add(2); go func() { defer wg.Done() }()` | 确保所有协程完成 |
| 单次初始化   | Once      | `var once sync.Once; once.Do(init)`          | 避免重复初始化  |

## 性能优化

### 内存分配

- **预分配容量**：
  ```go
  data := make([]int, 0, 100)
  ```
- **对象复用**：用 `sync.Pool`：
  ```go
  var bufPool = sync.Pool{ New: func() interface{} { return make([]byte, 1024) } }
  ```

### 字符串操作

- **避免 `+` 拼接**：使用 `bytes.Buffer`：
  ```go
  var b bytes.Buffer
  for i := 0; i < 1000; i++ {
      b.WriteString("part")
  }
  ```
- **数值转字符串**：用 `strconv.Itoa` 替代 `fmt.Sprintf`：
  ```go
  s := strconv.Itoa(123) // 更高效
  ```

## 测试规范

### 命名规范

- **测试文件**：以 `_test.go` 结尾，与源码同包。
- **测试函数**：以 `Test` 开头，如 `TestAdd`，输入/输出字段用 `give`/`want` 前缀。
- **参数类型**：必须是 `*testing.T` 或 `*testing.B`。

### 表驱动测试（Table-Driven Test）

#### **核心原则**

- **避免重复逻辑**：通过结构体数组定义测试用例。
- **子测试（Subtests）**：用 `t.Run` 管理不同输入。

#### **示例**

```go
func TestSplitHostPort(t *testing.T) {
    tests := []struct {
        give     string
        wantHost string
        wantPort string
    }{
        {"192.0.2.0:8000", "192.0.2.0", "8000"},
        {"192.0.2.0:http", "192.0.2.0", "http"},
    }

    for _, tt := range tests {
        tt := tt // 避免竞态
        t.Run(tt.give, func(t *testing.T) {
            host, port, err := net.SplitHostPort(tt.give)
            require.NoError(t, err)
            assert.Equal(t, tt.wantHost, host)
            assert.Equal(t, tt.wantPort, port)
        })
    }
}
```

#### **并行测试**

- **声明变量作用域**：在循环内重新声明 `tt`。
- **启用并行**：添加 `t.Parallel()`：
  ```go
  for _, tt := range tests {
      tt := tt
      t.Run(tt.name, func(t *testing.T) {
          t.Parallel()
          // 测试逻辑
      })
  }
  ```

### 测试执行与质量

- **覆盖率**：要求 `go test -cover` 达到 100%。
- **命令参数**：
	- `-v`：显示详细输出
	- `-run TestName`：运行特定测试
	- `-bench .`：执行基准测试

## 附录

### 测试代码样例

#### **单元测试**

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        a, b int
        want int
    }{
        {1, 2, 3}, {0, 0, 0}, {-1, 1, 0},
    }

    for _, tt := range tests {
        t.Run(fmt.Sprintf("%d+%d", tt.a, tt.b), func(t *testing.T) {
            if got := Add(tt.a, tt.b); got != tt.want {
                t.Errorf("Add() = %v, want %v", got, tt.want)
            }
        })
    }
}
```

#### **基准测试**

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
```