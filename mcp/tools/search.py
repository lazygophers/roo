import random
from pydantic import Field

from langchain.utilities import SearxSearchWrapper

from core.config import searx_hosts
from core.croe import mcp


@mcp.tool()
async def search_searx(
    query: str = Field(description="要搜索的关键词"),
    num_results: int = Field(description="要返回的搜索结果数量", default=20),
) -> list[dict]:
    """通过 Searx 进行搜索
    Returns:
        Dict with the following keys:
        {
            snippet:  The description of the result.
            title:  The title of the result.
            link: The link to the result.
            engines: The engines used for the result.
            category: Searx category of the result.
        }

    """
    search = SearxSearchWrapper(searx_host=random.choice(searx_hosts))
    return search.results(query, num_results=num_results)
