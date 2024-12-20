#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso:$PYTHONPATH"

# Run the streamlit app
nohup /home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso/.venv/bin/streamlit run ~/Tools/pythagora-core/workspace/fabric-to-espanso/src/search_qdrant/streamlit_app.py & exit
