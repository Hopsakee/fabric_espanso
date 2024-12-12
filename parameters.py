import os

# 
# Initialize some automated variables
#
# Project root directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Get Windows user profile path
import subprocess
windows_user = subprocess.check_output(['cmd.exe', '/c', 'echo %USERNAME%'], text=True).strip()

# 
# User parameters
#
# Location of input and output files
MARKDOWN_FOLDER="/mnt/c/Obsidian/BrainCave/Extra/FabricPatterns"
YAML_OUTPUT_FOLDER=f"/mnt/c/Users/{windows_user}/AppData/Roaming/espanso/match"

# Headings to extract from markdown files
BASE_WORDS = ['Identity', 'Purpose', 'Task', 'Goal']

# Model parameters
USE_FASTEMBED = True
EMBED_MODEL = "fast-bge-small-en" 
COLLECTION_NAME = "markdown_files"

#
# Checks
#
# Ensure required directories exist
os.makedirs(MARKDOWN_FOLDER, exist_ok=True)
os.makedirs(YAML_OUTPUT_FOLDER, exist_ok=True)