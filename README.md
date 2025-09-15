# FinancialAIAgent-Langchain
This sample application does stock analysis by conducting news search, fundamental review and technical analysis.
This app is built on Single Supervisor with multiple agents architecture as described [here](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/agent_supervisor.ipynb). 
The multiple agents used in this app uses OpenAI LLM Model and uses TavilySearch tool to search for news. Additionally it uses Yahoo Finance for fundamental and technical analysis.

## New Features

### Insurance Agent
The application now includes a specialized insurance agent (`insurance_agent.py`) that provides policy information based on the contents of `insurance_policy.txt`. This agent features:

- **RAG-based Policy Retrieval**: Uses vector embeddings to find relevant policy information
- **Comprehensive Safety Monitoring**: Multiple layers of safety checks with detailed telemetry
- **Customizable Policy Data**: Modify `insurance_policy.txt` to customize the demo with your own policy information
- **Advanced Telemetry**: Extensive OpenTelemetry instrumentation for monitoring safety violations, compliance issues, and response quality

### Safety Features
The insurance agent implements multiple safety checks:
- **Fraud Detection**: Blocks queries attempting fraudulent activities
- **PII Protection**: Prevents exposure of sensitive personal information (SSN, credit cards, emails)
- **Content Filtering**: Blocks inappropriate or harmful content
- **Topic Validation**: Ensures queries are insurance-related
- **Response Quality Monitoring**: Tracks compliance issues, accuracy, and professional tone

### Monitoring & Dashboards
The repository includes Notebooks and Dashboards that you can download and customize for monitoring the application's performance and safety metrics.

### Customization
The application supports customizable branding through environment variables:
* `COMPANY_NAME` - Sets the company name displayed in the app title and page configuration (defaults to "AcmeCorp" if not set)

### API Keys
The following API keys are required for this app:
* `OPENAI_API_KEY`
* `TAVILY_API_KEY`

### Environment Variables
The following environment variables can be configured:

**Required:**
* `OPENAI_API_KEY` - Required for OpenAI LLM functionality
* `TAVILY_API_KEY` - Required for news search functionality

**Optional (Customization):**
* `COMPANY_NAME` - Company name for branding (default: "AcmeCorp")
* `OTEL_SERVICE_NAME` - Service name for telemetry (default: "AcmeAIAgent")

**Optional (Dynatrace Integration):**
* `DYNATRACE_EXPORTER_OTLP_ENDPOINT` - Dynatrace telemetry endpoint
* `DYNATRACE_API_TOKEN` - Dynatrace API token for tracing
* `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` - OTEL metrics temporality setting
* `TRACELOOP_TRACE_CONTENT` - Enable traceloop content tracing

### Requirements
* Python 3.8 or higher

### Usage
The app uses streamlit to create a web page so that users can interact with the app using browser. Once the app is launched, it spits out the url to access the app. Open a browser window and put the url to access the UI of this app.

The supervisor agent (`supervisor_agent.py`) has been updated to accommodate the newly created insurance agent, providing users with comprehensive financial and insurance assistance.

### Instrumentation
The app uses traceloop to send telemetry data. If you want to capture those telemetry data please add the endpoints in .env file.

The insurance agent provides extensive telemetry including:
- Safety violation detection and categorization
- Query risk level assessment
- Response quality scoring
- Compliance monitoring
- Fraud attempt tracking

To get tracing data in Dynatrace, provide these keys:
* DYNATRACE_EXPORTER_OTLP_ENDPOINT (e.g <tenant>.live.dynatrace.com/api/v2/otlp)
* DYNATRACE_API_TOKEN

### How to run
#### On Desktop
Copy .env.template to .env 
Update .env file with all the required keys

Example .env file:
```bash
# Dynatrace Ingest tokens and endpoints
export DYNATRACE_EXPORTER_OTLP_ENDPOINT="https://YOURTENANTID.live.dynatrace.com/api/v2/otlp" 
export DYNATRACE_API_TOKEN="dt007.DUMMYMASKEDFAKETOKEN.MOREDUMMYFAKETOKENTHATYOUREALLYNEEDTOCHANGETOHAVEITWORK" 

# LLM AUTH
export OPENAI_API_KEY='OPENAITOKENMASKEDOPENAI-MAKESUREYOUCHANGETHISTOSOMETHINGREALOTHERWISENOTHINGWILLWORK' 
export TAVILY_API_KEY='TVILYTOKENOHBOYYOUNEEDTOCHANGETHISTOO' 

# OTEL and TRACELOOP ENV VARIABLES. DELTA TEMPORALITY BECAUSE DT ACCEPTS delta and not cumulative
export OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="delta" 
export TRACELOOP_TRACE_CONTENT=true  

# Change these to reflect client details in the App and the detected OTEL Dynatrace Service 
export COMPANY_NAME="Acme Insurance Corp" 
export OTEL_SERVICE_NAME="AcmeAIAgent"