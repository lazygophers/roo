# MCP工具说明

> 配套的 MCP 模组

## 开发说明

- 日志请写入临时目录中 tempfile.gettempdir() + "/mcp/log/"
- 使用环境变量管理配置信息
- 尽可能的模块化、结构化

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

> 代码位于 `tools_file.py`

| 工具名称        | 功能描述    | 参数示例                                                          | 返回类型    |
|-------------|---------|---------------------------------------------------------------|---------|
| read_file   | 读取文件内容  | {"file_path": "/etc/hosts"}                                   | 文件字符串内容 |
| write_file  | 写入文件内容  | {"file_path": "/etc/hosts", "content": "127.0.0.1 localhost"} | 无       |
| delete_file | 删除文件    | {"file_path": "/etc/hosts"}                                   | 无       |
| mkdir       | 创建目录    | {"dir_path": "/tmp/test"}                                     | 无       |
| rmdir       | 删除目录    | {"dir_path": "/tmp/test"}                                     | 无       |
| chmod       | 修改文件权限  | {"file_path": "/etc/hosts", "mode": "777"}                    | 无       |
| chown       | 修改文件所有者 | {"file_path": "/etc/hosts", "owner": "root", "group": "root"} | 无       |
| chgrp       | 修改文件所属组 | {"file_path": "/etc/hosts", "group": "root"}                  | 无       |
| ln          | 创建符号链接  | {"src_path": "/etc/hosts", "dest_path": "/tmp/hosts"}         | 无       |
| mv          | 重命名文件   | {"src_path": "/etc/hosts", "dest_path": "/tmp/hosts"}         | 无       |
| cp          | 复制文件    | {"src_path": "/etc/hosts", "dest_path": "/tmp/hosts"}         | 无       |
| edit_file   | 编辑文件    | {"file_path": "/etc/hosts", "content": "127.0.0.1 localhost"} | 无       |