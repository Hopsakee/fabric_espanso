#!/bin/bash

# Add the project root to PYTHONPATH
export PYTHONPATH="/home/jelle/Tools/pythagora-core/workspace/fabric-to-espanso:$PYTHONPATH"

# Run the query script with all arguments passed to this script
python src/search_qdrant/database_query.py "$@"
