from langgraph_supervisor import create_supervisor
from langchain.chat_models import init_chat_model
from langgraph.prebuilt import create_react_agent

def supervisor_agent(news_agent: create_react_agent, fundamental_agent:create_react_agent, technical_agent:create_react_agent, humorous_news_agent:create_react_agent, insurance_agent:create_react_agent) -> create_supervisor:
  supervisor = create_supervisor(
      model=init_chat_model("gpt-4o-mini"),
      agents=[news_agent, fundamental_agent, technical_agent, humorous_news_agent, insurance_agent],
      prompt=(
          "You are a supervisor managing five agents:\n"
          "- a news agent. Assign news-related tasks to this agent\n"
          "- a fundamental agent. Assign fundamental analysis tasks to this agent\n"
          "- a technical agent. Assign technical analysis tasks to this agent\n"
          "- a humorous news agent. Assign any request for humorous news to this agent\n"
          "- an insurance agent. Assign any insurance-related questions, policy inquiries, coverage questions, claims information, or insurance product questions to this agent\n"
          "- For stock analysis use news agent, fundamental agent and technical agent\n"
          "- For insurance matters (policies, coverage, claims, premiums, etc.) use the insurance agent\n"
          "- Do not answer questions about anything else.\n"
          # "Assign work to one agent at a time, do not call agents in parallel.\n"
          "Do not do any work yourself."
          "After you get the results, send the results to the users"
      ),
      add_handoff_back_messages=True,
      output_mode="full_history",
  )
  return supervisor