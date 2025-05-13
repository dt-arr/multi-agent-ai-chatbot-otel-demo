from langchain_tavily import TavilySearch
from langchain_core.tools import tool

def news_search() -> TavilySearch:
  my_news_search = TavilySearch(max_results=3)
  return my_news_search
