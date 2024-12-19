#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso:$PYTHONPATH"

# Run the streamlit app
streamlit run src/search_qdrant/streamlit_app.py
