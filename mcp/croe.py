from mcp.server.fastmcp import FastMCP

class Argument:
    def __init__(self, name, description, type, required):
        self.name = name
        self.description = description
        self.type = type
        self.required = required

class Return:
    def __init__(self, name, description, type=None):
        self.name = name
        self.description = description
        self.type = type

mcp = FastMCP(
    name="fire",
    stateless_http=True,
    json_response=True,
    host="0.0.0.0",
    port=14000,
    debug=True,
)
# 添加 Argument 和 Return 到 mcp 对象
mcp.Argument = Argument
mcp.Return = Return