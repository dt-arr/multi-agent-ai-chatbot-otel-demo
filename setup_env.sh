#!/bin/bash
# Lightweight Environment Setup Script - Compatible with bash and zsh

set -e  # Exit on any error

# Create temp directory if it doesn't exist
mkdir -p temp

# Source existing environment if available
if [ -f "temp/.env.local" ]; then
    echo "Loading existing environment variables from temp/.env.local..."
    set -a  # automatically export all variables
    source temp/.env.local
    set +a
fi

echo "=== Environment Variable Setup ==="
echo "Please provide the following environment variables:"
echo

# Function to prompt for input (required unless existing value)
prompt_with_existing() {
    local var_name="$1"
    local prompt_text="$2"
    local is_sensitive="$3"
    local existing_value="${!var_name}"  # Get current value of the variable
    local display_value=""
    local user_input=""
    
    # Create display value for existing data
    if [ -n "$existing_value" ]; then
        if [ "$is_sensitive" = "true" ]; then
            # Show only first 4 and last 4 characters for sensitive data
            local length=${#existing_value}
            if [ $length -gt 8 ]; then
                display_value="${existing_value:0:4}...${existing_value: -4}"
            else
                display_value="****"
            fi
        else
            # Show full value for non-sensitive data
            display_value="$existing_value"
        fi
        echo -n "$prompt_text [current: $display_value] (press Enter to keep): "
    else
        echo -n "$prompt_text: "
    fi
    
    if [ "$is_sensitive" = "true" ]; then
        read -s user_input
        echo  # Add newline after hidden input
    else
        read user_input
    fi
    
    # Use existing value if input is empty and existing value exists
    if [ -z "$user_input" ] && [ -n "$existing_value" ]; then
        user_input="$existing_value"
    fi
    
    # Validate that we have a value
    if [ -z "$user_input" ]; then
        echo "This field is required. Please enter a value."
        prompt_with_existing "$var_name" "$prompt_text" "$is_sensitive"
        return
    fi
    
    # Export the variable
    export "$var_name"="$user_input"
}

# LLM AUTH
echo "--- LLM Authentication ---"
prompt_with_existing "OPENAI_API_KEY" "Enter OpenAI API Key" "true"
prompt_with_existing "TAVILY_API_KEY" "Enter Tavily API Key" "true"

echo
echo "--- Dynatrace Configuration ---"
echo "Endpoint format examples:"
echo "  https://your-tenant-id.sprint.dynatracelabs.com/api/v2/otlp"
echo "  https://your-tenant-id.live.dynatrace.com/api/v2/otlp"
prompt_with_existing "DYNATRACE_EXPORTER_OTLP_ENDPOINT" "Enter Dynatrace OTLP Endpoint" "false"
echo "API Token should have OpenTelemetry Metrics, Traces and Logs permissions (format: dtxxxxxxxxxxxxxxxxx)"
prompt_with_existing "DYNATRACE_API_TOKEN" "Enter Dynatrace API Token" "true"

echo
echo "--- OTEL and Traceloop Configuration ---"
echo "Setting OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE to 'delta'"
echo "Setting TRACELOOP_TRACE_CONTENT to 'true'"
export OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="delta"
export TRACELOOP_TRACE_CONTENT=true

echo
echo "--- Optional: Console Trace Logging ---"
echo "WARNING: Enabling console trace logging will make the output very noisy!"

# Check existing value for console traces
existing_console_traces="${OTEL_CONSOLE_TRACES:-false}"
echo -n "Enable console trace logging for debugging? [current: $existing_console_traces] (y/N): "
read enable_console_traces

if [[ "$enable_console_traces" =~ ^[Yy]$ ]]; then
    export OTEL_CONSOLE_TRACES=true
    echo "Console trace logging ENABLED - output will be verbose!"
elif [[ -z "$enable_console_traces" ]]; then
    # Keep existing value if just pressed Enter
    export OTEL_CONSOLE_TRACES="$existing_console_traces"
    echo "Console trace logging kept as: $existing_console_traces"
else
    export OTEL_CONSOLE_TRACES=false
    echo "Console trace logging disabled"
fi

echo
echo "--- Client Configuration ---"
echo "Examples: Company Name could be 'Acme Insurance Corp', Service Name could be 'AcmeAIAgent'"
prompt_with_existing "COMPANY_NAME" "Enter Company Name" "false"
prompt_with_existing "OTEL_SERVICE_NAME" "Enter OTEL Service Name" "false"

echo
echo "=== Environment Variables Set (Session Only) ==="
echo "Variables are now available in this session and will be inherited by child processes."

# Write to temp/.env.local file (gitignored) for persistence
echo "Saving environment variables to temp/.env.local (temp directory is gitignored)..."
cat > temp/.env.local << EOF
# Auto-generated environment variables - DO NOT COMMIT TO VERSION CONTROL

# LLM AUTH
OPENAI_API_KEY='$OPENAI_API_KEY'
TAVILY_API_KEY='$TAVILY_API_KEY'

# Dynatrace Configuration  
DYNATRACE_EXPORTER_OTLP_ENDPOINT='$DYNATRACE_EXPORTER_OTLP_ENDPOINT'
DYNATRACE_API_TOKEN='$DYNATRACE_API_TOKEN'

# OTEL and TRACELOOP ENV VARIABLES
OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE="$OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE"
TRACELOOP_TRACE_CONTENT=$TRACELOOP_TRACE_CONTENT
OTEL_CONSOLE_TRACES=$OTEL_CONSOLE_TRACES

# Client Configuration
COMPANY_NAME="$COMPANY_NAME"
OTEL_SERVICE_NAME="$OTEL_SERVICE_NAME"
EOF

echo "Environment variables saved to temp/.env.local"
echo
echo "IMPORTANT: The temp/ directory is gitignored to prevent committing sensitive data!"

# Check if .gitignore exists and add temp/ if not present
if [ -f ".gitignore" ]; then
    if ! grep -q "temp/" .gitignore; then
        echo "" >> .gitignore
        echo "# Temp directory for local files" >> .gitignore
        echo "temp/" >> .gitignore
        echo "Added temp/ directory to .gitignore"
    fi
else
    echo "# Temp directory for local files" > .gitignore
    echo "temp/" >> .gitignore
    echo "Created .gitignore and added temp/ directory"
fi

echo
echo "=== Ready to Start Application? ==="
echo "The following commands will be executed:"
echo "1. python -m venv financial-agent"
echo "2. source financial-agent/bin/activate"
echo "3. pip install -r requirements.txt"
echo "4. streamlit run main.py"
echo

read -p "Do you want to start the application now? (y/N): " start_app

if [[ "$start_app" =~ ^[Yy]$ ]]; then
    echo
    echo "=== Starting Application ==="
    
    # Get the repository name from the current directory
    REPOSITORY_NAME=$(basename "$(pwd)")
    echo "Repository: $REPOSITORY_NAME"
    
    # Create virtual environment
    echo "Creating virtual environment..."
    python -m venv financial-agent
    
    # Activate virtual environment
    echo "Activating virtual environment..."
    source financial-agent/bin/activate
    
    # Install requirements
    echo "Installing requirements..."
    pip install -r requirements.txt
    
    # Start Streamlit (source temp/.env.local first to ensure variables are available)
    echo "Sourcing environment variables..."
    if [ -f "temp/.env.local" ]; then
        set -a
        source temp/.env.local
        set +a
    fi
    
    echo "Starting Streamlit application..."
    ./financial-agent/bin/streamlit run main.py
else
    echo
    echo "Environment variables are set for this session and saved to .env.local"
    echo "To start the application later, run:"
    echo "source financial-agent/bin/activate"
    echo "source temp/.env.local  # Load environment variables"
    echo "streamlit run main.py"
    echo
    echo "Note: temp/.env.local will persist your settings between script runs."
fi