from langgraph.prebuilt import create_react_agent
from dotenv import load_dotenv
from tools import news_tool
from tools.news_tool import news_search

load_dotenv()
web_search = news_search()

def news_agent() -> create_react_agent:
  my_news_agent = create_react_agent(
      model="openai:gpt-4.1",
      tools=[web_search],
      prompt=(
          "You are a news agent that helps users find the latest news.\n\n"
          "INSTRUCTIONS:\n"
          # "- Assist ONLY with research-related tasks, DO NOT do any math\n"
          # "- After you're done with your tasks, respond to the supervisor directly\n"
          # "- Respond ONLY with the results of your work, do NOT include ANY other text."
          "User Query: Respond with 4 of the latest news items on the given stock.\n"
          "Search Process: Retrieve 10 recent news items in English, then select the top 4 unique and relevant items.\n"
          "Output: Provide concise and clear summaries of the selected news items."
      ),
      name="news_agent",
  )
  return my_news_agent
