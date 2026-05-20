from duckduckgo_search import DDGS
from crewai.tools import tool


@tool("Financial News Search")
def search_financial_news(query: str) -> str:
    """
    Search for recent financial news using DuckDuckGo. Returns top 6 results with dates.
    query: e.g. 'HDFC Bank Q4 results 2026' or 'HDFC Bank RBI penalty'
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.news(query, max_results=6))

        if not results:
            with DDGS() as ddgs:
                results = list(ddgs.text(query, max_results=6))

        output = []
        for r in results:
            title = r.get("title", "")
            body = r.get("body", r.get("snippet", ""))
            date = r.get("date", r.get("published", ""))
            source = r.get("source", "")
            output.append(f"[{date}] {title}\nSource: {source}\n{body}")

        return "\n\n---\n\n".join(output) if output else "No news found."
    except Exception as exc:
        return f"Search error: {exc}"


@tool("Web Search")
def search_web(query: str) -> str:
    """
    General web search for financial data, company information, or regulatory news.
    query: Search query string
    """
    try:
        with DDGS() as ddgs:
            results = list(ddgs.text(query, max_results=5))

        output = []
        for r in results:
            output.append(f"Title: {r.get('title', '')}\n{r.get('body', '')}")

        return "\n\n---\n\n".join(output) if output else "No results found."
    except Exception as exc:
        return f"Search error: {exc}"
