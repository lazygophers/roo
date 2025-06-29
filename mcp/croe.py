from mcp.server.fastmcp import FastMCP

mcp = FastMCP(
	name="fire",
	stateless_http=True,
	json_response=True,
	host="0.0.0.0",
	port=14000,
	debug=True,
)