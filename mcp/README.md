# MCP工具说明

> 配套的 MCP 模组

## 开发说明

- 不输出日志
- 使用环境变量管理配置信息
- 尽可能的模块化、结构化
- 使用 https://github.com/modelcontextprotocol/python-sdk 作为 SDK

## 配置说明

```json
{
  "mcpServers": {
	"mcp": {
	  "command": ""
	}
  }
}
```

## 工具列表

### 文件操作

| 工具名称         | 功能描述    | 参数示例                                                          | 返回类型 |
|--------------|---------|---------------------------------------------------------------|------|
| read_file    | 读取文件内容  | {"file_path": "/etc/hosts"}                                   | str  |
| write_file   | 写入文件内容  | {"file_path": "/etc/hosts", "content": "127.0.0.1 localhost"} | bool |
| delete_file  | 删除文件    | {"file_path": "/etc/hosts"}                                   | bool |
| mkdir        | 创建目录    | {"dir_path": "/tmp/test"}                                     | bool |
| rmdir        | 删除目录    | {"dir_path": "/tmp/test"}                                     | bool |
| file_exists  | 检查文件存在  | {"path": "/etc/hosts"}                                        | bool |
| file_is_dir  | 检查是否目录  | {"path": "/etc"}                                              | bool |
| file_is_file | 检查是否文件  | {"path": "/etc/hosts"}                                        | bool |
| ln           | 创建符号链接  | {"src": "/etc/hosts", "dest": "/tmp/hosts"}                   | bool |
| mv           | 重命名文件   | {"src": "/etc/hosts", "dest": "/tmp/hosts"}                   | bool |
| edit_file    | 编辑文件内容  | {"file_path":"/etc/hosts", "line_range":"1-10"}               | bool |
| append_file  | 追加内容到文件 | {"file_path":"/etc/hosts", "content":"127.0.0.1 localhost"}   | bool |