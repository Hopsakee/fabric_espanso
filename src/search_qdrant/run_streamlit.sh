#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso:$PYTHONPATH"

# Create a log directory if it doesn't exist
LOG_DIR="/home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso/logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/streamlit.log"

# Clean up any existing nohup.out
if [ -f nohup.out ]; then
    cat /dev/null > nohup.out
fi

# Check if streamlit is already running on port 8501
if ss -tuln | grep -q ":8501 "; then
	echo "Port 8501 is already in use. No need to start the app again."
	exit 0
fi
	

# Run the streamlit app
echo "Starting Streamlit app..."
nohup /home/jelle/Tools/pythagora-core/workspace/fabric_to_espanso/.venv/bin/streamlit run ~/Tools/pythagora-core/workspace/fabric_to_espanso/src/search_qdrant/streamlit_app.py >> "LOG_FILE" 2>&1 &

echo "Streamlit process started with PID: $!"

# Wait a moment and check if the process is still running
sleep 2
if ps -p $! > /dev/null; then
    echo "Streamlit successfully started"
else
    echo "Failed to start Streamlit. Check $LOG_FILE for details"
    exit 1
fi
# Wait for Streamlit to start and capture its initial output
# max_attempts=5
# attempt=0
# while [ $attempt -lt $max_attempts ]; do
# 	if grep -q "You can now view your Streamlit app" streamlit.log; then
# 		cat streamlit.log | grep -A 3 "You can now view your Streamlit app"
# 		exit 0
# 	fi
# 	sleep 1
# 	((attempt++))
# done

# echo "Failed to start Streamlit server"
