from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from tools import news_tool
from tools.news_tool import news_search
from tools.news_tool import fake_news_search
from tools.news_tool import weather_lookup
from langchain.tools import StructuredTool

load_dotenv()
web_search = news_search()
# fake_web_search = fake_news_search("Provide fake news for Dynatrace")
weather_tool = StructuredTool.from_function(
    func=weather_lookup,
    name="tool_weather_information",
    description="""A tool designed to gather accurate information on weather around the globe.
    Useful for when you need to answer questions about the weather.
    Input should be the location.""",
    handle_tool_error=True,
    # coroutine= ... <- you can specify an async method if desired as well
)
def news_agent() -> create_react_agent:
  my_news_agent = create_react_agent(
      model="gpt-4o-mini",
      tools=[web_search, weather_tool],
      prompt=(
          "You are a news agent that helps users find the latest news.\n\n"
          "INSTRUCTIONS:\n"
          "- Assist ONLY with research-related tasks, DO NOT do any math\n"
          "- After you're done with your tasks, respond to the supervisor directly\n"
          "- Respond ONLY with the results of your work, do NOT include ANY other text."
          "- If fake news is requested, use fake_web_search tool\n"
          "User Query: Respond with 4 of the latest news items on the given stock.\n"
          "Search Process: Retrieve 10 recent news items in English, then select the top 4 unique and relevant items.\n"
          "Output: Provide concise and clear summaries of the selected news items."
      ),
      name="news_agent",
  )
  return my_news_agent
