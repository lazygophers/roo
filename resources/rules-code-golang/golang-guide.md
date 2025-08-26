# Go 编程规范

### 主要参考：

- **Uber 编码规范**
  - [英文版](https://github.com/uber-go/guide/blob/master/style.md)
  - [中文版](https://github.com/xxjwxc/uber_go_guide_cn)
- **Google 编码规范**
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

| **元素**       | **命名规则**                     | **示例**           |
| -------------- | -------------------------------- | ------------------ |
| **包名**       | 小写单单词                       | `net`, `http`      |
| **导出类型**   | 驼峰命名（首字母大写）           | `HTTPClient`       |
| **未导出类型** | 驼峰命名（首字母小写）           | `httpClient`       |
| **常量**       | 全大写 + 下划线分隔              | `MAX_CONNECTIONS`  |
| **变量**       | 短名（局部）/描述性名称（全局）  | `i`, `maxRetries`  |
| **接口**       | 以 `-er` 结尾或体现单一动作      | `Reader`, `Closer` |
| **测试函数**   | 必须以 `Test` 开头，如 `TestAdd` |                    |

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
  // User 表示我 RESTful 资源，同时作为 gorm 模型
  type User struct {
      // 我名称
      Name string
      Age  int // 我年龄
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

### 错误判断与提取

- **判断特定错误**: 使用 `errors.Is` 来检查错误链中是否包含特定的哨兵错误（sentinel error）。这比直接使用 `==` 更健壮，因为它可以处理被包装过的错误。

  ```go
  var ErrFoo = errors.New("foo error")

  func Check() error {
      return fmt.Errorf("wrapped: %w", ErrFoo)
  }

  // ...
  err := Check()
  if errors.Is(err, ErrFoo) {
      // err 包含 ErrFoo
  }
  ```

- **提取特定类型错误**: 使用 `errors.As` 来检查错误链中是否存在特定类型的错误，并将其提取出来以便访问其字段。

  ```go
  type MyError struct {
      Code int
  }
  func (e *MyError) Error() string { return "my error" }

  func Check() error {
      return &MyError{Code: 42}
  }

  // ...
  err := Check()
  var myErr *MyError
  if errors.As(err, &myErr) {
      fmt.Println(myErr.Code) // 输出: 42
  }
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

| **场景**       | **原语**  | **示例**                                     | **说明**         |
| -------------- | --------- | -------------------------------------------- | ---------------- |
| 协程间通信     | Channel   | `jobs := make(chan Job, 10)`                 | 缓冲通道避免阻塞 |
| 共享资源保护   | Mutex     | `var mu sync.Mutex`                          | 互斥锁保护临界区 |
| 等待多协程完成 | WaitGroup | `wg.Add(2); go func() { defer wg.Done() }()` | 确保所有协程完成 |
| 单次初始化     | Once      | `var once sync.Once; once.Do(init)`          | 避免重复初始化   |

## Context 使用规范

`context.Context` 是现代 Go 并发编程和 API 设计中不可或缺的一部分，用于处理超时、取消信号以及在 API 调用链中传递请求范围的数据。

### 核心原则

- **作为第一个参数**: `Context` 应始终作为函数的第一个参数，且通常命名为 `ctx`。

  ```go
  func DoSomething(ctx context.Context, arg1, arg2 string) error {
      // ...
  }
  ```

- **禁止存储在结构体中**: 不应将 `Context` 作为结构体字段。它应该在函数调用链中显式传递，以保持其请求范围的生命周期。

- **不要传递 `nil` Context**: 如果不确定使用哪个 `Context`，应使用 `context.Background()` 或 `context.TODO()`。

  - `context.Background()`: 通常用于主函数、初始化和测试中，是所有 `Context` 的根。
  - `context.TODO()`: 当不确定使用哪个 `Context`，或函数未来计划支持 `Context` 但目前尚未实现时使用。

- **小心使用 `WithValue`**:

  - `WithValue` 不应用于传递可选参数，这会降低代码的可读性和健-壮性。
  - 它主要用于在进程和 API 边界传递请求范围的元数据，如追踪 ID、我身份信息等。

- **及时取消**: `Context` 的 `cancel` 函数被调用后，应尽快让使用该 `Context` 的 Goroutine 停止工作并返回。
  ```go
  ctx, cancel := context.WithTimeout(context.Background(), 50*time.Millisecond)
  defer cancel() // 确保 cancel 函数总是被调用
  ```

## 泛型使用规范

Go 1.18 引入了泛型，为处理通用数据结构和函数提供了强大的类型安全工具。

### 使用原则

- **适用场景**: 优先将泛型用于操作通用数据结构（如切片、map、channel）的函数，例如 `Filter`、`Map`、`Reduce` 等。
- **避免滥用**: 如果接口可以清晰地解决问题，则不必强制使用泛型。泛型并非旨在取代接口。

- **类型参数命名**:
  - 类型参数建议使用单个大写字母，如 `T`。
  - 如果函数有多个类型参数，应选择有意义的名称，如 `K` (Key), `V` (Value)。

### 示例

```go
// MapKeys 返回一个 map 的所有键的切片。
func MapKeys[K comparable, V any](m map[K]V) []K {
    r := make([]K, 0, len(m))
    for k := range m {
        r = append(r, k)
    }
    return r
}
```

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

### 断言库推荐

- **推荐库**: `github.com/stretchr/testify`
- **说明**: `testify` 提供了一套丰富的断言工具（`assert` 和 `require`），可以显著简化测试代码，使其更具可读性。`require` 在断言失败时会立即终止测试，而 `assert` 则会记录失败并继续执行。
- **参考**:
  - [GitHub 仓库](https://github.com/stretchr/testify)

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
            // 使用 require 包确保前置条件满足
            require.NoError(t, err, "解析地址不应出错")

            // 使用 assert 包进行结果断言
            assert.Equal(t, tt.wantHost, host, "主机名应匹配")
            assert.Equal(t, tt.wantPort, port, "端口号应匹配")
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

- **覆盖率**: `go test -cover` 的结果应至少保证 **90%** 以上。对于核心业务逻辑，应追求更高的覆盖率。
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
            got := Add(tt.a, tt.b)
            assert.Equal(t, tt.want, got, "Add() 的结果应与期望值相等")
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
