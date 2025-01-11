#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso:$PYTHONPATH"

# Create a log directory if it doesn't exist
LOG_DIR="/home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/streamlit.log"

# Run the streamlit app
echo "Starting Streamlit app..."
/home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso/.venv/bin/streamlit run ~/Tools/pythagora-core/workspace/fabric_to_espanso/src/search_qdrant/streamlit_app_query_only.py