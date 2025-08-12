# lazygophers/log 使用指南

`lazygophers/log` 是一个为追求极致简洁与扩展性而生的 Go 日志库。它提供了一套优雅、直观的 API，摒弃了繁杂的配置，让开发者能更专注于业务逻辑本身。

## 简介

通过实现 `io.Writer` 和 `Format` 接口，您可以随心所欲地定制日志的输出目标与展现形式，无论是写入文件、发送到远程服务，还是集成到您自己的监控系统，都游刃有余。

### 功能特性

- **多日志级别**: 支持 `Trace`, `Debug`, `Info`, `Warn`, `Error`, `Fatal`, `Panic`。
- **灵活输出目标**: 支持同时向一个或多个 `io.Writer` 输出日志。
- **自定义格式**: 通过实现 `Format` 接口，轻松定制 JSON、Logfmt 或任意文本格式。
- **调用栈追踪**: 精准定位日志来源（文件、行号、函数名）。
- **协程安全**: 所有方法均为协程安全，无需担心并发问题。
- **性能导向**: 清晰的性能优化路线图，致力于零内存分配。

## 安装

您可以使用 `go get` 命令来安装 `lazygophers/log`：

```shell
go get github.com/lazygophers/log
```

## 快速入门

以下是一个基础示例，展示了如何快速上手使用。

```go
package main

import "github.com/lazygophers/log"

func main() {
    // 库的默认日志级别为 Info
    log.Info("Application started")

    // 这条 Debug 级别的日志在默认配置下不会被输出
    log.Debug("This is a debug message")

    // 将日志级别设置为 Debug
    log.SetLevel(log.DebugLevel)
    log.Debug("Now, this debug message will be visible.")

    log.Warnf("User %s might not have permission", "Alice")
    log.Error("Failed to connect to the database")
}
```
