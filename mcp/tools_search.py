import random

from langchain.utilities import SearxSearchWrapper

from config import searx_hosts
from croe import mcp


@mcp.tool()
async def search_searx(
    query: str,
    num_results: int = 10,
) -> list[dict]:
    """通过 Searx 进行搜索

    Args:
        query: The query to search for.
        num_results: Limit the number of results to return.

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
