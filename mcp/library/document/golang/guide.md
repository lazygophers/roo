# Go编程规范

### 主要参考：

- [Uber编码规范](https://github.com/uber-go/guide/blob/master/style.md)
	- [Uber编码规范中文版](https://github.com/xxjwxc/uber_go_guide_cn)
- [Google编码规范](https://google.github.io/styleguide/go/index)

### 包引用问题

- 日志包，优先推荐 `github.com/lazygophers/log`
- 工具包，优先推荐 `github.com/lazygophers/utils`，其中
	- json 包： `github.com/lazygophers/utils/json`
	- string 扩展包： `github.com/lazygophers/utils/stringx`
	- time 扩展包： `github.com/lazygophers/utils/xtime`
	- bufio 扩展包： `github.com/lazygophers/utils/bufiox`
	- rand 扩展包： `github.com/lazygophers/utils/randx`
	- 类型扩展包： `github.com/lazygophers/utils/anyx`
	- 语法糖： `github.com/lazygophers/utils/candy`

## 代码风格

### 格式化要求

- 所有代码必须通过 `gofmt -s` 格式化
- 缩进使用Tab(四个空格)

### 命名约定

| 元素    | 命名规则           | 示例                |
|-------|----------------|-------------------|
| 包名    | 小写单单词          | `net`, `http`     |
| 导出类型  | 驼峰命名（首字母大写）    | `HTTPClient`      |
| 未导出类型 | 驼峰命名（首字母小写）    | `httpClient`      |
| 常量    | 全大写+下划线        | `MAX_CONNECTIONS` |
| 变量    | 短名（局部）/描述名（全局） | `i`, `maxRetries` |
| 接口    | 以`-er`结尾或单一动作  | `Reader`, `Close` |

### 注释规范

- 注释应包含功能说明、参数描述、返回值解释
- 推荐包含使用示例
- 使用自然流畅的中文技术文档风格

- 包注释：每个包应有简短说明

```go
// Package mypackage 实现 xxx 功能
package mypackage
```

- 函数注释：包含功能描述、参数说明和示例

```go
// MyFunction 执行核心业务逻辑
// 参数：
//   - i: 输入整数
// 返回：
//   - 转换后的字符串
// 示例：
//     result := MyFunction(42)
//     fmt.Println(result) // 输出 "42"
func MyFunction(i int) string {
    return strconv.Itoa(i)
}
```

- 所有公开API必须包含注释

```go
// Connect 建立到指定主机的网络连接
func Connect(host string) (*Connection, error) { ... }
```

- 类型注释应跟随字段

```go
// User 用户结构体
type User struct {
	// 用户名
	Name string
	// 密码
	Password string
	// 创建时间
	CreatedAt time.Time
}

```

#### 注释维护原则

- 每次代码修改时更新相关注释
- 使用中文注释中文项目
- 关键算法需添加注释水印

## 编码规范

### 减少嵌套

代码应通过尽可能先处理错误情况/特殊情况并尽早返回或继续循环来减少嵌套。减少嵌套多个级别的代码的代码量。

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

### 减少不必要的 else

如果在 if 的两个分支中都设置了变量，则可以将其替换为单个 if。

```go
a := 10
if b {
  a = 100
}
```

#### 变量初始化

##### 对零值结构使用 var

如果在声明中省略了结构的所有字段，请使用 var 声明结构。

```go
var user User
```

##### 初始化 Struct 引用

在初始化结构引用时，请使用&T{}代替new(T)，以使其与结构体初始化一致。

```go
sval := T{Name: "foo"}

sptr := &T{Name: "bar"}
```

##### 初始化 Map

对于空 map 请使用 make(..) 初始化，并且 map 是通过编程方式填充的。 这使得 map 初始化在表现上不同于声明，并且它还可以方便地在 make 后添加大小提示。

```go
var (
  // m1 读写安全;
  // m2 在写入时会 panic
  m1 = make(map[T1]T2)
  m2 map[T1]T2
)
```

##### 初始化 Slice

对于空的 slice，请使用 var 创建。

```go
var s1 []T
```

## 错误处理

- 禁止在业务逻辑中使用 `panic`

- 优先使用 `errors.New` 或 `fmt.Errorf` 创建错误

```go
var ErrNotFound = errors.New("资源未找到")

func ReadFile(path string) ([]byte, error) {
    _, err := os.Stat(path)
    if err != nil {
        if os.IsNotExist(err) {
            return nil, ErrNotFound
        }
        log.Errorf("err:%s", err)
        return nil, err
    }
    // ...
}
```

- 采用尽早返回模式减少嵌套

```go
func Process(data []byte) error {
    if len(data) == 0 {
        return errors.New("数据不能为空")
    }
    // 处理逻辑
    return nil
}
```

```go
// 推荐：尽早返回，减少嵌套
func ReadFile(path string) ([]byte, error) {
    f, err := os.Open(path)
    if err != nil {
		log.Errorf("err:%s", err)
		return nil, err
    }
    defer f.Close()

    data, err := io.ReadAll(f)
    if err != nil {
		log.Errorf("err:%s", err)
		return nil, err
    }
    return data, nil
}
```

### 错误设计

```go
// 静态错误
var ErrNotFound = errors.New("resource not found")

// 动态错误（使用%w保留原始错误）
return fmt.Errorf("parse config: %w", err)

// 结构化错误
type HTTPError struct {
    Code int
    Msg  string
}

func (e *HTTPError) Error() string {
    return fmt.Sprintf("HTTP %d: %s", e.Code, e.Msg)
}
```

## 并发编程

### goroutine管理

```go
// 使用channel控制goroutine退出
func worker(jobs <-chan Job, stop <-chan struct{}) {
    for {
        select {
        case job, ok := <-jobs:
            if !ok {\n            return\n        }\n        process(job)
            process(job)
        case <-stop:
            return
        }
    }
}

// 启动和停止示例
stopCh := make(chan struct{})
jobsCh := make(chan Job)

go worker(jobsCh, stopCh)

// 停止工作
close(stopCh)
```

### 并发原语

| 场景 | 推荐原语 | 示例代码 | 说明 |
|---------|-----------|----------------------------------------------|
| 协程间通信 | Channel | `jobs := make(chan Job, 10)`                 |
| 共享资源保护 | Mutex | `var mu sync.Mutex`                          |
| 等待多协程完成 | WaitGroup | `wg.Add(2); go func() { defer wg.Done() }()` |
| 单次初始化 | Once | `var once sync.Once; once.Do(init)`          |

## 性能优化

### 内存分配

```go
// 预分配切片容量
data := make([]int, 0, 100)

// 对象复用（sync.Pool）
var bufPool = sync.Pool{
    New: func() interface{} {
        return make([]byte, 1024)
    },
}

func process() {
    buf := bufPool.Get().([]byte)
    defer bufPool.Put(buf)
    // 使用buf
}
```

### 字符串操作

```go
// 推荐：使用bytes.Buffer替代+
var b bytes.Buffer
for i := 0; i < 1000; i++ {
    b.WriteString("part")
}
result := b.String()

// 数值转字符串：使用strconv而非fmt
s := strconv.Itoa(123) // 比fmt.Sprintf快3-4倍
```

## 测试规范

### 单元测试

```go
func TestAdd(t *testing.T) {
    tests := []struct {
        a, b int
        want int
    }{
        {1, 2, 3},
        {0, 0, 0},
        {-1, 1, 0},
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

### 基准测试

```go
func BenchmarkAdd(b *testing.B) {
    for i := 0; i < b.N; i++ {
        Add(1, 2)
    }
}
### 注释规范增强
#### 代码注释标准
```go
// 包注释应描述包的用途
package main

// 函数注释应遵循Google风格
func calculateTotal(items []int) int {
    // 函数体
}
```