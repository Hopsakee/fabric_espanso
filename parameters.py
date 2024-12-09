import os

# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

MARKDOWN_FOLDER="/mnt/c/_Tools/FabricConvertData"
# MARKDOWN_FOLDER="/mnt/c/Obsidian/BrainCave/Extra/FabricPatterns"
YAML_OUTPUT_FOLDER="/mnt/c/Drive/Fabric_yml"
FABRIC_PURPOSES_FILE="/mnt/c/Drive/Fabric_yml/Fabric_purposes.md"

# Headings to extract from markdown files
BASE_WORDS = ['Identity', 'Purpose', 'Task', 'Goal']

# Ensure required directories exist
os.makedirs(MARKDOWN_FOLDER, exist_ok=True)
os.makedirs(YAML_OUTPUT_FOLDER, exist_ok=True)