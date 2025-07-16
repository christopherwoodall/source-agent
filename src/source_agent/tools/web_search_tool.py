import requests
from bs4 import BeautifulSoup
from ddgs import DDGS
from .tool_registry import registry


@registry.register(
    name="web_search_tool",
    description="Search the web using DuckDuckGo and return snippets and optional page content.",
    parameters={
        "type": "object",
        "properties": {
            "query": {
                "type": "string",
                "description": "Search query to find information on the web",
            },
            "max_results": {
                "type": "integer",
                "description": "Maximum number of search results to return",
                "default": 5,
            },
        },
        "required": ["query"],
    },
)
def web_search_tool(query: str, max_results: int = 5) -> dict:
    try:
        ddgs = DDGS()
        results = ddgs.text(query, max_results=max_results)
        simplified_results = []

        for result in results:
            try:
                # Fetch content
                response = requests.get(
                    result["href"], headers={"User-Agent": "Mozilla/5.0"}, timeout=10
                )
                response.raise_for_status()

                soup = BeautifulSoup(response.text, "html.parser")
                for script in soup(["script", "style"]):
                    script.decompose()

                text = soup.get_text()
                clean_text = " ".join(text.split())
                snippet = (
                    clean_text[:1000] + "..." if len(clean_text) > 1000 else clean_text
                )

                simplified_results.append(
                    {
                        "title": result.get("title"),
                        "url": result.get("href"),
                        "snippet": snippet,
                        "content": result.get("body"),
                    }
                )

            except Exception as fetch_err:
                simplified_results.append(
                    {
                        "title": result.get("title"),
                        "url": result.get("href"),
                        "snippet": result.get("body"),
                        "content": f"Could not fetch content: {str(fetch_err)}",
                    }
                )

        return {"success": True, "content": simplified_results}

    except Exception as search_err:
        return {"success": False, "content": [f"Search failed: {str(search_err)}"]}
