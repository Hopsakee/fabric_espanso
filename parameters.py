import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

MARKDOWN_FOLDER="/mnt/c/_Tools/FabricConvertData"
# MARKDOWN_FOLDER="/mnt/c/Obsidian/BrainCave/Extra/FabricPatterns"
QDRANT_DB_LOCATION="/home/jelle/Qdrant_databases/fabric_db"
YAML_OUTPUT_FOLDER="/mnt/c/Drive/Fabric_yml"
FABRIC_PURPOSES_FILE="/mnt/c/Drive/Fabric_yml/Fabric_purposes.md"

# Ensure required directories exist
os.makedirs(MARKDOWN_FOLDER, exist_ok=True)
os.makedirs(QDRANT_DB_LOCATION, exist_ok=True)
os.makedirs(YAML_OUTPUT_FOLDER, exist_ok=True)