from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

def supervisor_agent(news_agent: create_react_agent, fundamental_agent:create_react_agent, technical_agent:create_react_agent) -> create_supervisor:
  supervisor = create_supervisor(
      model=init_chat_model("openai:gpt-4.1"),
      agents=[news_agent, fundamental_agent,technical_agent],
      prompt=(
          "You are a supervisor managing three agents:\n"
          "- a news agent. Assign news-related tasks to this agent\n"
          "- a fundamental agent. Assign fundamental analysis tasks to this agent\n"
          "= a technical agent. Assign technical analysis tasks to this agent\n"
          "Assign work to one agent at a time, do not call agents in parallel.\n"
          "Do not do any work yourself."
      ),
      add_handoff_back_messages=True,
      output_mode="full_history",
  )
  return supervisor
