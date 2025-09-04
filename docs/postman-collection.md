# Postman Collection 文档

## 概述

本文档提供了基于 FastAPI 路由文件的 Postman Collection 格式说明。由于文档工程师模式的限制，无法直接生成 `.json` 文件，因此以 Markdown 格式展示完整的 Postman Collection 结构。

## Postman Collection 结构

```json
{
  "info": {
    "name": "FastAPI Routes Collection",
    "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json"
  },
  "item": [
    {
      "name": "Hello Endpoint",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"User\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/hello",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "hello"
          ]
        }
      }
    },
    {
      "name": "Get All Models",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/models",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "models"
          ]
        }
      }
    },
    {
      "name": "Get Model by Slug",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"slug\": \"doc-writer\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/models/get",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "models",
            "get"
          ]
        }
      }
    },
    {
      "name": "Get Before Hook",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/hooks/before",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "hooks",
            "before"
          ]
        }
      }
    },
    {
      "name": "Get After Hook",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/hooks/after",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "hooks",
            "after"
          ]
        }
      }
    },
    {
      "name": "Get Rule by Slug",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"slug\": \"base\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/rules/get",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "rules",
            "get"
          ]
        }
      }
    },
    {
      "name": "Get Commands",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/commands",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "commands"
          ]
        }
      }
    },
    {
      "name": "Get Roles",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/roles",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "roles"
          ]
        }
      }
    },
    {
      "name": "Save Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"test-config\",\n  \"content\": \"configuration content\",\n  \"description\": \"Test configuration\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/save",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "save"
          ]
        }
      }
    },
    {
      "name": "Get Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"test-config\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/get",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "get"
          ]
        }
      }
    },
    {
      "name": "Update Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"test-config\",\n  \"content\": \"updated content\",\n  \"description\": \"Updated test configuration\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/update",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "update"
          ]
        }
      }
    },
    {
      "name": "Delete Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"name\": \"test-config\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/delete",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "delete"
          ]
        }
      }
    },
    {
      "name": "Export YAML Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/export/yaml",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "export",
            "yaml"
          ]
        }
      }
    },
    {
      "name": "Export JSON Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/export/json",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "export",
            "json"
          ]
        }
      }
    },
    {
      "name": "Import YAML Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"yaml_content\": \"name: test\\ndescription: Test configuration\\n\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/import/yaml",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "import",
            "yaml"
          ]
        }
      }
    },
    {
      "name": "Import JSON Configuration",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"json_content\": \"{\\\"name\\\": \\\"test\\\", \\\"description\\\": \\\"Test configuration\\\"}\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/configurations/import/json",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "configurations",
            "import",
            "json"
          ]
        }
      }
    },
    {
      "name": "Execute Command",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"command\": \"ls -la\",\n  \"timeout\": 10\n}"
        },
        "url": {
          "raw": "http://localhost:8000/commands/execute",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "commands",
            "execute"
          ]
        }
      }
    },
    {
      "name": "Get Role by Slug",
      "request": {
        "method": "POST",
        "header": [
          {
            "key": "Content-Type",
            "value": "application/json"
          }
        ],
        "body": {
          "mode": "raw",
          "raw": "{\n  \"slug\": \"doc-writer\"\n}"
        },
        "url": {
          "raw": "http://localhost:8000/roles/get",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "roles",
            "get"
          ]
        }
      }
    },
    {
      "name": "List All Roles (GET)",
      "request": {
        "method": "GET",
        "header": [],
        "url": {
          "raw": "http://localhost:8000/roles",
          "protocol": "http",
          "host": [
            "localhost"
          ],
          "port": "8000",
          "path": [
            "roles"
          ]
        }
      }
    }
  ]
}
```

## 使用说明

### 导入 Postman

1. 将上述 JSON 内容保存为 `fastapi-routes-collection.json`
2. 打开 Postman
3. 点击 `Import` 按钮
4. 选择文件导入或粘贴原始 JSON
5. 导入后即可使用所有预定义的 API 请求

### 环境变量设置

建议在 Postman 中设置环境变量：

```json
{
  "name": "FastAPI Environment",
  "values": [
    {
      "key": "base_url",
      "value": "http://localhost:8000",
      "enabled": true
    }
  ]
}
```

### 请求说明

所有请求都需要设置 `Content-Type: application/json` 头部。

### 测试脚本示例

可以在 Postman 的 Tests 标签页中添加测试脚本：

```javascript
// 测试响应状态码
pm.test("Status code is 200", function () {
    pm.response.to.have.status(200);
});

// 测试响应时间
pm.test("Response time is less than 1000ms", function () {
    pm.expect(pm.response.responseTime).to.be.below(1000);
});

// 测试响应体结构
pm.test("Response has required fields", function () {
    const responseJson = pm.response.json();
    pm.expect(responseJson).to.have.property('success');
    pm.expect(responseJson).to.have.property('data');
});
```

## 注意事项

1. 所有端点都是 POST 方法（除了一个 GET 端点）
2. 请求体需要是 JSON 格式
3. 根据实际部署情况修改 `base_url`
4. 某些端点可能需要认证信息
5. 文件上传端点需要使用 form-data 格式