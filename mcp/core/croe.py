from mcp.server.fastmcp import FastMCP
from core.config import http_port

mcp = FastMCP(
    name="fire",
    stateless_http=True,
    sse_http=True,
    json_response=True,
    host="0.0.0.0",
    port=http_port,
    log_level="DEBUG",
)