import shutup

shutup.please()

from core.config import http_port
import anyio
from core.croe import mcp
from tools import *


if __name__ == "__main__":
    log.info("正在启动服务.....")
    log.info("http_streamable: http://127.0.0.1:{}/mcp".format(http_port))

    """Run the server using StreamableHTTP transport."""
    import uvicorn

    starlette_app = mcp.streamable_http_app()

    config = uvicorn.Config(
        starlette_app,
        host=mcp.settings.host,
        port=mcp.settings.port,
        log_level="critical",
    )
    server = uvicorn.Server(config)
    anyio.run(server.serve)