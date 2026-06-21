from dotenv import load_dotenv
load_dotenv()

from langchain_tavily import TavilySearch


def web_search(question: str) -> list[str]:
    search_tool = TavilySearch(max_results=3)
    results = search_tool.invoke({"query": question})
    return [result["content"] for result in results["results"]]