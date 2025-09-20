import getpass
import os

# from utils.pretty_print import pretty_print_messages
# from utils.get_pretty import get_pretty_messages
from dotenv import load_dotenv
from agents.news_agent import news_agent
from agents.fundamental_agent import fundamental_agent
from agents.supervisor_agent import supervisor_agent
from agents.technical_agent import technical_agent
from agents.humorous_news_agent import humorous_news_agent
from agents.insurance_agent import insurance_agent
from traceloop.sdk import Traceloop
import streamlit as st
from langchain_core.messages import HumanMessage
from langchain_core.messages.ai import AIMessageChunk
from utils.utils import astream_graph, random_uuid
from langchain_core.runnables import RunnableConfig
from langchain_core.messages.tool import ToolMessage
import asyncio

# Add these imports for console tracing
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.resources import Resource

import os
import streamlit as st

# Get company name from environment variable, with fallback
COMPANY_NAME = os.getenv("COMPANY_NAME", "AcmeCorp")

st.set_page_config(
    page_title=f"{COMPANY_NAME} AI Agent",
    page_icon="☀️",  # Insurance shield emoji
    layout="centered",
    initial_sidebar_state="expanded"
)

st.title(f"☀️ {COMPANY_NAME} GPT")

load_dotenv()

# Check if console tracing is enabled
CONSOLE_TRACES_ENABLED = os.getenv("OTEL_CONSOLE_TRACES", "false").lower() == "true"

if CONSOLE_TRACES_ENABLED:
    # Create temp directory for logs
    os.makedirs("temp", exist_ok=True)
    
    # Set up logging to file in temp directory
    import logging
    from datetime import datetime
    
    # Create log filename with timestamp
    log_filename = f"temp/console_traces_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
    
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_filename),
            logging.StreamHandler()  # Still show in console too
        ]
    )
    
    print(f"🔍 CONSOLE TRACING ENABLED - Logs will be saved to: {log_filename}")
    print("=" * 60)

# Add at line number 22
headers = { "Authorization": "Api-Token " + os.environ.get("DYNATRACE_API_TOKEN") }

# Initialize Traceloop with console tracing support
Traceloop.init(
    app_name=os.environ.get("OTEL_SERVICE_NAME", "CustomerAIAgent"),
    api_endpoint=os.environ.get("DYNATRACE_EXPORTER_OTLP_ENDPOINT"),
    headers=headers,
    disable_batch=True
)

# Add console tracing if enabled
if CONSOLE_TRACES_ENABLED:
    # Get the existing tracer provider that Traceloop set up
    tracer_provider = trace.get_tracer_provider()
    
    # Add console span exporter
    console_exporter = ConsoleSpanExporter()
    console_processor = BatchSpanProcessor(console_exporter)
    tracer_provider.add_span_processor(console_processor)
    
    print("✅ Console span exporter added to trace provider")
    print("=" * 60)

# Create and reuse global event loop (create once and continue using)
if "event_loop" not in st.session_state:
    loop = asyncio.new_event_loop()
    st.session_state.event_loop = loop
    asyncio.set_event_loop(loop)

# Initialize session state
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False  # Session initialization flag
    st.session_state.agent = None  # Storage for ReAct agent object
    st.session_state.history = []  # List for storing conversation history
    st.session_state.timeout_seconds = (
        120  # Response generation time limit (seconds), default 120 seconds
    )

    st.session_state.recursion_limit = 100  # Recursion call limit, default 100

if "thread_id" not in st.session_state:
    st.session_state.thread_id = random_uuid()

def _set_if_undefined(var: str):
  if not os.environ.get(var):
    os.environ[var] = getpass.getpass(f"Please provide your {var}")

_set_if_undefined("OPENAI_API_KEY")

news_agent = news_agent()
fundamental_agent = fundamental_agent()
technical_agent = technical_agent()
humorous_news_agent = humorous_news_agent()
insurance_agent = insurance_agent()
supervisor: supervisor_agent = supervisor_agent(news_agent, fundamental_agent, technical_agent, humorous_news_agent, insurance_agent).compile()

def print_message():
  """
  Displays chat history on the screen.

  Distinguishes between user and assistant messages on the screen,
  and displays tool call information within the assistant message container.
  """
  i = 0
  while i < len(st.session_state.history):
    message = st.session_state.history[i]

    if message["role"] == "user":
      st.chat_message("user", avatar="🧑‍💻").markdown(message["content"])
      i += 1
    elif message["role"] == "assistant":
      # Create assistant message container
      with st.chat_message("assistant", avatar="🤖"):
        # Display assistant message content
        st.markdown(message["content"])

        # Check if the next message is tool call information
        if (
          i + 1 < len(st.session_state.history)
          and st.session_state.history[i + 1]["role"] == "assistant_tool"
        ):
          # Display tool call information in the same container as an expander
          with st.expander("🔧 Tool Call Information", expanded=False):
            st.markdown(st.session_state.history[i + 1]["content"])
          i += 2  # Increment by 2 as we processed two messages together
        else:
          i += 1  # Increment by 1 as we only processed a regular message
    else:
      # Skip assistant_tool messages as they are handled above
      i += 1

