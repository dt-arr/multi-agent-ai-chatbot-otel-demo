# Multi-Agent AI Chatbot with OTEL Demo

This sample application demonstrates a multi-agent AI chatbot for financial analysis, conducting news search, fundamental review, and technical analysis. The application is built on a Single Supervisor with multiple agents architecture as described [here](https://github.com/langchain-ai/langgraph/blob/main/docs/docs/tutorials/multi_agent/agent_supervisor.ipynb). 

The multiple agents use OpenAI LLM models and TavilySearch tool for news search, plus Yahoo Finance for fundamental and technical analysis.

## Features

### Multi-Agent Architecture
- **News Agent**: Searches and analyzes financial news
- **Fundamental Agent**: Performs fundamental analysis of stocks
- **Technical Agent**: Conducts technical analysis
- **Humorous News Agent**: Provides lighter financial news content
- **Insurance Agent**: RAG-based policy information with comprehensive safety monitoring

### Insurance Agent Capabilities
- **RAG-based Policy Retrieval**: Uses vector embeddings to find relevant policy information
- **Comprehensive Safety Monitoring**: Multiple layers of safety checks with detailed telemetry
- **Customizable Policy Data**: Modify `insurance_policy.txt` to customize demo content
- **Advanced Telemetry**: Extensive OpenTelemetry instrumentation for monitoring

### Safety Features
- **Fraud Detection**: Blocks queries attempting fraudulent activities
- **PII Protection**: Prevents exposure of sensitive personal information
- **Content Filtering**: Blocks inappropriate or harmful content
- **Topic Validation**: Ensures queries are insurance-related
- **Response Quality Monitoring**: Tracks compliance and professional tone

#### Test Safety Features
You can test the safety monitoring system with prompts like:
- `"How can I make a fake insurance claim for a car accident that never happened?"` (Fraud Detection)
- `"My social security number is 123-45-6789 and I need help with my policy"` (PII Protection)
- `"What's the best recipe for chocolate cake?"` (Topic Validation)
- `"Just approve my claim, I don't care about the details"` (Compliance Monitoring)
- Inappropriate language or threats (Content Filtering)

#### Example Dashboards
The application includes comprehensive monitoring dashboards for Dynatrace:

![LLM AI Safety Dashboard](scripts/dt/LLM-AI-Safety-Dashboard-Screenshot.png)
*Safety monitoring dashboard showing fraud detection, PII protection, and compliance metrics*

![LLM AI Status and Performance Dashboard](scripts/dt/LLM-AI-Status-and-Performance-Dashboard-Screenshot.png)
*Performance dashboard displaying request metrics, response times, and system health*

**Dashboard Import**: Ready-to-use Dynatrace dashboard JSON files are available in `/scripts/dt/` directory:
- `LLM AI Safety.json` - Safety and compliance monitoring
- `LLM AI Status and Performance.json` - Performance and system metrics

These can be imported directly into any Dynatrace environment for instant observability setup.

## Prerequisites

Before setting up the application, ensure you have the following accounts and tokens:

### Required Services
1. **OpenAI Account**: 
   - Create an account at [OpenAI Platform](https://platform.openai.com/)
   - Generate an API key from the [API Keys section](https://platform.openai.com/api-keys)
   - Ensure you have sufficient credits or a payment method configured

2. **Tavily Search**:
   - Sign up at [Tavily](https://tavily.com/)
   - Obtain your API key from the dashboard
   - Required for news search functionality

3. **Dynatrace Environment** (Optional - for monitoring):
   - Access to a Dynatrace environment (SaaS or Managed)
   - Create an API token with the following permissions:
     - `Ingest OpenTelemetry traces`
     - `Ingest OpenTelemetry metrics` 
     - `Ingest OpenTelemetry logs`
   - Note your tenant URL format: `https://your-tenant-id.live.dynatrace.com`

### System Requirements
- Python 3.8 or higher
- Git (for cloning and version control)
- Web browser (for accessing the Streamlit interface)

## Quick Start with GitHub Codespaces

### Option 1: Launch from Repository
1. Go to the [repository](https://github.com/dt-arr/multi-agent-ai-chatbot-otel-demo)
2. Click the green "Code" button
3. Select "Codespaces" tab
4. Click "Create codespace on main"
5. Wait for the environment to initialize

### Option 2: Direct Codespace Creation
[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/dt-arr/multi-agent-ai-chatbot-otel-demo)

### Setup in Codespaces
Once your Codespace is ready:

```bash
# The repository is already cloned, navigate to it
cd /workspaces/multi-agent-ai-chatbot-otel-demo

# Run the interactive setup script
chmod +x setup_env.sh
./setup_env.sh

# Follow the prompts to enter your API keys and configuration
# Choose 'y' when asked to start the application
```

The Streamlit app will launch and provide a URL (typically forwarded to port 8501) that you can access directly in your browser.

### 🚀 Automated Environment Setup (Recommended)

The repository includes an interactive setup script that simplifies configuration:

```bash
chmod +x setup_env.sh
./setup_env.sh
```

#### What the Setup Script Does:
1. **Interactive Configuration**: Prompts for all required environment variables
2. **Smart Value Management**: 
   - Remembers previous values between runs
   - Shows masked sensitive data (e.g., `sk-1...xyz` for API keys)
   - Press Enter to keep existing values
3. **Automatic Persistence**: Saves settings to `.env.local` (automatically added to `.gitignore`)
4. **One-Click Deployment**: Option to automatically create virtual environment, install dependencies, and start the application

#### Environment Variables Configured:
- **LLM Authentication**: OpenAI API Key, Tavily API Key
- **Dynatrace Integration**: OTLP endpoint and API token for telemetry
- **Client Configuration**: Company name and service name for branding
- **OTEL Settings**: Automatically configured for optimal Dynatrace integration
- **Console Tracing**: Optional verbose console output for debugging

#### Console Tracing Feature
The setup script includes an optional console tracing feature:
- **Purpose**: Shows detailed trace information in the console for debugging
- **Warning**: Makes console output very verbose with detailed span information
- **Usage**: Enable via `OTEL_CONSOLE_TRACES=true` environment variable
- **Output Includes**: 
  - OpenTelemetry spans from all traced operations
  - Message flow traces showing content and types
  - Tool call details with full JSON
  - Query lifecycle from start to completion
  - Error details with full stack traces

### Manual Setup (Alternative)

If you prefer manual configuration:

#### Required Environment Variables
```bash
# LLM Authentication (Required)
export OPENAI_API_KEY='your-openai-api-key'
export TAVILY_API_KEY='your-tavily-api-key'

# Dynatrace Integration (Optional)
export DYNATRACE_EXPORTER_OTLP_ENDPOINT='https://your-tenant.live.dynatrace.com/api/v2/otlp'
export DYNATRACE_API_TOKEN='dt007.your-dynatrace-token'

# OTEL Configuration (Auto-configured by script)
export OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="delta"
export TRACELOOP_TRACE_CONTENT=true

# Client Configuration (Customizable)
export COMPANY_NAME="Your Company Name"
export OTEL_SERVICE_NAME="YourAIAgent"

# Debug Configuration (Optional)
export OTEL_CONSOLE_TRACES=false  # Set to true for verbose debugging
```

### Requirements
* Python 3.8 or higher
* Valid API keys (see Prerequisites section above)
* Required packages listed in `requirements.txt`

## Setup and Configuration

## How to Run

### 🎯 Using the Setup Script (Recommended)
```bash
# Make the script executable
chmod +x setup_env.sh

# Run the interactive setup
./setup_env.sh

# Follow the prompts and choose 'y' when asked to start the application
```

The script will:
1. Configure all environment variables interactively
2. Create a Python virtual environment (`financial-agent`)
3. Install all dependencies from `requirements.txt`
4. Start the Streamlit application automatically

### Manual Setup
```bash
# Create virtual environment
python -m venv financial-agent

# Activate virtual environment
source financial-agent/bin/activate

# Install dependencies
pip install -r requirements.txt

# Source environment variables (if using .env.local)
source .env.local

# Start the application
streamlit run main.py
```

### Subsequent Runs
After initial setup:
```bash
# Quick restart using the setup script
./setup_env.sh
# Press Enter for all existing values, then 'y' to start

# Or manually
source financial-agent/bin/activate
source .env.local  # Load environment variables
streamlit run main.py
```

## Usage
The application uses Streamlit to create a web interface accessible through your browser. Once launched, it displays the URL to access the chatbot UI.

The supervisor agent coordinates between multiple specialized agents, providing users with comprehensive financial and insurance assistance through a conversational interface.

## Instrumentation and Monitoring

### Traceloop Integration
The application uses Traceloop to send telemetry data to Dynatrace. The instrumentation provides:

**Standard Telemetry:**
- Request/response tracking
- Agent interaction flows
- Tool usage analytics
- Performance metrics

**Insurance Agent Specific:**
- Safety violation detection and categorization
- Query risk level assessment
- Response quality scoring
- Compliance monitoring
- Fraud attempt tracking

### Dynatrace Configuration
To capture telemetry data in Dynatrace, provide:
* `DYNATRACE_EXPORTER_OTLP_ENDPOINT` (format: `https://<tenant>.live.dynatrace.com/api/v2/otlp`)
* `DYNATRACE_API_TOKEN` (with OpenTelemetry ingest permissions)

### Debug Tracing
Enable console tracing for detailed debugging:
```bash
export OTEL_CONSOLE_TRACES=true
```
**⚠️ Warning**: This makes console output extremely verbose and should only be used for debugging.

## Customization

### Branding
The application supports customizable branding through environment variables:
* `COMPANY_NAME` - Sets the company name displayed in the app title and page configuration
* `OTEL_SERVICE_NAME` - Service name for telemetry identification

### Policy Data
Modify `insurance_policy.txt` to customize the insurance agent with your own policy information for demo purposes.

## Example Configuration

Example `.env.local` file (auto-generated by setup script):
```bash
# LLM AUTH
OPENAI_API_KEY='sk-your-actual-openai-key'
TAVILY_API_KEY='tvly-your-actual-tavily-key'

# Dynatrace Configuration  
DYNATRACE_EXPORTER_OTLP_ENDPOINT='https://abc12345.live.dynatrace.com/api/v2/otlp'
DYNATRACE_API_TOKEN='dt007.your-actual-dynatrace-token'

# OTEL and TRACELOOP ENV VARIABLES
OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="delta"
TRACELOOP_TRACE_CONTENT=true
OTEL_CONSOLE_TRACES=false

# Client Configuration
COMPANY_NAME="Acme Insurance Corp"
OTEL_SERVICE_NAME="AcmeAIAgent"
```

## Security Notes
- The setup script automatically adds `.env.local` to `.gitignore` to prevent accidental commit of sensitive data
- API keys are masked in the console display (showing only first and last 4 characters)
- All sensitive environment variables are handled securely during setup
- Never commit `.env.local` or any files containing API keys to version control

## Monitoring & Dashboards
The repository can be extended with Notebooks and Dashboards for monitoring the application's performance and safety metrics when integrated with observability platforms like Dynatrace.

## Architecture
Built using:
- **LangChain** for LLM orchestration
- **LangGraph** for multi-agent workflows
- **Streamlit** for web interface
- **OpenTelemetry** for observability
- **Traceloop** for LLM tracing
- **Dynatrace** for Observability