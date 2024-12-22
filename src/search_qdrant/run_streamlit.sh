#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso:$PYTHONPATH"

# Check if streamlit is already running on port 8501
if ss -tuln | grep -q ":8501 "; then
	echo "Port 8501 is already in use. No need to start the app again."
	exit 0
fi
	
# Clean up any existing nohup.out
[ -f nohup.out ] && rm -f nohup.out

# Run the streamlit app
nohup /home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso/.venv/bin/streamlit run ~/Tools/pythagora-core/workspace/fabric-to-espanso/src/search_qdrant/streamlit_app.py > streamlit.log 2>&1 &

# Wait for Streamlit to start and capture its initial output
max_attempts=5
while [ $attempt -lt $max_attempts ]; do
	if grep -q "You can now view your Streamlit app" streamlit.log; then
		cat streamlit.log | grep -A 3 "You can now view your Streamlit app"
		exit 0
	fi
	sleep 1
	((attempt++))
done

echo "Failed to start Streamlit server"