async def initialize_session():
  """
  Sets the agent to Supervisor Agent

  Returns:
      bool: Initialization success status
  """

  st.session_state.agent = supervisor
  st.session_state.session_initialized = True
  return True

def get_streaming_callback(text_placeholder, tool_placeholder):
  """
  Creates a streaming callback function.

  This function creates a callback function to display responses generated from the LLM in real-time.
  It displays text responses and tool call information in separate areas.

  Args:
      text_placeholder: Streamlit component to display text responses
      tool_placeholder: Streamlit component to display tool call information

  Returns:
      callback_func: Streaming callback function
      accumulated_text: List to store accumulated text responses
      accumulated_tool: List to store accumulated tool call information
  """
  accumulated_text = []
  accumulated_tool = []

  def callback_func(message: dict):
    nonlocal accumulated_text, accumulated_tool
    message_content = message.get("content", None)

    # Add console logging for traces if enabled
    if CONSOLE_TRACES_ENABLED:
        trace_msg = f"🔍 TRACE: Message received - Type: {type(message_content)}"
        print(trace_msg)
        logging.info(trace_msg)
        
        if hasattr(message_content, 'content'):
            content_preview = f"🔍 TRACE: Content preview: {str(message_content.content)[:100]}..."
            print(content_preview)
            logging.info(content_preview)

    if isinstance(message_content, AIMessageChunk):
      content = message_content.content
      # If content is in list form (mainly occurs in Claude models)
      if isinstance(content, list) and len(content) > 0:
        message_chunk = content[0]
        # Process text type
        if message_chunk["type"] == "text":
          accumulated_text.append(message_chunk["text"])
          text_placeholder.markdown("".join(accumulated_text))
          if CONSOLE_TRACES_ENABLED:
              text_trace = f"🔍 TRACE: Text chunk: {message_chunk['text']}"
              print(text_trace)
              logging.info(text_trace)
        # Process tool use type
        elif message_chunk["type"] == "tool_use":
          if "partial_json" in message_chunk:
            accumulated_tool.append(message_chunk["partial_json"])
          else:
            tool_call_chunks = message_content.tool_call_chunks
            tool_call_chunk = tool_call_chunks[0]
            accumulated_tool.append(
              "\n```json\n" + str(tool_call_chunk) + "\n```\n"
            )
          with tool_placeholder.expander(
            "🔧 Tool Call Information", expanded=True
          ):
            st.markdown("".join(accumulated_tool))
          if CONSOLE_TRACES_ENABLED:
              tool_trace = f"🔍 TRACE: Tool use: {message_chunk}"
              print(tool_trace)
              logging.info(tool_trace)
      # Process if tool_calls attribute exists (mainly occurs in OpenAI models)
      elif (
        hasattr(message_content, "tool_calls")
        and message_content.tool_calls
        and len(message_content.tool_calls[0]["name"]) > 0
      ):
        tool_call_info = message_content.tool_calls[0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
        if CONSOLE_TRACES_ENABLED:
            tool_call_trace = f"🔍 TRACE: Tool call: {tool_call_info}"
            print(tool_call_trace)
            logging.info(tool_call_trace)
      # Process if content is a simple string
      elif isinstance(content, str):
        accumulated_text.append(content)
        text_placeholder.markdown("".join(accumulated_text))
        if CONSOLE_TRACES_ENABLED:
            string_trace = f"🔍 TRACE: String content: {content}"
            print(string_trace)
            logging.info(string_trace)
      # Process if invalid tool call information exists
      elif (
        hasattr(message_content, "invalid_tool_calls")
        and message_content.invalid_tool_calls
      ):
        tool_call_info = message_content.invalid_tool_calls[0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information (Invalid)", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
        if CONSOLE_TRACES_ENABLED:
            invalid_trace = f"🔍 TRACE: Invalid tool call: {tool_call_info}"
            print(invalid_trace)
            logging.info(invalid_trace)
      # Process if tool_call_chunks attribute exists
      elif (
        hasattr(message_content, "tool_call_chunks")
        and message_content.tool_call_chunks
      ):
        tool_call_chunk = message_content.tool_call_chunks[0]
        accumulated_tool.append(
          "\n```json\n" + str(tool_call_chunk) + "\n```\n"
        )
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
        if CONSOLE_TRACES_ENABLED:
            chunk_trace = f"🔍 TRACE: Tool call chunk: {tool_call_chunk}"
            print(chunk_trace)
            logging.info(chunk_trace)
      # Process if tool_calls exists in additional_kwargs (supports various model compatibility)
      elif (
        hasattr(message_content, "additional_kwargs")
        and "tool_calls" in message_content.additional_kwargs
      ):
        tool_call_info = message_content.additional_kwargs["tool_calls"][0]
        accumulated_tool.append("\n```json\n" + str(tool_call_info) + "\n```\n")
        with tool_placeholder.expander(
          "🔧 Tool Call Information", expanded=True
        ):
          st.markdown("".join(accumulated_tool))
        if CONSOLE_TRACES_ENABLED:
            kwargs_trace = f"🔍 TRACE: Tool call from additional_kwargs: {tool_call_info}"
            print(kwargs_trace)
            logging.info(kwargs_trace)
    # Process if it's a tool message (tool response)
    elif isinstance(message_content, ToolMessage):
      accumulated_tool.append(
        "\n```json\n" + str(message_content.content) + "\n```\n"
      )
      with tool_placeholder.expander("🔧 Tool Call Information", expanded=True):
        st.markdown("".join(accumulated_tool))
      if CONSOLE_TRACES_ENABLED:
          tool_msg_trace = f"🔍 TRACE: Tool message: {message_content.content}"
          print(tool_msg_trace)
          logging.info(tool_msg_trace)
    return None

  return callback_func, accumulated_text, accumulated_tool

async def process_query(query, text_placeholder, tool_placeholder, timeout_seconds=60):
  """
  Processes user questions and generates responses.

  This function passes the user's question to the agent and streams the response in real-time.
  Returns a timeout error if the response is not completed within the specified time.

  Args:
      query: Text of the question entered by the user
      text_placeholder: Streamlit component to display text responses
      tool_placeholder: Streamlit component to display tool call information
      timeout_seconds: Response generation time limit (seconds)

  Returns:
      response: Agent's response object
      final_text: Final text response
      final_tool: Final tool call information
  """
  try:
    if st.session_state.agent:
      if CONSOLE_TRACES_ENABLED:
          query_start = f"🔍 TRACE: Processing query: {query}"
          print(query_start)
          logging.info(query_start)
          print("=" * 60)
      
      streaming_callback, accumulated_text_obj, accumulated_tool_obj = (
        get_streaming_callback(text_placeholder, tool_placeholder)
      )
      try:
        response = await asyncio.wait_for(
          astream_graph(
            st.session_state.agent,
            {"messages": [HumanMessage(content=query)]},
            callback=streaming_callback,
            config=RunnableConfig(
              recursion_limit=st.session_state.recursion_limit,
              thread_id=st.session_state.thread_id,
            ),
          ),
          timeout=timeout_seconds,
        )
        
        if CONSOLE_TRACES_ENABLED:
            query_complete = f"🔍 TRACE: Query completed successfully"
            print(query_complete)
            logging.info(query_complete)
            print("=" * 60)
            
      except asyncio.TimeoutError:
        error_msg = f"⏱️ Request time exceeded {timeout_seconds} seconds. Please try again later."
        if CONSOLE_TRACES_ENABLED:
            timeout_trace = f"🔍 TRACE: Timeout error: {error_msg}"
            print(timeout_trace)
            logging.error(timeout_trace)
        return {"error": error_msg}, error_msg, ""

      final_text = "".join(accumulated_text_obj)
      final_tool = "".join(accumulated_tool_obj)
      return response, final_text, final_tool
    else:
      return (
        {"error": "🚫 Agent has not been initialized."},
        "🚫 Agent has not been initialized.",
        "",
      )
  except Exception as e:
    import traceback

    error_msg = f"❌ Error occurred during query processing: {str(e)}\n{traceback.format_exc()}"
    if CONSOLE_TRACES_ENABLED:
        exception_trace = f"🔍 TRACE: Exception: {error_msg}"
        print(exception_trace)
        logging.error(exception_trace)
    return {"error": error_msg}, error_msg, ""

success = st.session_state.event_loop.run_until_complete(
  initialize_session()
)

print_message()

user_query = st.chat_input("💬 Ask about stocks, financial analysis, or insurance questions")
if user_query:
  if st.session_state.session_initialized:
    st.chat_message("user", avatar="🧑‍💻").markdown(user_query)
    with st.chat_message("assistant", avatar="🤖"):
      tool_placeholder = st.empty()
      text_placeholder = st.empty()
      resp, final_text, final_tool = (
        st.session_state.event_loop.run_until_complete(
          process_query(
            user_query,
            text_placeholder,
            tool_placeholder,
            st.session_state.timeout_seconds,
          )
        )
      )
    if "error" in resp:
      st.error(resp["error"])
    else:
      st.session_state.history.append({"role": "user", "content": user_query})
      st.session_state.history.append(
        {"role": "assistant", "content": final_text}
      )
      if final_tool.strip():
        st.session_state.history.append(
          {"role": "assistant_tool", "content": final_tool}
        )
      st.rerun()
  else:
    st.warning(
      "⚠️ MCP server and agent are not initialized. Please click the 'Apply Settings' button in the left sidebar to initialize."
    )