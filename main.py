from mcp.server.fastmcp import FastMCP
from dotenv import load_dotenv
import json 
import httpx 
import os 
from bs4 import BeautifulSoup


load_dotenv()

mcp = FastMCP("docs")

# including https:// is wrong format!
# documentation_url = "https://pytorch.org/docs/stable/index.html"
documentation_url = "pytorch.org/tutorials/recipes/torch_compiler_set_stance_tutorial.html"
SERPER_URL="https://google.serper.dev/search"


def search(query: str) -> dict | None:
    payload = json.dumps({"q": query, "num": 2})

    headers = {
        "X-API-KEY": os.getenv("SERPER_API_KEY"),
        "Content-Type": "application/json",
    }

    with httpx.Client() as client:
        try: 
            response = client.post(
                SERPER_URL, headers=headers, data=payload, timeout=30.0
            )
            response.raise_for_status()
            return response.json()
        except httpx.TimeoutException: 
            return {"organic": []}


def data_from_url(link: str) -> str:
    with httpx.Client() as client:
        try:
            response = client.get(link, timeout=50.0)
            soup = BeautifulSoup(response.text, "html.parser")
            text = soup.get_text()
            return text
        except httpx.TimeoutException:
            return "Timeout error"


@mcp.tool()
def get_documentation(query: str, library: str):
    """
    Search the latest documentation of any provided library using the query.
    Currently only supports PyTorch.

    Args:
        query: The query to search for (e.g. "what does torch.randn do?")
        library: The library to search in (e.g. "pytorch")

    Returns:
        Text from the latest documentation
    """

    if library != "pytorch":
        raise ValueError(f"Library {library} is not supported by this tool")

    query = f"site:{documentation_url} {query}"
    results = search(query)

    if len(results["organic"]) == 0:
        return f"No seearch results for the query {query}"
    
    text = ""
    for result in results["organic"]:
        text += data_from_url(result["link"])
    return text


if __name__ == "__main__":
    mcp.run(transport="stdio")
