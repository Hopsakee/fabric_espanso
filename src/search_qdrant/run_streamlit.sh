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
nohup /home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso/.venv/bin/streamlit run ~/Tools/pythagora-core/workspace/fabric-to-espanso/src/search_qdrant/streamlit_app.py &

# Wait for Streamlit to start and capture its initial output
until grep -q "You can now view your Streamlit app" nohup.out
do
	sleep 1
done

# Display the captured output
cat nohup.out | grep -A 3 "You can now view your Streamlit app"

# Wait 3 seconds before closing
sleep 3
